import {useEffect,useRef,useState} from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {AmcheLayers} from './AmcheLayers';
import {Button} from './components/arc/button/button';
import type {SatelliteArea,SatelliteObservation} from './satellite-api';
import {observationDate as dateLabel} from './SatelliteHistory';
import {areaError} from './satellite-timeline';

export function SatelliteMap({area,onArea,observation,candidates,disabled=false}:{area:SatelliteArea|null;onArea:(area:SatelliteArea)=>void;observation?:SatelliteObservation;candidates?:GeoJSON.FeatureCollection;disabled?:boolean}) {
  const container=useRef<HTMLDivElement>(null),map=useRef<L.Map|null>(null),selection=useRef<L.Rectangle|null>(null),features=useRef<L.GeoJSON|null>(null),overlay=useRef<L.ImageOverlay|null>(null);
  const selecting=useRef(false),first=useRef<L.LatLng|null>(null),callback=useRef(onArea),blocked=useRef(disabled);
  const firstMarker=useRef<L.CircleMarker|null>(null),draft=useRef<L.Rectangle|null>(null);
  const [mapInstance,setMapInstance]=useState<L.Map|null>(null);
  const [drawing,setDrawing]=useState(false),[corner,setCorner]=useState(false),[opacity,setOpacity]=useState(100),[tileError,setTileError]=useState(false);
  const [viewport,setViewport]=useState<SatelliteArea['bbox']|null>(null),[draftError,setDraftError]=useState('');
  callback.current=onArea;blocked.current=disabled;
  const bbox=(bounds:L.LatLngBounds):SatelliteArea['bbox']=>[bounds.getWest(),bounds.getSouth(),bounds.getEast(),bounds.getNorth()];
  function removeDraft(){firstMarker.current?.remove();firstMarker.current=null;draft.current?.remove();draft.current=null;first.current=null;}
  function cancelDrawing(){removeDraft();selecting.current=false;setDrawing(false);setCorner(false);setDraftError('');}
  useEffect(()=>{
    if(!container.current)return;
    const instance=L.map(container.current,{center:[15.4,74],zoom:10,preferCanvas:true,zoomAnimation:false,minZoom:8,maxZoom:19,maxBounds:[[14.7,73.5],[16,74.6]],maxBoundsViscosity:.8});map.current=instance;setMapInstance(instance);
    // OSM requires a referrer. Send only the public origin for tiles, while
    // keeping the workspace's no-referrer policy for all other requests.
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,referrerPolicy:'strict-origin',attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).on('tileerror',()=>setTileError(true)).addTo(instance);
    L.control.scale({imperial:false}).addTo(instance);
    instance.createPane('satellite-imagery');instance.getPane('satellite-imagery')!.style.zIndex='350';
    const updateViewport=()=>setViewport(bbox(instance.getBounds()));
    instance.on('moveend',updateViewport);updateViewport();
    const showDraft=(position:L.LatLng)=>{
      if(!first.current)return;
      const bounds=L.latLngBounds(first.current,position),error=areaError(bbox(bounds));
      const style={color:error?'#8a391f':'#193e32',weight:2,fillOpacity:.12,dashArray:'6 4',interactive:false};
      if(draft.current)draft.current.setBounds(bounds).setStyle(style);
      else draft.current=L.rectangle(bounds,style).addTo(instance);
      setDraftError(error||'');
    };
    instance.on('mousemove',(event:L.LeafletMouseEvent)=>{if(selecting.current&&!blocked.current)showDraft(event.latlng);});
    instance.on('click',(event:L.LeafletMouseEvent)=>{
      if(!selecting.current||blocked.current)return;
      if(!first.current){
        first.current=event.latlng;setCorner(true);setDraftError('');
        firstMarker.current=L.circleMarker(event.latlng,{radius:7,color:'#193e32',weight:3,fillColor:'#ffffff',fillOpacity:1,interactive:false}).addTo(instance);
        return;
      }
      const bounds=L.latLngBounds(first.current,event.latlng);
      const value=bbox(bounds),error=areaError(value);
      if(error){showDraft(event.latlng);return;}
      cancelDrawing();callback.current({bbox:value});
    });
    const escape=(event:KeyboardEvent)=>{if(event.key==='Escape'&&selecting.current){event.preventDefault();cancelDrawing();}};
    instance.getContainer().addEventListener('keydown',escape);
    const resize=new ResizeObserver(()=>{instance.invalidateSize();updateViewport();});resize.observe(container.current);
    return()=>{resize.disconnect();instance.getContainer().removeEventListener('keydown',escape);removeDraft();selecting.current=false;instance.remove();map.current=null;setMapInstance(null);};
  },[]);
  useEffect(()=>{if(disabled)cancelDrawing();},[disabled]);
  useEffect(()=>{
    if(!map.current)return;
    cancelDrawing();
    selection.current?.remove();map.current.stop();
    if(area){const [w,s,e,n]=area.bbox;selection.current=L.rectangle([[s,w],[n,e]],{color:'#193e32',weight:2,fillOpacity:0,interactive:false}).addTo(map.current);map.current.fitBounds([[s,w],[n,e]],{maxZoom:16,padding:[24,24],animate:false});}
  },[area]);
  useEffect(()=>{if(map.current){features.current?.remove();features.current=null;if(candidates)features.current=L.geoJSON(candidates,{style:{color:'#8a391f',weight:2,fillOpacity:.22}}).addTo(map.current);}},[candidates]);
  useEffect(()=>{
    overlay.current?.remove();overlay.current=null;
    const layer=observation?.map_layer;
    if(map.current&&layer){const [w,s,e,n]=layer.bbox;overlay.current=L.imageOverlay(observation.image,[[s,w],[n,e]],{pane:'satellite-imagery',attribution:'Contains modified Copernicus Sentinel data',alt:`Sentinel-2 acquisition ${observation.acquired_at.join(', ')}`}).addTo(map.current);}
  },[observation]);
  useEffect(()=>{overlay.current?.setOpacity(opacity/100);},[opacity,observation]);
  const viewportError=viewport?areaError(viewport):'The map is loading.';
  const viewportGuidance=viewportError==='Choose a valid area around Goa.'?'Zoom in and keep the visible map within Goa, or draw a smaller area. The limit is 25 km².':viewportError;
  return <div className="satellite-map-section">
    <div className="satellite-map-toolbar"><Button type="button" variant="secondary" disabled={disabled} onClick={()=>{const start=!selecting.current;cancelDrawing();if(start){selecting.current=true;setDrawing(true);}}}>{drawing?'Cancel area selection':'Draw an area'}</Button>
      <Button type="button" variant="ghost" disabled={disabled||!!viewportError} aria-describedby="satellite-viewport-guidance" onClick={()=>{const bounds=map.current?.getBounds();if(bounds){const value=bbox(bounds);if(!areaError(value)){cancelDrawing();onArea({bbox:value});}}}}>Use visible map area</Button>
      <p role="status">{drawing?(draftError||(corner?'First corner marked. Choose the opposite corner, or press Escape to cancel.':'Choose the first corner.')):area?'Selected area outlined. Pan and zoom to explore.':'Navigate to a place, then draw two opposite corners. Up to 25 km².'}</p></div>
    <p id="satellite-viewport-guidance" className="satellite-note">{viewportGuidance||'The visible area fits the size limit. Use it directly or draw a smaller selection.'}</p>
    <div ref={container} className="satellite-map" aria-label="Goa investigation map. Pan and zoom, then draw an area. Coordinate fields below provide a keyboard alternative." />
    <AmcheLayers map={mapInstance}/>
    {tileError&&<p className="satellite-note">Some street-map tiles could not load. Selected areas and loaded satellite images remain available.</p>}
    {observation&&<div className="satellite-map-caption"><p><strong>{dateLabel(observation.acquired_at[0])}</strong> · Sentinel-2, 10 m grid{!observation.map_layer?' · This saved observation predates map overlays; see its image below.':''}</p>
      {observation.map_layer&&<label>Imagery opacity <input type="range" min="0" max="100" value={opacity} onChange={e=>setOpacity(Number(e.target.value))}/><span>{opacity}%</span></label>}</div>}
  </div>;
}
