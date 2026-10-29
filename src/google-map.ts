/// <reference types="google.maps" />
import {importLibrary, setOptions} from '@googlemaps/js-api-loader';
import type {SatelliteArea} from './satellite-api';

export const GOA_BOUNDS = {west:73.5,south:14.7,east:74.6,north:16};
export const bboxBounds = ([west,south,east,north]:SatelliteArea['bbox']):google.maps.LatLngBoundsLiteral => ({west,south,east,north});
export const boundsBbox = (bounds:google.maps.LatLngBounds):SatelliteArea['bbox'] => {
  const {west,south,east,north}=bounds.toJSON();return [west,south,east,north];
};
export const withinGoa = (latitude:number,longitude:number) => Number.isFinite(latitude)&&Number.isFinite(longitude)&&longitude>=GOA_BOUNDS.west&&longitude<=GOA_BOUNDS.east&&latitude>=GOA_BOUNDS.south&&latitude<=GOA_BOUNDS.north;

let pending:Promise<google.maps.MapsLibrary>|undefined;
let configured=false;
export function loadGoogleMap(){
  if(!pending)pending=(async()=>{
    if(!configured){
      const response=await fetch('/api/map-config',{signal:AbortSignal.timeout(10000),cache:'no-store'});
      if(!response.ok)throw Error('Google Maps is not configured for this site yet. You can select an area using coordinates below.');
      const {browserKey}=await response.json();
      if(typeof browserKey!=='string'||!/^AIza[\w-]{35}$/.test(browserKey))throw Error('Google Maps is not configured for this site yet. You can select an area using coordinates below.');
      setOptions({key:browserKey,v:'quarterly',language:'en',region:'IN',authReferrerPolicy:'origin'});
      configured=true;
    }
    return importLibrary('maps');
  })().catch(error=>{pending=undefined;throw error;});
  return pending;
}

export async function searchGooglePlaces(query:string){
  await loadGoogleMap();
  const {Place}=await importLibrary('places');
  const {places}=await Place.searchByText({textQuery:query,fields:['id','displayName','formattedAddress','location'],locationRestriction:GOA_BOUNDS,maxResultCount:5,language:'en',region:'IN'});
  return places.filter(place=>place.location&&withinGoa(place.location.lat(),place.location.lng())).map(place=>({id:place.id,name:place.displayName||'Unnamed place',detail:place.formattedAddress||'',latitude:place.location!.lat(),longitude:place.location!.lng()}));
}
