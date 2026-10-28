import {useState} from 'react';
import {createRoot} from 'react-dom/client';
import '@fontsource-variable/manrope';
import beforeImage from '../reports/satellite-live-2026-10-28/before.png';
import afterImage from '../reports/satellite-live-2026-10-28/after.png';
import recorded from './satellite-preview-data.json';
import type {SatelliteIntent,SatelliteResult} from './satellite-api';
import './satellite-preview.css';

const topics:Record<SatelliteIntent,string>={canopy_loss:'Trees & vegetation',surface_water:'Water',land_change:'Development',waste:'Waste',fire:'Fire'};
const labels:Record<string,string>={ndvi:'Vegetation index',ndwi:'Water index',nbr:'Burn ratio'};
const date=(value:string,full=false)=>new Date(value).toLocaleString('en-IN',{timeZone:'Asia/Kolkata',dateStyle:'long',...(full?{timeStyle:'medium' as const}:{})})+(full?' IST':'');
const evidenceLabels={before:'Earlier image',after:'Later image',coverage:'Visibility',spectral:'Measurements',assessment:'Image assessment'};
const sourceRoot='https://github.com/actforgoa2026/ActForGoa-website/blob/c1fc6fe71a6d5c9d6a8564a7b4a91612655d723c/reports/satellite-live-2026-10-28';

function SatellitePreview(){
  const [topic,setTopic]=useState<SatelliteIntent>('canopy_loss');
  const [split,setSplit]=useState(50),[view,setView]=useState<'swipe'|'pair'>('swipe');
  const summary=recorded.summaries[topic] as SatelliteResult['summary'];
  const water=recorded.evidence.water_change;
  const noCandidates=recorded.evidence.candidates.features.length===0;
  const headline=topic==='canopy_loss'&&noCandidates?'No vegetation-loss patches met the current thresholds.':topic==='surface_water'?'No pixels were labelled as water in this selected pair.':'This pair has no verified '+(topic==='land_change'?'development':topic==='waste'?'waste':'fire')+' assessment.';
  return <div className="preview-app">
    <a className="preview-skip" href="#preview-main">Skip to the observations</a>
    <header className="preview-header"><a className="preview-brand" href="https://actforgoa-field-guide.vercel.app/">actforgoa<span>.</span></a><span className="preview-header-label">Satellite observations</span><a className="preview-source-link" href={sourceRoot+'/README.md'} target="_blank" rel="noreferrer">View source record <span aria-hidden="true">↗</span></a></header>
    <main id="preview-main" className="preview-shell">
      <div className="preview-intro"><p className="preview-eyebrow">GOA · OBSERVATIONS OVER TIME</p><h1>A closer look at<br/>what’s changing.</h1><p className="preview-lead">Explore a real satellite image pair from Goa. Compare the same ground on two dates, then inspect what the measured evidence can tell us.</p></div>
      <div className="preview-status" role="status"><span className="preview-status-dot" aria-hidden="true"/><div><strong>Recorded imagery preview — new comparisons not connected</strong><p>These images were acquired on 10 and 20 October 2026 and retrieved on 28 October 2026. This page does not check today’s conditions.</p></div></div>
      <section className="preview-overview" aria-label="Observation overview"><div><span>Selected area</span><strong>{(recorded.area.area_m2/1_000_000).toFixed(2)} km² <small>in Goa</small></strong></div><div id="preview-coverage"><span>Usable in both images</span><strong>{Math.round(recorded.evidence.common_usable_fraction*100)}% <small>under the current mask</small></strong></div><div><span>Time between observations</span><strong>10 days <small>10 → 20 October 2026</small></strong></div><div><span>Visible / near-infrared pixels</span><strong>10 m <small>not individual-tree resolution</small></strong></div></section>

      <section className="preview-workspace" aria-labelledby="comparison-heading">
        <div className="preview-imagery"><div className="preview-section-heading"><div><p className="preview-eyebrow">01 / LOOK AT THE GROUND</p><h2 id="comparison-heading">One place. Two observations.</h2></div><div className="preview-view-toggle" role="group" aria-label="Image layout"><button aria-pressed={view==='swipe'} onClick={()=>setView('swipe')}>Swipe</button><button aria-pressed={view==='pair'} onClick={()=>setView('pair')}>Side by side</button></div></div>
          {view==='swipe'?<><div className="preview-swipe" aria-label="Before and after satellite comparison"><img className="preview-swipe-base" src={beforeImage} alt="Earlier real Sentinel-2 observation of the selected Goa area, 10 October 2026"/><img className="preview-swipe-after" src={afterImage} style={{clipPath:`inset(0 0 0 ${split}%)`}} alt="Later real Sentinel-2 observation of the same area, 20 October 2026"/><div className="preview-image-date preview-image-date-before">10 OCT 2026</div><div className="preview-image-date preview-image-date-after">20 OCT 2026</div><div className="preview-divider" style={{left:split+'%'}} aria-hidden="true"><span>↔</span></div></div><label className="preview-slider-label" htmlFor="preview-swipe-control"><span>Move the slider to compare the same ground.</span><input id="preview-swipe-control" type="range" min="0" max="100" value={split} onChange={event=>setSplit(Number(event.target.value))} aria-label="Earlier image share" aria-valuetext={`${split}% earlier image, ${100-split}% later image`}/></label></>:<div className="preview-image-pair">{[beforeImage,afterImage].map((image,index)=><figure key={image}><img src={image} alt={`${index?'Later':'Earlier'} real Sentinel-2 observation, ${date(recorded.observations[index].acquired_at)}`}/><figcaption>{index?'After':'Before'} · {date(recorded.observations[index].acquired_at)}</figcaption></figure>)}</div>}
          <div className="preview-acquisitions">{recorded.observations.map((observation,index)=><div key={observation.label} id={'preview-'+observation.label}><span>{index?'After acquisition':'Before acquisition'}</span><strong>{date(observation.acquired_at,true)}</strong></div>)}</div>
          <p className="preview-caption">Contains modified Copernicus Sentinel data (2026). Images are enlarged for viewing; enlargement does not add ground detail. SWIR and scene classification are native 20 m.</p>
          <a className="preview-location-link" href="https://amche.in/?atlas=goa#15/15.48500/73.82500" target="_blank" rel="noreferrer">Locate this area in Amche Atlas ↗</a><p className="preview-coordinate">Bounds: 73.82°–73.83° E, 15.48°–15.49° N</p>
        </div>

        <div className="preview-findings"><p className="preview-eyebrow">02 / READ THE EVIDENCE</p><h2>What can we learn?</h2><div className="preview-topics" role="group" aria-label="Evidence topic">{Object.entries(topics).map(([value,label])=><button key={value} aria-pressed={topic===value} onClick={()=>setTopic(value as SatelliteIntent)}>{label}</button>)}</div>
          <div className="preview-finding" aria-live="polite"><span className="preview-finding-kind">{topic==='canopy_loss'||topic==='surface_water'?'MEASURED EVIDENCE':'ASSESSMENT NOT AVAILABLE'}</span><h3>{headline}</h3>
            <p>{topic==='canopy_loss'?'This is a numeric vegetation check, not proof that no trees were removed. Smaller changes and individual trees may be missed.':topic==='surface_water'?'This small selected area is not a river-change validation case. A water label does not measure flow, depth or water quality.':topic==='land_change'?'Satellite images alone cannot determine whether a building is lawful. Planning permissions and parcel records have not been checked.':topic==='waste'?'Ordinary litter and small dumps are not reliably resolvable at this resolution. No material has been identified as waste.':'No FIRMS detections have been queried. An absence of a verified assessment is not evidence that no fire occurred.'}</p>
          </div>
          <div id="preview-spectral" className="preview-measurements"><h3>{topic==='surface_water'?'Water-classified area':'Reflectance measurements'}</h3>{topic==='surface_water'&&water?<dl>{(['before','after','gained','lost'] as const).map(key=><div key={key}><dt>{key[0].toUpperCase()+key.slice(1)}</dt><dd>{water[`${key}_area_m2`].toLocaleString('en-IN')} m²</dd></div>)}</dl>:<div className="preview-table-scroll"><table><thead><tr><th>Index</th><th>Before</th><th>After</th><th>Paired change</th></tr></thead><tbody>{Object.entries(recorded.evidence.metrics).map(([key,value])=><tr key={key}><th><span>{key.toUpperCase()}</span><small>{labels[key]}</small></th><td>{value.before_median.toFixed(3)}</td><td>{value.after_median.toFixed(3)}</td><td>{value.median_paired_change>0?'+':''}{value.median_paired_change.toFixed(3)}</td></tr>)}</tbody></table></div>}<p>Measured on the same {recorded.evidence.metrics.ndvi.paired_pixels.toLocaleString('en-IN')} usable pixels in both observations. Exploratory thresholds need field validation.</p></div>
          <details className="preview-details"><summary>Read the evidence-linked interpretation</summary>{summary?.statements.map((statement,index)=><p key={index}>{statement.text}{' '}<span>{statement.sources.map(source=><a key={source} href={'#preview-'+source}>{evidenceLabels[source]}</a>)}</span></p>)}</details>
          <div id="preview-assessment" className="preview-assessment"><strong>Image decisions: not run</strong><p>No OpenAI yes/no answers have been generated for this pair. We have not inferred canopy presence, tree removal, cause or an exact event date.</p></div>
        </div>
      </section>

      <section className="preview-next"><div><p className="preview-eyebrow">THE NEXT STEP</p><h2>From one pair to a fuller picture.</h2><p>The query dashboard is being connected for new area and date comparisons. Saved investigations, current acquisition checks and cited ecology-library context are part of that work. This preview contains one recorded comparison.</p></div><a href="https://actforgoa-field-guide.vercel.app/map">Query dashboard route ↗<small>Connection pending; new comparisons unavailable</small></a></section>
      <details className="preview-provenance"><summary>Acquisition records and method</summary><p>The underlying eight-band rasters were verified on the same 10 m grid with matching acquisition metadata. Both images use the same selected area; clouds, shadows and uncertain pixels are excluded from numeric comparison.</p>{recorded.observations.map(observation=><div key={observation.label}><strong>{observation.label==='before'?'Before':'After'} product</strong><code>{observation.catalog_scene_id}</code><small>Raster SHA-256: {observation.spectral_sha256}</small></div>)}<a href={sourceRoot+'/validation.json'} target="_blank" rel="noreferrer">Open the recorded validation evidence ↗</a></details>
    </main><footer className="preview-footer"><span>actforgoa. <small>Understanding the Goa we share.</small></span><span>Recorded evidence · Exploratory findings · Local review needed</span></footer>
  </div>;
}

createRoot(document.getElementById('satellite-preview-root')!).render(<SatellitePreview/>);
