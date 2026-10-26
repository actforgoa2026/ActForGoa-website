import details from './content/directory-details.json';
import type { DirectoryDetails, RecordItem } from './types';

const curated: Record<string, DirectoryDetails> = details;

export function enrichDirectory(record: RecordItem): RecordItem {
  if (record.kind !== 'organisation' && record.kind !== 'contact') return record;
  const directory = curated[record.id] ?? {
    tags: record.kind === 'contact' ? ['Snake rescue', 'Wildlife'] : record.topics,
    sources: [record.source],
  };
  return {
    ...record, directory,
    locality: directory.locality ?? record.locality,
    locations: directory.address ? [directory.address] : record.locations,
    image: directory.photo?.src ?? record.image,
    imageSource: directory.photo?.source ?? record.imageSource,
  };
}

export function directoryTags(record: RecordItem): string[] {
  return record.directory?.tags.length ? record.directory.tags : record.topics;
}

// A search link is deliberately not a claim that a precise place ID was matched.
// Locality-only volunteer records never acquire a business pin or directions.
export function directoryMapUrl(record: RecordItem): string | null {
  if (record.kind !== 'organisation') return null;
  const address = record.locations.find(value => value.trim().length > 5 && !/^goa(?:,? india)?$/i.test(value.trim()));
  if (!address) return null;
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${record.title}, ${address}`)}`;
}

export function directoryLinks(record: RecordItem): {label:string;url:string}[] {
  const sourceLinks = record.directory?.links ?? record.links;
  const seen = new Set<string>();
  return sourceLinks.filter(link => {
    try {
      const url = new URL(link.url);
      if (!['https:', 'http:'].includes(url.protocol) || seen.has(url.href)) return false;
      seen.add(url.href);
      return true;
    } catch { return false; }
  });
}
