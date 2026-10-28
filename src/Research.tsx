import {createContext,useContext,useEffect,useRef,useState,type FormEvent,type ReactNode} from 'react';
import {Link,useLocation,useParams,useSearchParams} from 'react-router-dom';
import {ArrowLeft,ArrowRight,ArrowUpRight,BookOpen,Download} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import SegmentedControl from './components/arc/segmented-control/segmented-control';
import {researchApi as api} from './research-api';
import {splitCodePointRange} from './text-range';
import './research.css';

type Evidence={id:string;document_id:string;page:number;label:string;title:string;url:string;text:string;origin:string;warning:string;retrieved_at:string;format:string;matches:string[];reader_url:string;generation:string};
type Answer={status:string;paragraphs:{text:string;citations:string[]}[];citations:Evidence[];notice?:string};
type Status={search_ready:boolean;chat_ready:boolean;provider_label?:string;stats:{documents?:number;pages?:number;chunks?:number}};
type Turn={question:string;answer?:Answer;results:Evidence[];error?:string;mode:'search'|'ask'};
type Session={question:string;turns:Turn[];mode:'search'|'ask'};
const emptySession:Session={question:'',turns:[],mode:'ask'};
type Memory={sessions:Record<string,Session>;update:(scope:string,change:Partial<Session>|((previous:Session)=>Partial<Session>))=>void};
const ResearchMemory=createContext<Memory|null>(null);
// App-lifetime memory only: source navigation preserves work, a reload clears it.
export function ResearchMemoryProvider({children}:{children:ReactNode}){
 const [sessions,setSessions]=useState<Record<string,Session>>({});
 function update(scope:string,change:Partial<Session>|((previous:Session)=>Partial<Session>)){
  setSessions(current=>{const previous=current[scope]||emptySession;return {...current,[scope]:{...previous,...(typeof change==='function'?change(previous):change)}};});
 }
 return <ResearchMemory.Provider value={{sessions,update}}>{children}</ResearchMemory.Provider>;
}
type Document={id:string;title:string;url:string;retrieved_at:string;format:string;page_count:number;generation:string;sha256:string;quality:{low_text_pages:number;ocr_pages:number};original_url:string;text_url:string};
type Page={page:number;label:string;text:string;origin:string;warning:string};
const date=(value:string)=>value?new Date(value).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}):'Date unavailable';
function Source({source,number,returnTo}:{source:Evidence;number?:number;returnTo:string}){
 return <article className="research-source"><div className="research-source-meta">{number&&<span>Source {number}</span>}<span>{source.label}</span><span>{source.format==='pdf'?'PDF':source.format==='html'?'Webpage':source.format.toUpperCase()}</span></div>
  <h3><Link to={source.reader_url} state={{researchReturn:returnTo}}>{source.title}<ArrowUpRight size={17}/></Link></h3>
  <p className="source-excerpt">{source.text.slice(0,310)}{source.text.length>310?'…':''}</p>
  {source.warning&&<p className="extraction-note">{source.warning}</p>}
  <details><summary>Read the cited passage</summary><p className="evidence-text">{source.text}</p><a href={source.url} target="_blank" rel="noreferrer">Publisher’s source <ArrowUpRight size={14}/></a><p className="research-small">Saved {date(source.retrieved_at)}. This is the retrieval date.</p></details>
  <Link className="text-link" to={source.reader_url} state={{researchReturn:returnTo}}>Open full document <BookOpen size={16}/></Link>
 </article>
}
export function Research(){
 const [params]=useSearchParams();const docId=params.get('document')||undefined;const sourceGeneration=params.get('generation')||undefined;
 const scope=docId?'?'+new URLSearchParams({document:docId,...(sourceGeneration?{generation:sourceGeneration}:{})}):'';
 return <ResearchConversation key={scope} scope={scope} docId={docId} sourceGeneration={sourceGeneration}/>;
}
function ResearchConversation({scope,docId,sourceGeneration}:{scope:string;docId?:string;sourceGeneration?:string}){
 const memory=useContext(ResearchMemory);if(!memory)throw Error('Research memory provider is required.');
 const {question,turns,mode}=memory.sessions[scope]||emptySession;const returnTo='/ask'+scope;
 const setQuestion=(question:string)=>memory.update(scope,{question});
 const setMode=(mode:'search'|'ask')=>memory.update(scope,{mode});
 const setTurns=(change:(turns:Turn[])=>Turn[])=>memory.update(scope,previous=>({turns:change(previous.turns)}));
 const [status,setStatus]=useState<Status|null>(null);const [statusError,setStatusError]=useState('');const [busy,setBusy]=useState(false);const request=useRef<AbortController|null>(null);const questionInput=useRef<HTMLTextAreaElement>(null);const latestTurn=useRef<HTMLElement|null>(null);
 useEffect(()=>{const controller=new AbortController();api<Status>('/api/status',{signal:controller.signal}).then(setStatus).catch(e=>{if(e.name!=='AbortError')setStatusError('Research is temporarily unavailable. Please try again shortly.');});return()=>{controller.abort();request.current?.abort();};},[]);
 useEffect(()=>{if(turns.length){latestTurn.current?.scrollIntoView({block:'start'});latestTurn.current?.focus({preventScroll:true});}},[turns.length]);
 async function run(value=question,action=mode){
  const clean=value.trim();if(clean.length<2||busy)return;setBusy(true);setQuestion(clean);const controller=new AbortController();request.current=controller;
  try{
   const results=await api<{results:Evidence[]}>('/api/search?'+new URLSearchParams({q:clean,...(docId?{document_id:docId}:{}),...(sourceGeneration?{generation:sourceGeneration}:{})}),{signal:controller.signal});
   const turn:Turn={question:clean,results:results.results,mode:action};
   if(action==='ask'){
    try{turn.answer=await api<Answer>('/api/chat',{method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json'},body:JSON.stringify({question:clean,document_id:docId,generation:sourceGeneration,history:turns.filter(t=>t.answer?.status==='answered').flatMap(t=>[{role:'user',content:t.question},{role:'assistant',content:t.answer!.paragraphs.map(p=>p.text).join('\n').slice(0,4000)}]).slice(-8)})});}
    catch(e){if((e as Error).name==='AbortError')throw e;turn.error=(e as Error).message;}
   }
   setTurns(current=>[...current,turn]);if(!turn.error)setQuestion('');
  }catch(e){if((e as Error).name!=='AbortError')setTurns(current=>[...current,{question:clean,results:[],error:(e as Error).message,mode:action}]);}
  finally{if(!controller.signal.aborted){setBusy(false);}}
 }
 const submit=(e:FormEvent)=>{e.preventDefault();void run();};
 return <main className="research shell"><header className="research-heading"><Link to="/library" className="back-link"><ArrowLeft size={16}/>Reading library</Link><h1>Goa’s research library.</h1><p>Explore its rivers, landscapes and living systems. Find the evidence, ask a question, then read the whole document.</p></header>
  <div className="research-layout"><div className="research-main">
   {turns.map((turn,index)=><section className="research-turn" ref={index===turns.length-1?latestTurn:undefined} tabIndex={-1} key={index} aria-label={'Question '+(index+1)}><h2>{turn.question}</h2>
    {turn.error&&<p role="alert" className="research-message">{turn.error}</p>}
    {turn.answer?.notice&&<p role="status" className="research-message">{turn.answer.notice}</p>}
    {turn.answer?.paragraphs.map((p,i)=><p className="answer-paragraph" key={i}>{p.text}{p.citations.map(id=>{const n=turn.answer!.citations.findIndex(c=>c.id===id);const cite=turn.answer!.citations[n];return cite?<Link className="citation-link" key={id} to={cite.reader_url} state={{researchReturn:returnTo}} aria-label={`Source ${n+1}: ${cite.title}, ${cite.label}`}>[{n+1}]</Link>:null;})}</p>)}
    <h3 className="evidence-heading">{turn.answer?.status==='answered'?'Sources for this answer':turn.results.length?'Passages to explore':turn.error?'Sources unavailable':'No matching passages'}</h3>
    {!turn.results.length&&!turn.error&&<p>Try a place, species name or a broader topic such as “groundwater” or “khazan”.</p>}
    {(turn.answer?.status==='answered'?turn.answer.citations:turn.results).map((source,n)=><Source key={source.id} source={source} number={n+1} returnTo={returnTo}/>)}
   </section>)}
   <form className="research-composer" onSubmit={submit}>
    <Textarea label={turns.length?'Keep exploring':'What would you like to understand?'} ref={questionInput} id="research-question" value={question} onChange={e=>setQuestion(e.target.value)} rows={3} maxLength={2000} minLength={2} required placeholder="How do Goa’s laterite plateaus store and release water?" disabled={busy}/>
    <div className="composer-actions"><fieldset className="research-mode-fieldset" disabled={busy}><SegmentedControl label="Research mode" options={[{value:'search',label:'Find sources'},{value:'ask',label:'Ask with citations'}]} value={mode} onValueChange={value=>{if(!busy)setMode(value as 'search'|'ask');}}/></fieldset><Button className="research-submit" type="submit" disabled={busy||question.trim().length<2}>{busy?'Working…':mode==='search'?'Search':'Ask'}<ArrowRight size={17}/></Button></div>
    <p className="research-small">{mode==='ask'?`Your question, recent chat and selected passages are sent to ${status?.provider_label||'the configured AI provider'}. Your chat and draft stay in this tab while you browse sources and clear when you reload or close it. Answers without chat history may be reused from our server cache for ten minutes.`:'Source search runs on ActForGoa’s research service. It does not send your query to an AI provider.'}</p>
    {busy&&<p role="status" className="research-small">{mode==='ask'?'Finding evidence and preparing a cited answer…':'Matching meaning and keywords…'}</p>}
   </form>
   {!turns.length&&<div className="research-starters"><h2>Follow a question</h2>{['How do khazans manage fresh and salt water?','What threatens Goa’s laterite plateaus?','Which animals are endemic to Goa?'].map(q=><Button variant="ghost" key={q} type="button" disabled={busy} onClick={()=>void run(q,mode)}>{q}<ArrowRight size={17}/></Button>)}</div>}
  </div><aside className="research-aside"><h2>Keep the evidence close.</h2><p>Every passage opens at its source page. Read the full extracted text or open the saved original.</p>
   {status?.search_ready&&<p className="research-coverage">{status.stats.documents?.toLocaleString()} documents · {status.stats.pages?.toLocaleString()} pages and sections<br/>Matched by meaning and keywords.</p>}
   <p role="status">{statusError||(!status?'Connecting to the research library…':!status.search_ready?'The research index is not ready yet.':!status.chat_ready?'Source search is ready. Cited answers are not available yet.':'Cited answers are available.')}</p>
   {docId&&<p>Searching within one document. <Link to="/ask">Search the whole collection</Link></p>}
   <h2>Read with context.</h2><p>The collection includes historical documents and incomplete scans. Dates, OCR notes and the original source help you judge what each can support.</p><p>English meaning search is supported. Exact names and terms can also be found with keyword matching.</p>
  </aside></div>
 </main>
}
export function ResearchDocument(){
 const location=useLocation();const returnTo=typeof location.state?.researchReturn==='string'&&/^\/ask(?:\?|$)/.test(location.state.researchReturn)?location.state.researchReturn:'/ask';
 const {id}=useParams();const [params,setParams]=useSearchParams();const generation=params.get('generation')||'';const page=Math.max(1,Number(params.get('page'))||1);
 const [view,setView]=useState<'text'|'original'>('text');const [imageError,setImageError]=useState(false);
 const [highlight,setHighlight]=useState<{page:number;start:number;end:number}|null>(null);const passageId=params.get('passage');
 const [doc,setDoc]=useState<Document|null>(null);const [content,setContent]=useState<Page|null>(null);const [error,setError]=useState('');const [loading,setLoading]=useState(true);const [jump,setJump]=useState(String(page));
 useEffect(()=>{const controller=new AbortController();setLoading(true);setError('');setDoc(null);setContent(null);setHighlight(null);setImageError(false);setJump(String(page));const qs=generation?'?generation='+encodeURIComponent(generation):'';
  Promise.all([api<Document>(`/api/documents/${id}${qs}`,{signal:controller.signal}),api<{pages:Page[]}>(`/api/documents/${id}/pages?`+new URLSearchParams({generation,start:String(page),limit:'1'}),{signal:controller.signal})]).then(([document,pages])=>{setDoc(document);if(!pages.pages[0])throw Error('That page is outside this document.');setContent(pages.pages[0]);}).catch(e=>{if(e.name!=='AbortError')setError(e.message);}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
  if(passageId)api<{page:number;start:number;end:number}>(`/api/documents/${id}/passages/${passageId}${qs}`,{signal:controller.signal}).then(setHighlight).catch(()=>{});return()=>controller.abort();
 },[id,generation,page,passageId]);
 function go(value:number){if(!doc||!Number.isFinite(value))return;const next=new URLSearchParams(params);next.set('page',String(Math.max(1,Math.min(doc.page_count,Math.floor(value)))));next.delete('passage');setParams(next,{state:location.state});}
 const highlighted=content&&highlight?.page===page&&content.page===page?splitCodePointRange(content.text,highlight.start,highlight.end):null;
 return <main className="research-reader shell"><Link className="back-link" to={returnTo}><ArrowLeft size={16}/>{location.state?.researchReturn?'Back to your research':'Research library'}</Link>{loading?<p role="status">Opening the source document…</p>:error?<div role="alert"><h1>This document could not open.</h1><p>{error}</p><Link to={returnTo}>Return to research</Link></div>:doc&&content&&<>
  <header><h1>{doc.title}</h1><p className="reader-meta">{doc.format==='pdf'?'PDF':'Document'} · {doc.page_count} {doc.format==='pdf'?'pages':'sections'} · Saved {date(doc.retrieved_at)}</p><p className="research-small">Saved date is the retrieval date, not the publication date.</p><div className="reader-actions"><a className="button green" href={doc.original_url}>{doc.format==='pdf'?'Download original PDF':'Download original'}<Download size={17}/></a><a className="text-link" href={doc.text_url}>Download full text<Download size={16}/></a><a className="text-link" href={doc.url} target="_blank" rel="noreferrer">Publisher’s source<ArrowUpRight size={16}/></a></div></header>
  <div className="reader-body"><article><nav className="reader-pagination" aria-label="Document pages"><Button variant="secondary" disabled={page<=1} onClick={()=>go(page-1)} aria-label="Previous page"><ArrowLeft size={17}/></Button><form onSubmit={e=>{e.preventDefault();go(Number(jump));}}><Input label={doc.format==='pdf'?'Page':'Section'} id="page-number" type="number" min={1} max={doc.page_count} value={jump} onChange={e=>setJump(e.target.value)} required/><span>of {doc.page_count}</span><Button variant="ghost" className="text-link" type="submit">Go</Button></form><Button variant="secondary" disabled={page>=doc.page_count} onClick={()=>go(page+1)} aria-label="Next page"><ArrowRight size={17}/></Button></nav>
   <div className="reader-view"><h2>{content.label}</h2>{doc.format==='pdf'&&<SegmentedControl label="Document view" options={[{value:'text',label:'Read text'},{value:'original',label:'Original page'}]} value={view} onValueChange={value=>setView(value as 'text'|'original')}/>}</div>{content.warning&&view==='text'&&<p className="research-message">{content.warning}</p>}<div className="document-text">{view==='original'&&doc.format==='pdf'?(imageError?<p role="alert">This page image could not load. Download the original PDF to view it.</p>:<img className="original-page" src={`/api/documents/${doc.id}/pages/${page}/image?generation=${encodeURIComponent(doc.generation)}`} alt={`Original ${content.label} of ${doc.title}. Use Read text for the extracted text.`} onError={()=>setImageError(true)}/>):highlighted?<>{highlighted.before}<mark>{highlighted.selected}</mark>{highlighted.after}</>:content.text||'No readable text was extracted from this page. Open the original to see it.'}</div>
   <div className="reader-bottom"><Button variant="ghost" className="text-link" disabled={page<=1} onClick={()=>go(page-1)}><ArrowLeft size={16}/>Previous</Button><Button variant="ghost" className="text-link" disabled={page>=doc.page_count} onClick={()=>go(page+1)}>Next<ArrowRight size={16}/></Button></div>
  </article><aside className="research-aside"><h2>The complete source</h2><p>This reader includes every extracted page or section. Maps, images, tables and page layout are best checked in the original file.</p><Link className="text-link" to={'/ask?'+new URLSearchParams({document:doc.id,generation:doc.generation})}>Ask about this document<ArrowRight size={16}/></Link><h2>Extraction notes</h2><p>{doc.quality.ocr_pages} pages use machine OCR. {doc.quality.low_text_pages} pages have little extractable text.</p><details><summary>Document version</summary><p className="research-small">Original file checksum</p><code className="document-hash">{doc.sha256}</code><p className="research-small">Citations keep this saved version even when the index is rebuilt.</p></details></aside></div>
 </>}</main>
}
