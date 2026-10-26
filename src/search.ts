import type {RecordItem} from './types';
const stop=new Set('a an the i me my we our you your to for of in on at and or is are do does can who how what where when with need get help find goa oh there theres s it its this that have has please want would could should about'.split(' '));
export const tokens=(value:string)=>value.toLowerCase().normalize('NFKD').replace(/[^a-z0-9\s]/g,' ').split(/\s+/).filter(t=>t.length>1&&!stop.has(t));
const intents=[
 {trigger:/\b(snakes?|cobras?|serpents?|reptiles?|vipers?|pythons?)\b/i,terms:['snake','rescue','wildlife'],boost:['resource-590480849c','org-27']},
 {trigger:/rubbish|garbage|trash|waste|recycl|segregat|plastic/i,terms:['waste','recycling','recycle','segregation'],boost:[]},
 {trigger:/compost|kitchen scraps|food scraps/i,terms:['composting','organic','waste'],boost:[]},
 {trigger:/volunteer|give back|lend a hand|take part/i,terms:['volunteer','participate','community'],boost:[]},
 {trigger:/cut.*tree|tree.*cut|felling/i,terms:['tree','cutting','forest'],boost:[]},
 {trigger:/gram sabha|village.*meeting|panchayat/i,terms:['panchayat','gram','sabha','citizen'],boost:[]},
 {trigger:/\b(injured|hurt|trapped|sick|rescue)\b.*\b(animals?|dogs?|cats?|cattle|cows?|birds?)\b|\b(animals?|dogs?|cats?|cattle|cows?|birds?)\b.*\b(injured|hurt|trapped|sick|rescue)\b/i,terms:['animal','rescue','veterinary','welfare'],boost:[]},
];
export function lexicalSearch(records:RecordItem[],query:string){
 const terms=tokens(query),intent=intents.filter(x=>x.trigger.test(query));
 const expanded=[...new Set(intent.flatMap(x=>x.terms).filter(t=>!terms.includes(t)))];
 if(!query.trim())return records.map(record=>({record,score:0}));
 if(!terms.length&&!expanded.length)return [];
 const matches=records.map(record=>{
  const title=record.title.toLowerCase(), body=(record.text+' '+(record.documentText||'')+' '+(record.directory?.description||'')+' '+(record.locality||'')+' '+record.locations.join(' ')+' '+(record.directory?.tags||[]).join(' ')).toLowerCase(),topic=record.topics.join(' ').toLowerCase();
  const tset=new Set(tokens(title)),bset=new Set(tokens(body));
  let score=0,hit=0;
  for(const t of terms){if(tset.has(t)||title.includes(t)){score+=8;hit++}else if(bset.has(t)){score+=2;hit++}else if(topic.includes(t)){score+=.3}}
  for(const t of expanded){if(title.includes(t))score+=3;else if(body.includes(t))score+=.7}
  if(terms.length&&hit===terms.length)score+=4;
  if(title.includes(query.toLowerCase()))score+=10;
  if(intent.some(x=>x.boost.includes(record.id)))score+=15;
  return {record,score};
 }).filter(x=>x.score>=1);
 return matches.sort((a,b)=>b.score-a.score||a.record.title.localeCompare(b.record.title));
}
export function hybridSearch(records:RecordItem[],query:string,semantic:Map<string,number>|null){
 const lexical=lexicalSearch(records,query);if(!semantic||!query.trim())return lexical;
 const map=new Map(lexical.map(x=>[x.record.id,x]));
 for(const record of records){const sim=semantic.get(record.id)||0;
  if(sim>=.39){const old=map.get(record.id);map.set(record.id,{record,score:(old?.score||0)+(sim-.3)*18})}
 }
 return [...map.values()].sort((a,b)=>b.score-a.score||a.record.title.localeCompare(b.record.title));
}
