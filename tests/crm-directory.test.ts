import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { crmDirectoryDetails, crmDirectoryLinks, crmDirectoryMapUrl, crmDirectoryTags } from '../src/crm-directory';
import { directoryFacets, filterRecords, filtersFrom, type CRMSnapshot } from '../src/crm-model';
import { directoryMatches } from '../src/mcp-search';
import mapping from '../src/content/crm-directory-map.json';

const snapshot: CRMSnapshot = JSON.parse(readFileSync(new URL('../public/data/crm.json', import.meta.url), 'utf8'));
const records = snapshot.records;
const wag = records.find(r => r.record_id === 'goa-b4193b3b40c7')!;

test('website search consolidates corporation listings and repairs malformed website links', () => {
  const search = (collection: string) => filterRecords(records, new Set(), filtersFrom(new URLSearchParams({ q: 'waste', collection })), {});
  const all = directoryMatches(search('all'), Number.MAX_SAFE_INTEGER);
  const corp = all.filter(({record}) => /^goa waste management corporation$/i.test(record.name));
  assert.equal(corp.length, 1);
  assert.equal(corp[0].additional[0].record_id, 'goa-b3f711f6b7f3');
  const facets = directoryFacets(records, new Set(), filtersFrom(new URLSearchParams({ q: 'waste', collection: 'all' })), {}, undefined, true);
  assert.equal(facets.collection.all, all.length);
  assert.equal(facets.type[''], all.length);
  assert.ok(directoryMatches(search('government'), Number.MAX_SAFE_INTEGER).some(({record}) => record.record_id === 'goa-b3f711f6b7f3'));
  const office = records.find(r => r.record_id === 'goa-80732e1537a8')!;
  assert.equal(crmDirectoryLinks(office).find(link => link.label === 'Website')?.url, 'https://dstwm.goa.gov.in/');
  assert.ok(!crmDirectoryLinks({ ...office, website_url: 'javascript:alert(1)' }).some(link => link.label === 'Website'));
});

test('CRM enrichments join exact source identities and preserve the research snapshot', () => {
  const before = JSON.stringify(snapshot);
  for (const [id, entry] of Object.entries(mapping)) {
    const record = records.find(r => r.record_id === id)!;
    assert.ok(record, id);
    assert.ok(record.notes.includes(`Connections API, entry ${entry.catalogueId.slice(4)}.`), id);
    assert.ok(crmDirectoryDetails(record), id);
    assert.equal(crmDirectoryDetails({ ...record, source_urls: 'https://example.org/unrelated' }), undefined);
    assert.equal(crmDirectoryDetails({ ...record, record_type: 'individual' }), undefined);
  }
  assert.equal(records.filter(r => crmDirectoryDetails(r)?.photo).length, 7);
  assert.equal(JSON.stringify(snapshot), before);
});

test('every displayed CRM work tag leads to results containing its source record', () => {
  for (const record of records.filter(r => crmDirectoryDetails(r))) {
    for (const tag of crmDirectoryTags(record)) {
      const filters = filtersFrom(new URLSearchParams({ collection: 'all', q: tag }));
      assert.ok(filterRecords([record], new Set(), filters, {}).some(r => r.record_id === record.record_id), `${record.name}: ${tag}`);
    }
  }
});

test('reviewed labels retain the CRM specialisms, including a fourth focus area', () => {
  for (const id of ['goa-86ed573c2125', 'goa-e8495fb5ba0a']) {
    const tags = crmDirectoryTags(records.find(r => r.record_id === id)!);
    for (const focus of ['Environmental law', 'Forests', 'Mining', 'Biodiversity']) assert.ok(tags.includes(focus), `${id}: ${focus}`);
    assert.equal(new Set(tags.map(t => t.toLowerCase())).size, tags.length);
  }
});

test('CRM maps require a reviewed organisation address; historical records never get outreach actions', () => {
  assert.match(new URL(crmDirectoryMapUrl(wag)!).searchParams.get('query')!, /Mulga Vaddo/);
  for (const record of records.filter(r => r.record_type !== 'organization')) assert.equal(crmDirectoryMapUrl(record), undefined);
  const historical = { ...wag, activity_status: 'deceased_historical_record' };
  assert.deepEqual(crmDirectoryLinks(historical), []);
  assert.equal(crmDirectoryMapUrl(historical), undefined);
  const unsafe = { ...wag, website_url: 'javascript:alert(1)', volunteer_url: 'tel:12345', instagram_url: 'data:text/html,unsafe' };
  assert.ok(crmDirectoryLinks(unsafe).every(l => /^https?:/.test(l.url)));
});

test('reviewed duplicate groups preserve source records, separate roles and facet counts', async () => {
  const { duplicateGroups } = await import('../src/directory-quality');
  const { directoryMatches } = await import('../src/mcp-search');
  for (const group of duplicateGroups) {
    const originals = group.map(id => records.find(r => r.record_id === id)!);
    assert.ok(originals.every(Boolean), group.join(','));
    const result = directoryMatches(originals, 20);
    assert.equal(result.length, 1);
    assert.deepEqual([result[0].record.record_id, ...result[0].additional.map(r => r.record_id)].sort(), [...group].sort());
  }
  const distinct = records.filter(r => ['goa-e018231c8b9a', 'goa-d6da3f0e0f38'].includes(r.record_id));
  assert.equal(directoryMatches(distinct, 20).length, 2);
  const filters = filtersFrom(new URLSearchParams({collection:'all', q:'Shri Abhir Hede'}));
  const found = directoryMatches(filterRecords(records, new Set(), filters, {}), 100);
  const facets = directoryFacets(records, new Set(), filters, {}, undefined, true);
  assert.equal(facets.collection.all, found.length);
});

test('website audit repairs known transcription errors and suppresses non-website values', async () => {
  const { directoryWebsite } = await import('../src/directory-quality');
  const expected: Record<string,string> = {
    'goa-6d8e5298ec90':'https://www.cpwd.gov.in',
    'goa-fe7e9c7a7d57':'https://egov.goa.nic.in/dslr',
    'goa-bb1b92ba4e69':'http://goasacs.nic.in',
    'goa-bcecb799534c':'https://clm.goa.gov.in',
    'goa-1df5248b2938':'https://passportindia.gov.in',
    'goa-80732e1537a8':'https://www.dstegoa.goa.gov.in',
  };
  for (const [id, url] of Object.entries(expected)) {
    const record = records.find(r => r.record_id === id)!;
    assert.equal(directoryWebsite(record.website_url), url);
    assert.equal(crmDirectoryLinks(record).find(link => link.label === 'Website')?.url, id === 'goa-80732e1537a8' ? 'https://dstwm.goa.gov.in/' : url);
  }
  const bad = records.find(r => r.name.startsWith('MINISTRY OF SHIPPING DIRECTORATE GENERAL'))!;
  assert.equal(directoryWebsite(bad.website_url), '');
  assert.equal(crmDirectoryLinks(bad).find(link => link.label === 'Website'), undefined);
  assert.equal(directoryWebsite('javascript:alert(1)'), '');
  assert.equal(directoryWebsite('https://example.org/path'), 'https://example.org/path');
});

test('live check evidence and replacements preserve uncertainty and future source updates', async () => {
  const {directoryWebsite, websiteEvidence, duplicateGroup} = await import('../src/directory-quality');
  assert.equal(directoryWebsite('https://www.dstegoa.goa.gov.in','goa-80732e1537a8'), 'https://dstwm.goa.gov.in/');
  assert.equal(websiteEvidence('https://www.dstegoa.goa.gov.in','goa-80732e1537a8').source, 'https://www.goa.gov.in/department/department-of-science-and-technology-and-waste-management/');
  assert.equal(directoryWebsite('https://new.example.org/', 'goa-80732e1537a8'), 'https://new.example.org/');
  assert.equal(directoryWebsite('https://www.ahvs.goa.gov.in'), 'https://ahvs.goa.gov.in');
  assert.equal(websiteEvidence('https://www.ahvs.goa.gov.in').status, 'responded');
  assert.equal(websiteEvidence('https://www.arcgoa.in/').status, 'unverified');
  assert.equal(websiteEvidence('https://not-in-snapshot.example.org').status, 'not_checked');
  assert.ok(duplicateGroup('goa-a1f1014604fa').includes('goa-b8b44e35e553'));
  assert.ok(!duplicateGroup('goa-f80172c68298').includes('goa-d6da3f0e0f38'));
});
