# Satellite implementation verification — 28 October 2026

Implemented in isolated branch `codex/satellite-monitoring`, starting from `7bf1965`. Not merged or deployed. The companion [plan](../../docs/GOA-MAP-INTELLIGENCE-PLAN.md) distinguishes this bounded prototype from statewide monitoring and future contextual joins.

Checks actually run:

- `.venv/bin/python -m pytest tests/satellite -q`: 28 passed. Synthetic catalog/process/Decisions contracts; numeric image grids, cloud abstention, candidate polygons, acquisition/date checks, input limits, quotas/restart behavior, actor access, MCP authentication/discovery/host protections and masking of model images. These are not accuracy tests.
- `NODE_USE_ENV_PROXY=1 npm test`: 181 passed, including three satellite proxy/auth tests. Session, CSRF, trusted actor propagation, route restrictions, redirects and bounded responses are exercised.
- `npm run build`: passed. Existing large-chunk warning remains.
- Local Chromium desktop 1440×1000 and phone 390×844: public access restrictions; actual named-account login through existing admin backend; natural-language plan, catalog selection and asynchronous comparison through the real proxy/Python service with synthetic providers; two decoded images; actual fixture dates and overlapping-window caveat; date changes clear old results; no horizontal overflow, italic text or browser page errors. See `browser.json` and screenshots. Synthetic comparison screenshots are prominently labelled. OpenStreetMap tiles are real basemap context, not satellite observations.
- One live Anthropic planning request: the selected-area canopy-loss question resolved to `ready`, `canopy_loss`, `Asia/Kolkata`, exactly ten days. No satellite observation or finding was claimed. The existing research service and its usage ledger were not changed.
- `git diff --check`: passed before checkpoint.

Not verified: live CDSE OAuth/catalog/Process provenance and spectral payload; live Decisions inference; packaging/Docker build; hosted service or Vercel deployment; field accuracy; Amche vector ingestion; statewide search; FIRMS or alerts. Existing research Python tests were not rerun because that runtime was untouched. This is feature evidence, not the full release-route acceptance record.

The installed Impeccable skill was unavailable in this executor; existing design guidance and rendered desktop/phone inspection were used. Do not describe this as an Impeccable pass. User reports CDSE secrets are saved, but this executor still reports revision 1 without them. Recheck in the new environment before any credential request.
