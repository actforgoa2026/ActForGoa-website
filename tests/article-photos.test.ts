import {test} from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';
import {articlePhoto, supplementalPhoto} from '../src/article-photos';
import type {RecordItem} from '../src/types';

const catalogue = JSON.parse(readFileSync(new URL('../public/data/catalog.json', import.meta.url), 'utf8')) as RecordItem[];
test('every archived article has a local cover while original images retain precedence', () => {
  for (const record of catalogue.filter(r => ['story', 'resource', 'page'].includes(r.kind))) {
    const photo = articlePhoto(record);
    assert.ok(photo, record.id);
    if (record.image) assert.equal(photo.src, record.image);
    else {
      assert.ok(existsSync(new URL('../public' + photo.src, import.meta.url)), photo.src);
      assert.ok(photo.credit && photo.license && photo.licenseUrl && photo.source);
    }
  }
});
test('supplemental covers match topics and never impersonate a directory organisation', () => {
  assert.match(supplementalPhoto('Composting food waste').src, /paddy/);
  assert.match(supplementalPhoto('Goa mangroves').src, /mangrove/);
  assert.match(supplementalPhoto('Goan heritage').src, /panaji/);
  const organisation = catalogue.find(r => r.kind === 'organisation')!;
  assert.equal(articlePhoto({...organisation, image:'', images:[], directory:undefined}), undefined);
});
