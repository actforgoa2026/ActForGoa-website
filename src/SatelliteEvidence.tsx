import {useEffect, useId, useRef, useState, type FormEvent, type ReactNode} from 'react';
import {Button} from './components/arc/button/button';
import {Checkbox} from './components/ui/checkbox';
import {Textarea} from './components/arc/textarea/textarea';
import {satelliteApi, type SatelliteArea, type SatelliteContext, type SatelliteIntent, type SatelliteResult} from './satellite-api';
import {observationDate, satelliteIntents} from './SatelliteHistory';
import './satellite-evidence.css';

type EvidenceCard = {
  id: string; created_at: string; intent: SatelliteIntent; question: string;
  spatial: {relation: 'same_area'|'partial_overlap'; query_fraction: number; comparison_fraction: number; intersection_area_m2: number};
  temporal: {relation: 'within_window'|'overlaps_window'; before: string; after: string};
  clarity: {state: string; common_usable_fraction: number|null};
  classification: {state: string; provider?: string; model?: string; calibration?:'not_calibrated'; confidence_threshold?:null;
    answers?: Record<string, {choice: string; confidence?:number; probabilities?:{value:string;probability:number}[]; probabilities_complete?:boolean; score_validation?:'invalid_saved_scores_omitted';reason?:'provider_refused'}>};
  provenance?: {before:{catalog_scene_id:string;acquired_at:string[]};after:{catalog_scene_id:string;acquired_at:string[]}};
  canopy_presence?: SatelliteResult['canopy_presence']|null;
  summary: SatelliteResult['summary']|null;
  measurements: {metrics: Record<string,{before_median:number|null;after_median:number|null;median_paired_change:number|null}>; vegetation_candidate_count: number|null; candidates_truncated?:boolean; water_change?: SatelliteResult['evidence']['water_change']; scope_note: string};
  citation: {job_id: string; route: string; label: string};
};
type AmcheMatch = {
  id: string; source_record_id: string; label: string; village: string; taluka: string; survey: string; subdivision: string;
  geometry_type: string; relation: 'area_overlap'|'boundary_touch'|'location_only'; intersection_area_m2: number|null;
  query_fraction: number|null; match_accuracy: string; partial_plot_match: string;
};
type AmcheLayer = {
  id: string; title: string; state: 'available'|'unavailable'; match_state: 'matches'|'no_matches'|'unknown';
  source_url: string; source_label: string; dataset_url: string; snapshot_sha256: string;
  reference_date: string; effective_date: null; fetched_at: string|null; coverage: 'not_established';
  matched_records?: number; polygon_match_count?: number; point_match_count?: number; boundary_touch_count?: number;
  union_overlap_m2?: number; query_fraction?: number; truncated?: boolean; matches?: AmcheMatch[]; note: string;
};
type AmcheContext = {
  state: 'available'|'partial'|'no_matches'|'unavailable'|'not_configured'; message: string; checked_at: string;
  coverage: 'not_established'; matched_records: number; layers: AmcheLayer[];
};
export type SatelliteEvidenceResponse = {
  state: 'available'|'no_matches';
  query: {area: SatelliteArea; start_date: string; end_date: string; intent?: SatelliteIntent; question: string};
  headline: string; cards: EvidenceCard[]; gaps: {code: string; message: string}[];
  scanned_count: number; matched_count: number; scan_truncated: boolean; results_truncated: boolean;
  retention_days: number; method: 'saved-evidence-v1'; library_context?: SatelliteContext; amche_context?: AmcheContext;
};

const fraction = (value: number|null|undefined) => typeof value === 'number' && Number.isFinite(value)
  ? value > 0 && value < 0.01 ? '<1%' : `${Math.round(value*100)}%` : 'Not recorded';
const date = (value: string) => Number.isFinite(Date.parse(value)) ? observationDate(value) : 'Date not recorded';
const day = (value: string) => /^\d{4}-\d{2}-\d{2}$/.test(value) && Number.isFinite(Date.parse(value))
  ? new Date(value+'T00:00:00+05:30').toLocaleDateString('en-IN', {timeZone:'Asia/Kolkata', dateStyle:'medium'}) : 'Choose a date';
const choice = (value: string) => value.replaceAll('_', ' ');
const measuredNumber = (value: unknown) => typeof value==='number'&&Number.isFinite(value)?value.toLocaleString('en-IN'):'Not recorded';
function sourceUrl(value: string): string|undefined {
  try {const url=new URL(value);return ['https:','http:'].includes(url.protocol)&&!url.username&&!url.password ? url.href : undefined;}
  catch {return undefined;}
}
function SourceLink({url, children}: {url: string; children: ReactNode}) {
  const href=sourceUrl(url);
  return href ? <a href={href} target="_blank" rel="noreferrer">{children}</a> : <span>{children}</span>;
}

function SavedEvidence({card,index,onOpen,disabled}: {card:EvidenceCard;index:number;onOpen:(id:string)=>void;disabled:boolean}) {
  const answers=Object.entries(card.classification.answers??{});
  const scores=answers.filter(([,answer])=>typeof answer.confidence==='number'||answer.probabilities?.length||answer.score_validation||answer.reason);
  const usable=card.clarity.state==='observable';
  const statements=Array.isArray(card.summary?.statements)?card.summary.statements:[];
  return <article className="satellite-evidence-card">
    <h4>[{index+1}] {card.summary?.headline||satelliteIntents[card.intent]||'Saved comparison'}</h4>
    <p className="satellite-evidence-dates">{date(card.temporal.before)} → {date(card.temporal.after)}</p>
    <p>{card.spatial.relation==='same_area' ? 'Same selected area.' : `Overlapping comparison: its footprint covers ${fraction(card.spatial.query_fraction)} of your selected area.`}{' '}
      {card.temporal.relation==='overlaps_window' ? 'The observation interval extends outside your selected period; a possible change may fall outside it.' : 'Both observations fall within your selected period.'}</p>
    <p className="satellite-evidence-scope">{card.measurements.scope_note||'Measurements describe the complete original comparison footprint.'}{card.spatial.relation==='partial_overlap'?' They have not been recalculated for the overlapping part of your selection.':''}</p>
    <dl className="satellite-evidence-facts"><div><dt>Usable in both observations</dt><dd>{fraction(card.clarity.common_usable_fraction)}</dd></div><div><dt>Evidence quality</dt><dd>{usable?'Clear enough for an exploratory comparison':card.clarity.state==='insufficient_clear_coverage'?'Inconclusive: insufficient clear coverage':'Clear coverage not established'}</dd></div></dl>
    {!usable&&<p>This comparison cannot establish whether the area changed. Cloud, shadow or missing pixels can hide a change.</p>}
    {!!statements.length&&<div className="satellite-evidence-statements">{statements.map((statement,i)=><p key={i}>{statement.text}</p>)}</div>}
    <details><summary>Measurements and saved image decisions</summary>
      {usable&&card.intent==='canopy_loss'&&typeof card.measurements.vegetation_candidate_count==='number'&&<p>{card.measurements.candidates_truncated?'At least ':''}{card.measurements.vegetation_candidate_count} possible vegetation-loss patches met the saved comparison’s exploratory thresholds.{card.measurements.candidates_truncated?' The saved patch list is incomplete.':''} This is not a count of trees; zero candidates does not establish that no trees were removed.</p>}
      {usable&&card.intent==='surface_water'&&card.measurements.water_change&&<p>Water-classified area gained: {measuredNumber(card.measurements.water_change.gained_area_m2)} m². Area lost: {measuredNumber(card.measurements.water_change.lost_area_m2)} m². Tides, seasonality and classification uncertainty require review.</p>}
      {Object.keys(card.measurements.metrics).length>0&&<div className="satellite-evidence-table"><table><caption>Original comparison’s spectral measurements</caption><thead><tr><th>Index</th><th>Before median</th><th>After median</th><th>Paired change</th></tr></thead><tbody>{Object.entries(card.measurements.metrics).map(([name,metric])=><tr key={name}><th scope="row">{name.toUpperCase()}</th><td>{metric.before_median??'Unavailable'}</td><td>{metric.after_median??'Unavailable'}</td><td>{metric.median_paired_change??'Unavailable'}</td></tr>)}</tbody></table></div>}
      {answers.length ? <><p>Saved image decisions{card.classification.provider?` · ${card.classification.provider}`:''}{card.classification.model?` · ${card.classification.model}`:''}. These are the earlier comparison’s model proposals, not field-validated findings. This search did not run a model.</p>
        <dl className="satellite-evidence-decisions">{answers.map(([name,answer])=><div key={name}><dt>{choice(name)}</dt><dd>{choice(answer.choice)}</dd></div>)}</dl>
        {!!scores.length&&<details><summary>Provider scores</summary><p>Provider scores are not validated accuracy. No calibrated cutoff has been established for these findings.</p>
          {scores.map(([name,answer])=><div className="satellite-evidence-score" key={name}><h5>{choice(name)}</h5>
            {typeof answer.confidence==='number'&&<p>Provider confidence score: {answer.confidence} (0–1).</p>}
            {!!answer.probabilities?.length&&<><dl className="satellite-evidence-decisions">{answer.probabilities.map(item=><div key={item.value}><dt>{choice(item.value)}</dt><dd>{item.probability} provider probability</dd></div>)}</dl>{answer.probabilities_complete===false&&<p>Only part of the choice distribution was retained.</p>}</>}
            {answer.score_validation&&<p>Invalid saved score metadata was omitted.</p>}
            {answer.reason==='provider_refused'&&<p>The provider declined this decision. It remains uncertain.</p>}
          </div>)}
        </details>}
        {card.canopy_presence?.scope&&<p>{card.canopy_presence.scope}</p>}</> : <p>No image decisions are available in this saved comparison. Measured evidence and model decisions are separate.</p>}
      {card.question&&<p>Original investigation question: {card.question}</p>}
      {card.provenance&&<dl className="satellite-evidence-decisions">{(['before','after'] as const).map(which=><div key={which}><dt>{which==='before'?'Before':'After'} acquisition source</dt><dd>{card.provenance![which].catalog_scene_id||'Not recorded'}</dd></div>)}</dl>}
      <p className="satellite-evidence-muted">Saved {date(card.created_at)}. Acquisition dates above are not exact dates of a change.</p>
    </details>
    <Button type="button" variant="secondary" disabled={disabled} onClick={()=>onOpen(card.citation.job_id)}>Open cited comparison {index+1}</Button>
  </article>;
}

function AmcheEvidence({context}: {context:AmcheContext}) {
  return <section className="satellite-evidence-context" aria-label="Amche reference evidence"><h3>Amche reference records</h3><p>{context.message}</p>
    <p className="satellite-evidence-muted">These source collections have their own dates. A record’s presence does not establish current conditions or historical conditions during your selected period. Coverage is not established.</p>
    {context.layers.map(layer=><article key={layer.id}>
      <h4><SourceLink url={layer.dataset_url}>{layer.title}</SourceLink></h4>
      <p>{layer.reference_date} · <SourceLink url={layer.source_url}>{layer.source_label}</SourceLink></p>
      {layer.state==='unavailable' ? <p>This source could not be checked. Its missing response is not evidence that no records exist here.</p> : layer.match_state==='no_matches' ? <p>No matching records were found in this source snapshot. Unmapped places and incomplete boundaries may still exist.</p> : <p>{layer.matched_records??layer.matches?.length??0} reference record{(layer.matched_records??layer.matches?.length)!==1?'s':''} intersect or locate within the selected area. These are record counts, not counts of physical forests or water bodies.</p>}
      {!!layer.matches?.length&&<ul>{layer.matches.map(match=><li key={match.id}><strong>{match.label||'Mapped record'}</strong>
        <p>{match.relation==='location_only'?'Point location only; no mapped extent is established.':match.relation==='boundary_touch'?'Touches the selection boundary; no overlapping area is established.':`Mapped polygon intersects the selection${match.query_fraction!==null?` across ${fraction(match.query_fraction)} of it`:''}.`}{match.partial_plot_match?` Partial plot reference: ${match.partial_plot_match}.`:''}{match.match_accuracy?` Source match note: ${match.match_accuracy}.`:''}</p>
        {match.source_record_id&&<small>Source record {match.source_record_id}</small>}
      </li>)}</ul>}
      {layer.truncated&&<p>Only part of the matching record list is shown.</p>}
      {layer.note&&<p>{layer.note}</p>}
      {layer.fetched_at&&<p className="satellite-evidence-muted">Source snapshot fetched {date(layer.fetched_at)}.</p>}
    </article>)}
  </section>;
}

function LibraryEvidence({context}: {context:SatelliteContext}) {
  return <section className="satellite-evidence-context" aria-label="Ecology background evidence"><h3>Ecology background</h3><p>{context.message}</p>
    {context.state==='no_matches'&&<p>No matching passages were returned. This does not establish that no relevant research exists.</p>}
    <p className="satellite-evidence-muted">These passages provide background. They do not independently verify a change at your selected location or its cause.</p>
    {context.sources.map((source,index)=><article key={source.id+'-'+index}><h4><SourceLink url={source.reader_url}>[E{index+1}] {source.title}</SourceLink></h4>
      <p className="satellite-evidence-excerpt">{source.text}{source.excerpt_truncated?'…':''}</p><p>{source.label}</p>
      {source.warning&&<p>{source.warning}</p>}
      <p><SourceLink url={source.url}>Original source ↗</SourceLink>{source.retrieved_at?` · Source retrieved ${source.retrieved_at}`:''}</p>
    </article>)}
  </section>;
}

type Props = {
  csrfToken:string; area:SatelliteArea|null; startDate:string; endDate:string; intent:SatelliteIntent;
  question:string; onQuestion:(question:string)=>void; onOpen:(id:string)=>void; busy:boolean; revision:number;
};

export function SatelliteEvidence({csrfToken,area,startDate,endDate,intent,question,onQuestion,onOpen,busy,revision}:Props) {
  const id=useId(), controller=useRef<AbortController|null>(null);
  const [includeContext,setIncludeContext]=useState(true),[pending,setPending]=useState(false),[elapsed,setElapsed]=useState(0);
  const [error,setError]=useState(''),[answer,setAnswer]=useState<{key:string;token:string;data:SatelliteEvidenceResponse}|null>(null);
  const key=JSON.stringify([area?.bbox??null,startDate,endDate,intent,question,includeContext,revision]);
  const currentKey=useRef({key,token:csrfToken});currentKey.current={key,token:csrfToken};
  const result=answer?.key===key&&answer.token===csrfToken?answer.data:null;
  useEffect(()=>{controller.current?.abort();controller.current=null;setPending(false);setAnswer(null);setError('');},[key,csrfToken]);
  useEffect(()=>()=>controller.current?.abort(),[]);
  useEffect(()=>{if(!pending)return;const started=Date.now();setElapsed(0);const timer=setInterval(()=>setElapsed(Math.floor((Date.now()-started)/1000)),1000);return()=>clearInterval(timer);},[pending]);
  const invalidDates=!/^\d{4}-\d{2}-\d{2}$/.test(startDate)||!/^\d{4}-\d{2}-\d{2}$/.test(endDate)||!Number.isFinite(Date.parse(startDate))||!Number.isFinite(Date.parse(endDate))||startDate>endDate;
  const reason=!csrfToken?'Sign in to search your saved evidence.':!area?'Select an area on the map first.':invalidDates?'Choose an ordered start and end date.':question.trim().length<3?'Enter a question or a few words about what you want to investigate.':busy?'Wait for the current imagery operation to finish.':'';
  async function search(event:FormEvent) {
    event.preventDefault();if(reason||controller.current)return;
    const abort=new AbortController(),submittedKey=key;controller.current=abort;setPending(true);setAnswer(null);setError('');
    try {
      const data=await satelliteApi<SatelliteEvidenceResponse>('/evidence',csrfToken,{area,start_date:startDate,end_date:endDate,intent,question:question.trim(),limit:8,include_context:includeContext},abort.signal);
      if(!abort.signal.aborted&&currentKey.current.key===submittedKey&&currentKey.current.token===csrfToken)setAnswer({key:submittedKey,token:csrfToken,data});
    } catch(error) {if(!abort.signal.aborted&&currentKey.current.key===submittedKey&&currentKey.current.token===csrfToken)setError(error instanceof Error?error.message:'Evidence search could not complete. Please try again.');}
    finally {if(controller.current===abort){controller.current=null;setPending(false);}}
  }
  function cancel(){controller.current?.abort();controller.current=null;setPending(false);}
  return <section className="satellite-evidence" aria-labelledby={id+'-heading'}>
    <h2 id={id+'-heading'}>What evidence do we have for this area?</h2>
    <p>Search your saved satellite comparisons by place, period and question. The answer lists measured and saved evidence; it does not generate an AI interpretation or retrieve new satellite imagery.</p>
    <div className="satellite-evidence-query-scope"><p><strong>{satelliteIntents[intent]}</strong> · {day(startDate)} to {day(endDate)}</p>
      <p>{area?`Selected bounds: ${area.bbox.map(n=>n.toFixed(5)).join(', ')} (west, south, east, north).`:'No area selected.'}</p></div>
    <form onSubmit={event=>void search(event)}>
      <Textarea label="Question for this area and period" value={question} maxLength={1000} rows={3} onChange={event=>onQuestion(event.target.value)} placeholder="What evidence do we have of water or canopy changes here?" description="Your words rank relevant saved findings. They do not become a new model-generated conclusion."/>
      <label className="satellite-evidence-context-toggle" htmlFor={id+'-context'}><Checkbox id={id+'-context'} checked={includeContext} onCheckedChange={value=>setIncludeContext(value===true)}/><span>Include Amche and ecology context</span></label>
      <p className="satellite-evidence-muted">Reference context is read-only and has separate source dates. It does not run AI analysis.</p>
      <div className="satellite-evidence-actions"><Button type="submit" loading={pending} disabled={!!reason} aria-describedby={reason?id+'-reason':undefined}>Search evidence for this area</Button>{pending&&<Button type="button" variant="ghost" onClick={cancel}>Cancel search</Button>}</div>
      {reason&&<p id={id+'-reason'}>{reason}</p>}
    </form>
    {pending&&<p role="status">Searching saved evidence{includeContext?' and reference sources':''}… {elapsed}s elapsed.</p>}
    {error&&<p role="alert" className="satellite-evidence-error">{error}</p>}
    {result&&<div className="satellite-evidence-response">
      <h3>{result.headline}</h3>
      {result.state==='no_matches'&&<p>{result.scan_truncated?'No matching comparison was found in the records checked. Older retained records were not checked.':'No saved comparison matched this selected area, period and topic.'} This is a gap in saved evidence, not a finding that nothing changed. Load observations and analyse a pair to create an investigation, or adjust the area and dates.</p>}
      {!!result.gaps.length&&<ul className="satellite-evidence-gaps">{result.gaps.map((gap,index)=><li key={gap.code+'-'+index}>{gap.message}</li>)}</ul>}
      {!!result.cards.length&&<><p>Showing {result.cards.length} of {result.matched_count} matching saved comparison{result.matched_count!==1?'s':''}. Your question ranks these records; the selected area, period and topic determine their scope.</p>
        <div className="satellite-evidence-cards">{result.cards.map((card,index)=><SavedEvidence key={card.id} card={card} index={index} onOpen={onOpen} disabled={busy||pending}/>)}</div></>}
      {(result.scan_truncated||result.results_truncated)&&<p>This is a partial result list. Narrow the period or topic to search a more focused set of records.</p>}
      <p className="satellite-evidence-muted">Searched {result.scanned_count} retained comparisons from your account. Saved comparisons are retained for {result.retention_days} days; this is not statewide or continuous monitoring coverage.</p>
      {result.amche_context&&<AmcheEvidence context={result.amche_context}/>}
      {result.library_context&&<LibraryEvidence context={result.library_context}/>}
    </div>}
  </section>;
}
