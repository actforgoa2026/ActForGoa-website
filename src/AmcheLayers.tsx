import {useEffect, useRef, useState} from 'react';

import {Checkbox} from './components/ui/checkbox';
import {AMCHE_LAYERS, amcheFeatureLabel, loadAmcheLayer, type AmcheLayerId} from './amche-layers';
import './amche-layers.css';

type LayerState = {checked: boolean; loading: boolean; message: string};
const initial = (): Record<AmcheLayerId, LayerState> => ({
  'water-bodies': {checked: false, loading: false, message: ''},
  'private-forests': {checked: false, loading: false, message: ''},
});

export function AmcheLayers({map}: {map: google.maps.Map | null}) {
  const [state, setState] = useState(initial);
  const active = useRef(new Map<AmcheLayerId, google.maps.Data>());
  const popups = useRef(new Map<AmcheLayerId, google.maps.InfoWindow>());
  const requests = useRef(new Map<AmcheLayerId, AbortController>());
  useEffect(() => {
    setState(initial());
    return () => {
      for (const request of requests.current.values()) request.abort();
      for (const layer of active.current.values()) {layer.setMap(null);google.maps.event.clearInstanceListeners(layer);}
      for (const popup of popups.current.values()) popup.close();popups.current.clear();
      requests.current.clear(); active.current.clear();
    };
  }, [map]);

  async function toggle(id: AmcheLayerId, checked: boolean) {
    requests.current.get(id)?.abort(); requests.current.delete(id);
    const previousLayer=active.current.get(id);if(previousLayer){previousLayer.setMap(null);google.maps.event.clearInstanceListeners(previousLayer);}active.current.delete(id);
    popups.current.get(id)?.close();popups.current.delete(id);
    setState(previous => ({...previous, [id]: {checked, loading: checked, message: ''}}));
    if (!checked || !map) return;
    const source = AMCHE_LAYERS.find(item => item.id === id)!;
    const controller = new AbortController(); requests.current.set(id, controller);
    const timeout = setTimeout(() => controller.abort(new Error('timeout')), 30_000);
    try {
      const data = await loadAmcheLayer(id, controller.signal);
      if (controller.signal.aborted) return;
      const layer=new google.maps.Data({map});
      layer.addGeoJson(data);
      layer.setStyle({strokeColor:source.color,strokeWeight:1.5,fillColor:source.color,fillOpacity:.16,zIndex:2,icon:{path:google.maps.SymbolPath.CIRCLE,scale:5,strokeColor:source.color,strokeWeight:2,fillColor:source.color,fillOpacity:.4}});
      const popup=new google.maps.InfoWindow();popups.current.set(id,popup);
      layer.addListener('click',(event:google.maps.Data.MouseEvent)=>{
        const properties:Record<string,unknown>={};event.feature.forEachProperty((value,name)=>{properties[name]=value;});
        const label=document.createElement('div');
        const title=document.createElement('strong');title.textContent=amcheFeatureLabel(properties);label.append(title);
        const note=document.createElement('p');note.textContent=`${source.date}. ${source.note}`;label.append(note);
        popup.setContent(label);popup.setPosition(event.latLng);popup.open({map,shouldFocus:false});
      });
      active.current.set(id, layer);
      setState(previous => ({...previous, [id]: {checked: true, loading: false, message: `${data.features.length.toLocaleString('en-IN')} mapped records`}}));
    } catch (error) {
      if (requests.current.get(id) !== controller) return;
      const message = controller.signal.aborted ? 'This source took too long to load. Toggle it to try again.' : error instanceof Error ? error.message : 'This map source is unavailable.';
      setState(previous => ({...previous, [id]: {checked: false, loading: false, message}}));
    } finally {
      clearTimeout(timeout);
      if (requests.current.get(id) === controller) requests.current.delete(id);
    }
  }

  return <details className="amche-layers"><summary>Local context from Amche Atlas</summary>
    <p>Show reference records on this map. Their dates are separate from the satellite observations.</p>
    <div className="amche-layer-options">{AMCHE_LAYERS.map(source => <div className="amche-layer-option" key={source.id}>
      <label><Checkbox checked={state[source.id].checked} disabled={!map} onCheckedChange={checked => void toggle(source.id, checked===true)}/><span>{source.title}<small>{source.date}</small></span></label>
      <p className="amche-layer-status" role="status">{state[source.id].loading ? 'Loading mapped records…' : state[source.id].message}</p>
      <p>{source.note} <a href={source.sourceUrl} target="_blank" rel="noreferrer">Source records</a></p>
    </div>)}</div>
    <p className="amche-layer-credit">Sources curated by <a href="https://amche.in/?atlas=goa" target="_blank" rel="noreferrer">Amche Atlas</a>. The base map is Google Maps. Layers load only when selected.</p>
  </details>;
}
