# Cloud implementation and landing plan — 28 October 2026

## Homepage AI library button live · 30 October 2026

PR #136 merged as `4fdbfdbcd7eb4dbeeb602d732877943cabbf1f89`, tree `88f6752c3b4f194b1aa2099742f8fd6832c80b6f`, and is live at the existing field-guide alias on Vercel `dpl_5APj4U1KGWzZE1BfUTA9iHamUG9m`. Existing Arc ButtonLink “Use AI to explore our vetted library of surveys and guides” targets `/ai`, precedes the homepage search, and shares its width. Latest carousel, category groups and footer are preserved.

Validation: all 281 tests and production build pass; actual local and public Chromium checks cover 40 retained route renders on desktop/phone. At 1440/768/390/320px the complete button is above the fold with no horizontal overflow; desktop/phone clicks reach `/ai`. Rendered public screenshots inspected. Impeccable unavailable in this executor. No model call or report submission ran; backend/corpus/credentials/original WordPress unchanged. Rollback is `dpl_D5QinYMGKHoHPe7rof1Jwb5mkgCb`.

The unchanged guarded release passed all pre-promotion research, editorial, staff/public-map, newsletter and MCP probes before final promotion. Transport incidents are recorded explicitly: an initially ignored staging query assigned the alias early, so the prior deployment was restored; the transport was corrected to Vercel CLI’s `autoAssignCustomDomains:false` behavior. The guarded retry reused the same ready build and passed all probes. Its immediate post-promotion inspection raced asynchronous alias propagation; subsequent independent API inspection and public browser acceptance confirmed the expected deployment. The transport now waits for alias convergence. Protected evidence and full incident record: ignored `.reports/home-ai-button/{evidence.json,verified-release.log,published.json,live-routes.json,live-check.log,release-notes.md,live-1440.png,live-390.png}`. This documentation-only completion record is excluded from deployment uploads; no further deployment is needed.


## Homepage carousel and categories verified live · 30 October 2026

The user corrected the standard homepage after the NOTES release: restore the original hero photo carousel with centered mission wording, group topics into Climate/Civic/Culture, enlarge and describe the field-guide sections, and blend the taller stippled footer illustration behind its links. Isolated `codex/home-carousel-categories` preserves current main `2f21e61`, the separate AI homepage, reader cleanup and all NOTES destinations. Actual Arc controls and credited existing photos are reused; the heading stays still while photos rotate. New English copy is tracked for editorial translation.

PR138 is live through `release:review`: runtime `00c34d494ed2699f6b9793cf86f40c1efce657dc`, tree `e33879ef6843c537aac03c69001e25c70e91c175`, Vercel `dpl_D5QinYMGKHoHPe7rof1Jwb5mkgCb`. All 281 tests, the production build and staged service probes passed. Local 320/390/768/1440px renders, carousel autoplay/manual/pause controls, topic search, all fifteen topic/plan links and forty retained desktop/phone route renders passed; final public acceptance repeated the forty route renders and confirmed the carousel, categories and blended footer. Impeccable and rendered checks found no overflow, italic text or decorative side stripes. See `reports/home-refinement-2026-10-30/README.md` for evidence and rollback. Local ports 4176/4197 remain running; original WordPress is unchanged. This completion record needs no further deployment.

## Document reader formatting live · 30 October 2026

User authorized “ship it”. PR #135 merged as `2f21e6192b7a00fe78ce3ffbd87d9a52b669d9e3`, tree `c66faf26c1bd841c0fe528a786e9776fe975e1c8`, preserving the newer AI composer release. Plain Read text removes passage backgrounds, reflows print lines into paragraphs and keeps headings, captions, lists and table rows separate. Stored source text, citation URLs and Original page remain intact.

The unchanged guarded `release:review` promoted Vercel `dpl_6Z5f6f1ZbXeXzJaY5qnGcdFdwZsH`. All 281 Node tests, production build and staged research/editorial/public-map/newsletter/MCP service probes passed. Local Chromium checked 34 desktop/phone route renders; the focused reader also passed at 320px. Actual public desktop/390px acceptance confirms plain paragraph flow, no marks/overflow/page errors, loaded original PDF page image, next/previous navigation, and retained `/`, `/AI`, `/explore` pages. Rendered public desktop/phone screenshots were inspected. No model call or submitted report ran; no backend, corpus or credential configuration changed.

Evidence and project-scoped REST transport are under ignored `.reports/reader-cleanup/`: `evidence.json`, `retry-release.log`, `live-identity.json`, `live-checks.json`, `live-{1440,390}.png`. Initial redundant upload failed authentication before creating a deployment; retry reused unchanged content-addressed files and uploaded the changed source. Final alias identity and release commit independently verified. Impeccable is unavailable in this executor. Rollback: `dpl_icX57yDd1PWwh6PnCfFd4M3McfXi`. Original WordPress domain unchanged. This documentation-only record is excluded from deployment uploads; no further deployment is required.

## AI composer surface, source intro and arrow live · 30 October 2026

User requested removing the inner surface visible while typing and mentioning vetted surveys and data above the composer. The cause is Arc Textarea's higher-specificity hover treatment. AI-only hover/focus overrides keep the field transparent while preserving the outer keyboard focus outline. Intro copy now explicitly says the AI draws on vetted surveys and data.  The same follow-up removes provider-branding copy from the homepage and replaces the text send label with an up-arrow inside the installed Arc Button, retaining a 46px target and accessible “Send question” name. No destination or backend change.

Live verification: PR #133 merged as `bbfb018aade2f39344ea1fd86bdac4530ded0f5c`, tree `675d18691c1c6bed98aec80f7362677313f9531f`, promoted via the unchanged guarded release to Vercel `dpl_icX57yDd1PWwh6PnCfFd4M3McfXi`. All 279 tests, build and staged service probes passed. Desktop/390px/320px public browser checks verify transparent hover/focus/typing states, the vetted-surveys/data intro, no provider-branding copy and the accessible Arc arrow. Clicking the arrow on public desktop/phone opens exactly one actual reviewed cached answer; zero model calls. Local checks cover 34 retained/new route renders. Rendered desktop/phone screenshots were inspected. Evidence: ignored `.reports/ai-home/surface-{release.log,evidence.json,live-checks.json,live-final.json,live-1440.png,live-390.png}` and `composer-live-results.json`. Rollback: `dpl_E4dHjcZFCzeiR1wwbvBysrAwb3vy`. No further deployment is needed for this excluded documentation-only record.

## NOTES and public map verified live · 30 October 2026

All feasible team-note changes and the public Google/Earth Engine map are published on the existing field-guide site. PR127 carries the mission homepage, action-first topic menus and Google heritage pin form; PR129 fixes phone map/header stacking and expanded-map layering. The later guarded PR130 release includes both: runtime commit `7ede7b29255933a468149635972a76c0645bf195`, tree `a78f0b813cc3fc13579281b93f8d1720e5612657`, deployment `dpl_E4dHjcZFCzeiR1wwbvBysrAwb3vy`. Vercel metadata and final public desktop/phone acceptance independently confirm this; no further frontend deployment is required. Earlier pending wording below is historical.

The exact Google website restriction was added after direct user approval, retaining existing origins and two API restrictions. Coordinated Railway API `fa0b1552-b5e6-46b2-80e4-8d5ebec46020` and gateway `7b9a57c4-3567-4a24-a2a2-635d47db9f42` are verified with preserved databases/configuration and revoked temporary SSH access. Actual imagery from 25 October, Google click-to-pin, 40 public route renders and phone/desktop map layering passed. All 279 Node tests, 144 Python tests and both builds passed. No satellite AI, report submission or story email was triggered. Local ports 4176 and 4197 remain running; original WordPress is unchanged. See [complete release evidence, rollback and remaining team dependencies](../reports/notes-release-2026-10-30/README.md). This record is documentation only and excluded from deployment uploads.

## Taller AI composer live · 30 October 2026

User-requested ChatGPT-style entry box is live at https://actforgoa-field-guide.vercel.app/AI. PR #130 merged as `7ede7b29255933a468149635972a76c0645bf195`, preserving the map owner's intervening page-stacking fix `87207f0`. Runtime tree is `a78f0b813cc3fc13579281b93f8d1720e5612657`; Vercel deployment is `dpl_E4dHjcZFCzeiR1wwbvBysrAwb3vy`. The installed Arc Textarea replaces only the AI hero's single-line field. It has a 174px chat surface, bottom-right send button, Enter to send and Shift+Enter for a newline. Existing destinations and standard search are preserved.

The unchanged guarded release passed all 279 Node tests, build, freshness checks and all staged service probes before promotion. Desktop/390px/320px local browser checks and native public desktop/phone checks confirm the height, multiline editing and exactly one submitted question. Public chat handoff returns the real reviewed cached answer, zero model calls. Rendered desktop/phone captures were inspected. Protected evidence is under ignored `.reports/ai-home/` (`composer-evidence.json`, `composer-release.log`, `composer-live-results.json`, `composer-live-1440.png`, `composer-live-390.png`). Previous frontend `dpl_59Hcgb6KL2cpydMBJksKg6sv8jUL` is the rollback baseline. No backend, corpus, credential or accounting configuration changed. This documentation-only follow-up is excluded from deployment uploads.

## AI homepage live · 30 October 2026

The user explicitly said “ship it” after narrowing the fork request to one `/AI` homepage on the existing site. [PR #126](https://github.com/actforgoa2026/ActForGoa-website/pull/126) merged as `9b8d53e2d13dd4a77d2c508eb9063ff71b400ccf`, preserving main `5029172` (mission homepage, updated action menus, heritage and public Earth Engine map). The spiral hero sends questions to the existing `/ask` conversation; topic buttons use all 14 current topic/submenu destinations. Six resource cards open existing tools. Reviewed cached starter questions avoid new model calls; custom questions and follow-ups use the existing agent. No separate project, answer route, backend, corpus or accounting change.

Live: https://actforgoa-field-guide.vercel.app/AI. Vercel `dpl_59Hcgb6KL2cpydMBJksKg6sv8jUL`, source tree `9ba41d28d9d2b51a7b30eec2ee1992dc8b90a569`. The unchanged `release:review` guard passed 279 Node tests, build, fresh source/alias checks and staged research, editorial, reporting, map, newsletter and MCP probes. A project-scoped REST command transport accommodates the cloud credential without the general CLI’s unavailable user-profile lookup. It preserves the release guard’s checks, stages without assigning aliases, and promotes only the verified deployment. Transport and private evidence remain in ignored `.reports/ai-home/`.

Actual staged and public Chromium checks pass on desktop and phone: all 39 photos load; no overflow/page errors; original topic menus work; `/AI` initiates exactly one cached answer on `/ask`; cited documents and 34 retained/new route renders pass. Intercepted transport separately verifies follow-up history. No paid model request ran. Rendered desktop/phone screenshots were inspected; Impeccable is unavailable in this executor. The original WordPress domain is unchanged. The preceding NOTES deployment `dpl_dpggLDGjzCbYL1PauqpbTTS5iXCi` remains the frontend rollback. See [release record](../reports/ai-home-2026-10-30/README.md).

The preceding NOTES promotion had completed before this release. Its phone map/header follow-up remains with that owner; it was not included here. Any subsequent release must fetch current main and treat this deployment as the new alias baseline. This documentation-only follow-up is excluded from Vercel uploads and needs no further deployment.

## Combined NOTES release authorized · 30 October 2026

The user has now said “ok, ship it when ready” after requiring all NOTES changes in the integrated4197 preview and preserving4176. NOTES owns this combined main-site promotion and coordinates the existing satellite owner for the Railway gateway/API deployment. The isolated `codex/satellite-public-map` tree carries both scopes; primary dirty checkout remains untouched. Production target is the existing field-guide alias only. New public-map readiness gates extend `release:review` without weakening staff authentication checks. Exact source, browser evidence, service backups and hosted acceptance must be recorded before completion. See `reports/TEAM-NOTES-2026-10-30.md` and `docs/SATELLITE-PUBLIC-MAP.md`.

## Integrated public Earth Engine map and control grid · 30 October 2026

Local `codex/satellite-public-map`, based on 2c7e006, now uses the latest Google/Earth Engine SatelliteWorkspace on the main `/map` route, automatic browser visitor sessions and same-origin `/api/satellite/*`. The user rejected the retained OSM provider; that build-mode split is removed. Their latest correction removes the map-view selector entirely. Earth Engine is the sole view. The control grid uses shared edges, equal date columns, consistent 48px targets and coherent search/map-tool rows. The persistent grid rule is recorded in AGENTS.md and DESIGN.md.

The satellite-google owner's latest cache/UI work is reconciled; NOTES has added its requested homepage/menu/heritage changes into this isolated checkout. The user-authorized NOTES port handoff is complete: 4197 serves the integrated tree,4183 redirects, and4176 remains running. Existing browser-key website restrictions are restored to4176/4197/Railway. See `docs/SATELLITE-PUBLIC-MAP.md` for exact access boundaries, cache changes and release prerequisites.

Map validation before the NOTES merge: 266 Node and 144 Python tests, both builds, real anonymous 25 October Earth Engine acquisition, 320/390/768/1440px browser geometry, calendars and expanded-map exit. No AI call ran. NOTES owns the combined full-suite rerun and the user-authorized release; this map chat has not committed, pushed or deployed. Hosted publication must configure the main public browser key/exact field-guide origin and deploy the public satellite gateway and main functions together, preserving data/budgets/credentials. No concurrent promotion and no change to original WordPress domain.

## Research speed release — 30 October 2026

The user authorized cached starter answers, timing measurements and batched retrieval, followed by a live release. The focused local release owner holds issue #89; other local agents remain paused. Branch `codex/research-speed-release` starts at fresh main `2c7e006` and integrates reviewed flood-guidance PR124 (`bb9d311`). Existing live SAPCC generation `20261030-sapcc-native-v2` and every original corpus/accounting record are preserved.

Implemented: three allowlisted, manually reviewed public starter answers with exact citations and runtime/corpus/CRM invalidation; new questions and follow-ups stay live. A bounded batch tool searches and reads originals together, and the frontend avoids its redundant pre-answer search. Metadata-only timing separates provider, tool and total elapsed time. Official preparedness remains separate from SAPCC proposals. October's $50 / 500-attempt daily allowance and dated reversion are unchanged. The durable production ledger has a pre-release backup.

Next: run integrated automated and rendered acceptance, publish clean source and the backend package, review and preload bounded hosted starter investigations, verify a live follow-up and official guidance, then promote through `release:review`. Keep backend deployment `986679ef-46fd-4a65-9086-01085913e051` and frontend `dpl_ENfoDDJTZrG7wAmJQvsC2Qo8AR4f` available for rollback. No original-domain or satellite deployment is part of this release.

## Official flood preparedness addition ready for integration · 30 October 2026

The user requested official resident flood guidance alongside SAPCC proposals. Isolated branch `codex/sapcc-flood-preparedness` starts from main `2c7e006` and adds a read-only SDK tool for reviewed Goa DFES/NIDM summaries, strict source-category separation, direct official citations, checked-date labels and a live-alert link. No corpus generation, budget, credential or accounting change. The original domain and satellite remain outside scope.

Validation: 256 frontend tests, 225 backend tests, build, four-width UI with explicitly mocked model transport and real source links; original NIDM flood page rendered and reviewed. No paid request or deployment ran in this feature branch. ORCHESTRATOR holds the active cache/timing/batched-retrieval release in issue #89 and requested this reviewed PR for combined integration. Preserve both sets of changes; include the guidance version in example-cache invalidation. See [source review and verification](../reports/sapcc/FLOOD-PREPAREDNESS.md).


## SAPCC research assistant live · 30 October 2026

The resident SAPCC question flow is live, with entry points on the plan overview/topics and general research assistant. PRs #119, #121 and #122 are merged; runtime `977c55a4ebbef9d1a609c24ca6c260fdff213ef5` is deployed as research service `986679ef-46fd-4a65-9086-01085913e051` and guarded frontend `dpl_ENfoDDJTZrG7wAmJQvsC2Qo8AR4f`. Active generation is `20261030-sapcc-native-v2`. The completed SDK workflow, current map/Explore source and unrelated corpus documents are preserved. The primary dirty checkout was untouched.

Verified: 255 frontend tests, 221 backend tests, build, 20 retained routes with PDF export on desktop/phone, four-width SAPCC journeys, three accepted hosted topic questions and 14 exact passage links. Full native spreads and original adjacent table context stay with citations; unread discovery snippets and incomplete scanned minutes cannot support answers. All failed attempts remain charged. Final UTC October 29 total is 69; October conservative reservation is $32.664589 of $50. Previous imports/receipts and source SQL are unchanged. A derived ANN timestamp/cache-byte difference is documented explicitly; no blanket byte-identity claim is made for that file. Temporary SSH access is revoked. See [source, acceptance, accounting and rollback record](../reports/sapcc/RESEARCH.md). This SAPCC release is complete; no further alias promotion remains active.

## Claude Agent SDK production release complete — 30 October 2026

The user's focused production authorization is fulfilled. PR #118 merged as `ee90772a90a6158fa2f9608c9bcd885c7ede3c1f`, preserving newer map/design/SAPCC/Explore work. `release:review` passed all 254 Node tests, the production build and staged probes, then promoted `dpl_47zN5Y9MpUzWmeMkY8FyJzWhhX2g` to the existing field-guide alias. Research backend `274f19ca-335a-4b39-8988-49ae195b6fac` runs clean package `048181c4fb2eb7539871c664743df53c22e60fa7`. Public `/api/chat` invokes Claude Agent SDK with full-page corpus tools, public CRM, citations, clarifications and contextual follow-ups. Hosted API and actual desktop/390px browser acceptance passed.

The complete 1,174-document / 21,534-page corpus and original hashes are intact. Existing production accounting and every prior receipt are preserved; the six bounded release conversations added 26 model attempts, including the failed semantic checkpoint. Final October conservative reservations are $23.676383 of $50; UTC Oct29 total is 39 of 500. Dated expiry and November's 100/day and $5/month defaults are unchanged. No development ledger was used or reset. CURRENT remains `20261027T065155-law-5bc5619b`; the staged SAPCC generation is preserved for its owner's separate activation. Runtime identities, acceptance, limitations and rollback are in the [release report](../reports/research-agent-production-2026-10-30/README.md). ORCHESTRATOR's promotion is complete; issue #89 records release ownership handoff.


## Satellite workspace reconciliation and hosted acceptance — 30 October 2026

[PR #116](https://github.com/actforgoa2026/ActForGoa-website/pull/116) preserves concurrent PR #115 exactly in the integrated guide's `Satellite.tsx`, `SatelliteHistory.tsx` and `satellite-layout.css`. The standalone entry now owns `SatelliteWorkspace.tsx`, `SatelliteWorkspaceHistory.tsx` and `satellite-workspace.css`. Its accepted inline Arc picker coexists with the guide's new portalled picker; shared Calendar retains the valid-date Today fix. No integrated website deployment is performed by this release.

Reconciled checks pass: 254 Node tests, both production builds and desktop/390px browser captures. Satellite API source remains hash-identical to the 142-test verified package. Impeccable's bounded preservation review is `ship`; documentation records both source boundaries.

API deployment `2454a251-1b10-4deb-82c3-b3113243ba03` is healthy. First app deployment `aa08c8be-bf52-44b0-ae56-94727ca8bf60` passed hosted real Earth Engine tile/cache, rectangle-to-acquisition, actual Arc calendar and saved completed AI synopsis checks. Final app deployment `1beec385-cb3a-4a58-be91-374d234ebd3e` from `3a7326a` carries the reconciled source boundary and passes all 17 runtime/static file hashes; API `1642dea` passes all 19 runtime file hashes. Original staff, eight existing jobs, four cached observations and raster bytes are unchanged. Verification used two preview generations, two catalog reservations and one observation; no new AI call. Temporary verification account and sessions are revoked. See the release report for final runtime identities and source hashes.

## Satellite workspace release authorized — 30 October 2026

The user said “ship it” for the locally verified Earth Engine workspace. This supersedes the local-only release boundary below. Isolated branch `codex/satellite-earth-engine-workspace` carries implementation `71722ca` and reconciles fresh main `4d0f497`, preserving its Arc MorphSelect/Slider controls, Google-only standalone map, Leaflet main-site map, SAPCC and unrelated features. Scope is the existing Railway satellite API and satellite app only. The main Vercel alias and original domain are outside this release.

Current release checks: 251 Node tests, 142 satellite Python tests, both production builds, desktop/390px local UI, actual Arc calendar and saved real AI synopsis. Private backups of both hosted databases precede deployment. Existing users, jobs, rasters, provider credentials and quota history must remain intact. The ongoing local workspace stays available at `http://127.0.0.1:4176/map`; its approved browser-key referrer remains enabled. Hosted deployment identities and acceptance will be recorded in `reports/satellite-workspace-2026-10-30/README.md` after successful release.

## Local satellite interaction follow-up — 29 October 2026

User superseded deployment iteration with local-only work and explicitly approved restoring the browser key's `http://127.0.0.1:4176` referrer. At that checkpoint, uncommitted work in `/Users/zakkrevitt/.codex/worktrees/satellite-google/ActForGoa` on `codex/satellite-google`: isolated hot-reload launcher, real Earth Engine navigation preview, automatic exact-acquisition load after drawing, real Arc date pickers and a two-column map/analysis workspace with explicit AI synopsis status. Saved hosted release above remains unchanged. Local actual comparison on the user's footprint, 10/20 October, completed OpenAI Decisions `gpt-6-luna` with 100% common clear coverage; the earlier cloudy pair correctly skipped AI. Checks: 142 satellite Python tests, 226 Node tests, production build, desktop/phone/browser workflow and local auth boundary. See [local workflow and verification](SATELLITE-LOCAL.md). No push, merge, deployment or hosted data mutation in this follow-up. Local work remains reviewable and uncommitted; next iteration stays local unless the user authorizes release.

## Map and landscape release authorized — 30 October 2026

The user's latest explicit “SHIP IT” authorizes publishing this follow-up to the existing field-guide alias and satellite frontend. This supersedes the local-only instruction below for this release. The original WordPress domain, hosted Python API, corpus, credentials, quotas and persistent data are unchanged. Reconcile the newer Goa SAPCC work from origin/main before the exact-tree browser checks. Use the existing release guard and an allowlisted satellite frontend package. Record final deployment identities and live checks under ignored `.reports/map-workspace-release-2026-10-30/`.

## Local follow-up — 30 October 2026

The user has explicitly returned this chat to local-only work after the earlier design release. No further commit, push, merge or production deployment is authorized. Active source remains `/Users/zakkrevitt/.codex/worktrees/actforgoa-design-iteration`.

Implemented locally: larger submenu labels, reuse of the approved stippled landscape, and a two-column satellite workspace with actual Arc calendar pickers. The running local satellite API is configured for Google Earth Engine. A bounded fresh catalogue/image check succeeded through the authenticated local app route; optional image classification remains unconfigured locally. `npm run dev:check -- --satellite-only` now verifies local readiness without depending on the hosted corpus AI service. Main and standalone builds, 11 targeted Node tests, desktop/phone renders, and a real Earth Engine numeric comparison pass. See [local follow-up](design/local-followup-2026-10-30.md).

## Goa SAPCC live and verified · 30 October 2026

The user explicitly said “ship it” for the downloaded Goa SAPCC and resident navigator. The focused release uses isolated branch `codex/goa-sapcc-release` from fresh main `60844a3`, preserving the shared dirty checkout and the newer Arc/Figtree release. The target is the existing field-guide review alias; the original WordPress domain is outside this change. The preceding design promotion has completed and its shared release lock has cleared.

Shipped scope: original government PDF and provenance in docs, 13 resident topics and 26 selected measures, chapter/source navigation, exact spread references, library/catalogue and homepage routing. Hosted research corpus, backend services, accounts, provider configuration and accounting are unchanged. Validation: 248 Node tests, production build, SAPCC browser journeys and required retained routes on desktop/phone, including local PDF export. Impeccable release-integration verdict is `ship`; source research limitations remain explicit. See [release evidence](../reports/sapcc/RELEASE.md).

[PR #113](https://github.com/actforgoa2026/ActForGoa-website/pull/113) merged as `a08277b5f5ccaa5cf32e75eebfdf6731ac31c7c2`, tree `db7aaaca64f84db00664e77649b4f778caa766ad`. The guarded `release:review` workflow promoted deployment `dpl_BHVXg7q6p7YtbqgKkN3h84MbgNN6`; [the resident navigator is live](https://actforgoa-field-guide.vercel.app/climate-plan). Public SAPCC journeys and all 20 retained routes passed at desktop and phone sizes, with no browser errors; rendered source, overview, topic and retained-route captures were inspected. Read-only service readiness, nested admin authorization, newsletter media and MCP gates passed. Zero paid AI requests ran. Exact evidence is saved under `.reports/sapcc-release/`. This documentation follow-up records the deployed runtime; it requires no further deployment because both changed paths are excluded from Vercel uploads.

## Design release authorized — 30 October 2026

The user explicitly requested pushing all updates to production. This chat owns the focused release of the reviewed design/function iteration, targeting the existing field-guide Vercel alias and existing satellite frontend. The previous issue89 checkpoint says release ownership is clear; no earlier promotion remains active. The original WordPress site at actforgoa.org remains a separate migration decision.

Fresh origin/main is 1b16b87. The satellite Google release is already live from committed branch source ddbea28, so it must be reconciled before packaging the new frontend. Preserve the newer Google map/Places integration, image dates and attribution, existing hosted API, credentials, volumes, accounts and provider accounting. The dirty satellite-google working tree belongs to another ongoing task and is excluded. No model, corpus, quota or credential changes are part of this release.

Committed live source has been reconciled. The standalone build explicitly retains Google Maps/Places; the integrated main/local build retains its working Leaflet/Photon map without expanding the standalone browser key’s origin permissions. Newsletter media now lives under /assets/newsletters to avoid the SPA rewrite, and the release gate probes the PDF and image content types plus the new authenticated satellite environment route. Next: check the exact combined tree on desktop and phone, merge the reviewed source and deploy through release:review. Final deployment identities and public verification will be recorded under reports/design-release-2026-10-30/.

## Local design and function iteration — 29 October 2026

Active checkout: `/Users/zakkrevitt/.codex/worktrees/actforgoa-design-iteration`, branch `codex/design-iteration`, based on main `1b16b87`. The primary dirty checkout remains preserved. All changes stay local and uncommitted. No push, merge or deployment is authorized for this iteration.

`npm run dev:full` serves the full local environment at `http://127.0.0.1:4173`. Research uses the existing hosted corpus; reporting, editorial/admin and satellite API services run locally. See [local development](LOCAL-DEVELOPMENT.md) for startup and health checks and [the completed notes](design/local-iteration-2026-10-29.md) for the design/function scope and verification boundaries.

Current verification: all 238 Node tests pass; production build passes with an existing large-chunk warning. TypeScript and diff checks pass. Rendered desktop and phone checks cover the changed public surfaces. Source scans found no italic/oblique declarations or decorative side stripes in changed UI files. The final Impeccable review and updated design documentation accompany the local package. Earlier detector output is advisory evidence from the initial scope, not a final quality verdict.

## Satellite Google integration — 29 October 2026 (local)

User explicitly requested connecting Earth Engine and Google Maps APIs to the existing hosted standalone satellite app and testing them there. Isolated branch `codex/satellite-google` starts at fresh main `1b16b87`; the active hosted Python source hash-matches that base. Existing deployments before this change: API `8e598615-7b63-497b-8cd8-608486e98a85`, app `393c446c-2fa6-4b8b-b1e9-0a35bb5c9a77`. Both private databases were backed up before configuration. Main/research aliases and paused chats are outside this work.

Implemented and live from runtime commit `df57d1b`: explicit Earth Engine retrieval, preserved spectral/cloud/actor-cache checks, on-demand current Google weather/air quality and a directions link. API deployment `906213da-e9c4-4524-9659-4e91d0e7cc46` and app deployment `a231af84-a064-4baa-af37-c3611c98b009` succeeded. Hosted acceptance retrieved and compared exact 8/13 January Sentinel-2 images with 94.11% common usable coverage, reused the cache, reopened saved results on desktop/390px browser and verified five Google web services. All copied runtime/static files match package hashes. Original four jobs, two rasters and staff account are unchanged. Temporary verification access was revoked. The user subsequently chose Google street map/search, approved its separate two-API website-restricted browser key, and then supplied an existing OpenAI key and explicitly resumed Decisions activation. API deployment `124d02d2-e583-47a0-82bc-fc5e9796b2fa` retains runtime `df57d1b` and passed a real seven-question Decisions comparison using `gpt-6-luna` with 94.11% common usable coverage. Google street maps and Places search are live from frontend runtime `b28902ddcb9111f0694c1d895eb206484b1451c4`, app deployment `eeccb3e7-4938-49af-9d56-7ced40baf378`. All 20 copied app files hash-match the manifest. Hosted Panaji search, saved Earth Engine overlay, timeline/opacity and 390px phone checks passed. The browser key now permits only the hosted origin and two APIs; the temporary account, sessions and SSH key are revoked. Original staff data remains unchanged. The concurrent user-approved larger map/Figtree styling from “Start local design environment” is preserved. Automated validation: 140 Python satellite tests, 223 Node tests, main and standalone builds, and final-patch typecheck. [Configuration](SATELLITE-GOOGLE.md), [hosted acceptance and limits](../reports/satellite-google-2026-10-29/README.md).

## Satellite query audit — 29 October 2026 (cloud)

Active isolated checkout `/workspace/actforgoa-satellite`, branch `codex/satellite-query-audit`, starts from fresh main `f20fc25`. PR95 is already merged; this audit uses [PR109](https://github.com/actforgoa2026/ActForGoa-website/pull/109). Concurrent map-controls main `05720cb` is reconciled, preserving PR108 and its place/search/drawing improvements. User requested a deep audit and fixes for selected-area/time questions, Amche/CDSE history and OpenAI image decisions. [Full findings and remaining acceptance](SATELLITE-QUERY-AUDIT.md); [checks and package evidence](../reports/satellite-query-audit-2026-10-29/README.md).

Implemented: actor-private spatial/time evidence retrieval, area-filtered history, pinned Amche intersections and cited ecology background, explicit map/workflow/readiness states, resumable existing jobs and improved scoped Decisions uncertainty. Initial main review `/map` was an older frontend/API deployment; the latest public check finds the new map frontend but nested satellite API still404, addressed in source by explicit Vercel handlers; current standalone has working real CDSE but no configured OpenAI. These audit changes are source-only until both existing standalone packages are deployed. Combined alias/research ownership is unchanged. No new paid calls, credentials or deployments in this audit. Browser tools unavailable, so fresh desktop/phone acceptance remains outstanding; cloud Railway binding still covers `.app` rather than required `.com`. Reconciled runtime checkpoint `97cde8be5cd79e1a2e1e620a216a3f9f7c133048`: 136 satellite Python tests, 221 Node tests, production build, both clean packagers and isolated API/app container checks pass. PR109 remains unmerged/source-only. Next: review/accept rendered desktop and phone behavior, then deploy both existing standalone services and explicit Vercel routes through the release owner. Exact package manifests and limitations are in the linked report.

## Satellite live imagery acceptance complete — 29 October 2026, 11:12 UTC

The user supplied new CDSE credentials through protected local storage and explicitly authorized configuration. OAuth validation succeeded; both values were sent to the existing Railway satellite API via stdin without logging secrets. API deployment `9014df8b-69de-4178-8072-135f96239875` reuses the accepted `11582ac` image, with all 14 satellite runtime files hash-matching. The app remains `b0fadee`, deployment `4bd7fc4b-8d60-487b-8219-bc978d07324f`. Both services are successful at https://satellite-app-production.up.railway.app/map. This supersedes the earlier missing-CDSE blocker below.

Fresh hosted acceptance passed: a new small Ribandar/Chimbel footprint returned ten acquisitions; explicit October 20 and 25 loads produced real georeferenced imagery. Desktop 1440×1000 and phone-sized browser 390×844 checks covered dated overlays, keyboard/button timeline switching, fresh named-account sign-in, saved comparison search/reopening and server-side cache reuse. The comparison correctly remains inconclusive because only 41.1% of this area is usable in both images. This is functional verification, not Goa field validation; optional AI interpretation/classification remains unconfigured and was not called.

Total new service reservations: five catalog searches, two image retrievals and one comparison. Both cached rasters remained byte-identical through comparison and phone reload; no third Process retrieval or duplicate observation job occurred. No AI request ran. The hosted runtime does not retain provider processing-unit headers, so no exact PU or currency charge is asserted. Original account access, saved recorded comparison, volumes and service tokens remain intact; a fresh SQLite backup precedes configuration. Temporary SSH verification access was revoked. Research accounting, the review Vercel alias and actforgoa.org were unchanged. Other agents and heartbeat remain paused. See `reports/satellite-cdse-2026-10-29/README.md` and the ignored `.reports/satellite-cdse-20261029/` evidence.

## Local SDK working after explicit renewal — 30 October 2026 IST

The user explicitly renewed the dev allowance with up to $2 more, preserving all accounting and prohibiting deployment. Local commit `2cf9738` appends one checksum-bound grant to the existing dev ledger: $4 lifetime cap, no calendar reset, and the original expired receipt and sealed cloud baseline unchanged. A pre-renewal backup remains private. Duplicate renewal is rejected.

The renewed browser test now completes end to end through the actual Claude Agent SDK and Anthropic. An initial citation-validation failure remains counted. The corrected run resolves model-selected IDs to complete original source text, as the existing production normalizer does, and only permits document/CRM evidence actually read in that conversation. Search snippets alone cannot become citations; source exclusions remain enforced. The successful run displays a cited takeaway, deeper detail, Agonda CRM provenance/caveats, a clarifying question and related follow-ups. Exact PDF-page and CRM references opened in separate tabs, and the location authority lookup works.

Accounting after both renewed runs: 19 attempts, $3.253040 reserved, $0.746960 remaining under the $4 cap. The additional eight provider attempts reserved $1.529455; all four cloud receipts and seven earlier SDK reservations remain identical. SDK-reported costs are estimates, not replacements for reserved accounting. Seventeen focused Python tests and TypeScript checking pass. The 1,174-document / 21,534-page corpus and 499 + 2,768 public CRM records remain unchanged. See [current local workspace handoff](../dev/LOCAL-WORKSPACE.md). UI: <http://127.0.0.1:4276/ask>. No deployment, production-accounting change, paused-agent activation or full release checklist.

## Local SDK accounting handoff — 30 October 2026 IST

Under the user's explicit local-development instruction, the isolated `codex/research-agent-local` checkout contains the full immutable 1,174-document / 21,534-page corpus and public CRM snapshot (499 community + 2,768 government records). Local runtime `55121d0`, handoff `734b31f`, and SDK/accounting follow-up `bf00575` are local commits only. The live-reloading UI remains at <http://127.0.0.1:4276/ask>. Shared unfinished work and production are untouched.

The cloud chat “AI” exported its complete existing dev ledger after confirming its writer was stopped. Four prior attempts/$0.441196 were imported with all receipts and checksums preserved. One local end-to-end SDK request failed to return a verified answer (HTTP 502); seven new conservative reservations total $1.282389. The continuing dev ledger now has 11 attempts/$1.723585 reserved, leaving $0.276415 under the original $2 cap. No reservations were reset or refunded. The original expiry, 2026-10-29T18:54:01.867828+00:00, is preserved and has passed, so paid answers are paused.

The follow-up fixes missing SDK gateway headers and preserves visible accounting after expiry, with private diagnostics for future failures. Fifteen focused Python tests, TypeScript checking, a real SDK subprocess against a synthetic localhost provider exercising all six tools, and local HTTP checks pass. No successful live model answer is claimed after the fix, and no further paid retry was made. See [local workspace evidence and continuation limits](../dev/LOCAL-WORKSPACE.md). No deployment, production-accounting changes, paused-agent activation or full release checklist occurred.

## Private live development workspace — 29 October 2026

The user rejected the public snapshot and explicitly authorized a real private development workspace, then separately approved up to $2 additional dev AI spend. This supersedes the public-preview iteration approach. `backend/dev_app.py`, `dev/workbench.html`, `dev/private-gateway.mjs`, `dev/relay_worker.py` and the combined launcher provide a private session-based frontend/backend workflow. See `dev/PRIVATE-WORKSPACE.md` for restart, limits, paths and actual evidence.

Actual Vite source is served over an authenticated running-sandbox relay; backend code reloads, and browser-edited prompt/retrieval settings apply to the next request. Source retrieval uses the hosted index read-only, while generation and validation execute locally with the managed Anthropic binding. No provider credential is copied to the sandbox/browser. Source-index rebuilds and corpus-wide contextual embedding work remain separate and pending. The public preview alias's anonymous access override was revoked; production alias/runtime/accounting are unchanged.

One paid dev request, explicitly within the separate $2 allowance, answered the bar example with four cited paragraphs/four sources; retrieval 1200ms, provider 12880ms, total14080ms. The dev ledger preserves that reservation. Unauthenticated private settings access returned401; authenticated live settings changed and restored without build/deployment, and authenticated HTML served actual Vite development modules. This is a bounded smoke check, not repeated release testing or semantic acceptance. The workspace is session-based (about five hours from sandbox creation), not permanent hosting. Secrets/invitations, configuration and accounting stay outside Git under `/workspace/.research-private/`.


## Research clarity and early feedback — 29 October 2026

Branch `fix/research-clarity-latency`, based on `origin/main` at `1c4ac7c`, prepares the user's requested short top-level takeaway with deeper information below. The answer brief makes the first existing cited paragraph the takeaway; the API marks the new presentation with `summary_first` so older API responses retain their layout. All existing citation, qualification, word-limit and outside-context checks remain in place. No extra model call, provider/model change or budget change.

The frontend immediately appends the submitted question and pending status, starts source preview and chat concurrently (chat already retrieves its own evidence), and displays source matches before generation finishes. A failed source preview does not discard a successful answer. Existing conversation history excludes unfinished turns. Cancellation and AI failure remain explicit. This removes the sequential preview wait; it is not streaming and does not establish a measured improvement in provider latency.

Validation: 209 Node tests, production build, 180 research tests plus the added citation-preservation test passed. Delayed fixture browser checks at 1440/390 verify immediate feedback, concurrent request dispatch, sources before answer and cited takeaway/detail. Existing fixture journeys at 1440/390/320 passed, including citations, follow-ups, unavailable answers and failure states. Screenshots: ignored `.reports/clarity/`. No paid calls or live semantic acceptance performed. The referenced installed Impeccable skill was not found in this executor; manual rendered inspection completed. Implementation is local/PR-ready only, not merged or deployed. The release coordinator must review the prompt change and perform required live acceptance before coordinated backend/frontend deployment; no alias was promoted.


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

### Rapid iteration steering — 29 October 2026

The user requests development iteration without a full build/check cycle per prompt. `scripts/serve_research.py --live-api` now launches Vite plus a localhost-only bridge to the existing answer API; the API status smoke check passes. Source changes update the frontend without builds. Full-corpus mode adds Uvicorn backend reload and checks for the index before startup. The live-API mode keeps production accounting and backend prompts; it does not activate local prompt changes. This executor lacks the full corpus and Railway management returned an HTTP403 edge block, so a fully isolated prompt/retrieval runtime and externally reachable dev hostname are not yet established. Do not describe this localhost frontend as a hosted backend sandbox. No production deployment, budget reset or provider test occurred. Existing initial changes are PR106/commit6918761.

Both supplied Anthropic articles were read: contextual retrieval and building effective agents. Pending application: benchmark chunk-specific retrieval context in both lexical/vector indexes, compare bounded reranking with current hybrid retrieval and measure stage latency/recall. Prefer preprocessing and a simple single-answer workflow over extra serial model calls. Keep generated retrieval context separate from original citable passage text. These retrieval changes remain pending, not implemented or measured.

### Location-aware government referral prototype

The user requests a location question after a structure/building answer, then a CRM-backed government referral. The development frontend now asks for the village/town and looks up named government-office local bodies directly in the existing public CRM. It links both the CRM record and its listed government URL, retains contact verification labels, and asks the office to confirm parcel-level jurisdiction. It excludes named officials, historical/unresolved entries, and broad district tags. A targeted actual-data check finds Panaji's city corporation and Agonda's Village Panchayat; North Goa and missing Calangute produce no invented match. No full tests repeated during this rapid iteration. The answer brief also prohibits assuming Panchayat jurisdiction, pending backend deployment.

A separate preview deployment was created through the existing Vercel project after project creation was denied. The new dev alias `actforgoa-research-dev.vercel.app` has an alias-only access override; production alias, source and project-wide protection remain unchanged. The preview uses the existing answer API/accounting and packages the location-aware frontend. This is a hosted snapshot, not a remotely connected hot-reload backend. The local Vite process remains available inside the executor; the device cannot access its localhost. Continue isolated runtime/index setup before claiming live prompt/retrieval editing.

### Commercial-premises intent and follow-up buttons — 29 October 2026

The user supplied the failed “i want to build a bar, how can I?” answer and requested related follow-up buttons plus better corpus understanding. The frontend now offers new structure / existing building / operating licence branches for commercial premises, and retains user history even after an insufficient-evidence answer. Venue construction/opening intent triggers the location lookup; sandbar, pressure, steel bar and legal Bar meanings are excluded from the premises rules. No extra model call is used for button generation or intent recognition.

Backend `retrieval_intent.py` adds bounded building/planning/change-of-use search vocabulary at the common library search entry; this affects retrieval only, not original question or citable source text. The answer brief allows general rules to establish partial coverage without matching a venue word and forbids claiming that missing retrieved excerpts establish absence from the entire corpus. These backend changes are pending release.

The development-only `dev/research-proxy.mjs` applies an explicit premises-question reformulation to the existing live API so this behavior can be tried without changing its runtime. The original wording stays visible in the frontend; the dev API receives the reformulated question. Its source-preview request expands the same premises concepts. Production prompts, index, quota and ledger are unchanged. This adapter is a bounded intent-based prototype, not contextual embeddings or a complete semantic upgrade.

Targeted live source-search comparison: the original bar query returned an activity report, compressed-air pressure/bar construction rules and unrelated material. The expanded query returned building/development forms, land-use/change-of-use provisions and technical-clearance sources. This establishes improved retrieval relevance for this example only, not answer accuracy or broad recall gains. Local intent checks include bar/cafe versus sandbar/pressure/legal Bar. No full test suite was repeated and no paid answer was dispatched by the agent.

## Full corpus and CRM access requested — 29 October 2026

The user explicitly requested the complete research corpus for a Claude Agent SDK workflow, followed by the full community CRM. The complete published CRM snapshot was fetched from the live public data endpoint and materialized outside Git: version `directory-2026-10-23`, 499 community/2768 government/3267 total, SHA256 `838df16f19bf43bd3b9929b70e5e2a7ab6242254c707dc6c4aa3af45b2e5013e`. `backend/crm_store.py` provides read-only full-collection browsing, FTS5 search, pagination and record reads; private workbench controls and API endpoints are live through code reload. Targeted counts, record access and waste/wildlife searches passed; no paid model calls or full release suite were run.

Research corpus restoration remains blocked, not complete. Both accessible GitHub repositories exclude original/extracted corpus/index content; their releases contain directory assets only. The live research API still reports1174documents/21534pages. Railway's documented management endpoint is `https://backboard.railway.com/graphql/v2`; the credential is currently bound only to `backboard.railway.app`, which returnsHTTP403. The correct .com endpoint responds but rejects authentication. An asynchronous user request is pending to update the credential destination (or identify another existing full backup). Do not route the managed secret through another service or claim API search samples are a full corpus restore.

`scripts/restore_agent_corpus.py` is prepared for a complete export: verifies original checksums and database integrity, copies the immutable generation and indexed originals, exports every document's full page text with page locators, and writes a full catalogue/readiness report without production accounting or credentials. It has not been executed on the missing corpus. Claude Agent SDK integration and corpus-wide search/read tools remain pending full-source access; the CRM tools are ready for integration. See `dev/PRIVATE-WORKSPACE.md`.

## Mac research-agent workspace — 29 October 2026

The user explicitly requested continuing this setup locally, superseding the earlier cloud-only implementation constraint for this work. The isolated checkout `/Users/zakkrevitt/.codex/worktrees/research-agent-local/ActForGoa`, branch `codex/research-agent-local`, starts from PR #106 commit `2f73438295f0e1186267626f59ad642a2ade7d9b`; shared unfinished work is preserved. No paused agent was resumed.

The complete current corpus was found in `research-accounting/ActForGoa/.reports/anthropic-acceptance-20261027/data`, not reconstructed from search samples. Actual manifest, SQLite and live status agree: generation `20261027T065155-law-5bc5619b`, 1,174 documents/originals, 21,534 pages, 79,564 passages. All original checksums and all 16 immutable index files were checked. A separate read-only copy, full text exports and catalogue are under `~/.local/share/actforgoa-research-dev/corpus/20261027T065155-law-5bc5619b`. The broader source corpus archive is also copied and hashed: 4,782 files under `original-archive`. Production accounting was neither copied nor reset. Complete public CRM: 499 community + 2,768 government = 3,267 records, unchanged snapshot SHA256 `838df16f19bf43bd3b9929b70e5e2a7ab6242254c707dc6c4aa3af45b2e5013e`; personal CRM notes remain separate.

Implemented: Claude Agent SDK with six restricted read-only/clarification tools, corpus-wide keyword search and complete page cursors, preserved provenance/warnings/exclusions, exact-quote citation validation, and a 50/50 research/catalogue+CRM UI. Localhost <http://127.0.0.1:4276/ask> runs Vite HMR plus backend reload. Prompt/Tune/retrieval edits apply locally without builds. Existing cited takeaways, deeper detail, related follow-ups, authority lookup and new-tab references are retained. The original vector index is preserved; the local workflow uses all-page FTS5 and does not claim hybrid-search parity.

Tested: 12 focused Python checks, 18 existing focused Node checks, TypeScript checking, and desktop/390/320 browser flows including PDF rendering, full text, authority lookup and live settings. Paid Claude SDK generation is not tested: the prior cloud dev reservation ledger and allowance are unavailable on this Mac, so remaining approved additional $2 is unknown and paid dispatch is blocked. No new AI spend, fabricated zero baseline, production ledger fallback or accounting reset. A checksum-bound, one-time final DEV-ledger importer and atomic per-attempt lifetime cap are prepared; obtain the existing cloud dev accounting before activation. See `dev/LOCAL-WORKSPACE.md` and `reports/local-agent-2026-10-29/verification.json` for exact paths, evidence and restart instructions. Implemented/tested locally only; not merged, pushed or deployed. No full release checklist repeated.

Runtime/source commit: `55121d0` (`codex/research-agent-local`). Independent Impeccable verdict scored both requested UI fixes resolved: short initial source disclosure with direct workspace navigation, and readable legal-status copy. Existing design sidecar drift is documented without changing the design system. The localhost launcher remains running on ports 4276/8093; next required action is to obtain and reconcile the final prior cloud DEV accounting before any paid SDK call.


## Research speed release — 30 October 2026

The release coordinator integrated reviewed starter-answer caching, bounded batched retrieval and metadata-only timing measurements with PR #124's official flood guidance. Backend source `333cb3bda02773ba301ba56a559102adb1bc574c` is running on existing Railway deployment `96bfcdbe-22e5-4ab9-9f16-3986ad1ac2f7`; all 28 packaged runtime files match. Three approved cached answers returned through the public API in 0.37–0.52 seconds without model calls or ledger changes. Fresh follow-up `9a89dbf1a4c449daa4f43c5bef10d2e6` used both batched retrieval and official guidance and passed original-passage, semantic and desktop/phone review after documented citation/prompt corrections.

The entire production corpus and all prior reservations/imports remain intact. Acceptance ends at 48 attempts today and $45.052337 in October conservative reservations, within unchanged 500/day and $50 October limits. No development accounting was used. See `reports/research-speed-2026-10-30/README.md` for checks, failed attempts, cache boundaries and rollback. Frontend promotion remains owned by this coordinator through `release:review`; issue #89 records final deployment identity and public verification.
