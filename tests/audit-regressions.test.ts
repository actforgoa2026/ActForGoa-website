import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createCatalogueLoader, needsCatalogue } from '../src/catalogue-loader';
import { catalogueFilters, searchDestination, showEmergencyShortcut } from '../src/search-navigation';
import { practicalGuides } from '../src/guides';
import { practicalGuideRecords } from '../src/guide-records';

test('search keeps the current collection and deliberate filters, but resets relevance scope', () => {
  assert.equal(searchDestination('/directory/archive', '?topic=Nature+%26+wildlife', 'snake rescue'), '/directory/archive?topic=Nature+%26+wildlife&q=snake+rescue');
  assert.equal(searchDestination('/directory', '?topic=Nature+%26+wildlife&scope=all', 'snake rescue'), '/directory?topic=Nature+%26+wildlife&q=snake+rescue');
  assert.equal(searchDestination('/library/', '?type=resource&q=trees', ' compost '), '/library?type=resource&q=compost');
  assert.equal(searchDestination('/search', '?q=waste&type=organisation', ''), '/search?type=organisation');
  assert.equal(searchDestination('/', '', 'waste & recycling'), '/search?q=waste+%26+recycling');
});

test('unknown URL filters cannot silently hide the whole catalogue', () => {
  assert.deepEqual(catalogueFilters('?topic=mistyped&type=obsolete'), { topic: '', type: 'all' });
  assert.deepEqual(catalogueFilters('?topic=Nature+%26+wildlife&type=organisation'), { topic: 'Nature & wildlife', type: 'organisation' });
});

test('medical and emergency searches offer official help independently of archived ranking', () => {
  for (const query of ['snake bit me', 'bitten by a cobra', 'snakebite first aid', 'dog bite', 'ambulance', 'police help', 'house on fire', 'child helpline', '112']) assert(showEmergencyShortcut(query), query);
  for (const query of ['snake in my garden', 'compost', 'fireflies', 'volunteer', 'snake plants', 'snake rescue']) assert(!showEmergencyShortcut(query), query);
});

test('independent pages do not fetch the catalogue, including on cold starts', async () => {
  const loader = createCatalogueLoader((async () => { throw new Error('Should not fetch'); }) as typeof fetch);
  for (const path of ['/ask', '/documents/source-id', '/directory', '/directory/example', '/crm', '/crm/example', '/emergency', '/emergency/', '/contact', '/get-involved', '/templates/03-rti-records-request', '/read/guide-farming', '/read/guide-sources', '/missing']) {
    assert(!needsCatalogue(path), path);
    assert.deepEqual(await loader(path), { records: [], error: false });
  }
  for (const path of ['/', '/search', '/directory/archive', '/library', '/about', '/read/org-27']) assert(needsCatalogue(path), path);
});

test('catalogue request is shared and sanitised, and is reused after an independent page', async () => {
  let calls = 0;
  const raw = JSON.parse(readFileSync('public/data/catalog.json', 'utf8')).slice(0, 2);
  const loader = createCatalogueLoader((async () => { calls++; return new Response(JSON.stringify(raw)); }) as typeof fetch);
  const [a, b] = await Promise.all([loader('/'), loader('/directory/archive')]);
  assert.equal(calls, 1);
  assert.equal(a, b);
  assert(!a?.error);
  assert(a?.records.every(record => record.phones.length === 0));
  await loader('/emergency');
  assert.equal(await loader('/search'), a);
  assert.equal(calls, 1);
});

test('opening explore directly loads the same collection as the homepage', async () => {
  let calls = 0;
  const raw = JSON.parse(readFileSync('public/data/catalog.json', 'utf8')).slice(0, 2);
  const loader = createCatalogueLoader((async () => { calls++; return new Response(JSON.stringify(raw)); }) as typeof fetch);
  const explored = await loader('/explore/');
  assert.equal(explored.error, false);
  assert(explored.records.length >= raw.length);
  assert.equal(calls, 1);
  assert.equal(await loader('/'), explored);
  assert.equal(calls, 1);
});

test('a failed catalogue request can recover on a later route', async () => {
  let calls = 0;
  const loader = createCatalogueLoader((async () => ++calls === 1 ? new Response('', { status: 503 }) : new Response('[]')) as typeof fetch);
  assert.equal((await loader('/'))?.error, true);
  assert.equal((await loader('/emergency'))?.error, false);
  assert.equal((await loader('/search'))?.error, false);
  assert.equal(calls, 2);
});

test('a stalled catalogue request times out rather than trapping navigation indefinitely', async () => {
  const loader = createCatalogueLoader(((_url, options) => new Promise((_resolve, reject) => {
    options?.signal?.addEventListener('abort', () => reject(new Error('Aborted')));
  })) as typeof fetch, 10);
  assert.equal((await loader('/'))?.error, true);
});

test('malformed catalogue responses recover into the explicit failure state', async () => {
  for (const body of ['not json', '{}', '[{}]']) {
    const loader = createCatalogueLoader((async () => new Response(body)) as typeof fetch);
    assert.equal((await loader('/'))?.error, true);
  }
});

test('the split guide search index exactly matches the published guides', () => {
  assert.deepEqual(practicalGuideRecords, practicalGuides);
});

test('verified source corrections do not rewrite archival evidence', async () => {
  const { publicRecord } = await import('../src/public-record');
  const records = JSON.parse(readFileSync('public/data/catalog.json', 'utf8'));
  const original = records.find((record: { id: string }) => record.id === 'resource-008a023335');
  const corrected = publicRecord(original);
  assert.match(original.title, /1976/);
  assert.match(corrected.title, /1972/);
  assert(corrected.editorialCorrection?.source.startsWith('https://www.indiacode.nic.in/'));
  assert.equal(corrected.documents[0].url, original.documents[0].url);
  const amendment = publicRecord(records.find((record: { id: string }) => record.id === 'resource-51740e8285'));
  assert(!amendment.text.includes('replaces the earlier'));
  assert(!amendment.text.includes('currently has four'));
});

test('expired consultation cards use historical wording while preserving the original article', async () => {
  const { publicRecord } = await import('../src/public-record');
  const records = JSON.parse(readFileSync('public/data/catalog.json', 'utf8'));
  const original = records.find((record: { id: string }) => record.id === 'wp-9389');
  const corrected = publicRecord(original);
  assert.match(original.summary, /is open until/);
  assert.match(corrected.title, /2025 archive/);
  assert.match(corrected.summary, /does not establish that submissions are open now/);
  assert.equal(corrected.blocks.length, original.blocks.length);
  assert.equal(corrected.source, original.source);
});
