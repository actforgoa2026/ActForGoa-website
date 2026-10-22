import {writeFileSync, readFileSync} from 'node:fs';
import {lexicalSearch} from '../../src/search.ts';
import {AutoTokenizer, pipeline, env} from '@huggingface/transformers';
env.allowRemoteModels=false; env.localModelPath=process.cwd()+'/public/models/';
const records=JSON.parse(readFileSync('public/data/catalog.json','utf8'));
const tokenizer=await AutoTokenizer.from_pretrained('all-MiniLM-L6-v2');
const embed=await pipeline('feature-extraction','all-MiniLM-L6-v2',{dtype:'q8',device:'cpu'});
const queries=['Who do I call about a snake in my lawn?','Where can I take my rubbish?','Griselda Nobay Donvaddo','zzzxqvplm','composting at home','village meeting','injured animal','volunteer','discarded household materials','Café & Goa: trees?','', 'the'];
const fixtures=[];
for(const query of queries){
 const ids=(await tokenizer(query)).input_ids.tolist()[0].map(Number);
 const vector=query ? Array.from((await embed(query,{pooling:'mean',normalize:true})).data) : [];
 fixtures.push({query,tokenIDs:ids,top:lexicalSearch(records,query).slice(0,10).map(x=>({id:x.record.id,score:x.score})),embedding:vector});
}
writeFileSync('ios/Tests/search-fixtures.json',JSON.stringify(fixtures));
console.log(`Exported ${fixtures.length} web search and MiniLM reference cases.`);
