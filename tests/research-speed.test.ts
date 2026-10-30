import test from 'node:test';
import assert from 'node:assert/strict';
import {requestResearch,type ResearchInput} from '../src/research-request';
import {canUseCachedExample,type ResearchStatus} from '../src/research-model';
import {researchApi} from '../src/research-api';
const input:ResearchInput={question:'What happens next?',domain:'all',history:[{role:'user',content:'Earlier question'},{role:'assistant',content:'A cited answer'}],include_outside_context:true};
test('answer mode makes only one request and preserves follow-up history and citations',async()=>{
 const calls:{url:string;body?:string}[]=[];const citations=[{id:'exact-page'}];
 const fake=(async(url:string,options:RequestInit)=>{calls.push({url,body:options.body as string});return {paragraphs:[],citations};}) as typeof researchApi;
 const result=await requestResearch(input,'ask',new AbortController().signal,fake);
 assert.equal(calls.length,1);assert.equal(calls[0].url,'/api/chat');assert.deepEqual(JSON.parse(calls[0].body!).history,input.history);assert.deepEqual(result.results,citations);
});
test('source-only mode does not invoke a model and rejects wrong scoped collections',async()=>{
 const calls:string[]=[];const fake=(async(url:string)=>{calls.push(url);return {results:[],domain:'all'};}) as typeof researchApi;
 await assert.rejects(requestResearch({...input,domain:'ecology'},'search',new AbortController().signal,fake),/section is not available/);
 assert.equal(calls.length,1);assert.ok(calls[0].startsWith('/api/search?'));
});
test('cached starter availability never crosses histories, documents, domains or generations',()=>{
 const status={cached_examples:['Example question?'],generation:'v1'} as ResearchStatus;
 assert.ok(canUseCachedExample(status,'  Example   question? ','all',undefined,0));
 assert.ok(!canUseCachedExample(status,'Example question?','all',undefined,1));
 assert.ok(!canUseCachedExample(status,'Example question?','ecology',undefined,0));
 assert.ok(!canUseCachedExample(status,'Example question?','all','document',0));
 assert.ok(!canUseCachedExample(status,'Example question?','all',undefined,0,'v0'));
});
