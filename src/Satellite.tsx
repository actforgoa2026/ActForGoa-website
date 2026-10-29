import {useEffect,useRef,useState,type FormEvent} from 'react';
import {Link} from 'react-router-dom';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import {adminApi,AdminApiError,type AdminSession} from './admin-api';
import {satelliteApi,SatelliteApiError,type SatelliteArea,type SatelliteScene,type SatellitePlan,type SatelliteResult,type SatelliteIntent,type SatelliteRequest,type SatelliteObservation} from './satellite-api';
import {SatelliteHistory,satelliteIntents as intents,observationDate as dateLabel} from './SatelliteHistory';
import {SatelliteContext} from './SatelliteContext';
import {SatelliteMap} from './SatelliteMap';
import {SatelliteEnvironment} from './SatelliteEnvironment';
import {SatelliteEvidence} from './SatelliteEvidence';
import {pollSatelliteJob,pendingJobKey,validJobId,sameImageryContext,cacheObservations} from './satellite-jobs';
import {SatelliteTimeline} from './SatelliteTimeline';
import {SatelliteDatePicker} from './SatelliteDatePicker';
import type {SatellitePreview} from './satellite-api';
import {areaError,orderedPair,orderedScenes,suggestedPair} from './satellite-timeline';
import './satellite.css';
import '@fontsource-variable/figtree';
import './satellite-layout.css';

const percent=(n:number)=>`${Math.round(n*100)}%`;
const today=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
type Readiness={imagery_ready:boolean;imagery_provider?:string;google_maps_ready?:boolean;planner_ready:boolean;decisions_ready:boolean;classification_ready?:boolean;classification_provider?:string|null};
type SavedJob={id:string;status:string;request:(SatelliteRequest&{kind?:string;scene_id?:string})|null;result:(SatelliteResult&{observation?:SatelliteObservation;error?:string})|null};
const evidenceLabels={before:'Before image',after:'After image',coverage:'Visibility',spectral:'Numeric evidence',assessment:'Image decisions'};
const decisionLabel=(value:string)=>value==='yes'?'Yes':value==='no'?'No':'Uncertain';

function ImageDecisions({result}:{result:SatelliteResult}){
  return <div id="satellite-assessment">
    {result.canopy_presence&&(!result.intent||result.intent==='canopy_loss')&&<><h3>Was tree canopy visible in the same area?</h3><p>Image assessment proposals: yes, no or uncertain. Presence on both dates does not establish that the same trees survived.</p><dl className="satellite-presence"><div><dt>Before · {dateLabel(result.before.acquired_at[0])}</dt><dd>{decisionLabel(result.canopy_presence.before)}</dd></div><div><dt>After · {dateLabel(result.after.acquired_at[0])}</dt><dd>{decisionLabel(result.canopy_presence.after)}</dd></div></dl><p className="satellite-note">{result.canopy_presence.scope}</p></>}
    {result.classification.provider&&<p className="satellite-note">Image decisions: {result.classification.provider==='openai-decisions'?'OpenAI Decisions':'Anthropic'} · {result.classification.model}. {result.classification.validation}</p>}
    {result.classification.scope&&<p className="satellite-note">{result.classification.scope.description} Target: <code>{result.classification.scope.target_id||'Unidentified older footprint'}</code>.</p>}
    {result.classification.message&&<p>{result.classification.message}</p>}
    {!!Object.keys(result.classification.answers).length&&<details><summary>Image decision details</summary><dl className="satellite-assessments">{Object.entries(result.classification.answers).map(([name,a])=><div key={name}><dt>{name.replaceAll('_',' ')}</dt><dd>{a.choice.replaceAll('_',' ')}{typeof a.confidence==='number'&&<span className="satellite-score">Provider confidence: {percent(a.confidence)} (uncalibrated)</span>}{a.probabilities&&<span className="satellite-score">Provider scores: {a.probabilities.map(p=>`${p.value.replaceAll('_',' ')} ${percent(p.probability)}`).join(' · ')}. These are not validated accuracy.</span>}</dd></div>)}</dl></details>}
  </div>;
}

export default function Satellite(){
  const [session,setSession]=useState<AdminSession|null>(null),[authChecked,setAuthChecked]=useState(false),[accessError,setAccessError]=useState(''),[accessRevision,setAccessRevision]=useState(0),[pendingJob,setPendingJob]=useState('');
  const [area,setArea]=useState<SatelliteArea|null>(null),[coords,setCoords]=useState(['73.82','15.48','73.83','15.49']);
  const [question,setQuestion]=useState('');
  const [start,setStart]=useState(()=>{const d=new Date();d.setDate(d.getDate()-40);return d.toISOString().slice(0,10);}),[end,setEnd]=useState(today);
  const [intent,setIntent]=useState<SatelliteIntent>('canopy_loss'),[plan,setPlan]=useState<SatellitePlan|null>(null);
  const [scenes,setScenes]=useState<SatelliteScene[]>([]),[before,setBefore]=useState(''),[after,setAfter]=useState('');
  const [activeId,setActiveId]=useState(''),[observations,setObservations]=useState<Record<string,SatelliteObservation>>({});
  const [result,setResult]=useState<SatelliteResult|null>(null),[busy,setBusy]=useState(''),[error,setError]=useState(''),[notice,setNotice]=useState('');
  const [historyRevision,setHistoryRevision]=useState(0),[catalogFreshness,setCatalogFreshness]=useState<{searched_at:string;latest_acquired_at:string|null}|null>(null);
  const [readiness,setReadiness]=useState<Readiness|null>(null);
  const [preview,setPreview]=useState<SatellitePreview|null>(null),[previewBusy,setPreviewBusy]=useState(false),[previewError,setPreviewError]=useState('');
  const [previewPeriod,setPreviewPeriod]=useState(()=>({start,end,revision:0}));
  useEffect(()=>{
    if(!session||!readiness?.imagery_ready||readiness.imagery_provider!=='earth-engine'){setPreview(null);return;}
    const abort=new AbortController();setPreviewBusy(true);setPreviewError('');
    satelliteApi<SatellitePreview>('/preview',session.csrfToken,{start_date:previewPeriod.start,end_date:previewPeriod.end},abort.signal)
      .then(value=>{if(!abort.signal.aborted)setPreview(value);})
      .catch(error=>{if(!abort.signal.aborted)setPreviewError(error instanceof Error?error.message:'Earth Engine could not load.');})
      .finally(()=>{if(!abort.signal.aborted)setPreviewBusy(false);});
    return()=>abort.abort();
  },[session?.user.id,session?.csrfToken,readiness?.imagery_ready,readiness?.imagery_provider,previewPeriod]);
  function updateOverview(){setPreviewPeriod(previous=>({start,end,revision:previous.revision+1}));}

  const controller=useRef<AbortController|null>(null),lock=useRef(false),verifiedActor=useRef<string|null>(null);
  function clearPrivateState(){controller.current?.abort();lock.current=false;setBusy('');clearResults();setPlan(null);setQuestion('');setArea(null);setCoords(['','','','']);setPendingJob('');}
  useEffect(()=>{
    const abort=new AbortController();setAuthChecked(false);setAccessError('');if(verifiedActor.current===null)setReadiness(null);
    async function check(){
      try {
        const account=await adminApi<AdminSession>('/api/admin/session',{signal:abort.signal});
        if(abort.signal.aborted)return;
        if(verifiedActor.current!==null&&verifiedActor.current!==account.user.id)clearPrivateState();
        verifiedActor.current=account.user.id;setSession(account);
        try {const id=sessionStorage.getItem(pendingJobKey(account.user.id));setPendingJob(validJobId(id)?id:'');}catch{/* Storage may be unavailable; in-memory recovery still works. */}
        const status=await satelliteApi<Readiness>('/status',account.csrfToken,undefined,abort.signal);
        if(!abort.signal.aborted)setReadiness(status);
      }catch(e){
        if(abort.signal.aborted)return;
        if(e instanceof AdminApiError&&e.status===401){if(verifiedActor.current!==null)clearPrivateState();verifiedActor.current=null;setSession(null);setReadiness(null);setPendingJob('');}
        else setAccessError(e instanceof SatelliteApiError&&e.status===401?'The satellite service rejected access after your account was verified. Retry the check; if it persists, the service connection needs attention.':e instanceof Error?e.message:'Unable to check satellite access.');
      }finally{if(!abort.signal.aborted)setAuthChecked(true);}
    }
    void check();return()=>abort.abort();
  },[accessRevision]);
  useEffect(()=>{const recheck=()=>setAccessRevision(value=>value+1);window.addEventListener('focus',recheck);return()=>{window.removeEventListener('focus',recheck);controller.current?.abort();};},[]);
  function trackJob(id:string){
    setPendingJob(id);
    if(session)try{if(id)sessionStorage.setItem(pendingJobKey(session.user.id),id);else sessionStorage.removeItem(pendingJobKey(session.user.id));}catch{/* Retain the visible reference when storage is unavailable. */}
  }
  function clearResults(){setActiveId('');setObservations({});setScenes([]);setBefore('');setAfter('');setResult(null);setNotice('');setError('');setCatalogFreshness(null);}
  function chooseArea(value:SatelliteArea){
    if(lock.current||pendingJob)return false;const message=areaError(value.bbox);if(message){setError(message);return false;}
    setArea(value);setCoords(value.bbox.map(v=>v.toFixed(5)));setPlan(null);clearResults();
    document.querySelector<HTMLElement>('.satellite-analysis-column')?.scrollTo({top:0});
    if(session&&readiness?.imagery_ready&&!periodError&&!pendingJob)findScenes(value);
    return true;
  }
  async function run(label:string,action:(signal:AbortSignal)=>Promise<void>){
    if(lock.current)return;lock.current=true;const abort=new AbortController();controller.current=abort;setBusy(label);setError('');
    try{await action(abort.signal);}catch(e){if(!abort.signal.aborted){setError(e instanceof Error?e.message:'The investigation could not complete.');if(e instanceof SatelliteApiError&&e.status===401)setAccessRevision(value=>value+1);}}
    finally{lock.current=false;if(!abort.signal.aborted)setBusy('');}
  }
  function ask(event:FormEvent){event.preventDefault();if(!session)return;void run('Interpreting your question…',async signal=>{
    clearResults();const value=await satelliteApi<SatellitePlan>('/plan',session.csrfToken,{question,area},signal);setPlan(value);
    if(value.state==='ready'){setStart(value.catalog_start!);setEnd(value.catalog_end!);setIntent(value.intent!);}
  });}
  async function fetchObservation(selectedArea:SatelliteArea,sceneId:string,signal:AbortSignal){
    const response=await satelliteApi<{id?:string;status:string;result?:{observation:SatelliteObservation}}>('/observation',session!.csrfToken,{area:selectedArea,start_date:start,end_date:end,scene_id:sceneId},signal);
    if(response.status==='complete'&&response.result)return response.result.observation;
    if(!response.id)throw new Error('Earth Engine did not return an observation reference.');
    trackJob(response.id);
    const job=await pollSatelliteJob(response.id,(id,abort)=>satelliteApi<SavedJob>('/jobs/'+id,session!.csrfToken,undefined,abort),signal);
    if(job.status==='failed'){trackJob('');throw new Error(job.result?.error||'The Earth Engine image could not load.');}
    if(!job.result?.observation)throw new Error('The image is not ready. Check the saved job to resume.');
    trackJob('');return job.result.observation;
  }
  function findScenes(selectedArea:SatelliteArea|null=area){if(!session||!selectedArea||pendingJob||periodError)return;void run('Finding Earth Engine acquisitions for your rectangle…',async signal=>{
    clearResults();
    if(previewPeriod.start!==start||previewPeriod.end!==end)updateOverview();
    const data=await satelliteApi<{scenes:SatelliteScene[];truncated:boolean;searched_at:string;latest_acquired_at:string|null}>('/catalog',session.csrfToken,{area:selectedArea,start_date:start,end_date:end},signal);
    setCatalogFreshness(data);
    const sorted=orderedScenes(data.scenes),latest=sorted.at(-1);setScenes(sorted);setActiveId(latest?.id||'');const pair=suggestedPair(sorted);setBefore(pair?.[0]||'');setAfter(pair?.[1]||'');
    setNotice(data.scenes.length?(data.truncated?'This is a partial catalog. Narrow the date range to see all matches.':'Cloud percentages describe the whole satellite scene. Local visibility is checked during comparison.'):'No imagery was found for this area and date range. Try a wider range.');
    if(latest){
      setBusy('Loading the latest Earth Engine acquisition…');
      const observation=await fetchObservation(selectedArea,latest.id,signal);
      setObservations(previous=>cacheObservations(previous,[observation]));setActiveId(latest.id);
    }
  });}
  function restoreComparison(job:SavedJob,preserveTimeline=false){
    if(!job.result)throw new Error('This investigation has no saved result.');
    const preserve=preserveTimeline&&job.request&&sameImageryContext(job.request,{area,start_date:start,end_date:end})&&scenes.length>0;
    if(!preserve)clearResults();setPlan(null);
    if(job.request){const r=job.request;setArea(r.area);setCoords(r.area.bbox.map(String));setStart(r.start_date);setEnd(r.end_date);setIntent(r.intent);setQuestion(r.question||'');}else{setArea(null);setCoords(['','','','']);}
    const value=job.result;setResult(value);
    const pair=[value.before,value.after];setObservations(previous=>cacheObservations(preserve?previous:{},pair));
    if(!preserve)setScenes(orderedScenes(pair.map(o=>({id:o.catalog_scene_id,acquired_at:o.acquired_at[0],scene_cloud_percent:null}))));
    setBefore(pair[0].catalog_scene_id);setAfter(pair[1].catalog_scene_id);setActiveId(pair[1].catalog_scene_id);

  }
  async function finishJob(id:string,signal:AbortSignal){
    if(!session)return;
    const job=await pollSatelliteJob(id,(jobId,abort)=>satelliteApi<SavedJob>('/jobs/'+jobId,session.csrfToken,undefined,abort),signal);
    if(job.status==='failed'){trackJob('');setHistoryRevision(v=>v+1);throw new Error(job.result?.error||'The imagery job failed.');}
    if(!job.result)throw new Error('The service did not return a completed result. Check this job again.');
    if(job.result.observation){
      const observation=job.result.observation,r=job.request;
      // A resumed job can belong to a previously selected footprint. Restore its
      // request before displaying any cached image over the map.
      if(r&&!sameImageryContext(r,{area,start_date:start,end_date:end})){
        clearResults();setArea(r.area);setCoords(r.area.bbox.map(String));setStart(r.start_date);setEnd(r.end_date);setPlan(null);
        setScenes([{id:observation.catalog_scene_id,acquired_at:observation.acquired_at[0],scene_cloud_percent:null}]);setBefore(observation.catalog_scene_id);
      }else if(!scenes.some(scene=>scene.id===observation.catalog_scene_id))setScenes(previous=>orderedScenes([...previous,{id:observation.catalog_scene_id,acquired_at:observation.acquired_at[0],scene_cloud_percent:null}]));
      setObservations(previous=>cacheObservations(previous,[observation]));
      setActiveId(observation.catalog_scene_id);
    }else{restoreComparison(job,true);setHistoryRevision(v=>v+1);}
    trackJob('');
  }
  function compare(){if(!session||!area||pendingJob||!orderedPair(scenes,before,after))return;void run('Checking clear coverage, measuring change and requesting AI analysis…',async signal=>{
    setResult(null);const job=await satelliteApi<{id:string}>('/compare',session.csrfToken,{area,start_date:start,end_date:end,before_id:before,after_id:after,intent,question,
      ...(plan?.state==='ready'?{window_start:plan.window_start,window_end:plan.window_end}:{})},signal);
    trackJob(job.id);await finishJob(job.id,signal);
  });}
  function loadObservation(){if(!session||!area||pendingJob||!activeId||observations[activeId])return;void run('Loading this Earth Engine acquisition…',async signal=>{
    const observation=await fetchObservation(area,activeId,signal);setObservations(previous=>cacheObservations(previous,[observation]));
  });}
  function resumeJob(){if(!pendingJob)return;void run('Checking the existing imagery job…',async signal=>{
    try{await finishJob(pendingJob,signal);}catch(e){if(e instanceof SatelliteApiError&&e.status===404)trackJob('');throw e;}
  });}
  function openSaved(id:string){if(!session)return;void run('Opening saved investigation…',async signal=>{
    const job=await satelliteApi<SavedJob>('/jobs/'+id,session.csrfToken,undefined,signal);
    if(job.status!=='complete')throw new Error('This investigation has not completed.');
    restoreComparison(job);

  });}
  useEffect(()=>{
    if(!result)return;
    const frame=requestAnimationFrame(()=>{
      const synopsis=document.querySelector<HTMLElement>('.satellite-synopsis');
      const panel=document.querySelector<HTMLElement>('.satellite-analysis-column');
      if(!synopsis||!panel)return;
      const behavior=window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth';
      if(window.matchMedia('(min-width:1001px)').matches){
        panel.scrollTo({top:panel.scrollTop+synopsis.getBoundingClientRect().top-panel.getBoundingClientRect().top-12,behavior});
        document.querySelector('.satellite-investigation-layout')?.scrollIntoView({behavior,block:'start'});
      }else synopsis.scrollIntoView({behavior,block:'start'});
    });
    return()=>cancelAnimationFrame(frame);
  },[result]);
  const periodDays=(Date.parse(end)-Date.parse(start))/86400000;
  const periodError=!start||!end||!Number.isFinite(periodDays)||periodDays<0?'Choose an ordered start and end date.':start<'2017-03-28'||end>today()?'Choose dates from 28 March 2017 through today.':periodDays>120?'New imagery searches cover up to 120 days. Use a shorter period; saved-evidence search below can span longer periods.':'';
  const findReason=!authChecked?'Checking your access…':accessError?'Retry the access check to enable imagery.':!session?'Sign in to retrieve imagery.':!readiness?.imagery_ready?'Earth Engine imagery is not available on this server.':!area?'Select an area on the map first.':periodError;
  const centre=area?[(area.bbox[0]+area.bbox[2])/2,(area.bbox[1]+area.bbox[3])/2]:[74,15.4];
  return <main className="satellite-page shell"><header className="satellite-heading"><h1>Explore Goa with Earth Engine</h1><p>Choose a period. Draw an area to load its satellite imagery.</p></header>
    {!authChecked&&<p role="status">Checking satellite access…</p>}
    {accessError&&<div className="satellite-access" role="alert"><p>{accessError}</p><Button type="button" variant="secondary" disabled={!authChecked} onClick={()=>setAccessRevision(v=>v+1)}>Retry access check</Button><p><a href="https://satellite-app-production.up.railway.app/map">Open the standalone satellite workspace</a></p></div>}
    {session&&readiness&&!readiness.imagery_ready&&<p role="status">New imagery retrieval is unavailable until the imagery provider is connected. You can explore the map and open saved results.</p>}
    <div className="satellite-investigation-layout">
      <div className="satellite-map-column">
    <section className="satellite-workbench" aria-label="Map and timeline"><h2>1. Select your area</h2>
      <SatelliteMap area={area} onArea={chooseArea} disabled={!!busy||!!pendingJob} preview={preview} previewBusy={previewBusy} previewError={previewError} onRetryPreview={updateOverview} progress={busy||(!scenes.length?notice:'')} error={error} accessMessage={!authChecked?'Checking your access…':!session?'Sign in to load Earth Engine imagery for this area.':periodError||(!readiness?.imagery_ready?'Earth Engine is not connected.':'')} observation={observations[activeId]} candidates={result&&[result.before.catalog_scene_id,result.after.catalog_scene_id].includes(activeId)?result.intent==='surface_water'?result.evidence.water_candidates:result.intent==='canopy_loss'?result.evidence.candidates:undefined:undefined}/>
      {result&&[result.before.catalog_scene_id,result.after.catalog_scene_id].includes(activeId)&&<p className="satellite-note">Any change outlines compare {dateLabel(result.before.acquired_at[0])} with {dateLabel(result.after.acquired_at[0])}. They are exploratory candidates.</p>}
      {!scenes.length&&<p className="satellite-note">The overview combines clear Sentinel-2 pixels from the displayed period. Draw a rectangle to inspect an exact dated acquisition.</p>}
      <SatelliteTimeline scenes={scenes} activeId={activeId} onSelect={setActiveId} observations={observations} onLoad={loadObservation} busy={!!busy} canLoad={!!session&&!!readiness?.imagery_ready&&!pendingJob} before={before} after={after} onBefore={id=>{setBefore(id);setResult(null);}} onAfter={id=>{setAfter(id);setResult(null);}}/>
    </section>
      </div>
      <aside className="satellite-analysis-column" aria-label="Imagery controls and change analysis">
    <section className="satellite-period-bar" aria-label="Earth Engine imagery period">
      <SatelliteDatePicker label="Search from" value={start} max={end} min="2017-03-28" disabled={!!busy||!!pendingJob} onChange={value=>{setStart(value);setPlan(null);clearResults();}}/>
      <SatelliteDatePicker label="Search until" value={end} min={start} max={today()} disabled={!!busy||!!pendingJob} onChange={value=>{setEnd(value);setPlan(null);clearResults();}} alignEnd/>
      <Button type="button" variant="secondary" disabled={!!busy||!!pendingJob||previewBusy||!!periodError||!session||!readiness?.imagery_ready} onClick={()=>{updateOverview();if(area)findScenes();}}>Update imagery</Button>
      <p>{periodError||'Draw an area up to 25 km² to load its latest image. Choose two dates below to analyse change.'}</p>
    </section>
    {pendingJob&&<div className="satellite-job" role="status"><p>Imagery job reference: <code>{pendingJob}</code>. Checking resumes this job without submitting new imagery or AI work.</p><Button type="button" variant="secondary" disabled={!!busy||!session} onClick={resumeJob}>Check job</Button><Button type="button" variant="ghost" disabled={!!busy} onClick={()=>trackJob('')}>Stop tracking</Button><p className="satellite-note">Stopping tracking does not cancel the server job. Completed comparisons remain in your history.</p></div>}
    {busy&&<p role="status" aria-live="polite">{busy}</p>}{error&&<p className="satellite-error" role="alert">{error}</p>}
    <fieldset className="satellite-controls" disabled={!!busy||!!pendingJob}><legend>Analyse change</legend>
      <details className="satellite-coordinate-details"><summary>Set area by coordinates</summary><div className="satellite-coordinates">{['West longitude','South latitude','East longitude','North latitude'].map((label,i)=><Input key={label} label={label} type="number" step="0.00001" value={coords[i]} onChange={e=>setCoords(v=>v.map((old,j)=>i===j?e.target.value:old))}/>)}</div>
      <Button type="button" variant="secondary" onClick={()=>{if(coords.some(s=>!s.trim())){setError('Enter all four area coordinates.');return;}chooseArea({bbox:coords.map(Number) as SatelliteArea['bbox']});}}>Use these coordinates</Button></details>
      <div className="satellite-dates"><label>Investigate<select value={intent} onChange={e=>{setIntent(e.target.value as SatelliteIntent);setResult(null);setPlan(null);}}>{Object.entries(intents).map(([v,l])=><option value={v} key={v}>{l}</option>)}</select></label></div>
      {!!scenes.length&&<><div className="satellite-dates">{(['Before','After'] as const).map(label=><label key={label}>{label} observation<select value={label==='Before'?before:after} onChange={e=>{(label==='Before'?setBefore:setAfter)(e.target.value);setResult(null);}}><option value="">Choose an acquisition</option>{scenes.map(s=><option key={s.id} value={s.id}>{dateLabel(s.acquired_at)} · scene cloud {s.scene_cloud_percent===null?'unknown':Math.round(s.scene_cloud_percent)+'%'}</option>)}</select></label>)}</div><Button type="button" onClick={compare} disabled={!session||!area||!readiness?.imagery_ready||!!pendingJob||!!periodError||!orderedPair(scenes,before,after)}>Analyse change with AI</Button><Button type="button" variant="ghost" disabled={!suggestedPair(scenes)} onClick={()=>{const pair=suggestedPair(scenes);if(pair){setBefore(pair[0]);setAfter(pair[1]);setResult(null);}}}>Suggest clearer pair</Button><p className="satellite-note">Suggestions use scene cloud cover; AI runs only when the selected area is clear enough on both dates.</p>{before&&after&&!orderedPair(scenes,before,after)&&<p role="status">Choose an after acquisition later than the before acquisition.</p>}</>}
      <Button type="button" variant="ghost" onClick={()=>findScenes()} disabled={!!findReason||!!pendingJob}>Reload area imagery</Button>{findReason&&<p role="status">{findReason}</p>}

      <details className="satellite-catalog-notes"><summary>Acquisition availability</summary>{notice&&<p role="status">{notice}</p>}
      {catalogFreshness?.latest_acquired_at&&<p className="satellite-freshness">Latest acquisition found in this search: <strong>{dateLabel(catalogFreshness.latest_acquired_at)}</strong>. Catalog checked {dateLabel(catalogFreshness.searched_at)}. Availability does not guarantee clear local visibility.</p>}</details>
    </fieldset>
    {result&&<section className="satellite-results"><div className="satellite-synopsis" tabIndex={-1} aria-live="polite"><h2>Change synopsis</h2><p className="satellite-ai-status"><strong>{result.classification.state==='complete'?'AI analysis complete':result.classification.state==='skipped'?'AI skipped: visibility too low':'AI analysis unavailable'}</strong>{result.classification.model&&<span>{result.classification.model}</span>}</p><h3>{result.summary?.headline??'What these observations show'}</h3>      {result.summary&&<div className="satellite-answer" aria-label="Evidence-based interpretation">{result.summary.statements.map((statement,i)=><p key={i}>{statement.text}{' '}<span className="satellite-evidence-links">{statement.sources.map(source=><a href={'#satellite-'+source} key={source}>{evidenceLabels[source]}</a>)}</span></p>)}</div>}
{result.classification.state==='skipped'&&<p>Choose a clearer pair or an earlier, drier period. We will not infer change through cloud cover.</p>}<p className="satellite-note">This synopsis combines measured evidence and any completed AI decisions. It is not a field-verified finding.</p></div><details className="satellite-analysis-detail"><summary>Images, AI decisions and measurements</summary>
      {result.recorded_example&&<p className="satellite-recorded"><strong>Recorded real comparison.</strong> Retrieved {dateLabel(result.recorded_example.retrieved_at)}. {result.recorded_example.note}{' '}<a href={result.recorded_example.source_url} target="_blank" rel="noreferrer">View the original verification</a></p>}
      <ImageDecisions result={result}/>
      {result.freshness&&<div className="satellite-freshness"><p>Latest acquisition found in the saved search: <strong>{dateLabel(result.freshness.latest_acquired_at_in_search)}</strong>. Catalog checked {dateLabel(result.freshness.catalog_searched_at)}.</p>
        <p>{result.freshness.newer_acquisitions_in_search?`${result.freshness.newer_acquisitions_in_search} newer acquisition(s) were available than the selected after image.`:'The selected after image was the newest acquisition returned by this search.'} {result.freshness.note}{result.freshness.catalog_truncated?' This was a partial catalog; newer matches may be missing.':''}</p></div>}
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
    </details></section>}
    {!result&&<section className="satellite-synopsis satellite-analysis-empty" aria-live="polite"><h2>Change synopsis</h2><p>{busy||'Your comparison will appear here.'}</p><p className="satellite-note">{!readiness?'Checking the imagery and AI connection…':(readiness.classification_ready??readiness.decisions_ready)?'OpenAI Decisions is connected. Analyse a pair to check canopy, land, water or fire evidence.':'AI is unavailable on this server. Spectral measurements remain available.'}</p></section>}
      </aside>
    </div>
    {authChecked&&!session&&!accessError&&<p className="satellite-access">The map and source links are open to explore. <Link to="/admin">Sign in to the team workspace</Link> to retrieve and compare imagery.</p>}
    <details className="satellite-limitations"><summary>About the imagery and location search</summary><p className="satellite-qualification">Experimental area investigations. Clear imagery can lag behind today, especially during monsoon. Small litter and individual trees may not be resolvable; construction legality requires planning records.</p><p className="satellite-note">Place search sends your submitted search terms and the Goa search boundary to Google Maps. Avoid private information. Your location is requested only when you press the location button and is not saved. Map tiles are requested for the area you view.</p>{session&&readiness&&!(readiness.classification_ready??readiness.decisions_ready)&&<p>Image decisions are awaiting server configuration. Dated imagery and numeric comparisons are available.</p>}</details>
    <details className="satellite-planner"><summary>Optional: prepare dates and topic from a question</summary>    <form className="satellite-question" onSubmit={ask}><Textarea label="Describe the investigation to prepare" value={question} maxLength={1000} rows={3} onChange={e=>setQuestion(e.target.value)} placeholder="Compare canopy here during the last month"/>
      <Button type="submit" disabled={!session||!!busy||!readiness?.planner_ready||question.trim().length<3}>Prepare investigation</Button>
      {session&&readiness&&!readiness.planner_ready&&<p className="satellite-note">Question interpretation is unavailable on this server. Use the date and topic controls above to compare imagery.</p>}</form>
    {plan&&<div className="satellite-plan" role="status"><p>{plan.message}</p>{plan.window_start&&<p>Requested period: {dateLabel(plan.window_start)} to {dateLabel(plan.window_end!)}.</p>}{plan.place_name&&<p>Requested place: {plan.place_name}. Select it on the map, then ask about “this area”.</p>}{plan.warnings?.map(w=><p key={w}>{w}</p>)}</div>}
</details>
    <SatelliteEnvironment area={area} csrfToken={session?.csrfToken||''} ready={!!readiness?.google_maps_ready}/>
    <SatelliteEvidence csrfToken={session?.csrfToken||''} area={area} startDate={start} endDate={end} intent={intent} question={question} onQuestion={setQuestion} onOpen={openSaved} busy={!!busy} revision={historyRevision}/>
    {session&&<SatelliteHistory area={area} csrfToken={session.csrfToken} revision={historyRevision} busy={!!busy} onOpen={openSaved}/>}
    <section className="satellite-context"><h2>Understand the local context</h2><p>Amche Atlas brings together Goa’s survey plots, forests, wetlands, water bodies and planning maps. Check each layer’s date and source alongside the satellite observations.</p>
      <a href={`https://amche.in/?atlas=goa#14/${centre[1].toFixed(5)}/${centre[0].toFixed(5)}`} target="_blank" rel="noreferrer">Open this location in Amche Atlas ↗</a>
      <p>Water-body and private-forest records from Amche are available in the map’s context controls. Use evidence search to find reference records that intersect your selected area, with source dates and citations. Reference records do not establish a change’s cause or legality.</p>
    </section>
  </main>;
}
