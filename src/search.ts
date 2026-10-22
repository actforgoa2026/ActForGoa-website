import type {RecordItem} from './types';
import config from '../shared/search-config.json';
const stop=new Set(config.stopWords.split(' '));
const weights=config.weights;
export const tokens=(value:string)=>value.toLowerCase().normalize('NFKD').replace(/[^a-z0-9\s]/g,' ').split(/\s+/).filter(t=>t.length>1&&!stop.has(t));
const intents=config.intents.map(intent=>({...intent,trigger:new RegExp(intent.pattern,'i')}));
export function lexicalSearch(records:RecordItem[],query:string){
 const terms=tokens(query),intent=intents.filter(x=>x.trigger.test(query));
 const expanded=[...new Set(intent.flatMap(x=>x.terms).filter(t=>!terms.includes(t)))];
 if(!query.trim())return records.map(record=>({record,score:0}));
 if(!terms.length&&!expanded.length)return [];
 const matches=records.map(record=>{
  const title=record.title.toLowerCase(), body=(record.text+' '+(record.documentText||'')).toLowerCase(),topic=record.topics.join(' ').toLowerCase();
  const tset=new Set(tokens(title)),bset=new Set(tokens(body));
  let score=0,hit=0;
  for(const t of terms){if(tset.has(t)||title.includes(t)){score+=weights.title;hit++}else if(bset.has(t)){score+=weights.body;hit++}else if(topic.includes(t)){score+=weights.topic}}
  for(const t of expanded){if(title.includes(t))score+=weights.expandedTitle;else if(body.includes(t))score+=weights.expandedBody}
  if(terms.length&&hit===terms.length)score+=weights.allTerms;
  if(title.includes(query.toLowerCase()))score+=weights.exactPhrase;
  if(intent.some(x=>x.boost.includes(record.id)))score+=weights.intentBoost;
  return {record,score};
 }).filter(x=>x.score>=weights.minimum);
 return matches.sort((a,b)=>b.score-a.score||a.record.title.localeCompare(b.record.title));
}
export function hybridSearch(records:RecordItem[],query:string,semantic:Map<string,number>|null){
 const lexical=lexicalSearch(records,query);if(!semantic||!query.trim())return lexical;
 const map=new Map(lexical.map(x=>[x.record.id,x]));
 for(const record of records){const sim=semantic.get(record.id)||0;
  if(sim>=weights.semanticThreshold){const old=map.get(record.id);map.set(record.id,{record,score:(old?.score||0)+(sim-weights.semanticOffset)*weights.semanticWeight})}
 }
 return [...map.values()].sort((a,b)=>b.score-a.score||a.record.title.localeCompare(b.record.title));
}
