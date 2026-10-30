import {createContext,useContext,useEffect,useMemo,useRef,useState,type FormEvent,type ReactNode} from 'react';
import {Link,useLocation,useNavigate,useParams,useSearchParams} from 'react-router-dom';
import {ArrowLeft,ArrowRight,ArrowUp,ArrowUpRight,BookOpen,Download,Leaf,Scale,Users,Plus,Square} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {ButtonLink} from './components/arc/button/button-link';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import SegmentedControl from './components/arc/segmented-control/segmented-control';
import {researchApi as api} from './research-api';
import {requestResearch} from './research-request';
import {canUseCachedExample,citedLibraryParagraphs,isOfficialGuidance,researchParagraphGroups,researchDomain,researchDomains,researchReturnPath,researchSourceNotes,supportsResearchDomain,type ResearchDomain,type ResearchEvidence as Evidence,type ResearchAnswer as Answer,type ResearchStatus as Status} from './research-model';
import {researchCommunityMatches,needsBuildingAuthority,buildingAuthorityMatches} from './research-community';
import {reviewPolytechnicSnapshot} from './polytechnic-directory';
import {words,type CRMSnapshot} from './crm-model';
import {readerBlocks} from './reader-text';
import './research.css';
import LocalResearchTools from './LocalResearchTools';
const localAgent=import.meta.env.DEV&&import.meta.env.VITE_LOCAL_AGENT==='1';
import {useStarredIds} from './CurationProvider';
import {prioritizeStarred} from './curation';
import {climatePlanResearch,climatePlanResearchPath,climatePlanReaderPath,isClimatePlanResearch} from './climate-plan-research';

type Turn={id:string;question:string;answer?:Answer;results:Evidence[];error?:string;mode:'search'|'ask';pending?:'searching'|'answering';stopped?:boolean};
type Session={question:string;turns:Turn[];mode:'search'|'ask'};
const emptySession:Session={question:'',turns:[],mode:localAgent?'search':'ask'};
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
 const official=isOfficialGuidance(source);
 return <article className="research-source"><div className="research-source-meta">{number&&<span>Source {number}</span>}<span>{source.label}</span><span>{source.format==='pdf'?'PDF':source.format==='html'?'Webpage':source.format.toUpperCase()}</span>{source.publisher_class==='actforgoa_authored_guide'&&<span>Authored draft guide</span>}</div>
  <h3>{official?<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>:<Link to={source.reader_url} state={{researchReturn:returnTo}}>{source.title}</Link>}</h3>
  <p className="source-excerpt">{source.text.slice(0,310)}{source.text.length>310?'…':''}</p>
  {source.warning&&<p className="extraction-note">{source.warning}</p>}
  {researchSourceNotes(source).map(note=><p key={note.label} className="extraction-note"><strong>{note.label}:</strong> {note.label==='Legal status'?words(note.text):note.text}</p>)}
  <details><summary>{official?'Read the guidance summary':'Read the cited passage'}</summary><p className="evidence-text">{source.text}</p><a href={source.url} target="_blank" rel="noreferrer">Publisher’s source <ArrowUpRight size={14}/></a><p className="research-small">{official?`Source checked ${date(source.checked_on||source.retrieved_at)}. Publication date not stated.`:`Saved ${date(source.retrieved_at)}. This is the retrieval date.`}</p></details>
  {official?<a className="text-link" href={source.url} target="_blank" rel="noopener noreferrer">Open official guidance <ArrowUpRight size={16}/></a>:<Link className="text-link" to={source.reader_url} target="_blank" rel="noopener noreferrer" state={{researchReturn:returnTo}}>{source.format==='crm'?'Open registry record':'Open full document'} <BookOpen size={16}/></Link>}
 </article>
}
function Sources({sources,turn,returnTo}:{sources:Evidence[];turn:Turn;returnTo:string}){
 const previewCount=localAgent?2:sources.length;
 return <details className="research-sources" open={turn.mode==='search'||undefined}><summary>{turn.answer?'View sources':turn.mode==='ask'?'View matching sources':'Matching sources'} <span>({sources.length})</span></summary>
  {sources.slice(0,previewCount).map((source,n)=><Source key={source.id} source={source} number={n+1} returnTo={returnTo}/>)}
  {sources.length>previewCount&&<details className="local-more-sources"><summary>View {sources.length-previewCount} more source passages</summary>{sources.slice(previewCount).map((source,n)=><Source key={source.id} source={source} number={n+previewCount+1} returnTo={returnTo}/>)}</details>}
 </details>;
}
function AnswerSections({answer,returnTo,isClimatePlan=false}:{answer:Answer;returnTo:string;isClimatePlan?:boolean}){
 const {library:paragraphs,guidance,checkedDates}=researchParagraphGroups(answer);
 const outside=answer.outside_context?.provenance==='model_knowledge'?answer.outside_context:null;
 const libraryHeading=isClimatePlan?'SAPCC: risks and proposals':'From our library';
 function paragraphContent(paragraph:Answer['paragraphs'][number]){
  return <>{paragraph.text}{paragraph.citations.map(id=>{const n=answer.citations.findIndex(c=>c.id===id);const cite=answer.citations[n];const label=`Source ${n+1}: ${cite.title}, ${cite.label}`;return isOfficialGuidance(cite)?<a className="citation-link" key={id} href={cite.url} target="_blank" rel="noopener noreferrer" aria-label={label}>[{n+1}]</a>:<Link className="citation-link" key={id} to={cite.reader_url} target="_blank" rel="noopener noreferrer" state={{researchReturn:returnTo}} aria-label={label}>[{n+1}]</Link>;})}</>;
 }
 return <div className="research-answer">
  {(paragraphs.length>0||!guidance.length)&&<section className="research-answer-section" aria-label={libraryHeading}><h3><BookOpen size={18}/>{libraryHeading}</h3>
   {isClimatePlan&&<p className="research-small">From the 2023–2033 plan. Proposals do not establish current delivery.</p>}
   {answer.cache?.hit&&<p className="research-small">Saved example, checked {date(answer.cache.reviewed_at)}. Follow-ups are researched live.</p>}
   {paragraphs.length?paragraphs.map((paragraph,index)=>{
    const content=paragraphContent(paragraph);
    return answer.summary_first&&index===0?<ul key={index} aria-label="Key takeaway"><li className="answer-paragraph">{content}</li></ul>:<div key={index}>{answer.summary_first&&index===1&&<h4>More detail</h4>}<p className="answer-paragraph">{content}</p></div>;
   }):!answer.clarification&&<p className="answer-paragraph">The passages retrieved for this question did not provide enough evidence to answer it yet.</p>}
  </section>}
  {guidance.length>0&&<section className="research-answer-section research-official-guidance" aria-label="Official flood preparedness guidance"><h3>Official flood preparedness guidance</h3><p className="research-small">Practical steps from official sources, separate from SAPCC proposals. {checkedDates.length>0&&`Sources checked ${checkedDates.map(date).join(', ')}. `}This is general preparedness advice, not a live flood warning.</p><ul className="guidance-steps">{guidance.map((paragraph,index)=><li className="answer-paragraph" key={index}>{paragraphContent(paragraph)}</li>)}</ul><p className="research-small">Follow current local instructions. <a href="https://sachet.ndma.gov.in/" target="_blank" rel="noopener noreferrer">Check official alerts on NDMA’s Sachet portal <ArrowUpRight size={14}/></a></p></section>}
  {answer.clarification&&<p className="answer-paragraph">{answer.clarification}</p>}
  {(answer.library_notice||answer.notice)&&<p className="research-small">{answer.library_notice||answer.notice}</p>}
  {outside?.text&&<section className="research-answer-section research-outside" aria-label="Outside our library"><h3>Outside our library</h3><p className="research-provenance">AI general knowledge · not checked against external sources</p><p className="answer-paragraph">{outside.text}</p></section>}
 </div>;
}
function BuildingAuthority({data,question,loading,error}:{data:CRMSnapshot|null;question:string;loading:boolean;error:boolean}){
 const [location,setLocation]=useState('');const [submitted,setSubmitted]=useState(false);
 const matches=useMemo(()=>buildingAuthorityMatches(data?.records||[],location),[data,location]);
 if(!needsBuildingAuthority(question))return null;
 return <section className="research-community" aria-label="Find your local authority"><h3>Find the right local office</h3>
  <p>Which village or town is the structure in? I can look up the local authority in the ActForGoa directory.</p>
  <form onSubmit={event=>{event.preventDefault();setSubmitted(true);}}><Input label="Village or town" value={location} maxLength={120} required onChange={event=>{setLocation(event.target.value);setSubmitted(false);}} placeholder="For example, Panaji or Agonda"/><Button type="submit" disabled={location.trim().length<3}>Find the office</Button></form>
  {submitted&&(loading?<p role="status">Looking up the government directory…</p>:error?<p role="alert">The directory could not load. <Link to="/directory">Open the directory</Link>.</p>:matches.length?<><p>These CRM listings match the place you entered. Confirm the property's jurisdiction with the office; other approvals may also apply.</p><ul>{matches.map(({record,source,verification})=><li key={record.record_id}><h4><Link to={'/directory/'+encodeURIComponent(record.record_id)} target="_blank" rel="noopener noreferrer">{record.name}</Link></h4><p><a href={source} target="_blank" rel="noreferrer">Open government office website or listing <ArrowUpRight size={14}/></a></p><p className="research-small">{verification}</p></li>)}</ul></>:<p>I couldn't identify a local-body office for that place in our CRM. Please enter the village or town rather than just the district or taluka. <Link to={'/directory?'+new URLSearchParams({q:location,collection:'government'})}>Search government listings</Link>.</p>)}
 </section>;
}
function CommunitySuggestions({data,question,loading,error}:{data:CRMSnapshot|null;question:string;loading:boolean;error:boolean}){
 const starredIds=useStarredIds();
 const matches=useMemo(()=>prioritizeStarred(researchCommunityMatches(data?.records||[],question,6),starredIds,match=>match.record.record_id).slice(0,3),[data,question,starredIds]);
 return <section className="research-community" aria-label="Relevant community and government"><h3><Users size={18}/>People and organisations to explore</h3>
  <p className="research-small">Public registry matches, not endorsements. Check current roles and availability.</p>
  {loading?<p role="status" className="research-small">Finding related community records…</p>:error?<p className="research-small">Community matches could not load. <Link to="/directory">Open the directory</Link>.</p>:!matches.length?<p className="research-small">No close registry match for this question. <Link to="/directory">Browse the directory</Link>.</p>:<ul>{matches.map(({record,reason,activity,verification,source})=><li key={record.record_id}>
   <div className="community-match-meta">{record.collection==='government'?'Government':words(record.record_type)}</div>
   <h4><Link to={'/directory/'+encodeURIComponent(record.record_id)}>{record.name}</Link></h4>
   <p>{reason}</p><p className="research-small">{activity} · {verification}</p>
   <a href={source} className="research-small" target="_blank" rel="noreferrer">Registry source</a>
  </li>)}</ul>}
 </section>;
}
export function Research({domain:providedDomain}:{domain?:ResearchDomain}={}){
 const location=useLocation();const navigate=useNavigate();const memory=useContext(ResearchMemory);
 const domain=providedDomain||researchDomain(location.pathname);
 const [params]=useSearchParams();const docId=params.get('document')||undefined;const sourceGeneration=params.get('generation')||undefined;
 const query=docId?'?'+new URLSearchParams({document:docId,...(sourceGeneration?{generation:sourceGeneration}:{})}):'';
 const initialQuestion=!docId&&params.get('start')==='ai'?params.get('q')?.trim().slice(0,2000):undefined;
 const scope=researchDomains[domain].path+(initialQuestion?'?'+new URLSearchParams({q:initialQuestion,start:'ai'}):query);
 useEffect(()=>{
  const state=location.state as {draftQuestion?:string}|null;
  if(!state?.draftQuestion?.trim())return;
  memory?.update(scope,{question:state.draftQuestion});
  // Consume the draft once, so returning from a citation keeps an edited follow-up.
  navigate(location.pathname+location.search+location.hash,{replace:true,state:{...state,draftQuestion:undefined}});
 },[location.key,scope]);
 return <ResearchConversation key={scope} initialQuestion={initialQuestion} scope={scope} domain={domain} docId={docId} sourceGeneration={sourceGeneration}/>;
}
function ResearchConversation({scope,domain,docId,sourceGeneration,initialQuestion}:{scope:string;domain:ResearchDomain;docId?:string;sourceGeneration?:string;initialQuestion?:string}){
 const navigate=useNavigate();const transcript=useRef<HTMLDivElement>(null);const heading=useRef<HTMLElement>(null);
 const memory=useContext(ResearchMemory);if(!memory)throw Error('Research memory provider is required.');
 const {question,turns,mode}=memory.sessions[scope]||{...emptySession,question:initialQuestion||''};const returnTo=scope;const content=researchDomains[domain];
 const isClimatePlan=isClimatePlanResearch(docId,sourceGeneration);
 const setQuestion=(question:string)=>memory.update(scope,{question});
 const setMode=(mode:'search'|'ask')=>memory.update(scope,{mode});
 const setTurns=(change:(turns:Turn[])=>Turn[])=>memory.update(scope,previous=>({turns:change(previous.turns)}));
 const [status,setStatus]=useState<Status|null>(null);const [statusError,setStatusError]=useState('');const [statusAttempt,setStatusAttempt]=useState(0);
 const [busy,setBusy]=useState(false);const request=useRef<AbortController|null>(null);const questionInput=useRef<HTMLTextAreaElement>(null);const latestTurn=useRef<HTMLElement|null>(null);
 const [community,setCommunity]=useState<CRMSnapshot|null>(null);const [communityError,setCommunityError]=useState(false);
 const domainSupported=supportsResearchDomain(status,domain);const canAsk=domainSupported&&!!status?.chat_ready&&status.provider==='anthropic';
 const cachedExample=(value:string)=>canUseCachedExample(status,value,domain,docId,turns.length,sourceGeneration);
 useEffect(()=>{const controller=new AbortController();setStatusError('');api<Status>('/api/status',{signal:controller.signal}).then(setStatus).catch(e=>{if(e.name!=='AbortError')setStatusError('The research service could not connect. Please try again.');});return()=>controller.abort();},[statusAttempt]);
 useEffect(()=>()=>request.current?.abort(),[]);
 const hasTurns=turns.length>0;
 useEffect(()=>{if(!hasTurns)return;const controller=new AbortController();api<CRMSnapshot>('/data/crm.json',{signal:controller.signal}).then(value=>{
  if(!Array.isArray(value.records)||!Array.isArray(value.opportunities)||!value.version)throw Error('Invalid registry');
  setCommunity(reviewPolytechnicSnapshot(value));
 }).catch(e=>{if(e.name!=='AbortError')setCommunityError(true);});return()=>controller.abort();},[hasTurns]);
 useEffect(()=>{if(!turns.length)return;if(turns.length===1)heading.current?.closest('main')?.scrollIntoView({block:'start'});const container=transcript.current;const latest=latestTurn.current;if(container&&latest){container.scrollTop=latest.offsetTop-container.offsetTop;latest.focus({preventScroll:true});}},[turns.length]);
 useEffect(()=>{const input=questionInput.current;if(input){input.style.height='auto';input.style.height=`${Math.min(input.scrollHeight,180)}px`;}},[question]);
 useEffect(()=>{const previous=document.title;document.title=`${isClimatePlan?"Goa climate plan questions":content.label} | ActForGoa`;return()=>{document.title=previous;};},[content.label,isClimatePlan]);
 function patchTurn(id:string,change:Partial<Turn>){setTurns(current=>current.map(turn=>turn.id===id?{...turn,...change}:turn));}
 function stop(){request.current?.abort();setBusy(false);setTurns(current=>current.map(turn=>turn.pending?{...turn,pending:undefined,stopped:true}:turn));}
 function newChat(){stop();memory!.update(scope,{...emptySession});requestAnimationFrame(()=>{heading.current?.closest('main')?.scrollIntoView({block:'start'});questionInput.current?.focus({preventScroll:true});});}
 async function run(value=question,requested=mode){
  const clean=value.trim();if(clean.length<2||request.current&&!request.current.signal.aborted||!domainSupported||(requested==='ask'&&!canAsk&&!cachedExample(clean)))return;
  const id=crypto.randomUUID();const controller=new AbortController();request.current=controller;
  setBusy(true);setQuestion('');
  // Paint the submitted question before the request starts.
  setTurns(current=>[...current,{id,question:clean,results:[],mode:requested,pending:requested==='ask'?'answering':'searching'}]);
  try{
   const result=await requestResearch({question:clean,domain,include_outside_context:!isClimatePlan,document_id:docId,generation:sourceGeneration,history:turns.filter(t=>t.answer).flatMap(t=>[{role:'user',content:t.question},{role:'assistant',content:[...citedLibraryParagraphs(t.answer!).map(p=>p.text),t.answer?.clarification].filter(Boolean).join('\n').slice(0,4000)}]).filter(message=>message.content).slice(-8)},requested,controller.signal);
   patchTurn(id,{...result,pending:undefined});
  }catch(e){patchTurn(id,(e as Error).name==='AbortError'?{pending:undefined,stopped:true}:{pending:undefined,error:(e as Error).message});}
  finally{if(request.current===controller){request.current=null;setBusy(false);}}
 }
 const autoStarted=useRef(false);
 useEffect(()=>{
  if(!initialQuestion||initialQuestion.length<2||autoStarted.current||turns.length||!canAsk)return;
  autoStarted.current=true;
  void run(initialQuestion,'ask');
 },[initialQuestion,canAsk,turns.length]);
 const submit=(event:FormEvent)=>{event.preventDefault();void run();};
 const statusText=statusError||(!status?'Connecting to the library…':!status.search_ready?'The research library is not ready yet.':!domainSupported?'This collection is not available on the research service yet.':!canAsk?'Source search is ready. AI answers are not available yet.':'Library search and AI answers are available.');
 return <main className={`research research-chat shell ${hasTurns?'has-conversation':''}`}><header ref={heading} className="research-heading"><Link to={isClimatePlan?"/climate-plan":"/library"} className="back-link"><ArrowLeft size={16}/>{isClimatePlan?"Climate plan guide":"Reading library"}</Link><h1>{isClimatePlan?"Ask about Goa’s climate plan":content.title}</h1><p>{isClimatePlan?"Explore SAPCC proposals and official flood preparedness guidance, with sources for both.":"Ask a question. Explore the answer together, grounded in our library."}</p></header>
  {!isClimatePlan&&<nav className="research-domains" aria-label="Choose a research collection">{(['legal','ecology','all'] as const).map(key=><Button key={key} variant={domain===key?'primary':'secondary'} size="sm" onClick={()=>navigate(researchDomains[key].path)} aria-current={domain===key?'page':undefined} aria-label={researchDomains[key].label}>{key==='legal'?<Scale size={16}/>:key==='ecology'?<Leaf size={16}/>:<BookOpen size={16}/>}<span className="domain-full-label">{researchDomains[key].label}</span><span className="domain-short-label" aria-hidden="true">{key==='legal'?'Legal':key==='ecology'?'Environment':'All research'}</span></Button>)}</nav>}
  <div className="chat-toolbar">{hasTurns&&<Button variant="secondary" size="sm" onClick={newChat}><Plus size={16}/>New chat</Button>}<Link className="text-link" to={isClimatePlan?climatePlanReaderPath:'/research-library?domain='+domain} state={{researchReturn:returnTo}}><BookOpen size={16}/>{isClimatePlan?"Read the full plan":"Browse the library"}</Link>{isClimatePlan?<Link className="text-link" to="/ask">Explore all research<ArrowRight size={16}/></Link>:!docId&&!hasTurns&&domain!=="legal"&&<Link className="text-link" to={climatePlanResearchPath}>Ask about Goa’s climate plan<ArrowRight size={16}/></Link>}</div>
  <div className="research-layout"><div className="research-main">
   {!domainSupported&&<div className="research-message" role="status"><p>{statusText}</p>{status&&<Link className="text-link" to="/ask">Explore all available research<ArrowRight size={16}/></Link>}</div>}
   <div className="chat-transcript" ref={transcript} role="region" aria-label="Conversation" tabIndex={0}>
   {turns.map((turn,index)=>{const sources=turn.answer?.citations.length?turn.answer.citations:turn.results;return <section className="research-turn" ref={index===turns.length-1?latestTurn:undefined} tabIndex={-1} key={turn.id} aria-label={'Question '+(index+1)}><div className="chat-user-message"><span className="chat-sr-only">You asked</span><h2>{turn.question}</h2></div>
    {turn.pending&&<div className="chat-progress" role="status"><span className="chat-working-dot" aria-hidden="true"/><span>{turn.pending==='searching'?'Finding relevant sources…':'Reading the sources and writing your answer…'}</span></div>}
    {turn.stopped&&<p className="research-small">Response stopped. You can ask again when you’re ready.</p>}
    {turn.error&&<div role="alert" className="research-message"><p>{turn.error}</p><Button variant="secondary" size="sm" disabled={busy} onClick={()=>void run(turn.question,turn.mode)}>Try again</Button></div>}
    {turn.answer&&<AnswerSections answer={turn.answer} returnTo={returnTo} isClimatePlan={isClimatePlan}/>}
    {!!turn.answer?.followups?.length&&<div className="research-starters" aria-label="Suggested follow-ups">{turn.answer.followups.map(value=><Button wrap variant="secondary" size="sm" key={value} disabled={busy} onClick={()=>void run(value,'ask')}>{value}</Button>)}</div>}
    {sources.length?<details className="research-sources" open={turn.mode==='search'||undefined}><summary>{turn.answer?'View sources':turn.mode==='ask'?'View matching sources':'Matching sources'} <span>({sources.length})</span></summary>{sources.map((source,n)=><Source key={source.id} source={source} number={n+1} returnTo={returnTo}/>)}</details>:!turn.pending&&!turn.stopped&&!turn.error&&!turn.answer&&<p>No matching passages. Try a place, an official term or a broader topic.</p>}
    {!turn.pending&&<details className="chat-related"><summary><Users size={15}/>Related people and organisations</summary><CommunitySuggestions data={community} question={turn.question} loading={!community&&!communityError} error={communityError}/></details>}
   </section>;})}
   </div>
   <form className="research-composer chat-composer" onSubmit={submit}>
    <div className="chat-input"><Textarea label={turns.length?'Ask a follow-up':'Message ActForGoa'} ref={questionInput} id="research-question" value={question} onChange={event=>setQuestion(event.target.value)} onKeyDown={event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.nativeEvent.isComposing){event.preventDefault();void run();}}} rows={1} maxLength={2000} minLength={2} required placeholder={turns.length?'Ask a follow-up…':isClimatePlan?'Ask about flooding, heat or solar…':domain==='all'?'Ask anything about Goa…':domain==='legal'?'Ask about Goa’s legal framework…':'Ask about Goa’s ecosystems…'}/></div>
    <div className="composer-actions"><fieldset className="research-mode-fieldset" disabled={busy}><SegmentedControl label="Research mode" options={[{value:'ask',label:'Answer'},{value:'search',label:'Find sources'}]} value={mode} onValueChange={value=>{if(!busy)setMode(value as 'search'|'ask');}}/></fieldset>{busy?<Button className="research-submit" type="button" aria-label="Stop response" title="Stop response" onClick={stop}><Square size={16}/></Button>:<Button className="research-submit" type="submit" aria-label={mode==='ask'?'Ask':'Find sources'} title={mode==='ask'?'Send message':'Find sources'} disabled={question.trim().length<2||!domainSupported||(mode==='ask'&&!canAsk&&!cachedExample(question))}><ArrowUp size={21}/></Button>}</div>
   </form>
   <div className="chat-composer-meta"><p>{busy?'': 'Enter to send · Shift + Enter for a new line'}</p><p>{isClimatePlan?"Plan proposals and official guidance are labelled separately.":"Grounded in our library. Check the sources."}</p></div>
   {mode==='ask'&&!canAsk&&domainSupported&&(status||statusError)&&<div className="chat-availability" role="status"><p>{!docId&&domain==='all'&&!!status?.cached_examples?.length?'Live answers are unavailable right now. Saved examples still open; choose “Find sources” for other questions.':'Live answers are unavailable right now. Choose “Find sources” to browse the library.'}</p><Button variant="ghost" type="button" onClick={()=>setStatusAttempt(value=>value+1)}>Check availability</Button></div>}
   {!turns.length&&<div className="research-starters"><h2>Start with a question</h2>{(isClimatePlan?climatePlanResearch.starters:content.starters).map(question=><Button wrap variant="secondary" key={question} type="button" disabled={busy||!domainSupported||(mode==='ask'&&!canAsk&&!cachedExample(question))} onClick={()=>void run(question)}><span className="chat-starter-label">{question}{cachedExample(question)&&<span className="research-small"> — saved answer</span>}</span></Button>)}</div>}
  </div><details className="research-aside chat-library-info"><summary><BookOpen size={16}/>About the library and your chat</summary><div className="chat-library-body"><h2>Our library comes first.</h2><p>Answers start with evidence from this collection. Source links let you check the passage and the full document.</p>{isClimatePlan?<p>This conversation reads the saved SAPCC and, for flood preparedness, reviewed guidance from Goa Fire & Emergency Services and NIDM. These sources do not establish current delivery or live flood conditions. Tables and scanned pages can be difficult to extract; check the original page when an answer is incomplete.</p>:<p>The research assistant can search the collection, read full pages and look up public directory records. It asks for missing details when they matter.</p>}<p>{mode==='ask'&&canAsk?isClimatePlan?'Your question, recent chat, selected SAPCC passages and any official guidance used go to Anthropic.':'New answers send your question, recent chat and retrieved passages to Anthropic. Reviewed saved examples open without a new AI request; follow-ups are researched live.':'Source search uses our library and does not send your question to an AI provider.'} Your chat stays in this tab’s memory and clears on reload.</p>
   <p className="research-service-status" role="status">{statusText}</p>{(statusError||status&&!canAsk)&&<Button variant="ghost" type="button" onClick={()=>setStatusAttempt(value=>value+1)}>Check availability</Button>}
   {status?.search_ready&&<p className="research-coverage">{isClimatePlan?'One source: Goa SAPCC 2023–2033, 111 PDF pages.':domain==='all'?`${status.stats.documents?.toLocaleString()||'Available'} documents in the collection`:status.domain_counts?.[domain]!==undefined?`${status.domain_counts[domain].toLocaleString()} documents in this section`:'Coverage is limited to the indexed collection.'}<br/>{localAgent?"Keyword search across all extracted pages. Original semantic index preserved separately.":"Matched by meaning and keywords."}</p>}
   {docId&&<p>Searching within one document. <Link to={content.path}>Search this collection</Link></p>}
   <h2>{domain==='legal'?'Check current requirements.':'Read with context.'}</h2><p>{domain==='legal'?'Legal documents and draft guides may be historical or incomplete. Confirm current rules with the responsible authority before acting.':'Sources can include older research and incomplete scans. Dates, extraction notes and original documents help you judge the evidence.'}</p>
  </div></details></div>
  {localAgent&&<LocalResearchTools/>}
 </main>;
}
export function ResearchDocument(){
 const location=useLocation();const returnTo=researchReturnPath(location.state?.researchReturn);
 const {id}=useParams();const [params,setParams]=useSearchParams();const generation=params.get('generation')||'';const page=Math.max(1,Number(params.get('page'))||1);
 const [view,setView]=useState<'text'|'original'>('text');const [imageError,setImageError]=useState(false);
 const [doc,setDoc]=useState<Document|null>(null);const [content,setContent]=useState<Page|null>(null);const [error,setError]=useState('');const [loading,setLoading]=useState(true);const [jump,setJump]=useState(String(page));
 useEffect(()=>{const controller=new AbortController();setLoading(true);setError('');setDoc(null);setContent(null);setImageError(false);setJump(String(page));const qs=generation?'?generation='+encodeURIComponent(generation):'';
  Promise.all([api<Document>(`/api/documents/${id}${qs}`,{signal:controller.signal}),api<{pages:Page[]}>(`/api/documents/${id}/pages?`+new URLSearchParams({generation,start:String(page),limit:'1'}),{signal:controller.signal})]).then(([document,pages])=>{setDoc(document);if(!pages.pages[0])throw Error('That page is outside this document.');setContent(pages.pages[0]);}).catch(e=>{if(e.name!=='AbortError')setError(e.message);}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
  return()=>controller.abort();
 },[id,generation,page]);
 function go(value:number){if(!doc||!Number.isFinite(value))return;const next=new URLSearchParams(params);next.set('page',String(Math.max(1,Math.min(doc.page_count,Math.floor(value)))));next.delete('passage');setParams(next,{state:location.state});}
 return <main className="research-reader shell"><Link className="back-link" to={returnTo}><ArrowLeft size={16}/>{returnTo.startsWith('/research-library')?'Back to the library':location.state?.researchReturn?'Back to your research':'Research library'}</Link>{loading?<p role="status">Opening the source document…</p>:error?<div role="alert"><h1>This document could not open.</h1><p>{error}</p><Link to={returnTo}>Return to research</Link></div>:doc&&content&&<>
  <header><h1>{doc.title}</h1><p className="reader-meta">{doc.format==='pdf'?'PDF':'Document'} · {doc.page_count} {doc.format==='pdf'?'pages':'sections'} · Saved {date(doc.retrieved_at)}</p><p className="research-small">Saved date is the retrieval date, not the publication date.</p><div className="reader-actions"><ButtonLink href={doc.original_url}>{doc.format==='pdf'?'Download original PDF':'Download original'}<Download size={17}/></ButtonLink><a className="text-link" href={doc.text_url}>Download full text<Download size={16}/></a><a className="text-link" href={doc.url} target="_blank" rel="noreferrer">Publisher’s source<ArrowUpRight size={16}/></a></div></header>
  <div className="reader-body"><article><nav className="reader-pagination" aria-label="Document pages"><Button variant="secondary" disabled={page<=1} onClick={()=>go(page-1)} aria-label="Previous page"><ArrowLeft size={17}/></Button><form onSubmit={e=>{e.preventDefault();go(Number(jump));}}><Input label={doc.format==='pdf'?'Page':'Section'} id="page-number" type="number" min={1} max={doc.page_count} value={jump} onChange={e=>setJump(e.target.value)} required/><span>of {doc.page_count}</span><Button variant="ghost" className="text-link" type="submit">Go</Button></form><Button variant="secondary" disabled={page>=doc.page_count} onClick={()=>go(page+1)} aria-label="Next page"><ArrowRight size={17}/></Button></nav>
   <div className="reader-view"><h2>{content.label}</h2>{doc.format==='pdf'&&<SegmentedControl label="Document view" options={[{value:'text',label:'Read text'},{value:'original',label:'Original page'}]} value={view} onValueChange={value=>setView(value as 'text'|'original')}/>}</div>{content.warning&&view==='text'&&<p className="research-message">{content.warning}</p>}<div className="document-text">{view==='original'&&doc.format==='pdf'?(imageError?<p role="alert">This page image could not load. Download the original PDF to view it.</p>:<img className="original-page" src={`/api/documents/${doc.id}/pages/${page}/image?generation=${encodeURIComponent(doc.generation)}`} alt={`Original ${content.label} of ${doc.title}. Use Read text for the extracted text.`} onError={()=>setImageError(true)}/>):content.text?readerBlocks(content.text).map((block,index)=>block.kind==='heading'?<h3 key={index}>{block.text}</h3>:block.kind==='table'?<pre key={index}>{block.text}</pre>:<p key={index}>{block.text}</p>):'No readable text was extracted from this page. Open the original to see it.'}</div>
   <div className="reader-bottom"><Button variant="ghost" className="text-link" disabled={page<=1} onClick={()=>go(page-1)}><ArrowLeft size={16}/>Previous</Button><Button variant="ghost" className="text-link" disabled={page>=doc.page_count} onClick={()=>go(page+1)}>Next<ArrowRight size={16}/></Button></div>
  </article><aside className="research-aside"><h2>The complete source</h2><p>This reader includes every extracted page or section. Maps, images, tables and page layout are best checked in the original file.</p><Link className="text-link" to={researchDomains[researchDomain(returnTo.split('?')[0])].path+'?'+new URLSearchParams({document:doc.id,generation:doc.generation})}>Ask about this document<ArrowRight size={16}/></Link><h2>Extraction notes</h2><p>{doc.quality.ocr_pages} pages use machine OCR. {doc.quality.low_text_pages} pages have little extractable text.</p><details><summary>Document version</summary><p className="research-small">Original file checksum</p><code className="document-hash">{doc.sha256}</code><p className="research-small">Citations keep this saved version even when the index is rebuilt.</p></details></aside></div>
 </>}</main>
}
