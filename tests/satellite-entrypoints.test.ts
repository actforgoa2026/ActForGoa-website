import assert from 'node:assert/strict';
import {once} from 'node:events';
import {createServer} from 'node:http';
import type {AddressInfo} from 'node:net';
import test from 'node:test';
import actionHandler from '../api/admin/satellite/[action].ts';
import jobHandler from '../api/admin/satellite/jobs/[id].ts';

test('explicit satellite function entries preserve gated responses and trusted session transport',async()=>{
  const nativeFetch=globalThis.fetch,previousOrigin=process.env.ADMIN_API_ORIGIN;
  const calls:{url:string;method:string;headers:Headers;body:unknown}[]=[];
  process.env.ADMIN_API_ORIGIN='https://admin.example.test';
  globalThis.fetch=async(input,init)=>{
    const headers=new Headers(init?.headers);
    calls.push({url:String(input),method:init?.method||'GET',headers,
      body:init?.body?JSON.parse(Buffer.from(init.body as Uint8Array).toString()):undefined});
    assert.equal(init?.redirect,'manual');
    if(!headers.get('cookie'))return Response.json({error:'Sign in to continue.'},{status:401});
    return Response.json({state:'test-only-response'});
  };
  const server=createServer((req,res)=>void (req.url?.startsWith('/api/admin/satellite/jobs/')?jobHandler:actionHandler)(req,res));
  try{
    server.listen(0,'127.0.0.1');await once(server,'listening');
    const base=`http://127.0.0.1:${(server.address() as AddressInfo).port}`;
    const anonymous=await nativeFetch(base+'/api/admin/satellite/status');
    assert.equal(anonymous.status,401);
    assert.deepEqual(await anonymous.json(),{error:'Sign in to continue.'});
    const headers={'content-type':'application/json',cookie:'afg_admin_session=unit-test-only',
      'x-csrf-token':'unit-test-csrf',origin:'https://site.example.test',
      authorization:'Bearer must-not-forward','x-actor-id':'must-not-forward'};
    const body={area:{bbox:[73.82,15.48,73.83,15.49]},question:'Test-only area evidence'};
    assert.equal((await nativeFetch(base+'/api/admin/satellite/evidence',{method:'POST',headers,body:JSON.stringify(body)})).status,200);
    const job='a1234567-1234-1234-1234-123456789abc';
    assert.equal((await nativeFetch(base+'/api/admin/satellite/jobs/'+job,{headers})).status,200);
    assert.equal(calls.length,3);
    assert.equal(calls[0].url,'https://admin.example.test/api/admin/satellite/status');
    assert.equal(calls[0].headers.get('cookie'),null);
    assert.equal(calls[1].url,'https://admin.example.test/api/admin/satellite/evidence');
    assert.equal(calls[1].method,'POST');
    assert.deepEqual(calls[1].body,body);
    assert.equal(calls[2].url,'https://admin.example.test/api/admin/satellite/jobs/'+job);
    assert.equal(calls[2].method,'GET');
    for(const call of calls.slice(1)){
      assert.equal(call.headers.get('cookie'),headers.cookie);
      assert.equal(call.headers.get('x-csrf-token'),headers['x-csrf-token']);
      assert.equal(call.headers.get('origin'),headers.origin);
      assert.equal(call.headers.get('authorization'),null);
      assert.equal(call.headers.get('x-actor-id'),null);
    }
    for(const path of ['/api/admin/satellite/secrets','/api/admin/satellite/jobs/not-a-job'])
      assert.equal((await nativeFetch(base+path,{headers})).status,404);
    assert.equal(calls.length,3,'Unknown paths must not reach the upstream service');
  }finally{
    globalThis.fetch=nativeFetch;
    if(previousOrigin===undefined)delete process.env.ADMIN_API_ORIGIN;else process.env.ADMIN_API_ORIGIN=previousOrigin;
    if(server.listening){server.closeAllConnections();server.close();await once(server,'close');}
  }
});
