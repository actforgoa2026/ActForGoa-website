import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { reviewPolytechnicSnapshot } from '../src/polytechnic-directory';
import { filterRecords, filtersFrom, type CRMSnapshot } from '../src/crm-model';

const snapshot: CRMSnapshot = JSON.parse(readFileSync(new URL('../public/data/crm.json', import.meta.url), 'utf8'));
test('review preserves the archived snapshot while preventing an old officeholder from appearing current', () => {
  const reviewed = reviewPolytechnicSnapshot(snapshot);
  const find = (id: string) => reviewed.records.find(r => r.record_id === id)!;
  const office = find('goa-64e8456a16a7');
  const previous = find('goa-553c2b1f141c');
  const current = find('goa-polytechnic-mayem-pramodini-naik');
  assert.match(office.public_phone, /2361235/);
  assert.match(office.public_email, /principalgpbicholim@gmail\.com/);
  assert.match(office.public_email, /gpbicholim\.goa@gov\.in/);
  assert.match(office.activity_verification_notes, /iGOOD/);
  assert.match(office.public_phone, /2360240/);
  assert.equal(previous.public_phone, '');
  assert.equal(previous.activity_status, 'historical_official_listing');
  assert.match(previous.summary, /undated iGOOD/);
  assert.match(current.summary, /confirm current tenure/i);
  assert.equal(current.activity_evidence_date, '2026-10-27');
  assert.match(snapshot.records.find(r => r.record_id === previous.record_id)!.public_phone, /7821833280/);
  assert.equal(reviewPolytechnicSnapshot(reviewed).records.filter(r => r.record_id === current.record_id).length, 1);
  const search = filterRecords(reviewed.records, new Set(), filtersFrom(new URLSearchParams({q:'Pramodini Naik',collection:'all'})), {});
  assert.ok(search.some(r => r.record_id === current.record_id));
});
test('review does not overwrite a different future source identity', () => {
  const changed = { ...snapshot, records: snapshot.records.map(r => r.record_id === 'goa-553c2b1f141c' ? { ...r, name: 'A different person' } : r) };
  assert.equal(reviewPolytechnicSnapshot(changed), changed);
});
