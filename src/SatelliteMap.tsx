import {useEffect,useRef,useState,type FormEvent,type PointerEvent as ReactPointerEvent} from 'react';
import L from 'leaflet';
import {LocateFixed,Maximize2,Minimize2,Minus,Plus,Scan,SquareDashed,X,MapPin,Search} from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import {AmcheLayers} from './AmcheLayers';
import {Button} from './components/arc/button/button';
import {SearchField} from './components/arc/search-field/search-field';
import type {SatelliteArea,SatelliteObservation} from './satellite-api';
import {areaError} from './satellite-timeline';
import {observationDate as dateLabel} from './SatelliteHistory';

type Place={id:string;name:string;detail:string;longitude:number;latitude:number};
export function SatelliteMap({area,onArea,observation,candidates,disabled=false}:{area:SatelliteArea|null;onArea:(area:SatelliteArea)=>void;observation?:SatelliteObservation;candidates?:GeoJSON.FeatureCollection;disabled?:boolean}) {
  const container=useRef<HTMLDivElement>(null),workspace=useRef<HTMLDivElement>(null),map=useRef<L.Map|null>(null),selection=useRef<L.Rectangle|null>(null),features=useRef<L.GeoJSON|null>(null),overlay=useRef<L.ImageOverlay|null>(null);
  const preview=useRef<L.Rectangle|null>(null),pin=useRef<L.CircleMarker|null>(null),anchor=useRef<L.LatLng|null>(null),cornerPin=useRef<L.CircleMarker|null>(null);
  const press=useRef<{x:number;y:number;second:boolean}|null>(null),searchRequest=useRef<AbortController|null>(null),locationAttempt=useRef(0);
  const [mapInstance,setMapInstance]=useState<L.Map|null>(null);
  const [drawing,setDrawing]=useState(false),[corner,setCorner]=useState(false),[expanded,setExpanded]=useState(false),[opacity,setOpacity]=useState(100),[tileError,setTileError]=useState(false);
  const [message,setMessage]=useState(''),[selectionError,setSelectionError]=useState(''),[locating,setLocating]=useState(false);
  const [query,setQuery]=useState(''),[places,setPlaces]=useState<Place[]>([]),[searching,setSearching]=useState(false),[searchMessage,setSearchMessage]=useState('');
  function clearDraft(){preview.current?.remove();preview.current=null;cornerPin.current?.remove();cornerPin.current=null;anchor.current=null;press.current=null;setCorner(false);}
  function cancelDraw(){clearDraft();setDrawing(false);setSelectionError('');}
  useEffect(()=>{
    if(!container.current)return;
    const instance=L.map(container.current,{center:[15.4,74],zoom:10,zoomControl:false,preferCanvas:true,zoomAnimation:false,minZoom:8,maxZoom:19,maxBounds:[[14.7,73.5],[16,74.6]],maxBoundsViscosity:.8});map.current=instance;setMapInstance(instance);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,referrerPolicy:'strict-origin',attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).on('tileerror',()=>setTileError(true)).addTo(instance);
    L.control.scale({imperial:false}).addTo(instance);
    instance.createPane('satellite-imagery');instance.getPane('satellite-imagery')!.style.zIndex='350';
    const resize=new ResizeObserver(()=>instance.invalidateSize());resize.observe(container.current);
    return()=>{resize.disconnect();searchRequest.current?.abort();locationAttempt.current++;instance.remove();map.current=null;setMapInstance(null);};
  },[]);
  useEffect(()=>{if(disabled)cancelDraw();},[disabled]);
  useEffect(()=>{
    const instance=map.current;if(!instance)return;
    if(drawing){instance.dragging.disable();instance.doubleClickZoom.disable();instance.touchZoom.disable();instance.scrollWheelZoom.disable();}
    else{instance.dragging.enable();instance.doubleClickZoom.enable();instance.touchZoom.enable();instance.scrollWheelZoom.enable();}
  },[drawing]);
  useEffect(()=>{
    const escape=(event:KeyboardEvent)=>{if(event.key==='Escape'){cancelDraw();setExpanded(false);setPlaces([]);}};
    document.addEventListener('keydown',escape);return()=>document.removeEventListener('keydown',escape);
  },[]);
  useEffect(()=>{
    if(!expanded)return;
    const previous=document.body.style.overflow;document.body.style.overflow='hidden';
    const keepFocus=(event:KeyboardEvent)=>{
      if(event.key!=='Tab'||!workspace.current)return;
      const controls=[...workspace.current.querySelectorAll<HTMLElement>('button:not(:disabled),input:not(:disabled),a[href],summary,[tabindex="0"]')].filter(el=>el.getBoundingClientRect().width>0);
      const first=controls[0],last=controls.at(-1);if(!first||!last)return;
      if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
      else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    };
    document.addEventListener('keydown',keepFocus);
    return()=>{document.body.style.overflow=previous;document.removeEventListener('keydown',keepFocus);};
  },[expanded]);
  useEffect(()=>{
    if(!map.current)return;
    selection.current?.remove();selection.current=null;map.current.stop();
    if(area){const [w,s,e,n]=area.bbox;selection.current=L.rectangle([[s,w],[n,e]],{color:'#193e32',weight:3,fillOpacity:.06,interactive:false}).addTo(map.current);map.current.fitBounds([[s,w],[n,e]],{maxZoom:16,padding:[48,48],animate:false});}
  },[area]);
  useEffect(()=>{if(map.current){features.current?.remove();features.current=null;if(candidates)features.current=L.geoJSON(candidates,{style:{color:'#8a391f',weight:2,fillOpacity:.22}}).addTo(map.current);}},[candidates]);
  useEffect(()=>{
    overlay.current?.remove();overlay.current=null;
    const layer=observation?.map_layer;
    if(map.current&&layer){const [w,s,e,n]=layer.bbox;overlay.current=L.imageOverlay(observation.image,[[s,w],[n,e]],{pane:'satellite-imagery',attribution:'Contains modified Copernicus Sentinel data',alt:`Sentinel-2 acquisition ${observation.acquired_at.join(', ')}`}).addTo(map.current);}
  },[observation]);
  useEffect(()=>{overlay.current?.setOpacity(opacity/100);},[opacity,observation]);
  function acceptBounds(bounds:L.LatLngBounds){
    const bbox:SatelliteArea['bbox']=[bounds.getWest(),bounds.getSouth(),bounds.getEast(),bounds.getNorth()];
    const error=areaError(bbox);clearDraft();
    if(error){setSelectionError(error);return false;}
    onArea({bbox});setDrawing(false);setSelectionError('');setMessage('Area selected. Choose dates below to find observations.');return true;
  }
  function pointerDown(event:ReactPointerEvent<HTMLDivElement>){
    if(disabled||!map.current||event.button!==0||!event.isPrimary)return;
    event.preventDefault();event.currentTarget.setPointerCapture(event.pointerId);setSelectionError('');
    press.current={x:event.clientX,y:event.clientY,second:!!anchor.current};
    if(!anchor.current){anchor.current=map.current.mouseEventToLatLng(event.nativeEvent);cornerPin.current=L.circleMarker(anchor.current,{radius:5,color:'#193e32',fillColor:'#fff',fillOpacity:1,interactive:false}).addTo(map.current);setCorner(true);}
  }
  function pointerMove(event:ReactPointerEvent<HTMLDivElement>){
    if(!event.isPrimary||!anchor.current||!map.current)return;
    const bounds=L.latLngBounds(anchor.current,map.current.mouseEventToLatLng(event.nativeEvent));
    if(preview.current)preview.current.setBounds(bounds);
    else preview.current=L.rectangle(bounds,{color:'#193e32',weight:2,dashArray:'6 4',fillOpacity:.16,interactive:false}).addTo(map.current);
  }
  function pointerUp(event:ReactPointerEvent<HTMLDivElement>){
    if(!event.isPrimary)return;
    const start=press.current;press.current=null;
    if(event.currentTarget.hasPointerCapture(event.pointerId))event.currentTarget.releasePointerCapture(event.pointerId);
    if(!start||!anchor.current||!map.current)return;
    if(start.second||Math.hypot(event.clientX-start.x,event.clientY-start.y)>=5)acceptBounds(L.latLngBounds(anchor.current,map.current.mouseEventToLatLng(event.nativeEvent)));
  }
  function showPlace(latitude:number,longitude:number,label:string,zoom=15){
    cancelDraw();pin.current?.remove();if(!map.current)return;
    map.current.setView([latitude,longitude],zoom,{animate:false});
    pin.current=L.circleMarker([latitude,longitude],{radius:8,color:'#fff',weight:3,fillColor:'#193e32',fillOpacity:1,interactive:false}).addTo(map.current);
    setMessage(label+' — draw an area around the place you want to investigate.');
  }
  async function search(event:FormEvent){
    event.preventDefault();searchRequest.current?.abort();const controller=new AbortController();searchRequest.current=controller;
    setSearching(true);setSearchMessage('');setPlaces([]);
    try{
      const response=await fetch('/api/map-places?'+new URLSearchParams({q:query.trim()}),{signal:controller.signal});
      const data=await response.json();if(!response.ok)throw Error(data.error||'Place search is unavailable.');
      setPlaces(data.places);setSearchMessage(data.places.length?'Choose a place to move the map.':'No matching places around Goa. Try the business name with its village or town.');
    }catch(error){if(!controller.signal.aborted)setSearchMessage(error instanceof Error?error.message:'Place search is unavailable.');}
    finally{if(!controller.signal.aborted)setSearching(false);}
  }
  function locate(){
    if(!navigator.geolocation){setMessage('This browser does not support location. Search for a place instead.');return;}
    const attempt=++locationAttempt.current;setLocating(true);setMessage('Waiting for your location permission…');
    navigator.geolocation.getCurrentPosition(position=>{
      if(attempt!==locationAttempt.current)return;setLocating(false);
      const {latitude,longitude}=position.coords;
      if(longitude<73.5||longitude>74.6||latitude<14.7||latitude>16){setMessage('Your current location is outside the Goa map. Search for a place in Goa instead.');return;}
      showPlace(latitude,longitude,'Your approximate location');
    },error=>{if(attempt!==locationAttempt.current)return;setLocating(false);setMessage(error.code===1?'Location access was declined. Allow it in your browser settings, or search for a place.':error.code===3?'Location took too long. Try again or search for a place.':'Your location is unavailable. Try again or search for a place.');},{enableHighAccuracy:false,timeout:10000,maximumAge:60000});
  }
  return <div ref={workspace} className={'satellite-map-section'+(expanded?' satellite-map-expanded':'')}>
    <div className="satellite-map-search">
      <form onSubmit={search}><SearchField label="Find an area or business in Goa" placeholder="Try Panaji or a business name" value={query} maxLength={120} minLength={3} onValueChange={value=>{setQuery(value);searchRequest.current?.abort();setSearching(false);setPlaces([]);setSearchMessage('');}}/><Button type="submit" size="sm" loading={searching} disabled={query.trim().length<3} aria-label="Search places"><Search size={18} aria-hidden="true"/></Button></form>
      <div className="satellite-map-tools">
        <Button type="button" size="sm" variant={drawing?'primary':'secondary'} aria-pressed={drawing} disabled={disabled} onClick={()=>{if(drawing)cancelDraw();else{clearDraft();setSelectionError('');setDrawing(true);}}}>{drawing?<X size={18}/>:<SquareDashed size={18}/>}<span>{drawing?'Cancel drawing':'Draw area'}</span></Button>
        <Button type="button" size="sm" variant="secondary" loading={locating} onClick={locate} title="Use my current location" aria-label="Use my current location"><LocateFixed size={18}/></Button>
        <Button type="button" size="sm" variant="secondary" aria-label={expanded?'Exit expanded map':'Expand map'} title={expanded?'Exit expanded map':'Expand map'} aria-pressed={expanded} onClick={()=>setExpanded(v=>!v)}>{expanded?<Minimize2 size={18}/>:<Maximize2 size={18}/>}</Button>
      </div>
    </div>
    {(searchMessage||places.length>0)&&<div className="satellite-place-results"><p role="status">{searchMessage}</p>{places.length>0&&<ul>{places.map(place=><li key={place.id}><Button type="button" variant="ghost" onClick={()=>{showPlace(place.latitude,place.longitude,place.name);setPlaces([]);setSearchMessage('');}}><MapPin size={18} aria-hidden="true"/><span><strong>{place.name}</strong>{place.detail&&<small>{place.detail}</small>}</span></Button></li>)}</ul>}<p className="satellite-search-credit">Search by <a href="https://photon.komoot.io" target="_blank" rel="noreferrer">Photon</a> · <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a>. Some businesses may be missing.</p></div>}
    <div className="satellite-map-canvas">
      <div ref={container} className="satellite-map" aria-label="Goa investigation map. Pan and zoom, then draw an area. Coordinate fields below provide a keyboard alternative." />
      {drawing&&<div className="satellite-draw-surface" role="group" tabIndex={0} aria-label="Draw a rectangle by dragging or tapping two opposite corners. Escape cancels." onPointerDown={pointerDown} onPointerMove={pointerMove} onPointerUp={pointerUp} onPointerCancel={clearDraft} onLostPointerCapture={()=>{if(press.current)clearDraft();}}/>}
      <div className="satellite-map-zoom"><Button type="button" size="sm" variant="secondary" aria-label="Zoom in" disabled={drawing} onClick={()=>map.current?.zoomIn()}><Plus size={20}/></Button><Button type="button" size="sm" variant="secondary" aria-label="Zoom out" disabled={drawing} onClick={()=>map.current?.zoomOut()}><Minus size={20}/></Button></div>
      <div className="satellite-map-bottom"><p role="status">{selectionError|| (drawing?(corner?'Drag or tap the opposite corner. Escape cancels.':'Drag a rectangle, or tap two opposite corners. Up to 25 km².'):message||'Find a place, then draw the area you want to explore.')}</p><Button type="button" variant="secondary" size="sm" disabled={disabled||drawing} onClick={()=>{const bounds=map.current?.getBounds();if(bounds)acceptBounds(bounds);}} title="Select the visible map" aria-label="Use visible map area"><Scan size={18}/><span className="satellite-use-view-label">Use view</span></Button></div>
    </div>
    <AmcheLayers map={mapInstance}/>
    {tileError&&<p className="satellite-note">Some street-map tiles could not load. Selected areas and loaded satellite images remain available.</p>}
    {observation&&<div className="satellite-map-caption"><p><strong>{dateLabel(observation.acquired_at[0])}</strong> · Sentinel-2, 10 m grid{!observation.map_layer?' · This saved observation predates map overlays; see its image below.':''}</p>
      {observation.map_layer&&<label>Imagery opacity <input type="range" min="0" max="100" value={opacity} onChange={e=>setOpacity(Number(e.target.value))}/><span>{opacity}%</span></label>}</div>}
  </div>;
}
