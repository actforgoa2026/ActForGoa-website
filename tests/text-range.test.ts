import test from 'node:test';
import assert from 'node:assert/strict';
import { splitCodePointRange } from '../src/text-range.ts';

test('ASCII boundaries include the first character, last character and full source', () => {
  assert.deepEqual(splitCodePointRange('water', 0, 1), { before: '', selected: 'w', after: 'ater' });
  assert.deepEqual(splitCodePointRange('water', 4, 5), { before: 'wate', selected: 'r', after: '' });
  assert.deepEqual(splitCodePointRange('water', 0, 5), { before: '', selected: 'water', after: '' });
});

test('astral characters before and inside the citation do not shift or cut the highlight', () => {
  assert.deepEqual(splitCodePointRange('🌊🐚 A🐟B end', 4, 6), {
    before: '🌊🐚 A', selected: '🐟B', after: ' end',
  });
  assert.deepEqual(splitCodePointRange('🌊water🐟', 1, 6), {
    before: '🌊', selected: 'water', after: '🐟',
  });
  assert.deepEqual(splitCodePointRange('🌊water🐟', 6, 7), {
    before: '🌊water', selected: '🐟', after: '',
  });
});

test('Devanagari, combining marks and line breaks remain unnormalized', () => {
  assert.deepEqual(splitCodePointRange('🌊\nनदी e\u0301 🐟 water\r\nend', 2, 9), {
    before: '🌊\n', selected: 'नदी e\u0301 ', after: '🐟 water\r\nend',
  });
  // Python counts combining code points separately; do not expand to grapheme boundaries.
  assert.deepEqual(splitCodePointRange('e\u0301 नदी', 1, 2), {
    before: 'e', selected: '\u0301', after: ' नदी',
  });
});

test('invalid ranges fail closed instead of clamping or coercing source offsets', () => {
  const invalid: [unknown, unknown][] = [
    [-1, 2], [0, -1], [2, 1], [1, 1], [0, 0], [0.5, 2], [0, 1.5],
    [0, 4], [3, 4], [NaN, 2], [0, Infinity], [Infinity, 2],
    ['0', 2], [0, '2'], [null, 2], [0, undefined], [false, 2],
    [0, Number.MAX_SAFE_INTEGER + 1],
  ];
  for (const [start, end] of invalid) assert.equal(splitCodePointRange('a🐟b', start, end), null);
  assert.equal(splitCodePointRange('', 0, 1), null);
  // The UTF-16 length is not a valid end offset for a Python code-point range.
  assert.equal(splitCodePointRange('🐟', 0, '🐟'.length), null);
});

test('every valid range selects the requested code points and exactly reassembles the source', () => {
  const text = '🌊\r\nनदी e\u0301 👩🏽‍🔬 end';
  const points = Array.from(text);
  for (let start = 0; start < points.length; start++) {
    for (let end = start + 1; end <= points.length; end++) {
      const parts = splitCodePointRange(text, start, end);
      assert.ok(parts);
      assert.equal(parts.selected, points.slice(start, end).join(''));
      assert.equal(parts.before + parts.selected + parts.after, text);
    }
  }
});
