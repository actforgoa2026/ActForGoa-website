import details from './content/directory-details.json';
import mapping from './content/crm-directory-map.json';
import type { CRMRecord } from './crm-model';
import type { DirectoryDetails } from './types';

const curated: Record<string, DirectoryDetails> = details;
const sourceMap: Record<string, { catalogueId: string; source: string }> = mapping;

// Presentation only. Exact source identities connect the two catalogues; names
// and approximate location matches must never merge organisations or people.
export function crmDirectoryDetails(record: CRMRecord): DirectoryDetails | undefined {
  const entry = sourceMap[record.record_id];
  if (!entry || record.record_type !== 'organization' ||
    !record.source_urls.split(' | ').includes(entry.source)) return undefined;
  return curated[entry.catalogueId];
}

export function crmDirectoryTags(record: CRMRecord): string[] {
  const focus = (record.focus_areas || '').split(' | ')
    .filter(tag => tag && !tag.endsWith('_lead') && tag !== 'environmental_relevance_unestablished')
    .map(tag => tag.replaceAll('_', ' ').replace(/^\w/, c => c.toUpperCase()));
  const tags = [...(crmDirectoryDetails(record)?.tags || []), ...focus];
  return tags.filter((tag, index) => tags.findIndex(value => value.toLowerCase() === tag.toLowerCase()) === index);
}

export function crmDirectoryMapUrl(record: CRMRecord): string | undefined {
  const address = crmDirectoryDetails(record)?.address;
  if (!address || record.activity_status === 'deceased_historical_record') return undefined;
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${record.name}, ${address}`)}`;
}

export function crmDirectoryLinks(record: CRMRecord): { label: string; url: string }[] {
  if (record.activity_status === 'deceased_historical_record') return [];
  const extra = crmDirectoryDetails(record)?.links || [];
  const candidates = [
    { label: 'Website', url: record.website_url || extra.find(l => l.label === 'Website')?.url || '' },
    { label: 'Get involved', url: record.volunteer_url },
    { label: 'Instagram', url: record.instagram_url },
    ...extra.filter(l => !['Website', 'Instagram', 'Facebook'].includes(l.label)),
  ];
  const seen = new Set<string>();
  return candidates.filter(link => {
    try {
      const url = new URL(link.url);
      if (!['https:', 'http:'].includes(url.protocol) || seen.has(url.href)) return false;
      seen.add(url.href);
      return true;
    } catch { return false; }
  });
}
