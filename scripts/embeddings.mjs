import { pipeline, env } from '@huggingface/transformers';
import { readFileSync, writeFileSync } from 'node:fs';
env.allowRemoteModels = false;
env.localModelPath = './public/models/';
const records = JSON.parse(readFileSync('public/data/catalog.json','utf8'));
const extractor = await pipeline('feature-extraction','all-MiniLM-L6-v2',{dtype:'q8'});
const ids = [], chunks = [], vectors = [];
for(const r of records){
  const text = `${r.title}. ${r.summary}. ${r.text} ${r.documentText || ''}`;
  const words = text.split(/\s+/);
  // 160-word chunks with overlap avoid losing a useful passage in a long report.
  for(let i=0;i<Math.min(words.length,3200);i+=130){
    ids.push(r.id);
    chunks.push(`${r.title}. ${words.slice(i,i+160).join(' ')}`);
  }
}
for(let i=0;i<chunks.length;i+=12){
 const out = await extractor(chunks.slice(i,i+12),{pooling:'mean',normalize:true});
 vectors.push(...out.tolist().flat());
 if(i%120===0) console.log(`Embedded ${i}/${chunks.length} passages`);
}
const f32 = new Float32Array(vectors);
writeFileSync('public/data/vectors.bin',Buffer.from(f32.buffer));
writeFileSync('public/data/vector-index.json',JSON.stringify({model:'Xenova/all-MiniLM-L6-v2',dtype:'q8',dimensions:384,ids,chunks:chunks.length,records:records.length,maxIndexedWordsPerRecord:3200,generatedAt:new Date().toISOString()}));
console.log(`Indexed ${records.length} records / ${chunks.length} passages`);
