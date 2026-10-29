import type {Feature, FeatureCollection, Geometry, GeoJsonProperties, Position} from 'geojson';

// A reviewed subset of publicmap/amche-atlas's Goa registry. Fetch these pinned
// datasets only when requested; do not execute registry JavaScript or adopt its
// Mapbox credentials. Upstream software licensing does not license its datasets.
// Registry: https://github.com/publicmap/amche-atlas/blob/main/config/goa.atlas.json
export const AMCHE_LAYERS = [
  {
    id: 'water-bodies', title: 'Water bodies', date: 'Water Body Atlas 2025', color: '#187eae',
    url: 'https://gist.githubusercontent.com/planemad/e5ccc47bf2a1aa458a86d6839476f539/raw/6922fcc2d5ffd4d58b0fb069b9f57334f13cd953/goa-water-bodies.geojson',
    sourceUrl: 'https://goawrd.gov.in/', sourceLabel: 'Goa Water Resources Department',
    attribution: 'Water Body Atlas of Goa · Goa Water Resources Department · via Amche Atlas',
    note: 'Mapped water bodies are reference records; their current water extent may differ.',
    maxBytes: 12_000_000,
  },
  {
    id: 'private-forests', title: 'Private forest records', date: 'June 2026 collection', color: '#8a642a',
    url: 'https://gist.githubusercontent.com/planemad/54b84c11fc0325889f1127e49b5740db/raw/1f99740ddb55a1528d76a5364aa9a95c1fe800da/goa_private_forest_plots-jun-2026.geojson',
    sourceUrl: 'https://docs.google.com/spreadsheets/d/1OHrd9c61IQ2rE_pKqPrtMgT5AY5Wepru/edit?gid=378361244',
    sourceLabel: 'Goa private forest records, collected by Amche community',
    attribution: 'Goa Private Forest Plots · Amche.in community',
    note: 'Some records are points or partial plot matches. These records do not establish present canopy or legal status.',
    maxBytes: 3_000_000,
  },
] as const;

export type AmcheLayerId = typeof AMCHE_LAYERS[number]['id'];
const fields = ['name', 'village', 'taluka', 'survey', 'subdivision', 'subdiv', 'purpose', 'condition', 'wb_id', 'match_accuracy', 'match_notes'] as const;
const invalid = () => new Error('This map layer has an unsupported or invalid geographic format.');
const record = (value: unknown): value is Record<string, unknown> => !!value && typeof value === 'object' && !Array.isArray(value);

export function validateAmcheGeoJSON(value: unknown): FeatureCollection {
  if (!record(value) || value.type !== 'FeatureCollection' || !Array.isArray(value.features) || value.features.length > 5000) throw invalid();
  if (value.crs != null) {
    if (!record(value.crs) || !record(value.crs.properties) || !['urn:ogc:def:crs:OGC:1.3:CRS84', 'EPSG:4326'].includes(String(value.crs.properties.name))) throw invalid();
  }
  let positions = 0;
  const position = (point: unknown): Position => {
    if (!Array.isArray(point) || point.length < 2 || point.length > 3 || !point.every(n => typeof n === 'number' && Number.isFinite(n)) || Math.abs(point[0]) > 180 || Math.abs(point[1]) > 90 || ++positions > 500_000) throw invalid();
    return [point[0], point[1]];
  };
  const polygon = (rings: unknown): Position[][] => {
    if (!Array.isArray(rings) || !rings.length) throw invalid();
    return rings.map(ring => {
      if (!Array.isArray(ring) || ring.length < 4) throw invalid();
      const points = ring.map(position), first = points[0], last = points[points.length - 1];
      if (first[0] !== last[0] || first[1] !== last[1]) throw invalid();
      return points;
    });
  };
  const features: Feature[] = value.features.map(item => {
    if (!record(item) || item.type !== 'Feature' || !record(item.geometry)) throw invalid();
    const {type, coordinates} = item.geometry;
    let geometry: Geometry;
    if (type === 'Point') geometry = {type, coordinates: position(coordinates)};
    else if (type === 'Polygon') geometry = {type, coordinates: polygon(coordinates)};
    else if (type === 'MultiPolygon' && Array.isArray(coordinates) && coordinates.length) geometry = {type, coordinates: coordinates.map(polygon)};
    else throw invalid();
    // Copy only useful, bounded public context labels. In particular do not
    // retain ownership names, arbitrary HTML, source URLs, or provider metadata.
    const properties: Record<string, string> = {};
    if (record(item.properties)) for (const key of fields) {
      const input = item.properties[key];
      if (typeof input === 'string' || typeof input === 'number') properties[key] = String(input).slice(0, 240);
    }
    return {type: 'Feature', geometry, properties};
  });
  return {type: 'FeatureCollection', features};
}

export function amcheFeatureLabel(properties: GeoJsonProperties): string {
  if (!properties) return 'Mapped record';
  const text = (key: string) => typeof properties[key] === 'string' ? properties[key].trim() : '';
  const name = text('name'), village = text('village'), taluka = text('taluka');
  const title = name && !['--', 'N/A'].includes(name) ? name : text('wb_id') || (text('survey') ? `Survey ${text('survey')}${text('subdivision') ? '/' + text('subdivision') : ''}` : 'Mapped record');
  return [title, village, taluka].filter(Boolean).join(' · ');
}

export async function loadAmcheLayer(id: AmcheLayerId, signal: AbortSignal, fetcher: typeof fetch = fetch): Promise<FeatureCollection> {
  const source = AMCHE_LAYERS.find(item => item.id === id);
  if (!source) throw new Error('Unknown map layer.');
  const response = await fetcher(source.url, {signal, mode: 'cors', credentials: 'omit', redirect: 'error', cache: 'force-cache'});
  if (!response.ok || !response.body) throw new Error('This map source is unavailable. You can still navigate and select an area.');
  if (Number(response.headers.get('content-length') || 0) > source.maxBytes) {
    await response.body.cancel();
    throw new Error('This map layer is larger than the supported download limit.');
  }
  const reader = response.body.getReader(), chunks: Uint8Array[] = [];
  let length = 0;
  try {
    while (true) {
      signal.throwIfAborted();
      const chunk = await reader.read();
      if (chunk.done) break;
      length += chunk.value.byteLength;
      if (length > source.maxBytes) throw new Error('This map layer is larger than the supported download limit.');
      chunks.push(chunk.value);
    }
  } catch (error) {
    await reader.cancel().catch(() => {});
    throw error;
  } finally {
    reader.releaseLock();
  }
  signal.throwIfAborted();
  const bytes = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  let json: unknown;
  try { json = JSON.parse(new TextDecoder().decode(bytes)); } catch { throw invalid(); }
  return validateAmcheGeoJSON(json);
}
