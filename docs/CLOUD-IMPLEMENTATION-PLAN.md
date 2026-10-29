# Cloud implementation and landing plan — 28 October 2026

## Satellite Google integration — 29 October 2026 (local)

User explicitly requested connecting Earth Engine and Google Maps APIs to the existing hosted standalone satellite app and testing them there. Isolated branch `codex/satellite-google` starts at fresh main `1b16b87`; the active hosted Python source hash-matches that base. Existing deployments before this change: API `8e598615-7b63-497b-8cd8-608486e98a85`, app `393c446c-2fa6-4b8b-b1e9-0a35bb5c9a77`. Both private databases were backed up before configuration. Main/research aliases and paused chats are outside this work.

Implemented and live from runtime commit `df57d1b`: explicit Earth Engine retrieval, preserved spectral/cloud/actor-cache checks, on-demand current Google weather/air quality and a directions link. API deployment `906213da-e9c4-4524-9659-4e91d0e7cc46` and app deployment `a231af84-a064-4baa-af37-c3611c98b009` succeeded. Hosted acceptance retrieved and compared exact 8/13 January Sentinel-2 images with 94.11% common usable coverage, reused the cache, reopened saved results on desktop/390px browser and verified five Google web services. All copied runtime/static files match package hashes. Original four jobs, two rasters and staff account are unchanged. Temporary verification access was revoked. Google browser map replacement and OpenAI key setup remain unselected; the current map is preserved and no AI request ran. Automated validation: 140 Python satellite tests, 221 Node tests and production build. [Configuration](SATELLITE-GOOGLE.md), [hosted acceptance and limits](../reports/satellite-google-2026-10-29/README.md).

## Satellite query audit — 29 October 2026 (cloud)

Active isolated checkout `/workspace/actforgoa-satellite`, branch `codex/satellite-query-audit`, starts from fresh main `f20fc25`. PR95 is already merged; this audit uses [PR109](https://github.com/actforgoa2026/ActForGoa-website/pull/109). Concurrent map-controls main `05720cb` is reconciled, preserving PR108 and its place/search/drawing improvements. User requested a deep audit and fixes for selected-area/time questions, Amche/CDSE history and OpenAI image decisions. [Full findings and remaining acceptance](SATELLITE-QUERY-AUDIT.md); [checks and package evidence](../reports/satellite-query-audit-2026-10-29/README.md).

Implemented: actor-private spatial/time evidence retrieval, area-filtered history, pinned Amche intersections and cited ecology background, explicit map/workflow/readiness states, resumable existing jobs and improved scoped Decisions uncertainty. Initial main review `/map` was an older frontend/API deployment; the latest public check finds the new map frontend but nested satellite API still404, addressed in source by explicit Vercel handlers; current standalone has working real CDSE but no configured OpenAI. These audit changes are source-only until both existing standalone packages are deployed. Combined alias/research ownership is unchanged. No new paid calls, credentials or deployments in this audit. Browser tools unavailable, so fresh desktop/phone acceptance remains outstanding; cloud Railway binding still covers `.app` rather than required `.com`. Reconciled runtime checkpoint `97cde8be5cd79e1a2e1e620a216a3f9f7c133048`: 136 satellite Python tests, 221 Node tests, production build, both clean packagers and isolated API/app container checks pass. PR109 remains unmerged/source-only. Next: review/accept rendered desktop and phone behavior, then deploy both existing standalone services and explicit Vercel routes through the release owner. Exact package manifests and limitations are in the linked report.

## Satellite live imagery acceptance complete — 29 October 2026, 11:12 UTC

The user supplied new CDSE credentials through protected local storage and explicitly authorized configuration. OAuth validation succeeded; both values were sent to the existing Railway satellite API via stdin without logging secrets. API deployment `9014df8b-69de-4178-8072-135f96239875` reuses the accepted `11582ac` image, with all 14 satellite runtime files hash-matching. The app remains `b0fadee`, deployment `4bd7fc4b-8d60-487b-8219-bc978d07324f`. Both services are successful at https://satellite-app-production.up.railway.app/map. This supersedes the earlier missing-CDSE blocker below.

Fresh hosted acceptance passed: a new small Ribandar/Chimbel footprint returned ten acquisitions; explicit October 20 and 25 loads produced real georeferenced imagery. Desktop 1440×1000 and phone-sized browser 390×844 checks covered dated overlays, keyboard/button timeline switching, fresh named-account sign-in, saved comparison search/reopening and server-side cache reuse. The comparison correctly remains inconclusive because only 41.1% of this area is usable in both images. This is functional verification, not Goa field validation; optional AI interpretation/classification remains unconfigured and was not called.

Total new service reservations: five catalog searches, two image retrievals and one comparison. Both cached rasters remained byte-identical through comparison and phone reload; no third Process retrieval or duplicate observation job occurred. No AI request ran. The hosted runtime does not retain provider processing-unit headers, so no exact PU or currency charge is asserted. Original account access, saved recorded comparison, volumes and service tokens remain intact; a fresh SQLite backup precedes configuration. Temporary SSH verification access was revoked. Research accounting, the review Vercel alias and actforgoa.org were unchanged. Other agents and heartbeat remain paused. See `reports/satellite-cdse-2026-10-29/README.md` and the ignored `.reports/satellite-cdse-20261029/` evidence.

## Current local satellite rollout — 29 October 2026 (IST)

The user explicitly authorized the local ORCHESTRATOR to reconcile PR95 with current main and deploy both existing standalone Railway services. PR95 merged as `11582ac`; PR103 fixes the hosted OpenStreetMap referrer failure and merged as `b0fadee`. Both satellite services are deployed, retaining existing volumes and account/history data. Real Copernicus credentials remain absent; recorded comparisons must remain labelled as such.

The previous combined release is complete: source `1b79db83b3b90f547bee0ad466c175c92aa9b6ac`, review deployment `dpl_LWEsW2jqaauxfyhbHF5ZNGYCuykD`, accepted Sonnet runtime `961652d`, all71 semantic cases and3local/3hosted conversation checks passed. On October29 the user explicitly approved500 AI requests per UTC day and a$50 total October cap through October31, automatically returning to100/day and$5/month on November1. Enable only with `RESEARCH_HACKATHON_ALLOWANCE_20261029=1`. All prior reservations remain counted; this is not a ledger reset. The provider, prompts, retrieval, citation checks and per-request token/cost maximum remain unchanged. Verify the dated limits, production ledger continuity and public readiness without repeating accepted paid questions. Other agents remain paused.

PR95 checkpoint `b839bea86cfa942d6e57e42322286e4af9be0553` is being reconciled with main `1b79db8`, preserving newer homepage, editorial nested routes, research and citation corrections. Only documentation conflicts required manual concatenation; no historical acceptance evidence was removed. This operation targets project `e119f1f6-f1c7-4a58-a33c-0ea536dcfdce`, existing satellite API/app services and persistent volumes. Other agents remain paused. No combined review alias promotion, reporting service change or original actforgoa.org change is included. Final standalone deployment identities and hosted capabilities will be recorded in issue89 and the satellite release report.

## Satellite standalone deployment update

The user explicitly authorized a separate persistent Railway satellite release while ORCHESTRATOR retains the combined website release. App runtime `78e7fe4` and satellite package `fe935ed` are deployed in a new project `e119f1f6-f1c7-4a58-a33c-0ea536dcfdce`, at https://satellite-app-production.up.railway.app/map. No existing production service, website alias or actforgoa.org was changed. PR #95 contains the deployed source; it is not merged to main.

The user subsequently deferred copying the cloud CDSE secrets locally and requested useful progress without them. The app therefore provides authenticated reopening of a clearly labeled recorded real 10/20 October comparison, imported from the existing hash-verified validation evidence. CDSE access from Railway is not verified or configured. New retrieval and question interpretation are disabled; OpenAI decisions remain unavailable. Both services have separate persistent volumes, and the new satellite account does not copy or reset editorial accounts. See [release evidence](../reports/satellite-standalone-2026-10-28/README.md). Future work is secure real CDSE configuration and a new hosted retrieval, not a repeat of the failed OpenAI key-creation flow.

## Accepted runtime ready for hosted release

Research runtime `961652d` passes all 71 frozen semantic cases and three actual HTTP/browser conversation journeys, including the repaired referential follow-up. The 71 accepted cases and first two HTTP requests retain identical prepared queries/payloads after the focused retrieval fix; only the changed failed follow-up was dispatched again. Its prior failure remains charged. The final follow-up cites the original low-flow passages, preserves the draft policy attribution and states the missing dry-season salinity evidence. Desktop and phone checks show the rounded answer-first interface and correct exact-passage links. Research tests: 176 passed. Frontend integration: 193 Node tests and production build passed.

Final authorization is 160 combined requests on October 28 UTC and a $15.30 October conservative reservation cap, returning automatically to 100 daily on October 29 UTC and $5 monthly in November. Accounting reached 155 requests and $14.698659 reserved; four launch requests remain reserved. The exact 125-reservation delta after the recorded `7bf1965` production checkpoint was imported once with receipt `anthropic-validation-after7bf1965-through961652d-20261028-v1`, before/after backups, and unchanged historical counters. Failed and unknown attempts remain counted. No old sealed service package is deployable. Preservation byte audit passed for all 1,258 files and 31 directories after native test processes exited.

The remaining release operation is fresh accepted service deployment, hosted named-editor and AI checks, `release:review`, and native homepage routing cutover. This section supersedes older pending-budget and failed-acceptance status below; those entries are retained as the audit trail. Other local agents remain paused. Only the review alias is authorized.


## Browser follow-up correction

All71 frozen semantic cases passed on fe461dc; the first two browser journeys also passed. The third safely abstained because the eight-word question “How does that differ during the dry season?” lost its prior Mandovi/Zuari retrieval subject. The HTTP body carried the correct history, but the API only appended prior user context below eight words. Reservation154/$14.588499 remains charged and the journey remains failed. Referential follow-ups now retain the last user subject regardless of that length threshold; assistant history is never used as retrieval evidence. Verify the71 accepted request queries and two accepted browser queries remain unchanged before retaining their captures. Then rerun only the changed failed follow-up. Limits remain160/$15.30; four launch slots remain reserved.


## Final allowance approved and resumed

The user answered all pending allowance questions and explicitly approved the final160 combined requests for the Oct28 UTC window and$15.30 total October hard reservation cap. This supersedes the earlier155/$15 and160/$15 responses. At resumption it is Oct29 locally but still Oct28 UTC. The dated opt-in expires to100daily on Oct29UTC and$5monthly on November1; every failed/unknown reservation remains charged. Starting checkpoint:a77966e,66/71 accepted,146requests/$13.694491 reserved. Resume only assessment-service-enabling-law, boundary4 and three distinct HTTP/browser journeys, preserving four launch slots. Other local agents remain paused; issue89 records sole local release ownership. No deployment or generated-answer activation has yet occurred.


## Current conditional and document-selection correction

The combined PR93/94/96/99 candidate now has 66 of 71 frozen cases accepted on research runtime d58b786. Before that correction, it reached 55 accepted cases. The next saved-law case returned the correct 24-hour report deadline but converted the source's counterfactual danger condition into an assertion that immediate felling had not occurred. That answer remains failed and charged. Canonical accounting after the eleven-case consumed12 prefix is 146 attempts on 28 October and 13,694,491 microUSD reserved for October; production reconciliation is still pending.

Selected original excerpts containing an explicit counterfactual now receive focused guidance to preserve the condition, permitted action and deadline. No source text or generated answer is rewritten. Offline preflight also found that unrelated building documents crowded the individual-farmer form out of the input budget. Generic document ranking now distinguishes a named form/manual/law's subject from a trailing hypothetical condition and uses its title only for document identification. Full conditions remain in hybrid recall, within-document passage selection and model context; metadata remains inadmissible as factual answer evidence. All 55 accepted provider requests, selected sources and assembled answers remain identical in exact capture replay. All 16 remaining cases now include their frozen required passages. These are offline checks, not fresh paid or hosted acceptance.

The research source passes 171 tests. The homepage integration below passes 193 Node tests and the configured production build. Research backend, server and API source remain byte-identical to d58b786. Local desktop/phone checks cover integrated homepage, topics, About, directory, reporting, emergency actions, guides, forms/PDF, editorial curation and blog workflows. Hosted AI and named-account checks still remain.

Only 150 combined attempts today and $15 October are approved. Completing all remaining checks plus four reserved launch requests requires at least 158 attempts and a conservative $15.041 total reservation. A replacement request for 160 today/$15.30 October is pending and must not be applied without the user's answer. Paid testing is stopped at146 to preserve four launch slots. Next is assessment-service-enabling-law, then four boundary cases and three distinct HTTP/browser journeys. Do not dispatch until adequate new authorization or a UTC reset; preserve every failed reservation. No source expectation is relaxed. Daily 100 resumes 29 October; monthly $5 resumes November. No new production accounting import, activation or alias promotion has occurred. The local ORCHESTRATOR remains sole release owner; other local agents stay paused.


## Native homepage integration and routing cutover

PR98 head887a41da contains the already-public animated homepage. It is integrated with PR99 guided topic routing, PR94 staff curation and the rest of current main in the focused release branch. The orbit composer routes to named topics; ambiguous wording retains the question and links to the eight topic choices. The separate conversation link still opens Ask. The original photos, motion/pause control, headline, new labels, navigation gradient and sectioned feed are preserved. Small-phone input text is16px and its placeholder fits.

Actual Chrome checks at1440x900,390x844 and320x740 found no horizontal overflow or italic text. All39 hero photos loaded; visitor staff controls were absent. Food-waste and ecosystem questions reached the correct topic; ambiguous input announced a fallback and focused the topic heading at104px below the header. The phone Resources menu retains legal/ecology/general research. Impeccable source inspection has no non-advisory findings; inherited colors/radii remain advisory. Evidence is ignored .reports/orbit-integration/. These are local integration checks, not hosted acceptance or new AI generations.

The public alias currently has host-scoped project routing overrides for root, /explore and /orbit-assets. Production routing version2e8e015b-ac52-4c67-bfe6-e66ca3070f4b points them at actforgoa-explore-assets.vercel.app (owner-reported deploymentdpl_DhYDhkrruPcWxhc8zdz6v1zqDAB1). An alias deployment ID alone does not prove the served homepage source. Keep these overrides until the integrated native build is accepted; follow the explicit cutover procedure in docs/RELEASING.md. No routing rule has been changed by this integration. Other local agents remain paused; the local ORCHESTRATOR is sole release owner under the direct user resumption.


## Reviewed source inconsistency

The b98b352 candidate reached39 accepted cases before biodiversity-04 reproduced an internally inconsistent statistic in the original report:158 of218 amphibian species was printed as87.8percent. The original PDF physical page135 was rendered and inspected; the inconsistency is in the source, not an extraction repair. The failed answer and its reservation remain rejected/preserved. The existing exact-byte source-review registry now excludes only that passage from answer evidence, while original-document access and search remain available with a warning. No corrected number, source text, prompt or frozen expectation is substituted.

All39 accepted provider payloads, selected source lists and assembled answers were re-prepared/replayed and verified identical after this source-review change. They remain captured-generation evidence, not new paid HTTP passes. The failed case has a changed evidence payload and requires a fresh dispatch. Canonical October28 accounting is118attempts and10,582,575microUSD reserved. With32 frozen cases,3HTTP journeys and4launch slots still needed, the minimum is157total attempts. Only150today/$15October is authorized; the160-today request is still pending. Continue only stages that preserve4launch slots and the hard monthly cap. Default100daily resumes29October and$5monthly resumesNovember. No public activation or alias promotion has occurred.


## Focused contrast-retrieval correction

The combined candidate includes merged PR93/94/96/99. Acceptance on5456414 reached22 accepted cases, then water-10 failed HTTP502: its missing-evidence note was550characters against the unchanged500-character bound, and it returned no coverage for a case expecting a supported answer. The failed output remains rejected and charged. Canonical October28 accounting is100attempts and8,584,037microUSD reserved; production reconciliation is still pending.

The cause investigation found comparison alternatives crowding out the requested subject: generic coverage ranking now favors the subject before explicit “rather than” or “instead of”, while both sides remain in hybrid recall and the model question. The changed request includes the original Goa water-policy passage on gauging and discharge-data limitations. No source, prompt, provider schema, answer bounds or frozen expectation changed.166research tests pass. All22 accepted requests, selected-source lists and accepted assembled answers were re-prepared/replayed and verified identical; those real captures remain evidence without duplicate paid generations. The failed water-10 requires a fresh dispatch on its changed payload. No result is a new live HTTP pass merely because replay succeeds.

All71 frozen cases and3HTTP journeys remain required. From100attempts,49remaining cases plus3HTTP journeys and4launch slots need156total. A replacement160-today request is pending; only150today/$15October is authorized until the user answers. Stop before a stage would spend reserved launch capacity or exceed either hard cap. Default100daily resumes29October and$5monthly resumesNovember. No alias promotion before acceptance, accounting reconciliation, fresh packaging and hosted verification.

## Current citation-assembly correction

PR99 homepage routing is integrated alongside PR93/94/96. PR94 has landed on main as d4268ff; PR96's routine merge conflict is being reconciled. Sole local ORCHESTRATOR retains review-alias promotion ownership. The named editorial account is preserved. No public deployment has occurred.

The a2b0070 request configuration passed water-04, scope-01, RTI, TCP and farming semantic review. The next dog-relocation answer failed HTTP validation because its second paragraph omitted a context ID already present in the supplied evidence and first paragraph. The failed reservation remains charged. Canonical October28 accounting is83attempts and6,691,025microUSD; production reconciliation remains pending. Caps remain150today/$15October;155today is awaiting user approval.

Citation assembly now expands each selected passage to its exact required original context on the server, with missing/cross-document/cyclic context rejected. Generated prose and original source bytes are never repaired. This changes response assembly only: the model, prompt, strict tool schema, evidence selection, xhigh effort,5632token output ceiling,20000byte input ceiling and60second timeout remain unchanged. Before retaining any generation evidence, compare each newly prepared request byte-for-byte with its captured provider payload, then replay that real response through the corrected assembly and repeat semantic review. This is a new assembly test, not a relabeling of the old HTTP failure or a duplicate paid generation. All71 frozen cases plus3HTTP journeys and hosted checks remain required; report capture reuse and fresh dispatch separately. Any changed provider payload invalidates its capture. All failed and unknown accounting is retained, with no refunds or cap bypass.


Feature development, tests, indexing and browser QA ran under `/workspace` in the cloud. CLOUD owns this implementation. The user subsequently appointed **Coordinate agent threads and PRs** (`01a181ad-56ba-70c2-93cd-1aa5185d007a`) as the continuing cloud release coordinator. Its durable inbox and release record is [issue #89](https://github.com/actforgoa2026/ActForGoa-website/issues/89). The earlier proposal to resume the local ORCHESTRATOR is superseded; keep local workers and their old heartbeat paused. The user then directly instructed CLOUD to “ship it”: CLOUD is completing the bounded PR #90 source landing; the primary coordinator retains live deployment ownership.

## Focused Sonnet source review and acceptance checkpoint

The sole focused release owner remains the local ORCHESTRATOR under direct user authorization. Fresh main includes PR97 offline recovery; those experiments are retained but are not integrated as runtime validators. PR93, PR94 and PR96 remain in the combined candidate. Other local chats and the old heartbeat remain paused.

Candidate15492ba passed its two diagnostics but failed the critical RTI case: the official FAQ itself has ambiguous jurisdiction wording that became a definite rule. Ten critical responses and one interrupted unknown were reserved; all are retained. Canonical accounting is72attempts on2026-10-28UTC and5,455,733microUSD reserved for October. The original stage is rejected. The source review registry now excludes only the exact passage ID, document, URL and text hash from generated-answer context, with an explicit search warning. Corpus bytes, source search and original-document access remain unchanged; no wording is silently repaired. Regression tests cover changed-source identity and atomic table context.

Fresh71cases plus3HTTP journeys require74attempts, ending at146 and leaving4launch slots within the approved150. Worst-case additional reservation is8,387,456microUSD, within the approved$15October cap. Sonnet uses high adaptive effort,4096tokens,60seconds and one strict call; no retries. Review each captured case before dispatching the next. Frozen expectations are unchanged. Any failed case stops the stage. No previous runtime pass transfers. No AI activation or alias promotion before acceptance and actual hosted browser checks. Named editorial account exists; do not reset it.

## Retrieval correction after first Sonnet acceptance

The first Sonnet candidate failed the critical stage: ambiguous RTI wording became a definite rule, a farming deadline came from locator metadata rather than its cited passage, and exact/private-measurement cases did not abstain. All15Sonnet attempts remain charged. Canonical Oct28 is59attempts andOctoberreserved4,019,675microUSD. No remaining paid stage ran on that failed candidate.

Inspection found that the cloud backend dropped the previously reviewed passage-selection and exact table-context helpers. They are restored from ab21949 and adapted to preserve current domain filters, public API shape and strict single-tool provider contract. Prompt budgeting retains required source/header groups atomically. Actual indexed excerpts now include the RTI applicant manual fee/payment paragraph, the farming clause6 deadline and the Mandovi monsoon-salinity account. Locator claim summaries are removed from provider context; dates and limitations remain. Sonnet uses high adaptive effort within the unchanged4096-token/60-second/cost ceilings, and explicitly abstains from unavailable exact measurements or fabricated evidence. Fresh71+3acceptance is still required; no prior passes transfer. Default and approved dated budget limits are unchanged.

## Current Sonnet release authorization

On 28 October the user explicitly approved Claude Sonnet 5.5, a $15 October total AI cap and 150 combined testing/public requests for this UTC day. Default daily100 resumes29October; monthly$5 resumes1November. The dated opt-in is checked within ledger transactions and expires without requiring a restart. All failed and unknown requests remain charged. Canonical accounting before Sonnet acceptance is44Oct28attempts and2,387,513microUSD October reserved. The74 remaining checks reserve at most8,387,456additional microUSD;32launch slots remain within150 if all pass. This supersedes the earlier120-testing/$5 authorization below, without waiving accuracy checks.

The full combined PR93/94/96 runtime will be validated fresh with Sonnet, medium adaptive effort, a4,096output-token ceiling and60second timeout. The latest Haiku scope answer still generalized a104-bird survey into104species without its bird qualifier and is rejected. Mechanical validity is not semantic acceptance. No failed result transfers to Sonnet. The named editorial account has been provisioned securely; hosted workflow verification and review-alias publication remain outstanding. Other local agents remain paused.

## Resume here

The user subsequently resumed the local ORCHESTRATOR for a focused release, then explicitly requested an audit and correction of the live acceptance failure. Issue #89 records sole promotion ownership. Other local workers and their heartbeat remain paused. The clean `codex/anthropic-release-contract` worktree is the correction owner; do not promote concurrently.

Live acceptance on merged `7bf1965` failed on source identity and length. All reservations remain charged. The focused correction is now integrated with #92's warm/simple five-paragraph/300-word contract and #93's answer-first rounded chat UI and complete excerpt/location context. Provider responses use five nullable paragraph slots and select only supplied passage IDs. The server resolves support references to the complete unmodified source text, including damaged PDF/control characters, instead of asking the model to copy quotes. Unknown references, invented quote objects, unsupported fields and overlong answers fail closed. This guarantees source identity and lossless supporting text; it does not establish semantic entailment. The frozen 71-case semantic gate plus three distinct HTTP journeys remains required, with fresh acceptance on this combined runtime. No prior failed answer is relabeled accepted.

The user authorized up to 120 attempts for acceptance testing on 28 October UTC only, keeping the $5 monthly cap; public runtime remains capped at 100 unless separately authorized. Canonical accounting after the pre-integration diagnostic is 37 attempts on Oct28 and2351412microUSD for October, including all failures. Other local workers and the old heartbeat remain paused. The editorial service is deployed separately but hosted workflow checks, account provisioning, full AI acceptance and publication remain pending. The user also requested integration of PR #94's shared website/dashboard curation before release. Issue #89 records source, service and deployment identities.

Read this file and `AGENTS.md` before doing work. Inspect `git status`, fetch `origin/main`, and compare workstream commits below before rebuilding or deploying. Never treat an in-progress row as completed. After each handoff, update its implementation, tests, merge and live states separately. Keep pending questions and exact next actions here so another agent can resume without the chat transcript.

## Focused release continuation and provider guidelines

The user renewed the instruction to ship PR93 and PR94 with working AI and the named dashboard, explicitly excluding satellite work, then added the recent About copy in PR96. All three are integrated in the focused local checkout. The editorial account is now provisioned securely; credentials are outside the repository and chat. Hosted login, curation and publishing acceptance remain pending.

Current primary-provider documentation confirms forced tool choice skips adaptive thinking. The candidate now uses automatic selection of the one strict answer tool, explicit adaptive thinking at medium effort, and a 4,096-token combined output ceiling whose full maximum is reserved before dispatch. The 60-second timeout, 300-word/five-paragraph answer bounds, no automatic retries, frozen accuracy criteria, $5 monthly cap and public 100-attempt daily cap remain. The earlier forced-tool water answer is not accepted: its assessed-area table summary incorrectly changed the measured quantity to all assessed units. The interrupted scope attempt remains unknown and charged. New acceptance must use the corrected request setup; no prior failed or unknown result is transferred.

The preserved 1,174-document candidate already has substantive verified PIB extraction for V08 (53 chunks) and V15 (2 chunks). The PR90 refresh-script finding affects future rebuilding of already-present originals; it does not require replacing this verified preserved generation. Do not rebuild it from the old extraction branch. Follow the documented [AI integration guidelines](AI-INTEGRATION-GUIDELINES.md) before changing provider settings. They are based on current primary documentation, with local regression checks and live semantic acceptance kept separate.

## Latest voice follow-up and active release operation

After PR #90 merged as `7bf1965a2c46f76537437a822056b2bf9023f96c`, the user chose **warm, friendly and simple** as the answer voice. The follow-up branch `codex/warm-research-voice` updates the shared legal/ecology prompt, honors requests for simpler wording or more detail, and replaces the rigid 180-word/three-paragraph rejection with a 300-word/five-paragraph maximum while keeping simple answers short by default. Citations, evidence qualification, outside-context separation and budget limits remain enforced. See [RESEARCH-CLOUD-HANDOFF.md](RESEARCH-CLOUD-HANDOFF.md#answer-voice) for the editable editorial brief and exact limits. No dashboard voice control is included.

Implementation and offline verification are complete: **119 research tests pass**. The new regression checks a longer four-step answer, citation preservation and failure for fabricated support or oversized text. Live tone/semantic acceptance and deployment are still pending; the follow-up is not automatically merged into a release being prepared elsewhere. The prior portable runtime hashes describe PR #90, not this changed prompt.

The latest operation recorded in [issue #89, comment 6465343889](https://github.com/actforgoa2026/ActForGoa-website/issues/89#issuecomment-6465343889) reports a direct user-authorized focused local **ORCHESTRATOR** release. Treat it as the active promotion owner and do not race it. Other local workers and the old heartbeat remain paused; the primary cloud coordinator keeps reporting oversight. This newer operation supersedes the earlier default deployment-owner wording below. The release owner should review/include this voice follow-up before creating its accepted runtime package, and record its exact head and actual live acceptance. Existing full-corpus/accounting gates and the separate post-merge legal extraction finding in #89 remain outstanding; this voice change does not resolve them.

### Voice landing checks and current live hold

The user subsequently instructed CLOUD to ship [PR #92](https://github.com/actforgoa2026/ActForGoa-website/pull/92). This authorizes its source landing; the exact merge result is recorded in #92 and issue #89. The unchanged voice runtime from `6016ba3` has 119 passing research tests, 178 passing Node tests and a passing production build. An independent scoped code review found no actionable issues. Six cloud Chromium UI-fixture checks cover legal/ecology answers at 1440px, 390px and 320px: all five paragraphs/300 words and citations render intact, outside context stays separate, and there are no page errors or horizontal overflow. These are layout checks, not live generated answers. Evidence is in `reports/voice-shipping-2026-10-28.json`. The Impeccable skill remains unavailable in this executor.

The local release owner now [reports working Vercel/Railway credentials and a live acceptance hold](https://github.com/actforgoa2026/ActForGoa-website/issues/89#issuecomment-6465660719). On the earlier `7bf1965` runtime, water-04 returned a mechanically valid answer without final semantic acceptance; scope-01 returned an app 502 after the provider used document titles as citation IDs while its supports used passage IDs. That captured answer also exceeded the old 180-word bound, and the owner flagged ecological scope/population wording concerns. Only the length bound is changed by the voice follow-up: citation identity and semantic issues remain unresolved. Do not relabel the failed capture as accepted, replay unchanged diagnostics or bypass validation. The remaining cases and HTTP/hosted/admin checks have not passed. The owner retained both charged reservations, reconciled accounting and stopped promotion; deployment of AI answers remains held.

## Internal tools continuation — public-site curation

The user requested shipping the blogging/internal tools, then added curation while browsing the normal website. Source `26a447bfea5d7c3d2129b160ba0130a4ed64d504` on `codex/internal-tools-shipping` adds staff-only stars on public records, the staff browsing bar, direct dashboard team-picks view, and cross-tab synchronization of the existing shared curation. It preserves relevant-only ranking and private sessions. See [the scoped handoff and verification](../reports/internal-tools-2026-10-28/README.md).

Implemented and cloud-tested; this follow-up is pending integration and is **not live**. 178 Node tests/build and 17 local real-service browser checks passed. Cloud Railway requests return a Cloudflare 403, despite a ready binding. The user explicitly chose **ORCHESTRATOR’s working local access** to deploy. No competing alias promotion or service creation occurred here; the existing focused release owner remains responsible for the hosted editorial service, named accounts, server-only Vercel wiring and actual hosted checks. This request does not waive research acceptance or increase its budget. The original domain remains out of scope.

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

Latest satellite instruction: user explicitly authorized getting an iterative version live and requested a local deployment handoff. **OpenAI is optional for initial imagery publication.** Cloud published an isolated static preview using verified real recorded imagery, while [the local handoff](SATELLITE-LOCAL-DEPLOYMENT.md) covers full hosted comparison service/admin wiring. The active local ORCHESTRATOR is still working on combined research release acceptance; its aliases and services must not be overwritten. Main `9cea6e2` was reconciled in satellite merge `cfcbc1f`, preserving its research evidence/hold. Railway access is blocked by this executor's `.app` credential-host binding versus Railway's documented `.com` API; cloud tools cannot edit that binding or export real CDSE secrets.

Recorded preview **live**: source `18112a2`, deployment `dpl_4b7qNRdy2VsQEhXLig7bBF2sgEhP`, existing Vercel project, preview target. New-project creation was forbidden, so only an isolated preview deployment was created; project build/protection settings and production `dpl_FzbANqhz96u2JNt2eb6fK4BDtS7c` are unchanged. A seven-day deployment-scoped share link was supplied to the user; token omitted from Git. Anonymous desktop/390px/320px hosted checks pass. [Evidence](../reports/satellite-preview-2026-10-28/README.md). **Full hosted queries remain unconnected; PR #95 remains unmerged.** No CDSE/model calls or research generation occurred during this preview publication.

## About copy update — 28 October 2026

Branch `codex/about-copy-update` replaces the About page's historic introductory text and imported blocks with the user's supplied platform statement, content policy, Kokum Trust attribution and gratitude paragraph. The archive link, sidebar and field-guide provenance remain available. Implementation complete; production build passes and Chromium at 1440px and 390px confirms the supplied copy and no horizontal overflow. Screenshots: `.reports/about/1440.png` and `.reports/about/390.png` (local). Rendered desktop/phone reviewed; Impeccable skill unavailable in this executor. Merge and live deployment pending; existing release owner retains promotion ownership.

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

## Homepage search routing, 28 October 2026

Feature commit `9cdac9c09e6da4f1734ed6f23daa7b1f844f1fa7` on `codex/home-search-routing` changes the homepage question composer to open the matching top-level topic menu, exactly like its large topic button. Emergency requests use the existing emergency destination; unclear or competing needs retain the input and offer the topic choices. Catalogue search retains its existing filters and retrieval behavior. The user explicitly requested shipping.

Implemented and verified in an isolated checkout based on fresh main `9cea6e2`: 191 Node tests pass, production build passes, all eight topic destinations and emergency routing were exercised, and desktop/phone render and retained-route smoke checks pass. Impeccable reports no primary findings. Exact runtime hashes, screenshots, scope and limitations are in `reports/home-search-2026-10-28/`. Source landing and live deployment are pending at this handoff. The active ORCHESTRATOR retains combined promotion ownership; this feature chat has not changed the public alias. Next: review/land the branch and include it in the coordinator’s accepted release through `release:review`.

## Satellite map and timeline — 29 October 2026 (IST)

The user requested an actual selectable map and temporal exploration using Amche context. Latest PR #95 source now implements a map-first workspace, opt-in attributed Amche water-body/private-forest overlays, real-acquisition slider, explicit single-observation retrieval, correctly reprojected map imagery and separate before/after analysis. Authenticated observation jobs and bounded actor-private cache prevent repeat retrieval while browsing; no model is called by scrubbing. Single display PNG per observation keeps responses within existing 4 MiB proxy bounds. Source was reconciled with main `51abb34` in `b5ba7d5`, preserving all newer site features.

[Verification](../reports/satellite-map-2026-10-29/README.md) distinguishes synthetic-provider UI checks from a real new Mandovi-area October 20/25 retrieval. Both images retrieved and projected successfully, but only 53.98% common usable coverage correctly prevents a reliable overall change conclusion. Cache replay and pair reuse passed; no live AI ran. The timeline is implemented/tested and awaiting standalone deployment. Existing live app remains https://satellite-app-production.up.railway.app/map on older source; new-area queries still need real CDSE variables in Railway. The old static preview is not the product flow. No main merge, deployment, alias promotion, hosted credential change, research generation or ledger reset occurred in this continuation.

Final map/timeline runtime is `f181babf0b757e069f91609cbca0f8ee30e8adc9` (feature `cc1d399`, saved-area navigation fix `f181bab`). Verification: 83 Python satellite tests, 202 Node tests, both builds, packaged API 17/app 18 allowlisted files, and final Chromium 1440/390/320 flow pass. Actual Amche datasets load; the real river pair is replayed locally with visible geographic alignment. Initial phone fit failure is retained and corrected. Package commit `100868d` has the same runtime. Evidence and exact hashes are in `reports/satellite-map-2026-10-29`. Implemented/tested only; no new deployment.

## Secondary orbit chat landing — 28 October 2026

Branch `codex/goa-orbit-landing`, based on freshly fetched main `a786df5`, adds `/explore` as a separate above-the-fold chat landing inspired by the supplied Cosmos reference. Three concentric photo rings rotate at 90/150/240 seconds; existing local Goa/community images surround the central question bar. Pause/resume, reduced-motion, suggested questions and draft transfer to `/ask` are implemented. Existing home, header/footer and chat availability rules are preserved on other routes. No generated images or paid inference.

Implemented + tested: 178 Node tests and production build pass; Chromium desktop 1440px and phone 390/320px validate image loading, no overflow/page errors, animation control and exact question transfer. Evidence: `reports/orbit-landing-2026-10-28/`. Impeccable is unavailable in this executor. Not merged or live. The release owner should integrate the feature commit and review `/explore` before including it in a coordinated release; no alias promotion was attempted.

### Orbit landing live follow-up

User explicitly requested shipping `/explore` on the existing field-guide URL and aligning photos upright. Source `755177e` implements the alignment. The page is now live via two scoped Vercel project routing rules, with isolated static deployment `dpl_4VzSLExLmufsCCJ9HvNohACTbFXu`; existing production deployment/alias is unchanged. Public desktop + 390/320px checks pass, including loaded photos and exact draft transfer. Full publication/route IDs and retirement instructions are recorded in `reports/orbit-landing-2026-10-28/README.md`. Implemented, tested and route-published; PR #98 source is not yet merged. Future release owners must remove the scoped routing overrides when integrated `/explore` is deployed and verified.

Orbit page follow-up `ce0b0ed` is live through isolated asset deployment `dpl_8LKejjCqfL5fdVNoDx77d6YPeEtn`: no eyebrow labels; upright photos spiral inward at initial 5× speed and settle to 1× in three seconds. Build and live Chromium entrance checks pass. No change to existing production target or project route definitions. `AGENTS.md` records the user's explicit no-eyebrow preference.

Orbit follow-up `27285db` is live via isolated deployment `dpl_8RDqSrA9CZafsYWEpDX9qRGUAqqo`: entrance now completes 3/2.5/2 turns in three seconds (inner to outer), then settles to steady orbit. Photos increase in size outward (62–78 / 86–102 / 116–132px). Build + public desktop/phone checks pass; latest evidence is in the orbit report directory. Existing production target and route rules remain unchanged.

Explore update `a9f8e4a` is live through isolated deployment `dpl_36ZVhBLW4cF3MNmmsBhUe7WebRdj`. Reuses the homepage navigation component and adds Cosmos-style rolling capability examples beneath “A place to”. No eyebrows; pause and reduced-motion include text. Build + live desktop/phone menu, layout and phrase checks pass. Existing production target/routing definitions are unchanged; source remains on PR #98 for integration.

### Animated main homepage publication

The user explicitly requested replacing the main homepage hero with the orbit landing, keeping the main-path buttons and additional content below, with the original homepage search behavior. Local `1ca0e0c` and remote source commits `06770c9` / `6a45736` / `79dab98` implement this. Source sync used GitHub contents API after shell Git push access expired; do not confuse local and remote commit identities.

Live deployment `dpl_AfenrgMxRbbxqHQCjuF2fMASeBSp` now serves both `/` and `/explore` through scoped project routes. Root route `7ff31abb-9b89-4c3c-89d0-de36bf52a435` was added; active routing version is `2e8e015b-ac52-4c67-bfe6-e66ca3070f4b`. Existing production target and APIs are unchanged. All 178 tests, build, and public desktop/phone checks pass. Search uses `searchDestination`; eight topic paths and discovery feed remain below the hero. The entrance is 70% gentler, with 39 distinct tile photos from a 42-photo pool. Future release owners must retire all three root/explore/asset routing overrides when native integrated source is deployed and verified. Full handoff and screenshots: orbit report directory.

Latest orbit motion/fade source: local `71a69c2`, remote `ec734aa` including helper/hero/App updates. Actual Cosmos client code showed independent equal-distance inward spiral travel, with a 700ms speed ramp before decay, rather than rigid rotating rings. The adaptation preserves upright photos, unique images and gentle intensity; navigation now overlays the scene with a soft gradient. Live isolated asset deployment is `dpl_2jZiMe2bDLbgga2fr5YXRCXYiR1s`; existing root/explore/asset routes and production target are unchanged. Build and desktop/phone motion/layout/search checks pass; see orbit report for source URLs and exact parameters.

Latest circle homepage updates: `231f82d` starts the burst immediately when images decode (7.9× easing only downward to 1×), correcting the slow-start report. `f1fce7f` enlarges main-path cards, recovers “Community and Youth” / “Biodiversity” wording from HOME MENU, and lifts the hero 30px desktop/20px phone. Source synchronized remotely through `0446a77`; current isolated asset deployment is `dpl_6r9oafbneujYTFNdGjbYukNmbZsK`. 178 tests/build and public desktop/phone card, copy, navigation, search, layout and motion checks pass. HOME MENU's other unpublished support/schemes/nav work remains separate. Routes/production backend target unchanged; see orbit report for evidence and retirement instructions.

Homepage scroll cue: local `db49109`, remote `bfd0452` adds the bottom-center downward arrow, smooth scroll/focus to the main-path buttons and immediate scrolling with reduced motion. `/explore` now shares the complete homepage composition. Live isolated deployment `dpl_DhYDhkrruPcWxhc8zdz6v1zqDAB1`; build and public desktop/phone arrow checks pass for both routes. Existing project routing/backend target unchanged; orbit report has evidence.

## Visual simplification — 29 October 2026

User requested substantially less repeated text/components and more imagery. Isolated branch `codex/visual-cleanup`, based on fresh main `1c4ac7c`, implements this in `cdfc4de`: label-only navigation, fewer top-level links, shorter homepage/catalogue presentation, image-led article cards, three reading picks and three compact contacts on topic pages, and licensed local Wikimedia Commons supplemental covers for articles without images. Original images/body content and substantive draft/source/service notices remain. Credits, license links and derivative sidecars are included.

211 Node tests pass, production build passes, Chromium 1440/390/320 checks pass for main browsing routes, compact topic sections and action/menu navigation. Blog list/detail and original-inline-image retention use explicitly local API fixtures; no hosted editorial acceptance is claimed. All tested images load; no horizontal overflow or page errors. Final screenshot evidence and limitations: `reports/visual-cleanup-2026-10-29/`. Impeccable is unavailable in this executor; no detector pass is claimed.

Implemented/tested only; source landing and deployment remain pending with the release coordinator. No alias promotion, backend/service/account change or paid inference. Next: review this branch/PR and include the accepted change through `release:review` under existing coordinator ownership.

## Local map control follow-up — 29 October 2026

Direct user requests extend the focused local shipping authorization: fix map drawing, add area/business search and current-location access, and make the map larger with actual Arc/shadcn controls. Other local agents stay paused. PR105 was published through `release:review` at `f20fc25b88681fc7228002a4ca63b8a1dbab2230`, deployment `dpl_D3RkM62YFcnLXRy1Me9ZMbRU2h84`, with live desktop/phone checks. See issue #89 comment 6495781299.

Map implementation/acceptance is in `reports/map-controls-2026-10-29/README.md`. Local gates pass; deploy the allowlisted standalone app package to existing Railway service `aea6b770-cd6d-4165-9802-7ce46fa0fd4a`, preserving `/data/admin`, then verify saved imagery/history and the new controls. Promote the combined main frontend through `release:review`. No satellite API/corpus/accounting migration or paid AI revalidation is required by this frontend/gateway change. Record final identities in issue #89.

## PR109 local release continuation — 29 October 2026

Direct user authorization resumes the local coordinator for this focused release; other local agents and heartbeat remain paused. Issue89 comment6496808456 holds coordinated satellite API/app/editorial/Vercel ownership. Current main05720cb is contained in PR109; 136 Python/221 Node tests, build and CUA desktop/phone acceptance pass with retained real imagery and a disposable recovery fixture. Positive small intersections now show `<1%`. See reports/satellite-query-audit-2026-10-29/README.md.

Next: merge reviewed source; clean API then app packages to the existing Railway services; connect the existing editorial proxy and ecology origin; promote only the review alias through release:review; verify hosted retained imagery, private evidence and exact passage links. OpenAI is absent in hosted/local configured access, so no live Decisions call ran and no ledger was reset. Missing optional AI does not block this imagery/evidence deployment.
