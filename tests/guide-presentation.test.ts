import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {guideForReaders} from '../src/guide-presentation.ts';
import {guideDocuments} from '../src/guides.ts';

const fixtures = JSON.parse(readFileSync(new URL('./fixtures/guide-cautions.json', import.meta.url), 'utf8')) as {
 cases: {id:string; guide:string; markdown:string; required:string[]}[];
};
const referenceUses = (markdown:string) => [...markdown.matchAll(/\]\[([^\]]+)\]/g)].map(m=>m[1]);
const definitions = (markdown:string) => [...markdown.matchAll(/^\[[^\]]+\]: .+$/gm)].map(m=>m[0]);
const inlineDestinations = (markdown:string) => [...markdown.matchAll(/\]\(([^)]+)\)/g)].map(m=>m[1]);

for (const fixture of fixtures.cases) {
 test(`reader preserves verified caution ${fixture.id}, its references and local limits`,()=>{
  const presented = guideForReaders(fixture.markdown);
  assert(!presented.includes('Verification needed'));
  assert(presented.includes('**Before you act:**'));
  for(const phrase of fixture.required) assert(presented.includes(phrase), phrase);
  assert.deepEqual(referenceUses(presented), referenceUses(fixture.markdown));
  assert.deepEqual(definitions(presented), definitions(fixture.markdown));
  assert.deepEqual(inlineDestinations(presented), inlineDestinations(fixture.markdown));
 });
}

test('new flags retain complete advice even when embedded in a source update',()=>{
 const caution = 'Do not start work without the required permission. Ask for the site-specific conditions. [Official procedure][NEW1]';
 const presented = guideForReaders(`Published information precedes the flag. **Verification needed NEW99:** ${caution}\n\n[NEW1]: https://goa.gov.in/`);
 assert(presented.includes(caution));
 assert(!presented.includes('Verification needed'));
});

test('reader retains source attribution, legal draft status, templates and every citation',()=>{
 for(const guide of guideDocuments.filter(g=>g.listed)) {
  const presented = guideForReaders(guide.markdown);
  assert.deepEqual(referenceUses(presented), referenceUses(guide.markdown), guide.id);
  assert.deepEqual(definitions(presented), definitions(guide.markdown), guide.id);
  assert.deepEqual(inlineDestinations(presented), inlineDestinations(guide.markdown), guide.id);
  assert.equal(guideForReaders(presented), presented, guide.id);
 }
 const environmental = guideForReaders(guideDocuments.find(g=>g.id==='guide-environmental-protection')!.markdown);
 assert(environmental.includes('**A draft notification is a proposal, not the final notification.**'));
 assert(environmental.includes('or attempt emergency felling using this guide.'));
});

test('editorial draft labels do not erase untested-service and legal-status qualifications',()=>{
 const source = '**Draft status:** steps marked **Verification needed** require the checks listed in the [verification register](/read/guide-verification) before publication. Contact details below were checked against published sources, not tested by calling or submitting a case. These drafts do not determine whether a particular activity is unlawful.';
 const presented = guideForReaders(source);
 assert(presented.includes('not tested by calling or submitting a case.'));
 assert(presented.includes('do not determine whether a particular activity is unlawful.'));
 assert(presented.includes('](/read/guide-verification)'));
 assert(!/Draft status|Verification needed|before publication|verification register/.test(presented));
});
