import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { activityLabel, backupJSON, emptyNote, exportCSV, directoryFacets, filterRecords, filtersFrom, isDue, mergeBackup, parseBackup, safeUrl, verification, type CRMSnapshot } from '../src/crm-model';

const data: CRMSnapshot = JSON.parse(readFileSync(new URL('../public/data/crm.json', import.meta.url), 'utf8'));
const ids = new Set(data.records.map(r => r.record_id));
const opportunities = new Set(data.opportunities.flatMap(r => r.related_record_ids.split(' | ')));
const filters = (query = '') => filtersFrom(new URLSearchParams(query));

test('published snapshot preserves records and relationship integrity without counting participation twice', () => {
  assert.equal(data.records.length, 3267); assert.equal(ids.size, 3267);
  assert.equal(data.records.filter(r => r.collection === 'community').length, 499);
  assert.equal(data.records.filter(r => r.collection === 'government').length, 2768);
  assert.equal(opportunities.size, 28);
  for (const r of data.records) {
    for (const id of r.related_record_ids.split(' | ').filter(Boolean)) assert.ok(ids.has(id));
    assert.ok(r.name && r.summary && r.source_urls && r.checked_on);
  }
});
test('search handles names, locality, normalized focus tags and combined filters', () => {
  const maria = filterRecords(data.records, opportunities, filters('q=maria'), {});
  assert.ok(maria.some(r => r.name === 'Maria Gomes (Maria Aunty)'));
  const results = filterRecords(data.records, opportunities, filters('location=Canacona&contact=phone'), {});
  assert.ok(results.length > 0); assert.ok(results.every(r => r.public_phone && (r.goa_location + r.jurisdiction).toLowerCase().includes('canacona')));
  assert.equal(filterRecords(data.records, opportunities, filters('q=unlikely-unmatched-person-1234'), {}).length, 0);
  assert.equal(filterRecords(data.records, opportunities, filters('collection=opportunities'), {}).length, 28);
  assert.equal(filterRecords(data.records, opportunities, filters('collection=all'), {}).length, 3267);
});
test('activity labels never turn undated listings or government listings into current verification', () => {
  const govt = data.records.find(r => r.collection === 'government')!;
  assert.equal(activityLabel(govt), 'Activity not assessed'); assert.equal(verification(govt), 'government');
  const undated = data.records.find(r => r.activity_status === 'current_primary_listing_undated')!;
  assert.equal(activityLabel(undated), 'Listed; activity undated');
  const deceased = data.records.find(r => r.activity_status === 'deceased_historical_record')!;
  assert.equal(emptyNote(deceased).stage, 'do_not_contact');
});
test('workspace backups round trip and merge without silently replacing existing notes', () => {
  const row = data.records[0], old = { ...emptyNote(row), notes: 'Keep my human correction', followUp: '2026-10-25' };
  const incoming = { ...old, notes: 'Imported version' };
  const stored = { [row.record_id]: old };
  assert.deepEqual(JSON.parse(JSON.stringify(parseBackup(backupJSON(stored)))), stored);
  assert.equal(mergeBackup(stored, { [row.record_id]: incoming }, false)[row.record_id].notes, old.notes);
  assert.equal(mergeBackup(stored, { [row.record_id]: incoming }, true)[row.record_id].notes, incoming.notes);
  assert.equal(isDue(old, '2026-10-25'), true);
  assert.equal(isDue({ ...old, stage: 'closed' }, '2026-10-25'), false);
  assert.equal(isDue({ ...old, stage: 'do_not_contact' }, '2026-10-25'), false);
  assert.equal(filterRecords(data.records, opportunities, filters('due=1&collection=all'), stored, '2026-10-25').length, 1);
});
test('reject malformed backups, impossible dates, prototype keys and unsafe URLs', () => {
  for (const value of ['null', '{}', '{"version":2,"records":{}}', '{"version":1,"records":{"__proto__":{}}}']) assert.throws(() => parseBackup(value));
  const id = data.records[0].record_id;
  for (const patch of [{ followUp: '2026-02-30' }, { stage: 'toString' }, { notes: 44 }]) assert.throws(() => parseBackup(JSON.stringify({ version: 1, records: { [id]: { ...emptyNote(data.records[0]), ...patch } } })));
  assert.equal(safeUrl('javascript:alert(1)'), ''); assert.equal(safeUrl('data:text/html,test'), '');
  assert.equal(safeUrl('https://example.org/path'), 'https://example.org/path');
});
test('filtered export retains provenance and escapes formula-like notes and phone values', () => {
  const row = data.records[0]; const csv = exportCSV([row], { [row.record_id]: { ...emptyNote(row), notes: '=HYPERLINK("https://example.org")\nquoted, note' } });
  assert.ok(csv.startsWith('\uFEFF')); assert.ok(csv.includes('"source_urls"'));
  assert.ok(csv.includes('"\'=HYPERLINK(""https://example.org"")\nquoted, note"'));
  assert.ok(csv.includes('"crm_follow_up"'));
});

test('search ranks exact and partial names before mentions while respecting explicit sort', () => {
  const base = data.records[0];
  const rows = [
    { ...base, record_id: 'goa-mention', name: 'A local project', summary: 'Works with Maria Gomes' },
    { ...base, record_id: 'goa-name', name: 'Maria Gomes', summary: 'Community work' },
    { ...base, record_id: 'goa-long', name: 'Maria Gomes Foundation', summary: 'Community work' },
  ];
  assert.deepEqual(filterRecords(rows, new Set(), filters('q=maria+gomes'), {}).map(r => r.record_id), ['goa-name', 'goa-long', 'goa-mention']);
  assert.equal(filterRecords(rows, new Set(), filters('q=mari+gom'), {})[0].record_id, 'goa-name');
  assert.equal(filterRecords(rows, new Set(), filters('q=maria&sort=name'), {})[0].record_id, 'goa-mention');
  assert.equal(filterRecords(rows, new Set(), filters('q=maria+nonexistent'), {}).length, 0);
});
test('search normalizes accents, apostrophes, hyphens and phone formatting', () => {
  const row = { ...data.records[0], name: 'José D’Souza', goa_location: 'Ona-Maulingem', public_phone: '+919876543210 | +918765432109' };
  for (const query of ['jose d\'souza', 'jose dsouza', 'ona maulingem', '+91 (98765) 43210', '98765-43210']) {
    assert.equal(filterRecords([row], new Set(), filters('q=' + encodeURIComponent(query)), {}).length, 1, query);
  }
  assert.equal(filterRecords([row], new Set(), filters('q=432108765'), {}).length, 0, 'cannot match across separate phone numbers');
});
test('invalid enum parameters recover safely and relevance is the default', () => {
  const value = filters('collection=bogus&stage=toString&contact=invalid&sort=bad&verification=constructor&activity=invalid');
  assert.equal(value.collection, 'community'); assert.equal(value.stage, ''); assert.equal(value.contact, '');
  assert.equal(value.verification, ''); assert.equal(value.activity, ''); assert.equal(value.sort, 'relevance');
});

test('facet counts predict replacements without silently dropping other filters', () => {
  const f = filters('q=goa&collection=all&focus=wildlife_rescue&contact=phone');
  const facets = directoryFacets(data.records, opportunities, f, {}, '2026-10-26');
  for (const [key, choices] of Object.entries({ collection: ['community', 'government', 'all', 'opportunities'], type: ['individual', 'organization'], focus: ['wildlife_rescue', 'waste', ''], contact: ['phone', 'email', 'missing'] })) {
    for (const value of choices) assert.equal(facets[key as keyof typeof facets][value] || 0, filterRecords(data.records, opportunities, { ...f, [key]: value }, {}, '2026-10-26').length, `${key}: ${value}`);
  }
  const row = data.records.find(r => r.collection === 'community')!;
  const workspace = { [row.record_id]: { ...emptyNote(row), followUp: '2026-10-26' } };
  const dueFilters = filters('due=1');
  assert.equal(directoryFacets(data.records, opportunities, dueFilters, workspace, '2026-10-26').due['1'], 1);
  assert.equal(filterRecords(data.records, opportunities, dueFilters, workspace, '2026-10-26').length, 1);
  assert.equal(directoryFacets(data.records, opportunities, dueFilters, workspace, '2026-10-25').due['1'] || 0, 0);
});
