import {createContext,useContext,useEffect,useMemo,useRef,useState,type FormEvent,type ReactNode} from 'react';
import {Link,useLocation,useParams,useSearchParams} from 'react-router-dom';
import {ArrowLeft,ArrowRight,ArrowUp,ArrowUpRight,BookOpen,Download,Leaf,Scale,Users,MessageCircle} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import SegmentedControl from './components/arc/segmented-control/segmented-control';
import {researchApi as api} from './research-api';
import {citedLibraryParagraphs,researchDomain,researchDomains,researchReturnPath,researchSourceNotes,supportsResearchDomain,type ResearchDomain,type ResearchEvidence as Evidence,type ResearchAnswer as Answer,type ResearchStatus as Status} from './research-model';
import {researchCommunityMatches} from './research-community';
import {reviewPolytechnicSnapshot} from './polytechnic-directory';
import {words,type CRMSnapshot} from './crm-model';
import {splitCodePointRange} from './text-range';
import './research.css';
import {useStarredIds} from './CurationProvider';
import {prioritizeStarred} from './curation';

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
 return <article className="research-source"><div className="research-source-meta">{number&&<span>Source {number}</span>}<span>{source.label}</span><span>{source.format==='pdf'?'PDF':source.format==='html'?'Webpage':source.format.toUpperCase()}</span>{source.publisher_class==='actforgoa_authored_guide'&&<span>Authored draft guide</span>}</div>
  <h3><Link to={source.reader_url} state={{researchReturn:returnTo}}>{source.title}<ArrowUpRight size={17}/></Link></h3>
  <p className="source-excerpt">{source.text.slice(0,310)}{source.text.length>310?'…':''}</p>
  {source.warning&&<p className="extraction-note">{source.warning}</p>}
  {researchSourceNotes(source).map(note=><p key={note.label} className="extraction-note"><strong>{note.label}:</strong> {note.text}</p>)}
  <details><summary>Read the cited passage</summary><p className="evidence-text">{source.text}</p><a href={source.url} target="_blank" rel="noreferrer">Publisher’s source <ArrowUpRight size={14}/></a><p className="research-small">Saved {date(source.retrieved_at)}. This is the retrieval date.</p></details>
  <Link className="text-link" to={source.reader_url} state={{researchReturn:returnTo}}>Open full document <BookOpen size={16}/></Link>
 </article>
}
function AnswerSections({answer,returnTo}:{answer:Answer;returnTo:string}){
 const paragraphs=citedLibraryParagraphs(answer);
 const outside=answer.outside_context?.provenance==='model_knowledge'?answer.outside_context:null;
 return <div className="research-answer">
  <section className="research-answer-section" aria-label="From our library"><h3><BookOpen size={18}/>From our library</h3>
   {paragraphs.length?paragraphs.map((paragraph,index)=><p className="answer-paragraph" key={index}>{paragraph.text}{paragraph.citations.map(id=>{const n=answer.citations.findIndex(c=>c.id===id);const cite=answer.citations[n];return <Link className="citation-link" key={id} to={cite.reader_url} state={{researchReturn:returnTo}} aria-label={`Source ${n+1}: ${cite.title}, ${cite.label}`}>[{n+1}]</Link>;})}</p>):<p className="answer-paragraph">We did not find enough evidence in this collection to answer your question.</p>}
   {(answer.library_notice||answer.notice)&&<p className="research-small">{answer.library_notice||answer.notice}</p>}
  </section>
  {outside?.text&&<section className="research-answer-section research-outside" aria-label="Outside our library"><h3>Outside our library</h3><p className="research-provenance">AI general knowledge · not checked against external sources</p><p className="answer-paragraph">{outside.text}</p></section>}
 </div>;
}
function CommunitySuggestions({data,question,loading,error}:{data:CRMSnapshot|null;question:string;loading:boolean;error:boolean}){
 const starredIds=useStarredIds();
 const matches=useMemo(()=>prioritizeStarred(researchCommunityMatches(data?.records||[],question,6),starredIds,match=>match.record.record_id).slice(0,3),[data,question,starredIds]);
 return <section className="research-community" aria-label="Relevant community and government"><h3><Users size={18}/>People and organisations to explore</h3>
  <p className="research-small">Public registry matches, not endorsements. Check current roles and availability.</p>
  {loading?<p role="status" className="research-small">Finding related community records…</p>:error?<p className="research-small">Community matches could not load. <Link to="/directory">Open the directory</Link>.</p>:!matches.length?<p className="research-small">No close registry match for this question. <Link to="/directory">Browse the community directory</Link>.</p>:<ul>{matches.map(({record,reason,activity,verification,source})=><li key={record.record_id}>
   <div className="community-match-meta">{record.collection==='government'?'Government':words(record.record_type)}</div>
   <h4><Link to={'/directory/'+encodeURIComponent(record.record_id)}>{record.name}<ArrowUpRight size={15}/></Link></h4>
   <p>{reason}</p><p className="research-small">{activity} · {verification}</p>
   <a href={source} className="research-small" target="_blank" rel="noreferrer">Registry source<ArrowUpRight size={13}/></a>
  </li>)}</ul>}
 </section>;
}
export function Research({domain:providedDomain}:{domain?:ResearchDomain}={}){
 const location=useLocation();const memory=useContext(ResearchMemory);
 useEffect(()=>{const draft=(location.state as {draftQuestion?:string}|null)?.draftQuestion;if(draft?.trim())memory?.update(researchDomains[providedDomain||researchDomain(location.pathname)].path,{question:draft});},[location.key]);
 const domain=providedDomain||researchDomain(location.pathname);
 const [params]=useSearchParams();const docId=params.get('document')||undefined;const sourceGeneration=params.get('generation')||undefined;
 const query=docId?'?'+new URLSearchParams({document:docId,...(sourceGeneration?{generation:sourceGeneration}:{})}):'';
 const scope=researchDomains[domain].path+query;
 return <ResearchConversation key={scope} scope={scope} domain={domain} docId={docId} sourceGeneration={sourceGeneration}/>;
}
function ResearchConversation({scope,domain,docId,sourceGeneration}:{scope:string;domain:ResearchDomain;docId?:string;sourceGeneration?:string}){
 const memory=useContext(ResearchMemory);if(!memory)throw Error('Research memory provider is required.');
 const {question,turns,mode}=memory.sessions[scope]||emptySession;const returnTo=scope;const content=researchDomains[domain];
 const setQuestion=(question:string)=>memory.update(scope,{question});
 const setMode=(mode:'search'|'ask')=>memory.update(scope,{mode});
 const setTurns=(change:(turns:Turn[])=>Turn[])=>memory.update(scope,previous=>({turns:change(previous.turns)}));
 const [status,setStatus]=useState<Status|null>(null);const [statusError,setStatusError]=useState('');const [statusAttempt,setStatusAttempt]=useState(0);
 const [busy,setBusy]=useState(false);const request=useRef<AbortController|null>(null);const questionInput=useRef<HTMLTextAreaElement>(null);const latestTurn=useRef<HTMLElement|null>(null);
 const [community,setCommunity]=useState<CRMSnapshot|null>(null);const [communityError,setCommunityError]=useState(false);
 const domainSupported=supportsResearchDomain(status,domain);const canAsk=domainSupported&&!!status?.chat_ready&&status.provider==='anthropic';
 useEffect(()=>{const controller=new AbortController();setStatusError('');api<Status>('/api/status',{signal:controller.signal}).then(setStatus).catch(e=>{if(e.name!=='AbortError')setStatusError('The research service could not connect. Please try again.');});return()=>controller.abort();},[statusAttempt]);
 useEffect(()=>()=>request.current?.abort(),[]);
 const hasTurns=turns.length>0;
 useEffect(()=>{if(!hasTurns)return;const controller=new AbortController();api<CRMSnapshot>('/data/crm.json',{signal:controller.signal}).then(value=>{
  if(!Array.isArray(value.records)||!Array.isArray(value.opportunities)||!value.version)throw Error('Invalid registry');
  setCommunity(reviewPolytechnicSnapshot(value));
 }).catch(e=>{if(e.name!=='AbortError')setCommunityError(true);});return()=>controller.abort();},[hasTurns]);
 useEffect(()=>{if(turns.length){latestTurn.current?.scrollIntoView({block:'start'});latestTurn.current?.focus({preventScroll:true});}},[turns.length]);
 useEffect(()=>{const input=questionInput.current;if(input){input.style.height='auto';input.style.height=`${Math.min(input.scrollHeight,180)}px`;}},[question]);
 useEffect(()=>{const previous=document.title;document.title=`${content.label} | ActForGoa`;return()=>{document.title=previous;};},[content.label]);
 async function run(value=question,requested=mode){
  const clean=value.trim();if(clean.length<2||busy||!domainSupported||(requested==='ask'&&!canAsk))return;
  const action=requested;setBusy(true);setQuestion(clean);const controller=new AbortController();request.current=controller;
  try{
   const results=await api<{results:Evidence[];domain?:ResearchDomain}>('/api/search?'+new URLSearchParams({q:clean,domain,...(docId?{document_id:docId}:{}),...(sourceGeneration?{generation:sourceGeneration}:{})}),{signal:controller.signal});
   if(domain!=='all'&&results.domain!==domain)throw Error('This section is not available on the research service yet. Use All research to explore the current collection.');
   const turn:Turn={question:clean,results:results.results,mode:action};
   if(action==='ask'){
    try{turn.answer=await api<Answer>('/api/chat',{method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json'},body:JSON.stringify({question:clean,domain,include_outside_context:true,document_id:docId,generation:sourceGeneration,history:turns.filter(t=>t.answer?.status==='answered').flatMap(t=>[{role:'user',content:t.question},{role:'assistant',content:citedLibraryParagraphs(t.answer!).map(p=>p.text).join('\n').slice(0,4000)}]).filter(message=>message.content).slice(-8)})});}
    catch(e){if((e as Error).name==='AbortError')throw e;turn.error=(e as Error).message;}
   }
   setTurns(current=>[...current,turn]);if(!turn.error)setQuestion('');
  }catch(e){if((e as Error).name!=='AbortError')setTurns(current=>[...current,{question:clean,results:[],error:(e as Error).message,mode:action}]);}
  finally{if(!controller.signal.aborted)setBusy(false);}
 }
 const submit=(event:FormEvent)=>{event.preventDefault();void run();};
 const statusText=statusError||(!status?'Connecting to the library…':!status.search_ready?'The research library is not ready yet.':!domainSupported?'This collection is not available on the research service yet.':!canAsk?'Source search is ready. AI answers are not available yet.':'Library search and AI answers are available.');
 return <main className={`research research-chat shell ${hasTurns?'has-conversation':''}`}><header className="research-heading"><Link to="/library" className="back-link"><ArrowLeft size={16}/>Reading library</Link><div className="chat-mark" aria-hidden="true"><MessageCircle size={25}/></div><h1>{content.title}</h1><p>Ask a question. Explore the answer together, grounded in our library.</p></header>
  <nav className="research-domains" aria-label="Choose a research collection">{(['legal','ecology','all'] as const).map(key=><Link key={key} to={researchDomains[key].path} aria-current={domain===key?'page':undefined}>{key==='legal'?<Scale size={18}/>:key==='ecology'?<Leaf size={18}/>:<BookOpen size={18}/>}<span>{researchDomains[key].label}</span></Link>)}</nav>
  <div className="research-layout"><div className="research-main">
   {!domainSupported&&<div className="research-message" role="status"><p>{statusText}</p>{status&&<Link className="text-link" to="/ask">Explore all available research<ArrowRight size={16}/></Link>}</div>}
   {turns.map((turn,index)=>{const sources=turn.answer?.citations.length?turn.answer.citations:turn.results;return <section className="research-turn" ref={index===turns.length-1?latestTurn:undefined} tabIndex={-1} key={index} aria-label={'Question '+(index+1)}><div className="chat-user-message"><span className="chat-sr-only">You asked</span><h2>{turn.question}</h2></div>
    {turn.error&&<p role="alert" className="research-message">{turn.error}</p>}
    {turn.answer&&<AnswerSections answer={turn.answer} returnTo={returnTo}/>}
    {sources.length?<details className="research-sources" open={turn.mode==='search'||undefined}><summary>{turn.answer?'View sources':turn.mode==='ask'?'View matching sources':'Matching sources'} <span>({sources.length})</span></summary>{sources.map((source,n)=><Source key={source.id} source={source} number={n+1} returnTo={returnTo}/>)}</details>:!turn.error&&!turn.answer&&<p>No matching passages. Try a place, an official term or a broader topic.</p>}
    <details className="chat-related"><summary><Users size={15}/>Related people and organisations</summary><CommunitySuggestions data={community} question={turn.question} loading={!community&&!communityError} error={communityError}/></details>
   </section>;})}
   <form className="research-composer chat-composer" onSubmit={submit}>
    <div className="chat-input"><Textarea label={turns.length?'Ask a follow-up':'Message ActForGoa'} ref={questionInput} id="research-question" value={question} onChange={event=>setQuestion(event.target.value)} onKeyDown={event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.nativeEvent.isComposing){event.preventDefault();void run();}}} rows={1} maxLength={2000} minLength={2} required placeholder={turns.length?'Ask a follow-up…':domain==='all'?'Ask anything about Goa…':domain==='legal'?'Ask about Goa’s legal framework…':'Ask about Goa’s ecosystems…'} disabled={busy}/></div>
    <div className="composer-actions"><fieldset className="research-mode-fieldset" disabled={busy}><SegmentedControl label="Research mode" options={[{value:'ask',label:'Answer'},{value:'search',label:'Find sources'}]} value={mode} onValueChange={value=>{if(!busy)setMode(value as 'search'|'ask');}}/></fieldset><Button className="research-submit" type="submit" aria-label={busy?'Working…':mode==='ask'?'Ask':'Find sources'} title={mode==='ask'?'Send message':'Find sources'} disabled={busy||question.trim().length<2||!domainSupported||(mode==='ask'&&!canAsk)}><ArrowUp size={21}/></Button></div>
    {busy&&<p role="status" className="chat-composer-status"><span className="chat-working-dot"/>{mode==='ask'?'Reading the library and preparing your answer…':'Finding matching passages…'}</p>}
   </form>
   <div className="chat-composer-meta"><p>{busy?'': 'Enter to send · Shift + Enter for a new line'}</p><p>Grounded in our library. Check the sources.</p></div>
   {mode==='ask'&&!canAsk&&domainSupported&&<div className="chat-availability" role="status"><p>Answers are unavailable right now. Choose “Find sources” to browse the library while we restore them.</p><Button variant="ghost" type="button" onClick={()=>setStatusAttempt(value=>value+1)}>Check availability</Button></div>}
   {!turns.length&&<div className="research-starters"><h2>Start with a question</h2>{content.starters.map(question=><Button variant="ghost" key={question} type="button" disabled={busy||!domainSupported||(mode==='ask'&&!canAsk)} onClick={()=>void run(question)}>{question}<ArrowRight size={17}/></Button>)}</div>}
  </div><details className="research-aside chat-library-info"><summary><BookOpen size={16}/>About the library and your chat</summary><div className="chat-library-body"><h2>Our library comes first.</h2><p>Answers start with evidence from this collection. Source links let you check the passage and the full document.</p><p>When the library cannot fully answer, any extra AI context appears under <strong>Outside our library</strong>. It is not verified web research.</p><p>{mode==='ask'&&canAsk?'Your question, recent chat and selected passages go to Anthropic. General knowledge, when needed, is labelled separately.':'Source search uses our library and does not send your question to an AI provider.'} Your chat stays in this tab’s memory and clears on reload.</p>
   <p className="research-service-status" role="status">{statusText}</p>{(statusError||status&&!canAsk)&&<Button variant="ghost" type="button" onClick={()=>setStatusAttempt(value=>value+1)}>Check availability</Button>}
   {status?.search_ready&&<p className="research-coverage">{domain==='all'?`${status.stats.documents?.toLocaleString()||'Available'} documents in the collection`:status.domain_counts?.[domain]!==undefined?`${status.domain_counts[domain].toLocaleString()} documents in this section`:'Coverage is limited to the indexed collection.'}<br/>Matched by meaning and keywords.</p>}
   {docId&&<p>Searching within one document. <Link to={content.path}>Search this collection</Link></p>}
   <h2>{domain==='legal'?'Check current requirements.':'Read with context.'}</h2><p>{domain==='legal'?'Legal documents and draft guides may be historical or incomplete. Confirm current rules with the responsible authority before acting.':'Sources can include older research and incomplete scans. Dates, extraction notes and original documents help you judge the evidence.'}</p>
  </div></details></div>
 </main>;
}
export function ResearchDocument(){
 const location=useLocation();const returnTo=researchReturnPath(location.state?.researchReturn);
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
  </article><aside className="research-aside"><h2>The complete source</h2><p>This reader includes every extracted page or section. Maps, images, tables and page layout are best checked in the original file.</p><Link className="text-link" to={researchDomains[researchDomain(returnTo.split('?')[0])].path+'?'+new URLSearchParams({document:doc.id,generation:doc.generation})}>Ask about this document<ArrowRight size={16}/></Link><h2>Extraction notes</h2><p>{doc.quality.ocr_pages} pages use machine OCR. {doc.quality.low_text_pages} pages have little extractable text.</p><details><summary>Document version</summary><p className="research-small">Original file checksum</p><code className="document-hash">{doc.sha256}</code><p className="research-small">Citations keep this saved version even when the index is rebuilt.</p></details></aside></div>
 </>}</main>
}
