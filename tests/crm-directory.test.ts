import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { crmDirectoryDetails, crmDirectoryLinks, crmDirectoryMapUrl, crmDirectoryTags } from '../src/crm-directory';
import { filterRecords, filtersFrom, type CRMSnapshot } from '../src/crm-model';
import mapping from '../src/content/crm-directory-map.json';

const snapshot: CRMSnapshot = JSON.parse(readFileSync(new URL('../public/data/crm.json', import.meta.url), 'utf8'));
const records = snapshot.records;
const wag = records.find(r => r.record_id === 'goa-b4193b3b40c7')!;

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
