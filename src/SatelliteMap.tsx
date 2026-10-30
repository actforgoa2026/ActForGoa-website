import {lazy, Suspense, type ReactNode} from 'react';
import type {SatelliteArea, SatelliteObservation, SatellitePreview} from './satellite-api';

// The ActForGoa /map route and standalone preview share the Earth Engine workspace.
export const satelliteMapProvider = 'google';
const ProviderMap = lazy(() => import('./SatelliteGoogleMap').then(module => ({default: module.SatelliteGoogleMap})));

export type SatelliteMapProps = {
  periodControls?: ReactNode;
  updateControl?: ReactNode;
  periodError?: string;
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
