import {test} from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';
import {articlePhoto, supplementalPhoto} from '../src/article-photos';
import type {RecordItem} from '../src/types';

const catalogue = JSON.parse(readFileSync(new URL('../public/data/catalog.json', import.meta.url), 'utf8')) as RecordItem[];
test('article covers retain original imagery without filling missing covers with generic photos', () => {
 for (const record of catalogue) {
  const photo = articlePhoto(record);
  if (record.image) assert.equal(photo?.src, record.image, record.id);
  else if (record.images?.[0]?.src) assert.equal(photo?.src, record.images[0].src, record.id);
  else assert.equal(photo, undefined, record.id);
 }
});
test('supplemental landscapes are limited to named subjects, never broad tags or animal stories', () => {
 for (const title of ['Animal welfare in Goa', 'Environmental protection in Goa', 'Snake Rescue Volunteers in Goa', 'Composting food waste']) assert.equal(supplementalPhoto(title), undefined);
 for (const title of ['Goa mangroves', 'Paddy fields', 'Panaji streets', 'Vagator beach']) {
  const photo = supplementalPhoto(title)!;
  assert.ok(existsSync(new URL('../public' + photo.src, import.meta.url)), photo.src);
  assert.ok(photo.credit && photo.license && photo.licenseUrl && photo.source);
 }
});
