import {DatePicker} from './components/arc/date-picker/date-picker';
import {calendarDate,calendarValue} from './satellite-calendar';
import {MorphSelect} from './components/arc/morph-select/morph-select';
import {useEffect,useRef,useState,type FormEvent} from 'react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {satelliteApi,type SatelliteHistory as History,type SatelliteIntent,type SatelliteArea} from './satellite-api';

export const satelliteIntents:Record<SatelliteIntent,string>={canopy_loss:'Tree canopy',surface_water:'Rivers and wetlands',waste:'Waste and material accumulation',land_change:'Clearing and construction',fire:'Fire evidence'};
export const observationDate=(s:string)=>new Date(s).toLocaleString('en-IN',{timeZone:'Asia/Kolkata',dateStyle:'medium',timeStyle:'short'})+' IST';

export function SatelliteHistory({csrfToken,revision,busy,onOpen,area=null}:{csrfToken:string;revision:number;busy:boolean;onOpen:(id:string)=>void;area?:SatelliteArea|null}){
  const [query,setQuery]=useState(''),[intent,setIntent]=useState(''),[start,setStart]=useState(''),[end,setEnd]=useState('');
  const [filters,setFilters]=useState({query:'',intent:'',start_date:'',end_date:''});
  const [refresh,setRefresh]=useState(0);
  const scope=JSON.stringify([filters,area?.bbox??null]);
  const [pagination,setPagination]=useState({scope:'',offset:0});
  // A changed selection starts at page one during this render, without first
  // requesting the previous area's offset or displaying its saved results.
  const offset=pagination.scope===scope?pagination.offset:0;
  const key=JSON.stringify([scope,offset,revision,refresh]);
  const current=useRef({key,token:csrfToken});current.current={key,token:csrfToken};
  const [response,setResponse]=useState<{key:string;token:string;data:History}|null>(null);
  const [status,setStatus]=useState<{key:string;token:string;loading:boolean;error:string}|null>(null);
  const data=response?.key===key&&response.token===csrfToken?response.data:null;
  const currentStatus=status?.key===key&&status.token===csrfToken?status:null;
  const loading=currentStatus?.loading??true,error=currentStatus?.error||'';
  useEffect(()=>{
    const abort=new AbortController();setStatus({key,token:csrfToken,loading:true,error:''});
    const body=Object.fromEntries(Object.entries({...filters,offset,limit:6,...(area?{area}:{})}).filter(([,value])=>value!==''));
    const isCurrent=()=>!abort.signal.aborted&&current.current.key===key&&current.current.token===csrfToken;
    satelliteApi<History>('/history',csrfToken,body,abort.signal).then(data=>{if(isCurrent()){setResponse({key,token:csrfToken,data});setStatus({key,token:csrfToken,loading:false,error:''});}})
      .catch(error=>{if(isCurrent())setStatus({key,token:csrfToken,loading:false,error:error instanceof Error?error.message:'Saved investigations could not be loaded.'});});
    return()=>abort.abort();
  },[key,csrfToken]);
  function search(event:FormEvent){event.preventDefault();setPagination({scope:'',offset:0});setFilters({query,intent,start_date:start,end_date:end});setRefresh(value=>value+1);}
  return <section className="satellite-history" aria-labelledby="satellite-history-heading"><h2 id="satellite-history-heading">Your investigations</h2>
    <p>{area?'Showing your saved comparisons that overlap the selected map area. Their measurements describe each original comparison footprint.':'Showing your private history across all saved areas. Select an area on the map to narrow this list.'}</p>
    <p>Revisit comparisons by topic and observation period. Results are private to your account and retained for 30 days. These selected areas do not represent monitoring coverage across Goa.</p>
    <form onSubmit={search}><div className="satellite-dates"><Input label="Search saved questions and findings" value={query} maxLength={300} onChange={e=>setQuery(e.target.value)}/>
      <MorphSelect label="Topic" value={intent} onValueChange={setIntent} items={[{value:'',label:'All topics'},...Object.entries(satelliteIntents).map(([value,label])=>({value,label}))]}/>
      <DatePicker label="Observation period from" value={calendarDate(start)} maxDate={calendarDate(end)} onChange={date=>setStart(calendarValue(date))}/><DatePicker label="Observation period until" value={calendarDate(end)} minDate={calendarDate(start)} onChange={date=>setEnd(calendarValue(date))}/></div>
      <Button type="submit" variant="secondary" disabled={loading}>Search investigations</Button></form>
    {loading&&<p role="status">Loading saved investigations{area?' for this area':''}…</p>}{error&&<p role="alert">{error}</p>}
    {data&&!data.items.length&&<p>No saved investigations match these filters{area?' in the selected area':''}. Start a comparison above or broaden the filters. This does not establish that no environmental change occurred.</p>}
    {data?.scan_truncated&&<p className="satellite-note">This list comes from a bounded search of retained comparisons and may be incomplete. Narrow the dates, topic or question to inspect more relevant results.</p>}
    {data&&<><ul className="satellite-history-list">{data.items.map(item=><li key={item.id}><div><p className="satellite-history-topic">{item.request?satelliteIntents[item.request.intent]:'Earlier investigation'} · {item.status}</p>
      <h3>{item.request?.question||item.summary?.headline||'Saved comparison'}</h3>
      {item.request?.question&&item.summary?.headline&&<p>{item.summary.headline}</p>}
      {item.spatial&&<p>{item.spatial.relation==='same_area'?'Same selected footprint.':`Overlapping footprint covers ${Math.round(item.spatial.query_fraction*100)}% of your selection. Measurements apply to the whole original comparison, not just this overlap.`}</p>}
      {item.observation_interval&&<p>{observationDate(item.observation_interval.before)} → {observationDate(item.observation_interval.after)}</p>}
      {item['evidence.common_usable_fraction']!==null&&<p>{Math.round(item['evidence.common_usable_fraction']*100)}% usable in both observations.</p>}
      {item.error&&<p>{item.error}</p>}</div><Button type="button" variant="secondary" disabled={busy||item.status!=='complete'} onClick={()=>onOpen(item.id)}>Open saved result</Button></li>)}</ul>
      <div className="satellite-history-pages">{offset>0&&<Button type="button" variant="secondary" disabled={loading} onClick={()=>setPagination({scope,offset:Math.max(0,offset-6)})}>Previous results</Button>}{data.next_offset!==null&&<Button type="button" variant="secondary" disabled={loading} onClick={()=>setPagination({scope,offset:data.next_offset!})}>More results</Button>}</div></>}
  </section>;
}
