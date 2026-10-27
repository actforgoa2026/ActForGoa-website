import { lexicalSearch, tokens } from './search.js';
import type { RecordItem } from './types.js';

// Only strip conversational filler from questions; leave ordinary names and
// keyword searches unchanged. The directory still requires all remaining terms.
const filler = new Set('who what where when how why which can could would should do does did is are i me my we our you your please tell find help get need looking call contact looking for a an the in on at to of with in goa near me file apply submit request application'.split(' '));
export function searchTerms(query: string): string {
  if (!/[?]|\b(?:who|what|where|when|how|which|can|could|would|please)\b/i.test(query)) return query.trim();
  const words = query.match(/[\p{L}\p{N}]+/gu) || [];
  const meaningful = words.filter(word => !filler.has(word.toLowerCase()));
  return meaningful.length ? meaningful.join(' ') : query.trim();
}
function firstMatch(text: string, terms: string[]): number {
  const matches = [...text.matchAll(/[\p{L}\p{N}]+/gu)];
  return matches.find(match => terms.includes(match[0].toLowerCase()))?.index ?? -1;
}
export function siteMatches(records: RecordItem[], query: string, limit: number) {
  const expanded = query.replace(/\bright\s+to\s+information\b/gi, 'RTI');
  const normalized = searchTerms(expanded);
  const terms = tokens(normalized);
  return lexicalSearch(records, normalized).map(({record,score}) => {
    const text = record.text || '';
    const index = firstMatch(text, terms);
    // An early exact match is more useful than a brief late mention, without
    // replacing the existing title and intent ranking.
    const relevance = score + (index >= 0 && index < 2000 ? 3 : 0);
    const start = index > 250 ? Math.max(0,index-250) : 0;
    return {record, relevance, excerpt:text.slice(start,start+1600)};
  }).sort((a,b)=>b.relevance-a.relevance || a.record.title.localeCompare(b.record.title)).slice(0,limit);
}
