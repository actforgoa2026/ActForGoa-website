import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { climatePlan, planTopics, planChapters, planPdfPage, planPageHref, searchPlanTopics, searchPlanChapters } from '../src/climate-plan';
import { createCatalogueLoader, needsCatalogue } from '../src/catalogue-loader';
import { homeSearchDestination } from '../src/home-search';
import { climatePlanResearch, climatePlanResearchPath, climatePlanReaderPath, isClimatePlanResearch } from '../src/climate-plan-research';

test('SAPCC questions and reading pin the same verified source edition', () => {
  assert.equal(climatePlanResearch.sha256, climatePlan.source.sha256);
  const ask = new URL(climatePlanResearchPath, 'https://example.test');
  const reader = new URL(climatePlanReaderPath, 'https://example.test');
  assert.equal(ask.pathname, '/ask/ecology');
  assert.equal(reader.pathname, `/documents/${ask.searchParams.get('document')}`);
  assert.equal(ask.searchParams.get('generation'), reader.searchParams.get('generation'));
  assert(isClimatePlanResearch(ask.searchParams.get('document')!, ask.searchParams.get('generation')!));
  assert(!isClimatePlanResearch(climatePlanResearch.documentId, 'another-generation'));
  assert(!isClimatePlanResearch('another-document', climatePlanResearch.generation));
  assert(!isClimatePlanResearch());
});

test('source PDF remains the reviewed 111-page spread edition and guide copies stay in sync', () => {
  const bytes = readFileSync('docs/climate/goa-sapcc-2023-2033.pdf');
  assert.equal(bytes.length, climatePlan.source.bytes);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), climatePlan.source.sha256);
  assert.equal(readFileSync('docs/climate/READING-GUIDE.md', 'utf8'), readFileSync('public/guides/goa-climate-plan.md', 'utf8'));
});

test('printed references resolve to the correct PDF spreads, including odd pages and the final map', () => {
  for (const [printed, physical] of [[19, 11], [25, 14], [76, 40], [77, 40], [132, 68], [133, 68], [141, 72], [153, 78], [162, 83], [163, 83], [194, 99], [218, 111]]) {
    assert.equal(planPdfPage(printed), physical);
    assert.equal(new URL(planPageHref(printed)).hash, `#page=${physical}`);
  }
  for (const invalid of [0, 3, 219, 1.5, NaN]) assert.throws(() => planPdfPage(invalid), RangeError);
  for (const reference of [...planChapters, ...planChapters.flatMap(c => c.children ?? []), ...planTopics.flatMap(t => [...t.references, ...t.actions.map(a => a.reference)])]) {
    assert(reference.start <= reference.end);
    assert(planPdfPage(reference.start) <= climatePlan.source.pdfPages);
    assert(planPdfPage(reference.end) <= climatePlan.source.pdfPages);
  }
});

test('resident searches find related subjects, agencies and selected actions without losing unknown-query empty states', () => {
  for (const [query, id] of [['salt water', 'water'], ['fish', 'farming'], ['heatwave', 'health'], ['solar', 'energy'], ['cycling', 'transport'], ['panchayat', 'homes'], ['groundwater mining', 'mining'], ['budget', 'funding']]) {
    assert(searchPlanTopics(query).some(topic => topic.id === id), query);
  }
  assert.equal(searchPlanTopics('  ').length, 13);
  assert.equal(searchPlanTopics('zzzz-nonexistent').length, 0);
  assert(searchPlanChapters('human health').some(chapter => chapter.id === '7'));
  assert(searchPlanChapters('committee').some(chapter => chapter.scanned));
  const ids = new Set(planTopics.map(topic => topic.id));
  assert.equal(ids.size, planTopics.length);
  assert(planTopics.every(topic => topic.related.every(id => ids.has(id))));
  assert.equal(planTopics.flatMap(topic => topic.actions).length, 26);
});

test('climate routes remain usable when the large catalogue is unavailable, and the guide joins library search', async () => {
  const loader = createCatalogueLoader((async () => new Response('[]')) as typeof fetch);
  for (const path of ['/climate-plan', '/climate-plan/water', '/read/goa-sapcc']) {
    assert.equal(needsCatalogue(path), false);
    assert.deepEqual(await loader(path), { records: [], error: false });
  }
  const catalogue = await loader('/library');
  assert.equal(catalogue.records.filter(record => record.id === 'goa-sapcc').length, 1);
  for (const query of ['SAPCC for Goa', 'Goa climate action plan', 'state action plan for climate change']) assert.equal(homeSearchDestination(query), '/climate-plan');
  assert.equal(homeSearchDestination('emergency flooding climate plan'), '/emergency');
});
