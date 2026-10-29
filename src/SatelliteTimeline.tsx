import {Button} from './components/arc/button/button';
import type {SatelliteObservation,SatelliteScene} from './satellite-api';
import {observationDate as dateLabel} from './SatelliteHistory';

export function SatelliteTimeline({scenes,activeId,onSelect,observations,onLoad,busy,canLoad,before,after,onBefore,onAfter}:{
  scenes:SatelliteScene[];activeId:string;onSelect:(id:string)=>void;observations:Record<string,SatelliteObservation>;
  onLoad:()=>void;busy:boolean;canLoad:boolean;before:string;after:string;onBefore:(id:string)=>void;onAfter:(id:string)=>void;
}){
  if(!scenes.length)return null;
  const index=Math.max(0,scenes.findIndex(s=>s.id===activeId)),scene=scenes[index],observation=observations[scene.id];
  return <section className="satellite-timeline" aria-label="Observation timeline">
    <div className="satellite-timeline-title"><h3>Move through time</h3><span>{index+1} of {scenes.length} acquisitions</span></div>
    <label htmlFor="observation-time">{dateLabel(scene.acquired_at)}</label>
    <input id="observation-time" type="range" min="0" max={Math.max(0,scenes.length-1)} step="1" value={index} disabled={busy||scenes.length<2}
      aria-valuetext={dateLabel(scene.acquired_at)} onChange={e=>onSelect(scenes[Number(e.target.value)].id)}/>
    <div className="satellite-timeline-ends"><span>{dateLabel(scenes[0].acquired_at)}</span><span>{dateLabel(scenes.at(-1)!.acquired_at)}</span></div>
    <div className="satellite-timeline-actions">
      <Button type="button" variant="secondary" disabled={busy||index===0} onClick={()=>onSelect(scenes[index-1].id)}>Earlier</Button>
      <Button type="button" variant="secondary" disabled={busy||index===scenes.length-1} onClick={()=>onSelect(scenes[index+1].id)}>Later</Button>
      {!observation&&<Button type="button" disabled={busy||!canLoad} onClick={onLoad}>Load this observation</Button>}
      <Button type="button" variant="ghost" disabled={busy||before===scene.id} onClick={()=>onBefore(scene.id)}>{before===scene.id?'Before selected':'Use as before'}</Button>
      <Button type="button" variant="ghost" disabled={busy||after===scene.id} onClick={()=>onAfter(scene.id)}>{after===scene.id?'After selected':'Use as after'}</Button>
    </div>
    <p role="status">{observation?`${Math.round(observation.quality.usable_fraction*100)}% locally usable · ${Math.round(observation.quality.cloud_shadow_or_uncertain_fraction*100)}% cloud, shadow or uncertain.`:'Image not loaded for this date. Load it to inspect this location.'} Scene cloud: {scene.scene_cloud_percent===null?'unknown':Math.round(scene.scene_cloud_percent)+'%'}.</p>
    <p className="satellite-note">Each step is a real acquisition, not an evenly spaced day. Loaded dates switch instantly. Loading a new date retrieves imagery; it does not run AI analysis.</p>
  </section>;
}
