import test from 'node:test';
import assert from 'node:assert/strict';
import {citedLibraryParagraphs,researchDomain,researchReturnPath,supportsResearchDomain,type ResearchAnswer,type ResearchStatus} from '../src/research-model.ts';

test('legal and ecology maintain distinct routes and document return paths',()=>{
 assert.equal(researchDomain('/ask/legal'),'legal');
 assert.equal(researchDomain('/ask/ecology'),'ecology');
 assert.equal(researchDomain('/ask'),'all');
 assert.equal(researchReturnPath('/ask/legal?document=abc&generation=1'),'/ask/legal?document=abc&generation=1');
 assert.equal(researchReturnPath('/ask/ecology'),'/ask/ecology');
 for(const input of ['https://elsewhere.example/ask','//elsewhere.example/ask','/ask/not-a-domain','/ask/legal/other'])assert.equal(researchReturnPath(input),'/ask');
});

test('legacy search cannot silently masquerade as a legal or ecology filter',()=>{
 const legacy:ResearchStatus={search_ready:true,chat_ready:false,stats:{documents:100}};
 assert.equal(supportsResearchDomain(legacy,'all'),true);
 assert.equal(supportsResearchDomain(legacy,'legal'),false);
 assert.equal(supportsResearchDomain({...legacy,domains:['legal','ecology']},'legal'),true);
});

test('library answer sections reject uncited text and do not mix outside context into library paragraphs',()=>{
 const answer={status:'answered',paragraphs:[{text:'Supported library claim',citations:['a']},{text:'Uncited claim',citations:[]},{text:'Invented citation',citations:['missing']}],citations:[{id:'a'}],outside_context:{text:'General context',provenance:'model_knowledge',notice:'Unverified'}} as ResearchAnswer;
 assert.deepEqual(citedLibraryParagraphs(answer),[{text:'Supported library claim',citations:['a']}]);
 assert.equal(answer.outside_context?.text,'General context');
});
