import {lazy, Suspense} from 'react';
import type {SatelliteArea, SatelliteObservation, SatellitePreview} from './satellite-api';

// Each deployment keeps its deliberately configured provider. This build-time
// branch removes the other provider's import; no browser key probing or fallback.
export const satelliteMapProvider = import.meta.env.MODE === 'satellite' ? 'google' : 'leaflet';
const ProviderMap = import.meta.env.MODE === 'satellite'
  ? lazy(() => import('./SatelliteGoogleMap').then(module => ({default: module.SatelliteGoogleMap})))
  : lazy(() => import('./SatelliteLeafletMap').then(module => ({default: module.SatelliteLeafletMap})));

export type SatelliteMapProps = {
  area: SatelliteArea | null;
  onArea: (area: SatelliteArea) => boolean | void;
  observation?: SatelliteObservation;
  candidates?: GeoJSON.FeatureCollection;
  disabled?: boolean;
  preview?: SatellitePreview|null;
  previewBusy?: boolean;
  previewError?: string;
  onRetryPreview?: ()=>void;
  progress?: string;
  error?: string;
  accessMessage?: string;
};

export function SatelliteMap(props: SatelliteMapProps) {
  return <Suspense fallback={<p role="status">Opening the map…</p>}><ProviderMap {...props}/></Suspense>;
}
