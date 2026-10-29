import {useEffect,useRef,useState} from 'react';
import {Button} from './components/arc/button/button';
import {satelliteApi,type SatelliteArea} from './satellite-api';

type Environment = {
  retrieved_at:string;unavailable:string[];
  weather:null|{currentTime:string;temperature:{degrees:number;unit:string};relativeHumidity:number;weatherCondition:{description:{text:string}}};
  air_quality:null|{dateTime:string;indexes:{code:string;displayName:string;aqi:number;category:string}[]};
};
const time=(value:string)=>value?new Date(value).toLocaleString('en-IN',{timeZone:'Asia/Kolkata',dateStyle:'medium',timeStyle:'short'})+' IST':'Time unavailable';

export function SatelliteEnvironment({area,csrfToken,ready}:{area:SatelliteArea|null;csrfToken:string;ready:boolean}){
  const [data,setData]=useState<Environment|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
  const request=useRef<AbortController|null>(null);
  useEffect(()=>{request.current?.abort();setData(null);setBusy(false);setError('');return()=>request.current?.abort();},[area,csrfToken]);
  async function load(){
    if(!area)return;
    request.current?.abort();const controller=new AbortController();request.current=controller;
    setBusy(true);setError('');setData(null);
    try{setData(await satelliteApi<Environment>('/environment',csrfToken,{area},controller.signal));}
    catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Current conditions could not load. Try again.');}
    finally{if(!controller.signal.aborted)setBusy(false);}
  }
  const centre=area?[(area.bbox[1]+area.bbox[3])/2,(area.bbox[0]+area.bbox[2])/2]:null;
  const reason=!area?'Select an area to check its current conditions.':!csrfToken?'Sign in to check current conditions.':!ready?'Google environmental services are not connected yet.':'';
  return <details className="satellite-environment"><summary>Current conditions and directions</summary>
    <p>Weather and air quality at the centre of your selected area. These are current readings, separate from the historical satellite images.</p>
    <div className="satellite-environment-actions"><Button type="button" variant="secondary" loading={busy} disabled={!!reason} onClick={load}>{data?'Refresh current conditions':'Check current conditions'}</Button>
      {centre&&<a href={'https://www.google.com/maps/dir/?api=1&destination='+centre.join(',')} target="_blank" rel="noreferrer">Get directions in Google Maps</a>}</div>
    {reason&&<p className="satellite-note">{reason}</p>}{error&&<p role="alert">{error}</p>}
    {data&&<div role="status">
      <dl className="satellite-environment-readings">
        {data.weather&&<div><dt>Weather</dt><dd>{data.weather.temperature?.degrees} °C · {data.weather.weatherCondition?.description?.text}<small>{data.weather.relativeHumidity}% humidity · {time(data.weather.currentTime)}</small></dd></div>}
        {data.air_quality?.indexes.map(index=><div key={index.code}><dt>{index.displayName}</dt><dd>{index.aqi} · {index.category}<small>{time(data.air_quality!.dateTime)}</small></dd></div>)}
      </dl>
      {data.unavailable.length>0&&<p>{data.unavailable.join(' and ')} could not load. Try refreshing shortly.</p>}
      <p className="satellite-google-credit">Google Maps</p>
    </div>}
    <p className="satellite-note">Checking conditions sends the selected area’s centre to Google. Readings are not saved with your investigation. <a href="https://maps.google.com/help/terms_maps/" target="_blank" rel="noreferrer">Google Maps terms</a> · <a href="https://policies.google.com/privacy" target="_blank" rel="noreferrer">Google privacy policy</a></p>
  </details>;
}
