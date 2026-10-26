import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync, readdirSync} from 'node:fs';
import {guideDocuments, practicalGuides, guideHeadingId} from '../src/guides.ts';
import {lexicalSearch} from '../src/search.ts';
import {buildDiscoveryFeed} from '../src/discovery.ts';

test('published guides resolve every citation, internal route and downloadable file', () => {
 const ids = new Set(guideDocuments.map(g => g.id));
 assert.equal(practicalGuides.length, 5);
 assert.equal(readdirSync('public/guides/templates').length, 18);
 for (const guide of guideDocuments) {
  assert(existsSync('public' + guide.download));
  const definitions = new Set([...guide.markdown.matchAll(/^\[([^\]]+)\]:\s+https?:\/\/\S+/gm)].map(m => m[1]));
  for (const m of guide.markdown.matchAll(/\[[^\]]+\]\[([^\]]+)\]/g)) assert(definitions.has(m[1]), `${guide.id}: missing ${m[1]}`);
  for (const m of guide.markdown.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
   const href = m[1];
   if (href.startsWith('/read/')) assert(ids.has(href.slice(6)), href);
   else if (href.startsWith('/guides/')) assert(existsSync('public' + href), href);
   else assert(/^https?:\/\//.test(href) || href === '/library', `${guide.id}: unresolved ${href}`);
  }
  const headings = [...guide.markdown.matchAll(/^## (.+)$/gm)].map(m => guideHeadingId(m[1]));
  assert.equal(new Set(headings).size, headings.length, `${guide.id}: duplicate section anchors`);
  assert(!guide.markdown.includes('/Users/'));
 }
});

test('every new verification flag is carried into the public review register', () => {
 const register = guideDocuments.find(g => g.id === 'guide-verification')!.markdown;
 for (const guide of guideDocuments.filter(g => g.listed)) {
  for (const m of guide.markdown.matchAll(/Verification needed (AG\d+|AW\d+|EP\d+)/g)) assert(register.includes(m[1]), m[1]);
 }
});

test('new guides are discoverable without the semantic model', () => {
 const archive = JSON.parse(readFileSync('public/data/catalog.json', 'utf8'));
 const records = [...practicalGuides, ...archive];
 assert.equal(new Set(records.map(r => r.id)).size, records.length);
 for (const [query, id] of [['Krishi Card registration', 'guide-farming'], ['animal welfare', 'guide-animal-welfare'], ['environmental protection', 'guide-environmental-protection']]) {
  assert(lexicalSearch(records, query).slice(0, 10).some(r => r.record.id === id), query);
 }
});

test('guides respect phone-free presentation and appear in the mixed discovery feed', () => {
 const text = guideDocuments.map(g => g.markdown).join('\n');
 for (const number of ['9607948546', '8956863414', '0832-2228772', '0832-2750246', '0832-2492533', '8956487938']) assert(!text.includes(number));
 const archive = JSON.parse(readFileSync('public/data/catalog.json', 'utf8'));
 const first = buildDiscoveryFeed([...practicalGuides, ...archive]).slice(0,12);
 for (const id of ['guide-farming','guide-animal-welfare','guide-environmental-protection']) assert(first.some(r=>r.id===id));
});
