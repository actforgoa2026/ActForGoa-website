# Map controls acceptance — 29 October 2026

The hosted drawing control previously kept Leaflet panning enabled and accepted only two corner clicks. A desktop drag reproduced the failure: no selected area and the prompt remained “Choose the first corner.”

The replacement intercepts pointer gestures while drawing, previews a rectangle, and commits either a drag or two opposite-corner taps. Cancellation and invalid selections leave the previous investigation intact. Area limits are unchanged. Search moves the view and marks the place; it does not silently replace a selected investigation area.

The workspace uses the actual existing Arc Button/SearchField components and shadcn/Radix Checkbox. The canvas spans the available width and can expand to the viewport. Escape exits drawing/expanded mode, and expanded keyboard focus stays within the controls. Location is requested only on an explicit click; coordinates are not stored or sent to geocoding. Street-map tiles still describe the area viewed.

## Verification before hosting

- 215 Node tests passed, including four new geocoder tests: Goa-only normalized results, cached duplicate requests, single-flight/rate bounds, oversized-response rejection and UTC daily reset.
- Integrated TypeScript/build and standalone Vite build passed. Existing bundle-size warning remains.
- Actual CUA browser checks at 1440×1000 and 390×844: drag selection; two-corner selection; Escape cancellation; oversized area feedback; expand/exit; map zoom; Panaji area lookup; real Artjuna business matches; no horizontal overflow.
- Phone toolbar clipping discovered during verification was fixed and checked again. Screenshots show the final selection and controls.
- Explicit location action was exercised. This browser did not provide a position within 10 seconds; the retry/search fallback appeared. A successful physical-device location fix is not claimed.
- Impeccable context, Operate guidance, craft floor, detector and rendered checks applied. Changed interface text is upright and no decorative side stripes were added.
- No new CDSE catalog, imagery, comparison or AI requests were needed for these interface checks. Existing hosted cached observations/history are the post-deployment regression target.

## Place search service

[Photon's official service guidance](https://github.com/komoot/photon#demo-server) permits modest use without an availability guarantee. Search is submit-only, cached for 24 hours in bounded memory, single-flight with at least 1.5 seconds between provider requests, and capped at 400 uncached requests per UTC day per single-replica app. No automatic retries, autocomplete, bulk lookup or reverse geocoding. A server-only `SATELLITE_GEOCODER_URL` can replace the compatible provider. The review-site handler uses the same standalone gateway, not another independently limited provider client. Queries are not logged by application code. Results and attribution identify Photon/OpenStreetMap; coverage is not complete.

Provider documentation: https://github.com/komoot/photon/blob/master/docs/api-v1.md
Pointer/map behavior: https://leafletjs.com/reference.html
Location permission: https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/getCurrentPosition

## Release boundary

This report records implementation and local acceptance. Hosting identity and hosted verification are recorded in coordination issue #89 after deployment. Existing satellite API, persistent volumes, named accounts, tokens, CDSE credentials, research corpus and accounting must remain unchanged. Only the standalone app package requires replacement; review-site promotion must use `release:review`.
