import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';
import {topicFlows, allTopicActions, actionHref, topicFor, type TopicAction} from '../src/topic-flows.ts';
import {TOPICS} from '../src/types.ts';
import {guideDocuments, guideHeadingId} from '../src/guides.ts';
import {guideForReaders} from '../src/guide-presentation.ts';
import {needsCatalogue, createCatalogueLoader} from '../src/catalogue-loader.ts';
import {actionsInBranch, topicPeople} from '../src/topic-records.ts';
import type {RecordItem} from '../src/types.ts';
import {templates} from '../src/template-catalogue.ts';
import {templatePurpose} from '../src/template-path.ts';

const records = JSON.parse(readFileSync('public/data/catalog.json', 'utf8'));
const ids = new Set([...records, ...guideDocuments].map(r=>r.id));
const leaves = (actions:TopicAction[]):TopicAction[] => actions.flatMap(a=>a.choices ? leaves(a.choices) : [a]);

test('each topic has an action menu, with waste first and no snake shortcut at the top level',()=>{
 assert.equal(topicFlows[0].slug, 'waste');
 for(const topic of TOPICS) assert(topicFor(topic),topic);
 assert.equal(new Set(topicFlows.map(f=>f.slug)).size,14);
 for(const flow of topicFlows) {
  assert(flow.actions.length >= 3 && flow.actions.length <= 12);
  assert.equal(new Set(flow.actions.map(a=>a.id)).size,flow.actions.length);
  assert(!/snake/i.test(flow.label));
 }
 const waste=topicFlows[0];
 const collection=allTopicActions(waste).find(a=>a.id==='collection')!;
 assert.equal(collection.choices!.length,4);
 assert.equal(actionHref(waste,collection.choices![0],collection),'/topics/waste/collection/household');
});

test('every menu outcome has usable destinations, valid record ids, anchors and form editors',()=>{
 for(const flow of topicFlows) for(const action of leaves(allTopicActions(flow))) {
  assert(action.links?.length,`${flow.slug}/${action.id} is a dead end`);
  for(const id of [...(action.resourceIds ?? []),...(action.peopleIds ?? [])]) assert(ids.has(id),id);
  for(const {href,download} of action.links!) {
   const url=new URL(href,'https://actforgoa-field-guide.vercel.app');
   if(href==='#topic-people') {
    assert(topicPeople(records,flow,action).length,`${flow.slug}/${action.id} points to an empty directory`);
    continue;
   }
   if(href==='#topic-reading') {
    assert(action.resourceIds?.length,`${flow.slug}/${action.id} needs curated reading`);
    continue;
   }
   if(href.startsWith('/read/')) {
    const id=url.pathname.slice(6); assert(ids.has(id),href);
    if(url.hash) {
     const doc=guideDocuments.find(g=>g.id===id); assert(doc,href);
     const headings=[...guideForReaders(doc.markdown).matchAll(/^## (.+)$/gm)].map(m=>guideHeadingId(m[1]));
     assert(headings.includes(url.hash.slice(1)),`Missing heading: ${href}`);
    }
   } else if(href.startsWith('/templates/')) assert(templates.some(t=>t.id===url.pathname.slice('/templates/'.length)),href);
   else if(download) assert(existsSync('public'+url.pathname),href);
   else if(href.startsWith('/topics/')) {
    const [, ,slug,actionId,choiceId]=url.pathname.split('/');
    const target=topicFlows.find(f=>f.slug===slug) && allTopicActions(topicFlows.find(f=>f.slug===slug)!).find(a=>a.id===actionId);
    assert((!actionId || target) && (!choiceId || target.choices?.some(c=>c.id===choiceId)),href);
   } else if(href.startsWith('/')) assert(['/contacts/forest','/contacts/agriculture','/contacts/veterinary','/directory','/search','/library','/stories','/get-involved','/contact','/collaborate','/heritage/share','/emergency','/climate-plan','/climate-plan/water','/climate-plan/funding','/climate-plan/homes','/climate-plan/tourism','/climate-plan/energy','/climate-plan/health'].includes(url.pathname),href);
   else if(url.protocol==='mailto:') assert(records.some((r:RecordItem)=>r.emails.includes(url.pathname)),`Email absent from source catalogue: ${href}`);
   else assert.equal(url.protocol,'https:');
  }
 }
});

test('no main topic pathway requires downloading a blank form',()=>{
 let editors=0;
 for(const flow of topicFlows) for(const action of leaves(allTopicActions(flow))) for(const link of action.links ?? []) {
  assert(!link.download, `${flow.slug}/${action.id}: ${link.label}`);
  assert(!link.href.startsWith('/guides/templates/'), link.href);
  if(link.href.startsWith('/')) assert(!/download|\.pdf(?:$|[?#])/i.test(link.href), link.href);
  assert(!/download/i.test(link.label), link.label);
  if(link.href.startsWith('/templates/')) editors++;
 }
 assert(editors >= 25, `Expected all former downloads to have editors, found ${editors}`);
 const damage=allTopicActions(topicFlows.find(f=>f.slug==='food')!).find(a=>a.id==='damage')!;
 const href=damage.links!.find(l=>l.href.startsWith('/templates/'))!.href;
 assert.equal(templatePurpose(new URL(href, 'https://example.test').search), 'damage');
 assert.equal(templatePurpose('?purpose=unknown'), undefined);
});

test('follow-up choices fit the route depth and affirmative actions precede reporting',()=>{
 for(const flow of topicFlows) {
  const firstConcern=flow.actions.findIndex(action=>action.concern);
  assert(firstConcern!==0,flow.slug+' starts with reporting');
  if(firstConcern>=0) assert(flow.actions.slice(firstConcern).every(action=>action.concern),flow.slug+' interleaves reporting');
  for(const action of actionsInBranch(allTopicActions(flow))) {
   if(action.choices) {
    assert(action.question);
    assert(action.choices.length>=2 && action.choices.length<=6);
    assert.equal(new Set(action.choices.map(c=>c.id)).size,action.choices.length);
    assert(!action.choices.some(c=>c.choices),'Routes support one follow-up question');
   } else assert(action.links?.length,`${flow.slug}/${action.id} has no next step`);
  }
 }
});

test('curated services cross incomplete source tags and stay scoped to the selected need',()=>{
 const health=topicFlows.find(f=>f.slug==='health')!;
 const mental=allTopicActions(health).find(a=>a.id==='mental-health')!;
 assert(!records.find((r:RecordItem)=>r.id==='org-186').topics.includes(health.topic));
 assert.deepEqual(topicPeople(records,health,mental.choices!.find(a=>a.id==='clinic')).map(r=>r.id),['org-186']);
 const disability=health.actions.find(a=>a.id==='disability')!;
 assert(topicPeople(records,health,disability).some(r=>r.id==='org-14'));
 const planning=topicFlows.find(f=>f.slug==='planning')!;
 const design=planning.actions.find(a=>a.id==='professionals')!.choices!.find(a=>a.id==='design')!;
 assert.deepEqual(topicPeople(records,planning,design).map(r=>r.id),['org-119','org-108']);
 for(const flow of topicFlows) for(const action of actionsInBranch(allTopicActions(flow))) {
  const result=topicPeople(records,flow,action);
  assert.equal(new Set(result.map(r=>r.id)).size,result.length);
  for(const id of action.peopleIds ?? []) assert(result.some(r=>r.id===id),`${flow.slug}/${action.id}: missing ${id}`);
 }
});

test('direct topic visits load the catalogue for menus and service outcomes', async()=>{
 const paths = topicFlows.flatMap(flow => [
  '/topics/'+flow.slug,
  ...flow.actions.flatMap(action => [actionHref(flow,action), ...(action.choices ?? []).map(choice => actionHref(flow,choice,action))]),
 ]);
 for(const path of paths) assert(needsCatalogue(path), path);
 let requests=0;
 const load=createCatalogueLoader(async()=>{ requests++; return new Response(JSON.stringify(records)); });
 for(const path of ['/topics/waste/collection/household','/topics/water','/topics/health/disability']) {
  const result=await load(path);
  assert.equal(result.error,false,path);
  assert(result.records.some(r=>r.id==='org-165'),path);
 }
 assert.equal(requests,1);
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
