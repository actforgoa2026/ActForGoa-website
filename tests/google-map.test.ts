import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {serveMapConfig} from '../server/map-config.ts';
import {bboxBounds,boundsBbox,withinGoa} from '../src/google-map.ts';

test('Google coordinates preserve satellite west/south/east/north order and Goa boundaries',()=>{
  const bbox:[number,number,number,number]=[73.845,15.49,73.85,15.495];
  const bounds=bboxBounds(bbox);
  assert.deepEqual(bounds,{west:73.845,south:15.49,east:73.85,north:15.495});
  assert.deepEqual(boundsBbox({toJSON:()=>bounds} as google.maps.LatLngBounds),bbox);
  assert.ok(withinGoa(15.49,73.845));
  for(const pair of [[NaN,74],[15,Infinity],[0,0],[74,15],[16.01,74],[15,75]])assert.equal(withinGoa(...pair as [number,number]),false);
});

test('public map configuration never falls back to the server key or exposes other credentials',async()=>{
  const originalServer=process.env.GOOGLE_MAPS_API_KEY,originalBrowser=process.env.GOOGLE_MAPS_BROWSER_KEY;
  process.env.GOOGLE_MAPS_API_KEY='private-server-sentinel';delete process.env.GOOGLE_MAPS_BROWSER_KEY;
  const server=createServer((req,res)=>serveMapConfig(req,res));
  await new Promise<void>(r=>server.listen(0,'127.0.0.1',r));
  const address=server.address();assert(address&&typeof address==='object');const url=`http://127.0.0.1:${address.port}`;
  try{
    const absent=await fetch(url);assert.equal(absent.status,503);assert.doesNotMatch(await absent.text(),/sentinel/);
    process.env.GOOGLE_MAPS_BROWSER_KEY='invalid';assert.equal((await fetch(url)).status,503);
    const browserKey='AIza'+'a'.repeat(35);process.env.GOOGLE_MAPS_BROWSER_KEY=browserKey;
    const configured=await fetch(url);assert.equal(configured.status,200);assert.equal(configured.headers.get('cache-control'),'no-store');assert.deepEqual(await configured.json(),{browserKey});
    const post=await fetch(url,{method:'POST'});assert.equal(post.status,405);assert.doesNotMatch(await post.text(),/AIza/);
  }finally{
    if(originalServer===undefined)delete process.env.GOOGLE_MAPS_API_KEY;else process.env.GOOGLE_MAPS_API_KEY=originalServer;
    if(originalBrowser===undefined)delete process.env.GOOGLE_MAPS_BROWSER_KEY;else process.env.GOOGLE_MAPS_BROWSER_KEY=originalBrowser;
    await new Promise<void>(r=>server.close(()=>r()));
  }
});
