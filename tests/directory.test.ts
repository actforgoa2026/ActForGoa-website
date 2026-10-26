import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { directoryLinks, directoryMapUrl, directoryTags, enrichDirectory } from '../src/directory';
import { publicCatalogue } from '../src/public-record';
import { lexicalSearch } from '../src/search';
import type { RecordItem } from '../src/types';

const originals: RecordItem[] = JSON.parse(readFileSync(new URL('../public/data/catalog.json', import.meta.url), 'utf8'));
const records = publicCatalogue(originals);

test('reviewed place details retain their sources without mutating the archived catalogue', () => {
  const source = originals.find(r => r.id === 'org-18')!;
  const snapshot = JSON.stringify(source);
  const enriched = enrichDirectory(source);
  assert.equal(enriched.locality, 'Panaji');
  assert.match(enriched.locations[0], /E-463/);
  assert.ok(enriched.directory?.sources.includes('https://goafoundation.org/contact/'));
  assert.equal(JSON.stringify(source), snapshot);
});

test('maps use encoded address searches and never turn rescue volunteers into place pins', () => {
  for (const contact of records.filter(r => r.kind === 'contact')) assert.equal(directoryMapUrl(contact), null);
  const place = records.find(r => r.id === 'org-2')!;
  const map = new URL(directoryMapUrl(place)!);
  assert.equal(map.searchParams.get('api'), '1');
  assert.ok(map.searchParams.get('query')!.includes('Mulga Vaddo'));
  assert.equal(directoryMapUrl({ ...place, locations: ['Goa'] }), null);
});

test('new photos have a local file, source credit and descriptive alt text', () => {
  for (const record of records) {
    const photo = record.directory?.photo;
    if (!photo) continue;
    assert.ok(existsSync(new URL('../public' + photo.src, import.meta.url)), photo.src);
    assert.ok(photo.credit && photo.alt && photo.sourcePage.startsWith('https://'));
    const sidecar = JSON.parse(readFileSync(new URL('../public' + photo.src + '.json', import.meta.url), 'utf8'));
    assert.equal(sidecar.source, photo.source);
  }
});

test('keywords and refreshed locations are searchable, and keyword groups contain the expected records', () => {
  const animals = records.filter(r => directoryTags(r).includes('Animal welfare'));
  assert.ok(animals.some(r => r.id === 'org-2'));
  assert.ok(animals.some(r => r.id === 'org-52'));
  assert.ok(!animals.some(r => r.id === 'org-91'));
  assert.ok(lexicalSearch(records, 'citizen science').some(r => r.record.id === 'org-206'));
  assert.ok(lexicalSearch(records, 'Socorro').some(r => r.record.id === 'org-142'));
});

test('direct links reject unsafe protocols, deduplicate destinations and keep source phone restrictions', () => {
  const record = records.find(r => r.id === 'org-2')!;
  const links = directoryLinks({ ...record, directory: { tags: [], sources: [], links: [
    { label: 'Unsafe', url: 'javascript:alert(1)' },
    { label: 'Phone', url: 'tel:1234567890' },
    { label: 'Website', url: 'https://www.wagoa.com/' },
    { label: 'Duplicate', url: 'https://www.wagoa.com/' },
  ] } });
  assert.deepEqual(links.map(l => l.label), ['Website']);
  for (const r of records) assert.deepEqual(r.phones, []);
  assert.equal(directoryLinks(records.find(r => r.id === 'org-17')!).length, 0);
});
