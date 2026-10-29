import test from 'node:test';
import assert from 'node:assert/strict';
import {createPlaceSearch,PlaceSearchError} from '../server/map-places.ts';
const feature=(name:string,coordinates:number[]=[73.83,15.5])=>({type:'Feature',geometry:{type:'Point',coordinates},properties:{name,osm_type:'N',osm_id:123,city:'Panaji',state:'Goa'}});

test('place search stays bounded to Goa, strips arbitrary provider fields, and caches repeated user queries',async()=>{
 let time=0,calls=0;
 const search=createPlaceSearch({now:()=>time,fetcher:(async(input)=>{calls++;const url=new URL(String(input));assert.equal(url.origin,'https://photon.komoot.io');assert.equal(url.searchParams.get('bbox'),'73.5,14.7,74.6,16');assert.equal(url.searchParams.get('limit'),'5');assert.equal(url.searchParams.get('q'),'Panaji');return Response.json({features:[feature('Panaji'),feature('Outside',[0,0]),feature('Invalid',[NaN,15])]});}) as typeof fetch});
 assert.deepEqual(await search(' Panaji '),[{id:'N123',name:'Panaji',detail:'Goa',longitude:73.83,latitude:15.5}]);
 assert.equal((await search('panaji')).length,1);assert.equal(calls,1);
 await assert.rejects(search('Artjuna'),(e:unknown)=>e instanceof PlaceSearchError&&e.status===429);
 time=1600;await assert.rejects(search('a'),(e:unknown)=>e instanceof PlaceSearchError&&e.status===400);assert.equal(calls,1);
});
test('single in-flight search prevents parallel provider traffic and failures release the slot',async()=>{
 let release!:()=>void,time=0,calls=0;
 const search=createPlaceSearch({now:()=>time,fetcher:(async()=>{calls++;await new Promise<void>(r=>release=r);return new Response('',{status:503});}) as typeof fetch});
 const first=search('Panaji');time=5000;
 await assert.rejects(search('Artjuna'),(e:unknown)=>e instanceof PlaceSearchError&&e.status===429);
 release();await assert.rejects(first,(e:unknown)=>e instanceof PlaceSearchError&&e.status===502);assert.equal(calls,1);
 const next=search('Panaji');release();await assert.rejects(next);assert.equal(calls,2);
});
test('oversized provider bodies fail safely without leaking their contents',async()=>{
 const search=createPlaceSearch({fetcher:(async()=>new Response('x'.repeat(100001))) as typeof fetch});
 await assert.rejects(search('Panaji'),(e:unknown)=>e instanceof PlaceSearchError&&e.status===502&&!e.message.includes('xxxxx'));
});
test('400 daily provider requests remain a hard cap; cached searches work after exhaustion and UTC reset restores access',async()=>{
 let time=0,calls=0;
 const search=createPlaceSearch({now:()=>time,fetcher:(async()=>{calls++;return Response.json({features:[]});}) as typeof fetch});
 for(let i=0;i<400;i++){time=i*1600;await search('place '+i);}
 await assert.rejects(search('one more'),(e:unknown)=>e instanceof PlaceSearchError&&e.status===429);await search('place 399');assert.equal(calls,400);
 time=86400001;await search('one more');assert.equal(calls,401);
});
