# Goa map and acquisition timeline — 29 October 2026 (IST)

Final runtime source: `f181babf0b757e069f91609cbca0f8ee30e8adc9` (feature `cc1d399`, map-navigation correction `f181bab`), PR #95, reconciled with main `51abb34`. Implemented and tested; **this new runtime is not deployed or merged to main**. The existing standalone app at https://satellite-app-production.up.railway.app/map remains on the prior release. Its Copernicus credentials are still absent; the old static Vercel example is not this map flow.

## What changed

- Select a bounded Goa area by drawing, visible map extent or coordinates. Inspect actual Amche water-body/private-forest reference layers on OpenStreetMap with source dates and attribution. No Amche Mapbox token or application code was copied. Amche's deployed iframe lacks the location-sharing bridge in its current source, so full Atlas navigation is linked separately.
- Search dated acquisitions; move through real acquisition steps; explicitly load a date; mark before/after; run analysis separately. Moving the slider never fetches a new image or calls a model. Loaded images switch immediately and stay registered to the chosen area. Unloaded dates remove the previous overlay. The current server search window remains bounded to 120 days.
- Authenticated single-acquisition jobs, actor/scene/grid/ROI-specific persistent caching and reuse during comparisons. Browsing never calls a planner/classifier. The cache retains at most 60 entries/128 MiB raw imagery for 30 days; observation jobs remain out of saved comparison history.
- Display-only reprojection from native EPSG:32643 to EPSG:3857. One PNG serves both map and image views, avoiding duplicated base64 and oversized proxy responses. Native spectral measurements and classifier images are unchanged. Older saved results without georeferencing metadata are not placed by guessed bounds.

## Checks

**83 satellite Python tests, 202 Node tests, production build, standalone build and both allowlisted packages pass.** Tests cover projection/transparent masks, a valid 24.6 km² high-detail payload under the 4 MiB response cap, cache concurrency, actor/ROI isolation, restart persistence, chronology, provenance and no provider calls on cache hits. The API package has 17 files, app package 18; manifests contain hashes and source identity. No secret, database or raw raster is packaged.

Real local authentication/service with explicitly synthetic providers checks the full browser flow at 1440, 390 and 320 px: three-date scrubbing, explicit load only, new 202/cached 200 responses, cleared overlays, selected-date labels, before/after ordering, reuse, separate analysis, no horizontal overflow or page errors. Synthetic screenshots are visibly labelled; they are not field findings. The final browser run also fetches both actual pinned Amche datasets and replays the newly captured real river-area comparison locally without another CDSE request. These recorded-real screenshots are labelled local replay, not hosted acceptance.

A stronger phone check caught a saved-area fit being dropped during an active Leaflet zoom. The failure is retained; disabling zoom animation for this investigation map and stopping prior pan before fitting the selected area fixes it. Final desktop/phone checks confirm the real dated overlay actually intersects the visible map, rather than only checking that image bytes decoded.

Installed Impeccable skill was unavailable; existing design guidance and rendered desktop/phone inspection were used. Routine dependency/build size warnings remain.

## New real imagery evidence

Area `[73.878, 15.499, 73.892, 15.511]`, a Mandovi-area footprint independent of the original example. The October 1–28 catalog returned seven acquisitions, latest October 25. Exact October 20/25 observations were retrieved through the new authenticated observation/job path. Provider provenance and reprojected map extents are retained in `live-cdse-validation.json`; raw imagery/cache remain ignored.

Local usable fractions: **73.09% before, 59.31% after; common usable 53.98%**. The system correctly reports insufficient clear imagery for a reliable overall change finding. The common-clear subset contains a possible 19,200 m² increase in SCL water-classified pixels, but incomplete coverage, classification resolution, tides/seasonality and lack of field evidence prevent an overall river-change conclusion. No tree count, waste identification, cause or legal status is established.

Exactly two Process requests ran; revisiting an image made no network request, and comparison reused both cached native observations. The initial telemetry helper looked for the wrong Process URL suffix; the retained actual request log supports the corrected cache-reuse result. No provider request was repeated to fix reporting. Total reported CDSE processing units including initial catalog discovery: **0.7705907954287251**. This is not a currency amount. No live OpenAI/Anthropic inference ran.

## Hosting continuation

Update both existing Railway services from current PR #95 source and securely configure real CDSE variables on the satellite API service. Existing accounts, volumes, history and tokens must be preserved. This cloud executor cannot deploy through its current Railway credential host binding or export proxy placeholders. [Exact local continuation](../../docs/SATELLITE-LOCAL-DEPLOYMENT.md). OpenAI remains optional. No combined review alias, hosted secret, research generation, acceptance gate or accounting ledger was changed.
