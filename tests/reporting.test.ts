import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import sharp from 'sharp';
import { createReportingServer } from '../server/reporting.ts';
import { validateReport, type ReportDraft } from '../shared/reporting.ts';

const token = 'test-only-review-key-not-a-real-secret-12345';
const draft: ReportDraft = { category: 'dumping', description: 'Synthetic test report: bags of waste beside the road.', observedAt: '2026-01-01T10:00:00.000Z', location: 'Test location, Goa', coordinates: { latitude: 15.5, longitude: 73.8 }, email: '', consent: true };
async function start(path: string, rateLimit = 100) {
  const server = createReportingServer({ databasePath: path, reviewerToken: token, publicOrigin: 'https://reports.test', local: true, rateLimit });
  await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve));
  const address = server.address() as { port: number };
  return { server, url: `http://127.0.0.1:${address.port}`, stop: () => new Promise<void>(resolve => server.close(() => resolve())) };
}
function form(report: unknown, images: { bytes: Uint8Array; type: string }[] = []) {
  const f = new FormData(); f.set('report', JSON.stringify(report));
  for (const image of images) f.append('photos', new Blob([image.bytes as BlobPart], { type: image.type }), 'sample.jpg');
  return f;
}
const auth = { Authorization: `Bearer ${token}` };
async function submit(url: string, report: unknown = draft, key = randomUUID(), images: { bytes: Uint8Array; type: string }[] = []) {
  return fetch(url + '/api/reports', { method: 'POST', headers: { 'Idempotency-Key': key }, body: form(report, images) });
}

test('reports and sanitized photos persist atomically, retries deduplicate, private reads require authentication', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'actforgoa-report-test-'));
  const path = join(dir, 'reports.sqlite'); let app = await start(path);
  try {
    const image = await sharp({ create: { width: 100, height: 80, channels: 3, background: '#193e32' } }).jpeg().withExif({ IFD0: { Artist: 'Synthetic private metadata' } }).toBuffer();
    const key = randomUUID();
    const response = await submit(app.url, draft, key, [{ bytes: image, type: 'image/jpeg' }]);
    assert.equal(response.status, 201); const receipt = await response.json(); assert.match(receipt.id, /^AFG-/);
    const retry = await submit(app.url, draft, key, [{ bytes: image, type: 'image/jpeg' }]);
    assert.equal(retry.status, 200); assert.equal((await retry.json()).id, receipt.id);
    assert.equal((await submit(app.url, { ...draft, description: 'A different incident description.' }, key)).status, 409);
    assert.equal((await fetch(app.url + '/api/reports/review')).status, 401);
    assert.equal((await fetch(app.url + '/api/reports/' + receipt.id)).status, 404);
    let inbox = await (await fetch(app.url + '/api/reports/review', { headers: auth })).json();
    assert.equal(inbox.reports.length, 1); assert.equal(inbox.reports[0].status, 'new'); assert.equal(inbox.reports[0].data.email, '');
    const photoPath = `/api/reports/${receipt.id}/photos/${inbox.reports[0].photos[0]}`;
    assert.equal((await fetch(app.url + photoPath)).status, 401);
    const photo = await fetch(app.url + photoPath, { headers: auth });
    assert.equal(photo.headers.get('cache-control'), 'no-store');
    const metadata = await sharp(Buffer.from(await photo.arrayBuffer())).metadata(); assert.equal(metadata.format, 'jpeg'); assert.equal(metadata.exif, undefined);
    const update = { status: 'in_review', note: 'Synthetic test review.', updatedAt: inbox.reports[0].updatedAt };
    assert.equal((await fetch(app.url + '/api/reports/' + receipt.id, { method: 'PATCH', headers: { ...auth, 'Content-Type': 'application/json' }, body: JSON.stringify(update) })).status, 200);
    assert.equal((await fetch(app.url + '/api/reports/' + receipt.id, { method: 'PATCH', headers: { ...auth, 'Content-Type': 'application/json' }, body: JSON.stringify(update) })).status, 409);
    await app.stop(); app = await start(path);
    inbox = await (await fetch(app.url + '/api/reports/review', { headers: auth })).json();
    assert.equal(inbox.reports.length, 1); assert.equal(inbox.reports[0].status, 'in_review'); assert.equal(inbox.reports[0].photos.length, 1);
  } finally { await app.stop(); rmSync(dir, { recursive: true, force: true }); }
});

test('invalid fields, forged images, excess photos and cross-origin requests never save reports', async () => {
  const app = await start(':memory:');
  try {
    for (const invalid of [{ ...draft, category: 'invented' }, { ...draft, coordinates: { latitude: 100, longitude: 0 } }, { ...draft, consent: false }, { ...draft, observedAt: '9999-01-01T10:00:00Z' }, { ...draft, location: '' }, { ...draft, email: 'bad' }]) assert.equal((await submit(app.url, invalid)).status, 400);
    assert.equal((await submit(app.url, draft, randomUUID(), [{ bytes: Buffer.from('<svg>not a photo</svg>'), type: 'image/jpeg' }])).status, 400);
    const photo = { bytes: Buffer.from('bad'), type: 'image/jpeg' };
    assert.equal((await submit(app.url, draft, randomUUID(), [photo, photo, photo, photo])).status, 400);
    assert.equal((await fetch(app.url + '/api/reports', { method: 'POST', headers: { Origin: 'https://attacker.test', 'Idempotency-Key': randomUUID() }, body: form(draft) })).status, 403);
    assert.equal((await fetch(app.url + '/api/reports', { method: 'POST', headers: { 'Idempotency-Key': randomUUID() }, body: 'not multipart' })).status, 415);
    const inbox = await (await fetch(app.url + '/api/reports/review', { headers: auth })).json(); assert.deepEqual(inbox.reports, []);
  } finally { await app.stop(); }
});

test('rate limits submission attempts and accepts a report without photos or contact', async () => {
  const app = await start(':memory:', 1);
  try { assert.equal((await submit(app.url)).status, 201); assert.equal((await submit(app.url)).status, 429); }
  finally { await app.stop(); }
});

test('shared validation rejects malformed coordinates and non-consenting reports', () => {
  assert.doesNotThrow(() => validateReport(draft));
  assert.throws(() => validateReport({ ...draft, coordinates: { latitude: '15', longitude: 73 } }));
  assert.throws(() => validateReport({ ...draft, consent: 'true' }));
});

test('retries retain their identity after revisiting review, but changed payloads get a new identity', async () => {
  const { createSubmissionIdentity } = await import('../shared/submission-identity.ts');
  let sequence = 0; const identity = createSubmissionIdentity(() => `submission-${++sequence}`);
  const first = identity(JSON.stringify([draft, ['photo-1']]));
  assert.equal(identity(JSON.stringify([{ ...draft }, ['photo-1']])), first);
  assert.notEqual(identity(JSON.stringify([{ ...draft, description: 'Changed details for this incident.' }, ['photo-1']])), first);
  assert.equal(sequence, 2);
  identity(JSON.stringify([draft, ['photo-2']])); assert.equal(sequence, 3);
});

test('cursor pagination stays stable when another report arrives between pages', async () => {
  const app = await start(':memory:');
  try {
    const ids = new Set<string>();
    for (let i = 0; i < 23; i++) ids.add((await (await submit(app.url)).json()).id);
    const page1 = await (await fetch(app.url + '/api/reports/review', { headers: auth })).json();
    assert.equal(page1.reports.length, 20); assert.ok(page1.nextCursor);
    await submit(app.url);
    const page2 = await (await fetch(app.url + '/api/reports/review?cursor=' + page1.nextCursor, { headers: auth })).json();
    assert.equal(page2.reports.length, 3); assert.equal(page2.nextCursor, null);
    assert.deepEqual(new Set([...page1.reports, ...page2.reports].map(r => r.id)), ids);
    assert.equal((await fetch(app.url + '/api/reports/review?cursor=invalid', { headers: auth })).status, 400);
  } finally { await app.stop(); }
});

test('CORS permits the configured site and blocks unrelated origins, including preflight', async () => {
  const app = await start(':memory:');
  try {
    const response = await fetch(app.url + '/api/reports', { method: 'OPTIONS', headers: { Origin: 'https://reports.test', 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'Idempotency-Key' } });
    assert.equal(response.status, 204); assert.equal(response.headers.get('access-control-allow-origin'), 'https://reports.test');
    assert.match(response.headers.get('access-control-allow-headers')!, /Idempotency-Key/);
    assert.equal((await fetch(app.url + '/api/reports', { method: 'OPTIONS', headers: { Origin: 'https://unrelated.test' } })).status, 403);
    const r = await fetch(app.url + '/api/reports/review', { headers: { Origin: 'https://reports.test' } });
    assert.equal(r.status, 401); assert.equal(r.headers.get('access-control-allow-origin'), 'https://reports.test');
  } finally { await app.stop(); }
});

test('review revisions advance within a single millisecond and malformed updates return 400', async t => {
  const app = await start(':memory:');
  try {
    const receipt = await (await submit(app.url)).json();
    const report = (await (await fetch(app.url + '/api/reports/review', { headers: auth })).json()).reports[0];
    const patch = (value: unknown) => fetch(app.url + '/api/reports/' + receipt.id, { method: 'PATCH', headers: { ...auth, 'Content-Type': 'application/json' }, body: JSON.stringify(value) });
    assert.equal((await patch(null)).status, 400);
    t.mock.method(Date, 'now', () => Date.parse(report.updatedAt));
    const change = { status: 'in_review', note: 'Checked.', updatedAt: report.updatedAt };
    const updated = await (await patch(change)).json();
    assert.ok(updated.updatedAt > report.updatedAt);
    assert.equal((await patch(change)).status, 409);
  } finally { t.mock.restoreAll(); await app.stop(); }
});

test('invalid calendar dates are rejected and forwarding headers are untrusted by default', async () => {
  assert.throws(() => validateReport({ ...draft, observedAt: '2026-02-30T10:00:00.000Z' }));
  const app = await start(':memory:', 1);
  try {
    for (const [i, expected] of [201, 429].entries()) {
      const r = await fetch(app.url + '/api/reports', { method: 'POST', headers: { 'Idempotency-Key': randomUUID(), 'X-Real-IP': `192.0.2.${i + 1}` }, body: form(draft) });
      assert.equal(r.status, expected);
    }
  } finally { await app.stop(); }
});
