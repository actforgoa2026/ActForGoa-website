import type {CRMRecord} from './crm-model';
import {activityLabel, verification, verificationLabels, safeUrl, split, words} from './crm-model';
import type {RecordItem} from './types';
import type {BlogPost, PostInput} from './admin-api';

export type CurationRecord = {id: string; title: string; kind: string; group: 'community' | 'government' | 'resource'; summary: string; topics: string[]; href: string; source: string; evidence: string};

export function curationRecords(crm: CRMRecord[], catalogue: RecordItem[]): CurationRecord[] {
  const records: CurationRecord[] = crm.map(record => ({
    id: record.record_id, title: record.name, kind: words(record.record_type || record.collection), group: record.collection,
    summary: record.summary || record.organization || record.role || '', topics: split(record.focus_areas).map(words),
    href: `/directory/${encodeURIComponent(record.record_id)}`, source: split(record.source_urls || record.source_url).find(safeUrl) || '',
    evidence: `${verificationLabels[verification(record)]} · ${activityLabel(record)}`,
  }));
  const existing = new Set(records.map(record => record.id));
  for (const record of catalogue) {
    if (existing.has(record.id) || record.kind === 'page') continue;
    records.push({id: record.id, title: record.title, kind: record.kind === 'resource' ? 'Guide or resource' : words(record.kind), group: record.kind === 'organisation' || record.kind === 'contact' ? 'community' : 'resource', summary: record.summary, topics: record.topics, href: `/read/${encodeURIComponent(record.id)}`, source: safeUrl(record.source), evidence: record.verification || record.editorialStatus || 'Archived source; check current details'});
    existing.add(record.id);
  }
  return records;
}

const normalize = (value: string) => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export function filterCuration(records: CurationRecord[], query: string, group: string, starred: Set<string>, onlyStarred: boolean) {
  const tokens = normalize(query).split(/\s+/).filter(Boolean);
  return records.filter(record => (!group || record.group === group) && (!onlyStarred || starred.has(record.id)) && tokens.every(token => normalize([record.title, record.summary, record.kind, ...record.topics].join(' ')).includes(token)));
}
export const slugFromTitle = (title: string) => normalize(title).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 100).replace(/-$/g, '');
export const emptyPost = (): PostInput => ({title: '', slug: '', excerpt: '', body: '', tags: []});
export function postInput(post: PostInput): PostInput { return {title: post.title, slug: post.slug, excerpt: post.excerpt, body: post.body, tags: [...post.tags]}; }
export function postChanged(draft: PostInput, saved: PostInput | null) { return JSON.stringify(postInput(draft)) !== JSON.stringify(saved ? postInput(saved) : emptyPost()); }
export function parseTags(text: string) { return [...new Set(text.split(',').map(tag => tag.trim()).filter(Boolean))]; }
export function validatePost(draft: PostInput, publish = false): string {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(draft.slug) || draft.slug.length > 100) return 'Add a URL name using lowercase letters, numbers and single hyphens.';
  if (draft.title.length > 180 || draft.excerpt.length > 500 || draft.body.length > 100000) return 'The story is over a field’s length limit. Shorten it before saving.';
  if (draft.tags.length > 12 || draft.tags.some(tag => tag.length > 40)) return 'Use up to 12 tags, with no more than 40 characters each.';
  if (publish && (!draft.title.trim() || !draft.excerpt.trim() || !draft.body.trim())) return 'Add a title, short introduction and story before publishing.';
  return '';
}
export function postStatus(post: Pick<BlogPost, 'status' | 'hasUnpublishedChanges'>) { return post.status === 'draft' ? 'Draft' : post.hasUnpublishedChanges ? 'Published · changes to publish' : 'Published'; }
