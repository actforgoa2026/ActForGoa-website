import type { RecordItem } from './types';
import { tokens } from './search';

type IntentId = 'snake-rescue' | 'animal-rescue' | 'waste-service' | 'compost' | 'report-trees' | 'participate' | 'read' | 'stories';
type ResultRole = 'contacts' | 'steps' | 'reading' | 'participate';
export interface SearchIntent {
  id: IntentId;
  title: string;
  description: string;
  roles: ResultRole[];
}
export interface SearchResult { record: RecordItem; score: number }

const profiles: Record<IntentId, Omit<SearchIntent, 'id'>> = {
  'snake-rescue': { title: 'Help with a snake nearby', description: 'Rescue contacts and practical guidance come first.', roles: ['contacts', 'steps'] },
  'animal-rescue': { title: 'Help for an animal', description: 'Animal rescue services and practical guidance come first.', roles: ['contacts', 'steps'] },
  'waste-service': { title: 'Find help with waste', description: 'Collection services, recycling contacts and practical guides come first.', roles: ['contacts', 'steps'] },
  compost: { title: 'Start composting', description: 'Practical composting guides come first.', roles: ['steps', 'contacts'] },
  'report-trees': { title: 'What to do about tree cutting', description: 'Reporting guidance and next steps come first.', roles: ['steps', 'contacts'] },
  participate: { title: 'Find a way to get involved', description: 'Ways to participate and organisations seeking help come first.', roles: ['participate'] },
  read: { title: 'Explore and learn', description: 'Guides and background reading come first.', roles: ['reading'] },
  stories: { title: 'Stories from the community', description: 'Stories and local projects come first.', roles: ['reading'] },
};

const normalize = (value: string) => value.toLowerCase().normalize('NFKD').replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
const snake = /\b(snakes?|cobras?|vipers?|pythons?|serpents?)\b/;
const animal = /\b(animals?|dogs?|cats?|cows?|cattle|birds?|wildlife)\b/;
const waste = /\b(rubbish|garbage|trash|waste|recycling|recycle|recyclers?)\b/;
const rescue = /\b(rescue|rescuer|rescuers|remove|removal|help|call|contact|trapped|injured|hurt|sick)\b/;
const reading = /\b(learn|read|research|information|facts|species|identify|identification|biodiversity|history)\b|\btell me about\b/;

function matchesSubject(text: string, query: string): boolean {
  const q = normalize(query);
  if (snake.test(q)) return snake.test(text);
  if (waste.test(q)) return waste.test(text);
  const subjects = tokens(q).filter(word => !/^(learn|read|research|information|facts|stories|story|success|tell|more|volunteer|volunteering|rescue|involved|give|back|lend|hand|take|part|join|participate|like|love)$/.test(word));
  return !subjects.length || subjects.some(word => new RegExp(`\\b${word.replace(/s$/, '')}s?\\b`).test(text));
}

/** Only focus a search when both its subject and the requested task are clear. */
export function inferSearchIntent(query: string): SearchIntent | null {
  const q = normalize(query);
  let id: IntentId | undefined;
  // A human bite/exposure must never be narrowed to animal-rescue contacts.
  if (/\b(snakebite|snakebites|bitten|bit|bites?|biting|first aid|antivenom)\b/.test(q)) return null;
  if (/\bsnake plants?\b/.test(q)) return null;
  if (/\b(no|not|dont|without)\s+(?:need\s+|want\s+)?(?:a\s+)?(?:rescue|help|volunteer|volunteering)\b/.test(q)) return null;
  if (/\b(stories|stories about|success stories)\b/.test(q)) id = 'stories';
  else if ((/\b(want to volunteer|volunteer opportunities|volunteering)\b/.test(q)
    || /\b(volunteer|give back|lend a hand|get involved|take part|join a|participate)\b/.test(q) && !/\b(call|contact|need|find|looking for)\b/.test(q))
    && !/\b(in my|at my|outside my|injured|trapped)\b/.test(q)) id = 'participate';
  else if (reading.test(q) && !/\b(right now|urgent|emergency|in my|at my|outside my)\b/.test(q)) id = 'read';
  else if (snake.test(q) && (rescue.test(q) || /\b(theres|there is|there s|saw|seen|found|spotted|yard|lawn|garden|house|home|kitchen|nearby|what (?:should|can|do) i do)\b/.test(q))) id = 'snake-rescue';
  else if (animal.test(q) && rescue.test(q)) id = 'animal-rescue';
  else if (/\b(compost|composting|kitchen scraps|food scraps)\b/.test(q)) id = 'compost';
  else if (/\btrees?\b/.test(q) && /\b(cutting|cut|felling|felled|chopped)\b/.test(q)) id = 'report-trees';
  else if (waste.test(q) && /\b(take|dispose|disposal|collect\w*|pickup|pick up|remove|removal|recycler|recyclers|service|services|call|contact|where|dumping|missed|outside|yard)\b/.test(q)) id = 'waste-service';
  return id ? { id, ...profiles[id] } : null;
}

function focusRole(record: RecordItem, intent: SearchIntent, query: string): ResultRole | null {
  const title = normalize(record.title);
  // Long documents can mention a service incidentally; capability checks use the
  // listing itself, never a broad topic tag or an embedding similarity alone.
  const text = normalize(`${record.title} ${record.summary} ${record.text}`);
  const person = record.kind === 'organisation' || record.kind === 'contact';
  const resource = record.kind === 'resource';
  switch (intent.id) {
    case 'snake-rescue':
      if (record.id === 'resource-590480849c' || (person && /\b(snake|wildlife) rescue\b/.test(text))) return 'contacts';
      if (record.id === 'guide-animal-welfare' || (resource && snake.test(title) && /\b(safety|rescue|guidance)\b/.test(title))) return 'steps';
      return null;
    case 'animal-rescue': {
      const wild = /\b(birds?|wildlife)\b/.test(normalize(query));
      if (person && (wild ? /\bwildlife rescue\b/ : /\b(veterinary|animal rescue|rescue clinic|rescuing)\b/).test(text)) return 'contacts';
      return record.id === 'guide-animal-welfare' ? 'steps' : null;
    }
    case 'waste-service':
      if (person && waste.test(text) && /\b(collect\w*|services?|solutions?|management|helps people|dispos\w*)\b/.test(text)) return 'contacts';
      if (resource && waste.test(title) && /\b(collection|centres?|helpline)\b/.test(title)) return 'contacts';
      if (resource && (record.id === 'guide-reporting' || (waste.test(title) && /\b(how|segregation|municipal)\b/.test(title)))) return 'steps';
      return null;
    case 'compost':
      if (resource && /\bcompost\w*\b/.test(title)) return 'steps';
      return person && /\bcompost\w*\b/.test(text) ? 'contacts' : null;
    case 'report-trees':
      if (resource && (/\btrees?\b/.test(title) && /\b(cutting|report|stop)\b/.test(title) || ['guide-environmental-protection', 'guide-reporting'].includes(record.id))) return 'steps';
      return null;
    case 'participate':
      return record.kind !== 'contact' && record.id !== 'resource-590480849c' && matchesSubject(text, query)
        && ((record.kind === 'page' && /\bvolunteer\b/.test(title)) || /\b(join us|volunteer with|ways to volunteer|become a volunteer|seeking volunteers|volunteers welcome|get involved)\b/.test(text)) ? 'participate' : null;
    case 'stories':
      return record.kind === 'story' && matchesSubject(text, query) ? 'reading' : null;
    case 'read':
      return (resource || record.kind === 'story') && record.id !== 'resource-590480849c' && matchesSubject(text, query) ? 'reading' : null;
  }
}

/** Focus after hybrid retrieval, so semantic matches cannot reintroduce unrelated kinds. */
export function focusSearchResults(results: SearchResult[], query: string, intent: SearchIntent): SearchResult[] {
  const q = ` ${normalize(query)} `;
  return results.filter(({ record }) => focusRole(record, intent, query)).map(result => {
    // A named locality is evidence; a generic "near me" is not a location.
    const places = (result.record.locality || '').split(/[,–]/).map(normalize).filter(place => place.length > 2 && place !== 'gcr' && place !== 'goa');
    const local = places.some(place => q.includes(` ${place} `));
    const priority = result.record.id === 'resource-590480849c' ? 40 : result.record.kind === 'organisation' ? 12 : 0;
    return { ...result, score: result.score + priority + (local ? 80 : 0) };
  }).sort((a, b) => b.score - a.score || a.record.title.localeCompare(b.record.title));
}

const roleTitles: Record<ResultRole, string> = { contacts: 'Who to contact', steps: 'What to do', reading: 'Guides & stories', participate: 'Ways to get involved' };
export function groupIntentResults(results: SearchResult[], query: string, intent: SearchIntent) {
  return intent.roles.map(role => ({ title: intent.id === 'stories' ? 'Stories & projects' : roleTitles[role], items: results.filter(({ record }) => focusRole(record, intent, query) === role) })).filter(group => group.items.length);
}
