import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import type { RecordItem } from '../src/types';
import { publicRecord, publicCatalogue, communityDescription } from '../src/public-record';
const records: RecordItem[] = JSON.parse(readFileSync(new URL('../public/data/catalog.json', import.meta.url), 'utf8'));
test('public presentation removes phone fields and inline numbers without changing source data', () => {
  for (const record of records) {
    const original = JSON.stringify(record);
    const view = publicRecord(record);
    assert.deepEqual(view.phones, []);
    const prose = [view.summary, view.text, ...view.blocks.map(block => block.text)].join(' ').replace(/\D/g, '');
    for (const phone of record.phones) {
      const digits = phone.display.replace(/\D/g, '');
      if (digits.length >= 7) assert.ok(!prose.includes(digits), `${record.id} exposes ${digits}`);
    }
    assert.equal(JSON.stringify(record), original);
  }
});
test('community descriptions use real work and are explicit when a biography is missing', () => {
  assert.match(communityDescription(publicRecord(records.find(record => record.id === 'org-206')!)), /environmental education/);
  assert.match(communityDescription(publicRecord(records.find(record => record.id === 'org-187')!)), /description of their work is not available/);
  const volunteer = publicRecord(records.find(record => record.kind === 'contact')!);
  assert.match(communityDescription(volunteer), /Snake rescue volunteer/);
  assert.ok(!/\d{7,}/.test(communityDescription(volunteer)));
});
test('restored photo galleries resolve to local files with source provenance', () => {
  for (const record of records) {
    const images = record.images ?? [];
    assert.equal(new Set(images.map(image => image.src)).size, images.length);
    for (const image of images) {
      assert.ok(existsSync(new URL('../public' + image.src, import.meta.url)), image.src);
      assert.ok(image.source.startsWith('https://actforgoa.org/'));
    }
  }
});

test('public catalogue hides raw landlines and spaced switchboard numbers while preserving dates and postal codes', () => {
  const views = publicCatalogue(records);
  const snake = views.find(record => record.id === 'resource-590480849c')!;
  assert.ok(!/\d{7,}/.test(snake.blocks.map(block => block.text).join(' ')));
  const rights = views.find(record => record.id === 'resource-6b880a7ef2')!;
  assert.ok(!rights.text.includes('022 4072 7382'));
  assert.ok(!rights.text.includes('98201 22602'));
  const fixture = { ...records[0], text: 'Published 22 October 2026, updated 2026-10-22, Panjim 403001.', blocks: [] };
  assert.equal(publicRecord(fixture).text, fixture.text);
});
