export const categories = [
  { id: 'burning', label: 'Illegal burning', description: 'Waste, plastic or other material being burned.' },
  { id: 'dumping', label: 'Illegal dumping', description: 'Waste left on land, roadsides or in water.' },
  { id: 'tree-cutting', label: 'Illegal tree cutting', description: 'Trees being cut or damaged without apparent permission.' },
  { id: 'water-pollution', label: 'Water pollution', description: 'Sewage, discharge or contamination.' },
  { id: 'other', label: 'Something else', description: 'Another environmental concern.' },
] as const;
export const statuses = ['new', 'in_review', 'resolved', 'closed'] as const;
export const statusLabels = { new: 'New', in_review: 'In review', resolved: 'Resolved', closed: 'Closed' };
export const MAX_PHOTOS = 3;
export const MAX_PHOTO_BYTES = 8 * 1024 * 1024;
export type Coordinates = { latitude: number; longitude: number; accuracy?: number };
export type ReportDraft = {
  category: string; description: string; observedAt: string; location: string;
  coordinates: Coordinates | null; email: string; consent: boolean;
};
export const emptyDraft: ReportDraft = { category: '', description: '', observedAt: '', location: '', coordinates: null, email: '', consent: false };
export function validateReport(value: unknown): asserts value is ReportDraft {
  if (!value || typeof value !== 'object') throw new Error('Please complete the report.');
  const d = value as ReportDraft;
  if (!categories.some(c => c.id === d.category)) throw new Error('Choose an incident category.');
  if (typeof d.description !== 'string' || d.description.trim().length < 10 || d.description.length > 3000) throw new Error('Describe what you saw in 10 to 3,000 characters.');
  if (typeof d.location !== 'string' || d.location.trim().length < 3 || d.location.length > 500) throw new Error('Add a place or landmark in 3 to 500 characters.');
  if (typeof d.observedAt !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{3})?)?Z$/.test(d.observedAt) || !Number.isFinite(Date.parse(d.observedAt)) || Date.parse(d.observedAt) > Date.now() + 60000) throw new Error('Choose a valid time in the past.');
  if (new Date(d.observedAt).toISOString().slice(0, 16) !== d.observedAt.slice(0, 16)) throw new Error('Choose a real calendar date and time.');
  if (typeof d.email !== 'string' || d.email.length > 254 || (d.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email))) throw new Error('Enter a valid email or leave it blank.');
  if (d.coordinates !== null) {
    const c = d.coordinates;
    if (!c || !Number.isFinite(c.latitude) || !Number.isFinite(c.longitude) || Math.abs(c.latitude) > 90 || Math.abs(c.longitude) > 180 || (c.accuracy !== undefined && (!Number.isFinite(c.accuracy) || c.accuracy < 0))) throw new Error('Check the location coordinates.');
  }
  if (d.consent !== true) throw new Error('Confirm you want to send this report for private review.');
}
