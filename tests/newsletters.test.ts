import {test} from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';

const issues = JSON.parse(readFileSync(new URL('../src/content/newsletters.json', import.meta.url), 'utf8')) as {id:string;source:string;markdown?:string;pdf?:string}[];
test('all five original newsletters have complete local reading material and source links', () => {
 assert.equal(issues.length, 5);
 assert.equal(new Set(issues.map(issue => issue.id)).size, 5);
 for (const issue of issues) {
  assert.match(issue.source, /^https:\/\/(actforgoa\.org|mailchi\.mp)\//);
  if (issue.pdf) {
   assert.ok((issue.markdown?.length || 0)>8000, 'The image-only PDF must also have its checked text transcription');
   for (const heading of ['Conscious planning','Nature conservation','Regenerative tourism','Cross cutting workstreams','Acknowledgements']) assert.ok(issue.markdown!.includes('## '+heading));
   const pdf=readFileSync(new URL('../public'+issue.pdf,import.meta.url));
   assert.equal(pdf.subarray(0,5).toString(),'%PDF-');
   for (let n=1;n<=4;n++) assert.ok(existsSync(new URL(`../public/assets/newsletters/2025-year-end-page-${n}.webp`,import.meta.url)));
  } else {
   assert.ok((issue.markdown?.length || 0)>1000,issue.id);
   assert.doesNotMatch(issue.markdown!, /<script|<iframe|https?:[^)\s]+unsubscribe|list-manage\.com|mc_eid=/i);
   for (const image of issue.markdown!.matchAll(/!\[[^\]]*\]\((\/assets\/newsletters\/[^)]+)\)/g)) assert.ok(existsSync(new URL('../public'+image[1],import.meta.url)),image[1]);
  }
 }
});
