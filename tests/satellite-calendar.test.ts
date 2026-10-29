import {test} from 'node:test';
import assert from 'node:assert/strict';
import {calendarDate,calendarValue} from '../src/satellite-calendar';

test('satellite calendar preserves acquisition days without UTC conversion', () => {
  for (const value of ['2017-03-28', '2024-02-29', '2026-01-08', '2026-10-30']) {
    const date = calendarDate(value)!;
    assert.equal(date.getHours(), 0);
    assert.equal(calendarValue(date), value);
  }
});

test('satellite calendar rejects impossible or incomplete days', () => {
  for (const value of ['', '2026-02-30', '2026-13-01', '2026-1-8', '2026-10-30T00:00:00Z']) {
    assert.equal(calendarDate(value), undefined);
  }
  assert.equal(calendarValue(undefined), '');
  assert.equal(calendarValue(new Date(NaN)), '');
});
