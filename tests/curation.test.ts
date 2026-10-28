import test from 'node:test';
import assert from 'node:assert/strict';
import { parseStarredIds, prioritizeStarred } from '../src/curation.ts';

test('curation promotes only existing relevant matches and preserves ordering within groups', () => {
  const matches = [{ id:'strong' }, { id:'star-two' }, { id:'ordinary' }, { id:'star-one' }];
  const result = prioritizeStarred(matches,new Set(['unrelated','star-one','star-two']), item=>item.id);
  assert.deepEqual(result.map(item=>item.id),['star-two','star-one','strong','ordinary']);
  assert.deepEqual(matches.map(item=>item.id),['strong','star-two','ordinary','star-one']);
  assert.equal(result.length,matches.length);
});

test('invalid or unavailable curation leaves public ordering intact', () => {
  for (const input of [null, {}, {starredIds:'oops'}, {starredIds:[null,23,'/invalid']}]) {
    assert.deepEqual(prioritizeStarred(['a','b'],parseStarredIds(input), item=>item),['a','b']);
  }
  assert.deepEqual([...parseStarredIds({starredIds:['goa-community-1','guide-farming','goa-community-1']})],['goa-community-1','guide-farming']);
});
