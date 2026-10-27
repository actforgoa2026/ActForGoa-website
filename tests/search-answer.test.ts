import test from 'node:test';
import assert from 'node:assert/strict';
import { cachedSearchAnswer, checkedSearchAnswer, fetchSearchAnswer } from '../src/search-answer';

const citation = { id: 'passage-one', title: 'Official source', label: 'PDF page 4', reader_url: '/documents/0123456789abcdef01234567-0123456789ab?generation=version-one&page=4&passage=passage-one' };
const supported = { status: 'answered', paragraphs: [{ text: 'Supported source text.', citations: [citation.id] }], citations: [citation] };

test('short search answers require cited paragraphs and local source-reader links', () => {
  assert.deepEqual(checkedSearchAnswer(supported), supported);
  assert.deepEqual(checkedSearchAnswer({ status: 'insufficient_evidence', paragraphs: [], citations: [] }).paragraphs, []);
  for (const data of [null, {}, { ...supported, paragraphs: [] }, { ...supported, citations: [] },
    { ...supported, paragraphs: [{ text: 'Unsupported.', citations: ['invented'] }] },
    { ...supported, citations: [{ ...citation, reader_url: 'https://untrusted.example/source' }] },
    { ...supported, citations: [{ ...citation, reader_url: '//untrusted.example/source' }] },
    { ...supported, status: 'insufficient_evidence' }]) assert.throws(() => checkedSearchAnswer(data));
});

test('submitted searches use the corpus chat API in brief mode and reuse successful answers', async t => {
  const calls: { url: string; body?: string }[] = [];
  const providers: string[] = [];
  t.mock.method(globalThis, 'fetch', async (url: string, options?: RequestInit) => {
    calls.push({ url, body: options?.body as string | undefined });
    if (url === '/api/chat') assert.equal(providers.at(-1), 'Anthropic', 'Identify the configured provider before sending the question');
    return Response.json(url === '/api/status' ? { search_ready: true, chat_ready: true, provider_label: 'Anthropic' } : supported);
  });
  const question = 'test cached corpus answer';
  const signal = new AbortController().signal;
  assert.equal((await fetchSearchAnswer(question, signal, label => providers.push(label))).status, 'answered');
  assert.deepEqual(JSON.parse(calls[1].body!), { question, answer_style: 'brief' });
  assert.deepEqual(calls.map(c => c.url), ['/api/status', '/api/chat']);
  await fetchSearchAnswer('  ' + question + '  ', signal, label => providers.push(label));
  assert.equal(calls.length, 2, 'Opening a source and returning should not pay again');
  assert(cachedSearchAnswer(question));
  assert.deepEqual(providers, ['Anthropic', 'Anthropic']);
});

test('unconfigured AI makes no paid request; budget failure remains retryable', async t => {
  let configured = false; let chats = 0;
  t.mock.method(globalThis, 'fetch', async (url: string) => {
    if (url === '/api/status') return Response.json({ search_ready: true, chat_ready: configured });
    chats++;
    return Response.json({ detail: 'The answer allowance has been reached. You can still search and read the full sources.' }, { status: 429 });
  });
  const signal = new AbortController().signal;
  await assert.rejects(fetchSearchAnswer('test unavailable provider', signal), /temporarily unavailable/);
  assert.equal(chats, 0);
  configured = true;
  await assert.rejects(fetchSearchAnswer('test allowance exhausted', signal), /allowance/);
  assert.equal(cachedSearchAnswer('test allowance exhausted'), undefined);
});

test('an obsolete search cannot populate the answer cache after cancellation', async t => {
  const controller = new AbortController();
  t.mock.method(globalThis, 'fetch', async (url: string) => {
    if (url === '/api/status') return Response.json({ search_ready: true, chat_ready: true });
    controller.abort();
    return Response.json(supported);
  });
  await assert.rejects(fetchSearchAnswer('test cancelled search', controller.signal), { name: 'AbortError' });
  assert.equal(cachedSearchAnswer('test cancelled search'), undefined);
});


test('legal source limitations are retained and malformed notices cannot be silently dropped', () => {
  const notice = 'Saved legal sources are not verified consolidated current law.';
  assert.equal(checkedSearchAnswer({ ...supported, notice }).notice, notice);
  for (const malformed of [null, 7, { text: notice }, [notice]]) {
    assert.throws(() => checkedSearchAnswer({ ...supported, notice: malformed }), /source limitations/);
  }
});
