# Satellite investigation workspace release

The user explicitly authorized shipping the completed local iteration on 30 October 2026. Release scope is the existing Railway satellite API and satellite app. The local workspace remains available through `npm run dev:satellite`, with the approved `http://127.0.0.1:4176` browser-key restriction. Main-site Vercel and the original domain are outside this release.

## Behavior

- Earth Engine supplies a dated, cloud-masked Sentinel-2 navigation overview. Exact observations supply analysis; the overview is not used as evidence of change.
- Drawing keeps the selected rectangle and automatically searches and loads its latest acquisition, with on-map progress and errors.
- Actual Arc Calendar/DatePicker, MorphSelect and Slider controls retain accessible interaction. Desktop uses a map and independently scrolling analysis column; phones stack the workflow.
- The visible change synopsis identifies completed, skipped or unavailable AI. OpenAI Decisions supplies bounded image assessments; spectral measurements and source imagery remain inspectable. The synopsis is not a second freeform model response or field validation.
- Main-site builds preserve Leaflet/Photon. Standalone and isolated satellite development use Google Maps/Places with Earth Engine imagery.

## Pre-deployment verification

All 254 Node tests, 142 satellite Python tests, TypeScript checks, main production build and standalone production build passed. Builds retain a nonblocking large-chunk warning. The Python suite reports existing raster/test warnings; no test failed.

Desktop 1452×759 and phone 390×844 browser checks cover the actual calendar, dated imagery, retained selection, Arc controls and saved real AI synopsis. Independent Impeccable release review: `ship`, no material visual fixes. It records a minor 3px excess document width at 390px, with no lost action or clipped reading content in the inspected frames; zero horizontal overflow is not claimed.

Local functional acceptance previously completed a real 10/20 October comparison over the user's selected area: 100% common usable coverage and seven completed OpenAI Decisions answers using `gpt-6-luna`. A cloudy September/October pair correctly skipped AI. These are functional checks, not field validation or a guarantee of tree-level detection. No new paid AI call is required solely to reopen this verified result.

Private SQLite backups precede the release. Final hosted deployment identities, runtime hash checks, data preservation, and browser acceptance are recorded below after deployment. Private evidence remains under ignored `.reports/satellite-release-20261030/`.

## Reconciliation with concurrent main-site work

PR #115 landed while the standalone release was being verified. Its integrated `Satellite.tsx`, history and layout stylesheet are preserved byte-for-byte. The standalone entry imports `SatelliteWorkspace.tsx`, its history and stylesheet, retaining the approved Earth Engine overview and open synopsis. The guide keeps its portalled Arc DatePicker; standalone keeps its accepted registry-derived inline variant. Both use the shared Calendar with the corrected disabled-Today state for bounded dates. The final preservation review is `ship`, and four new desktop/phone captures confirm the retained layout.

The runtime packages use explicit allowlists. Railway app uploads require `--path-as-root --no-gitignore` so compiled `dist-satellite` assets are included. An initial upload omitted that directory and failed before replacing the prior app; the corrected upload succeeded.
