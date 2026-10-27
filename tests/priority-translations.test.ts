import { test } from 'node:test';
import assert from 'node:assert/strict';
import translations from '../src/content/priority-topic-translations.json';
import { topicFlows, topicDescriptions, type TopicAction } from '../src/topic-flows';
import { translatePriority } from '../src/priority-translations';

test('each topic action label, question, step and destination has a draft in both languages', () => {
  const phrases = new Set<string>();
  const add = (s?: string) => { if (s?.trim()) phrases.add(s.trim()); };
  const collect = (actions: TopicAction[]) => actions.forEach(action => {
    add(action.label); add(action.question);
    action.steps?.forEach(add); action.links?.forEach(link => add(link.label));
    if (action.choices) collect(action.choices);
  });
  topicFlows.forEach(flow => { add(flow.label); add(topicDescriptions[flow.slug]); collect(flow.actions); });
  for (const text of phrases) for (const language of ['hi', 'gom'] as const) {
    assert.ok((translations[language] as Record<string, string>)[text], `${language}: ${text}`);
  }
  assert.equal(translatePriority('An untranslated string', 'hi'), 'An untranslated string');
  assert.equal(translatePriority('Report illegal dumping', 'en'), 'Report illegal dumping');
});
