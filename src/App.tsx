import {useEffect,useMemo,useRef,useState,type FormEvent} from 'react';
import {Link,NavLink,Route,Routes,useLocation,useNavigate,useParams,useSearchParams} from 'react-router-dom';
import {ArrowRight,ArrowUpRight,Search,Leaf,Recycle,Waves,Users,Heart,Landmark,Sprout,Route as RouteIcon,BookOpen,Phone,Mail,MapPin,ExternalLink,ArrowLeft,LayoutGrid,List,Check,Menu,X,FileText,SlidersHorizontal,Download} from 'lucide-react';
import type {RecordItem,Kind} from './types';
import {TOPICS,kindLabel} from './types';
import {hybridSearch} from './search';
import {Research,ResearchDocument,ResearchMemoryProvider} from './Research';
const topicIcons=[Recycle,Leaf,Waves,Users,Sprout,Landmark,RouteIcon,Heart];
const starts=['Snake rescue','Waste & recycling','Composting at home','Get involved'];
const recordPath=(r:RecordItem)=>'/read/'+r.id;
const formatDate=(s:string)=>{const d=new Date(s);return Number.isNaN(d.getTime())?s:d.toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'})};

function SearchBox({initial='',large=false}:{initial?:string;large?:boolean}){
 const [value,setValue]=useState(initial);const navigate=useNavigate();
 useEffect(()=>setValue(initial),[initial]);
 function submit(e:FormEvent){e.preventDefault();navigate('/search?q='+encodeURIComponent(value.trim()))}
 return <form className={'search-box '+(large?'large':'')} role="search" onSubmit={submit}>
  <Search size={23} aria-hidden="true"/><label className="sr-only" htmlFor={large?'home-search':'guide-search'}>Search ActForGoa</label>
  <input id={large?'home-search':'guide-search'} value={value} onChange={e=>setValue(e.target.value)} placeholder="What would you like help with?" autoComplete="off" type="search"/>
  <button type="submit" aria-label="Search the field guide"><span>Search</span><ArrowRight size={20}/></button>
 </form>
}
function Header(){
 const [open,setOpen]=useState(false);const location=useLocation();useEffect(()=>setOpen(false),[location.pathname,location.search]);
 return <header className="site-header"><div className="header-inner">
  <Link to="/" className="wordmark" aria-label="ActForGoa home">act<span>for</span>goa<span className="brand-dot">.</span></Link>
  <button className="menu-toggle icon-button" onClick={()=>setOpen(!open)} aria-expanded={open} aria-controls="main-nav" aria-label={open?'Close navigation':'Open navigation'}>{open?<X/>:<Menu/>}</button>
  <nav id="main-nav" className={open?'open':''} aria-label="Main navigation">
   <NavLink to="/" end>Explore</NavLink><NavLink to="/directory">Directory</NavLink><NavLink to="/library">Reading library</NavLink><NavLink to="/ask">Ask Goa</NavLink><NavLink to="/about">About us</NavLink>
   <Link className="nav-action" to="/get-involved">Get involved <ArrowUpRight size={17}/></Link>
  </nav>
 </div></header>
}
function Footer(){return <footer className="footer"><div className="footer-top"><div><Link to="/" className="wordmark">act<span>for</span>goa.</Link><p>Enabling people to care for Goa.</p></div><p>A platform belonging to everyone who loves Goa.<br/>Built on the collective work of people who care.</p><Link to="/contact">Let’s stay connected <ArrowUpRight size={18}/></Link></div><div className="footer-bottom"><span>Kokum Trust is the legal managing entity for Act for Goa.</span><div><a href="https://actforgoa.org/privacy-policy/">Privacy</a><a href="https://actforgoa.org/terms-and-conditions/">Terms</a><Link to="/about#sources">About this guide</Link></div></div></footer>}

function RecordCard({record:r,list=false,showImage=true}:{record:RecordItem;list?:boolean;showImage?:boolean}){
 const primaryPhone=r.phones.find(p=>p.href)||r.phones[0];
 const Icon=(r.kind==='organisation'||r.kind==='contact')?Users:r.kind==='resource'?BookOpen:r.kind==='story'?Leaf:FileText;
 return <article className={'record-card '+(list?'list-card':'')}>
  {showImage&&!list&&r.image&&<Link to={recordPath(r)} tabIndex={-1} aria-hidden="true" className="card-image"><img src={r.image} alt="" loading="lazy"/></Link>}
  <div className="card-content"><div className="record-meta"><span><Icon size={15}/>{kindLabel[r.kind]}</span>{r.locality&&<span>{r.locality}</span>}</div>
  <h3><Link to={recordPath(r)}>{r.title}<ArrowUpRight size={19}/></Link></h3>
  <p>{r.id==='resource-590480849c'?'A locality-by-locality list of snake rescue volunteers, published in 2018. Contact details need current confirmation.':r.summary}</p><div className="card-bottom"><span>{r.topics[0]}</span><Link to={recordPath(r)} aria-label={'Read '+r.title}><ArrowRight size={19}/></Link></div>
  {(r.kind==='organisation'||r.kind==='contact')&&r.phones.length>0&&<div className="quick-contact">{primaryPhone.href?<a href={primaryPhone.href}><Phone size={14}/>{primaryPhone.display}</a>:<span>{primaryPhone.display}</span>}<small>{r.kind==='contact'?'Source list: 2018 · please confirm details':'Listed contact · please confirm details'}</small></div>}
  </div>
 </article>
}
function Home({records}:{records:RecordItem[]}){
 const featured=['resource-590480849c','resource-5731eea370','resource-34bc1772ee'].map(id=>records.find(r=>r.id===id)).filter(Boolean) as RecordItem[];
 const story=records.find(r=>r.id==='wp-9352');
 return <main>
  <section className="hero shell"><div className="hero-copy"><h1>Enabling people<br/>to care for Goa.</h1><p>Good people. Local knowledge. Practical ways to help.<br className="desktop-break"/> Find your next step, right here.</p><SearchBox large/><div className="starter-queries"><span>Start here</span>{starts.map((x,i)=><Link key={x} to={i===3?'/get-involved':'/search?q='+encodeURIComponent(x)}>{x}<ArrowUpRight size={13}/></Link>)}</div></div><div className="hero-photo"><img src="/assets/goa-river.webp" alt="Palms reflected in a quiet Goan waterway" fetchPriority="high"/><span>For the Goa we love.</span></div></section>
  <section className="topics-section shell"><div className="section-heading"><h2>What do you care about?</h2><span>There’s a place to start.</span></div><div className="topic-index">{TOPICS.map((topic,i)=>{const Icon=topicIcons[i];return <Link key={topic} to={'/search?topic='+encodeURIComponent(topic)}><Icon size={23}/><span>{topic}</span><ArrowUpRight size={17}/></Link>})}</div></section>
  <section className="shell useful-section"><div className="section-heading"><div><h2>A little knowledge goes a long way.</h2><p>Useful guides for everyday life in Goa.</p></div><Link className="text-link" to="/library">Explore the library <ArrowRight size={17}/></Link></div><div className="card-grid">{featured.map(record=><RecordCard key={record.id} record={record} showImage={false}/>)}</div></section>
  {story&&<section className="spotlight shell"><Link to={recordPath(story)} className="spotlight-image"><img src={story.image||'/assets/candolim-cleanup.webp'} alt="Community participants at the Great Candolim Clean Up" loading="lazy"/></Link><div className="spotlight-copy"><h2>Small acts.<br/>A shared future.</h2><p>Meet the people showing up for Goa. Their stories are a reminder that change starts close to home.</p><Link className="text-link" to={recordPath(story)}>The Great Candolim Clean Up <ArrowUpRight size={18}/></Link><Link className="subtle-link" to="/stories">More community stories <ArrowRight size={16}/></Link></div></section>}
  <section className="join-strip shell"><div><h2>You don’t have to do it alone.</h2><p>Find the people and organisations working on what matters to you.</p></div><Link className="button green" to="/directory">Meet the community <ArrowRight size={18}/></Link></section>
 </main>
}

function Catalogue({records,mode='search'}:{records:RecordItem[];mode?:'search'|'directory'|'library'|'stories'}){
 const [params,setParams]=useSearchParams();const query=params.get('q')||'';const topic=params.get('topic')||'';const filter=params.get('type')||'all';
 const [view,setView]=useState<'grid'|'list'>(mode==='search'?'list':'grid');const [limit,setLimit]=useState(24);
 const [semantic,setSemantic]=useState<Map<string,number>|null>(null);const [status,setStatus]=useState<'idle'|'loading'|'ready'|'fallback'>('idle');
 const worker=useRef<Worker|null>(null);const seq=useRef(0);
 useEffect(()=>()=>worker.current?.terminate(),[]);
 useEffect(()=>{
  setLimit(24);setSemantic(null);const id=++seq.current;
  if(!query.trim()){setStatus('idle');return}
  setStatus('loading');
  const timer=setTimeout(()=>{
   try{worker.current ||= new Worker(new URL('./semantic.worker.ts',import.meta.url),{type:'module'});
    worker.current.onmessage=({data})=>{if(data.id!==seq.current)return;if(data.error){console.warn('Local search:',data.error);setStatus('fallback');return}setSemantic(new Map(data.scores));setStatus('ready')};
    worker.current.onerror=()=>setStatus('fallback');worker.current.postMessage({query,id});
   }catch{setStatus('fallback')}
  },250);return()=>clearTimeout(timer);
 },[query]);
 useEffect(()=>setLimit(24),[topic,filter,mode]);
 const base=useMemo(()=>records.filter(r=>mode==='directory'?(r.kind==='organisation'||r.kind==='contact'):mode==='library'?r.kind==='resource':mode==='stories'?r.kind==='story':true),[records,mode]);
 const ranked=useMemo(()=>hybridSearch(base,query,semantic),[base,query,semantic]);
 const results=ranked.filter(({record:r})=>(!topic||r.topics.includes(topic))&&(filter==='all'||r.kind===filter||(filter==='organisation'&&r.kind==='contact')));
 const grouped=query.trim()&&mode==='search'&&filter==='all';
 const groups=[
  {title:'People & organisations',kinds:['organisation','contact']},
  {title:'Guides & reading',kinds:['resource']},
  {title:'Stories & projects',kinds:['story']},
  {title:'About & action',kinds:['page']},
 ].map(group=>({...group,items:results.filter(({record})=>group.kinds.includes(record.kind))})).filter(group=>group.items.length).sort((a,b)=>results.indexOf(a.items[0])-results.indexOf(b.items[0]));
 const perGroup=Math.max(6,Math.floor(limit/4));
 const moreAvailable=grouped?groups.some(group=>group.items.length>perGroup):limit<results.length;
 const [title,description]=mode==='directory'?['People who care.','Find organisations, local initiatives, and people working for a better Goa.']:mode==='library'?['A library for everyday action.','Practical guides, civic information, and ideas worth putting into practice.']:mode==='stories'?['Good things start with people.','Stories of local action, shared effort, and a Goa worth caring for.']:['Find your next step.','Local people, practical resources, and community knowledge, all in one place.'];
 const change=(key:string,value:string)=>{const next=new URLSearchParams(params);value?next.set(key,value):next.delete(key);setParams(next)};
 return <main className="catalogue shell"><div className="catalogue-heading"><h1>{title}</h1><p>{description}</p>{mode==='library'&&<Link className="library-research-link" to="/ask">Explore Goa’s ecological research <ArrowRight size={17}/></Link>}</div><SearchBox initial={query}/>
  <div className="catalogue-layout"><aside className="filter-rail"><h2><SlidersHorizontal size={17}/>Explore by topic</h2><button className={!topic?'selected':''} onClick={()=>change('topic','')}>All topics <span>{base.length}</span></button>{TOPICS.map((t,i)=>{const Icon=topicIcons[i];return <button className={topic===t?'selected':''} key={t} onClick={()=>change('topic',t)}><Icon size={17}/>{t}</button>})}<p>Collected from ActForGoa.<br/>Every entry links to its source.</p></aside>
  <div className="results-area">{mode==='search'&&<div className="result-tabs" aria-label="Result type">{[['all','Everything'],['organisation','People & organisations'],['resource','Guides'],['story','Stories'],['page','About & action']].map(([value,label])=><button key={value} aria-pressed={filter===value} className={filter===value?'selected':''} onClick={()=>change('type',value==='all'?'':value)}>{label}</button>)}</div>}
   <div className="results-bar"><div><h2 aria-live="polite">{results.length} {results.length===1?'result':'results'}{query&&<> for “{query}”</>}</h2>{query&&<p className="search-status" role="status">{status==='loading'?'Keyword results ready. Matching meaning on your device…':status==='ready'?'Matched by meaning and keywords.':status==='fallback'?'Keyword search is available. Meaning search could not load.':''}</p>}</div><div className="view-toggle" aria-label="Result layout"><button onClick={()=>setView('grid')} aria-pressed={view==='grid'} aria-label="Grid view"><LayoutGrid size={18}/></button><button onClick={()=>setView('list')} aria-pressed={view==='list'} aria-label="List view"><List size={20}/></button></div></div>
   {topic&&<button className="active-filter" onClick={()=>change('topic','')}>{topic}<X size={14}/><span className="sr-only">Remove topic filter</span></button>}
   {query&&/snake|cobra/i.test(query)&&<div className="source-note"><Leaf size={22}/><p><strong>Looking for snake rescue?</strong> The volunteer list and wildlife contacts below come from the original site. Confirm availability directly; these numbers have not been independently reverified.</p></div>}
   {results.length?<>{grouped?<div className="grouped-results">{groups.map(group=><section className="result-group" key={group.title} aria-label={group.title}><div className="result-group-heading"><h2>{group.title}</h2><span>{group.items.length} {group.items.length===1?'match':'matches'}</span></div><div className={view==='grid'?'results-grid':'results-list'}>{group.items.slice(0,perGroup).map(({record})=><RecordCard key={record.id} record={record} list={view==='list'}/>)}</div></section>)}</div>:<div className={view==='grid'?'results-grid':'results-list'}>{results.slice(0,limit).map(({record})=><RecordCard key={record.id} record={record} list={view==='list'}/>)}</div>}{moreAvailable&&<button className="button load-more" onClick={()=>setLimit(limit+24)}>Show more results <ArrowRight size={18}/></button>}</>:<div className="empty-state"><Search size={32}/><h3>No matches just yet.</h3><p>Try a broader phrase such as “waste”, “wildlife” or “panchayat”, or remove a filter.</p><Link className="button green" to="/search">Browse all resources <ArrowRight size={17}/></Link><Link to="/contact">Ask ActForGoa for help</Link></div>}
  </div></div>
 </main>
}

function Detail({records}:{records:RecordItem[]}){
 const {id}=useParams();const r=records.find(x=>x.id===id);const [copied,setCopied]=useState(false);
 if(!r)return <NotFound/>;
 const related=records.filter(x=>x.id!==r.id&&x.kind===r.kind&&x.topics.some(t=>r.topics.includes(t))).slice(0,3);
 const externalLinks=r.links.filter(l=>!l.url.startsWith('mailto:')&&!l.url.startsWith('tel:'));
 return <main className="detail shell"><Link className="back-link" to={(r.kind==='organisation'||r.kind==='contact')?'/directory':r.kind==='story'?'/stories':'/library'}><ArrowLeft size={16}/>Back to {(r.kind==='organisation'||r.kind==='contact')?'directory':r.kind==='story'?'stories':'library'}</Link>
  <div className="detail-layout"><article><div className="record-meta"><span>{kindLabel[r.kind]}</span><span>{r.topics[0]}</span></div><h1>{r.title}</h1><div className="detail-byline">From ActForGoa{r.publishedAt&&<> · Published {formatDate(r.publishedAt)}</>}</div>
   {r.image&&<img className="detail-image" src={r.image} alt={r.title}/>}
   {(r.phones.length>0||r.kind==='organisation')&&<div className="verification-note">This is an archived source listing. Contact details and service availability need confirmation. Retrieved 22 October 2026.</div>}
   <div className="reading-body">{r.blocks.map((b,i)=>b.type==='heading'?<h2 key={i}>{b.text}</h2>:b.type==='list'?<p className="reading-list-item" key={i}>{b.text}</p>:<p key={i}>{b.text}</p>)}</div>
   {r.documents.length>0&&<section className="document-list"><h2>Documents & downloads</h2>{r.documents.map((d,i)=><a href={d.url} key={i} target="_blank" rel="noreferrer"><FileText size={22}/><span>{d.label}{d.pages&&<small>{d.pages} pages</small>}{d.status&&d.status>=400&&<small>Original link returned {d.status}; it may be unavailable</small>}</span><Download size={18}/></a>)}</section>}
   {externalLinks.length>0&&<details className="source-links"><summary>Links from the original entry ({externalLinks.length})</summary>{externalLinks.map((l,i)=><a key={i} href={l.url} target="_blank" rel="noreferrer">{l.label}<ExternalLink size={13}/></a>)}</details>}
  </article><aside className="detail-aside">
   {(r.phones.length>0||r.emails.length>0||r.locations.length>0)&&<section><h2>Get in touch</h2>{(r.kind==='resource'?r.phones.slice(0,5):r.phones).map((p,i)=><div key={i} className="contact-line"><Phone size={17}/>{p.href?<a href={p.href}>{p.display}</a>:<span>{p.display}</span>}</div>)}{r.emails.map((e,i)=><div className="contact-line" key={i}><Mail size={17}/><a href={'mailto:'+e}>{e}</a></div>)}{r.locations.map((l,i)=><div className="contact-line" key={i}><MapPin size={17}/><span>{l}</span></div>)}<small>Published contact information, not a confirmation of current availability. See the original entry for full context.</small></section>}
   <section><h2>Keep the source close.</h2><p>Read this entry in its original context.</p><a className="text-link" href={r.source} target="_blank" rel="noreferrer">Original ActForGoa page <ArrowUpRight size={16}/></a>{r.sourceApi&&<a className="subtle-link" href={r.sourceApi} target="_blank" rel="noreferrer">Public directory record <ExternalLink size={14}/></a>}<button className="subtle-link" onClick={async()=>{try{await navigator.clipboard.writeText(window.location.href);setCopied(true)}catch{setCopied(false)}}}>{copied?<Check size={15}/>:<ExternalLink size={15}/>} {copied?'Link copied':'Copy a link to this entry'}</button></section>
   <section><h2>Know something we should?</h2><p>Help keep this knowledge useful.</p><Link className="text-link" to={'/contact?entry='+encodeURIComponent(r.title)}>Suggest a correction <ArrowRight size={16}/></Link></section>
  </aside></div>{related.length>0&&<section className="related"><div className="section-heading"><h2>Keep exploring</h2></div><div className="card-grid">{related.map(record=><RecordCard key={record.id} record={record}/>)}</div></section>}
 </main>
}
function About({records}:{records:RecordItem[]}){
 const r=records.find(r=>r.id==='wp-2059');
 return <main className="about shell"><div className="about-intro"><h1>A platform for everyone<br/>who loves Goa.</h1><p>Enabling people to care for Goa.</p></div><div className="about-layout"><div className="reading-body"><h2>Why ActForGoa exists</h2><p>ACTforGOA is a new platform to help sustainable development take root in Goa.</p><p>What future could be possible if we all worked together to keep Goa Clean and Green now and for the future?</p>{r?<><h2>In ActForGoa’s own words</h2>{r.blocks.filter(b=>b.text.length>75&&!b.text.includes('ACTforGOA is a new platform')).map((b,i)=><p key={i}>{b.text}</p>)}</>:<p><a href="https://actforgoa.org/about-2/">Read the full original About page.</a></p>}<a className="text-link" href="https://actforgoa.org/about-2/">Read the original About page <ArrowUpRight size={16}/></a></div><aside><h2>Learn. Connect. Act.</h2><Link to="/library">Find useful knowledge <ArrowRight size={17}/></Link><Link to="/directory">Meet the community <ArrowRight size={17}/></Link><Link to="/get-involved">Take your next step <ArrowRight size={17}/></Link><a href="https://actforgoa.org/about-2/annual-reports/">Annual reports <ArrowUpRight size={17}/></a><a href="https://actforgoa.org/press-coverage/">Press coverage <ArrowUpRight size={17}/></a></aside></div>
  <section id="sources" className="about-sources"><h2>About this field guide</h2><p>This preview brings together publicly available information from ActForGoa, retrieved on 22 October 2026. Original content and links have been preserved in a local archive. Some records are historical; their publication date is shown where available.</p><p>Search combines keyword matching with a language model that runs on your device. It finds relevant entries; it does not generate advice or verify contact details. No account is needed and field-guide search queries are not sent to an AI provider. The separate Ask Goa research library searches saved documents on the research service. Asking for a cited answer sends your question, recent chat and retrieved passages to OpenAI. Full documents remain available in the source reader; chat and drafts stay in this tab’s memory while you browse and clear when you reload or close it.</p><p>Contact forms prepare an email for you to review and send. The preview does not store submissions. The existing ActForGoa website remains the original source.</p></section>
 </main>
}
function Contact({involve=false}:{involve?:boolean}){
 const [params]=useSearchParams();const [prepared,setPrepared]=useState(false);const [mailUrl,setMailUrl]=useState('');
 function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();const d=new FormData(e.currentTarget);const subject=String(d.get('reason'));const message=`${d.get('message')}\n\nName: ${d.get('name')}\nReply to: ${d.get('email')}${params.get('entry')?'\nEntry: '+params.get('entry'):''}`;setMailUrl('mailto:info@actforgoa.org?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(message));setPrepared(true)}
 return <main className="contact-page shell"><div className="catalogue-heading"><h1>{involve?'A better Goa starts with us.':'Let’s keep Goa connected.'}</h1><p>{involve?'Your time, your knowledge, your little corner of Goa. It all matters.':'Share a local initiative, update an entry, or tell us what you’re looking for.'}</p></div>
  {involve&&<div className="involvement-links"><a href="https://actforgoa.org/volunteer/"><Heart size={24}/><h2>Give your time</h2><p>Explore volunteering with ActForGoa.</p><ArrowUpRight size={21}/></a><Link to="/directory"><Users size={24}/><h2>Find your people</h2><p>Connect with an organisation near you.</p><ArrowUpRight size={21}/></Link><a href="https://actforgoa.org/greenviksitgoa/"><Leaf size={24}/><h2>Shape Goa’s future</h2><p>Explore the Green Viksit Goa initiative.</p><ArrowUpRight size={21}/></a></div>}
  <div className="contact-layout"><div><h2>{involve?'Tell us how you’d like to help.':'Send a little local knowledge.'}</h2><p>This form prepares an email. You’ll review it in your email app and send it yourself.</p><form onSubmit={submit} className="contact-form" onChange={()=>setPrepared(false)}><div className="form-pair"><label>Your name<input name="name" autoComplete="name" required maxLength={100}/></label><label>Email address<input name="email" type="email" autoComplete="email" required maxLength={160}/></label></div><label>I’d like to<select name="reason" defaultValue={params.get('entry')?'Suggest a correction':involve?'Volunteer with ActForGoa':'Ask a question'}><option>Ask a question</option><option>Suggest a correction</option><option>List an organisation</option><option>Share a story or resource</option><option>Volunteer with ActForGoa</option></select></label>{params.get('entry')&&<p className="entry-reference">About: {params.get('entry')}</p>}<label>Your message<textarea name="message" rows={6} required maxLength={4000} placeholder="Tell us a little about it. Include useful links if you have them."/></label><button className="button green" type="submit">Prepare email <ArrowRight size={18}/></button>{prepared&&<div className="email-ready" role="status"><Check size={20}/><div><strong>Your email is ready to review.</strong><p>Nothing has been sent yet.</p><a href={mailUrl}>Open your email app <ArrowUpRight size={16}/></a></div></div>}</form></div><aside><h2>Prefer to get in touch directly?</h2><a href="mailto:info@actforgoa.org"><Mail size={18}/>info@actforgoa.org</a><a href="https://wa.me/918554833885"><Phone size={18}/>+91 85548 33885</a><a href="https://wa.me/919823912012"><Phone size={18}/>+91 98239 12012</a><p>1 Design Valley<br/>Alto Povorim 403521, Goa</p><small>Contact details as published on the <a href="https://actforgoa.org/contact-us/">original contact page</a>. Please confirm they are current.</small></aside></div>
 </main>
}
function NotFound(){return <main className="empty-state shell"><h1>This path is still unexplored.</h1><p>That entry isn’t in this guide. Search the collection or head back to the start.</p><Link className="button green" to="/">Explore ActForGoa <ArrowRight size={18}/></Link></main>}
function ScrollReset(){const {pathname,search,hash}=useLocation();useEffect(()=>{if(hash){document.getElementById(hash.slice(1))?.scrollIntoView()}else window.scrollTo(0,0)},[pathname,search,hash]);return null}
export default function App(){
 const pathname=useLocation().pathname;const researchRoute=pathname==='/ask'||pathname.startsWith('/documents/');
 const [records,setRecords]=useState<RecordItem[]>([]);const [error,setError]=useState(false);const [loading,setLoading]=useState(true);
 useEffect(()=>{fetch('/data/catalog.json').then(r=>{if(!r.ok)throw Error('Catalogue unavailable');return r.json()}).then(setRecords).catch(()=>setError(true)).finally(()=>setLoading(false))},[]);
 return <ResearchMemoryProvider><a href="#content" className="skip-link">Skip to content</a><Header/><ScrollReset/><div id="content">{error&&!researchRoute?<main className="empty-state shell"><h1>The field guide couldn’t load.</h1><p>Please refresh to try again, or visit the original ActForGoa website.</p><button className="button green" onClick={()=>window.location.reload()}>Try again</button><a href="https://actforgoa.org/">Visit ActForGoa</a></main>:loading&&!researchRoute?<main className="loading-state shell" role="status"><div/><div/><p>Opening your field guide…</p></main>:<Routes><Route path="/ask" element={<Research/>}/><Route path="/documents/:id" element={<ResearchDocument/>}/><Route path="/" element={<Home records={records}/>}/><Route path="/search" element={<Catalogue records={records}/>}/><Route path="/directory" element={<Catalogue key="directory" records={records} mode="directory"/>}/><Route path="/library" element={<Catalogue key="library" records={records} mode="library"/>}/><Route path="/stories" element={<Catalogue key="stories" records={records} mode="stories"/>}/><Route path="/read/:id" element={<Detail records={records}/>}/><Route path="/about" element={<About records={records}/>}/><Route path="/get-involved" element={<Contact involve/>}/><Route path="/contact" element={<Contact/>}/><Route path="*" element={<NotFound/>}/></Routes>}</div><Footer/><div className="preview-note">A new field guide, in progress. <a href="https://actforgoa.org/">Visit the original site <ArrowUpRight size={12}/></a></div></ResearchMemoryProvider>
}
