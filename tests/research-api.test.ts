import test from 'node:test';
import assert from 'node:assert/strict';
import { researchApi } from '../src/research-api.ts';

test('source request timeout releases a stalled fetch without retrying', async t => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  let calls = 0;
  t.mock.method(globalThis, 'fetch', (_url: string, init: RequestInit) => {
    calls++;
    return new Promise((_resolve, reject) => init.signal!.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError'))));
  });
  const pending = assert.rejects(researchApi('/api/search?q=water'), /taking too long/);
  t.mock.timers.tick(30_000);
  await pending;
  assert.equal(calls, 1);
});

test('answer timeout also covers a stalled response body', async t => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  t.mock.method(globalThis, 'fetch', async (_url: string, init: RequestInit) => new Response(new ReadableStream({
    start(controller) { init.signal!.addEventListener('abort', () => controller.error(new DOMException('Aborted', 'AbortError'))); },
  })));
  const pending = assert.rejects(researchApi('/api/chat', { method: 'POST' }), /taking too long/);
  await Promise.resolve();
  t.mock.timers.tick(115_000);
  await pending;
});

test('navigation cancellation stays silent and does not become a timeout error', async t => {
  const parent = new AbortController();
  t.mock.method(globalThis, 'fetch', (_url: string, init: RequestInit) => new Promise((_resolve, reject) => {
    init.signal!.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
  }));
  const pending = assert.rejects(researchApi('/api/search?q=water', { signal: parent.signal }), { name: 'AbortError' });
  parent.abort();
  await pending;
});

test('already cancelled requests never reach the service', async t => {
  const fetch = t.mock.method(globalThis, 'fetch');
  await assert.rejects(researchApi('/api/chat', { signal: AbortSignal.abort() }), { name: 'AbortError' });
  assert.equal(fetch.mock.callCount(), 0);
});

test('network failures give a useful recovery message', async t => {
  t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('Failed to fetch'); });
  await assert.rejects(researchApi('/api/search?q=water'), /Check your connection and try again/);
});

test('server limits and malformed responses remain failures', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => new Response(JSON.stringify({ detail: 'Daily answer limit reached.' }), { status: 429 }));
  await assert.rejects(researchApi('/api/chat'), /Daily answer limit reached/);
  fetch.mock.mockImplementation(async () => new Response('<html>upstream unavailable</html>'));
  await assert.rejects(researchApi('/api/search?q=water'), /could not respond/);
});

test('successful requests preserve data and request options', async t => {
  t.mock.method(globalThis, 'fetch', async (_url: string, init: RequestInit) => {
    assert.equal(init.method, 'POST');
    assert.equal(init.body, '{"question":"water"}');
    return new Response(JSON.stringify({ status: 'answered', paragraphs: [] }));
  });
  assert.deepEqual(await researchApi('/api/chat', { method: 'POST', body: '{"question":"water"}' }), { status: 'answered', paragraphs: [] });
});
