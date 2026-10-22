import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';
import {topicFlows, actionHref, topicFor, type TopicAction} from '../src/topic-flows.ts';
import {TOPICS} from '../src/types.ts';
import {guideDocuments, guideHeadingId} from '../src/guides.ts';
import {guideForReaders} from '../src/guide-presentation.ts';

const records = JSON.parse(readFileSync('public/data/catalog.json', 'utf8'));
const ids = new Set([...records, ...guideDocuments].map(r=>r.id));
const leaves = (actions:TopicAction[]):TopicAction[] => actions.flatMap(a=>a.choices ? leaves(a.choices) : [a]);

test('each topic has an action menu, with waste first and no snake shortcut at the top level',()=>{
 assert.equal(topicFlows[0].slug, 'waste');
 for(const topic of TOPICS) assert(topicFor(topic),topic);
 assert.equal(new Set(topicFlows.map(f=>f.slug)).size,TOPICS.length);
 for(const flow of topicFlows) {
  assert(flow.actions.length >= 3 && flow.actions.length <= 6);
  assert.equal(new Set(flow.actions.map(a=>a.id)).size,flow.actions.length);
  assert(!/snake/i.test(flow.label));
 }
 const waste=topicFlows[0];
 const collection=waste.actions.find(a=>a.id==='collection')!;
 assert.equal(collection.choices!.length,4);
 assert.equal(actionHref(waste,collection.choices![0],collection),'/topics/waste/collection/household');
});

test('every menu outcome has usable destinations, valid record ids, anchors and downloads',()=>{
 for(const flow of topicFlows) for(const action of leaves(flow.actions)) {
  assert(action.links?.length,`${flow.slug}/${action.id} is a dead end`);
  for(const id of [...(action.resourceIds ?? []),...(action.peopleIds ?? [])]) assert(ids.has(id),id);
  for(const {href,download} of action.links!) {
   const url=new URL(href,'https://actforgoa-field-guide.vercel.app');
   if(href==='#topic-people') continue;
   if(href.startsWith('/read/')) {
    const id=url.pathname.slice(6); assert(ids.has(id),href);
    if(url.hash) {
     const doc=guideDocuments.find(g=>g.id===id); assert(doc,href);
     const headings=[...guideForReaders(doc.markdown).matchAll(/^## (.+)$/gm)].map(m=>guideHeadingId(m[1]));
     assert(headings.includes(url.hash.slice(1)),`Missing heading: ${href}`);
    }
   } else if(download) assert(existsSync('public'+url.pathname),href);
   else if(href.startsWith('/')) assert(['/directory','/search','/library','/stories','/get-involved','/contact'].includes(url.pathname),href);
   else assert.equal(url.protocol,'https:');
  }
 }
});

test('reader guides remove process notes while keeping source documents, cautions and citations',()=>{
 for(const guide of guideDocuments.filter(g=>g.listed)) {
  const source=guide.markdown;
  const presented=guideForReaders(source);
  assert(!/Verification needed|saved corpus|before publication|Draft (for review|reviewed|status:)|retrieval failed|verification register|source register/i.test(presented),guide.id);
  assert(presented.includes('**Before you act:**'),guide.id);
  assert.match(presented,/\[[^\]]+\]: https:\/\//);
  assert.equal(guide.markdown,source);
 }
 const animal=guideForReaders(guideDocuments.find(g=>g.id==='guide-animal-welfare')!.markdown);
 assert(animal.includes('at least 15 minutes'));
 assert(animal.includes('seek urgent medical assessment'));
 const environment=guideForReaders(guideDocuments.find(g=>g.id==='guide-environmental-protection')!.markdown);
 assert(environment.includes('Do not treat silence or elapsed time as permission'));
});
