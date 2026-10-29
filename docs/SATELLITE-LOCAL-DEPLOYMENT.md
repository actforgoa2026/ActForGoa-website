# Latest map/timeline update — 29 October 2026 (IST)

## Current continuation — 29 October 2026 query audit

The existing standalone map/timeline and real CDSE retrieval are already live. PR95 merged as `11582ac`; hosted CDSE acceptance is on main `f20fc25`. Earlier setup/credential/PR95 instructions below are historical and must not override this state.

Fetch `codex/satellite-query-audit` and its new PR; read [the query audit](SATELLITE-QUERY-AUDIT.md) and [verification](../reports/satellite-query-audit-2026-10-29/README.md). Update **both existing** standalone Railway services from the same reviewed source to add `/evidence`, area-scoped history, Amche references and UI recovery. Package only clean committed source with the existing scripts. Keep current named accounts, private data volumes, CDSE credentials and service tokens. Do not create another service or example site. The project/service identifiers below remain current.

Before promotion, inspect desktop and phone: area draw/viewport bounds, ordered dates, real acquisition slider, clear/obscured comparison, same/partial-area evidence results, context outage, account isolation and resuming a known job after network interruption. Reuse retained imagery for routine acceptance to avoid duplicate provider costs. Queries must never imply that missing records mean no change. Record deployed source and any provider usage separately.

OpenAI remains optional for shipping these usability/retrieval fixes. Use the user's chosen manual project-key setup if configuring Decisions; do not repeat the failed in-app key creation. Standalone ecology context requires the configured scoped research origin; current main research is chat-ready, so obsolete research-hold notes do not apply. Combined review-site alias promotion remains coordinator-owned.

## Earlier deployment instructions (historical)


Continue the existing standalone deployment; do not create another example site. Fetch the current `codex/satellite-monitoring` head, read `docs/SATELLITE-HANDOFF.md` and `reports/satellite-map-2026-10-29/README.md`, then package and deploy **both** the satellite API and satellite app. The frontend uses new authenticated `/observation` jobs, cached single acquisitions, reprojected imagery and a time slider. Keep the existing named account, SQLite data, imported recorded comparison, volumes and separate service tokens.

Existing Railway project `e119f1f6-f1c7-4a58-a33c-0ea536dcfdce`, production environment `178f97df-ed3d-4d66-94ac-f86797aa736c`; API service `2a16820e-393c-4385-b4f3-82d8d922c4d2`; app service `aea6b770-cd6d-4165-9802-7ce46fa0fd4a`. App URL: https://satellite-app-production.up.railway.app/map.

Hosted map checks must inspect the actual tile pixels: OpenStreetMap can return a blocked-message image that still has valid image dimensions. Its [tile policy](https://operations.osmfoundation.org/policies/tiles/) requires browser referrers, attribution and normal caching. The OSM layer uses `referrerPolicy: 'strict-origin'` so it sends only the public site origin, never account routes, query strings or investigation content. Keep the workspace and API `no-referrer` policy; do not disable privacy headers globally to fix tiles. Do not bulk-prefetch map tiles or bypass their cache headers.

Securely configure real `CDSE_CLIENT_ID` and `CDSE_CLIENT_SECRET` on the satellite API service using the user's CDSE account settings. Cloud-injected placeholders are not portable keys. Do not request secrets in chat or place them in shell history/Git. OpenAI remains optional; no key-creation retry is authorized by this handoff.

From clean committed source run `python scripts/package-satellite.py --output <new-staging-directory>` and `node scripts/package-satellite-app.mjs --output <different-new-staging-directory>`, deploy their allowlisted `service` directories using the existing local Railway workflow. Preserve volumes and one replica. Validate actual login, catalog for a new area, explicit observation load, date slider, two-image comparison, cache reuse and history persistence. Amche layers must load from their attributed public sources. Cloud already completed a bounded real river-area pair; avoid repeating it solely to reproduce screenshots. Record the exact new hosted source and any newly incurred provider usage. Keep the combined review alias and research services under ORCHESTRATOR ownership.

The older initial deployment handoff follows for context; the services above already exist.

# Local deployment handoff

The user explicitly authorizes getting the Goa satellite dashboard live for iteration. **OpenAI is optional for initial imagery retrieval. Do not turn its missing key into a deployment gate.** Continue implementation and deployment; do not stop at another plan or PR.

## Recover the current work

- Repository: `actforgoa2026/ActForGoa-website`.
- Fetch branch `codex/satellite-monitoring`; existing [PR #95](https://github.com/actforgoa2026/ActForGoa-website/pull/95). Do not create a duplicate PR.
- Read `AGENTS.md`, `docs/SATELLITE-HANDOFF.md`, `docs/CLOUD-IMPLEMENTATION-PLAN.md` and `docs/RELEASING.md`. Use an isolated checkout and reconcile current main. Main `9cea6e2` was already merged into this branch in `cfcbc1f`.
- Service runtime/package checkpoint `f42617b`: 17 allowlisted files, Docker startup/auth/private persistence verified. Current satellite suite: 72 passing tests. Existing main-site tests/build and desktop/phone dashboard checks pass; inspect reports for the exact source and test scope.
- Actual CDSE OAuth/catalog/Process calls succeeded. The verified October 10/20 pair is authentic imagery, with exact acquisition provenance and common clear masks. This is retrieval validation, not field accuracy.

## Deploy the functioning investigation service

1. Inspect the existing Railway/Vercel projects and active local ORCHESTRATOR release before changing anything. Another research release is active; preserve its services, corpus, accounting and acceptance hold. Do not replace `actforgoa.org` or independently race the review-site alias.
2. Use Railway's current API `https://backboard.railway.com/graphql/v2` or the authenticated Railway console/CLI. This cloud executor's `RAILWAY_TOKEN` binding only allows the old `.app` hostname, which returns 403. The cloud tools cannot edit the binding; a local authenticated deployment avoids that configuration obstacle.
3. Package the committed satellite runtime with `python scripts/package-satellite.py --output .reports/<new-directory>`. Deploy its `service/` to a **new satellite service**, one replica, persistent private `/data/satellite`. Follow `deploy/satellite/README.md`.
4. Set real `CDSE_CLIENT_ID` and `CDSE_CLIENT_SECRET` securely in the hosted service. Cloud-injected values are proxy placeholders and must not be copied into Railway. Set independent server-only `SATELLITE_SERVICE_TOKEN` and `SATELLITE_MCP_TOKEN`. Reuse the existing authorized Anthropic planner connection if available; manual area/date controls work without planning.
5. Deploy/repackage the named-account admin service with `server/satellite-proxy.ts`, configure its `SATELLITE_API_ORIGIN` and matching service token, and wire Vercel's server-only `ADMIN_API_ORIGIN`. Provision or reuse a named editor account securely; no shared default password or password in chat. See `deploy/admin/README.md`.
6. Coordinate the frontend release with the active release owner. Preserve the normal combined-site release checks. If its research release is still blocked, publish a separately scoped satellite app for iteration rather than weakening research acceptance or overwriting the main alias.
7. Verify hosted health/auth, one real bounded imagery comparison, actual acquisition dates/coverage, saved history and reopening, and desktop/phone behavior. Record deployment IDs, exact source commit, URL and remaining unavailable features.

## Optional AI and research connections

Decisions uses a normal OpenAI project API key as `OPENAI_API_KEY`. The user may create it manually in the console. The secure in-app creation request for `SatAnalysis2` was rejected without detail; do not automatically repeat it. No key was returned or saved. Keep image decisions visibly unavailable until a real call passes. The bounded `scripts/validate-satellite-decisions.py` can reuse verified recorded imagery and reserves one attempt before calling; preserve failures and do not reset the ledger.

Ecology passages use `SATELLITE_RESEARCH_ORIGIN` and the scoped `/api/search?domain=ecology` contract. The current public review endpoint is an older unscoped version; it must not be relabelled ecology-confirmed. Leave context unavailable until the correct service is connected. This integration does not authorize enabling held research generation or altering its budget ledger.

## What the cloud preview provides

Source `18112a2` adds a standalone static preview using the authentic recorded October pair. Build with `npx vite build --config vite.satellite-preview.config.ts`; output is `.reports/satellite-preview-dist`, containing only its HTML and public assets. It has a before/after slider, side-by-side view and measured evidence, with prominent recorded/read-only labels. **It cannot retrieve a new area/date pair or run AI.**

New Vercel project creation was forbidden by the cloud credential. An isolated preview deployment was instead created in the existing project, without production promotion or changing project build/protection settings. It uses a deployment-scoped seven-day share link. See `reports/satellite-preview-2026-10-28/live-browser.json` for deployment identity and live checks. The full share token is deliberately absent from Git; the user-facing chat contains the link.

Finish with a working URL and the actual verification results. Be explicit about recorded preview versus newly retrieved imagery and which services remain unavailable.
