import type { IncomingMessage, ServerResponse } from 'node:http';

const MAX_BODY = 420000;
const permittedPath = /^\/api\/(?:curation|blog(?:\/[a-z0-9][a-z0-9-]{0,159})?|admin\/(?:config|session|login|logout|stars|satellite\/(?:status|plan|catalog|compare|history|observation|evidence|environment|jobs\/[a-f0-9-]{36})|posts(?:\/[a-zA-Z0-9-]+(?:\/(?:publish|unpublish))?)?))$/;

export function configuredAdminOrigin(raw = process.env.ADMIN_API_ORIGIN): string | null {
  if (!raw) return null;
  try {
    const url = new URL(raw);
    if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash || url.pathname !== '/') return null;
    return url.origin;
  } catch { return null; }
}

async function requestBody(req: IncomingMessage & {body?:unknown}): Promise<Uint8Array | undefined> {
  if (req.method === 'GET' || req.method === 'HEAD') return undefined;
  const declared = Number(req.headers['content-length']);
  if (Number.isFinite(declared) && declared > MAX_BODY) throw new Error('oversize');
  if (req.body !== undefined) {
    const bytes = Buffer.isBuffer(req.body) ? req.body : Buffer.from(typeof req.body === 'string' ? req.body : JSON.stringify(req.body));
    if (bytes.length > MAX_BODY) throw new Error('oversize');
    return bytes;
  }
  const chunks: Buffer[] = []; let size = 0;
  for await (const chunk of req) {
    const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += bytes.length;
    if (size > MAX_BODY) throw new Error('oversize');
    chunks.push(bytes);
  }
  return size ? Buffer.concat(chunks) : undefined;
}

/** Same-origin session transport to one configured service; never an open URL proxy. */
export function createAdminProxy(options: {origin?:string; fetcher?:typeof fetch} = {}) {
  return async (req: IncomingMessage, res: ServerResponse) => {
    res.setHeader('Cache-Control','no-store');
    res.setHeader('Content-Type','application/json; charset=utf-8');
    res.setHeader('X-Content-Type-Options','nosniff');
    const fail = (code:number, error:string) => { res.statusCode=code; res.end(JSON.stringify({error})); };
    const url = new URL(req.url || '/', 'https://actforgoa.invalid');
    if (!permittedPath.test(url.pathname)) return fail(404,'This tool route does not exist.');
    const origin = configuredAdminOrigin(options.origin ?? process.env.ADMIN_API_ORIGIN);
    if (!origin) return fail(503,'The team tools service is not configured yet.');
    if (!['GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS'].includes(req.method || 'GET')) return fail(405,'Method not allowed.');
    const isAdmin = url.pathname.startsWith('/api/admin/');
    const headers = new Headers({accept:'application/json'});
    for (const key of ['content-type','origin','sec-fetch-site','x-csrf-token', ...(isAdmin ? ['cookie'] : [])]) {
      const value = req.headers[key];
      if (typeof value === 'string') headers.set(key,value);
    }
    try {
      const body = await requestBody(req);
      const response = await (options.fetcher ?? fetch)(origin + url.pathname + url.search, {
        method:req.method || 'GET', headers, body:body as BodyInit | undefined,
        redirect:'manual', signal:AbortSignal.timeout(url.pathname.startsWith('/api/admin/satellite/') ? 60_000 : 20_000),
      });
      if (response.status >= 300 && response.status < 400) return fail(502,'The team tools service returned an unexpected redirect.');
      const maximum = (url.pathname.startsWith('/api/admin/satellite/') ? 4 : 2) * 1024 * 1024;
      const chunks: Uint8Array[] = [];
      let size = 0;
      const reader = response.body?.getReader();
      if (reader) {
        for (;;) {
          const {done, value} = await reader.read();
          if (done) break;
          size += value.byteLength;
          if (size > maximum) {
            await reader.cancel();
            return fail(502,'The team tools response was too large.');
          }
          chunks.push(value);
        }
      }
      const payload = Buffer.concat(chunks);
      res.statusCode=response.status;
      res.setHeader('Content-Type',response.headers.get('content-type') || 'application/json; charset=utf-8');
      if (isAdmin) {
        const cookies=response.headers.getSetCookie();
        if (cookies.length) res.setHeader('Set-Cookie',cookies);
      }
      res.end(req.method === 'HEAD' ? undefined : payload);
    } catch (error) {
      if (!res.headersSent) return fail(error instanceof Error && error.message === 'oversize' ? 413 : 502,
        error instanceof Error && error.message === 'oversize' ? 'This request is too large.' : 'The team tools service could not respond. Please try again.');
      res.end();
    }
  };
}

export default createAdminProxy();
