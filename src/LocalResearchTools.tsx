import {useEffect,useState,type FormEvent} from 'react';
import {ArrowUpRight} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import SegmentedControl from './components/arc/segmented-control/segmented-control';
import {researchApi as api} from './research-api';
import './local-research.css';

type Doc={id:string;title:string;page_count:number;format:string;reader_url:string;text_url:string;original_url:string;url:string;legal_currency?:string;quality:{low_text_pages:number;ocr_pages:number}};
type RecordData={record_id:string;name:string;collection:string;summary:string;goa_location:string;verification_status:string;activity_verification_notes:string;notes:string;source_urls:string;checked_on:string};
type Results={documents?:Doc[];records?:RecordData[];total_matches:number;next_offset:number|null};
type Settings={answer_brief:string;extra_retrieval_terms:string;effort:string};
const cleanUrl=(url:string)=>/^https?:\/\//i.test(url)?url:undefined;

export default function LocalResearchTools(){
 const [tab,setTab]=useState('documents');const [query,setQuery]=useState('');const [location,setLocation]=useState('');const [collection,setCollection]=useState('all');
 const [result,setResult]=useState<Results|null>(null);const [offset,setOffset]=useState(0);const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 const [settings,setSettings]=useState<Settings|null>(null);const [saved,setSaved]=useState('');
 async function load(next=0){setBusy(true);setError('');try{
  const path=tab==='documents'?'/api/dev/catalogue?'+new URLSearchParams({q:query,offset:String(next),limit:'10'}):'/api/dev/crm/search?'+new URLSearchParams({q:query,collection,location,offset:String(next),limit:'10'});
  const data=await api<Results>(path);setResult(data);setOffset(next);
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 useEffect(()=>{setQuery('');setLocation('');setCollection('all');setResult(null);setOffset(0);setError('');if(tab==='settings')api<Settings>('/api/dev/config').then(({answer_brief,extra_retrieval_terms,effort})=>setSettings({answer_brief,extra_retrieval_terms,effort})).catch(e=>setError(e.message));else{
  const controller=new AbortController();setBusy(true);
  api<Results>(tab==='documents'?'/api/dev/catalogue?limit=10':'/api/dev/crm/search?collection=all&limit=10',{signal:controller.signal}).then(setResult).catch(e=>{if(e.name!=='AbortError')setError(e.message);}).finally(()=>{if(!controller.signal.aborted)setBusy(false);});return()=>controller.abort();
 }},[tab]);
 async function save(e:FormEvent){e.preventDefault();if(!settings)return;setBusy(true);setSaved('');setError('');try{await api('/api/dev/config',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(settings)});setSaved('Saved. Your next question uses these settings.');}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 return <section className="local-research-tools" id="local-evidence" tabIndex={-1} aria-label="Catalogue and CRM"><h2>Explore the evidence</h2><p>Browse the complete collection alongside your research. <a className="local-return-question" href="#research-question">Return to your question</a></p>
  <SegmentedControl label="Evidence workspace" value={tab} onValueChange={value=>{if(!busy)setTab(value);}} options={[{value:'documents',label:'Documents'},{value:'crm',label:'CRM'},{value:'settings',label:'Tune'}]} />
  {tab!=='settings'?<><form className="local-evidence-search" onSubmit={e=>{e.preventDefault();void load();}}>
   <Input label={tab==='documents'?'Filter document titles and topics':'Search public CRM'} value={query} onChange={e=>setQuery(e.target.value)} placeholder={tab==='documents'?'For example, water or building':'Organisation, office or activity'}/>
   {tab==='crm'&&<div className="local-crm-filters"><label>Collection<select value={collection} onChange={e=>setCollection(e.target.value)}><option value="all">All records</option><option value="community">Community</option><option value="government">Government</option></select></label><Input label="Village or town" value={location} onChange={e=>setLocation(e.target.value)} placeholder="For example, Agonda"/></div>}
   <Button type="submit" variant="secondary" disabled={busy}>{busy?'Searching…':query||location?'Search':'Browse all'}</Button>
  </form><p className="local-results-count" role="status">{busy?'Opening the collection…':result?`${result.total_matches.toLocaleString()} ${tab==='documents'?'documents':'records'} · ${result.total_matches?offset+1:0}–${offset+(result.documents||result.records||[]).length}`:''}</p>
  {tab==='crm'&&<p className="research-small">Public-source research. Confirm current contacts and exact local jurisdiction. Personal CRM notes are separate.</p>}
  {!busy&&result?.total_matches===0&&<p>No matching {tab==='documents'?'titles':'records'}. Try a broader term or clear the filters. Use “Find sources” in chat to search inside every document.</p>}
  <div aria-busy={busy}>{result?.documents?.map(doc=><article className="local-evidence-row" key={doc.id}>
   <h3><a href={doc.reader_url} target="_blank" rel="noopener noreferrer">{doc.title}<ArrowUpRight size={16}/></a></h3><p className="research-small">{doc.format.toUpperCase()} · {doc.page_count.toLocaleString()} pages or sections</p>
   <details><summary>Source and extraction notes</summary><p>{doc.quality.ocr_pages} OCR pages · {doc.quality.low_text_pages} pages with little text.</p>{doc.legal_currency&&<p>{doc.legal_currency.replaceAll('_',' ')}</p>}<div className="local-source-links"><a href={doc.original_url} target="_blank" rel="noopener noreferrer">Original file</a><a href={doc.text_url} target="_blank" rel="noopener noreferrer">Complete text</a>{cleanUrl(doc.url)&&<a href={doc.url} target="_blank" rel="noopener noreferrer">Publisher source</a>}</div></details>
  </article>)}{result?.records?.map(record=><article className="local-evidence-row" key={record.record_id}>
   <h3><a href={'/directory/'+encodeURIComponent(record.record_id)} target="_blank" rel="noopener noreferrer">{record.name}<ArrowUpRight size={16}/></a></h3><p>{record.summary}</p><p className="research-small">{record.collection} · {record.goa_location} · {record.verification_status.replaceAll('_',' ')}</p>
   <details><summary>Provenance and verification</summary><p>Checked: {record.checked_on||'Date not recorded'}</p><p>{record.activity_verification_notes}</p><p>{record.notes}</p><div className="local-source-links">{record.source_urls.split(' | ').filter(cleanUrl).map((url,i)=><a href={url} key={url} target="_blank" rel="noopener noreferrer">Source {i+1}<ArrowUpRight size={14}/></a>)}</div><a href={'/api/dev/crm/records/'+encodeURIComponent(record.record_id)} target="_blank" rel="noopener noreferrer">Full public record</a></details>
  </article>)}</div>
  {result&&<nav className="local-pagination" aria-label="Evidence pages"><Button variant="ghost" disabled={busy||offset===0} onClick={()=>void load(Math.max(0,offset-10))}>Previous</Button><Button variant="ghost" disabled={busy||result.next_offset===null} onClick={()=>void load(result.next_offset||0)}>Next</Button></nav>}</>:settings&&<form className="local-settings" onSubmit={save}><h3>Live research settings</h3><p>Prompt and retrieval edits apply to the next request. Source files stay read-only.</p><Textarea label="Answer style instructions" value={settings.answer_brief} onChange={e=>setSettings({...settings,answer_brief:e.target.value})} rows={6} maxLength={8000}/><Input label="Additional retrieval terms" value={settings.extra_retrieval_terms} onChange={e=>setSettings({...settings,extra_retrieval_terms:e.target.value})} maxLength={300}/><label>Reasoning effort<select value={settings.effort} onChange={e=>setSettings({...settings,effort:e.target.value})}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label><Button type="submit" disabled={busy}>Save settings</Button><p role="status">{saved}</p><p className="research-small">These settings cannot change the dev spend allowance. The agent's source and citation rules remain in place.</p></form>}
  {error&&<p role="alert">{error}</p>}
 </section>;
}
