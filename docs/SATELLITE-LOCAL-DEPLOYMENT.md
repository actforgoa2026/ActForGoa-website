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
