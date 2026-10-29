import test from 'node:test';
import assert from 'node:assert/strict';
import {citedLibraryParagraphs,researchDomain,researchReturnPath,researchSourceNotes,supportsResearchDomain,type ResearchAnswer,type ResearchEvidence,type ResearchStatus} from '../src/research-model.ts';

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

test('official source status and review limitations remain visible without implying current law',()=>{
 const source={warning:'',legal_currency:'Historical primary legislation; not verified consolidated current law.',guide_verification:{limitations:'This review covers section 4 only.',review_date_local:'2026-10-23'}} as ResearchEvidence;
 assert.deepEqual(researchSourceNotes(source),[{label:'Legal status',text:source.legal_currency},{label:'Review limitations',text:'This review covers section 4 only.'}]);
 assert.ok(researchSourceNotes(source).every(note=>!note.text.includes('2026-10-23')));
});

test('authored guide caveats do not repeat an identical extraction note',()=>{
 const warning='Authored draft guide; not primary legislation.';
 const source={warning,legal_currency:warning,guide_verification:{limitations:warning,source_file:'GUIDE_DRAFT.md'}} as ResearchEvidence;
 assert.deepEqual(researchSourceNotes(source),[]);
 source.guide_verification!.limitations='Local service availability has not been verified.';
 assert.deepEqual(researchSourceNotes(source),[{label:'Draft guide limitations',text:'Local service availability has not been verified.'}]);
});

test('library status enums render as readable caveats without altering source text',()=>{
 const source={warning:'',legal_currency:'not_consolidated_or_legally_verified'} as ResearchEvidence;
 assert.deepEqual(researchSourceNotes(source),[{label:'Legal status',text:'Not verified as consolidated or current law.'}]);
 assert.equal(source.legal_currency,'not_consolidated_or_legally_verified');
});
