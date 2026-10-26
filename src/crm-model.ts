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
export function filtersFrom(params: URLSearchParams): Filters {
  return { q: params.get('q') || '', collection: params.get('collection') || 'community', type: params.get('type') || '', focus: params.get('focus') || '', location: params.get('location') || '', activity: params.get('activity') || '', verification: params.get('verification') || '', contact: params.get('contact') || '', stage: params.get('stage') || '', due: params.get('due') === '1', sort: params.get('sort') || 'name' };
}
export function filterRecords(records: CRMRecord[], opportunities: Set<string>, filters: Filters, workspace: Workspace, date = today()) {
  const tokens = normalize(filters.q.trim()).split(/\s+/).filter(Boolean);
  return records.filter(r => {
    const note = workspace[r.record_id] || emptyNote(r);
    if (filters.collection === 'opportunities' ? !opportunities.has(r.record_id) : filters.collection !== 'all' && r.collection !== filters.collection) return false;
    if (filters.type && r.record_type !== filters.type || filters.focus && !split(r.focus_areas).includes(filters.focus)) return false;
    if (filters.location && !normalize(r.goa_location + ' ' + r.jurisdiction).includes(normalize(filters.location))) return false;
    if (filters.activity && r.activity_status !== filters.activity || filters.verification && verification(r) !== filters.verification) return false;
    if (filters.stage && note.stage !== filters.stage || filters.due && !isDue(note, date)) return false;
    if (filters.contact === 'phone' && !r.public_phone || filters.contact === 'email' && !r.public_email || filters.contact === 'missing' && (r.public_phone || r.public_email)) return false;
    const haystack = normalize([r.name, r.organization, r.role, r.summary, r.goa_location, r.jurisdiction, r.focus_areas.replaceAll('_', ' '), r.public_phone, r.public_email, crmDirectoryTags(r).join(' ')].join(' '));
    return tokens.every(t => haystack.includes(t));
  }).sort((a, b) => {
    if (filters.sort === 'followup') { const difference = (workspace[a.record_id]?.followUp || '9999').localeCompare(workspace[b.record_id]?.followUp || '9999'); if (difference) return difference; }
    if (filters.sort === 'activity') { const difference = b.activity_evidence_date.localeCompare(a.activity_evidence_date); if (difference) return difference; }
    return a.name.localeCompare(b.name);
  });
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
