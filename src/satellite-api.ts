export type SatelliteArea = {bbox: [number,number,number,number]};
export type SatelliteIntent = 'canopy_loss' | 'fire' | 'surface_water' | 'land_change' | 'waste';
export type SatelliteScene = {id:string; acquired_at:string; scene_cloud_percent:number|null};
export type SatellitePlan = {state:string; message:string; intent?:SatelliteIntent; area?:SatelliteArea; window_start?:string; window_end?:string; catalog_start?:string; catalog_end?:string; warnings?:string[]; place_name?:string};
export type SatelliteObservation = {catalog_scene_id:string; acquired_at:string[]; quality:{usable_fraction:number;missing_fraction:number;cloud_shadow_or_uncertain_fraction:number}; image:string;map_layer?:{bbox:[number,number,number,number];crs:string;width:number;height:number}};
export type SatelliteFreshness = {catalog_searched_at:string;latest_acquired_at_in_search:string;selected_after_acquired_at:string;newer_acquisitions_in_search:number;search_start:string;search_end:string;catalog_truncated:boolean;note:string};
export type SatelliteContext = {state:string;message:string;searched_at?:string;sources:{id:string;title:string;text:string;url:string;reader_url:string;generation:string;label:string;retrieved_at:string;warning:string;excerpt_truncated:boolean}[]};
export type SatelliteRequest = {area:SatelliteArea;start_date:string;end_date:string;before_id:string;after_id:string;intent:SatelliteIntent;question?:string;window_start?:string;window_end?:string};
export type SatelliteSpatialMatch={relation:'same_area'|'partial_overlap';query_fraction:number;comparison_fraction:number;intersection_area_m2:number};
export type SatelliteHistory = {scan_truncated?:boolean;items:{id:string;status:string;created_at:string;spatial?:SatelliteSpatialMatch;request:SatelliteRequest|null;summary:SatelliteResult['summary']|null;observation_interval:SatelliteResult['observation_interval']|null;freshness:SatelliteFreshness|null;'evidence.common_usable_fraction':number|null;error?:string}[];next_offset:number|null;retention_days:number;scope:string};
export type SatelliteDecision = {choice:string;confidence?:number;probabilities?:{value:string;probability:number}[];probabilities_complete?:boolean};
export type SatelliteResult = {
  recorded_example?:{kind:'recorded-real';retrieved_at:string;source_url:string;note:string};
  intent?:SatelliteIntent; freshness?:SatelliteFreshness;library_context?:SatelliteContext;planning_context?:{message:string};
  before:SatelliteObservation; after:SatelliteObservation;
  evidence:{state:string;common_usable_fraction:number;metrics:Record<string,{before_median:number;after_median:number;median_paired_change:number}>;candidates:GeoJSON.FeatureCollection; candidates_truncated?:boolean;water_candidates?:GeoJSON.FeatureCollection;water_change?:{before_area_m2:number;after_area_m2:number;gained_area_m2:number;lost_area_m2:number;method:string}|null};
  classification:{state:string;message?:string;provider?:string;model?:string;validation?:string;scope?:{target_id:string|null;description:string;common_usable_fraction:number|null};calibration?:string;answers:Record<string,SatelliteDecision>};
  summary?:{state:string;headline:string;statements:{text:string;sources:('before'|'after'|'coverage'|'spectral'|'assessment')[]}[]};
  canopy_presence?:{before:'yes'|'no'|'uncertain';after:'yes'|'no'|'uncertain';state:string;interpretation:string;scope:string};
  observation_interval:{before:string;after:string;query_window_relation?:string};
  limitations:string[]; fire_detections:{state:string;message:string};
};
export class SatelliteApiError extends Error {
  constructor(message:string,readonly status:number){super(message);this.name='SatelliteApiError';}
}
export async function satelliteApi<T>(route:string, csrfToken:string, body?:unknown, signal?:AbortSignal):Promise<T> {
  const response = await fetch('/api/admin/satellite'+route, {
    method:body === undefined ? 'GET':'POST',credentials:'same-origin',
    headers:{'Content-Type':'application/json',...(body === undefined ? {}:{'X-CSRF-Token':csrfToken})},
    ...(body === undefined ? {}:{body:JSON.stringify(body)}),signal:AbortSignal.any([AbortSignal.timeout(65000),...(signal?[signal]:[])]),
  });
  const data=await response.json().catch(()=>null);
  signal?.throwIfAborted();
  if (!response.ok || !data) throw new SatelliteApiError(data?.error || (response.status===404?'Satellite routes are unavailable on this host. Open the standalone satellite workspace.':'Satellite monitoring could not respond. Please try again.'),response.status);
  return data as T;
}
