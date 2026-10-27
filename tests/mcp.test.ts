import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import handler from '../api/mcp.ts';

test('remote MCP exposes public sources and returns source evidence', async () => {
 const http = createServer((req,res) => { void handler(req,res); });
 await new Promise<void>(resolve => http.listen(0,'127.0.0.1',resolve));
 const address=http.address(); if(!address || typeof address==='string') throw Error('No address');
 const client = new Client({name:'actforgoa-test',version:'1'});
 try {
  await client.connect(new StreamableHTTPClientTransport(new URL(`http://127.0.0.1:${address.port}/api/mcp`)));
  const tools=await client.listTools(); assert.deepEqual(tools.tools.map(x=>x.name),['search_site','search_directory','search_research']);
  assert.match(tools.tools.find(x => x.name === 'search_directory')!.description!, /concise subject and place keywords/);
  for (const tool of tools.tools) assert.deepEqual(tool.annotations, {readOnlyHint:true, destructiveHint:false, idempotentHint:true, openWorldHint:true});
  for (const [name,query] of [['search_site','wildlife'],['search_directory','waste'],['search_research','khazan wetlands']]) {
   const result=await client.callTool({name,arguments:{query,limit:2}});
   assert.notEqual(result.isError,true,`${name}: ${JSON.stringify(result)}`);
   const payload=JSON.parse((result.content as {text:string}[])[0].text);
   assert.ok(payload.results.length,`${name} returned no evidence`);
   assert.ok(payload.notice);
  }
  const natural=await client.callTool({name:'search_directory',arguments:{query:'Who can help with waste in Goa?',limit:3}});
  assert.ok(JSON.parse((natural.content as {text:string}[])[0].text).results.length > 0);
  const waste=await client.callTool({name:'search_directory',arguments:{query:'waste',limit:20}});
  const wasteResults=JSON.parse((waste.content as {text:string}[])[0].text).results;
  const corporations=wasteResults.filter((r:{name:string})=>/^goa waste management corporation$/i.test(r.name));
  assert.equal(corporations.length,1);
  assert.ok(corporations[0].additional_listings.some((r:{id:string})=>r.id==='goa-b3f711f6b7f3'));
  const science=wasteResults.find((r:{id:string})=>r.id==='goa-80732e1537a8');
  assert.equal(science?.website,'https://www.dstegoa.goa.gov.in');
  const rti=await client.callTool({name:'search_site',arguments:{query:'How do I file an RTI?',limit:3}});
  const result=JSON.parse((rti.content as {text:string}[])[0].text).results[0];
  assert.equal(result.id,'guide-reporting'); assert.match(result.excerpt,/\bRTI\b/i); assert.match(result.source,/^https:\/\//);
 } finally { await client.close(); await new Promise<void>((resolve,reject)=>http.close(e=>e?reject(e):resolve())); }
});

test('MCP search keeps meaningful directory terms and ranks actual RTI evidence', async () => {
 const {directoryMatches, directoryWebsite, searchTerms, siteMatches}=await import('../src/mcp-search.ts');
 const {publicCatalogue}=await import('../src/public-record.ts');
 const {filterRecords,filtersFrom}=await import('../src/crm-model.ts');
 const {readFileSync}=await import('node:fs');
 const raw=JSON.parse(readFileSync('public/data/catalog.json','utf8'));
 const guides=JSON.parse(readFileSync('src/content/guide-records.json','utf8'));
 const crm=JSON.parse(readFileSync('public/data/crm.json','utf8'));
 const directory=(query:string)=>filterRecords(crm.records,new Set(),filtersFrom(new URLSearchParams({q:searchTerms(query),collection:'all'})),{});
 assert.equal(searchTerms('Who can help with waste in Goa?'),'waste');
 assert.deepEqual(directory('Who can help with waste in Goa?').slice(0,3).map(r=>r.record_id),directory('waste').slice(0,3).map(r=>r.record_id));
 assert.equal(searchTerms('waste collection'),'waste collection');
 const matches = directoryMatches(directory('waste'), 20);
 const corporation = matches.filter(({record}) => /goa waste management corporation/i.test(record.name));
 assert.equal(corporation.length, 1);
 assert.equal(corporation[0].record.record_id, 'goa-3be8492c5821');
 assert.equal(corporation[0].additional[0].record_id, 'goa-b3f711f6b7f3');
 assert.ok(corporation[0].additional[0].contact_source_urls);
 const science = crm.records.find((r: {record_id:string}) => r.record_id === 'goa-80732e1537a8');
 assert.equal(directoryWebsite(science.website_url), 'https://www.dstegoa.goa.gov.in');
 assert.deepEqual(directory('waste collection').map(r=>r.record_id),directory('Who can help with waste collection in Goa?').map(r=>r.record_id));
 const results=siteMatches(publicCatalogue([...guides,...raw]),'How do I file an RTI?',5);
 assert.equal(results[0].record.id,'guide-reporting');
 for (const query of ['right to information','How can I submit a right to information request?','How do I submit an RTI application?']) assert.equal(siteMatches(publicCatalogue([...guides,...raw]),query,3)[0].record.id,'guide-reporting');
 assert.match(results[0].excerpt,/\bRTI\b/i);
 assert.ok(results[0].record.source);
 assert.ok(!results.some(({record})=>/occupancy certificate|^artist$/i.test(record.title)));
});
