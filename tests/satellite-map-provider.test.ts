import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {build, resolveConfig, type Plugin} from 'vite';

const root = fileURLToPath(new URL('../', import.meta.url));
const probeProviders: Plugin = {
  name: 'isolated-map-provider-probe',
  enforce: 'pre',
  resolveId(id) {
    if (id === './SatelliteGoogleMap') return '\0map-provider:google';
    if (id === './SatelliteLeafletMap') return '\0map-provider:leaflet';
  },
  load(id) {
    if (id === '\0map-provider:google') return 'export function SatelliteGoogleMap(){return "GOOGLE_PROVIDER_SENTINEL"}';
    if (id === '\0map-provider:leaflet') return 'export function SatelliteLeafletMap(){return "LEAFLET_PROVIDER_SENTINEL"}';
  },
};

test('standalone config selects satellite mode while retaining a production build', async () => {
  const config = await resolveConfig({root, configFile: root + 'vite.satellite.config.ts', envDir: false, logLevel: 'silent'}, 'build', 'production', 'production');
  assert.equal(config.mode, 'satellite');
  assert.equal(config.env.MODE, 'satellite');
  assert.equal(config.env.PROD, true);
});

test('main and local builds exclude Google; only standalone includes it', async () => {
  // Bundle the real provider boundary with harmless stand-ins for map vendors.
  // This checks import elimination without requesting tiles, Places or any key.
  for (const mode of ['production', 'development', 'satellite']) {
    const result = await build({
      root, configFile: false, envDir: false, publicDir: false, mode, logLevel: 'silent', plugins: [probeProviders],
      build: {write: false, emptyOutDir: false, minify: false, rollupOptions: {input: root + 'src/SatelliteMap.tsx', preserveEntrySignatures: 'strict', external: ['react']}},
    });
    const outputs = (Array.isArray(result) ? result : [result]).flatMap(item => 'output' in item ? item.output : []);
    const code = outputs.filter(item => item.type === 'chunk').map(item => item.code).join('\n');
    const standalone = mode === 'satellite';
    assert.equal(code.includes('GOOGLE_PROVIDER_SENTINEL'), standalone, `${mode}: Google import`);
    assert.equal(code.includes('LEAFLET_PROVIDER_SENTINEL'), !standalone, `${mode}: Leaflet import`);
  }
});
