import type {ResearchDomain, ResearchEvidence} from './research-model';

export const readingTopics = [
  {id:'rivers',label:'Rivers & wetlands',domain:'ecology',query:'Goa rivers wetlands khazan estuaries water ecology'},
  {id:'forests',label:'Forests & wildlife',domain:'ecology',query:'Goa forests wildlife biodiversity endemic species'},
  {id:'coasts',label:'Coasts & plateaus',domain:'ecology',query:'Goa coastal dunes lateritic plateaus mangroves habitats'},
  {id:'farming',label:'Farming & soil',domain:'ecology',query:'Goa agriculture paddy farming soil ecosystem'},
  {id:'local-government',label:'Local government',domain:'legal',query:'Goa panchayat municipality local government powers duties'},
  {id:'environment',label:'Environment & planning',domain:'legal',query:'Goa environment protection planning building permissions rules'},
  {id:'records',label:'Public records & rights',domain:'legal',query:'Goa Right to Information public records inspection application'},
  {id:'animals',label:'Animal welfare',domain:'legal',query:'Goa animal welfare cruelty protection rules'},
] as const;

export function topicsForDomain(domain:ResearchDomain) {
  return readingTopics.filter(topic=>domain==='all'||topic.domain===domain);
}

/** A passage search can return several pages of the same source. Browse each document once. */
export function browseDocuments(results:ResearchEvidence[]):ResearchEvidence[] {
  return [...new Map(results.map(source=>[source.document_id,source])).values()]
    .sort((a,b)=>a.title.localeCompare(b.title));
}

export function fullDocumentPath(source:Pick<ResearchEvidence,'document_id'|'generation'>):string {
  return `/documents/${encodeURIComponent(source.document_id)}?${new URLSearchParams({generation:source.generation})}`;
}

export function publisherHost(url:string):string {
  try {return new URL(url).hostname;} catch {return 'Saved source';}
}
