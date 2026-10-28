import {useEffect,useRef,useState,type FormEvent} from 'react';
import {Link} from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import {adminApi,type AdminSession} from './admin-api';
import {satelliteApi,type SatelliteArea,type SatelliteScene,type SatellitePlan,type SatelliteResult,type SatelliteIntent} from './satellite-api';
import './satellite.css';

const dateLabel=(s:string)=>new Date(s).toLocaleString('en-IN',{timeZone:'Asia/Kolkata',dateStyle:'medium',timeStyle:'short'})+' IST';
const percent=(n:number)=>`${Math.round(n*100)}%`;
const today=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const intents:Record<SatelliteIntent,string>={canopy_loss:'Tree canopy',fire:'Fire evidence',surface_water:'Visible water',land_change:'Clearing and construction'};

function AreaMap({area,onArea,candidates}:{area:SatelliteArea|null;onArea:(area:SatelliteArea)=>void;candidates?:GeoJSON.FeatureCollection}) {
  const container=useRef<HTMLDivElement>(null),map=useRef<L.Map|null>(null),selection=useRef<L.Rectangle|null>(null),features=useRef<L.GeoJSON|null>(null);
  const selecting=useRef(false),first=useRef<L.LatLng|null>(null),callback=useRef(onArea);
  const [drawing,setDrawing]=useState(false),[corner,setCorner]=useState(false);
  callback.current=onArea;
  useEffect(()=>{
    if(!container.current)return;
    const instance=L.map(container.current,{center:[15.4,74],zoom:10,minZoom:9,maxBounds:[[14.7,73.5],[16,74.6]],maxBoundsViscosity:.8});map.current=instance;
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(instance);
    instance.on('click',(event:L.LeafletMouseEvent)=>{
      if(!selecting.current)return;
      if(!first.current){first.current=event.latlng;setCorner(true);return;}
      const bounds=L.latLngBounds(first.current,event.latlng);
      callback.current({bbox:[bounds.getWest(),bounds.getSouth(),bounds.getEast(),bounds.getNorth()]});
      first.current=null;selecting.current=false;setDrawing(false);setCorner(false);
    });
    return()=>{instance.remove();map.current=null;};
  },[]);
  useEffect(()=>{
    if(!map.current)return;
    selection.current?.remove();
    if(area){const [w,s,e,n]=area.bbox;selection.current=L.rectangle([[s,w],[n,e]],{color:'#193e32',weight:2,fillOpacity:.12}).addTo(map.current);map.current.fitBounds([[s,w],[n,e]],{maxZoom:16,padding:[20,20]});}
  },[area]);
  useEffect(()=>{if(map.current){features.current?.remove();if(candidates)features.current=L.geoJSON(candidates,{style:{color:'#8a391f',weight:2,fillOpacity:.3}}).addTo(map.current);}},[candidates]);
  return <div className="satellite-map-section"><div ref={container} className="satellite-map" aria-label="Goa map. Use coordinate fields below as a keyboard alternative to drawing." />
    <div className="satellite-map-toolbar"><Button type="button" variant="secondary" onClick={()=>{selecting.current=!selecting.current;first.current=null;setCorner(false);setDrawing(selecting.current);}}>{drawing?'Cancel area selection':'Select an area on the map'}</Button>
      <p role="status">{drawing?(corner?'Choose the opposite corner.':'Choose the first corner.'):area?'Area selected. Keep it within Goa and under 25 km².':'Zoom to a place, then select two opposite corners.'}</p></div>
  </div>;
}

export default function Satellite(){
  const [session,setSession]=useState<AdminSession|null>(null),[authChecked,setAuthChecked]=useState(false);
  const [area,setArea]=useState<SatelliteArea|null>(null),[coords,setCoords]=useState(['73.82','15.48','73.83','15.49']);
  const [question,setQuestion]=useState('Where has tree canopy disappeared in this area in the last 10 days?');
  const [start,setStart]=useState(()=>{const d=new Date();d.setDate(d.getDate()-40);return d.toISOString().slice(0,10);}),[end,setEnd]=useState(today);
  const [intent,setIntent]=useState<SatelliteIntent>('canopy_loss'),[plan,setPlan]=useState<SatellitePlan|null>(null);
  const [scenes,setScenes]=useState<SatelliteScene[]>([]),[before,setBefore]=useState(''),[after,setAfter]=useState('');
  const [result,setResult]=useState<SatelliteResult|null>(null),[busy,setBusy]=useState(''),[error,setError]=useState(''),[notice,setNotice]=useState('');
  const [readiness,setReadiness]=useState<{imagery_ready:boolean;planner_ready:boolean;decisions_ready:boolean}|null>(null);
  const controller=useRef<AbortController|null>(null),lock=useRef(false);
  useEffect(()=>{const abort=new AbortController();adminApi<AdminSession>('/api/admin/session',{signal:abort.signal}).then(s=>{setSession(s);return satelliteApi<typeof readiness>('/status',s.csrfToken,undefined,abort.signal);}).then(setReadiness).catch(()=>{}).finally(()=>{if(!abort.signal.aborted)setAuthChecked(true);});return()=>{abort.abort();controller.current?.abort();};},[]);
  function clearResults(){setScenes([]);setBefore('');setAfter('');setResult(null);setNotice('');setError('');}
  function chooseArea(value:SatelliteArea){setArea(value);setCoords(value.bbox.map(v=>v.toFixed(5)));setPlan(null);clearResults();}
  async function run(label:string,action:(signal:AbortSignal)=>Promise<void>){
    if(lock.current)return;lock.current=true;const abort=new AbortController();controller.current=abort;setBusy(label);setError('');
    try{await action(abort.signal);}catch(e){if(!abort.signal.aborted)setError(e instanceof Error?e.message:'The investigation could not complete.');}
    finally{lock.current=false;if(!abort.signal.aborted)setBusy('');}
  }
  function ask(event:FormEvent){event.preventDefault();if(!session)return;void run('Interpreting your question…',async signal=>{
    clearResults();const value=await satelliteApi<SatellitePlan>('/plan',session.csrfToken,{question,area},signal);setPlan(value);
    if(value.state==='ready'){setStart(value.catalog_start!);setEnd(value.catalog_end!);setIntent(value.intent!);}
  });}
  function findScenes(){if(!session||!area)return;void run('Finding dated observations…',async signal=>{
    clearResults();const data=await satelliteApi<{scenes:SatelliteScene[];truncated:boolean}>('/catalog',session.csrfToken,{area,start_date:start,end_date:end},signal);
    setScenes(data.scenes);setNotice(data.scenes.length?(data.truncated?'This is a partial catalog. Narrow the date range to see all matches.':'Cloud percentages describe the whole satellite scene. Local visibility is checked during comparison.'):'No imagery was found for this area and date range. Try a wider range.');
  });}
  function compare(){if(!session||!area)return;void run('Comparing observations…',async signal=>{
    setResult(null);const job=await satelliteApi<{id:string}>('/compare',session.csrfToken,{area,start_date:start,end_date:end,before_id:before,after_id:after,intent,
      ...(plan?.state==='ready'?{window_start:plan.window_start,window_end:plan.window_end}:{})},signal);
    for(let attempts=0;attempts<120;attempts++){
      await new Promise<void>((resolve,reject)=>{const abort=()=>{clearTimeout(timer);reject(new DOMException('Cancelled','AbortError'));};const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},2000);signal.addEventListener('abort',abort,{once:true});});
      const update=await satelliteApi<{status:string;result:SatelliteResult&{error?:string}}>('/jobs/'+job.id,session.csrfToken,undefined,signal);
      if(update.status==='failed')throw new Error(update.result.error);
      if(update.status==='complete'){setResult(update.result);return;}
    }
    throw new Error('This comparison is taking longer than expected. Its job reference is '+job.id+'.');
  });}
  const centre=area?[(area.bbox[0]+area.bbox[2])/2,(area.bbox[1]+area.bbox[3])/2]:[74,15.4];
  return <main className="satellite-page shell"><header className="satellite-heading"><h1>Explore changes in Goa</h1><p>Ask about tree canopy, visible water, fire evidence or land change. Compare dated observations and see what the evidence can support.</p></header>
    <p className="satellite-qualification">Experimental investigation tool. Sentinel-2 can reveal changes in canopy patches; it cannot reliably count individual trees or prove why they disappeared.</p>
    {authChecked&&!session&&<p className="satellite-access">The map and source links are open to explore. <Link to="/admin">Sign in to the team workspace</Link> to retrieve and compare imagery.</p>}
    {session&&readiness&&!readiness.imagery_ready&&<p role="status">Copernicus imagery is awaiting server configuration. You can select an area and prepare a question.</p>}
    {session&&readiness&&!readiness.decisions_ready&&<p>Image classification is awaiting OpenAI configuration. Numeric imagery comparisons can still be inspected once imagery is connected.</p>}
    <form className="satellite-question" onSubmit={ask}><Textarea label="Ask about this area" value={question} maxLength={1000} rows={3} onChange={e=>setQuestion(e.target.value)} placeholder="Has tree canopy disappeared here in the last 10 days?"/>
      <Button type="submit" disabled={!session||!!busy||question.trim().length<3}>Prepare investigation</Button></form>
    {plan&&<div className="satellite-plan" role="status"><p>{plan.message}</p>{plan.window_start&&<p>Requested period: {dateLabel(plan.window_start)} to {dateLabel(plan.window_end!)}.</p>}{plan.place_name&&<p>Requested place: {plan.place_name}. Select it on the map, then ask about “this area”.</p>}{plan.warnings?.map(w=><p key={w}>{w}</p>)}</div>}
    <fieldset className="satellite-controls" disabled={!!busy}><legend>Choose your area and observations</legend>
      <AreaMap area={area} onArea={chooseArea} candidates={result?.evidence.candidates}/>
      <div className="satellite-coordinates">{['West longitude','South latitude','East longitude','North latitude'].map((label,i)=><Input key={label} label={label} type="number" step="0.00001" value={coords[i]} onChange={e=>setCoords(v=>v.map((old,j)=>i===j?e.target.value:old))}/>)}</div>
      <Button type="button" variant="secondary" onClick={()=>{const v=coords.map(Number);if(coords.some(s=>!s.trim())||v.some(n=>!Number.isFinite(n))||v[0]>=v[2]||v[1]>=v[3]||v[0]<73.5||v[2]>74.6||v[1]<14.7||v[3]>16){setError('Enter a valid west/south/east/north area around Goa.');return;}chooseArea({bbox:v as SatelliteArea['bbox']});}}>Use these coordinates</Button>
      <div className="satellite-dates"><Input label="Search from" type="date" value={start} max={end} min="2017-03-28" onChange={e=>{setStart(e.target.value);setPlan(null);clearResults();}}/><Input label="Search until" type="date" value={end} min={start} max={today()} onChange={e=>{setEnd(e.target.value);setPlan(null);clearResults();}}/>
        <label>Investigate<select value={intent} onChange={e=>setIntent(e.target.value as SatelliteIntent)}>{Object.entries(intents).map(([v,l])=><option value={v} key={v}>{l}</option>)}</select></label></div>
      <Button type="button" disabled={!session||!area||!start||!end||!!busy} onClick={findScenes}>Find observations</Button>
      {notice&&<p role="status">{notice}</p>}
      {!!scenes.length&&<><div className="satellite-dates">{(['Before','After'] as const).map(label=><label key={label}>{label} observation<select value={label==='Before'?before:after} onChange={e=>{(label==='Before'?setBefore:setAfter)(e.target.value);setResult(null);}}><option value="">Choose an acquisition</option>{scenes.map(s=><option key={s.id} value={s.id}>{dateLabel(s.acquired_at)} · scene cloud {s.scene_cloud_percent===null?'unknown':Math.round(s.scene_cloud_percent)+'%'}</option>)}</select></label>)}</div><Button type="button" onClick={compare} disabled={!before||!after||before===after}>Compare selected observations</Button></>}
    </fieldset>
    {busy&&<p role="status" aria-live="polite">{busy}</p>}{error&&<p className="satellite-error" role="alert">{error}</p>}
    {result&&<section className="satellite-results"><h2>What these observations show</h2><p>{percent(result.evidence.common_usable_fraction)} of the selected area is usable in both observations. {result.evidence.state!=='observable'?'Clear coverage is insufficient for reliable classification.':'Findings need review alongside the images.'}</p>
      <div className="satellite-pair">{(['before','after'] as const).map(which=><figure key={which}><img src={result[which].image} alt={`${which==='before'?'Earlier':'Later'} Sentinel-2 true-colour observation of the selected Goa area`}/><figcaption><strong>{which==='before'?'Before':'After'}</strong>{result[which].acquired_at.map(d=><span key={d}>{dateLabel(d)}</span>)}<span>{percent(result[which].quality.usable_fraction)} usable · {percent(result[which].quality.cloud_shadow_or_uncertain_fraction)} cloud, shadow or uncertain</span><small>{result[which].catalog_scene_id}</small></figcaption></figure>)}</div>
      <p>{result.evidence.candidates.features.length} possible vegetation-loss patch{result.evidence.candidates.features.length===1?'':'es'} meet the exploratory size and reflectance thresholds. This is not a count of trees.{result.evidence.candidates_truncated?' Only the largest 100 patches are shown.':''}</p>
      {result.observation_interval.query_window_relation==='overlaps_window'&&<p>The observation interval overlaps your requested period. A possible change could have occurred before that period.</p>}
      {result.observation_interval.query_window_relation==='outside_window'&&<p>This pair does not bracket a change inside your requested period. Select observations closer to that period.</p>}
      {result.classification.message&&<p>{result.classification.message}</p>}
      {!!Object.keys(result.classification.answers).length&&<dl className="satellite-assessments">{Object.entries(result.classification.answers).map(([name,a])=><div key={name}><dt>{name.replaceAll('_',' ')}</dt><dd>{a.choice.replaceAll('_',' ')}</dd></div>)}</dl>}
      <details><summary>Numeric spectral evidence</summary><div className="satellite-table"><table><thead><tr><th>Index</th><th>Before median</th><th>After median</th><th>Median paired change</th></tr></thead><tbody>{Object.entries(result.evidence.metrics).map(([k,v])=><tr key={k}><th>{k.toUpperCase()}</th><td>{v.before_median}</td><td>{v.after_median}</td><td>{v.median_paired_change}</td></tr>)}</tbody></table></div><p>Measured from reflectance. Visible/NIR bands are native 10 m; SWIR and scene classification are native 20 m.</p></details>
      <p>{result.fire_detections.message}</p>{result.limitations.map(l=><p className="satellite-note" key={l}>{l}</p>)}
    </section>}
    <section className="satellite-context"><h2>Understand the local context</h2><p>Amche Atlas brings together Goa’s survey plots, forests, wetlands, water bodies and planning maps. Check each layer’s date and source alongside the satellite observations.</p>
      <a href={`https://amche.in/?atlas=goa#14/${centre[1].toFixed(5)}/${centre[0].toFixed(5)}`} target="_blank" rel="noreferrer">Open this location in Amche Atlas ↗</a>
      <p>Context layers are not yet joined automatically to these findings. Map boundaries and planning records do not establish a change’s cause or legality.</p>
    </section>
  </main>;
}
