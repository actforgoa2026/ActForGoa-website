import test from 'node:test';
import assert from 'node:assert/strict';
import {amcheFeatureLabel, loadAmcheLayer, validateAmcheGeoJSON} from '../src/amche-layers.ts';

const collection = (properties: Record<string, unknown> = {}) => ({type: 'FeatureCollection', features: [{type: 'Feature', geometry: {type: 'Point', coordinates: [73.8, 15.5]}, properties}]});

test('Amche context retains bounded geographic labels without ownership or HTML fields', () => {
  const result = validateAmcheGeoJSON(collection({name: '<img src=x onerror=alert(1)>', village: 'Paliem', owners: 'A person', html: '<script>', url: 'javascript:alert(1)', condition: 'x'.repeat(1000)}));
  assert.equal(result.features[0].properties?.owners, undefined);
  assert.equal(result.features[0].properties?.html, undefined);
  assert.equal(result.features[0].properties?.url, undefined);
  assert.equal(result.features[0].properties?.condition.length, 240);
  assert.equal(amcheFeatureLabel(result.features[0].properties), '<img src=x onerror=alert(1)> · Paliem'); // Rendered as DOM text, never innerHTML.
});

test('Amche context rejects unsupported projections and malformed geometry', () => {
  assert.throws(() => validateAmcheGeoJSON({...collection(), crs: {type: 'name', properties: {name: 'EPSG:32643'}}}));
  const invalid = collection(); invalid.features[0].geometry.coordinates = [700000, 1500000];
  assert.throws(() => validateAmcheGeoJSON(invalid));
  assert.throws(() => validateAmcheGeoJSON({...collection(), features: Array(5001).fill(collection().features[0])}));
  assert.throws(() => validateAmcheGeoJSON({type: 'FeatureCollection', features: [{type: 'Feature', geometry: {type: 'Polygon', coordinates: [[[73,15],[74,15],[74,16],[73,16]]]}, properties: {}}]}));
});

test('Amche layer requests fixed public source without credentials or redirects', async () => {
  const fake: typeof fetch = async (input, options) => {
    assert.match(String(input), /^https:\/\/gist\.githubusercontent\.com\/planemad\//);
    assert.equal(options?.credentials, 'omit'); assert.equal(options?.redirect, 'error');
    return new Response(JSON.stringify(collection({name: 'Test lake'})));
  };
  assert.equal((await loadAmcheLayer('water-bodies', new AbortController().signal, fake)).features.length, 1);
});

test('Amche download rejects oversized streamed responses without trusting content-length', async () => {
  let cancelled = false;
  const fake: typeof fetch = async () => new Response(new ReadableStream({start(controller) {controller.enqueue(new Uint8Array(3_000_001));}, cancel() {cancelled = true;}}));
  await assert.rejects(loadAmcheLayer('private-forests', new AbortController().signal, fake), /download limit/);
  assert.equal(cancelled, true);
});
