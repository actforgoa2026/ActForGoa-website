import type {SatelliteArea,SatelliteObservation} from './satellite-api';
/** Poll a known job only. Retrying this function never creates provider work. */
export async function pollSatelliteJob<T extends {status:string}>(id:string, get:(id:string,signal:AbortSignal)=>Promise<T>, signal:AbortSignal, attempts=120, interval=2000):Promise<T> {
  for(let i=0;i<attempts;i++) {
    signal.throwIfAborted();
    const job=await get(id,signal);
    signal.throwIfAborted();
    if(job.status==='complete'||job.status==='failed')return job;
    if(job.status!=='running')throw new Error('The imagery service returned an unknown job state. Check this reference again.');
    await new Promise<void>((resolve,reject)=>{
      const abort=()=>{clearTimeout(timer);reject(signal.reason);};
      const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},interval);
      signal.addEventListener('abort',abort,{once:true});
      if(signal.aborted)abort();
    });
  }
  throw new Error('This job is still processing. Use Check job to resume without submitting it again.');
}

/** Store only the actor-scoped opaque job ID for this tab, never tokens or imagery. */
export function pendingJobKey(actor:string){return 'satellite.pending-job.'+actor;}
export function validJobId(value:string|null):value is string {return !!value&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);}

export function sameImageryContext(a:{area:SatelliteArea|null;start_date:string;end_date:string},b:{area:SatelliteArea|null;start_date:string;end_date:string}):boolean {
  return !!a.area&&!!b.area&&a.start_date===b.start_date&&a.end_date===b.end_date&&a.area.bbox.every((value,index)=>value===b.area!.bbox[index]);
}

export function cacheObservations(previous:Record<string,SatelliteObservation>,incoming:SatelliteObservation[]):Record<string,SatelliteObservation>{
  const updated=new Map(Object.entries(previous));
  for(const observation of incoming){updated.delete(observation.catalog_scene_id);updated.set(observation.catalog_scene_id,observation);}
  return Object.fromEntries([...updated].slice(-20));
}
