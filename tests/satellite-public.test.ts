import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import type {AddressInfo} from 'node:net';
import test from 'node:test';
import {createAdminServer} from '../server/admin.ts';
import {createAdminProxy} from '../server/admin-proxy.ts';
import {createSatelliteWeb} from '../server/satellite-web.ts';
import actionHandler from '../api/satellite/[action].ts';
import jobHandler from '../api/satellite/jobs/[id].ts';

async function listen(server:ReturnType<typeof createServer>){server.listen(0,'127.0.0.1');await once(server,'listening');return `http://127.0.0.1:${(server.address() as AddressInfo).port}`;}
async function close(server:ReturnType<typeof createServer>){server.closeAllConnections();server.close();await once(server,'close');}

test('public map sessions need no account and isolate visitor jobs, cookies, CSRF and rate limits',async()=>{
  const saved=new Map<string,string>(),calls:{route:string;actor:string}[]=[];
  const job='a1234567-1234-1234-1234-123456789abc';
  const upstream=createServer((req,res)=>{
    const actor=String(req.headers['x-actor-id']);calls.push({route:req.url!,actor});
    assert.equal(req.headers.authorization,'Bearer '+'test-public-map-token-'.repeat(3));
    if(req.url==='/compare')saved.set(job,actor);
    if(req.url?.startsWith('/jobs/')&&saved.get(job)!==actor)res.statusCode=404;
    res.setHeader('Content-Type','application/json');res.end(JSON.stringify(req.url==='/history'?{items:[...saved].filter(([,owner])=>owner===actor).map(([id])=>({id}))}:{id:job,imagery_ready:true}));
  });
  const previous={origin:process.env.SATELLITE_API_ORIGIN,token:process.env.SATELLITE_SERVICE_TOKEN};
  process.env.SATELLITE_API_ORIGIN=await listen(upstream);process.env.SATELLITE_SERVICE_TOKEN='test-public-map-token-'.repeat(3);
  let time=Date.now();
  const {server}=createAdminServer({databasePath:':memory:',knownRecordIds:new Set(),publicOrigin:'http://127.0.0.1:4173',local:true,now:()=>time});
  const base=await listen(server);
  const session=async(cookie='')=>{
    const response=await fetch(base+'/api/satellite/session',{headers:{cookie}});assert.equal(response.status,200);
    const value=await response.json();assert.match(value.visitorId,/^visitor_[A-Za-z0-9_-]{32}$/);assert.equal(value.user,undefined);
    assert.match(response.headers.get('set-cookie')!,/HttpOnly; SameSite=Strict; Path=\/api\/satellite/);
    return {...value,cookie:response.headers.get('set-cookie')!.split(';')[0]};
  };
  const post=(route:string,visitor:{cookie:string;csrfToken:string},extra:Record<string,string>={},body='{}')=>fetch(base+'/api/satellite/'+route,{method:'POST',headers:{'content-type':'application/json',cookie:visitor.cookie,'x-csrf-token':visitor.csrfToken,...extra},body});
  try{
    const a=await session(),b=await session();assert.notEqual(a.visitorId,b.visitorId);
    const reopened=await session(a.cookie);assert.equal(reopened.visitorId,a.visitorId);assert.equal(reopened.csrfToken,a.csrfToken);
    assert.equal((await fetch(base+'/api/satellite/status',{headers:{cookie:a.cookie}})).status,200);
    assert.equal((await post('compare',a,{'x-actor-id':b.visitorId,authorization:'Bearer forged'})).status,200);
    assert.equal(calls.at(-1)?.actor,a.visitorId);
    assert.equal((await fetch(base+'/api/satellite/jobs/'+job,{headers:{cookie:a.cookie}})).status,200);
    assert.equal((await fetch(base+'/api/satellite/jobs/'+job,{headers:{cookie:b.cookie}})).status,404);
    assert.equal((await (await post('history',a)).json()).items.length,1);
    assert.equal((await (await post('history',b)).json()).items.length,0);
    const count=calls.length;
    assert.equal((await post('catalog',a,{'x-csrf-token':b.csrfToken})).status,403);
    assert.equal((await post('catalog',a,{'x-csrf-token':'é'.repeat(43)})).status,403);
    assert.equal((await post('catalog',a,{origin:'https://foreign.example'})).status,403);
    assert.equal((await post('catalog',a,{'sec-fetch-site':'cross-site'})).status,403);
    assert.equal((await fetch(base+'/api/satellite/session',{headers:{'sec-fetch-site':'cross-site'}})).status,403);
    assert.equal((await fetch(base+'/api/satellite/status')).status,401);
    assert.equal((await fetch(base+'/api/satellite/status',{headers:{cookie:a.cookie+'tampered'}})).status,401);
    assert.equal((await fetch(base+'/api/satellite/status',{headers:{cookie:a.cookie+'; '+a.cookie}})).status,401);
    assert.equal((await fetch(base+'/api/satellite/catalog',{headers:{cookie:a.cookie}})).status,405);
    assert.equal((await post('catalog',a,{},JSON.stringify({question:'x'.repeat(17000)}))).status,413);
    assert.equal((await post('catalog',a,{},'{')).status,400);
    assert.equal((await fetch(base+'/api/satellite/files',{headers:{cookie:a.cookie}})).status,404);
    assert.equal((await fetch(base+'/api/admin/session',{headers:{cookie:a.cookie}})).status,401);
    assert.equal((await fetch(base+'/api/admin/posts',{headers:{cookie:a.cookie}})).status,401);
    assert.equal(calls.length,count);
    let limited=false;for(let i=0;i<31;i++)if((await post('history',b)).status===429){limited=true;break;}assert.equal(limited,true);
    time+=31*24*60*60*1000;
    assert.equal((await fetch(base+'/api/satellite/status',{headers:{cookie:a.cookie}})).status,401);
    assert.notEqual((await session(a.cookie)).visitorId,a.visitorId);
  }finally{
    for(const [key,value] of [['SATELLITE_API_ORIGIN',previous.origin],['SATELLITE_SERVICE_TOKEN',previous.token]])if(value===undefined)delete process.env[key!];else process.env[key!]=value;
    await close(server);await close(upstream);
  }
});

test('public proxy uses the satellite service, keeps the browser URL and never forwards staff credentials',async()=>{
  const calls:{url:string;headers:Headers}[]=[];
  const handler=createAdminProxy({origin:'https://admin.example.test',satelliteOrigin:'https://satellite.example.test',fetcher:async(input,init)=>{
    calls.push({url:String(input),headers:new Headers(init?.headers)});return Response.json({visitorId:'test'},{headers:{'Set-Cookie':'afg_map_visitor=test; HttpOnly; Path=/api/satellite'}});
  }});
  const server=createServer((req,res)=>void handler(req,res)),base=await listen(server);
  try{
    const response=await fetch(base+'/api/satellite/session',{headers:{cookie:'afg_admin_session=private; afg_map_visitor=public',authorization:'Bearer private','x-actor-id':'forged',origin:'https://actforgoa-field-guide.vercel.app'}});
    assert.equal(response.status,200);assert.match(response.headers.get('set-cookie')!,/afg_map_visitor/);
    assert.equal(calls[0].url,'https://satellite.example.test/api/satellite/session');
    assert.equal(calls[0].headers.get('cookie'),'afg_map_visitor=public');
    assert.equal(calls[0].headers.get('authorization'),null);assert.equal(calls[0].headers.get('x-actor-id'),null);
    assert.equal((await fetch(base+'/api/satellite/files')).status,404);assert.equal(calls.length,1);
  }finally{await close(server);}
});

test('deployed action and nested job entrypoints route public requests without admin login',async()=>{
  const nativeFetch=globalThis.fetch,previous=process.env.SATELLITE_WEB_ORIGIN;process.env.SATELLITE_WEB_ORIGIN='https://satellite.example.test';
  const paths:string[]=[];globalThis.fetch=async input=>{paths.push(String(input));return Response.json({ok:true});};
  const server=createServer((req,res)=>void (req.url?.includes('/jobs/')?jobHandler:actionHandler)(req,res)),base=await listen(server);
  try{
    for(const path of ['session','preview','jobs/a1234567-1234-1234-1234-123456789abc'])assert.equal((await nativeFetch(base+'/api/satellite/'+path)).status,200);
    assert.equal(paths.length,3);assert(paths.every(path=>path.startsWith('https://satellite.example.test/api/satellite/')));
  }finally{globalThis.fetch=nativeFetch;if(previous===undefined)delete process.env.SATELLITE_WEB_ORIGIN;else process.env.SATELLITE_WEB_ORIGIN=previous;await close(server);}
});

test('legacy satellite URLs lead back to the main ActForGoa map',async()=>{
  const {server}=createSatelliteWeb({publicOrigin:'https://satellite.example.test',databasePath:':memory:',staticRoot:'/not-used'}),base=await listen(server);
  try{for(const route of ['/','/map','/admin']){const response=await fetch(base+route,{redirect:'manual'});assert.equal(response.status,302);assert.equal(response.headers.get('location'),'https://actforgoa-field-guide.vercel.app/map');}}
  finally{await close(server);}
});
