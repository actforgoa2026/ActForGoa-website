import {useEffect,useState,type FormEvent} from 'react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {satelliteApi,type SatelliteHistory as History,type SatelliteIntent} from './satellite-api';

export const satelliteIntents:Record<SatelliteIntent,string>={canopy_loss:'Tree canopy',surface_water:'Rivers and wetlands',waste:'Waste and material accumulation',land_change:'Clearing and construction',fire:'Fire evidence'};
export const observationDate=(s:string)=>new Date(s).toLocaleString('en-IN',{timeZone:'Asia/Kolkata',dateStyle:'medium',timeStyle:'short'})+' IST';

export function SatelliteHistory({csrfToken,revision,busy,onOpen}:{csrfToken:string;revision:number;busy:boolean;onOpen:(id:string)=>void}){
  const [query,setQuery]=useState(''),[intent,setIntent]=useState(''),[start,setStart]=useState(''),[end,setEnd]=useState('');
  const [filters,setFilters]=useState({query:'',intent:'',start_date:'',end_date:''});
  const [offset,setOffset]=useState(0),[data,setData]=useState<History|null>(null),[error,setError]=useState(''),[loading,setLoading]=useState(false);
  useEffect(()=>{
    const abort=new AbortController();setLoading(true);setError('');setData(null);
    const body=Object.fromEntries(Object.entries({...filters,offset,limit:6}).filter(([,value])=>value!==''));
    satelliteApi<History>('/history',csrfToken,body,abort.signal).then(setData).catch(e=>{if(!abort.signal.aborted)setError(e instanceof Error?e.message:'Saved investigations could not be loaded.');}).finally(()=>{if(!abort.signal.aborted)setLoading(false);});
    return()=>abort.abort();
  },[csrfToken,revision,filters,offset]);
  function search(event:FormEvent){event.preventDefault();setOffset(0);setFilters({query,intent,start_date:start,end_date:end});}
  return <section className="satellite-history" aria-labelledby="satellite-history-heading"><h2 id="satellite-history-heading">Your investigations</h2>
    <p>Revisit saved comparisons by topic and observation period. Results are private to your account and retained for 30 days. These selected areas do not represent monitoring coverage across Goa.</p>
    <form onSubmit={search}><div className="satellite-dates"><Input label="Search saved questions and findings" value={query} maxLength={300} onChange={e=>setQuery(e.target.value)}/>
      <label>Topic<select value={intent} onChange={e=>setIntent(e.target.value)}><option value="">All topics</option>{Object.entries(satelliteIntents).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
      <Input label="Observation period from" type="date" value={start} max={end||undefined} onChange={e=>setStart(e.target.value)}/><Input label="Observation period until" type="date" value={end} min={start||undefined} onChange={e=>setEnd(e.target.value)}/></div>
      <Button type="submit" variant="secondary" disabled={loading}>Search investigations</Button></form>
    {loading&&<p role="status">Loading saved investigations…</p>}{error&&<p role="alert">{error}</p>}
    {data&&!data.items.length&&<p>No saved investigations match these filters. Start a comparison below or broaden the filters.</p>}
    {data&&<><ul className="satellite-history-list">{data.items.map(item=><li key={item.id}><div><p className="satellite-history-topic">{item.request?satelliteIntents[item.request.intent]:'Earlier investigation'} · {item.status}</p>
      <h3>{item.request?.question||item.summary?.headline||'Saved comparison'}</h3>
      {item.request?.question&&item.summary?.headline&&<p>{item.summary.headline}</p>}
      {item.observation_interval&&<p>{observationDate(item.observation_interval.before)} → {observationDate(item.observation_interval.after)}</p>}
      {item['evidence.common_usable_fraction']!==null&&<p>{Math.round(item['evidence.common_usable_fraction']*100)}% usable in both observations.</p>}
      {item.error&&<p>{item.error}</p>}</div><Button type="button" variant="secondary" disabled={busy||item.status!=='complete'} onClick={()=>onOpen(item.id)}>Open saved result</Button></li>)}</ul>
      <div className="satellite-history-pages">{offset>0&&<Button type="button" variant="secondary" onClick={()=>setOffset(Math.max(0,offset-6))}>Previous results</Button>}{data.next_offset!==null&&<Button type="button" variant="secondary" onClick={()=>setOffset(data.next_offset!)}>More results</Button>}</div></>}
  </section>;
}
