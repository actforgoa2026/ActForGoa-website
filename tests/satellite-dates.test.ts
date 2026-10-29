import test from 'node:test';
import assert from 'node:assert/strict';
import {calendarDate,dateValue} from '../src/satellite-dates.ts';

test('calendar values retain their day across timezone and daylight-saving boundaries',()=>{
 const previous=process.env.TZ;
 try {
  for(const zone of ['Asia/Kolkata','America/Los_Angeles','Pacific/Auckland']){
   process.env.TZ=zone;
   for(const day of ['2026-03-08','2026-11-01','2024-02-29','2026-10-29'])assert.equal(dateValue(calendarDate(day)),day);
  }
 }finally{if(previous===undefined)delete process.env.TZ;else process.env.TZ=previous;}
});
test('calendar rejects impossible or non-date-only values',()=>{
 for(const day of ['2026-02-29','2026-13-01','2026-04-31','2026-10-29T00:00:00Z',''])assert.equal(calendarDate(day),undefined);
 assert.equal(dateValue(undefined),'');
});
