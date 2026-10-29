import data from './content/climate-plan.json';
import type { RecordItem } from './types';

export interface PlanReference {
  label: string;
  start: number;
  end: number;
}
export interface PlanAction {
  title: string;
  description: string;
  agencies: string;
  reference: PlanReference;
}
export interface PlanTopic {
  id: string;
  title: string;
  summary: string;
  keywords: string[];
  references: PlanReference[];
  actions: PlanAction[];
  question: string;
  related: string[];
  note?: string;
}
export interface PlanChapter extends PlanReference {
  id: string;
  title: string;
  description: string;
  children?: PlanReference[];
  scanned?: boolean;
}

export const climatePlan = data as typeof data & { topics: PlanTopic[]; chapters: PlanChapter[] };
export const planTopics: PlanTopic[] = data.topics;
export const planChapters: PlanChapter[] = data.chapters;

/** This edition uses two-page spreads, starting with printed pages 4–5 at PDF page 4. */
export function planPdfPage(printedPage: number): number {
  if (!Number.isInteger(printedPage) || printedPage < 4 || printedPage > 218) {
    throw new RangeError('Printed page must be between 4 and 218 in this edition.');
  }
  return Math.floor((printedPage + 4) / 2);
}
export function planPageHref(printedPage: number): string {
  return `${data.source.url}#page=${planPdfPage(printedPage)}`;
}
export function planPageLabel(reference: PlanReference): string {
  return reference.start === reference.end ? `p. ${reference.start}` : `pp. ${reference.start}–${reference.end}`;
}
function normalize(text: string): string {
  return text.normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}
function matches(text: string, query: string): boolean {
  const haystack = normalize(text);
  return normalize(query).split(' ').filter(Boolean).every(word => haystack.includes(word));
}
export function searchPlanTopics(query: string): PlanTopic[] {
  return planTopics.filter(topic => matches([
    topic.title, topic.summary, topic.question, ...topic.keywords,
    ...topic.references.map(reference => reference.label),
    ...topic.actions.map(action => `${action.title} ${action.description} ${action.agencies}`),
  ].join(' '), query));
}
export function searchPlanChapters(query: string): PlanChapter[] {
  return planChapters.filter(chapter => matches([
    chapter.title, chapter.description, chapter.label, ...chapter.children?.map(child => child.label) ?? [],
  ].join(' '), query));
}

export const climatePlanRecord: RecordItem = {
  id: 'goa-sapcc', kind: 'resource', title: 'Goa’s climate action plan, explained',
  source: data.source.url, sourceApi: '', sourceStatus: 200,
  summary: 'Explore the 2023–2033 SAPCC by topic, browse every chapter, and find selected actions with exact source pages.',
  text: ['SAPCC State Action Plan for Climate Change Goa 2023 2033', ...planTopics.map(topic =>
    [topic.title, topic.summary, ...topic.keywords, ...topic.actions.map(action => `${action.title} ${action.agencies}`)].join(' ')),
  ].join('\n'),
  blocks: [], topics: ['Water & environment', 'Food & farming', 'Nature & wildlife', 'Planning & mobility', 'Health & wellbeing'],
  image: '', imageSource: '', publishedAt: data.source.publishedAt, updatedAt: data.source.checkedAt,
  retrievedAt: data.source.retrievedAt, phones: [], emails: [], locations: ['Goa'],
  documents: [{label: 'Goa SAPCC 2023–2033 · government PDF', url: data.source.url, status: 200, pages: data.source.pdfPages}],
  links: [{label: 'Explore the climate plan', url: '/climate-plan'}],
  verification: 'Source downloaded 29 October 2026. Plain-language navigation by ActForGoa. Implementation status is not independently verified.',
  editorialStatus: 'authored-climate-plan-navigation',
};
