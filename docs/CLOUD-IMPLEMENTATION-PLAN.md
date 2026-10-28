# Cloud implementation and landing plan — 28 October 2026

Feature development, tests, indexing and browser QA ran under `/workspace` in the cloud. CLOUD owns this implementation. The user subsequently appointed **Coordinate agent threads and PRs** (`01a181ad-56ba-70c2-93cd-1aa5185d007a`) as the continuing cloud release coordinator. Its durable inbox and release record is [issue #89](https://github.com/actforgoa2026/ActForGoa-website/issues/89). The earlier proposal to resume the local ORCHESTRATOR is superseded; keep local workers and their old heartbeat paused. The user then directly instructed CLOUD to “ship it”: CLOUD is completing the bounded PR #90 source landing; the primary coordinator retains live deployment ownership.

## Resume here

Read this file and `AGENTS.md` before doing work. Inspect `git status`, fetch `origin/main`, and compare workstream commits below before rebuilding or deploying. Never treat an in-progress row as completed. After each handoff, update its implementation, tests, merge and live states separately. Keep pending questions and exact next actions here so another agent can resume without the chat transcript.

## Latest voice follow-up and active release operation

After PR #90 merged as `7bf1965a2c46f76537437a822056b2bf9023f96c`, the user chose **warm, friendly and simple** as the answer voice. The follow-up branch `codex/warm-research-voice` updates the shared legal/ecology prompt, honors requests for simpler wording or more detail, and replaces the rigid 180-word/three-paragraph rejection with a 300-word/five-paragraph maximum while keeping simple answers short by default. Citations, evidence qualification, outside-context separation and budget limits remain enforced. See [RESEARCH-CLOUD-HANDOFF.md](RESEARCH-CLOUD-HANDOFF.md#answer-voice) for the editable editorial brief and exact limits. No dashboard voice control is included.

Implementation and offline verification are complete: **119 research tests pass**. The new regression checks a longer four-step answer, citation preservation and failure for fabricated support or oversized text. Live tone/semantic acceptance and deployment are still pending; the follow-up is not automatically merged into a release being prepared elsewhere. The prior portable runtime hashes describe PR #90, not this changed prompt.

The latest operation recorded in [issue #89, comment 6465343889](https://github.com/actforgoa2026/ActForGoa-website/issues/89#issuecomment-6465343889) reports a direct user-authorized focused local **ORCHESTRATOR** release. Treat it as the active promotion owner and do not race it. Other local workers and the old heartbeat remain paused; the primary cloud coordinator keeps reporting oversight. This newer operation supersedes the earlier default deployment-owner wording below. The release owner should review/include this voice follow-up before creating its accepted runtime package, and record its exact head and actual live acceptance. Existing full-corpus/accounting gates and the separate post-merge legal extraction finding in #89 remain outstanding; this voice change does not resolve them.

### Voice landing checks and current live hold

The user subsequently instructed CLOUD to ship [PR #92](https://github.com/actforgoa2026/ActForGoa-website/pull/92). This authorizes its source landing; the exact merge result is recorded in #92 and issue #89. The unchanged voice runtime from `6016ba3` has 119 passing research tests, 178 passing Node tests and a passing production build. An independent scoped code review found no actionable issues. Six cloud Chromium UI-fixture checks cover legal/ecology answers at 1440px, 390px and 320px: all five paragraphs/300 words and citations render intact, outside context stays separate, and there are no page errors or horizontal overflow. These are layout checks, not live generated answers. Evidence is in `reports/voice-shipping-2026-10-28.json`. The Impeccable skill remains unavailable in this executor.

The local release owner now [reports working Vercel/Railway credentials and a live acceptance hold](https://github.com/actforgoa2026/ActForGoa-website/issues/89#issuecomment-6465660719). On the earlier `7bf1965` runtime, water-04 returned a mechanically valid answer without final semantic acceptance; scope-01 returned an app 502 after the provider used document titles as citation IDs while its supports used passage IDs. That captured answer also exceeded the old 180-word bound, and the owner flagged ecological scope/population wording concerns. Only the length bound is changed by the voice follow-up: citation identity and semantic issues remain unresolved. Do not relabel the failed capture as accepted, replay unchanged diagnostics or bypass validation. The remaining cases and HTTP/hosted/admin checks have not passed. The owner retained both charged reservations, reconciled accounting and stopped promotion; deployment of AI answers remains held.

## Work ledger

Last updated: 28 October 2026. All `/workspace` paths below are on the cloud executor. Integration PR: https://github.com/actforgoa2026/ActForGoa-website/pull/90. Branch: `codex/cloud-integration-20261028`. Implementation and cloud acceptance are complete; the fresh review corrections below are included in the source landing. **Live deployment remains pending.** The exact merge SHA and latest release state are recorded on PR #90 and issue #89; a merge alone is not deployment.

| Task | Owner | Status | Finished / evidence | Next action |
| --- | --- | --- | --- | --- |
| Cloud setup and baseline | Root | Complete | Shell works; Python 3.12 / Node 24; freshly fetched main `fa43cf8`; six isolated worktrees | Keep all execution in cloud |
| Previous-work recovery | Root + reference_recovery | Complete with limitation | Admin Curation Plan and previous Anthropic/accounting work recovered; exact Disco source inaccessible | Reference comparison remains; do not claim exact parity |
| Research backend | research_api | Implemented + tested | Scoped Zvec + FTS5/RRF, concise Anthropic answers, explicit outside context, preserved budgets, loss-safe ledger; 118 Python tests | Restore full corpus/accounting through the coordinator; complete existing semantic/HTTP acceptance |
| Legal and ecology UX | research_ui | Implemented + tested | `/ask/legal`, `/ask/ecology`, `/ask`; cited library/outside separation; relevant public registry matches and source caveats | Verify against restored hosted service |
| Mobile forms/PDF | mobile_forms | Implemented + tested | 43 topic form actions use editors; all 18 authored forms export real PDFs; desktop/phone download + Unicode verified | Preserve official-form limitations; no blank download prerequisite in topic paths |
| Internal backend | admin_api | Implemented + tested | Durable SQLite, individual accounts, CSRF/session checks, shared stars, versioned drafts/published snapshots, paginated lists | Deploy separate persistent service and provision named accounts |
| Internal dashboard | admin_ui | Implemented + tested | Sidebar overview, community/resources curation, draft/editor/preview/publish; public journal and retained archive | Hosted login/publishing smoke after service wiring |
| Shared integration | Root | Implemented + tested | Routes/nav, relevant-only public curation, same-origin admin transport, cloud launch/proxies, release guards and allowlisted packager | Coordinator Vercel `ADMIN_API_ORIGIN` configuration |
| Combined tests and visual review | Root | Complete in cloud | 178 Node tests; 118 unchanged research tests; build; 36 route/provenance checks plus 10 shipping browser checks and real admin workflow | Live provider + hosted deployment checks remain distinct |
| PR / merge / release | CLOUD source landing; primary cloud coordinator deployment | Source landing authorized; deployment blocked | PR #90 with portable evidence, review fixes and handoff docs; exact merge result in #89 | Resolve provider tooling/access, restore corpus/accounting, complete existing acceptance and release gates |

### Current shipping handoff and review corrections

The primary cloud coordinator is **Coordinate agent threads and PRs** (`01a181ad-56ba-70c2-93cd-1aa5185d007a`). Deployment support is **Resume unfinished work** (`01a181aa-9a5b-7327-95a9-f93cc3b1b06e`). Both were idle at the shipping check. Direct cross-chat sending remains unavailable; issue #89 carries durable delivery, not an instant wake-up. The user directly authorized PR #90 shipping in CLOUD; its bounded source landing is recorded there to prevent competing merges. No local worker has been resumed.

Fresh GitHub review found two issues: `archive` could be published as a story slug despite the retained `/blog/archive` route, and browser history could discard unsaved editor changes. The source follow-up reserves that slug on create/edit/publish (including legacy drafts), mirrors it in the editor, and protects Back/Forward navigation with a router blocker. Fix commits: `ca66564` (server, source `e1122b4`) and `b222ceb` (editor/router, source `25498c7`). The combined 178 Node tests and production build pass. Ten new real-service desktop/phone checks pass with no page errors; see `reports/cloud-release-2026-10-28/browser-shipping.json`. The 118 research tests previously passed and their runtime is unchanged by these fixes.

Environment observations are specific: this older CLOUD instance still reports revision 1, no bound secrets/identities and restricted deployment egress. The support and coordinator environments report ready Vercel/Railway/Anthropic bindings. Support verified Vercel REST and Anthropic models access without paid inference, but Vercel CLI 65.5.0 rejects the injected placeholder before sending a request; Railway's configured GraphQL endpoint returns Cloudflare 403 and CLI authorization is unverified. Resolve supported tooling/configuration; do not fabricate tokens, bypass the proxy, bypass release gates, or assume a ready binding proves service access.

The existing semantic acceptance requirements remain **71 cases plus three HTTP journeys**. The small scenarios in the research handoff are supplemental, not a reduced release gate. Preserve the prior failed-candidate decisions and no-paid-continuation constraint; this handoff does not itself authorize further tuning or paid diagnostics.

Continuation for the cloud release coordinator:

1. Fetch PR #90 into a clean isolated checkout; inspect the exact remote head and this ledger. Do not reuse/reset the dirty shared checkout. Cloud code and follow-up review evidence is in [reports/cloud-release-2026-10-28](../reports/cloud-release-2026-10-28/README.md). The report hashes runtime files, so changes can be distinguished from the already-checked code.
2. Read [RESEARCH-CLOUD-HANDOFF.md](RESEARCH-CLOUD-HANDOFF.md). Recover the verified full research corpus and existing usage ledger using the prior local checkpoint at `/Users/zakkrevitt/.codex/worktrees/research-accounting/ActForGoa/.reports/anthropic-acceptance-20261027/checkpoint-after-main-release.json`. Inspect checkpoint JSON first; use disposable copies rather than opening sealed preservation databases. Retain older citation generations and the $5 monthly / 100-attempt daily limits. The five-guide cloud smoke dataset is **not** a release corpus.
3. Package/deploy the new research runtime to the existing research service, preserve source-search routing, and use the already-provided server-only Anthropic key. Verify model availability/pricing and restore the existing 71-case semantic plus three-HTTP-journey acceptance process before enabling answers. The legal/ecology/partial/no-match scenarios in the handoff supplement it. Quote validation is not semantic acceptance; preserve the no-paid-continuation constraint until the coordinator has applicable user authorization. Keep chat disabled if acceptance fails; do not reset accounting or repeat unchanged paid failures.
4. Follow [deploy/admin/README.md](../deploy/admin/README.md). Run `node scripts/package-admin.mjs --output .reports/admin-release-20261028` from clean committed source, deploy its `service/` directory with one replica and persistent `/data/admin`, set `ADMIN_PUBLIC_ORIGIN=https://actforgoa-field-guide.vercel.app` and `ADMIN_BEHIND_FRONTEND_PROXY=true`, and provision named editor accounts through the hidden-input CLI. These credentials are separate from private incident reporting.
5. Set Vercel server-only `ADMIN_API_ORIGIN` to that service's exact HTTPS origin. The PR includes same-origin `/api/admin/*`, `/api/curation`, and `/api/blog*` handlers. Verify actual cookies/login, star propagation, draft privacy, publication and public journal listing. Existing blog archive remains at `/blog/archive`.
6. Use the installed Impeccable workflow if available and check the restored hosted content on desktop/phone. Complete release evidence for the exact integrated tree with the **current**, freshly inspected previous deployment ID; do not copy a historical ID from old notes. The release script now requires new research/admin/blog routes and checks scoped research + admin/journal readiness.
7. Inspect PR #90 and issue #89 for CLOUD’s merge result; do not duplicate its source landing. Once the source is merged, fetch exact main into the clean release checkout, then run `npm run release:review -- --check --evidence .reports/release-evidence.json` and `npm run release:review -- --evidence .reports/release-evidence.json`. Verify the review alias and update this ledger with merged commit, service/deployment IDs, actual live-provider result and remaining limitations. Do not equate PR merge with deployment.

### Completed commit map

| Workstream | Feature commit(s) | Integrated evidence |
| --- | --- | --- |
| Research backend | `05ed430`, follow-up `a190ad9` | Integrated as `c148541`, `3c2e50c`; 118 Python tests, real 5-guide index; ledger and route fixes independently rechecked |
| Research UX | `c7802d9`, `6b7ece5`, `37c59ac` | Integrated as `70574b2`, `99ead3f`, `04d3f4b`; phone wrapping and source caveats verified |
| Forms | `393d8b7` | Integrated as `1ccaa7c`; [form audit](../reports/FORMS-CLOUD-20261028.md) |
| Admin backend | `4c74f37`, `669ca3d` | Integrated as `120f4e1`, `61c60b4`; auth/storage + actual proxy checks and real browser publishing |
| Dashboard UI | `4e19529` | Integrated as `2ea5873`; sidebar, curation, editor and public journal checked |
| Root integration | `e46a28c`, `71e66f6`, `92a5da7` and subsequent release/handoff commits | PR contains exact final routes, services, tests and evidence; use its current head rather than an intermediate SHA |

### Superseded local handoff

The earlier user instruction allowed local credential wiring after cloud implementation. A later user-appointed cloud coordinator and support environment now own that work. The old local checkpoint remains a source of preserved corpus/accounting evidence; access it only through an explicit focused transfer without restarting paused agents. Keep development and normal coordination in the cloud. The original actforgoa.org site remains out of scope.

### Deployment dependencies

- This CLOUD executor has no bound Anthropic or deployment secrets; separate support/coordinator executors have ready bindings with the concrete tooling/access limitations above. Do not solicit or print secret values in chat.
- Allowed destinations do not currently include Anthropic or Railway/Vercel control APIs. Do not bypass the configured proxy/policy.
- Full research corpus/index is absent from this cloud checkout. Public live search previously contained 1,156 documents; prior private candidate contained 1,174 including legal additions. These numbers are historical handoff evidence, not verification of current cloud data. Restore verified public-source corpus via approved deployment/storage access, preserving generation IDs and existing accounting. The five tracked canonical guides can be indexed/tested separately and must not be described as the full legal/ecology corpus.
- Impeccable skill installation has not been found. Existing `.impeccable` surface/design files and DESIGN.md are present. Record this gap; do not fabricate an Impeccable pass.
- Exact Disco dashboard source was not accessible through connected GitHub installations or the cloud filesystem. Implement the requested dashboard workflow and have the release coordinator arrange comparison against the existing Disco files before claiming exact parity. Do not replace the existing blog archive.

### Completion record format

For each landed workstream append: exact commit SHA; files/interfaces changed; commands and results; screenshot/evidence paths; known limits; integration dependencies; implemented / tested / merged / live states. A future orchestrator should work from the next-action column, then verify facts against Git and service health.

## Answer first follow up

The user supplied answer/retrieval briefs and explicitly requested shipping a conversational, corpus-first answer experience. Branch `codex/answer-first-evidence` implements this bounded follow-up for the focused release owner to integrate:

- `backend/answer_brief.py` directs the model to read the supplied excerpts, answer directly, synthesize supporting passages, explain supported inferences and conflicts, and state specific gaps. It is included in the existing answer request; it does not add a second model call or claim that hybrid retrieval performs model-based query decomposition.
- The actual provider message retains complete excerpt text and now includes document identity, page/section label, offsets and source URL alongside existing publication metadata and qualifications. An HTTP-boundary regression test inspects the serialized provider request, verifies two exact excerpts and their locations, and preserves all-or-nothing passage budgeting. Titles/IDs alone are not an evidence pack.
- Answer mode renders the synthesized response before expandable **View sources**. A failed answer keeps matching sources collapsed. When generation is unavailable, Ask is disabled with an explicit explanation; browsing requires choosing **Find sources**, rather than silently converting the request into search.
- The user's subsequent visual direction is implemented as a rounded chat interface: compact auto-growing composer, circular send control, user message bubbles, pill-shaped collection controls and suggested questions, and collapsed source/community/library details. Enter sends, Shift+Enter inserts a line, and composition input is preserved. This scoped chat treatment supersedes the old rectangular form styling for `/ask` and its domain routes.
- Validation: 121 research tests, 178 Node tests, production build, and nine Chromium fixture scenarios at 1440, 390 and 320 pixels. Browser checks cover answer/source order, source expansion, exact-passage navigation and return, follow-up context, generation failure and unavailable-answer behavior. Evidence is in `reports/answer-first-2026-10-28/`. These are not live model or semantic acceptance.

The existing local focused corrective release remains the sole promotion operation, as recorded in issue #89 after the later direct user instruction. Integrate this prompt change before freezing its candidate; previous provider acceptance does not transfer to changed instructions. Preserve the citation-contract corrections, full corpus, accounting and existing acceptance requirements. This follow-up does not authorize a budget increase or claim live deployment. The installed Impeccable skill was unavailable in this executor; the existing design guidance and rendered desktop/phone output were checked.

## Outcomes

1. Separate legal and ecology entry points using library-first Zvec dense + lexical hybrid retrieval and server-side Anthropic answers. Concise cited library answers and clearly separate outside-library context; never label model knowledge as a verified external source.
2. Relevant registry people, organisations and government offices alongside answers, with existing provenance and currency labels retained.
3. Main topic pathways open mobile form editors. PDF export is optional after completion; no blank-form download prerequisite.
4. An authenticated internal dashboard with a desktop sidebar, shared community/resource curation and a blogging workflow based on the prior Disco work where recoverable.

## Ownership and dependencies

| Workstream | Isolated checkout | Owned files |
| --- | --- | --- |
| Orchestrator | `/workspace/actforgoa-integration` | App routes, shared navigation, package/lock coordination, integration, release evidence |
| Research API | `/workspace/actforgoa-research-api` | backend, research scripts/tests/runtime requirements |
| Research UX | `/workspace/actforgoa-research-ui` | Research.tsx, research styles/API types, registry recommendation helpers/tests |
| Forms | `/workspace/actforgoa-forms` | template/editor/export/topic-form routing files and tests |
| Admin API | `/workspace/actforgoa-admin-api` | new admin service/storage/auth, shared contract, server tests |
| Admin UX | `/workspace/actforgoa-admin-ui` | new dashboard/blog components/styles/API client and tests |

Agents commit only their changes and return exact commits, interfaces, verification and remaining blockers. Cloud root cherry-picks into the integration branch and owns acceptance. The primary cloud coordinator takes the deployment work through issue #89; local workers remain paused. No independent feature-agent deployments.

## Existing work to preserve

Main at start: `fa43cf89d5306fb3128ed271de38a74ad4ee396b`. Research is already live as source search, but generated answers were deliberately disabled after prior semantic accuracy failures. Existing research-integration branch `ab2194987a9ce430ca011dfaf11e1f575eb3ed91` and research-accounting branch must be inspected before replacing or duplicating them. Preserve the previous $5 monthly / 100-attempt daily controls; do not reinitialize production accounting or deploy sealed old packages. Prior legal corpus additions are not necessarily on main or in this cloud checkout. Inspect what is actually present.

Admin Curation Plan was approved, but its prior summary says only isolated relevance-aware ranking was completed; login, shared storage and UI were unfinished. Stars must only reorder records already relevant to the query/filter. Private report authorization is separate from admin curation.

## Verification and landing gates

- Targeted behavior tests: provenance separation, domain filters, citations, no-evidence behavior, registry relevance, form completeness/PDF, admin authorization/revocation, durable updates and publication visibility.
- Integrated npm tests/build and Python research tests. Browser checks on desktop and phone, including all existing release routes and new routes. No Device Hub.
- Keep credentials, incident data, personal notes and raw research archives out of Git/deployments.
- Commit reviewable source and create an integration PR. Follow `docs/RELEASING.md` and `npm run release:review`; never bypass readiness or promote stale source. Only the review alias is in scope, not actforgoa.org.
- Report implemented, tested, merged and live separately.

## Initial environment gaps

Environment reports no bound secrets or cloud identities. HTTP access currently allows the review alias and package-manager hosts, but not Anthropic, Railway or Vercel control APIs. Secure runtime key/deployment access and permitted destination configuration must be restored for live provider testing and publication. Continue implementation and offline checks independently. Impeccable is referenced by AGENTS.md but its installed skill has not yet been found in the cloud; preserve existing design documents and record the verification limitation if unavailable.

## Satellite workstream checkpoint — 28 October 2026

Source chat **SAT IMAGE ANALYSIS** (`01a181d5-fcf6-745a-b440-89a455d69065`) implemented the isolated `codex/satellite-monitoring` branch from main `7bf1965`. See [satellite handoff](SATELLITE-HANDOFF.md), [consolidation plan](GOA-MAP-INTELLIGENCE-PLAN.md), and [verification evidence](../reports/satellite-2026-10-28/README.md). Implemented: private bounded Goa investigations and map, EVE-derived numeric CDSE adapter, Anthropic planning, optional Decisions classifications, MCP and authenticated admin bridge. Tested: 28 satellite Python tests, 181 Node tests, build, desktop/phone synthetic-provider workflow and one live Anthropic plan. **Not merged or live.** CDSE and OpenAI are absent in this executor revision 1; user is opening a new chat with newly saved CDSE configuration. Railway GraphQL remains inaccessible here. Provider imagery validation, packaging/deployment, Amche vector ingestion/place resolution, statewide indexing, FIRMS and field evaluation remain pending. Coordinator retains combined release ownership; existing research accounting/acceptance requirements are unchanged.

### Satellite live imagery continuation — 28 October 2026

The new executor has ready CDSE bindings and successful real authentication. Source checkpoint `133bd4e` was recovered in an isolated worktree, with main `a786df5` reconciled by merge `f60597a5c51796cc9ac40697b169931b1bf0d840`. Fix/validation commit: `deb1f1d1e54d828f1463da787e9b75dd2e4aea45`. Process now requests the TAR bundle explicitly; a real unbundled TIFF previously failed provenance validation. The real 10/20 October pair passed exact acquisition, aligned eight-band raster and numeric comparison checks. Both masks mark the selected area usable; no loss candidates met the prototype thresholds. This is one small-area retrieval check, not field accuracy or absence of cutting. [Evidence and usage](../reports/satellite-live-2026-10-28/README.md).

Implemented: provider request fix, repeatable bounded live-validation script and optional Docker build CA mount. Tested: 29 satellite Python tests, 181 Node tests and production build; local HTTP replay of recorded real provider responses also completes the job, preserves the overlapping-window caveat, abstains from unconfigured classification and rejects a different actor's job access. **Not merged to main or deployed.** OpenAI setup/Decisions, representative evaluation, context/place resolution, statewide indexing and hosted acceptance remain pending. Coordinator retains combined release ownership; no existing service, live secret or research ledger was modified.

Package/runtime checkpoint: `ebf570a771396ad126960400faeef9f0ea50b9a8`. All 15 staged files match their allowlist hashes. Docker build and startup pass after adding Rasterio's missing `libexpat1` dependency; health, REST/MCP auth, absent-provider handling, persistent usage, private SQLite permissions and interrupted jobs were checked in the container. [Manifest and runtime evidence](../reports/satellite-live-2026-10-28/README.md). Temporary containers are removed. Deployment remains coordinator-owned and pending; no credentials were exported to hosting.

### Satellite investigation dashboard continuation

The user clarified the target as a query/dashboard system for time-based changes in trees, rivers, waste and development, using current usable imagery and ecological articles. Draft [PR #95](https://github.com/actforgoa2026/ActForGoa-website/pull/95) continues `codex/satellite-monitoring`; local worktree branch is `codex/satellite-live-validation`. Main remains `a786df5`. Paired decision/interpretation checkpoint: `e705d69`. The following dashboard change adds actor-private saved history with actual observation-period filters, result reopening, freshness/newer acquisition metadata, common-mask water changes, waste and legality limitations, and bounded cited ecology passage retrieval. No statewide coverage or individual-tree detection is claimed.

Implemented and checked: 68 satellite Python tests, 181 Node tests with the environment proxy enabled, production build, and three real-local-auth/synthetic-provider Chromium workflows at 1440/390/320 px. [Evidence](../reports/satellite-decisions-2026-10-28/README.md). OpenAI remains unconfigured; user previously approved secure creation, but the old widget's opaque target IDs did not transfer and destination confirmation/secure write remain incomplete. No live Decisions call or new paid model call was made. Live research search responds but lacks domain confirmation, so ecology context is correctly unavailable until the coordinated research service supplies the scoped contract. Its generation/accounting/semantic-acceptance hold is unchanged.

**Not merged or deployed.** Continue this PR; do not reopen old local workers or create a duplicate PR. Next: complete secure OpenAI setup and one bounded live Decisions check; representative seasonal/cloud/water/waste/development field evaluation; coordinated scoped-research connection and hosted acceptance. Longer-term work remains place/context ingestion, watch areas, multi-acquisition timelines, statewide coverage/event index, FIRMS, follow-ups and alerts. Package the final reviewed runtime again; older 15-file package evidence describes the earlier source only.

Dashboard runtime checkpoint: `f42617bb956f20c5b2ca921f3cf8e08226f3d3d8`. Seventeen allowlisted files verified; Docker image `sha256:42cead7b4391f579116428636bf87c648bcf599402b802c2ef78683e05b9f664` builds and passes health/history auth/filter/isolation/restart-persistence checks with private SQLite mode 0600. Provider credentials were not passed into the test container. A first probe used a stale ephemeral port after restart; the corrected harness confirmed Docker had changed it. Both outcomes are retained in the current evidence directory. Screenshot/docs changes after this checkpoint do not alter runtime source. No live deployment occurred.

OpenAI follow-up: user confirmed `SatAnalysis2`, 30-day expiry and ignored `.env.local` destination. The single encrypted creation call was rejected by OpenAI Platform without a specific reason. No key was returned/saved, no Decisions call was made, and no creation retry was attempted. [Attempt evidence](../reports/satellite-decisions-2026-10-28/key-setup-attempt.json). The new bounded live validator verifies the recorded real CDSE inputs and reserves one persistent attempt before inference; its four offline tests bring the satellite suite to 72 passing. Service/UI runtime remains `f42617b`, with the existing 181 Node/build/browser/container checks unchanged. Next live step requires resolution of the selected project's key-creation access; do not ask again for the already-approved local destination or silently change project/expiry.
