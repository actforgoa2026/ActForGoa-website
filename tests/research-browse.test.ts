import test from 'node:test';
import assert from 'node:assert/strict';
import {browseDocuments,fullDocumentPath,publisherHost,topicsForDomain} from '../src/research-browse.ts';
import {researchReturnPath,type ResearchEvidence} from '../src/research-model.ts';

test('browse shelves keep ecology and legal collections separate',()=>{
 assert.ok(topicsForDomain('ecology').length>0);
 assert.ok(topicsForDomain('ecology').every(topic=>topic.domain==='ecology'));
 assert.ok(topicsForDomain('legal').every(topic=>topic.domain==='legal'));
 assert.equal(topicsForDomain('all').length,topicsForDomain('legal').length+topicsForDomain('ecology').length);
});

test('a shelf has one entry per document, with source-version links into the full reader',()=>{
 const sources=[{id:'p1',document_id:'doc-a',title:'River',generation:'gen-1'},{id:'p2',document_id:'doc-a',title:'River',generation:'gen-1'},{id:'p3',document_id:'doc-b',title:'Forest',generation:'gen-1'}] as ResearchEvidence[];
 const documents=browseDocuments(sources);
 assert.deepEqual(documents.map(doc=>doc.document_id),['doc-b','doc-a']);
 assert.equal(fullDocumentPath(documents[1]),'/documents/doc-a?generation=gen-1');
 assert.ok(!fullDocumentPath(documents[1]).includes('passage='));
});

test('reader returns to a selected browse shelf without accepting an external return URL',()=>{
 assert.equal(researchReturnPath('/research-library?domain=ecology&topic=rivers'),'/research-library?domain=ecology&topic=rivers');
 assert.equal(researchReturnPath('https://example.com/research-library'),'/ask');
 assert.equal(researchReturnPath('//example.com/research-library'),'/ask');
 assert.equal(researchReturnPath('/research-library/anything'),'/ask');
 assert.equal(publisherHost('https://forest.goa.gov.in/report.pdf'),'forest.goa.gov.in');
 assert.equal(publisherHost('not a URL'),'Saved source');
});
