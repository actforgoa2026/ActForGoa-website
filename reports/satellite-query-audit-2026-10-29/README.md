# Selected-area evidence audit and implementation

Date: 29 October 2026. Baseline main `f20fc25b88681fc7228002a4ca63b8a1dbab2230`; feature branch `codex/satellite-query-audit`.

Read [the full functional/data/model audit](../../docs/SATELLITE-QUERY-AUDIT.md) for findings, current changes and remaining work. [Hosted status](hosted-status.json) records public HTTP/bundle observations, not authenticated browser acceptance.

Implemented: bounded actor-private area/time/topic evidence search; area-filtered history; pinned Amche spatial reference queries; absolute ecology reader citations; explicit readiness and workflow; recoverable job polling; viewport/drawing feedback; scoped image decisions with retained uncalibrated scores and corrected numeric/model interpretation.

Validation is offline unless identified otherwise. The satellite Python suite and proxy/job tests cover scope isolation, actual acquisition intervals, partial overlap, stale geometry, bounded scans, unknown-versus-absent evidence, malformed scores, source outages, source privacy, polling recovery and context restoration. No new paid provider request ran. Test image inputs are synthetic and labelled. Existing real imagery acceptance remains in [the hosted CDSE report](../satellite-cdse-2026-10-29/README.md).

## Completed source checks

- `.venv/bin/python -m pytest tests/satellite -q --disable-warnings`: **136 passed**. Dependency deprecation warnings remain; no test failed.
- `NODE_USE_ENV_PROXY=1 npm test`: **216 passed**, including the existing read-only public MCP integration. The first run without Node proxy support failed that remote network test; using the documented managed-cloud proxy setting resolved it.
- `npm run build`: passed TypeScript/client/server checks and production bundling. Existing large-chunk warnings remain.
- Independent backend/UI/model reviews fixed stale area/date restoration, lost timeline state, bounded image-cache handling, malformed legacy data, score validation and optional-source failures.
- `git diff --check`: passed.

Source checkpoint and clean package verification are recorded below. Browser visual/interaction checks are not available in this executor and remain outstanding. OpenAI is unconfigured here; this report makes no live classification or accuracy claim. Neither the new query UI nor its endpoint has been deployed by this task.
