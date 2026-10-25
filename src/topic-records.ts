import type {TopicAction, TopicFlow} from './topic-flows';
import type {RecordItem} from './types';
import {hybridSearch} from './search';

export function actionsInBranch(actions: TopicAction[]): TopicAction[] {
 return actions.flatMap(action => [action, ...actionsInBranch(action.choices ?? [])]);
}

export function topicPeople(records: RecordItem[], flow: TopicFlow, action?: TopicAction): RecordItem[] {
 const people = records.filter(r => r.kind === 'organisation' || r.kind === 'contact');
 const curatedIds = [...new Set(actionsInBranch(action ? [action] : flow.actions).flatMap(a => a.peopleIds ?? []))];
 // Original topic tags are incomplete. Explicitly curated services may belong to another topic.
 const curated = curatedIds.flatMap(id => people.find(r => r.id === id) ?? []);
 if (action && (curatedIds.length || flow.slug !== 'waste')) return curated;
 const related = people.filter(r => r.topics.includes(flow.topic));
 const matched = action ? hybridSearch(related, action.query, null).map(r => r.record) : related;
 return [...new Map([...curated, ...matched].map(r => [r.id, r])).values()];
}
