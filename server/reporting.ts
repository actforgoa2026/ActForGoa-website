import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { DatabaseSync } from 'node:sqlite';
import { createHash, randomBytes, randomUUID, timingSafeEqual } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync, existsSync, chmodSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import sharp from 'sharp';
import { isIP } from 'node:net';
import { categories, MAX_PHOTOS, MAX_PHOTO_BYTES, statuses, validateReport, type ReportDraft } from '../shared/reporting.ts';

class HttpError extends Error { constructor(public status: number, message: string) { super(message); } }
const fail = (status: number, message: string): never => { throw new HttpError(status, message); };
const hash = (value: string | Buffer) => createHash('sha256').update(value).digest('hex');
const MAX_BODY = MAX_PHOTO_BYTES * MAX_PHOTOS + 64 * 1024;
async function body(req: IncomingMessage, limit = MAX_BODY) {
  const chunks: Buffer[] = []; let length = 0;
  for await (const chunk of req) { length += chunk.length; if (length > limit) fail(413, 'Photos are too large. Choose up to 3 photos, each under 8 MB.'); chunks.push(chunk); }
  return Buffer.concat(chunks);
}
function json(res: ServerResponse, status: number, value: unknown) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(value));
}

export function createReportingServer(options: { databasePath: string; reviewerToken: string; publicOrigin?: string; staticDir?: string; local?: boolean; rateLimit?: number; trustRailwayProxy?: boolean }) {
  if (options.reviewerToken.length < 32) throw new Error('REPORT_REVIEW_TOKEN must contain at least 32 characters.');
  const db = new DatabaseSync(options.databasePath);
  if (options.databasePath !== ':memory:') chmodSync(options.databasePath, 0o600);
  db.exec(`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
    CREATE TABLE IF NOT EXISTS reports (id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL, fingerprint TEXT NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL, data TEXT NOT NULL, note TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS photos (id TEXT PRIMARY KEY, report_id TEXT NOT NULL REFERENCES reports(id), bytes BLOB NOT NULL, sha256 TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS attempts (client TEXT NOT NULL, time INTEGER NOT NULL);
    CREATE INDEX IF NOT EXISTS attempts_time ON attempts(time);
    CREATE INDEX IF NOT EXISTS reports_created ON reports(created_at);
    CREATE TABLE IF NOT EXISTS review_events (report_id TEXT NOT NULL REFERENCES reports(id), time TEXT NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL);`);
  const authorized = (req: IncomingMessage) => {
    const supplied = createHash('sha256').update(req.headers.authorization ?? '').digest();
    const expected = createHash('sha256').update(`Bearer ${options.reviewerToken}`).digest();
    if (!timingSafeEqual(supplied, expected)) fail(401, 'Enter a valid review key to open the inbox.');
  };
  const rate = (req: IncomingMessage) => {
    // Opt in only behind Railway's edge, which supplies the real client address.
    const forwarded = req.headers['x-real-ip'];
    const address = options.trustRailwayProxy && typeof forwarded === 'string' && isIP(forwarded)
      ? forwarded : (req.socket.remoteAddress ?? 'unknown');
    const client = hash(options.reviewerToken + address);
    const cutoff = Date.now() - 3600000;
    db.prepare('DELETE FROM attempts WHERE time < ?').run(cutoff);
    const count = db.prepare('SELECT count(*) AS n FROM attempts WHERE client = ?').get(client) as { n: number };
    if (count.n >= (options.rateLimit ?? 20)) fail(429, 'Too many attempts. Please try again in an hour.');
    db.prepare('INSERT INTO attempts VALUES (?, ?)').run(client, Date.now());
  };
  let uploads = 0;
  const server = createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Referrer-Policy', 'no-referrer');
    try {
      let url: URL;
      try { url = new URL(req.url ?? '/', 'http://localhost'); } catch { return fail(400, 'Invalid request URL.'); }
      const path = url.pathname;
      if (path.startsWith('/api/')) {
        res.setHeader('Cache-Control', 'no-store');
        res.setHeader('Vary', 'Origin');
        const origin = options.publicOrigin ?? `http://${req.headers.host}`;
        if (req.headers.origin && req.headers.origin !== origin) fail(403, 'This request must come from the reporting site.');
        if (req.headers.origin === origin) {
          res.setHeader('Access-Control-Allow-Origin', origin);
          res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS');
          res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type, Idempotency-Key');
        }
        if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }
        if (path === '/api/reports/config' && req.method === 'GET') return json(res, 200, { available: true, local: options.local === true });
        if (path === '/api/reports' && req.method === 'POST') {
          const key = req.headers['idempotency-key'];
          if (typeof key !== 'string' || !/^[0-9a-f-]{36}$/i.test(key)) fail(400, 'The report could not be identified. Reload and try again.');
          const requestKey = key as string;
          if (uploads >= 2) fail(503, 'The reporting service is busy. Please try again shortly.');
          rate(req); uploads++;
          try {
            const contentType = req.headers['content-type'] ?? '';
            if (!contentType.startsWith('multipart/form-data;')) fail(415, 'Send the report using the reporting form.');
            const bytes = await body(req);
            let form: FormData;
            try { form = await new Request('http://localhost', { method: 'POST', headers: { 'content-type': contentType }, body: new Uint8Array(bytes) }).formData(); }
            catch { return fail(400, 'The upload could not be read. Please choose the photos again.'); }
            if (form.get('website')) fail(400, 'The report could not be accepted.');
            let draft: ReportDraft;
            try { draft = JSON.parse(String(form.get('report'))); validateReport(draft); }
            catch (error) { return fail(400, error instanceof Error && !(error instanceof SyntaxError) ? error.message : 'Check the report details.'); }
            // Copy only schema fields. Unknown client keys are never persisted.
            const data: ReportDraft = { category: draft.category, description: draft.description.trim(), observedAt: draft.observedAt, location: draft.location.trim(), coordinates: draft.coordinates ? { latitude: draft.coordinates.latitude, longitude: draft.coordinates.longitude, ...(draft.coordinates.accuracy === undefined ? {} : { accuracy: draft.coordinates.accuracy }) } : null, email: draft.email.trim(), consent: true };
            const files = form.getAll('photos');
            if (files.length > MAX_PHOTOS) fail(400, 'Choose no more than 3 photos.');
            const photos: Buffer[] = [];
            for (const file of files) {
              if (!(file instanceof File) || file.size === 0 || file.size > MAX_PHOTO_BYTES || !['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) fail(400, 'Use JPG, PNG or WebP photos under 8 MB each.');
              try {
                const input = sharp(Buffer.from(await (file as File).arrayBuffer()), { limitInputPixels: 40000000, animated: false });
                const meta = await input.metadata();
                if (!['jpeg', 'png', 'webp'].includes(meta.format ?? '') || (meta.pages ?? 1) > 1) fail(400, 'Use a still JPG, PNG or WebP photo.');
                // Re-encode, auto-orient, strip embedded metadata, and bound stored image size.
                photos.push(await input.rotate().resize({ width: 2048, height: 2048, fit: 'inside', withoutEnlargement: true }).jpeg({ quality: 88 }).toBuffer());
              } catch { fail(400, 'A photo could not be read. Choose a different JPG, PNG or WebP image.'); }
            }
            const fingerprint = hash(JSON.stringify(data) + photos.map(p => hash(p)).join(''));
            const existing = db.prepare('SELECT id, created_at, fingerprint FROM reports WHERE request_key = ?').get(requestKey) as { id: string; created_at: string; fingerprint: string } | undefined;
            if (existing) { if (existing.fingerprint !== fingerprint) fail(409, 'This submission changed. Go back to the form and try again.'); return json(res, 200, { id: existing.id, createdAt: existing.created_at }); }
            const id = 'AFG-' + randomUUID(); const now = new Date().toISOString();
            db.exec('BEGIN IMMEDIATE');
            try {
              db.prepare('INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(id, requestKey, fingerprint, now, 'new', JSON.stringify(data), '', now);
              for (const photo of photos) db.prepare('INSERT INTO photos VALUES (?, ?, ?, ?)').run(randomUUID(), id, photo, hash(photo));
              db.exec('COMMIT');
            } catch (error) { db.exec('ROLLBACK'); throw error; }
            return json(res, 201, { id, createdAt: now });
          } finally { uploads--; }
        }
        if (path === '/api/reports/review' && req.method === 'GET') {
          authorized(req);
          let cursor: { createdAt: string; id: string } | null = null;
          if (url.searchParams.has('cursor')) {
            try {
              cursor = JSON.parse(Buffer.from(url.searchParams.get('cursor')!, 'base64url').toString());
              if (!cursor || typeof cursor.createdAt !== 'string' || !Number.isFinite(Date.parse(cursor.createdAt)) || typeof cursor.id !== 'string' || !/^AFG-[a-f0-9-]{36}$/i.test(cursor.id)) throw new Error();
            } catch { return fail(400, 'Invalid inbox page. Refresh the inbox.'); }
          }
          const rows = cursor
            ? db.prepare('SELECT id, created_at, status, data, note, updated_at FROM reports WHERE created_at < ? OR (created_at = ? AND id < ?) ORDER BY created_at DESC, id DESC LIMIT 21').all(cursor.createdAt, cursor.createdAt, cursor.id)
            : db.prepare('SELECT id, created_at, status, data, note, updated_at FROM reports ORDER BY created_at DESC, id DESC LIMIT 21').all();
          const reports = rows.slice(0, 20).map(row => ({ id: row.id, createdAt: row.created_at, status: row.status, data: JSON.parse(row.data as string), note: row.note, updatedAt: row.updated_at, photos: db.prepare('SELECT id FROM photos WHERE report_id = ?').all(row.id as string).map(p => p.id) }));
          const last = reports.at(-1);
          return json(res, 200, { reports, nextCursor: rows.length > 20 && last ? Buffer.from(JSON.stringify({ createdAt: last.createdAt, id: last.id })).toString('base64url') : null });
        }
        const photoMatch = path.match(/^\/api\/reports\/(AFG-[\da-f-]+)\/photos\/([\da-f-]+)$/i);
        if (photoMatch && req.method === 'GET') {
          authorized(req);
          const photo = db.prepare('SELECT bytes FROM photos WHERE report_id = ? AND id = ?').get(photoMatch[1], photoMatch[2]);
          if (!photo) fail(404, 'Photo not found.');
          res.writeHead(200, { 'Content-Type': 'image/jpeg', 'Content-Disposition': 'inline; filename="report-photo.jpg"' });
          return res.end(photo!.bytes);
        }
        const reportMatch = path.match(/^\/api\/reports\/(AFG-[\da-f-]+)$/i);
        if (reportMatch && req.method === 'PATCH') {
          authorized(req);
          let input: { status: string; note: string; updatedAt: string };
          try { input = JSON.parse((await body(req, 16000)).toString()); } catch { return fail(400, 'Check the review update.'); }
          if (!input || !statuses.includes(input.status as typeof statuses[number]) || typeof input.note !== 'string' || input.note.length > 3000 || typeof input.updatedAt !== 'string' || !Number.isFinite(Date.parse(input.updatedAt))) fail(400, 'Choose a valid status and a note under 3,000 characters.');
          // Every successful edit advances the revision, even within one millisecond.
          const now = new Date(Math.max(Date.now(), Date.parse(input.updatedAt) + 1)).toISOString();
          db.exec('BEGIN IMMEDIATE');
          try {
            const result = db.prepare('UPDATE reports SET status = ?, note = ?, updated_at = ? WHERE id = ? AND updated_at = ?').run(input.status, input.note, now, reportMatch[1], input.updatedAt);
            if (!result.changes) fail(409, 'This report changed or no longer exists. Refresh the inbox before updating.');
            db.prepare('INSERT INTO review_events VALUES (?, ?, ?, ?)').run(reportMatch[1], now, input.status, input.note);
            db.exec('COMMIT');
          } catch (error) { db.exec('ROLLBACK'); throw error; }
          return json(res, 200, { updatedAt: now });
        }
        return fail(404, 'This reporting endpoint does not exist.');
      }
      if (!options.staticDir || !['GET', 'HEAD'].includes(req.method ?? '')) return fail(404, 'Not found.');
      const root = resolve(options.staticDir); const decoded = decodeURIComponent(path);
      if (decoded.split('/').some(p => p.startsWith('.'))) return fail(404, 'Not found.');
      let file = resolve(root, '.' + decoded);
      if (!file.startsWith(root + sep) && file !== root) return fail(404, 'Not found.');
      if (file === root || !extname(file)) file = resolve(root, 'index.html');
      const types: Record<string, string> = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.wasm': 'application/wasm' };
      let bytes: Buffer; try { bytes = await readFile(file); } catch { return fail(404, 'Not found.'); }
      res.setHeader('Content-Type', types[extname(file)] ?? 'application/octet-stream');
      res.end(req.method === 'HEAD' ? undefined : bytes);
    } catch (error) {
      if (!res.headersSent) json(res, error instanceof HttpError ? error.status : 500, { error: error instanceof HttpError ? error.message : 'The report could not be saved. Please try again.' });
      else res.end();
    }
  });
  server.requestTimeout = 30000; server.headersTimeout = 10000;
  server.on('close', () => db.close());
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  process.umask(0o077);
  const local = process.env.NODE_ENV !== 'production';
  const dir = resolve(process.env.REPORT_DATA_DIR ?? '.reports');
  mkdirSync(dir, { recursive: true, mode: 0o700 });
  const tokenPath = resolve(dir, 'reviewer-token');
  let token = process.env.REPORT_REVIEW_TOKEN;
  if (!token && local) {
    if (!existsSync(tokenPath)) writeFileSync(tokenPath, randomBytes(32).toString('hex'), { mode: 0o600 });
    token = readFileSync(tokenPath, 'utf8').trim();
  }
  if (!token || (!local && !process.env.REPORT_PUBLIC_ORIGIN?.startsWith('https://'))) throw new Error('Set REPORT_REVIEW_TOKEN and an HTTPS REPORT_PUBLIC_ORIGIN for production.');
  const port = Number(process.env.REPORT_PORT ?? process.env.PORT ?? 4187);
  const server = createReportingServer({ databasePath: resolve(dir, 'reports.sqlite'), reviewerToken: token, publicOrigin: process.env.REPORT_PUBLIC_ORIGIN ?? 'http://127.0.0.1:4173', staticDir: process.env.REPORT_STATIC_DIR, local, trustRailwayProxy: process.env.REPORT_TRUST_RAILWAY_PROXY === 'true' && Boolean(process.env.RAILWAY_PROJECT_ID) });
  server.listen(port, process.env.REPORT_HOST ?? '127.0.0.1', () => console.log(`Reporting service on port ${port}. ${local ? 'Local review key: .reports/reviewer-token' : 'Production mode.'}`));
  for (const signal of ['SIGINT', 'SIGTERM'] as const) process.on(signal, () => server.close(() => process.exit(0)));
}
