import test from 'node:test';
import assert from 'node:assert/strict';
import {researchCommunityMatches} from '../src/research-community.ts';
import type {CRMRecord} from '../src/crm-model.ts';

const record = (id:string, patch:Partial<CRMRecord>={}):CRMRecord => ({record_id:id,name:id,collection:'community',record_type:'organization',focus_areas:'',summary:'',source_urls:'https://example.org/source',activity_status:'current_primary_listing_undated',verification_status:'public_source_reviewed',...patch});

test('a question finds topical organisations and offices without boosting unrelated general government listings',()=>{
 const results=researchCommunityMatches([
  record('goa-water',{name:'River group',focus_areas:'water | wetlands'}),
  record('goa-office',{name:'Water Resources Department',collection:'government',record_type:'government_office',focus_areas:'government_environment_or_local_services'}),
  record('goa-general',{name:'General Office',collection:'government',focus_areas:'government_general | government_environment_or_local_services'}),
  record('goa-energy',{name:'Solar group',focus_areas:'solar | clean_energy'}),
 ],'Who can help protect water and wetlands?',6);
 assert.deepEqual(new Set(results.map(result=>result.record.record_id)),new Set(['goa-water','goa-office']));
 assert.match(results.find(result=>result.record.record_id==='goa-office')!.verification,/tenure unconfirmed/);
 assert.ok(results.every(result=>result.source==='https://example.org/source'));
});

test('generic or unrelated questions do not produce arbitrary community recommendations',()=>{
 const rows=[record('goa-water',{focus_areas:'water'}),record('goa-general',{collection:'government',focus_areas:'government_general'})];
 assert.deepEqual(researchCommunityMatches(rows,'Can you help me in Goa?'),[]);
 assert.deepEqual(researchCommunityMatches(rows,'What is quantum entanglement?'),[]);
});

test('a waste question does not recommend arbitrary village officeholders by their job title',()=>{
 const rows=[record('goa-officer',{name:'Village Panchayat Member',collection:'government',focus_areas:'government_general'}),record('goa-waste',{name:'Waste service',focus_areas:'waste'})];
 assert.deepEqual(researchCommunityMatches(rows,'What can a village panchayat do about dumping?').map(result=>result.record.record_id),['goa-waste']);
});

test('historical, unresolved and unsourced entries are not suggested as useful contacts',()=>{
 const rows=[
  record('goa-deceased',{focus_areas:'water',activity_status:'deceased_historical_record'}),
  record('goa-history',{focus_areas:'water',collection:'government',activity_status:'historical_official_listing'}),
  record('goa-unresolved',{focus_areas:'water',verification_status:'identity_conflict'}),
  record('goa-no-source',{focus_areas:'water',source_urls:'javascript:alert(1)'}),
  record('goa-listed',{focus_areas:'water'}),
 ];
 const results=researchCommunityMatches(rows,'water');
 assert.deepEqual(results.map(result=>result.record.record_id),['goa-listed']);
 assert.equal(results[0].activity,'Listed; activity undated');
});

test('reviewed duplicate registry identities are presented only once',()=>{
 const rows=[record('goa-3be8492c5821',{focus_areas:'biodiversity'}),record('goa-b3f711f6b7f3',{focus_areas:'biodiversity'})];
 assert.equal(researchCommunityMatches(rows,'biodiversity').length,1);
});

test('species questions do not treat animal welfare as biodiversity expertise',()=>{
 const rows=[record('goa-biodiversity',{focus_areas:'biodiversity'}),record('goa-welfare',{focus_areas:'animal_welfare'})];
 assert.deepEqual(researchCommunityMatches(rows,'Which animals are endemic to Goa?').map(result=>result.record.record_id),['goa-biodiversity']);
 assert.deepEqual(researchCommunityMatches(rows,'Who works on animal welfare?').map(result=>result.record.record_id),['goa-welfare']);
});
