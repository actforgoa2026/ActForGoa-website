# Cloud implementation and landing plan — 28 October 2026

Feature development, tests, indexing and browser QA ran under `/workspace` in the cloud. CLOUD owns this implementation. The user subsequently appointed **Coordinate agent threads and PRs** (`01a181ad-56ba-70c2-93cd-1aa5185d007a`) as the continuing cloud release coordinator. Its durable inbox and release record is [issue #89](https://github.com/actforgoa2026/ActForGoa-website/issues/89). The earlier proposal to resume the local ORCHESTRATOR is superseded; keep local workers and their old heartbeat paused. The user then directly instructed CLOUD to “ship it”: CLOUD is completing the bounded PR #90 source landing; the primary coordinator retains live deployment ownership.

## Resume here

Read this file and `AGENTS.md` before doing work. Inspect `git status`, fetch `origin/main`, and compare workstream commits below before rebuilding or deploying. Never treat an in-progress row as completed. After each handoff, update its implementation, tests, merge and live states separately. Keep pending questions and exact next actions here so another agent can resume without the chat transcript.

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
| Combined tests and visual review | Root | Complete in cloud | 176 Node tests; 118 Python tests; build; 36 route/provenance browser checks and real admin workflow | Live provider + hosted deployment checks remain distinct |
| PR / merge / release | CLOUD source landing; primary cloud coordinator deployment | Source landing authorized; deployment blocked | PR #90 with portable evidence, review fixes and handoff docs; exact merge result in #89 | Resolve provider tooling/access, restore corpus/accounting, complete existing acceptance and release gates |

### Current shipping handoff and review corrections

The primary cloud coordinator is **Coordinate agent threads and PRs** (`01a181ad-56ba-70c2-93cd-1aa5185d007a`). Deployment support is **Resume unfinished work** (`01a181aa-9a5b-7327-95a9-f93cc3b1b06e`). Both were idle at the shipping check. Direct cross-chat sending remains unavailable; issue #89 carries durable delivery, not an instant wake-up. The user directly authorized PR #90 shipping in CLOUD; its bounded source landing is recorded there to prevent competing merges. No local worker has been resumed.

Fresh GitHub review found two issues: `archive` could be published as a story slug despite the retained `/blog/archive` route, and browser history could discard unsaved editor changes. The source follow-up reserves that slug on create/edit/publish (including legacy drafts), mirrors it in the editor, and protects Back/Forward navigation with a router blocker. Targeted regression and real browser results are added to the portable evidence before landing.

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
