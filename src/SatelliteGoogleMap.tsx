import {Slider} from './components/arc/slider/slider';
import {useEffect,useRef,useState,type FormEvent,type PointerEvent as ReactPointerEvent} from 'react';
import {bboxBounds,boundsBbox,GOA_BOUNDS,loadGoogleMap,searchGooglePlaces,withinGoa} from './google-map';
import {LocateFixed,Maximize2,Minimize2,Minus,Plus,Scan,SquareDashed,X,MapPin,Search} from 'lucide-react';
import {AmcheGoogleLayers} from './AmcheGoogleLayers';
import {Button} from './components/arc/button/button';
import {SearchField} from './components/arc/search-field/search-field';
import type {SatelliteArea,SatelliteObservation} from './satellite-api';
import {areaError} from './satellite-timeline';
import {observationDate as dateLabel} from './SatelliteHistory';

type Place={id:string;name:string;detail:string;longitude:number;latitude:number};
export function SatelliteGoogleMap({area,onArea,observation,candidates,disabled=false}:{area:SatelliteArea|null;onArea:(area:SatelliteArea)=>void;observation?:SatelliteObservation;candidates?:GeoJSON.FeatureCollection;disabled?:boolean}) {
  const container=useRef<HTMLDivElement>(null),workspace=useRef<HTMLDivElement>(null),map=useRef<google.maps.Map|null>(null),selection=useRef<google.maps.Rectangle|null>(null),features=useRef<google.maps.Data|null>(null),overlay=useRef<google.maps.GroundOverlay|null>(null);
  const preview=useRef<google.maps.Rectangle|null>(null),pin=useRef<google.maps.Circle|null>(null),anchor=useRef<google.maps.LatLng|null>(null),cornerPin=useRef<google.maps.Circle|null>(null),projection=useRef<google.maps.OverlayView|null>(null);
  const press=useRef<{x:number;y:number;second:boolean}|null>(null),searchRequest=useRef(0),locationAttempt=useRef(0);
  const [mapInstance,setMapInstance]=useState<google.maps.Map|null>(null),[mapError,setMapError]=useState(''),[loadAttempt,setLoadAttempt]=useState(0);
  const [drawing,setDrawing]=useState(false),[corner,setCorner]=useState(false),[expanded,setExpanded]=useState(false),[opacity,setOpacity]=useState(100);
  const [message,setMessage]=useState(''),[selectionError,setSelectionError]=useState(''),[locating,setLocating]=useState(false);
  const [viewport,setViewport]=useState<SatelliteArea['bbox']|null>(null);
  const [query,setQuery]=useState(''),[places,setPlaces]=useState<Place[]>([]),[searching,setSearching]=useState(false),[searchMessage,setSearchMessage]=useState('');
  function clearDraft(){preview.current?.setMap(null);preview.current=null;cornerPin.current?.setMap(null);cornerPin.current=null;anchor.current=null;press.current=null;setCorner(false);}
  function cancelDraw(){clearDraft();setDrawing(false);setSelectionError('');}
  useEffect(()=>{
    let cancelled=false,instance:google.maps.Map|undefined,resize:ResizeObserver|undefined,listener:google.maps.MapsEventListener|undefined;
    setMapError('');
    const authWindow=window as Window&{gm_authFailure?:()=>void};
    const previousAuthFailure=authWindow.gm_authFailure;
    const authFailure=()=>{if(!cancelled)setMapError('Google Maps could not authorize this website. Use coordinates below, or ask the site administrator to check its map key.');};
    authWindow.gm_authFailure=authFailure;
    void loadGoogleMap().then(({Map,OverlayView})=>{
      if(cancelled||!container.current)return;
      instance=new Map(container.current,{center:{lat:15.4,lng:74},zoom:10,minZoom:8,maxZoom:19,restriction:{latLngBounds:GOA_BOUNDS,strictBounds:false},disableDefaultUI:true,clickableIcons:false,mapTypeId:'roadmap',renderingType:google.maps.RenderingType.RASTER,tilt:0,gestureHandling:'greedy',keyboardShortcuts:true});
      map.current=instance;
      class Projection extends OverlayView {onAdd(){} draw(){} onRemove(){}}
      const helper=new Projection();helper.setMap(instance);projection.current=helper;
      const updateViewport=()=>{const bounds=instance?.getBounds();if(bounds)setViewport(boundsBbox(bounds));};
      listener=instance.addListener('idle',updateViewport);
      resize=new ResizeObserver(()=>{if(instance){google.maps.event.trigger(instance,'resize');updateViewport();}});resize.observe(container.current);
      setMapInstance(instance);
    }).catch(error=>{if(!cancelled)setMapError(error instanceof Error&&error.message.startsWith('Google Maps is not configured')?error.message:'Google Maps could not load. Check your connection and retry, or use coordinates below.');});
    return()=>{
      cancelled=true;resize?.disconnect();listener?.remove();clearDraft();searchRequest.current++;locationAttempt.current++;
      selection.current?.setMap(null);features.current?.setMap(null);overlay.current?.setMap(null);pin.current?.setMap(null);projection.current?.setMap(null);projection.current=null;
      if(instance)google.maps.event.clearInstanceListeners(instance);
      if(container.current)container.current.replaceChildren();
      if(authWindow.gm_authFailure===authFailure)authWindow.gm_authFailure=previousAuthFailure;
      map.current=null;setMapInstance(null);setViewport(null);
    };
  },[loadAttempt]);
  useEffect(()=>{if(disabled)cancelDraw();},[disabled]);
  useEffect(()=>{
    map.current?.setOptions({gestureHandling:drawing?'none':'greedy',disableDoubleClickZoom:drawing,keyboardShortcuts:!drawing});
  },[drawing,mapInstance]);
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
    if(!mapInstance)return;
    cancelDraw();setMessage('');pin.current?.setMap(null);pin.current=null;selection.current?.setMap(null);selection.current=null;
    if(area){const bounds=bboxBounds(area.bbox);selection.current=new google.maps.Rectangle({map:mapInstance,bounds,strokeColor:'#193e32',strokeWeight:3,fillOpacity:.06,clickable:false});
      // Zoom in before recentering so the broad Goa restriction cannot clamp
      // a coastal selection to the middle of the state at the overview zoom.
      mapInstance.setZoom(16);
      mapInstance.fitBounds(bounds,48);
      google.maps.event.addListenerOnce(mapInstance,'idle',()=>{if((mapInstance.getZoom()||0)>16)mapInstance.setZoom(16);});}
  },[area,mapInstance]);
  useEffect(()=>{
    features.current?.setMap(null);features.current=null;
    if(mapInstance&&candidates){const data=new google.maps.Data({map:mapInstance});data.addGeoJson(candidates);data.setStyle({strokeColor:'#8a391f',strokeWeight:2,fillColor:'#8a391f',fillOpacity:.22,clickable:false,zIndex:3});features.current=data;}
    return()=>{features.current?.setMap(null);features.current=null;};
  },[candidates,mapInstance]);
  useEffect(()=>{
    overlay.current?.setMap(null);overlay.current=null;
    if(mapInstance&&observation?.map_layer){const layer=new google.maps.GroundOverlay(observation.image,bboxBounds(observation.map_layer.bbox),{clickable:false,opacity:opacity/100});layer.setMap(mapInstance);overlay.current=layer;}
    return()=>{overlay.current?.setMap(null);overlay.current=null;};
  },[observation,mapInstance]);
  useEffect(()=>{overlay.current?.setOpacity(opacity/100);},[opacity,observation,mapInstance]);
  const viewportError=viewport?areaError(viewport):'The map is loading.';
  const viewportGuidance=viewportError==='Choose a valid area around Goa.'?'Zoom in within Goa, or draw a smaller area up to 25 km².':viewportError;
  function showDraft(bounds:google.maps.LatLngBounds){
    if(!map.current)return;
    const error=areaError(boundsBbox(bounds));
    const style={strokeColor:error?'#8a391f':'#193e32',strokeWeight:2,fillColor:error?'#8a391f':'#193e32',fillOpacity:.16,clickable:false};
    if(preview.current)preview.current.setOptions({...style,bounds});
    else preview.current=new google.maps.Rectangle({...style,bounds,map:map.current});
    setSelectionError(error||'');
  }
  function acceptBounds(bounds:google.maps.LatLngBounds){
    const bbox=boundsBbox(bounds),error=areaError(bbox);
    if(error){if(anchor.current)showDraft(bounds);else setSelectionError(error);return false;}
    clearDraft();onArea({bbox});setDrawing(false);setSelectionError('');setMessage('Area selected. Choose dates below to find observations.');return true;
  }
  function pointerPosition(event:ReactPointerEvent<HTMLDivElement>){
    const box=container.current?.getBoundingClientRect(),project=projection.current?.getProjection();
    return box&&project?project.fromContainerPixelToLatLng(new google.maps.Point(event.clientX-box.left,event.clientY-box.top)):null;
  }
  function pointerDown(event:ReactPointerEvent<HTMLDivElement>){
    if(disabled||!map.current||event.button!==0||!event.isPrimary)return;
    const position=pointerPosition(event);if(!position)return;
    event.preventDefault();event.currentTarget.setPointerCapture(event.pointerId);setSelectionError('');
    press.current={x:event.clientX,y:event.clientY,second:!!anchor.current};
    if(!anchor.current){anchor.current=position;cornerPin.current=new google.maps.Circle({map:map.current,center:position,radius:12,strokeColor:'#193e32',fillColor:'#fff',fillOpacity:1,clickable:false});setCorner(true);}
  }
  function pointerMove(event:ReactPointerEvent<HTMLDivElement>){
    if(!event.isPrimary||!anchor.current||!map.current)return;
    const position=pointerPosition(event);if(position)showDraft(new google.maps.LatLngBounds().extend(anchor.current).extend(position));
  }
  function pointerUp(event:ReactPointerEvent<HTMLDivElement>){
    if(!event.isPrimary)return;
    const start=press.current;press.current=null;
    if(event.currentTarget.hasPointerCapture(event.pointerId))event.currentTarget.releasePointerCapture(event.pointerId);
    const position=pointerPosition(event);
    if(!start||!anchor.current||!position)return;
    if(start.second||Math.hypot(event.clientX-start.x,event.clientY-start.y)>=5)acceptBounds(new google.maps.LatLngBounds().extend(anchor.current).extend(position));
  }
  function showPlace(latitude:number,longitude:number,label:string,zoom=15){
    cancelDraw();pin.current?.setMap(null);if(!map.current)return;
    const center={lat:latitude,lng:longitude};map.current.setZoom(zoom);map.current.setCenter(center);
    pin.current=new google.maps.Circle({map:map.current,center,radius:35,strokeColor:'#fff',strokeWeight:3,fillColor:'#193e32',fillOpacity:1,clickable:false});
    setMessage(label+'. Draw an area around the place you want to investigate.');
  }
  async function search(event:FormEvent){
    event.preventDefault();if(searching||query.trim().length<3||!mapInstance)return;
    const request=++searchRequest.current;setSearching(true);setSearchMessage('');setPlaces([]);
    try{
      const results=await searchGooglePlaces(query.trim());
      if(request!==searchRequest.current)return;
      setPlaces(results);setSearchMessage(results.length?'Choose a place to move the map.':'No matching places around Goa. Try the business name with its village or town.');
    }catch{if(request===searchRequest.current)setSearchMessage('Google place search is unavailable. Retry, or navigate the map to choose an area.');}
    finally{if(request===searchRequest.current)setSearching(false);}
  }
  function locate(){
    if(!navigator.geolocation){setMessage('This browser does not support location. Search for a place instead.');return;}
    const attempt=++locationAttempt.current;setLocating(true);setMessage('Waiting for your location permission…');
    navigator.geolocation.getCurrentPosition(position=>{
      if(attempt!==locationAttempt.current)return;setLocating(false);
      const {latitude,longitude}=position.coords;
      if(!withinGoa(latitude,longitude)){setMessage('Your current location is outside the Goa map. Search for a place in Goa instead.');return;}
      showPlace(latitude,longitude,'Your approximate location');
    },error=>{if(attempt!==locationAttempt.current)return;setLocating(false);setMessage(error.code===1?'Location access was declined. Allow it in your browser settings, or search for a place.':error.code===3?'Location took too long. Try again or search for a place.':'Your location is unavailable. Try again or search for a place.');},{enableHighAccuracy:false,timeout:10000,maximumAge:60000});
  }
  return <div ref={workspace} className={'satellite-map-section'+(expanded?' satellite-map-expanded':'')}>
    <div className="satellite-map-search">
      <form onSubmit={search}><SearchField label="Find an area or business in Goa" placeholder="Search places in Goa" value={query} maxLength={120} minLength={3} onValueChange={value=>{setQuery(value);searchRequest.current++;setSearching(false);setPlaces([]);setSearchMessage('');}}/><Button type="submit" size="sm" loading={searching} disabled={query.trim().length<3||!mapInstance||!!mapError} aria-label="Search places"><Search size={18} aria-hidden="true"/></Button></form>
      <div className="satellite-map-tools">
        <Button type="button" size="sm" variant={drawing?'primary':'secondary'} aria-pressed={drawing} disabled={disabled||!mapInstance||!!mapError} onClick={()=>{if(drawing)cancelDraw();else{clearDraft();setSelectionError('');setDrawing(true);}}}>{drawing?<X size={18}/>:<SquareDashed size={18}/>}<span>{drawing?'Cancel drawing':'Draw area'}</span></Button>
        <Button type="button" size="sm" variant="secondary" loading={locating} disabled={!mapInstance||!!mapError} onClick={locate} title="Use my current location" aria-label="Use my current location"><LocateFixed size={18}/></Button>
        <Button type="button" size="sm" variant="secondary" aria-label={expanded?'Exit expanded map':'Expand map'} title={expanded?'Exit expanded map':'Expand map'} aria-pressed={expanded} onClick={()=>setExpanded(v=>!v)}>{expanded?<Minimize2 size={18}/>:<Maximize2 size={18}/>}</Button>
      </div>
    </div>
    {(searchMessage||places.length>0)&&<div className="satellite-place-results"><p role="status">{searchMessage}</p>{places.length>0&&<ul>{places.map(place=><li key={place.id}><Button type="button" variant="ghost" onClick={()=>{showPlace(place.latitude,place.longitude,place.name);setPlaces([]);setSearchMessage('');}}><MapPin size={18} aria-hidden="true"/><span><strong>{place.name}</strong>{place.detail&&<small>{place.detail}</small>}</span></Button></li>)}</ul>}<p className="satellite-search-credit">Search by Google Maps.</p></div>}
    <div className="satellite-map-canvas">
      <div ref={container} className="satellite-map" aria-label="Goa investigation map. Pan and zoom, then draw an area. The analysis panel has coordinate fields as a keyboard alternative." />
      {(!mapInstance||mapError)&&<div className="satellite-map-loading" role="status"><p>{mapError||'Loading Google Maps…'}</p>{mapError&&<Button type="button" variant="secondary" size="sm" onClick={()=>setLoadAttempt(value=>value+1)}>Retry map</Button>}</div>}
      {drawing&&!mapError&&<div className="satellite-draw-surface" role="group" tabIndex={0} aria-label="Draw a rectangle by dragging or tapping two opposite corners. Escape cancels." onPointerDown={pointerDown} onPointerMove={pointerMove} onPointerUp={pointerUp} onPointerCancel={clearDraft} onLostPointerCapture={()=>{if(press.current)clearDraft();}}/>}
      {mapInstance&&!mapError&&<><div className="satellite-map-zoom"><Button type="button" size="sm" variant="secondary" aria-label="Zoom in" disabled={drawing||!mapInstance||!!mapError} onClick={()=>{const m=map.current;if(m)m.setZoom((m.getZoom()||10)+1);}}><Plus size={20}/></Button><Button type="button" size="sm" variant="secondary" aria-label="Zoom out" disabled={drawing||!mapInstance||!!mapError} onClick={()=>{const m=map.current;if(m)m.setZoom((m.getZoom()||10)-1);}}><Minus size={20}/></Button></div>
      <div className="satellite-map-bottom"><p id="satellite-map-selection-status" role="status">{observation?.map_layer&&<strong className="satellite-map-date">{dateLabel(observation.acquired_at[0])} · Sentinel-2</strong>}{selectionError|| (drawing?(corner?'Drag or tap the opposite corner. Escape cancels.':'Drag a rectangle, or tap two opposite corners. Up to 25 km².'):[message,viewportGuidance].filter(Boolean).join(' ')||(area?'Selected area. Explore its dated imagery in the analysis panel.':'Find a place, then draw the area you want to explore.'))}</p><Button type="button" variant="secondary" size="sm" disabled={disabled||drawing||!!viewportError||!!mapError} aria-describedby="satellite-map-selection-status" onClick={()=>{const bounds=map.current?.getBounds();if(bounds)acceptBounds(bounds);}} title={viewportGuidance||'Select the visible map'} aria-label="Use visible map area"><Scan size={18}/><span className="satellite-use-view-label">Use view</span></Button></div></>}
    </div>
    <AmcheGoogleLayers map={mapInstance}/>

    {observation&&<div className="satellite-map-caption"><p><strong>{dateLabel(observation.acquired_at[0])}</strong> · Contains modified Copernicus Sentinel data · 10 m grid · {observation.provider==='earth-engine'?'Google Earth Engine':'Copernicus Data Space'}{!observation.map_layer?' · This saved observation predates map overlays; see its image below.':''}</p>
      {observation.map_layer&&<Slider label="Imagery opacity" min={0} max={100} value={opacity} onValueChange={setOpacity} format={value=>`${value}%`}/>}</div>}
  </div>;
}
