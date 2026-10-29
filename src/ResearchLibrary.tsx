import {useEffect,useMemo,useState} from 'react';
import {Link,useSearchParams} from 'react-router-dom';
import {ArrowLeft,BookOpen} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {researchApi} from './research-api';
import {researchDomains,researchSourceNotes,type ResearchDomain,type ResearchEvidence} from './research-model';
import {browseDocuments,fullDocumentPath,publisherHost,topicsForDomain} from './research-browse';
import './research.css';

const readingCache=new Map<string,ResearchEvidence[]>();
export function ResearchLibrary(){
 const [params,setParams]=useSearchParams();
 const domain:ResearchDomain=params.get('domain')==='ecology'?'ecology':params.get('domain')==='legal'?'legal':'all';
 const topics=topicsForDomain(domain);const selected=topics.find(topic=>topic.id===params.get('topic'))||topics[0];
 const [documents,setDocuments]=useState<ResearchEvidence[]>(readingCache.get(selected.id)||[]);
 const [loading,setLoading]=useState(!readingCache.has(selected.id));const [error,setError]=useState('');
 const [filter,setFilter]=useState('');const [attempt,setAttempt]=useState(0);
 const returnTo='/research-library?'+params.toString();
 const visible=useMemo(()=>documents.filter(doc=>`${doc.title} ${doc.url}`.toLocaleLowerCase().includes(filter.trim().toLocaleLowerCase())),[documents,filter]);
 useEffect(()=>{const previous=document.title;document.title='Browse the research library | ActForGoa';return()=>{document.title=previous;};},[]);
 useEffect(()=>{
  const cached=readingCache.get(selected.id);setFilter('');setError('');
  if(cached){setDocuments(cached);setLoading(false);return;}
  const controller=new AbortController();setLoading(true);setDocuments([]);
  researchApi<{results:ResearchEvidence[];domain?:ResearchDomain}>('/api/search?'+new URLSearchParams({q:selected.query,domain:selected.domain,limit:'20'}),{signal:controller.signal})
   .then(result=>{if(result.domain!==selected.domain)throw Error('This collection is not available yet. Try another collection.');const docs=browseDocuments(result.results);readingCache.set(selected.id,docs);setDocuments(docs);})
   .catch(cause=>{if(cause.name!=='AbortError')setError(cause.message);})
   .finally(()=>{if(!controller.signal.aborted)setLoading(false);});
  return()=>controller.abort();
 },[selected.id,attempt]);
 function selectDomain(value:ResearchDomain){setParams({domain:value});}
 return <main className="research-library shell">
  <Link to={researchDomains[domain].path} className="back-link"><ArrowLeft size={16}/>Ask a question</Link>
  <header><h1>Browse the research library</h1><p>Explore a selection by topic. Open any title to read the complete saved document, page by page.</p></header>
  <nav className="reading-collections" aria-label="Library collection">{(['all','ecology','legal'] as const).map(value=><Button key={value} size="sm" variant={domain===value?'primary':'secondary'} onClick={()=>selectDomain(value)} aria-pressed={domain===value} aria-label={researchDomains[value].label}><span className="domain-full-label">{researchDomains[value].label}</span><span className="domain-short-label" aria-hidden="true">{value==='legal'?'Legal':value==='ecology'?'Environment':'All research'}</span></Button>)}</nav>
  <div className="reading-browser"><nav className="reading-topics" aria-label="Reading topics"><h2>Browse by topic</h2>{topics.map(topic=><Button key={topic.id} variant={selected.id===topic.id?'secondary':'ghost'} size="sm" aria-pressed={selected.id===topic.id} onClick={()=>setParams({domain,topic:topic.id})}>{topic.label}</Button>)}</nav>
   <section className="reading-results" aria-labelledby="reading-topic-title"><div className="reading-results-heading"><h2 id="reading-topic-title">{selected.label}</h2>{!loading&&!error&&<p>{documents.length} documents to explore</p>}</div>
    {loading?<p role="status" className="reading-loading">Opening this shelf…</p>:error?<div className="research-message" role="alert"><p>{error}</p><Button variant="secondary" onClick={()=>setAttempt(value=>value+1)}>Try again</Button></div>:<>
     {!!documents.length&&<Input className="reading-filter" label="Filter these titles" type="search" value={filter} onChange={event=>setFilter(event.target.value)} placeholder="Find a title or publisher"/>}
     <div className="reading-document-list">{visible.map(doc=><article key={doc.document_id}><div className="reading-document-meta"><span>{doc.format==='pdf'?'PDF':'Document'}</span><span>{publisherHost(doc.url)}</span></div><h3><Link to={fullDocumentPath(doc)} state={{researchReturn:returnTo}}>{doc.title}</Link></h3><p>{doc.text.slice(0,220)}{doc.text.length>220?'…':''}</p>{researchSourceNotes(doc).length>0&&<details className="reading-source-notes"><summary>Source notes</summary>{researchSourceNotes(doc).map(note=><p className="research-small" key={note.label}><strong>{note.label}:</strong> {note.text}</p>)}</details>}<Link className="text-link" to={fullDocumentPath(doc)} state={{researchReturn:returnTo}}><BookOpen size={16}/>Read full document</Link></article>)}</div>
     {!visible.length&&<p className="reading-empty">{documents.length?'No titles match that filter. Try a shorter word.':'No documents could be found on this shelf. Choose another topic.'}</p>}
    </>}
   </section>
  </div>
  <p className="reading-note">These shelves show a topic-based selection from our indexed collection. <Link to={researchDomains[domain].path}>Search the complete collection</Link> for a specific question, or <Link to="/library">browse ActForGoa articles and guides</Link>.</p>
 </main>;
}
export default ResearchLibrary;
