import {useEffect, useRef, useState} from 'react';
import L from 'leaflet';
import {Checkbox} from './components/arc/checkbox/checkbox';
import {AMCHE_LAYERS, amcheFeatureLabel, loadAmcheLayer, type AmcheLayerId} from './amche-layers';
import './amche-layers.css';

type LayerState = {checked: boolean; loading: boolean; message: string};
const initial = (): Record<AmcheLayerId, LayerState> => ({
  'water-bodies': {checked: false, loading: false, message: ''},
  'private-forests': {checked: false, loading: false, message: ''},
});

export function AmcheLayers({map}: {map: L.Map | null}) {
  const [state, setState] = useState(initial);
  const active = useRef(new Map<AmcheLayerId, L.GeoJSON>());
  const requests = useRef(new Map<AmcheLayerId, AbortController>());
  useEffect(() => {
    setState(initial());
    return () => {
      for (const request of requests.current.values()) request.abort();
      for (const layer of active.current.values()) layer.remove();
      requests.current.clear(); active.current.clear();
    };
  }, [map]);

  async function toggle(id: AmcheLayerId, checked: boolean) {
    requests.current.get(id)?.abort(); requests.current.delete(id);
    active.current.get(id)?.remove(); active.current.delete(id);
    setState(previous => ({...previous, [id]: {checked, loading: checked, message: ''}}));
    if (!checked || !map) return;
    const source = AMCHE_LAYERS.find(item => item.id === id)!;
    const controller = new AbortController(); requests.current.set(id, controller);
    const timeout = setTimeout(() => controller.abort(new Error('timeout')), 30_000);
    try {
      const data = await loadAmcheLayer(id, controller.signal);
      if (controller.signal.aborted) return;
      const layer = L.geoJSON(data, {
        attribution: source.attribution,
        style: {color: source.color, weight: 1.5, fillOpacity: .16},
        pointToLayer: (_feature, position) => L.circleMarker(position, {radius: 5, color: source.color, weight: 2, fillOpacity: .4}),
        onEachFeature: (feature, featureLayer) => {
          const label = document.createElement('div');
          const title = document.createElement('strong'); title.textContent = amcheFeatureLabel(feature.properties); label.append(title);
          const note = document.createElement('p'); note.textContent = `${source.date}. ${source.note}`; label.append(note);
          // Leaflet interprets string popup contents as HTML. Use DOM text nodes.
          featureLayer.bindPopup(label);
        },
      }).addTo(map);
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
      <Checkbox label={source.title} description={source.date} checked={state[source.id].checked} disabled={!map} onCheckedChange={checked => void toggle(source.id, checked===true)}/>
      <p className="amche-layer-status" role="status">{state[source.id].loading ? 'Loading mapped records…' : state[source.id].message}</p>
      <p>{source.note} <a href={source.sourceUrl} target="_blank" rel="noreferrer">Source records ↗</a></p>
    </div>)}</div>
    <p className="amche-layer-credit">Sources curated by <a href="https://amche.in/?atlas=goa" target="_blank" rel="noreferrer">Amche Atlas</a>. The base map is OpenStreetMap. Layers load only when selected.</p>
  </details>;
}
