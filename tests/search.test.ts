import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {lexicalSearch,hybridSearch} from '../src/search.ts';
import type {RecordItem} from '../src/types.ts';
const records=JSON.parse(readFileSync('public/data/catalog.json','utf8')) as RecordItem[];
test('natural-language snake request returns the source volunteer list first',()=>{
 const found=lexicalSearch(records,'Who do I call about a snake in my lawn?');
 assert.equal(found[0].record.id,'resource-590480849c');
 assert(found.some(x=>x.record.kind==='contact'));
 assert(found.some(x=>x.record.id==='org-27'));
});
test('colloquial waste query finds waste-related content',()=>{
 const found=lexicalSearch(records,'Where can I take my rubbish?');
 assert(found.length>0);assert(found.slice(0,5).some(x=>x.record.topics.includes('Waste & recycling')));
});
test('named volunteer can be found by name and locality',()=>{
 const found=lexicalSearch(records,'Griselda Nobay Donvaddo');
 assert(found.slice(0,3).some(x=>x.record.title==='Griselda Nobay'));
});
test('unrelated nonsense produces an honest empty result',()=>{
 assert.equal(lexicalSearch(records,'zzzxqvplm').length,0);
 assert.equal(hybridSearch(records,'zzzxqvplm',new Map(records.map(r=>[r.id,.1]))).length,0);
});
test('meaning matches can retrieve a record with no lexical overlap',()=>{
 const target=records.find(r=>r.title==='V Recycle')!;assert(target);
 const found=hybridSearch(records,'discarded household materials',new Map([[target.id,.8]]));
 assert(found.some(x=>x.record.id===target.id));
});
test('records retain unique ids and public source provenance',()=>{
 assert.equal(new Set(records.map(r=>r.id)).size,records.length);
 assert(records.every(r=>r.source.startsWith('https://actforgoa.org/')));
 assert(records.every(r=>r.retrievedAt&&r.verification==='source-listed-unverified'));
 assert.equal(records.filter(r=>r.kind==='organisation').length,104);
});
test('telephone actions contain one complete number and short numbers are not invented',()=>{
 for(const r of records)for(const p of r.phones)if(p.href)assert.match(p.href,/^tel:\+91\d{10}$/);
 const short=records.filter(r=>r.kind==='contact').flatMap(r=>r.phones).filter(p=>/^\d{7}$/.test(p.display));
 assert(short.length>0);assert(short.every(p=>p.href===null));
});
test('all semantic index records resolve and vector dimensions match',()=>{
 const index=JSON.parse(readFileSync('public/data/vector-index.json','utf8'));
 const ids=new Set(records.map(r=>r.id));
 assert(index.ids.every((id:string)=>ids.has(id)));
 assert.equal(readFileSync('public/data/vectors.bin').byteLength,index.ids.length*384*4);
 assert.equal(index.records,records.length);
});
