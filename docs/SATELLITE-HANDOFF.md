# Satellite continuation handoff

Source chat: **SAT IMAGE ANALYSIS**, ID `01a181d5-fcf6-745a-b440-89a455d69065`, host `durable`.

The user is moving to a new chat to pick up saved CDSE credentials. Continue the implementation; do not restart research from scratch. Read `AGENTS.md`, `docs/CLOUD-IMPLEMENTATION-PLAN.md`, `docs/GOA-MAP-INTELLIGENCE-PLAN.md`, and `reports/satellite-2026-10-28/README.md`.

## Recover the code

Repository: `actforgoa2026/ActForGoa-website`. Branch: `codex/satellite-monitoring`. Isolated worktree in the original executor: `/workspace/actforgoa-satellite`. Shared checkout `/workspace/ActForGoa-website` was left untouched. The feature branch starts from main `7bf1965a2c46f76537437a822056b2bf9023f96c`. Fetch current main and reconcile carefully; preserve other owners' work. No merge or deployment has been performed.

## What exists

- `/map` React/Leaflet Goa map, coordinate/area selection, natural-language preparation, dated catalog choice, background comparisons, actual date/visibility/uncertainty display and Amche links.
- Authenticated Python service under `satellite/`, persistent SQLite jobs/usage, REST and four stateless MCP tools. Existing named admin session and CSRF protection gates browser provider calls. Separate service and MCP bearer tokens.
- EVE-derived, attributed adapter for CDSE client-credentials OAuth, bounded STAC catalog and single-acquisition numeric Sentinel-2 L2A retrieval. Original unsafe save paths are not exposed. Grid-aligned reflectance, cloud/shadow masks, NDVI/NDWI/NBR and exploratory vegetation-loss patches.
- Anthropic query planner, validated server-side; optional OpenAI Decisions adapter for fixed image questions. Unknowns stay unknown. Same common-clear mask is applied to both model images. Canopy loss does not prove cutting, cause, exact timing or individual-tree counts.
- Allowlisted Railway service packaging and deployment instructions. Packager is not yet exercised against a committed checkpoint; Docker build is unverified.
- Detailed staged plan for Amche source registry and cadastral/place resolution, vector intersections, observation/event/coverage PostGIS index, statewide queries, FIRMS corroboration, evaluation and later alerts. These are planned, not implemented by the first prototype.

## Checks and access

28 Python satellite tests, 181 Node tests and production build pass. Desktop/phone browser workflow passes with real local named-account authentication and clearly labelled synthetic imagery/providers; portable evidence is committed in the report directory. One live Anthropic request successfully planned the selected-area ten-day canopy question. No real satellite pair has been retrieved.

Original cloud environment ID: `ccarenv_b64_Y2NhcmVudl9iZGQwNmFkMGU4MTg4MTkxYTA1MmY0NjNhNzEyYmE4Nw`. Latest applied revision was 1; only Vercel/Railway/Anthropic bindings were present. User says CDSE secrets are definitely saved. Recheck safe readiness and variable presence in the new executor; never print values or ask for duplicate secrets in chat. Expected names: `CDSE_CLIENT_ID` and `CDSE_CLIENT_SECRET`. Token host `identity.dataspace.copernicus.eu`; imagery/catalog host `sh.dataspace.copernicus.eu`. The environment's outbound proxy must remain in use.

OpenAI key setup: user authorized secure key creation. Secure picker selected the project/key name and 30-day expiry, but creation/storage did not complete. A prompt to approve `/workspace/actforgoa-satellite/.env.local` as the local destination has not received a confirmation. Read the OpenAI key skill and resume the existing flow; do not claim an OpenAI key exists or create duplicates. Anthropic already works for planning. Decisions is optional until configured.

Vercel REST was accessible; project `prj_4BRx1f4MrLFE5p6Ljnhkp33TOltz`, account `team_HFlIoPSiBdah4eZZDkHUF4Z7`, project name `actforgoa-field-guide`. Only VITE_REPORT_API_ORIGIN was configured there at inspection. Railway control endpoint `https://backboard.railway.app/graphql/v2` returned Cloudflare 403; configured binding does not prove usable deployment access. Do not copy injected placeholder credentials into deployments.

## Next concrete steps

1. Check newly applied CDSE variables, then run one bounded OAuth/catalog/Process smoke for the documented Goa AOI. Validate actual TAR response names, TIFF grid/band order, scene timestamps against Process metadata, pixel coverage and provider charges. Fix adapter discrepancies before claiming readiness. Respect quotas and do not automatically repeat failed paid requests.
2. Review code and any new-main conflicts. Tests cover contracts, not provider accuracy. Complete real Decisions smoke when secure key setup is resolved. Preserve failed checks and actual provenance.
3. Exercise `scripts/package-satellite.py` from clean committed source and inspect the allowlist/manifest. Test the Docker package. Service must be a new Railway service with one replica, private persistent `/data/satellite`, separate server-only service/MCP tokens. Repackage admin service to include the satellite proxy. Do not replace research/reporting services.
4. Make a reviewable PR if one is not already present. Use the coordinator's release process in `docs/RELEASING.md`; no independent review-alias promotion. Full release-route/browser acceptance is still required and other project acceptance blockers remain. Original actforgoa.org is out of scope.
5. Continue the plan's context/places/index work as appropriate. The current Amche integration is a location link, not ingested/queryable context. Current NL flow plans a bounded investigation; it does not yet answer statewide conversational queries from an event index. FIRMS, field accuracy and alerts are outstanding.

This branch changes no existing research ledger, production data, live secrets or deployment. No old local agent was resumed.
