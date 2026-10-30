import {researchApi} from './research-api';
import type {ResearchAnswer,ResearchDomain,ResearchEvidence} from './research-model';
export type ResearchInput={question:string;domain:ResearchDomain;document_id?:string;generation?:string;include_outside_context:boolean;history:{role:string;content:string}[]};
/** Answers already retrieve their evidence. Never serialize another search first. */
export async function requestResearch(input:ResearchInput,mode:'ask'|'search',signal:AbortSignal,request=researchApi):Promise<{results:ResearchEvidence[];answer?:ResearchAnswer}>{
 if(mode==='ask'){
  const answer=await request<ResearchAnswer>('/api/chat',{method:'POST',signal,headers:{'Content-Type':'application/json'},body:JSON.stringify(input)});
  return {results:answer.citations,answer};
 }
 const result=await request<{results:ResearchEvidence[];domain?:ResearchDomain}>('/api/search?'+new URLSearchParams({q:input.question,domain:input.domain,...(input.document_id?{document_id:input.document_id}:{}),...(input.generation?{generation:input.generation}:{})}),{signal});
 if(input.domain!=='all'&&result.domain!==input.domain)throw Error('This section is not available on the research service yet. Use All research to explore the current collection.');
 return {results:result.results};
}
