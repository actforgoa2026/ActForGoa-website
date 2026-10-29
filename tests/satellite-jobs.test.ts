import test from 'node:test';
import assert from 'node:assert/strict';
import {pollSatelliteJob,pendingJobKey,validJobId,sameImageryContext,cacheObservations} from '../src/satellite-jobs.ts';

test('lost polling connection can resume the same reference without creating another job',async()=>{
  const requested:string[]=[];
  const signal=new AbortController().signal;
  let unavailable=true;
  const get=async(id:string)=>{requested.push(id);if(unavailable)throw new Error('connection lost');return {status:'complete',id};};
  await assert.rejects(pollSatelliteJob('existing-job',get,signal,2,0),/connection lost/);
  unavailable=false;
  assert.equal((await pollSatelliteJob('existing-job',get,signal,2,0)).id,'existing-job');
  assert.deepEqual(requested,['existing-job','existing-job']);
});

test('job polling preserves terminal failures, bounds waiting and stops on abort',async()=>{
  const signal=new AbortController().signal;
  assert.deepEqual(await pollSatelliteJob('job',async()=>({status:'failed',error:'cloud retrieval failed'}),signal),{status:'failed',error:'cloud retrieval failed'});
  let calls=0;
  await assert.rejects(pollSatelliteJob('job',async()=>{calls++;return {status:'running'};},signal,2,0),/still processing/);
  assert.equal(calls,2);
  const controller=new AbortController();controller.abort();
  await assert.rejects(pollSatelliteJob('job',async()=>{throw new Error('must not fetch');},controller.signal),{name:'AbortError'});
});

test('restored observations cannot share a timeline across changed dates or footprints',()=>{
  const original={area:{bbox:[73.82,15.48,73.83,15.49] as [number,number,number,number]},start_date:'2026-10-01',end_date:'2026-10-20'};
  assert.equal(sameImageryContext(original,structuredClone(original)),true);
  assert.equal(sameImageryContext(original,{...original,start_date:'2026-10-21',end_date:'2026-10-29'}),false);
  assert.equal(sameImageryContext(original,{...original,area:{bbox:[73.85,15.48,73.86,15.49]}}),false);
  assert.equal(sameImageryContext(original,{...original,area:null}),false);
});

test('persisted recovery references are opaque UUIDs separated by actor',()=>{
  assert.ok(validJobId('9014df8b-69de-4178-8072-135f96239875'));
  for(const input of [null,'','../../other-account','https://example.com','{"token":"secret"}'])assert.equal(validJobId(input),false);
  assert.notEqual(pendingJobKey('alice'),pendingJobKey('bob'));
});

test('pair comparisons preserve loaded dates while keeping the image cache bounded',()=>{
  const observation=(id:string)=>({catalog_scene_id:id,acquired_at:['2026-10-01T05:00:00Z'],image:'fixture',quality:{usable_fraction:1,missing_fraction:0,cloud_shadow_or_uncertain_fraction:0}});
  const existing=Object.fromEntries(Array.from({length:20},(_,i)=>[String(i),observation(String(i))]));
  const next=cacheObservations(existing,[observation('0'),observation('new')]);
  assert.equal(Object.keys(next).length,20);
  assert.ok(next['0']&&next.new&&next['19']);
  assert.equal(next['1'],undefined);
});
