# Satellite continuation handoff

Source chat: **SAT IMAGE ANALYSIS**, ID `01a181d5-fcf6-745a-b440-89a455d69065`, host `durable`.

The user is moving to a new chat to pick up saved CDSE credentials. Continue the implementation; do not restart research from scratch. Read `AGENTS.md`, `docs/CLOUD-IMPLEMENTATION-PLAN.md`, `docs/GOA-MAP-INTELLIGENCE-PLAN.md`, and `reports/satellite-2026-10-28/README.md`.

## Latest continuation — 28 October 2026

The user subsequently explicitly instructed this chat to **get a version live for iteration**, without waiting for OpenAI. OpenAI configuration is optional for the initial imagery dashboard. A separate static recorded-imagery preview is being prepared from the real verified October pair, leaving the active combined release and existing review alias untouched. Entry: `satellite-preview.html`; isolated build: `npx vite build --config vite.satellite-preview.config.ts`. This preview has no new-area/provider requests or stored private results. It must remain clearly labelled recorded/read-only until the hosted service is connected.

Hosted comparison blocker is infrastructure access, separate from OpenAI: Railway now documents `https://backboard.railway.com/graphql/v2`; this cloud executor's credential is bound only to `backboard.railway.app`, which returns 403. The documented `.com` endpoint responds to an unauthenticated schema probe. Cloud tools can inspect but cannot change that binding, and no connected local browser is available. A local-thread deployment handoff was supplied at the user's request: deploy a new persistent satellite service using real securely configured CDSE credentials, connect the authenticated admin proxy, and coordinate frontend promotion with the active local ORCHESTRATOR. Do not copy cloud-injected placeholders into hosted secrets. Vercel API access is working; isolated preview publication is user-authorized.

The active draft is [PR #95](https://github.com/actforgoa2026/ActForGoa-website/pull/95), head branch `codex/satellite-monitoring`. Local continuation uses `codex/satellite-live-validation`. Update this PR rather than creating another. The user's goal is broader than canopy pairs: queryable time-based Goa investigations across trees, rivers, waste and development, with current imagery and cited ecological context.

Paired decisions/interpretation checkpoint `e705d69` adds yes/no/uncertain canopy presence at the same common-clear footprint, deterministic evidence-linked explanations, explicit disagreement and date-window caveats, persistent classification reservations and opt-in Anthropic vision. OpenAI Decisions is the default; no silent provider substitution. Its key is still absent and no live Decisions request has run.

The subsequent monitoring continuation adds authenticated private history (question/finding, topic, actual observation interval), reopening saved results, acquisition freshness, newer-scene counts, common-mask SCL water gains/losses and polygons, waste limitations, planning-law caveats, and bounded ecology passage retrieval with retained citations. Ecology retrieval uses `SATELLITE_RESEARCH_ORIGIN` and only `/api/search?domain=ecology`; it never generates a research answer or touches research accounting. The review endpoint is reachable but still returns the older unscoped response, so the live context gate correctly fails. See [current verification](../reports/satellite-decisions-2026-10-28/README.md) for 68 Python tests, 181 Node tests, build and desktop/phone checks. All model/source responses in the browser evidence are synthetic and labelled.

This dashboard covers saved user-selected areas, not statewide monitoring. History is private to each actor and limited to 30 days; catalog coverage is bounded to the chosen period and may be truncated. Place resolution, watch areas, multi-acquisition timelines, statewide processing/coverage, FIRMS and field accuracy remain unfinished. The broader product plan now records these explicitly. No merge or deployment has occurred.

Current implementation/runtime checkpoint: `f42617bb956f20c5b2ca921f3cf8e08226f3d3d8`. Its 17-file package and Docker build pass, including history isolation and saved results across restart. Current [manifest and container evidence](../reports/satellite-decisions-2026-10-28/README.md) supersede the earlier 15-file runtime for this dashboard. Later screenshot/docs corrections leave runtime source unchanged.

Secure OpenAI setup was resumed with the user's new `SatAnalysis2` selection (30-day expiry) and explicit approval to save `OPENAI_API_KEY` to ignored `/workspace/actforgoa-satellite/.env.local`. One encrypted creation request returned **“OpenAI Platform rejected the API key request.”** No specific reason, key or ciphertext was returned; no key was saved and no live Decisions request ran. Do not automatically retry or change the selected project/expiry. The packaged helper was absent; an independently reviewed local equivalent passed synthetic crypto/path/write checks before the request. Its temporary private key was removed after rejection. [Safe attempt record](../reports/satellite-decisions-2026-10-28/key-setup-attempt.json).

`scripts/validate-satellite-decisions.py` is ready for a future authorized live check after Platform access is resolved. It verifies the previously captured real rasters and acquisition provenance, uses the common-clear mask, reserves one persistent attempt per UTC day, calls Decisions once, and preserves sanitized status/usage/results or failure. Four new offline checks bring the satellite suite to **72 passing tests**. The actual recorded input pair also passes the new preflight without network calls. No dashboard/runtime source changed in this validation-script follow-up.

### Earlier live retrieval and package checkpoint

Recovered checkpoint `133bd4e` into `/workspace/actforgoa-satellite`, merged current main `a786df5` without conflicts (`f60597a`), and committed real imagery validation/fixes as `deb1f1d`. Both CDSE bindings are now ready **and actual OAuth, catalog and Process calls succeed**. The corrected Process request explicitly asks for `application/tar`; without it the provider returned only a TIFF and provenance validation stopped safely.

The real 10/20 October 2026 pair for the default Goa area passed acquisition, bundle, eight-band grid and numeric comparison checks with 100% common usable coverage. Zero patches met the exploratory vegetation-loss thresholds; this does not establish absence of tree removal. See [live evidence](../reports/satellite-live-2026-10-28/README.md). Tests now pass: 29 satellite Python, 181 Node, production build. Raw provider imagery remains under ignored `.reports/`; reviewed metadata and previews are committed. OpenAI Decisions remains unconfigured and untested; no classification call was attempted. The older credential and synthetic-only statements below describe the original executor, not this continuation.

Packaging and Docker verification also pass at runtime commit `ebf570a771396ad126960400faeef9f0ea50b9a8`. The packager emits 15 allowlisted files. The container initially exposed a missing Rasterio system dependency; `libexpat1` is now installed. Health, REST/MCP authentication, missing-provider abstention, persistent quota, private SQLite permissions and interrupted-job restart handling pass. Container tests used temporary local service tokens and no provider keys. All test containers were removed. No service or frontend was deployed.

## Recover the code

Repository: `actforgoa2026/ActForGoa-website`. Branch: `codex/satellite-monitoring`. Isolated worktree in the original executor: `/workspace/actforgoa-satellite`. Shared checkout `/workspace/ActForGoa-website` was left untouched. The feature branch starts from main `7bf1965a2c46f76537437a822056b2bf9023f96c`. Fetch current main and reconcile carefully; preserve other owners' work. No merge or deployment has been performed.

## What exists

- `/map` React/Leaflet Goa map, coordinate/area selection, natural-language preparation, dated catalog choice, background comparisons, actual date/visibility/uncertainty display and Amche links.
- Authenticated Python service under `satellite/`, persistent SQLite jobs/usage, REST and four stateless MCP tools. Existing named admin session and CSRF protection gates browser provider calls. Separate service and MCP bearer tokens.
- EVE-derived, attributed adapter for CDSE client-credentials OAuth, bounded STAC catalog and single-acquisition numeric Sentinel-2 L2A retrieval. Original unsafe save paths are not exposed. Grid-aligned reflectance, cloud/shadow masks, NDVI/NDWI/NBR and exploratory vegetation-loss patches.
- Anthropic query planner, validated server-side; optional OpenAI Decisions adapter for fixed image questions. Unknowns stay unknown. Same common-clear mask is applied to both model images. Canopy loss does not prove cutting, cause, exact timing or individual-tree counts.
- Allowlisted Railway service packaging and deployment instructions. Packager and Docker build/startup/persistence are verified at `ebf570a`; hosted Railway deployment remains pending.
- Detailed staged plan for Amche source registry and cadastral/place resolution, vector intersections, observation/event/coverage PostGIS index, statewide queries, FIRMS corroboration, evaluation and later alerts. These are planned, not implemented by the first prototype.

## Original checks and access (historical)

28 Python satellite tests, 181 Node tests and production build pass. Desktop/phone browser workflow passes with real local named-account authentication and clearly labelled synthetic imagery/providers; portable evidence is committed in the report directory. One live Anthropic request successfully planned the selected-area ten-day canopy question. No real satellite pair has been retrieved.

Original cloud environment ID: `ccarenv_b64_Y2NhcmVudl9iZGQwNmFkMGU4MTg4MTkxYTA1MmY0NjNhNzEyYmE4Nw`. Latest applied revision was 1; only Vercel/Railway/Anthropic bindings were present. User says CDSE secrets are definitely saved. Recheck safe readiness and variable presence in the new executor; never print values or ask for duplicate secrets in chat. Expected names: `CDSE_CLIENT_ID` and `CDSE_CLIENT_SECRET`. Token host `identity.dataspace.copernicus.eu`; imagery/catalog host `sh.dataspace.copernicus.eu`. The environment's outbound proxy must remain in use.

OpenAI key setup: user authorized secure key creation. Secure picker selected the project/key name and 30-day expiry, but creation/storage did not complete. A prompt to approve `/workspace/actforgoa-satellite/.env.local` as the local destination has not received a confirmation. Read the OpenAI key skill and resume the existing flow; do not claim an OpenAI key exists or create duplicates. Anthropic already works for planning. Decisions is optional until configured.

Vercel REST was accessible; project `prj_4BRx1f4MrLFE5p6Ljnhkp33TOltz`, account `team_HFlIoPSiBdah4eZZDkHUF4Z7`, project name `actforgoa-field-guide`. Only VITE_REPORT_API_ORIGIN was configured there at inspection. Railway control endpoint `https://backboard.railway.app/graphql/v2` returned Cloudflare 403; configured binding does not prove usable deployment access. Do not copy injected placeholder credentials into deployments.

## Next concrete steps

1. CDSE credential and bounded live retrieval checks are complete; read the live evidence linked above before making further provider calls. The corrected pair consumed 0.45450926254445223 reported processing units; the initial unbundled failure's usage was not captured. Keep this separate from currency costs and field accuracy. Do not automatically repeat successful or failed requests.
2. Main through `a786df5` was reconciled without conflicts and tests/build pass. Complete real Decisions smoke when secure key setup is resolved. Preserve failed checks and actual provenance.
3. Packaging/Docker checks are complete at `ebf570a`; use the committed manifest/container evidence. For deployment, package the final reviewed source again. Service must be a new Railway service with one replica, private persistent `/data/satellite`, separate server-only service/MCP tokens. Repackage admin service to include the satellite proxy. Do not replace research/reporting services or copy injected CDSE placeholders into hosted configuration.
4. Continue draft PR #95 and the coordinator's release process in `docs/RELEASING.md`; no independent review-alias promotion. Full release-route/browser acceptance is still required and other project acceptance blockers remain. Original actforgoa.org is out of scope.
5. Continue the plan's context/places/index work as appropriate. The current Amche integration is a location link, not ingested/queryable context. Current NL flow plans a bounded investigation; it does not yet answer statewide conversational queries from an event index. FIRMS, field accuracy and alerts are outstanding.

This branch changes no existing research ledger, production data, live secrets or deployment. No old local agent was resumed.
