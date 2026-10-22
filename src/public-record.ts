import type { RecordItem } from './types';

// Presentation only: the source catalogue and archived records retain every field.
// Apply to prose too, since the source repeats numbers inside biographies and lists.
function phonePattern(numbers: string[]): RegExp | null {
  const values = [...new Set(numbers.map(number => number.replace(/\D/g, '')).filter(number => number.length >= 7))].sort((a, b) => b.length - a.length);
  return values.length ? new RegExp('\\+?(?:' + values.map(number => number.split('').join('[\\s().-]*')).join('|') + ')', 'g') : null;
}
export function publicRecord(record: RecordItem, cataloguePattern?: RegExp | null): RecordItem {
  const pattern = cataloguePattern ?? phonePattern(record.phones.flatMap(phone => [phone.display, phone.href?.replace(/^tel:/, '') ?? '']));
  const redact = (value: string) => {
    const result = pattern ? value.replace(pattern, '') : value;
    return result.replace(/(?<!\d)\(?0\)?[ .-]*(?:\d[ .()-]*){9}\d(?!\d)/g, '')
      .replace(/(?:\+91[\s()-]*)?\b[6-9]\d{4}[\s-]?\d{5}\b/g, '')
      .replace(/(?:phone|mobile|telephone|tel|contact no\.?)\s*:?\s*(?=[,;|]|$)/gi, '')
      .replace(/[ \t]{2,}/g, ' ').replace(/[\s/–-]+$/g, '').replace(/\((?:res|off)\)$/gi, '').trim();
  };
  return {
    ...record, phones: [], title: redact(record.title), summary: redact(record.summary),
    text: redact(record.text), documentText: record.documentText ? redact(record.documentText) : undefined,
    blocks: record.blocks.map(block => ({ ...block, text: redact(block.text) })).filter(block => /[\p{L}\p{N}]/u.test(block.text)),
    locations: record.locations.map(redact),
    images: record.images?.map(image => ({ ...image, alt: redact(image.alt) })),
    links: record.links.filter(link => !/^(tel:)|wa\.me\/|api\.whatsapp\.com\/send/i.test(link.url))
      .map(link => ({ ...link, label: redact(link.label) })),
  };
}

export function communityDescription(record: RecordItem): string {
  if (record.kind === 'contact') {
    return `Snake rescue volunteer${record.locality ? ` listed for ${record.locality}` : ' listed in Goa'}. Part of ActForGoa’s locality guide to wildlife rescue. The source listing dates to 2018; current availability needs confirmation.`;
  }
  const paragraphs = record.blocks.filter(block => block.type !== 'heading').map(block => block.text.trim()).filter(Boolean);
  const text = paragraphs.join(' ') || record.text.trim();
  if (!text) return `Listed in ActForGoa’s community directory${record.locality ? ` in ${record.locality}` : ''}. A description of their work has not yet been provided in the source listing.`;
  // Prefer actual work over legal registration boilerplate, preserving source sentences.
  const sentences = text.match(/[^.!?]+[.!?]+(?:\s|$)|[^.!?]+$/g) ?? [text];
  const description = sentences.filter(sentence => !/^\s*(registered under|registration number|reg\.? no)/i.test(sentence)).join(' ').replace(/\s+/g, ' ').trim() || text;
  if (description.length <= 620) return description;
  const cut = description.slice(0, 620);
  const sentenceEnd = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf('! '));
  return sentenceEnd > 240 ? cut.slice(0, sentenceEnd + 1) : cut.slice(0, cut.lastIndexOf(' ')) + '…';
}

export function publicCatalogue(records: RecordItem[]): RecordItem[] {
  // Cross-reference the full source catalogue: article prose can repeat a
  // volunteer's landline even when that article's parser missed the field.
  const numbers = [...new Set(records.flatMap(record => record.phones.map(phone => phone.display)))];
  const pattern = phonePattern(numbers);
  return records.map(record => publicRecord(record, pattern));
}
