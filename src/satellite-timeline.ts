import type {SatelliteScene} from './satellite-api';

export function orderedScenes(scenes: SatelliteScene[]): SatelliteScene[] {
  return [...new Map(scenes.map(scene=>[scene.id,scene])).values()]
    .filter(scene=>Number.isFinite(Date.parse(scene.acquired_at)))
    .sort((a,b)=>Date.parse(a.acquired_at)-Date.parse(b.acquired_at)||a.id.localeCompare(b.id));
}

export function orderedPair(scenes: SatelliteScene[], before: string, after: string): boolean {
  const a=scenes.find(s=>s.id===before),b=scenes.find(s=>s.id===after);
  return !!a&&!!b&&Date.parse(a.acquired_at)<Date.parse(b.acquired_at);
}

export function areaError(bbox: number[]): string|null {
  const [w,s,e,n]=bbox;
  if(bbox.length!==4||bbox.some(n=>!Number.isFinite(n))||w>=e||s>=n||w<73.5||e>74.6||s<14.7||n>16)
    return 'Choose a valid area around Goa.';
  const km2=(e-w)*111.32*Math.cos((n+s)/2*Math.PI/180)*(n-s)*111.32;
  if(e-w>.06||n-s>.06||km2>25)return 'Zoom in and select a smaller area, up to 25 km².';
  if(km2<.0009)return 'Select an area of at least 900 m². Individual trees may be too small to resolve.';
  return null;
}
