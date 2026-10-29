# Selected-area evidence audit and implementation

Date: 29 October 2026. Baseline main `f20fc25b88681fc7228002a4ca63b8a1dbab2230`; feature branch `codex/satellite-query-audit`.

Read [the full functional/data/model audit](../../docs/SATELLITE-QUERY-AUDIT.md) for findings, current changes and remaining work. [Hosted status](hosted-status.json) records public HTTP/bundle observations, not authenticated browser acceptance.

Concurrent PR108/main `05720cb` is reconciled, preserving its place search, location, Arc controls and drawing. Explicit nested Vercel handlers now forward satellite actions/jobs through the existing authenticated proxy; the latest public check found the map frontend deployed but the API still404.

Implemented: bounded actor-private area/time/topic evidence search; area-filtered history; pinned Amche spatial reference queries; absolute ecology reader citations; explicit readiness and workflow; recoverable job polling; viewport/drawing feedback; scoped image decisions with retained uncalibrated scores and corrected numeric/model interpretation.

Validation is offline unless identified otherwise. The satellite Python suite and proxy/job tests cover scope isolation, actual acquisition intervals, partial overlap, stale geometry, bounded scans, unknown-versus-absent evidence, malformed scores, source outages, source privacy, polling recovery and context restoration. No new paid provider request ran. Test image inputs are synthetic and labelled. Existing real imagery acceptance remains in [the hosted CDSE report](../satellite-cdse-2026-10-29/README.md).

## Completed source checks

- `.venv/bin/python -m pytest tests/satellite -q --disable-warnings`: **136 passed**. Dependency deprecation warnings remain; no test failed.
- `NODE_USE_ENV_PROXY=1 npm test`: **221 passed**, including the existing read-only public MCP integration. The first run without Node proxy support failed that remote network test; using the documented managed-cloud proxy setting resolved it.
- `npm run build`: passed TypeScript/client/server checks and production bundling. Existing large-chunk warnings remain.
- Independent backend/UI/model reviews fixed stale area/date restoration, lost timeline state, bounded image-cache handling, malformed legacy data, score validation and optional-source failures.
- `git diff --check`: passed.

Initial implementation checkpoint `150db3e` passed both clean packagers and isolated app/API container checks. Final reconciled source and package evidence are recorded below. Containers use synthetic service tokens and no provider credentials; local cloud builds mount the supplied CA only for dependency installation, preserving TLS verification. Browser visual/interaction checks are not available in this executor and remain outstanding. OpenAI is unconfigured here; this report makes no live classification or accuracy claim. Neither the new query UI nor its endpoint has been deployed by this task.


## Final reconciled package checkpoint

Runtime source: `97cde8be5cd79e1a2e1e620a216a3f9f7c133048`, incorporating current main `05720cb` and the explicit Vercel satellite handlers. [PR109](https://github.com/actforgoa2026/ActForGoa-website/pull/109) contains this source plus the final verification documentation.

Both packagers pass from a clean committed checkout: [API manifest](api-manifest.json) and [app manifest](app-manifest.json). The API includes the new `amche.py` and `evidence_query.py`; the app includes the current map-place gateway. No credentials, private accounts, image caches or research corpus are packaged.

[Container checks](container-checks.json) pass for both packages, running with network disabled. API health, authenticated evidence/no-match behavior, missing-actor and anonymous rejection, invalid-history-date validation, zero provider reservations and private SQLite permissions pass. The app delivers its evidence/job-recovery bundle, requires authentication and refuses private-file/unrelated-API paths. Temporary containers and synthetic token files were removed.

The first ordinary Docker dependency builds could not trust the managed-cloud HTTPS proxy. Local validation used build-only secret CA mounts (`PIP_CERT` / `NODE_EXTRA_CA_CERTS`), with TLS verification retained and the supplied CA excluded from image layers. Production Dockerfiles and packaged runtime files were unchanged by this trust adapter. These are container/API checks, not a rendered browser audit or hosted deployment.

Final status: implemented, committed, tested and packaged; **not merged or deployed by this task**. Complete rendered desktop/phone and hosted API acceptance after deploying both existing standalone services. Cloud Railway credentials remain bound to `.app`, not the required `.com` endpoint; no OpenAI binding exists in this executor. No paid satellite/model operations ran in this audit. Existing live imagery remains available on the standalone service.

## Local release acceptance continuation

The direct-authorized local coordinator reviewed PR109 against fresh main `05720cb` in an isolated checkout. Local gates passed: 136 satellite tests, 221 Node tests and the production build. The original `.venv` path was absent; the retained satellite environment ran the Python suite successfully. Dependency deprecations and the existing bundle-size warning remain.

Impeccable context, Operate guidance, craft floor and source detector were used. No primary detector findings; inherited map semantic colors/radii have advisories. CUA rendered desktop 1440×1000 and phone viewport 390×844 checks cover expanded drag/two-corner selection, real retained October20/25 image display and timeline, original-footprint/partial-overlap evidence, topic no-match explanation, measurement disclosure and comparison citations. A disposable authenticated local service replayed the retained real images; a deliberately interrupted job poll survived reload and resumed its existing reference. This replay did not contact CDSE or AI. Phone checks use the browser viewport and pointer input, not a physical phone.

One observed presentation issue was fixed: positive sub-one-percent intersections display `<1%`, never a rounded zero. The retained pair remains inconclusive at 41.1% common usable coverage. Real read-only Amche and scoped ecology queries returned cited references; these are background evidence, not field verification. Screenshots and private replay data stay in ignored `.reports/satellite-query-release-20261029/`.

Predeployment readiness found hosted CDSE configured, OpenAI/planning absent, and ecology origin unset. The existing combined-site editorial service also lacked the satellite upstream/token; its new proxy and explicit Vercel handlers must ship together. Issue89 comment6496808456 records focused local ownership; other agents remain paused. Hosted deployment identities and final checks will be recorded separately after promotion.

### Hosted upload regression caught before release completion

The first combined promotion from `a5355bc` still returned platform404 for
satellite handlers. Its deployed function inventory omitted the entire new
folder: `.vercelignore` had an unanchored `satellite/` exclusion intended only
for Python source. The standalone API/app/editorial deployments succeeded.
The focused follow-up anchors that exclusion to `/satellite/` and adds staged
401 authentication probes for every satellite action/job depth to
`release:review`. This prevents a successful local handler test from being
mistaken for an uploaded, reachable function. No frontend, API research/runtime,
accounting or provider changes are included in this upload correction.
