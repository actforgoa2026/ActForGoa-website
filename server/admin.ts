import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { timingSafeEqual } from 'node:crypto';
import { isIP } from 'node:net';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { AdminError, AdminStore, type PostPageOptions } from './admin-store.ts';

const cookieName = 'afg_admin_session';
const fail = (status: number, message: string): never => { throw new AdminError(status, message); };
function json(res: ServerResponse, status: number, data: unknown) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}
async function readJson(req: IncomingMessage): Promise<Record<string, unknown>> {
  if (!/^application\/json(?:;|$)/i.test(req.headers['content-type'] ?? '')) fail(415, 'Send JSON using the dashboard.');
  const chunks: Buffer[] = []; let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 420000) fail(413, 'This update is too large. Shorten the article and try again.');
    chunks.push(chunk);
  }
  let data: unknown;
  try { data = JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { return fail(400, 'The update could not be read. Check the fields and try again.'); }
  if (!data || typeof data !== 'object' || Array.isArray(data)) fail(400, 'Send an object with the dashboard fields.');
  return data as Record<string, unknown>;
}
function sessionToken(req: IncomingMessage) {
  const matches = (req.headers.cookie ?? '').split(';').map(item => item.trim()).filter(item => item.startsWith(`${cookieName}=`));
  return matches.length === 1 ? matches[0].slice(cookieName.length + 1) : '';
}
function csrfMatches(actual: unknown, expected: string) {
  if (typeof actual !== 'string' || actual.length !== expected.length) return false;
  const supplied = Buffer.from(actual), wanted = Buffer.from(expected);
  return supplied.length === wanted.length && timingSafeEqual(supplied, wanted);
}
function pageOptions(url: URL): PostPageOptions {
  const limit = Number(url.searchParams.get('limit') ?? 50), q = url.searchParams.get('q') ?? '', status = url.searchParams.get('status') ?? 'all';
  if (!Number.isSafeInteger(limit) || limit < 1 || limit > 100 || q.length > 200 || !['all', 'draft', 'published'].includes(status)) fail(400, 'Choose a valid page size, search and article status.');
  let cursor: PostPageOptions['cursor'];
  if (url.searchParams.has('cursor')) {
    try {
      const parsed = JSON.parse(Buffer.from(url.searchParams.get('cursor')!, 'base64url').toString());
      if (!parsed || typeof parsed.time !== 'string' || !Number.isFinite(Date.parse(parsed.time)) || new Date(parsed.time).toISOString() !== parsed.time || typeof parsed.id !== 'string' || !/^[a-f0-9-]{36}$/.test(parsed.id)) throw new Error();
      cursor = { time: parsed.time, id: parsed.id };
    } catch { return fail(400, 'This page link is invalid. Reload the article list.'); }
  }
  return { limit, q, status: status as PostPageOptions['status'], cursor };
}

/** Only IDs from the exact deployed catalogues may be newly starred. */
export function loadAdminRecordIds(root: string): Set<string> {
  const catalog = JSON.parse(readFileSync(resolve(root, 'public/data/catalog.json'), 'utf8')) as { id: string }[];
  const crm = JSON.parse(readFileSync(resolve(root, 'public/data/crm.json'), 'utf8')) as { records: { record_id: string }[]; opportunities: { record_id: string }[] };
  const guides = JSON.parse(readFileSync(resolve(root, 'src/content/guide-records.json'), 'utf8')) as { id: string }[];
  return new Set([...catalog.map(item => item.id), ...guides.map(item => item.id), ...crm.records.map(item => item.record_id), ...crm.opportunities.map(item => item.record_id)].filter(Boolean));
}

export type AdminServerOptions = {
  databasePath: string; knownRecordIds: ReadonlySet<string>; publicOrigin: string;
  local?: boolean; trustRailwayProxy?: boolean; behindFrontendProxy?: boolean; now?: () => number;
};
export function createAdminServer(options: AdminServerOptions) {
  const origin = new URL(options.publicOrigin);
  if (origin.origin !== options.publicOrigin || origin.username || origin.password || !['http:', 'https:'].includes(origin.protocol)) throw new Error('ADMIN_PUBLIC_ORIGIN must be an exact HTTP(S) origin without a path.');
  if (!options.local && origin.protocol !== 'https:') throw new Error('Production admin requires an HTTPS public origin.');
  if (options.local && origin.protocol === 'http:' && !['127.0.0.1', 'localhost', '[::1]'].includes(origin.hostname)) throw new Error('HTTP admin is only supported on localhost.');
  const store = new AdminStore(options.databasePath, options.knownRecordIds, options.now);
  let pendingLogins = 0;
  const server = createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('Referrer-Policy', 'no-referrer');
    res.setHeader('Vary', 'Origin');
    try {
      if ((req.url?.length ?? 0) > 4096) fail(414, 'Request URL is too long.');
      const url = new URL(req.url ?? '/', 'http://localhost');
      const path = url.pathname, method = req.method ?? 'GET';
      const unsafe = !['GET', 'HEAD', 'OPTIONS'].includes(method);
      if (req.headers.origin && req.headers.origin !== options.publicOrigin) fail(403, 'Open the dashboard on the ActForGoa site.');
      if (unsafe && req.headers['sec-fetch-site'] === 'cross-site') fail(403, 'This request must come from the dashboard.');
      if (method === 'OPTIONS') { res.writeHead(204); return res.end(); }
      if (path === '/api/admin/config' && method === 'GET') return json(res, 200, { available: true });
      if (path === '/api/curation' && method === 'GET') return json(res, 200, { starredIds: store.publicStars() });
      if (path === '/api/blog' && method === 'GET') return json(res, 200, store.publicPosts(pageOptions(url)));
      const publicPost = path.match(/^\/api\/blog\/([a-z0-9]+(?:-[a-z0-9]+)*)$/);
      if (publicPost && method === 'GET') return json(res, 200, { post: store.publicPost(publicPost[1]) });
      if (!path.startsWith('/api/admin/')) fail(404, 'Endpoint not found.');
      if (path === '/api/admin/login' && method === 'POST') {
        if (pendingLogins >= 2) fail(429, 'Sign-in is busy. Try again shortly.');
        pendingLogins++;
        try {
          const data = await readJson(req);
          if (typeof data.email !== 'string' || typeof data.password !== 'string') fail(400, 'Enter your email and password.');
          const real = req.headers['x-real-ip'];
          const address = options.trustRailwayProxy && typeof real === 'string' && isIP(real) ? real : req.socket.remoteAddress ?? 'unknown';
          const session = await store.login(data.email as string, data.password as string, options.behindFrontendProxy ? null : address);
          // Replace a previous session on login rather than retaining it indefinitely.
          if (sessionToken(req)) store.logout(sessionToken(req));
          res.setHeader('Set-Cookie', `${cookieName}=${session.token}; HttpOnly; SameSite=Strict; Path=/api/admin; Max-Age=43200${origin.protocol === 'https:' ? '; Secure' : ''}`);
          return json(res, 200, { user: session.user, csrfToken: session.csrfToken });
        } finally { pendingLogins--; }
      }
      const token = sessionToken(req), session = store.session(token);
      if (unsafe && !csrfMatches(req.headers['x-csrf-token'], session.csrfToken)) fail(403, 'Your security token expired. Reload the dashboard.');
      if (path === '/api/admin/session' && method === 'GET') return json(res, 200, session);
      if (path === '/api/admin/logout' && method === 'POST') {
        store.logout(token);
        res.setHeader('Set-Cookie', `${cookieName}=; HttpOnly; SameSite=Strict; Path=/api/admin; Max-Age=0${origin.protocol === 'https:' ? '; Secure' : ''}`);
        return json(res, 200, { ok: true });
      }
      if (path === '/api/admin/stars' && method === 'GET') return json(res, 200, { stars: store.stars() });
      if (path === '/api/admin/stars' && method === 'PUT') {
        const data = await readJson(req);
        if (typeof data.recordId !== 'string' || typeof data.starred !== 'boolean') fail(400, 'Choose a record and whether to star it.');
        return json(res, 200, { stars: store.star(store.session(token).user, data.recordId as string, data.starred as boolean) });
      }
      if (path === '/api/admin/posts' && method === 'GET') return json(res, 200, store.posts(pageOptions(url)));
      if (path === '/api/admin/posts' && method === 'POST') {
        const data = await readJson(req);
        return json(res, 201, { post: store.createPost(store.session(token).user, data) });
      }
      const post = path.match(/^\/api\/admin\/posts\/([a-f0-9-]{36})(?:\/(publish|unpublish))?$/);
      if (post) {
        if (!post[2] && method === 'GET') return json(res, 200, { post: store.getPost(post[1]) });
        if (!post[2] && method === 'PATCH') {
          const data = await readJson(req);
          return json(res, 200, { post: store.updatePost(store.session(token).user, post[1], data.version, data) });
        }
        if (!post[2] && method === 'DELETE') {
          const data = await readJson(req); store.deletePost(store.session(token).user, post[1], data.version);
          return json(res, 200, { ok: true });
        }
        if (post[2] && method === 'POST') {
          const data = await readJson(req);
          return json(res, 200, { post: store.publishPost(store.session(token).user, post[1], data.version, post[2] === 'publish') });
        }
      }
      fail(404, 'Endpoint not found.');
    } catch (error) {
      if (!res.headersSent) json(res, error instanceof AdminError ? error.status : 500, { error: error instanceof AdminError ? error.message : 'The dashboard could not complete this request. Try again.' });
      else res.end();
    }
  });
  server.requestTimeout = 30000; server.headersTimeout = 10000;
  server.on('close', () => store.close());
  return { server, store };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  process.umask(0o077);
  const local = process.env.NODE_ENV !== 'production';
  const publicOrigin = process.env.ADMIN_PUBLIC_ORIGIN ?? (local ? 'http://127.0.0.1:4173' : '');
  if (!publicOrigin) throw new Error('Set ADMIN_PUBLIC_ORIGIN to the frontend HTTPS origin.');
  const { server } = createAdminServer({
    databasePath: resolve(process.env.ADMIN_DATA_DIR ?? '.reports/admin', 'admin.sqlite'),
    knownRecordIds: loadAdminRecordIds(resolve(process.env.ADMIN_CATALOG_ROOT ?? '.')),
    publicOrigin, local,
    trustRailwayProxy: process.env.ADMIN_TRUST_RAILWAY_PROXY === 'true' && Boolean(process.env.RAILWAY_PROJECT_ID),
    behindFrontendProxy: process.env.ADMIN_BEHIND_FRONTEND_PROXY === 'true',
  });
  const port = Number(process.env.ADMIN_PORT ?? process.env.PORT ?? 4188);
  server.listen(port, process.env.ADMIN_HOST ?? '127.0.0.1', () => console.log(`Admin service listening on port ${port}.`));
  for (const signal of ['SIGINT', 'SIGTERM'] as const) process.on(signal, () => server.close(() => process.exit(0)));
}
