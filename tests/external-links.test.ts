import {test} from 'node:test';
import assert from 'node:assert/strict';
import {isExternalWebsite} from '../src/external-links';

test('offsite web links open separately, including protocol-relative URLs', () => {
  for (const href of ['https://forest.goa.gov.in/contact-us', '//goa.gov.in/', 'http://127.0.0.1:4176/map']) {
    assert.equal(isExternalWebsite(href, 'http://127.0.0.1:4173'), true);
  }
});
test('local routes, anchors and non-web actions stay in their normal context', () => {
  for (const href of ['/ask', '#source-2', '?topic=Water', 'http://127.0.0.1:4173/library', 'tel:08322228772', 'mailto:info@actforgoa.org', 'blob:http://127.0.0.1:4173/example', '', 'https://[invalid']) {
    assert.equal(isExternalWebsite(href, 'http://127.0.0.1:4173'), false);
  }
});
