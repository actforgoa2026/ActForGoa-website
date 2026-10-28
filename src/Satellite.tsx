import {useEffect,useRef,useState,type FormEvent} from 'react';
import {Link} from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import {adminApi,type AdminSession} from './admin-api';
import {satelliteApi,type SatelliteArea,type SatelliteScene,type SatellitePlan,type SatelliteResult,type SatelliteIntent,type SatelliteRequest} from './satellite-api';
import {SatelliteHistory,satelliteIntents as intents,observationDate as dateLabel} from './SatelliteHistory';
import {SatelliteContext} from './SatelliteContext';
import './satellite.css';

const percent=(n:number)=>`${Math.round(n*100)}%`;
const today=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const evidenceLabels={before:'Before image',after:'After image',coverage:'Visibility',spectral:'Numeric evidence',assessment:'Image decisions'};
const decisionLabel=(value:string)=>value==='yes'?'Yes':value==='no'?'No':'Uncertain';

function ImageDecisions({result}:{result:SatelliteResult}){
  return <div id="satellite-assessment">
    {result.canopy_presence&&(!result.intent||result.intent==='canopy_loss')&&<><h3>Was tree canopy visible in the same area?</h3><dl className="satellite-presence"><div><dt>Before · {dateLabel(result.before.acquired_at[0])}</dt><dd>{decisionLabel(result.canopy_presence.before)}</dd></div><div><dt>After · {dateLabel(result.after.acquired_at[0])}</dt><dd>{decisionLabel(result.canopy_presence.after)}</dd></div></dl><p className="satellite-note">{result.canopy_presence.scope}</p></>}
    {result.classification.provider&&<p className="satellite-note">Image decisions: {result.classification.provider==='openai-decisions'?'OpenAI Decisions':'Anthropic'} · {result.classification.model}. {result.classification.validation}</p>}
    {result.classification.message&&<p>{result.classification.message}</p>}
    {!!Object.keys(result.classification.answers).length&&<details><summary>Other image decisions</summary><dl className="satellite-assessments">{Object.entries(result.classification.answers).filter(([name])=>!['before_canopy','after_canopy'].includes(name)).map(([name,a])=><div key={name}><dt>{name.replaceAll('_',' ')}</dt><dd>{a.choice.replaceAll('_',' ')}</dd></div>)}</dl></details>}
  </div>;
}

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
  const [historyRevision,setHistoryRevision]=useState(0),[catalogFreshness,setCatalogFreshness]=useState<{searched_at:string;latest_acquired_at:string|null}|null>(null);
  const [readiness,setReadiness]=useState<{imagery_ready:boolean;planner_ready:boolean;decisions_ready:boolean;classification_ready?:boolean;classification_provider?:string|null}|null>(null);
  const controller=useRef<AbortController|null>(null),lock=useRef(false);
  useEffect(()=>{const abort=new AbortController();adminApi<AdminSession>('/api/admin/session',{signal:abort.signal}).then(s=>{setSession(s);return satelliteApi<typeof readiness>('/status',s.csrfToken,undefined,abort.signal);}).then(setReadiness).catch(()=>{}).finally(()=>{if(!abort.signal.aborted)setAuthChecked(true);});return()=>{abort.abort();controller.current?.abort();};},[]);
  function clearResults(){setScenes([]);setBefore('');setAfter('');setResult(null);setNotice('');setError('');setCatalogFreshness(null);}
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
    clearResults();const data=await satelliteApi<{scenes:SatelliteScene[];truncated:boolean;searched_at:string;latest_acquired_at:string|null}>('/catalog',session.csrfToken,{area,start_date:start,end_date:end},signal);
    setCatalogFreshness(data);
    setScenes(data.scenes);setNotice(data.scenes.length?(data.truncated?'This is a partial catalog. Narrow the date range to see all matches.':'Cloud percentages describe the whole satellite scene. Local visibility is checked during comparison.'):'No imagery was found for this area and date range. Try a wider range.');
  });}
  function compare(){if(!session||!area)return;void run('Comparing observations…',async signal=>{
    setResult(null);const job=await satelliteApi<{id:string}>('/compare',session.csrfToken,{area,start_date:start,end_date:end,before_id:before,after_id:after,intent,question,
      ...(plan?.state==='ready'?{window_start:plan.window_start,window_end:plan.window_end}:{})},signal);
    for(let attempts=0;attempts<120;attempts++){
      await new Promise<void>((resolve,reject)=>{const abort=()=>{clearTimeout(timer);reject(new DOMException('Cancelled','AbortError'));};const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},2000);signal.addEventListener('abort',abort,{once:true});});
      const update=await satelliteApi<{status:string;result:SatelliteResult&{error?:string}}>('/jobs/'+job.id,session.csrfToken,undefined,signal);
      if(update.status==='failed'){setHistoryRevision(v=>v+1);throw new Error(update.result.error);}
      if(update.status==='complete'){setResult(update.result);setHistoryRevision(v=>v+1);return;}
    }
    throw new Error('This comparison is taking longer than expected. Its job reference is '+job.id+'.');
  });}
  function openSaved(id:string){if(!session)return;void run('Opening saved investigation…',async signal=>{
    const job=await satelliteApi<{status:string;request:SatelliteRequest|null;result:SatelliteResult}>('/jobs/'+id,session.csrfToken,undefined,signal);
    if(job.status!=='complete')throw new Error('This investigation has not completed.');
    clearResults();setPlan(null);
    if(job.request){const r=job.request;setArea(r.area);setCoords(r.area.bbox.map(String));setStart(r.start_date);setEnd(r.end_date);setIntent(r.intent);setQuestion(r.question||'');}
    setResult(job.result);
    requestAnimationFrame(()=>document.querySelector('.satellite-results')?.scrollIntoView({behavior:'smooth',block:'start'}));
  });}
  const centre=area?[(area.bbox[0]+area.bbox[2])/2,(area.bbox[1]+area.bbox[3])/2]:[74,15.4];
  return <main className="satellite-page shell"><header className="satellite-heading"><h1>Explore changes in Goa</h1><p>Follow changes in trees, rivers, wetlands and land use over time. Compare dated satellite observations, revisit investigations and read relevant ecology research.</p></header>
    <p className="satellite-qualification">Experimental area investigations. Clear imagery can lag behind today, especially during monsoon. Small litter and individual trees may not be resolvable; construction legality requires planning records.</p>
    {authChecked&&!session&&<p className="satellite-access">The map and source links are open to explore. <Link to="/admin">Sign in to the team workspace</Link> to retrieve and compare imagery.</p>}
    {session&&readiness&&!readiness.imagery_ready&&<p role="status">Copernicus imagery is awaiting server configuration. You can select an area and prepare a question.</p>}
    {session&&readiness&&!(readiness.classification_ready??readiness.decisions_ready)&&<p>Image decisions are awaiting server configuration. You can still inspect dated imagery and numeric comparisons.</p>}
    {session&&<SatelliteHistory csrfToken={session.csrfToken} revision={historyRevision} busy={!!busy} onOpen={openSaved}/>}
    <form className="satellite-question" onSubmit={ask}><Textarea label="Ask about this area" value={question} maxLength={1000} rows={3} onChange={e=>setQuestion(e.target.value)} placeholder="Has tree canopy disappeared here in the last 10 days?"/>
      <Button type="submit" disabled={!session||!!busy||question.trim().length<3}>Prepare investigation</Button></form>
    {plan&&<div className="satellite-plan" role="status"><p>{plan.message}</p>{plan.window_start&&<p>Requested period: {dateLabel(plan.window_start)} to {dateLabel(plan.window_end!)}.</p>}{plan.place_name&&<p>Requested place: {plan.place_name}. Select it on the map, then ask about “this area”.</p>}{plan.warnings?.map(w=><p key={w}>{w}</p>)}</div>}
    <fieldset className="satellite-controls" disabled={!!busy}><legend>Choose your area and observations</legend>
      <AreaMap area={area} onArea={chooseArea} candidates={result?.intent==='surface_water'?result.evidence.water_candidates:result?.intent==='canopy_loss'?result.evidence.candidates:undefined}/>
      <div className="satellite-coordinates">{['West longitude','South latitude','East longitude','North latitude'].map((label,i)=><Input key={label} label={label} type="number" step="0.00001" value={coords[i]} onChange={e=>setCoords(v=>v.map((old,j)=>i===j?e.target.value:old))}/>)}</div>
      <Button type="button" variant="secondary" onClick={()=>{const v=coords.map(Number);if(coords.some(s=>!s.trim())||v.some(n=>!Number.isFinite(n))||v[0]>=v[2]||v[1]>=v[3]||v[0]<73.5||v[2]>74.6||v[1]<14.7||v[3]>16){setError('Enter a valid west/south/east/north area around Goa.');return;}chooseArea({bbox:v as SatelliteArea['bbox']});}}>Use these coordinates</Button>
      <div className="satellite-dates"><Input label="Search from" type="date" value={start} max={end} min="2017-03-28" onChange={e=>{setStart(e.target.value);setPlan(null);clearResults();}}/><Input label="Search until" type="date" value={end} min={start} max={today()} onChange={e=>{setEnd(e.target.value);setPlan(null);clearResults();}}/>
        <label>Investigate<select value={intent} onChange={e=>{setIntent(e.target.value as SatelliteIntent);setResult(null);setPlan(null);}}>{Object.entries(intents).map(([v,l])=><option value={v} key={v}>{l}</option>)}</select></label></div>
      <Button type="button" disabled={!session||!area||!start||!end||!!busy} onClick={findScenes}>Find observations</Button>
      {notice&&<p role="status">{notice}</p>}
      {catalogFreshness?.latest_acquired_at&&<p className="satellite-freshness">Latest acquisition found in this search: <strong>{dateLabel(catalogFreshness.latest_acquired_at)}</strong>. Catalog checked {dateLabel(catalogFreshness.searched_at)}. Availability does not guarantee clear local visibility.</p>}
      {!!scenes.length&&<><div className="satellite-dates">{(['Before','After'] as const).map(label=><label key={label}>{label} observation<select value={label==='Before'?before:after} onChange={e=>{(label==='Before'?setBefore:setAfter)(e.target.value);setResult(null);}}><option value="">Choose an acquisition</option>{scenes.map(s=><option key={s.id} value={s.id}>{dateLabel(s.acquired_at)} · scene cloud {s.scene_cloud_percent===null?'unknown':Math.round(s.scene_cloud_percent)+'%'}</option>)}</select></label>)}</div><Button type="button" onClick={compare} disabled={!before||!after||before===after}>Compare selected observations</Button></>}
    </fieldset>
    {busy&&<p role="status" aria-live="polite">{busy}</p>}{error&&<p className="satellite-error" role="alert">{error}</p>}
    {result&&<section className="satellite-results"><h2>{result.summary?.headline??'What these observations show'}</h2><ImageDecisions result={result}/>
      {result.freshness&&<div className="satellite-freshness"><p>Latest acquisition found in the saved search: <strong>{dateLabel(result.freshness.latest_acquired_at_in_search)}</strong>. Catalog checked {dateLabel(result.freshness.catalog_searched_at)}.</p>
        <p>{result.freshness.newer_acquisitions_in_search?`${result.freshness.newer_acquisitions_in_search} newer acquisition(s) were available than the selected after image.`:'The selected after image was the newest acquisition returned by this search.'} {result.freshness.note}{result.freshness.catalog_truncated?' This was a partial catalog; newer matches may be missing.':''}</p></div>}
      {result.summary&&<div className="satellite-answer" aria-label="Evidence-based interpretation">{result.summary.statements.map((statement,i)=><p key={i}>{statement.text}{' '}<span className="satellite-evidence-links">{statement.sources.map(source=><a href={'#satellite-'+source} key={source}>{evidenceLabels[source]}</a>)}</span></p>)}</div>}
      <p id="satellite-coverage">{percent(result.evidence.common_usable_fraction)} of the selected area is usable in both observations. {result.evidence.state!=='observable'?'Clear coverage is insufficient for reliable classification.':'Findings need review alongside the images.'}</p>
      <div className="satellite-pair">{(['before','after'] as const).map(which=><figure key={which} id={'satellite-'+which}><img src={result[which].image} alt={`${which==='before'?'Earlier':'Later'} Sentinel-2 true-colour observation of the selected Goa area`}/><figcaption><strong>{which==='before'?'Before':'After'}</strong>{result[which].acquired_at.map(d=><span key={d}>{dateLabel(d)}</span>)}<span>{percent(result[which].quality.usable_fraction)} usable · {percent(result[which].quality.cloud_shadow_or_uncertain_fraction)} cloud, shadow or uncertain</span><small>{result[which].catalog_scene_id}</small></figcaption></figure>)}</div>
      <p className="satellite-note">Contains modified Copernicus Sentinel data. Dates above are acquisition dates, not dates of a change.</p>
      {!result.summary&&<><p>{result.evidence.candidates.features.length} possible vegetation-loss patch{result.evidence.candidates.features.length===1?'':'es'} meet the exploratory size and reflectance thresholds. This is not a count of trees.{result.evidence.candidates_truncated?' Only the largest 100 patches are shown.':''}</p>
      {result.observation_interval.query_window_relation==='overlaps_window'&&<p>The observation interval overlaps your requested period. A possible change could have occurred before that period.</p>}
      {result.observation_interval.query_window_relation==='outside_window'&&<p>This pair does not bracket a change inside your requested period. Select observations closer to that period.</p>}</>}
      <details id="satellite-spectral"><summary>Numeric spectral evidence</summary><div className="satellite-table"><table><thead><tr><th>Index</th><th>Before median</th><th>After median</th><th>Median paired change</th></tr></thead><tbody>{Object.entries(result.evidence.metrics).map(([k,v])=><tr key={k}><th>{k.toUpperCase()}</th><td>{v.before_median}</td><td>{v.after_median}</td><td>{v.median_paired_change}</td></tr>)}</tbody></table></div><p>Measured from reflectance. Visible/NIR bands are native 10 m; SWIR and scene classification are native 20 m.</p>
        {result.intent==='surface_water'&&result.evidence.water_change&&<div><h3>Water-classified area</h3><dl className="satellite-assessments">{Object.entries(result.evidence.water_change).filter(([key])=>key.endsWith('_area_m2')).map(([key,value])=><div key={key}><dt>{key.replace('_area_m2','')}</dt><dd>{Number(value).toLocaleString('en-IN')} m²</dd></div>)}</dl><p>{result.evidence.water_change.method}</p></div>}</details>
      <details><summary>What these observations cannot establish</summary><p>{result.fire_detections.message}</p>{result.intent==='land_change'&&<p>{result.planning_context?.message}</p>}{result.limitations.map(l=><p className="satellite-note" key={l}>{l}</p>)}</details>
      {result.library_context&&<SatelliteContext context={result.library_context}/>}
    </section>}
    <section className="satellite-context"><h2>Understand the local context</h2><p>Amche Atlas brings together Goa’s survey plots, forests, wetlands, water bodies and planning maps. Check each layer’s date and source alongside the satellite observations.</p>
      <a href={`https://amche.in/?atlas=goa#14/${centre[1].toFixed(5)}/${centre[0].toFixed(5)}`} target="_blank" rel="noreferrer">Open this location in Amche Atlas ↗</a>
      <p>Context layers are not yet joined automatically to these findings. Map boundaries and planning records do not establish a change’s cause or legality.</p>
    </section>
  </main>;
}
