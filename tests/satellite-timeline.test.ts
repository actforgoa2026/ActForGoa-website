import test from 'node:test';
import assert from 'node:assert/strict';
import {areaError,orderedPair,orderedScenes} from '../src/satellite-timeline.ts';
const scenes=[{id:'later',acquired_at:'2026-10-20T05:44:00Z',scene_cloud_percent:2},{id:'earlier',acquired_at:'2026-10-10T05:44:00Z',scene_cloud_percent:8},{id:'same-time',acquired_at:'2026-10-20T05:44:00Z',scene_cloud_percent:null}];
test('timeline orders real acquisitions, deduplicates scene IDs and rejects reversed or simultaneous pairs',()=>{
  assert.deepEqual(orderedScenes([...scenes,scenes[0]]).map(s=>s.id),['earlier','later','same-time']);
  assert.equal(orderedPair(scenes,'earlier','later'),true);
  for(const pair of [['later','earlier'],['later','same-time'],['missing','later'],['earlier','earlier']])assert.equal(orderedPair(scenes,...pair as [string,string]),false);
});
test('map selection bounds work before sending provider requests',()=>{
  assert.equal(areaError([73.82,15.48,73.83,15.49]),null);
  for(const bbox of [[73,15,74,16],[73.8,15,73.9,15.1],[73.8,15,73.80001,15.00001],[74,15,73.8,15.1],[NaN,15,74,15.1]])assert.ok(areaError(bbox));
});
