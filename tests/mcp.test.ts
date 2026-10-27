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
 } finally { await client.close(); await new Promise<void>((resolve,reject)=>http.close(e=>e?reject(e):resolve())); }
});
