import type { ServerResponse } from 'node:http';

export async function forwardSatellite(path: string, method: string, actor: string, body: unknown, res: ServerResponse,
  options: {origin?: string; token?: string; local?: boolean; fetcher?: typeof fetch} = {}) {
  const fail = (status: number, error: string) => { res.writeHead(status, {'Content-Type':'application/json'}); res.end(JSON.stringify({error})); };
  const route = path.replace('/api/admin/satellite', '');
  if (!((method === 'GET' && /^\/(?:status|jobs\/[a-f0-9-]{36})$/.test(route)) || (method === 'POST' && /^\/(?:plan|catalog|compare)$/.test(route)))) return fail(404,'Satellite route not found.');
  const raw = options.origin ?? process.env.SATELLITE_API_ORIGIN;
  const token = options.token ?? process.env.SATELLITE_SERVICE_TOKEN;
  let origin: URL;
  try {
    origin = new URL(raw || '');
    const local = options.local && origin.protocol === 'http:' && ['localhost','127.0.0.1'].includes(origin.hostname);
    if ((!local && origin.protocol !== 'https:') || origin.pathname !== '/' || origin.search || origin.hash || origin.username || origin.password) throw new Error();
  } catch { return fail(503,'Satellite monitoring is not connected yet. The map and source links remain available.'); }
  if (!token || token.length < 32) return fail(503,'Satellite service authentication is not configured yet.');
  try {
    const response = await (options.fetcher ?? fetch)(origin.origin + route, {
      method, redirect:'manual', signal:AbortSignal.timeout(55000),
      headers:{'Authorization':`Bearer ${token}`,'Content-Type':'application/json','X-Actor-ID':actor},
      ...(body !== undefined ? {body:JSON.stringify(body)} : {}),
    });
    if (response.status >= 300 && response.status < 400) return fail(502,'The satellite service returned an unexpected redirect.');
    const chunks: Uint8Array[] = [];
    let size = 0;
    const reader = response.body?.getReader();
    if (reader) {
      for (;;) {
        const {done, value} = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > 4 * 1024 * 1024) {
          await reader.cancel();
          return fail(502,'This comparison response is too large. Select a smaller area.');
        }
        chunks.push(value);
      }
    }
    res.writeHead(response.status,{'Content-Type':'application/json; charset=utf-8'});
    res.end(Buffer.concat(chunks));
  } catch { return fail(502,'The satellite service could not respond. Try again shortly.'); }
}
