import {pipeline,env} from '@huggingface/transformers';
import wasmUrl from '../node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.asyncify.wasm?url';
import runtimeUrl from '../node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.asyncify.mjs?url';
env.allowRemoteModels=false;
env.allowLocalModels=true;
env.localModelPath='/models/';
env.backends.onnx.wasm!.numThreads=1;
env.backends.onnx.wasm!.wasmPaths={wasm:new URL(wasmUrl,self.location.origin).href,mjs:new URL(runtimeUrl,self.location.origin).href};
let setup:Promise<any>|undefined;
function initialize(){return setup ||= Promise.all([
 pipeline('feature-extraction','all-MiniLM-L6-v2',{dtype:'q8',device:'wasm'}),
 fetch('/data/vector-index.json').then(r=>{if(!r.ok)throw Error('Index unavailable');return r.json()}),
 fetch('/data/vectors.bin').then(r=>{if(!r.ok)throw Error('Vectors unavailable');return r.arrayBuffer()}).then(x=>new Float32Array(x))
]);}
let latest=0;
self.onmessage=async({data}:{data:{query:string;id:number}})=>{
 latest=data.id;
 try{
  const [extract,index,vectors]=await initialize();if(latest!==data.id)return;
  const result=await extract(data.query,{pooling:'mean',normalize:true});if(latest!==data.id)return;
  const query=result.data;const scores=new Map<string,number>();
  for(let i=0;i<index.ids.length;i++){let dot=0;for(let j=0;j<384;j++)dot+=query[j]*vectors[i*384+j];const id=index.ids[i];if(dot>(scores.get(id)||0))scores.set(id,dot)}
  self.postMessage({id:data.id,scores:[...scores]});
 }catch(error){console.warn('Local semantic search could not initialize:',String(error));self.postMessage({id:data.id,error:String(error)});setup=undefined}
};
