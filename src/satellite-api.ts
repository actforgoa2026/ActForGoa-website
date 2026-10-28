export type SatelliteArea = {bbox: [number,number,number,number]};
export type SatelliteIntent = 'canopy_loss' | 'fire' | 'surface_water' | 'land_change';
export type SatelliteScene = {id:string; acquired_at:string; scene_cloud_percent:number|null};
export type SatellitePlan = {state:string; message:string; intent?:SatelliteIntent; area?:SatelliteArea; window_start?:string; window_end?:string; catalog_start?:string; catalog_end?:string; warnings?:string[]; place_name?:string};
export type SatelliteObservation = {catalog_scene_id:string; acquired_at:string[]; quality:{usable_fraction:number;missing_fraction:number;cloud_shadow_or_uncertain_fraction:number}; image:string};
export type SatelliteResult = {
  before:SatelliteObservation; after:SatelliteObservation;
  evidence:{state:string;common_usable_fraction:number;metrics:Record<string,{before_median:number;after_median:number;median_paired_change:number}>;candidates:GeoJSON.FeatureCollection; candidates_truncated?:boolean};
  classification:{state:string;message?:string;answers:Record<string,{choice:string}>};
  observation_interval:{before:string;after:string;query_window_relation?:string};
  limitations:string[]; fire_detections:{state:string;message:string};
};
export async function satelliteApi<T>(route:string, csrfToken:string, body?:unknown, signal?:AbortSignal):Promise<T> {
  const response = await fetch('/api/admin/satellite'+route, {
    method:body === undefined ? 'GET':'POST',credentials:'same-origin',
    headers:{'Content-Type':'application/json',...(body === undefined ? {}:{'X-CSRF-Token':csrfToken})},
    ...(body === undefined ? {}:{body:JSON.stringify(body)}),signal:AbortSignal.any([AbortSignal.timeout(65000),...(signal?[signal]:[])]),
  });
  const data=await response.json().catch(()=>null);
  if (!response.ok || !data) throw new Error(data?.error || 'Satellite monitoring could not respond. Please try again.');
  return data as T;
}
