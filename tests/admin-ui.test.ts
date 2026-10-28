import test from 'node:test';
import assert from 'node:assert/strict';
import {adminApi, AdminApiError} from '../src/admin-api.ts';
import {curationRecords, emptyPost, filterCuration, parseTags, postChanged, slugFromTitle, validatePost} from '../src/admin-model.ts';
import type {CRMRecord} from '../src/crm-model.ts';
import type {RecordItem} from '../src/types.ts';

test('curation keeps canonical identities and source limitations while matching all query terms', () => {
  const crm = [
    {record_id: 'goa-mangroves', name: 'Mangrove volunteers', collection: 'community', record_type: 'organisation', summary: 'Restore coastal habitats', focus_areas: 'water | wildlife', activity_status: 'historical_activity_only', verification_status: 'published', source_urls: 'https://example.org/source'},
    {record_id: 'goa-council', name: 'Village council', collection: 'government', record_type: 'government', summary: 'Community water supply', focus_areas: 'water', activity_status: 'recent_public_contact_listing', verification_status: 'published'},
  ] as CRMRecord[];
  const catalogue = [{id: 'guide-water', title: 'Water protection', kind: 'resource', summary: 'A local water guide', topics: ['Water & environment'], source: 'https://example.org/water', verification: 'Draft pending legal review'}] as RecordItem[];
  const records = curationRecords(crm, catalogue);
  assert.equal(records.length, 3);
  assert.equal(records[0].href, '/directory/goa-mangroves');
  assert.match(records[0].evidence, /Historical/);
  assert.match(records[1].evidence, /tenure unconfirmed/);
  assert.equal(records[2].href, '/read/guide-water');
  assert.equal(records[2].evidence, 'Draft pending legal review');
  const stars = new Set(['goa-mangroves']);
  assert.deepEqual(filterCuration(records, 'water supply', '', stars, false).map(record => record.id), ['goa-council']);
  assert.deepEqual(filterCuration(records, 'water supply', '', stars, true), []);
  assert.deepEqual(filterCuration(records, 'water', 'resource', stars, false).map(record => record.id), ['guide-water']);
});

test('editor detects unsaved content and validates publication separately from drafts', () => {
  const draft = {...emptyPost(), slug: 'goa-story'};
  assert.equal(validatePost(draft), '');
  assert.match(validatePost(draft, true), /title, short introduction and story/);
  const saved = {...draft, title: 'Monsoon work', excerpt: 'A village update.', body: 'The team cleared the drains.', tags: ['Water']};
  assert.equal(postChanged({...saved, tags: ['Water']}, saved), false);
  assert.equal(postChanged({...saved, tags: ['Water', 'Community']}, saved), true);
  assert.equal(validatePost(saved, true), '');
  assert.match(validatePost({...saved, slug: '../admin'}), /URL name/);
  assert.match(validatePost({...saved, tags: Array.from({length: 13}, (_, index) => `Tag ${index}`)}), /12 tags/);
  assert.equal(slugFromTitle('São João: Goa & community'), 'sao-joao-goa-community');
  assert.deepEqual(parseTags('Water, Community, Water, ,'), ['Water', 'Community']);
});

test('story URLs cannot shadow the original archive route', () => {
  const draft = {...emptyPost(), title: 'Archive', excerpt: 'An update.', body: 'A story.', slug: 'archive'};
  assert.match(validatePost(draft), /reserved/);
  assert.match(validatePost(draft, true), /reserved/);
  assert.match(validatePost({...draft, slug: ' Archive '}), /reserved/);
  assert.equal(slugFromTitle('Archive'), 'archive-story');
  assert.equal(slugFromTitle('ARCHIVE!'), 'archive-story');
  assert.equal(validatePost({...draft, slug: slugFromTitle(draft.title)}, true), '');
  assert.equal(validatePost({...draft, slug: 'archive-news'}, true), '');
});

test('admin writes send cookie credentials and CSRF without URL secrets', async t => {
  let requestUrl = ''; let requestOptions: RequestInit | undefined;
  t.mock.method(globalThis, 'fetch', async (url: string | URL | Request, options?: RequestInit) => {
    requestUrl = String(url); requestOptions = options;
    return new Response(JSON.stringify({stars: []}), {status: 200, headers: {'Content-Type': 'application/json'}});
  });
  await adminApi('/api/admin/stars', {method: 'PUT', csrfToken: 'test-csrf', body: {recordId: 'goa-water', starred: true}});
  assert.equal(requestUrl, '/api/admin/stars');
  assert.equal(requestOptions?.credentials, 'same-origin');
  assert.equal(new Headers(requestOptions?.headers).get('X-CSRF-Token'), 'test-csrf');
  assert.equal(requestOptions?.body, JSON.stringify({recordId: 'goa-water', starred: true}));
});

test('admin requests preserve conflict/auth errors and reject a disconnected service', async t => {
  t.mock.method(globalThis, 'fetch', async () => new Response(JSON.stringify({error: 'The story changed. Reload before saving.'}), {status: 409}));
  await assert.rejects(adminApi('/api/admin/posts/a'), (error: unknown) => error instanceof AdminApiError && error.status === 409 && /Reload/.test(error.message));
  t.mock.restoreAll();
  t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('Failed to fetch'); });
  await assert.rejects(adminApi('/api/admin/session'), (error: unknown) => error instanceof AdminApiError && error.status === 0 && /reach the team workspace/.test(error.message));
});

test('aborted requests do not become misleading service errors', async t => {
  const controller = new AbortController(); controller.abort();
  t.mock.method(globalThis, 'fetch', async (_url: string | URL | Request, options?: RequestInit) => { assert.equal(options?.signal?.aborted, true); throw new DOMException('Aborted', 'AbortError'); });
  await assert.rejects(adminApi('/api/admin/posts', {signal: controller.signal}), (error: unknown) => error instanceof DOMException && error.name === 'AbortError');
});
