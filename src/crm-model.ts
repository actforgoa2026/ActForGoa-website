import { crmDirectoryTags } from './crm-directory';

export type CRMRecord = Record<string, string> & { record_id: string; name: string; collection: 'community' | 'government' };
export type CRMSnapshot = { version: string; records: CRMRecord[]; opportunities: CRMRecord[] };
export const stages = { new: 'Not contacted', shortlisted: 'Shortlisted', contacted: 'Contacted', conversation: 'In conversation', partner: 'Working together', closed: 'Closed', do_not_contact: 'Do not contact' };
export type Stage = keyof typeof stages;
export type CRMNote = { stage: Stage; notes: string; followUp: string; lastContact: string; updatedAt: string };
export type Workspace = Record<string, CRMNote>;
export const storageKey = 'actforgoa.crm.v1';
export const split = (value = '') => value.split(' | ').map(v => v.trim()).filter(Boolean);
export const words = (value = '') => value.replace(/_/g, ' ').replace(/\b\w/, c => c.toUpperCase());
export const normalize = (value: string) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export const activityLabels: Record<string, string> = {
  recent_activity_evidenced: 'Recent work evidenced', recent_programme_announced: 'Programme announced',
  current_primary_listing_undated: 'Listed; activity undated', official_project_status_undated: 'Project status undated',
  recent_public_reference_only: 'Recent mention only', recent_host_listing_activity_only: 'Host activity only',
  historical_activity_only: 'Historical work only', recent_public_contact_listing: 'Contact list only',
  historical_official_listing: 'Historical official listing', historical_directory_listing: 'Historical directory listing',
  activity_unverified_after_search: 'Activity unresolved', recent_non_environmental_activity: 'Other recent activity',
  deceased_historical_record: 'Deceased; historical record',
};
export function activityLabel(r: CRMRecord) { return activityLabels[r.activity_status] || 'Activity not assessed'; }
export const verificationLabels = { unresolved: 'Identity or evidence unresolved', historical: 'Historical source only', published: 'Public sources reviewed', government: 'Published role; tenure unconfirmed' };
export function verification(r: CRMRecord): keyof typeof verificationLabels {
  if (/unresolved|identity_conflict|not_established/.test(r.verification_status) || r.activity_status === 'activity_unverified_after_search') return 'unresolved';
  if (r.collection === 'government') return 'government';
  if (r.activity_status.startsWith('historical') || r.activity_status === 'deceased_historical_record') return 'historical';
  return 'published';
}
export function emptyNote(r: CRMRecord): CRMNote {
  return { stage: r.activity_status === 'deceased_historical_record' ? 'do_not_contact' : 'new', notes: '', followUp: '', lastContact: '', updatedAt: '' };
}
export function safeUrl(value: string) {
  try { const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) ? u.href : ''; } catch { return ''; }
}
export function today() { return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()); }
export function isDue(note: CRMNote | undefined, date = today()) { return !!note?.followUp && note.followUp <= date && !['closed', 'do_not_contact'].includes(note.stage); }
export type Filters = { q: string; collection: string; type: string; focus: string; location: string; activity: string; verification: string; contact: string; stage: string; due: boolean; sort: string };
export const collections = { community: 'Community', government: 'Government', opportunities: 'Participation', all: 'All records' };
export const contactLabels = { phone: 'Has a phone', email: 'Has an email', missing: 'No phone or email' };
export function filtersFrom(params: URLSearchParams): Filters {
  const choice = (key: string, values: Record<string, unknown>, fallback = '') => {
    const value = params.get(key) || ''; return Object.hasOwn(values, value) ? value : fallback;
  };
  return { q: params.get('q') || '', collection: choice('collection', collections, 'community'), type: params.get('type') || '', focus: params.get('focus') || '', location: params.get('location') || '', activity: choice('activity', activityLabels), verification: choice('verification', verificationLabels), contact: choice('contact', contactLabels), stage: choice('stage', stages), due: params.get('due') === '1', sort: choice('sort', { relevance: 1, name: 1, activity: 1, followup: 1 }, 'relevance') };
}

// Prepare source text once per snapshot, rather than rebuilding it on every keystroke.
const searchText = (value = '') => normalize(value).replace(/[’']/g, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
const searchCache = new WeakMap<CRMRecord, ReturnType<typeof prepareRecord>>();
function prepareRecord(r: CRMRecord) {
  const name = searchText(r.name);
  const identity = searchText([r.name, r.organization, r.role].join(' '));
  const location = searchText([r.goa_location, r.jurisdiction].join(' '));
  const topics = searchText([r.focus_areas, crmDirectoryTags(r).join(' ')].join(' '));
  const haystack = [identity, location, topics, searchText(r.summary), searchText(r.public_email), searchText(r.public_phone)].join(' ');
  return { name, identity, location, topics, haystack, phones: split(r.public_phone).map(p => p.replace(/\D/g, '')), focus: split(r.focus_areas) };
}
function indexed(r: CRMRecord) {
  let entry = searchCache.get(r);
  if (!entry) { entry = prepareRecord(r); searchCache.set(r, entry); }
  return entry;
}
function queryMatch(q: string) {
  const phrase = searchText(q), tokens = [...new Set(phrase.split(' ').filter(Boolean))];
  const digits = !/[\p{L}]/u.test(q) ? q.replace(/\D/g, '') : '';
  return (r: CRMRecord) => {
    const entry = indexed(r);
    if (digits.length >= 5 && entry.phones.some(phone => phone.includes(digits))) return 100;
    if (!tokens.every(token => entry.haystack.includes(token))) return -1;
    if (!tokens.length) return 0;
    let score = entry.name === phrase ? 1000 : entry.name.startsWith(phrase) ? 500 : entry.name.includes(phrase) ? 250 : 0;
    for (const token of tokens) {
      if (entry.name.split(' ').some(word => word === token)) score += 80;
      else if (entry.name.split(' ').some(word => word.startsWith(token))) score += 40;
      else if (entry.identity.includes(token)) score += 25;
      else if (entry.topics.includes(token)) score += 15;
      else if (entry.location.includes(token)) score += 10;
      else score += 1;
    }
    return score;
  };
}
type FacetKey = 'collection' | 'type' | 'focus' | 'contact' | 'due';
function matchesFilters(r: CRMRecord, opportunities: Set<string>, f: Filters, workspace: Workspace, date: string, except?: FacetKey) {
  const note = workspace[r.record_id] || emptyNote(r);
  if (except !== 'collection' && (f.collection === 'opportunities' ? !opportunities.has(r.record_id) : f.collection !== 'all' && r.collection !== f.collection)) return false;
  if (except !== 'type' && f.type && r.record_type !== f.type) return false;
  if (except !== 'focus' && f.focus && !indexed(r).focus.includes(f.focus)) return false;
  if (f.location && !indexed(r).location.includes(searchText(f.location))) return false;
  if (f.activity && r.activity_status !== f.activity) return false;
  if (f.verification && verification(r) !== f.verification) return false;
  if (f.stage && note.stage !== f.stage) return false;
  if (except !== 'due' && f.due && !isDue(note, date)) return false;
  if (except !== 'contact' && (f.contact === 'phone' && !r.public_phone || f.contact === 'email' && !r.public_email || f.contact === 'missing' && (r.public_phone || r.public_email))) return false;
  return true;
}
export function filterRecords(records: CRMRecord[], opportunities: Set<string>, filters: Filters, workspace: Workspace, date = today()) {
  const match = queryMatch(filters.q);
  return records.map(record => ({ record, score: match(record) }))
    .filter(({ record, score }) => score >= 0 && matchesFilters(record, opportunities, filters, workspace, date))
    .sort((a, b) => {
      if (filters.sort === 'relevance' && a.score !== b.score) return b.score - a.score;
      if (filters.sort === 'followup') { const difference = (workspace[a.record.record_id]?.followUp || '9999').localeCompare(workspace[b.record.record_id]?.followUp || '9999'); if (difference) return difference; }
      if (filters.sort === 'activity') { const difference = (b.record.activity_evidence_date || '').localeCompare(a.record.activity_evidence_date || ''); if (difference) return difference; }
      return a.record.name.localeCompare(b.record.name);
    }).map(({ record }) => record);
}
// Each facet counts alternatives while respecting every other active filter and the query.
export function directoryFacets(records: CRMRecord[], opportunities: Set<string>, filters: Filters, workspace: Workspace, date = today()) {
  const facets: Record<FacetKey, Record<string, number>> = { collection: {}, type: {}, focus: {}, contact: {}, due: {} };
  const match = queryMatch(filters.q);
  const add = (key: FacetKey, value: string) => { facets[key][value] = (facets[key][value] || 0) + 1; };
  for (const r of records) {
    if (match(r) < 0) continue;
    if (matchesFilters(r, opportunities, filters, workspace, date, 'collection')) {
      add('collection', r.collection); add('collection', 'all');
      if (opportunities.has(r.record_id)) add('collection', 'opportunities');
    }
    if (matchesFilters(r, opportunities, filters, workspace, date, 'type')) { add('type', ''); add('type', r.record_type); }
    if (matchesFilters(r, opportunities, filters, workspace, date, 'focus')) {
      add('focus', ''); for (const value of new Set(indexed(r).focus)) add('focus', value);
    }
    if (matchesFilters(r, opportunities, filters, workspace, date, 'contact')) {
      if (r.public_phone) add('contact', 'phone');
      if (r.public_email) add('contact', 'email');
      if (!r.public_phone && !r.public_email) add('contact', 'missing');
    }
    if (matchesFilters(r, opportunities, filters, workspace, date, 'due') && isDue(workspace[r.record_id] || emptyNote(r), date)) add('due', '1');
  }
  return facets;
}
const validDate = (s: string) => s === '' || /^\d{4}-\d{2}-\d{2}$/.test(s) && !Number.isNaN(Date.parse(s)) && new Date(s).toISOString().slice(0, 10) === s;
export function parseBackup(raw: string): Workspace {
  const data = JSON.parse(raw);
  if (!data || data.version !== 1 || !data.records || typeof data.records !== 'object' || Array.isArray(data.records)) throw new Error('Choose an ActForGoa CRM backup (version 1).');
  const result: Workspace = Object.create(null);
  for (const [id, item] of Object.entries(data.records)) {
    const n = item as CRMNote;
    if (!/^goa-[a-z0-9-]+$/i.test(id) || !n || !Object.hasOwn(stages, n.stage) || typeof n.notes !== 'string' || n.notes.length > 50000 || typeof n.followUp !== 'string' || !validDate(n.followUp) || typeof n.lastContact !== 'string' || !validDate(n.lastContact) || typeof n.updatedAt !== 'string' || n.updatedAt !== '' && Number.isNaN(Date.parse(n.updatedAt))) throw new Error('The backup contains an invalid record. Nothing was imported.');
    result[id] = { stage: n.stage, notes: n.notes, followUp: n.followUp, lastContact: n.lastContact, updatedAt: n.updatedAt };
  }
  return result;
}
export function backupJSON(records: Workspace) { return JSON.stringify({ version: 1, exportedAt: new Date().toISOString(), records }, null, 2); }
export function mergeBackup(current: Workspace, incoming: Workspace, replace: boolean): Workspace { return replace ? { ...current, ...incoming } : { ...incoming, ...current }; }
export function exportCSV(records: CRMRecord[], workspace: Workspace) {
  const fields = Object.keys(records[0] || {}).concat(['crm_stage', 'crm_notes', 'crm_follow_up', 'crm_last_contact']);
  const cell = (s: string) => '"' + (/^[\s]*[=+@\-]/.test(s) ? "'" + s : s).replaceAll('"', '""') + '"';
  return '\uFEFF' + [fields, ...records.map(r => { const n = workspace[r.record_id] || emptyNote(r); return [...Object.keys(records[0]).map(f => r[f] || ''), stages[n.stage], n.notes, n.followUp, n.lastContact]; })].map(row => row.map(cell).join(',')).join('\r\n');
}
