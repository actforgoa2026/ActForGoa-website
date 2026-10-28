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

## Cloud-only claim assessment continuation — 28 October 2026

The user's latest instruction keeps this research-chat work entirely in cloud;
do not reactivate the stopped local ECO SYSTEM thread. Earlier local-release
references above do not authorize local execution for this continuation.

Fresh remote main is `a786df50a9f69663c0e68751accc6d136890715a`;
PR #88 head remains `0c234e6f53dce24632875cc1f58f0c4dd302078a`.
Isolated branch: `codex/offline-claim-assessment`, cloud worktree
`/workspace/actforgoa-claim-assessment`. Candidate files:
`experiments/claim_review_candidate.py`, its test module, and
`docs/RESEARCH-OFFLINE-CLAIM-CANDIDATE.md`.

Implemented: offline explicit-span/claim review prototype only. Complete evidence
still permits wrong wording; the tests deliberately preserve that counterexample.
Mechanical verification: experiment discovery ran 71 tests, with one skipped
(70 executed); this count is coincidental and is NOT the 71-case semantic gate.
Unchanged research suite: 121 passed. `git diff --check` passed. No production
runtime, UI, provider configuration, ledger or acceptance expectations changed.
Semantic acceptance: none. Merge: not merged. Production verification: none.
No paid calls, deployments or local-thread activation performed.

Missing: historical capture reviews, unsealed dependency assessment, frozen
71 semantic cases plus three HTTP journeys, and verified persistent accounting.
Reported 28 daily attempts / 2,316,292 monthly microdollars remain historical,
not reconciled values. The source documents a runtime-limit mismatch on current
main that must be resolved before any dispatch. Next: review the offline candidate,
recover missing evidence through cloud storage, finish complete-set assessment,
and only then seek authorization for a concrete bounded acceptance run. Hold AI
activation and preserve distinct semantic, HTTP and production launch gates.

### Source-grounded offline follow-up

Continued from `dabe9b353c13a0ed4c4d1bdd4b71c0939affccf7` on the same isolated
cloud branch. Fresh main remains `a786df5`. Read-only production status confirms
search ready/chat disabled and the older 1,156-document generation. Recovered
public extracted pages and authenticated the original 155-page biodiversity PDF
against its source metadata hash; inspected original pages 61/66/67. The narrative
104 total conflicts with table numbering through 105. The lake extracts also
contain an unresolved area disagreement. No historical capture was recovered.

Implementation: seven authored real-source development probes with pinned private
inputs, a reproducible offline review packet, stronger review fingerprints and
support-limit failures. Facet checklist pass no longer implies semantic acceptance.
See `docs/RESEARCH-SOURCE-CONTEXT-ASSESSMENT.md` for hashes, source identities,
source-only verification and all limitations. The prototype is explicitly rejected
as a sufficient automatic semantic fix; no runtime integration is recommended yet.

Checks: experiment discovery 75 run/one skipped; evidence auditor 64 passed;
capture adapter 40 run/one skipped; diff whitespace check passed. Frozen specs and
expectations unchanged. Runtime regression result remains 121 passed from the
previous commit; runtime files are unchanged. Semantic acceptance: none. Merged:
no. Production launch verification: none. No paid call or ledger inspection;
canonical reconciliation remains mandatory before any future paid call. No local
execution, stopped-chat activation, release promotion or AI enabling occurred.

Read-only issue #89 inspection found a newer reported accounting checkpoint of
39 attempts / 2,360,028 monthly microdollars (comment 6467306803). This is reported,
not reconciled persistent state; the user's 100-attempt constraint remains in
force. Historical issue instructions do not authorize paid calls or local work.
The missing historical evidence's cloud location has been requested from the user.

### Native Git-history recovery — cloud-only

The user asked us to locate the prior material independently. Fetched remote
research branches and recovered PR #88 head `0c234e6f53dce24632875cc1f58f0c4dd302078a`
in an isolated detached cloud checkout. Recovered 50 Goa + 5 legal + 12 consumed
assessment cases byte-for-byte with the exact frozen hashes; 67/71 are now available.
Four boundary-case definitions, exact three HTTP journey definitions, private
historical captures/reviews and unsealed dependency draft remain unrecovered.
None is replaced or waived. See `docs/RESEARCH-NATIVE-RECOVERY.md` for the full
reproduction and limitations.

Native verification: 181 existing selected tests passed; six new pure-builder
profiles retained all full-page source text within 24,000/36,000/4,096 byte caps,
with 12,000 output tokens and no client, call or ledger access. The earlier
main-only runtime-limit concern remains separate from this recovered native path.
Offline support limits corrected to original native 10/600 from main's 6/1,600;
no production change. The matching Annexure V source obligation was recovered
from physical page 118 and added as an explicit two-probe extension. All nine
source probes retain semantic unassessed/release hold; adding duty/scope labels
again is explicitly rejected as a demonstrated fix because native plans already
had them. Source replay/experiment suite: 75 run, one missing frozen-capture skip.

Implemented: reproducible Git recovery, actual-native budget construction and
matching-obligation counterexamples. Semantically accepted: none. Merged: no.
Production verified: no. No paid provider calls, model/config sweeps, ledger
changes, local-host reads/execution, stopped-thread messages or activation.
