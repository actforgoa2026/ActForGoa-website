import {activityLabel, normalize, safeUrl, split, verification, verificationLabels, type CRMRecord} from './crm-model';
import {crmDirectoryTags} from './crm-directory';
import {premisesIntent} from './research-intent';
import {directoryIdentity} from './directory-quality';

export type CommunityMatch = {record: CRMRecord; reason: string; activity: string; verification: string; source: string};

const words = (value: string) => normalize(value).replace(/[_’']/g, ' ').replace(/[^\p{L}\p{N}]+/gu, ' ').trim().split(/\s+/).filter(Boolean);
const term = (value: string) => value.length > 4 && !/(ss|species)$/.test(value) ? value.replace(/s$/, '') : value;
const stop = new Set('a an and are as at be been by can could did do does for from get goa goas has have help how i in information is it its me my near of on or our please question should tell that the their them there these they this to us want was we what when where which who why will with would you your about find need know understand people organisation organisations organization organizations government'.split(' '));
const concepts = [
  {query: /\b(waste|rubbish|garbage|trash|dumping|recycl\w*|compost\w*)\b/, tags: ['waste', 'cleanups', 'recycling', 'circular economy', 'composting'], label: 'waste and recycling'},
  {query: /\b(water|river\w*|groundwater|khazan\w*|wetland\w*|lake\w*|flood\w*)\b/, tags: ['water', 'wetlands', 'waterways', 'waterbody restoration', 'khazan'], label: 'water and wetlands'},
  {query: /\b(pollution|sewage|effluent|contaminat\w*)\b/, tags: ['pollution', 'sanitation'], label: 'pollution and sanitation'},
  {query: /\b(forest\w*|tree\w*|felling)\b/, tags: ['forests', 'tree conservation', 'reforestation'], label: 'trees and forests'},
  {query: /\b(marine|ocean\w*|coast\w*|beach\w*|coral\w*|turtle\w*|fisher\w*)\b/, tags: ['marine conservation', 'coral reefs', 'fisheries', 'coastal conservation'], label: 'coastal ecosystems'},
  {query: /\b(biodiversity|wildlife|endemic|species|plateau\w*)\b/, tags: ['biodiversity', 'wildlife research', 'citizen science'], label: 'biodiversity'},
  {query: /\b(bird\w*)\b/, tags: ['birds', 'wildlife research'], label: 'birds'},
  {query: /\b(animal welfare|dog\w*|cat\w*|cattle|veterinar\w*)\b/, tags: ['animal welfare'], label: 'animal welfare'},
  {query: /\b(snake\w*|rescu\w*)\b/, tags: ['wildlife rescue', 'rescue'], label: 'wildlife rescue'},
  {query: /\b(farm\w*|agricultur\w*|grow\w*|crop\w*|soil)\b/, tags: ['agriculture', 'organic growing', 'local food'], label: 'farming'},
  {query: /\b(solar|energy|electricity)\b/, tags: ['solar', 'clean energy'], label: 'clean energy'},
  {query: /\b(law|legal|rights|rti|litigation)\b/, tags: ['environmental law', 'civic advocacy'], label: 'law and civic advocacy'},
  {query: /\b(construction|building|land|planning|zoning)\b/, tags: ['land use', 'ecological design'], label: 'land use'},
];

/** Public registry suggestions, not claims of expertise, availability or a current appointment. */
export function researchCommunityMatches(records: CRMRecord[], question: string, limit = 3): CommunityMatch[] {
  const query = words(question).join(' ');
  const tokens = [...new Set(words(question).filter(word => word.length > 2 && !stop.has(word)).map(term))];
  const topics = concepts.filter(concept => concept.query.test(query));
  if (!tokens.length && !topics.length) return [];
  const ranked = records.flatMap(record => {
    // Historical and unresolved entries remain available in the registry, but
    // are not presented as people to approach in a short answer.
    const status = verification(record);
    if (status === 'historical' || status === 'unresolved' || record.activity_status?.startsWith('historical') || record.activity_status === 'deceased_historical_record') return [];
    const source = split(record.source_urls).map(safeUrl).find(Boolean);
    if (!source || !record.name || !record.record_id) return [];
    const identityWords = words([record.name, record.role, record.organization].join(' '));
    const identity = new Set(identityWords.map(term));
    const tags = crmDirectoryTags(record).map(tag => words(tag).join(' '));
    const summaryWords = words(record.summary || '');
    const summary = new Set(summaryWords.map(term));
    const matchedTopics = topics.filter(topic => tags.some(tag => topic.tags.includes(tag)));
    const named = tokens.filter(token => identity.has(token));
    const detail = tokens.filter(token => summary.has(token));
    // Broad administrative/environmental tags alone never establish relevance.
    // A question about panchayat waste must not suggest arbitrary panchayat
    // members just because their title contains the word "panchayat".
    const topicalText = topics.some(topic => topic.query.test([...identityWords, ...summaryWords].join(' ')));
    if (topics.length && !matchedTopics.length && !topicalText) return [];
    if (!matchedTopics.length && !named.length && detail.length < 2) return [];
    const score = matchedTopics.length * 12 + named.length * 8 + Math.min(detail.length, 4) * 4;
    const reason = matchedTopics.length ? `Listed for ${matchedTopics.map(topic => topic.label).slice(0, 2).join(' and ')}.` : `Registry listing matches “${(named.length ? named : detail).slice(0, 3).join(', ')}”.`;
    return [{record, score, reason, activity: activityLabel(record), verification: verificationLabels[status], source}];
  }).sort((a, b) => b.score - a.score || a.record.name.localeCompare(b.record.name));
  const seen = new Set<string>();
  return ranked.filter(match => {
    const identity = directoryIdentity(match.record.record_id);
    if (seen.has(identity)) return false;
    seen.add(identity); return true;
  }).slice(0, Math.max(0, Math.min(limit, 6))).map(({score: _score, ...match}) => match);
}

/** Building questions need a local-body location before a specific office referral. */
export function needsBuildingAuthority(question: string): boolean {
  return !!premisesIntent(question) || /\b(structur\w*|buildings?|construction|demoli\w*|rebuild\w*|renovat\w*)\b/i.test(question);
}

/** Match named local bodies, never a person or a broad district tag as jurisdiction proof. */
export function buildingAuthorityMatches(records: CRMRecord[], location: string): CommunityMatch[] {
  const query = ` ${words(location).join(' ')} `;
  if (query.trim().length < 3) return [];
  const candidates = records.flatMap(record => {
    if (record.collection !== 'government' || record.record_type !== 'government_office') return [];
    const status = verification(record);
    if (status === 'historical' || status === 'unresolved' || record.activity_status?.startsWith('historical')) return [];
    const name = words(record.name).join(' ');
    const place = name.startsWith('village panchayat ') ? name.slice(18) : name.endsWith(' municipal council') ? name.slice(0, -18) : /^corporation of (the )?city of panaji$/.test(name) ? 'panaji' : '';
    if (!place || !query.includes(` ${place} `)) return [];
    const source = safeUrl(record.website_url) || split(record.source_urls).map(safeUrl).find(Boolean);
    if (!source) return [];
    return [{record, source, reason: `CRM listing for ${record.name}. Confirm that this office covers the property's exact location.`, activity:activityLabel(record), verification:verificationLabels[status], place}];
  });
  const seen = new Set<string>();
  return candidates.filter(match => {
    const key = match.place;
    if (seen.has(key)) return false;
    seen.add(key);return true;
  }).slice(0,3).map(({place: _place,...match})=>match);
}
