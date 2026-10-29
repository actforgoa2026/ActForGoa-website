import {useEffect,useRef,useState,type FormEvent} from 'react';
import {Link} from 'react-router-dom';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import {adminApi,type AdminSession} from './admin-api';
import {satelliteApi,type SatelliteArea,type SatelliteScene,type SatellitePlan,type SatelliteResult,type SatelliteIntent,type SatelliteRequest,type SatelliteObservation} from './satellite-api';
import {SatelliteHistory,satelliteIntents as intents,observationDate as dateLabel} from './SatelliteHistory';
import {SatelliteContext} from './SatelliteContext';
import {SatelliteMap} from './SatelliteMap';
import {SatelliteTimeline} from './SatelliteTimeline';
import {areaError,orderedPair,orderedScenes} from './satellite-timeline';
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

export default function Satellite(){
  const [session,setSession]=useState<AdminSession|null>(null),[authChecked,setAuthChecked]=useState(false);
  const [area,setArea]=useState<SatelliteArea|null>(null),[coords,setCoords]=useState(['73.82','15.48','73.83','15.49']);
  const [question,setQuestion]=useState('Where has tree canopy disappeared in this area in the last 10 days?');
  const [start,setStart]=useState(()=>{const d=new Date();d.setDate(d.getDate()-40);return d.toISOString().slice(0,10);}),[end,setEnd]=useState(today);
  const [intent,setIntent]=useState<SatelliteIntent>('canopy_loss'),[plan,setPlan]=useState<SatellitePlan|null>(null);
  const [scenes,setScenes]=useState<SatelliteScene[]>([]),[before,setBefore]=useState(''),[after,setAfter]=useState('');
  const [activeId,setActiveId]=useState(''),[observations,setObservations]=useState<Record<string,SatelliteObservation>>({});
  const [result,setResult]=useState<SatelliteResult|null>(null),[busy,setBusy]=useState(''),[error,setError]=useState(''),[notice,setNotice]=useState('');
  const [historyRevision,setHistoryRevision]=useState(0),[catalogFreshness,setCatalogFreshness]=useState<{searched_at:string;latest_acquired_at:string|null}|null>(null);
  const [readiness,setReadiness]=useState<{imagery_ready:boolean;planner_ready:boolean;decisions_ready:boolean;classification_ready?:boolean;classification_provider?:string|null}|null>(null);
  const controller=useRef<AbortController|null>(null),lock=useRef(false);
  useEffect(()=>{const abort=new AbortController();adminApi<AdminSession>('/api/admin/session',{signal:abort.signal}).then(s=>{setSession(s);return satelliteApi<typeof readiness>('/status',s.csrfToken,undefined,abort.signal);}).then(setReadiness).catch(()=>{}).finally(()=>{if(!abort.signal.aborted)setAuthChecked(true);});return()=>{abort.abort();controller.current?.abort();};},[]);
  function clearResults(){setActiveId('');setObservations({});setScenes([]);setBefore('');setAfter('');setResult(null);setNotice('');setError('');setCatalogFreshness(null);}
  function chooseArea(value:SatelliteArea){if(lock.current)return;const message=areaError(value.bbox);if(message){setError(message);return;}setArea(value);setCoords(value.bbox.map(v=>v.toFixed(5)));setPlan(null);clearResults();}
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
    const sorted=orderedScenes(data.scenes);setScenes(sorted);setActiveId(sorted.at(-1)?.id||'');setBefore(sorted[0]?.id||'');setAfter(sorted.length>1?sorted.at(-1)!.id:'');setNotice(data.scenes.length?(data.truncated?'This is a partial catalog. Narrow the date range to see all matches.':'Cloud percentages describe the whole satellite scene. Local visibility is checked during comparison.'):'No imagery was found for this area and date range. Try a wider range.');
  });}
  function compare(){if(!session||!area||!orderedPair(scenes,before,after))return;void run('Comparing observations…',async signal=>{
    setResult(null);const job=await satelliteApi<{id:string}>('/compare',session.csrfToken,{area,start_date:start,end_date:end,before_id:before,after_id:after,intent,question,
      ...(plan?.state==='ready'?{window_start:plan.window_start,window_end:plan.window_end}:{})},signal);
    for(let attempts=0;attempts<120;attempts++){
      await new Promise<void>((resolve,reject)=>{const abort=()=>{clearTimeout(timer);reject(new DOMException('Cancelled','AbortError'));};const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},2000);signal.addEventListener('abort',abort,{once:true});});
      const update=await satelliteApi<{status:string;result:SatelliteResult&{error?:string}}>('/jobs/'+job.id,session.csrfToken,undefined,signal);
      if(update.status==='failed'){setHistoryRevision(v=>v+1);throw new Error(update.result.error);}
      if(update.status==='complete'){setResult(update.result);setObservations(previous=>({...previous,[before]:update.result.before,[after]:update.result.after}));setActiveId(after);setHistoryRevision(v=>v+1);return;}
    }
    throw new Error('This comparison is taking longer than expected. Its job reference is '+job.id+'.');
  });}
  function loadObservation(){if(!session||!area||!activeId||observations[activeId])return;void run('Loading this acquisition…',async signal=>{
    const response=await satelliteApi<{id?:string;status:string;result?:{observation:SatelliteObservation}}>('/observation',session.csrfToken,{area,start_date:start,end_date:end,scene_id:activeId},signal);
    const save=(observation:SatelliteObservation)=>setObservations(previous=>{
      const entries=Object.entries(previous).filter(([id])=>id!==activeId).slice(-19);return {...Object.fromEntries(entries),[activeId]:observation};
    });
    if(response.status==='complete'&&response.result){save(response.result.observation);return;}
    if(!response.id)throw new Error('The imagery service did not return an observation reference.');
    for(let attempts=0;attempts<120;attempts++){
      await new Promise<void>((resolve,reject)=>{const abort=()=>{clearTimeout(timer);reject(new DOMException('Cancelled','AbortError'));};const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},1500);signal.addEventListener('abort',abort,{once:true});});
      const update=await satelliteApi<{status:string;result:{observation?:SatelliteObservation;error?:string}}>('/jobs/'+response.id,session.csrfToken,undefined,signal);
      if(update.status==='failed')throw new Error(update.result.error||'The observation could not be loaded.');
      if(update.status==='complete'&&update.result.observation){save(update.result.observation);return;}
    }
    throw new Error('The observation is taking longer than expected. Its reference is '+response.id+'.');
  });}
  function openSaved(id:string){if(!session)return;void run('Opening saved investigation…',async signal=>{
    const job=await satelliteApi<{status:string;request:SatelliteRequest|null;result:SatelliteResult}>('/jobs/'+id,session.csrfToken,undefined,signal);
    if(job.status!=='complete')throw new Error('This investigation has not completed.');
    clearResults();setPlan(null);
    if(job.request){const r=job.request;setArea(r.area);setCoords(r.area.bbox.map(String));setStart(r.start_date);setEnd(r.end_date);setIntent(r.intent);setQuestion(r.question||'');}else{setArea(null);setCoords(['','','','']);}
    setResult(job.result);
    const pair=[job.result.before,job.result.after];setObservations(Object.fromEntries(pair.map(o=>[o.catalog_scene_id,o])));
    setScenes(orderedScenes(pair.map(o=>({id:o.catalog_scene_id,acquired_at:o.acquired_at[0],scene_cloud_percent:null}))));
    setBefore(pair[0].catalog_scene_id);setAfter(pair[1].catalog_scene_id);setActiveId(pair[1].catalog_scene_id);
    requestAnimationFrame(()=>document.querySelector('.satellite-results')?.scrollIntoView({behavior:'smooth',block:'start'}));
  });}
  const centre=area?[(area.bbox[0]+area.bbox[2])/2,(area.bbox[1]+area.bbox[3])/2]:[74,15.4];
  return <main className="satellite-page shell"><header className="satellite-heading"><h1>Explore Goa through time</h1><p>Find a place. Draw an area. Explore what changed.</p></header>
    
    {authChecked&&!session&&<p className="satellite-access">The map and source links are open to explore. <Link to="/admin">Sign in to the team workspace</Link> to retrieve and compare imagery.</p>}
    {session&&readiness&&!readiness.imagery_ready&&<p role="status">New imagery retrieval is unavailable until Copernicus is connected. You can explore the map and open saved results.</p>}
    
    <section className="satellite-workbench" aria-label="Map and timeline">
      <SatelliteMap area={area} onArea={chooseArea} disabled={!!busy} observation={observations[activeId]} candidates={result&&[result.before.catalog_scene_id,result.after.catalog_scene_id].includes(activeId)?result.intent==='surface_water'?result.evidence.water_candidates:result.intent==='canopy_loss'?result.evidence.candidates:undefined:undefined}/>
      {result&&[result.before.catalog_scene_id,result.after.catalog_scene_id].includes(activeId)&&<p className="satellite-note">Any change outlines compare {dateLabel(result.before.acquired_at[0])} with {dateLabel(result.after.acquired_at[0])}. They are exploratory candidates.</p>}
      {!scenes.length&&<p className="satellite-note">Select an area, then find observations for the dates below. Satellite imagery will appear over this map.</p>}
      <SatelliteTimeline scenes={scenes} activeId={activeId} onSelect={setActiveId} observations={observations} onLoad={loadObservation} busy={!!busy} canLoad={!!session&&!!readiness?.imagery_ready} before={before} after={after} onBefore={id=>{setBefore(id);setResult(null);}} onAfter={id=>{setAfter(id);setResult(null);}}/>
    </section>
    <details className="satellite-limitations"><summary>About the imagery and location search</summary><p className="satellite-qualification">Experimental area investigations. Clear imagery can lag behind today, especially during monsoon. Small litter and individual trees may not be resolvable; construction legality requires planning records.</p><p className="satellite-note">Place search sends only your submitted search terms to Photon. Avoid private information. Your location is requested only when you press the location button and is not saved. Map tiles are requested for the area you view.</p>{session&&readiness&&!(readiness.classification_ready??readiness.decisions_ready)&&<p>Image decisions are awaiting server configuration. Dated imagery and numeric comparisons are available.</p>}</details>
    {busy&&<p role="status" aria-live="polite">{busy}</p>}{error&&<p className="satellite-error" role="alert">{error}</p>}
    <form className="satellite-question" onSubmit={ask}><Textarea label="Ask about this area" value={question} maxLength={1000} rows={3} onChange={e=>setQuestion(e.target.value)} placeholder="Has tree canopy disappeared here in the last 10 days?"/>
      <Button type="submit" disabled={!session||!!busy||!readiness?.planner_ready||question.trim().length<3}>Prepare investigation</Button>
      {session&&readiness&&!readiness.planner_ready&&<p className="satellite-note">Question interpretation is unavailable until configured. Choose an area, dates and investigation topic below to compare imagery.</p>}</form>
    {plan&&<div className="satellite-plan" role="status"><p>{plan.message}</p>{plan.window_start&&<p>Requested period: {dateLabel(plan.window_start)} to {dateLabel(plan.window_end!)}.</p>}{plan.place_name&&<p>Requested place: {plan.place_name}. Select it on the map, then ask about “this area”.</p>}{plan.warnings?.map(w=><p key={w}>{w}</p>)}</div>}
    <fieldset className="satellite-controls" disabled={!!busy}><legend>Choose your area and observations</legend>
      <details className="satellite-coordinate-details"><summary>Set area by coordinates</summary><div className="satellite-coordinates">{['West longitude','South latitude','East longitude','North latitude'].map((label,i)=><Input key={label} label={label} type="number" step="0.00001" value={coords[i]} onChange={e=>setCoords(v=>v.map((old,j)=>i===j?e.target.value:old))}/>)}</div>
      <Button type="button" variant="secondary" onClick={()=>{if(coords.some(s=>!s.trim())){setError('Enter all four area coordinates.');return;}chooseArea({bbox:coords.map(Number) as SatelliteArea['bbox']});}}>Use these coordinates</Button></details>
      <div className="satellite-dates"><Input label="Search from" type="date" value={start} max={end} min="2017-03-28" onChange={e=>{setStart(e.target.value);setPlan(null);clearResults();}}/><Input label="Search until" type="date" value={end} min={start} max={today()} onChange={e=>{setEnd(e.target.value);setPlan(null);clearResults();}}/>
        <label>Investigate<select value={intent} onChange={e=>{setIntent(e.target.value as SatelliteIntent);setResult(null);setPlan(null);}}>{Object.entries(intents).map(([v,l])=><option value={v} key={v}>{l}</option>)}</select></label></div>
      <Button type="button" disabled={!session||!readiness?.imagery_ready||!area||!start||!end||!!busy} onClick={findScenes}>Find observations</Button>
      {notice&&<p role="status">{notice}</p>}
      {catalogFreshness?.latest_acquired_at&&<p className="satellite-freshness">Latest acquisition found in this search: <strong>{dateLabel(catalogFreshness.latest_acquired_at)}</strong>. Catalog checked {dateLabel(catalogFreshness.searched_at)}. Availability does not guarantee clear local visibility.</p>}
      {!!scenes.length&&<><div className="satellite-dates">{(['Before','After'] as const).map(label=><label key={label}>{label} observation<select value={label==='Before'?before:after} onChange={e=>{(label==='Before'?setBefore:setAfter)(e.target.value);setResult(null);}}><option value="">Choose an acquisition</option>{scenes.map(s=><option key={s.id} value={s.id}>{dateLabel(s.acquired_at)} · scene cloud {s.scene_cloud_percent===null?'unknown':Math.round(s.scene_cloud_percent)+'%'}</option>)}</select></label>)}</div><Button type="button" onClick={compare} disabled={!session||!area||!readiness?.imagery_ready||!orderedPair(scenes,before,after)}>Analyse this pair</Button>{before&&after&&!orderedPair(scenes,before,after)&&<p role="status">Choose an after acquisition later than the before acquisition.</p>}</>}
    </fieldset>
    {result&&<section className="satellite-results"><h2>{result.summary?.headline??'What these observations show'}</h2>
      {result.recorded_example&&<p className="satellite-recorded"><strong>Recorded real comparison.</strong> Retrieved {dateLabel(result.recorded_example.retrieved_at)}. {result.recorded_example.note}{' '}<a href={result.recorded_example.source_url} target="_blank" rel="noreferrer">View the original verification</a></p>}
      <ImageDecisions result={result}/>
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
    {session&&<SatelliteHistory csrfToken={session.csrfToken} revision={historyRevision} busy={!!busy} onOpen={openSaved}/>}
    <section className="satellite-context"><h2>Understand the local context</h2><p>Amche Atlas brings together Goa’s survey plots, forests, wetlands, water bodies and planning maps. Check each layer’s date and source alongside the satellite observations.</p>
      <a href={`https://amche.in/?atlas=goa#14/${centre[1].toFixed(5)}/${centre[0].toFixed(5)}`} target="_blank" rel="noreferrer">Open this location in Amche Atlas ↗</a>
      <p>Water-body and private-forest records from Amche are available in the map’s context controls. These reference layers are not automatically joined to findings; they do not establish a change’s cause or legality.</p>
    </section>
  </main>;
}
