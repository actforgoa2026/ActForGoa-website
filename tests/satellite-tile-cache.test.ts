import test from 'node:test';
import assert from 'node:assert/strict';
import {EarthEngineTileCache,earthEngineTile,tileIntersectsBounds} from '../src/satellite-tile-cache';

const url=(key:string)=>`https://earthengine.googleapis.com/maps/${key}/tiles/14/11550/7478`;
const signal=()=>new AbortController().signal;
const response=()=>new Response(new Blob(['test tile'],{type:'image/png'}),{headers:{'content-type':'image/png'}});
const noStorage=Promise.resolve(null);

test('zoomed-in children reuse the same native-resolution tile with correct crops',()=>{
  const parents=new Set<string>();
  for(let x=400;x<404;x++)for(let y=800;y<804;y++){
    const tile=earthEngineTile(x,y,16);parents.add(`${tile.z}/${tile.x}/${tile.y}`);
    assert.equal(tile.scale,4);assert.equal(tile.left,-(x%4)*256);assert.equal(tile.top,-(y%4)*256);
  }
  assert.deepEqual([...parents],['14/100/200']);
  assert.deepEqual(earthEngineTile(2,3,10),{z:10,x:2,y:3,scale:1,left:-0,top:-0});
  assert.equal(earthEngineTile(-1,1,16).left,-768);
  const bounds=[73.67,14.9,74.34,15.81];
  assert.equal(tileIntersectsBounds(722,467,10,bounds),true);
  assert.equal(tileIntersectsBounds(700,467,10,bounds),false);
});

test('simultaneous children share one fetch and revisiting uses memory',async()=>{
  let calls=0;const cache=new EarthEngineTileCache(async()=>{calls++;return response();},noStorage);
  const tiles=await Promise.all(Array.from({length:16},()=>cache.load(url('first'),signal())));
  assert.equal(calls,1);assert.equal(cache.stats.shared,15);
  assert.ok(tiles.every(tile=>tile===tiles[0]));
  assert.equal(await cache.load(url('first'),signal()),tiles[0]);
  assert.equal(calls,1);assert.equal(cache.stats.memoryHits,1);
  await cache.load(url('different-period'),signal());assert.equal(calls,2);
});

test('expired pixels are fetched again without extending their age on reads',async()=>{
  let now=100,calls=0;const cache=new EarthEngineTileCache(async()=>{calls++;return response();},noStorage,()=>now);
  await cache.load(url('expiry'),signal(),110);
  now=105;await cache.load(url('expiry'),signal(),200);assert.equal(calls,1);
  now=111;await cache.load(url('expiry'),signal(),200);assert.equal(calls,2);
});

test('failed responses do not poison retries; unexpected destinations never fetch',async()=>{
  let calls=0;const cache=new EarthEngineTileCache(async()=>++calls===1?new Response('unavailable',{status:503}):response(),noStorage);
  await assert.rejects(cache.load(url('retry'),signal()));
  await cache.load(url('retry'),signal());assert.equal(calls,2);
  await assert.rejects(cache.load('https://example.com/tile',signal()));assert.equal(calls,2);
  cache.invalidate(url('retry'));
  await cache.load(url('retry'),signal());assert.equal(calls,3);
});

test('persistent cache survives a new instance and unavailable storage falls back',async()=>{
  const entries=new Map<string,Response>();
  const store={match:async(key:string|Request)=>entries.get(typeof key==='string'?key:key.url)?.clone(),put:async(key:string,value:Response)=>{entries.set(key,value);},keys:async()=>[...entries.keys()].map(key=>new Request(key)),delete:async(key:Request)=>entries.delete(key.url)} as unknown as Cache;
  const storage=Promise.resolve(store);let calls=0;
  const fetcher=async()=>{calls++;return response();};
  const first=new EarthEngineTileCache(fetcher,storage);
  await first.load(url('persist'),signal());
  // Allow the non-blocking cache write to finish, independent of display.
  await new Promise(resolve=>setImmediate(resolve));
  const second=new EarthEngineTileCache(fetcher,storage);
  await second.load(url('persist'),signal());assert.equal(calls,1);assert.equal(second.stats.diskHits,1);
  const blocked={match:async()=>{throw Error('Storage disabled');},put:async()=>{throw Error('Storage disabled');}} as unknown as Cache;
  await new EarthEngineTileCache(fetcher,Promise.resolve(blocked)).load(url('blocked'),signal());assert.equal(calls,2);
});

test('memory evicts older tiles at the count and byte bounds',async()=>{
  let calls=0;const cache=new EarthEngineTileCache(async()=>{calls++;return response();},noStorage);
  for(let i=0;i<97;i++)await cache.load(url(String(i)),signal());
  await cache.load(url('96'),signal());assert.equal(calls,97);
  await cache.load(url('0'),signal());assert.equal(calls,98);
  let largeCalls=0;
  const large=new EarthEngineTileCache(async()=>{largeCalls++;return new Response(new Blob([new Uint8Array(2*1024*1024)],{type:'image/png'}),{headers:{'content-type':'image/png'}});},noStorage);
  for(let i=0;i<13;i++)await large.load(url(String(i)),signal());
  await large.load(url('0'),signal());assert.equal(largeCalls,14);
});

test('network concurrency is bounded and abandoned queued views are not fetched',async()=>{
  let active=0,peak=0,calls=0;const release:Array<()=>void>=[];
  const cache=new EarthEngineTileCache(async()=>{calls++;active++;peak=Math.max(peak,active);await new Promise<void>(resolve=>release.push(resolve));active--;return response();},noStorage);
  const loads=Array.from({length:12},(_,i)=>cache.load(url(String(i)),signal()));
  const abandoned=new AbortController();
  const rejected=assert.rejects(cache.load(url('abandoned'),abandoned.signal),{name:'AbortError'});abandoned.abort();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(calls,12);release.forEach(resolve=>resolve());await Promise.all(loads);await rejected;
  assert.equal(peak,12);assert.equal(calls,12);
});
