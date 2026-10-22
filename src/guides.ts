import documents from './content/guides.json';
import type {RecordItem} from './types';

export const guideDocuments = documents;
export type GuideDocument = (typeof documents)[number];
export const practicalGuides: RecordItem[] = documents.filter(d => d.listed).map(d => ({
 id: d.id, title: d.title, kind: 'resource', source: '/read/guide-sources', sourceApi: '', sourceStatus: null,
 summary: d.summary, text: d.markdown, blocks: [], topics: d.topics, image: '', imageSource: '',
 publishedAt: '', updatedAt: '2026-10-22', retrievedAt: '2026-10-22', phones: [], emails: [], locations: [],
 documents: d.templates.map(t => ({...t, status: null})), links: [], verification: 'draft-review-required', editorialStatus: 'authored-practical-guide',
}));

export const guideHeadingId = (text: string) => text.toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim().replace(/\s+/g, '-');
