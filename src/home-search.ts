import { topicFlows, topicHref } from './topic-flows';
import { showEmergencyShortcut } from './search-navigation';

type Signal = readonly [pattern: RegExp, weight: number];

// Match the needs covered by the homepage menus, not incidental article text.
// Specific tasks outweigh broad subjects and generic actions such as reporting.
const signals: Record<string, readonly Signal[]> = {
  waste: [
    [/\b(waste|rubbish|garbage|trash|litter|recycl\w*|compost\w*|dumping|landfill)\b/, 4],
    [/\b(food scraps|kitchen scraps|food waste|garden waste|e waste|clean ?ups?|missed collection|bulky items|illegal dumping)\b/, 7],
    [/\b(dispos\w*|collect\w*|dumped|segregat\w*|batteries|electronics)\b/, 3],
  ],
  water: [
    [/\b(water|sewage|sewer\w*|pollution|polluted|rainwater|rivers?|lakes?|wetlands?|coast\w*|beaches?|environment\w*|flood\w*)\b/, 4],
    [/\b(water supply|water pressure|tap water|water quality|rain ?water harvesting|leaking pipe|broken pipe|sewage discharge|air pollution|noise pollution|oil spill)\b/, 7],
    [/\b(taps?|pipes?|drains?|drainage|leak\w*)\b/, 3],
  ],
  community: [
    [/\b(community|rights|rti|panchayat|municipal\w*|legal|lawyer\w*|gram sabha|discriminat\w*|homeless\w*|shelter\w*)\b/, 4],
    [/\b(public records|official records|right to information|legal aid|food bank|food donation\w*|food or shelter|family support|child support|basic needs|give back|get involved|lend a hand|take part)\b/, 7],
    [/\b(volunteer\w*|donat\w*|complaint\w*|report\w*|participat\w*|neighbou?rhood|hungry)\b/, 2],
  ],
  nature: [
    [/\b(nature|wildlife|animals?|dogs?|cats?|cows?|cattle|birds?|snakes?|cobras?|vipers?|pythons?|trees?|forest\w*|biodiversity|vets?|veterinar\w*)\b/, 4],
    [/\b(animals?|dogs?|cats?|cows?|cattle|birds?|snakes?|cobras?|vipers?|pythons?|vets?|veterinar\w*)\b/, 3],
    [/\b(animal rescue|animal welfare|animal cruelty|injured (?:dog|cat|bird|animal)|tree cutting|cutting (?:down )?trees?|trees? (?:cut|being cut|chopped|felled)|wildlife rescue|snake rescue)\b/, 7],
    [/\b(conserv\w*|habitats?|pets?)\b/, 3],
  ],
  food: [
    [/\b(food|farm\w*|agricultur\w*|crops?|seeds?|seedlings?|soil|vegetables?|nurser\w*|irrigat\w*|horticultur\w*|gardening|garden)\b/, 4],
    [/\b(grow\w* (?:my own |some )?(?:food|vegetables|plants)|plant\w* (?:a |some )?(?:tree|trees|seeds)|kitchen garden|krishi card|crop damage|farm support|organic farming)\b/, 7],
  ],
  planning: [
    [/\b(build\w*|construct\w*|transport\w*|planning|mobility|roads?|traffic|buses?|cycling|potholes?|architect\w*|renovat\w*|zoning|permits?)\b/, 4],
    [/\b(building permission|construction permit|illegal construction|public transport|bus routes?|road safety|land use|town planning|solar panels?)\b/, 7],
  ],
  health: [
    [/\b(health|wellbeing|wellness|hospital\w*|clinics?|doctors?|medical|disabilit\w*|accessib\w*|counsell?\w*|therapy|depression|anxiety|psychiatr\w*|blind|wheelchair\w*)\b/, 4],
    [/\b(mental health|disability (?:support|rights)|sight loss|learning support|daily living|child development|health care|healthcare)\b/, 7],
  ],
  culture: [
    [/\b(culture|cultural|heritage|history|historic\w*|arts?|artists?|music|dance|festivals?|museums?|tradition\w*|archaeolog\w*|konkani)\b/, 4],
    [/\b(heritage (?:building|place|site)|restor\w* (?:a |an )?(?:old |historic |heritage )?building|local stories|goan stories)\b/, 7],
  ],
};

function normalize(value: string) {
  return value.toLowerCase().normalize('NFKD').replace(/\p{M}/gu, '')
    .replace(/[’']/g, '').replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, ' ').trim();
}

/** Homepage questions enter the same topic roots as the large navigation buttons. */
export function homeSearchDestination(query: string): string | null {
  const q = normalize(query);
  if (!q) return null;
  // Explicitly rejected needs should not be selected from their keywords alone.
  if (/\b(?:dont|do not) (?:want|need)\b|\bnot (?:about|interested in|looking for|an? emergency)\b/.test(q)) return null;

  // A bite or emergency request must not disappear into wildlife browsing.
  if (showEmergencyShortcut(q)) return '/emergency';

  const exact = topicFlows.find(flow => [flow.label, flow.topic].some(label => normalize(label) === q));
  if (exact) return topicHref(exact.topic);

  // A snake plant is a gardening subject, not an animal-rescue request.
  const subject = q.replace(/\bsnake plants?\b/g, 'gardening');
  const ranked = topicFlows.map(flow => ({
    flow,
    score: (signals[flow.slug] ?? []).reduce((total, [pattern, weight]) => total + (pattern.test(subject) ? weight : 0), 0),
  })).sort((a, b) => b.score - a.score);
  const [best, next] = ranked;

  // A weak or tied match stays on the homepage so the visitor can choose.
  if (!best || best.score < 2 || best.score - (next?.score ?? 0) < 2) return null;
  return topicHref(best.flow.topic);
}
