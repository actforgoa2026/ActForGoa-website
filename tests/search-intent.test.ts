import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { hybridSearch } from '../src/search.ts';
import { inferSearchIntent, focusSearchResults, groupIntentResults } from '../src/search-intent.ts';
import { publicCatalogue } from '../src/public-record.ts';
import { practicalGuides } from '../src/guides.ts';
import type { RecordItem } from '../src/types.ts';

const records = publicCatalogue([
  ...JSON.parse(readFileSync('public/data/catalog.json', 'utf8')) as RecordItem[],
  ...practicalGuides,
]);
function search(query: string, semantic: Map<string, number> | null = null) {
  const intent = inferSearchIntent(query);
  assert(intent, `Expected a clear intent for ${query}`);
  const related = hybridSearch(records, query, semantic);
  const focused = focusSearchResults(related, query, intent);
  return { intent, related, focused, groups: groupIntentResults(focused, query, intent) };
}

test('a snake in the yard gives rescue contacts and practical steps, without stories or general wildlife matches', () => {
  for (const query of ["Oh, there's a snake in my front yard", 'theres a snake in my yard', 'Who do I call about a cobra?', 'I found a viper at home']) {
    const { intent, related, focused, groups } = search(query);
    assert.equal(intent.id, 'snake-rescue');
    assert(focused.length < related.length);
    assert.deepEqual(groups.map(group => group.title), ['Who to contact', 'What to do']);
    assert.equal(groups[0].items[0].record.id, 'resource-590480849c');
    assert(groups[0].items.some(item => item.record.id === 'org-27'));
    assert(groups[1].items.some(item => item.record.id === 'guide-animal-welfare'));
    assert(!focused.some(item => item.record.kind === 'story' || item.record.kind === 'page' || item.record.id === 'org-2'));
  }
});

test('a named locality ranks matching volunteers first; near me never invents a location', () => {
  const local = search('snake rescue in Mapusa').groups[0].items;
  assert(local.slice(0, 3).every(item => item.record.locality?.includes('Mapusa')));
  assert.equal(search('snake rescue near me').groups[0].items[0].record.id, 'resource-590480849c');
});

test('semantic scores cannot turn unrelated organisations or stories into rescue services', () => {
  const query = 'snake in my yard';
  const { focused } = search(query, new Map(records.map(record => [record.id, .99])));
  assert(!focused.some(item => ['story', 'page'].includes(item.record.kind)));
  assert(!focused.some(item => item.record.id === 'org-2' || item.record.title.includes('Sanctuary')));
  assert.equal(focused[0].record.id, 'resource-590480849c');
});

test('collection requests find services, while composting requests lead with instructions', () => {
  const waste = search('Where can I take my rubbish?');
  assert.equal(waste.intent.id, 'waste-service');
  assert(waste.groups[0].items.some(item => item.record.title === 'V Recycle'));
  assert(!waste.focused.some(item => item.record.title === 'Saahas Zero Waste'));
  assert(!waste.focused.some(item => /Annual Report|Form 1|Returns/.test(item.record.title)));
  assert.equal(search("Our garbage hasn't been collected").intent.id, 'waste-service');
  const compost = search('How do I compost at home?');
  assert.equal(compost.groups[0].title, 'What to do');
  assert.match(compost.groups[0].items[0].record.title, /Composting at home/);
});

test('animal help and tree reporting use services and guides for the specific need', () => {
  const animal = search('There is an injured dog on the road');
  assert.equal(animal.groups[0].items[0].record.id, 'org-2');
  assert(!animal.focused.some(item => item.record.kind === 'contact'));
  const trees = search('Someone is cutting down trees');
  assert.equal(trees.groups[0].title, 'What to do');
  assert(trees.groups[0].items.some(item => item.record.title === 'Report tree cutting'));
});

test('learning, stories and volunteering do not masquerade as rescue requests', () => {
  const learning = search('I want to learn about snakes');
  assert.equal(learning.intent.id, 'read');
  assert(learning.focused.every(item => ['resource', 'story'].includes(item.record.kind)));
  assert(!learning.focused.some(item => item.record.id === 'resource-590480849c'));
  assert.equal(search('Stories about snakes').intent.id, 'stories');
  assert.equal(search('I want to volunteer for snake rescue').intent.id, 'participate');
  assert(!search('I want to volunteer for snake rescue').focused.some(item => item.record.kind === 'contact' || item.record.id === 'resource-590480849c'));
  assert(search('How can I volunteer?').focused.some(item => item.record.id === 'wp-2249'));
});

test('unclear, negated, named-person, plant and medical queries keep broad search available', () => {
  for (const query of ['', 'snake', 'Griselda Nobay Donvaddo', 'zzzxqvplm', 'snake plants for my garden', 'I do not need rescue', 'snake bit me', 'snakebite first aid']) {
    assert.equal(inferSearchIntent(query), null, query);
  }
});

test('a focus with no supported matches stays empty for the UI to offer related results', () => {
  const intent = inferSearchIntent('snake in my yard')!;
  const unrelated = records.filter(record => record.kind === 'story' || record.id === 'org-2');
  assert.deepEqual(focusSearchResults(hybridSearch(unrelated, 'snake in my yard', new Map(unrelated.map(record => [record.id, .9]))), 'snake in my yard', intent), []);
});
