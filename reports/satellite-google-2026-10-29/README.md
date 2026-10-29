# Hosted Google integration acceptance

Live: https://satellite-app-production.up.railway.app/map

Runtime source: `df57d1b81a78fb2f25dfadb03fb389583e6ad3eb`, branch `codex/satellite-google`, based on main `1b16b874187027cb6b0d7d88b19ea0f0acdf2052`.

Both existing Railway services completed successfully:

- API: `906213da-e9c4-4524-9659-4e91d0e7cc46`
- App: `a231af84-a064-4baa-af37-c3611c98b009`

All 19 copied API runtime files and all 17 copied app/auth/static files hash-match their committed-source package manifests. Dockerfile and Railway configuration are packaging inputs rather than copied container files. Packages contained no credentials, environment files or SQLite databases.

## Real hosted checks

The authenticated website proxy returned four Earth Engine Sentinel-2 acquisitions for a small Ribandar-area footprint, 1–15 January 2026. Selected exact assets:

- `COPERNICUS/S2_SR_HARMONIZED/20260108T053109_20260108T054156_T43PCT`
- `COPERNICUS/S2_SR_HARMONIZED/20260113T053201_20260113T054409_T43PCT`

Both aligned rasters loaded, returned map overlays and retained provider/acquisition provenance. Their local usable fractions were 94.11% and 94.25%; common usable coverage was 94.11% across 2,813 pixels. A hosted comparison returned NDVI, NDWI and NBR metrics and an explicitly unavailable image-classifier state. This verifies integration, not ecological accuracy or field validation. No OpenAI or Anthropic model request ran.

The same-account observation reload returned `cache_hit: true`. Desktop and a confirmed 390×844 browser viewport reopened the saved comparison and switched the dated timeline. Current weather and Universal AQI loaded through the authenticated hosted interface, with timestamps and attribution. Geocoding, Places New and Routes each returned HTTP200 from the Railway API container; geocoding reported `OK`, Places returned a place ID, and Routes returned a distance and duration. The street map/search remain OSM/Photon; Google directions are an external Maps URL, not an embedded route overlay. No browser Maps JavaScript key was published.

Hosted reservations added: four catalog searches, two observation jobs, one comparison and one Google environment request (two provider calls). Three additional bounded direct Google API probes verified Geocoding, Places and Routes. No exact currency charge is asserted.

## Preservation and checks

Private SQLite backups precede configuration. All four previous jobs and both retained raw observations remain byte-identical to backup; the original staff account is unchanged. Temporary test-account sessions and temporary Railway SSH access were revoked after acceptance. Test observations remain actor-private under normal retention. Existing CDSE credentials, service tokens and volumes were preserved.

Automated checks: 140 Python satellite tests, 221 Node tests, production TypeScript/Vite build. Nonfatal warnings are existing Shapely/Starlette deprecations and build chunk-size advisories. The new environment action passed authentication, CSRF, request-limit and partial-provider-failure checks. UI review required removing one Unicode arrow; the reviewer scored that fix resolved with `disposition: ship`. The documenter found no durable design-system change. Existing typography documentation drift was left untouched. No Device Hub use occurred.

Private logs/manifests are under the isolated checkout's ignored `.reports/google-integration/`. Browser captures are local under the task visualization directory, including `hosted-earth-engine.jpg`, `hosted-earth-engine-mobile.jpg` and `hosted-google-conditions.jpg`.

The combined review alias, research runtime and actforgoa.org were not deployed. This runtime is live from the committed branch; merging its source is a separate repository action. OpenAI credential setup remains pending the user's key choice. Earth Engine currently uses the authorized read-only user credential; a dedicated hosted service identity is not provisioned by this change.


## Follow-up: Google map and OpenAI Decisions

The user approved Google street maps and place search, creation of a separate website-restricted browser key, and then supplied an existing OpenAI key and resumed Decisions activation. This supersedes the initial deferral above. `OPENAI_API_KEY` was saved privately outside the repository, verified against model access, and configured only on the hosted satellite API. Deployment `124d02d2-e583-47a0-82bc-fc5e9796b2fa` reuses runtime `df57d1b` and is successful.

One fresh hosted comparison reused the two retained Earth Engine rasters, returned all seven Decisions answers from `gpt-6-luna`, and reported 2,433 input tokens. Common usable coverage remained 94.11%. The website reopened this saved result and displayed the model, area scope, uncertain answers and uncalibrated-confidence qualification. This is an integration check, not a field accuracy assessment. API runtime hashes still match the original package, and all original jobs and rasters remain unchanged. The follow-up added one catalog search, one comparison and one classification reservation.

Google map implementation uses a separate browser configuration endpoint with no private-key fallback. Local acceptance verified a real Panaji Places search, geographic centering, pointer-drawn bounds, both Amche reference layers (3,854 water-body and 849 forest records), exact retained Earth Engine overlay alignment, opacity, timeline switching and mobile expansion/Escape. A reviewer requested keeping the acquisition date visible on the large map; it is now inside the existing status treatment. The user-approved larger map and Figtree refinement from the concurrent design chat are preserved. Browser captures use 1440×1000 and verified390×844 viewports, with no horizontal overflow or italic authored text.

Automated validation now passes223 Node tests and both main and standalone production builds; the prior140 satellite Python tests remain applicable because no Python source changed. Private Google, Earth Engine, OpenAI and service-token values are absent from browser artifacts. Frontend release identification and final restriction/cleanup verification will be added after deployment.
