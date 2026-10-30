import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyHeritageStory,heritageCoordinates,readHeritageDraft,heritageStoryEmail} from '../src/heritage-story.ts';

test('heritage drafts recover safely from unavailable or malformed browser data',()=>{
  for(const raw of [null,'broken','[]','3','null','{"story":42}']) assert.deepEqual(readHeritageDraft(raw),emptyHeritageStory);
  const saved=readHeritageDraft('{"title":"A village story","latitude":"15.5","longitude":"73.9","unexpected":"ignored"}');
  assert.equal(saved.title,'A village story');
  assert(!('unexpected' in saved));
  assert.deepEqual(heritageCoordinates(saved),[15.5,73.9]);
});

test('pins require a complete finite coordinate pair in Goa',()=>{
  for(const [latitude,longitude] of [['',''],['','73.9'],['15.5',''],['NaN','73.9'],['200','73.9'],['15.5','0'],['Infinity','73.9']]) assert.equal(heritageCoordinates({...emptyHeritageStory,latitude,longitude}),null);
});

test('prepared story email preserves the pin, credit and literal user text without publishing',()=>{
  const draft={...emptyHeritageStory,title:'A & B + heritage',place:'A public place',story:'First line\nSecond & third?',credit:'Photo: A + B',name:'Local tester',email:'local@example.test',latitude:'15.5',longitude:'73.9'};
  const url=new URL(heritageStoryEmail(draft));
  assert.equal(url.protocol,'mailto:');assert.equal(url.pathname,'info@actforgoa.org');
  assert.equal(url.searchParams.get('subject'),'Celebrate Goan heritage: A & B + heritage');
  const body=url.searchParams.get('body')!;
  assert(body.includes(draft.story));assert(body.includes(draft.credit));assert(body.includes('https://www.google.com/maps/search/?api=1&query=15.5,73.9'));assert(body.includes('Please review this story'));
  assert(new URL(heritageStoryEmail(emptyHeritageStory)).searchParams.get('body')!.includes('No pin added'));
});
