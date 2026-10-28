import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import type {AddressInfo} from 'node:net';
import test from 'node:test';
import {createAdminServer} from '../server/admin.ts';
import {forwardSatellite} from '../server/satellite-proxy.ts';
import {createAdminProxy} from '../server/admin-proxy.ts';

async function listen(server: ReturnType<typeof createServer>) {
  server.listen(0, '127.0.0.1'); await once(server, 'listening');
  return `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
}
async function close(server: ReturnType<typeof createServer>) {
  server.closeAllConnections(); server.close(); await once(server,'close');
}

test('satellite route uses named-session authentication, CSRF and verified actor identity', async () => {
  const calls: {path:string; actor:string; token:string}[] = [];
  const upstream = createServer((req,res) => {
    calls.push({path:req.url!,actor:String(req.headers['x-actor-id']),token:String(req.headers.authorization)});
    res.setHeader('Content-Type','application/json');res.end(JSON.stringify({state:'available'}));
  });
  const previousOrigin=process.env.SATELLITE_API_ORIGIN, previousToken=process.env.SATELLITE_SERVICE_TOKEN;
  process.env.SATELLITE_API_ORIGIN=await listen(upstream);
  process.env.SATELLITE_SERVICE_TOKEN='test-service-token-'.repeat(3);
  const {server,store}=createAdminServer({databasePath:':memory:',knownRecordIds:new Set(),publicOrigin:'http://127.0.0.1:4173',local:true});
  const user=await store.provision('satellite@example.test','Satellite tester','test-only-long-password');
  const login=await store.login('satellite@example.test','test-only-long-password','test-client');
  const base=await listen(server), path='/api/admin/satellite/catalog';
  const headers={'Content-Type':'application/json',Cookie:`afg_admin_session=${login.token}`,'X-CSRF-Token':login.csrfToken,'X-Actor-ID':'forged-user','Authorization':'Bearer forged'};
  try {
    assert.equal((await fetch(base+path,{method:'POST',body:'{}'})).status,401);
    assert.equal((await fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json',Cookie:headers.Cookie},body:'{}'})).status,403);
    assert.equal(calls.length,0);
    assert.equal((await fetch(base+path,{method:'POST',headers,body:'{}'})).status,200);
    assert.deepEqual(calls,[{path:'/catalog',actor:user.id,token:'Bearer '+process.env.SATELLITE_SERVICE_TOKEN}]);
    assert.equal((await fetch(base+'/api/admin/satellite/secret',{headers})).status,404);
    assert.equal(calls.length,1);
    assert.equal((await fetch(base+'/api/admin/satellite/history',{method:'POST',body:'{}'})).status,401);
    assert.equal((await fetch(base+'/api/admin/satellite/history',{method:'POST',headers:{Cookie:headers.Cookie,'Content-Type':'application/json'},body:'{}'})).status,403);
    assert.equal((await fetch(base+'/api/admin/satellite/history',{method:'POST',headers,body:'{}'})).status,200);
    assert.deepEqual(calls[1],{path:'/history',actor:user.id,token:'Bearer '+process.env.SATELLITE_SERVICE_TOKEN});
    store.logout(login.token);
    assert.equal((await fetch(base+'/api/admin/satellite/status',{headers})).status,401);
  } finally {
    if(previousOrigin===undefined)delete process.env.SATELLITE_API_ORIGIN;else process.env.SATELLITE_API_ORIGIN=previousOrigin;
    if(previousToken===undefined)delete process.env.SATELLITE_SERVICE_TOKEN;else process.env.SATELLITE_SERVICE_TOKEN=previousToken;
    await close(server);await close(upstream);
  }
});

test('satellite forwarding bounds origins, redirects and response memory', async () => {
  let mode='bad-origin', called=0, cancelled=false;
  const server=createServer((req,res)=>void forwardSatellite('/api/admin/satellite/status','GET','actor',undefined,res,{
    origin:mode==='bad-origin'?'https://user:pass@example.test':'https://satellite.example.test',token:'x'.repeat(40),
    fetcher:async()=>{called++;if(mode==='redirect')return new Response(null,{status:302,headers:{Location:'https://elsewhere.test'}});
      return new Response(new ReadableStream({pull(controller){controller.enqueue(new Uint8Array(1024*1024));},cancel(){cancelled=true;}}));},
  }));
  const base=await listen(server);
  try {
    assert.equal((await fetch(base)).status,503);assert.equal(called,0);
    mode='redirect';assert.equal((await fetch(base)).status,502);
    mode='oversize';assert.equal((await fetch(base)).status,502);assert.equal(cancelled,true);
  } finally {await close(server);}
});

test('frontend proxy permits satellite endpoints while rejecting invented paths', async()=>{
  const paths:string[]=[];
  const handler=createAdminProxy({origin:'https://admin.example.test',fetcher:async(input)=>{paths.push(String(input));return new Response('{}',{headers:{'Content-Type':'application/json'}});}});
  const server=createServer((req,res)=>void handler(req,res)),base=await listen(server);
  try{
    assert.equal((await fetch(base+'/api/admin/satellite/status')).status,200);
    assert.equal((await fetch(base+'/api/admin/satellite/catalog',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})).status,200);
    assert.equal((await fetch(base+'/api/admin/satellite/files')).status,404);
    assert.equal((await fetch(base+'/api/admin/satellite/history',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})).status,200);
    assert.equal(paths.length,3);
  }finally{await close(server);}
});
