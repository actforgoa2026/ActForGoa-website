# OpenRouter research chat validation

Date: 2026-10-26. Integrated base: main `4bda593`.

**Status: implemented, partially tested, not accepted or deployed.** The OpenRouter credential authenticated and generated real answers. Further paid testing is blocked by exhausted account credit. `/api/status.chat_ready` indicates a configured credential, not available credit or provider health. No further paid calls should run until credit is restored.

## Implementation

The current candidate is `openai/gpt-5.6-luna` through OpenRouter with low reasoning and strict structured output. Qwen 3.7, Qwen 3.8 and GPT-5 Nano comparisons exposed reliability or grounding problems; none is an approved fallback. Provider routing, price ceilings, bounded input/output and disabled automatic retries prevent silent model/provider changes. This model remains a candidate until acceptance passes.

Persistent SQLite reservations enforce defaults of $5 per UTC month and 100 new paid attempts per UTC day. Failed attempts count. Local evaluation increased the daily allowance while retaining the $5 monthly cap. The cap excludes infrastructure, taxes, credit-purchase fees and other account usage. First-question responses use a bounded ten-minute memory cache; follow-up conversations are not cached.

Answers carry paragraph-level passage citations and full-document links. Invalid structure, invented IDs, incomplete output and overlong brief answers are rejected. Legal/procedure evidence receives a notice covering unverified consolidated status, later amendments, court orders and current procedures. This does not certify legal currency.

Ask is the initial research mode; starters follow the selected mode. Existing Arc components, typography, palette and reader are retained. Provider disclosure identifies OpenRouter and its underlying provider. Companion main-search answer UI is in PR #12.

## Corpus and automated verification

Generation `20261026T131818-law-23a2e6a6` contains 1,174 documents, 21,534 pages and 79,564 indexed passages. The refreshed root and LAW data-only package have identical SQLite bytes, SHA-256 `c6d80208581f3776d2cfaa2cfe3ff08e026bd055be1c2a574461934fa52d870f`. LAW package `files.json` SHA-256: `9e03caf9af14bb5775fbf9154982dd562d80dc698ee0a13a9a0839ffcc9828f4`.

- **60 research tests pass** after the latest changes: real MiniLM/Zvec retrieval, documents/checksums, provider contracts, invalid output, prompt bounds, concurrent persistent budgets, cache isolation, service-only packaging and offline evidence-gate failure detection. Unit-test provider responses are simulated.
- **108 frontend tests and the production build passed** on the preceding implementation. Latest changes affect backend behavior, tests and documentation only. ORCHESTRATOR separately reported 113 frontend tests and a passing combined PR #12 build.
- Earlier desktop 1440 × 1000 and phone 390 × 844 browser checks covered Ask, source fallback, passage highlighting, rendered original PDF pages and preserved return state. No page overflow or italic/oblique UI text was found. Impeccable's source scan reported no findings; it is not a complete accessibility audit.
- These browser checks do not establish final-model acceptance. Real final-runtime answer/follow-up/citation/original checks at both sizes remain required.

## Live inference evidence

The evaluator checks answer structure, exact passage identity, citation page slices, full text and original-file checksums. These mechanical checks do not establish claim support. Raw reports and archives remain local, excluded from Git/static deployment. Failed outputs are retained.

| Run | Completed | Mechanical passes | Answered | Originals verified | Disposition |
| --- | ---: | ---: | ---: | ---: | --- |
| Qwen 3.7, 50 ecology cases | 50 | 47 | 32 | 40 | Rejected structures and unsupported claims; not accepted. |
| GPT-5 Nano, 55-case suite | 39 | 32 | 32 | 31 | Incomplete, brief-answer/citation/claim failures; not accepted. |
| Luna at `b4eb947`, 55-case suite | 36 | 34 | 34 | 41 | Parra brief rejected; credit failure stopped at biodiversity-05. Required claim corrections remain. |

Luna broad-run report SHA-256: `9ce7f42d0d270d19dd7e7a0f9b15bf9dfd476dd17824d9d01d5b8868120ac60d`. Targeted report SHA-256: `ecd6d3c0a157cf7d511c1c18bd427455a161bd1573fd891f75c51759c6b291de`.

LAW approved the targeted farming output's officer/deadline/citations, but identified RTI retrieval and TCP authority/approval problems. ORCHESTRATOR's climate/biodiversity review found a false chronology contradiction, unsupported transfer of plateau-wide reptile breeding evidence to seasonal pools, and claims supported only by page context outside the highlighted citation.

## Corrections and outstanding gates

Full page-opening prose is now excluded from model input. Short page headings remain geographic/section hints; facts must follow from the exact cited passage. Regression tests verify that uncited rainfall figures cannot enter through page context. This closes the exposure mechanism; live correctness remains unverified.

The prompt distinguishes prior evidence gaps from subsequent analysis, whole habitats from subhabitats, and animal groups. Brief answers target 50 words without character truncation and retain exact authority-to-approval mapping. These changes have not passed fresh live acceptance.

Required before release:

1. **RTI coverage:** retrieve the explicit non-BPL application fee in manual page 7, passage `e5d0e7777a79a19cf17cced54e173507`. Current retrieval may select the cover or SMS examples. Do not confuse an illustrative additional fee with the application fee.
2. **TCP mapping:** distinguish PDA development permission, TCP technical clearance and Municipal/Panchayat building licences. The latest observed output still conflated issuers; a prompt change alone is not acceptance.
3. **Exact-span/ecological review:** retest the climate, biodiversity, water and terrain holds from independent cached-output reviews. Climate-08 must preserve prior-gap/new-analysis chronology; biodiversity-03 must not transfer plateau-wide reptile breeding to pools. Terrain-05 must not turn a questionable national-coast climate/tsunami assertion into a Goa-specific conclusion, and other-state shoreline examples must retain their geography.
4. **Complete acceptance:** run remaining biodiversity/resource/abstention/follow-up/document-scope cases and rejected legal cases; finish substantive review of the final runtime's outputs. Cached water/terrain review is complete and found further citation-span issues; it is not acceptance of the new runtime. Uncompleted cases are not passes. Avoid unnecessary repetitions of unaffected checksum checks.
5. **Final UI/live checks:** verify real answers, follow-ups, citations, highlighted passages, originals and return state on desktop and phone, then repeat focused checks after coordinated deployment.

The [offline RTI diagnosis](rti-retrieval-diagnosis.md) establishes that the fee is already keyword candidate 14 but is displaced by cover/SMS passages. A local reranker experiment recovered it but lost reviewed farming and institutional-dog evidence, so production retrieval was left unchanged. The new offline gate passes 16/16 coarse smoke checks but fails all five RTI phrasings while retaining four other reviewed legal cases. These failures remain release blockers.

## Release handoff

PR #10 remains draft. ORCHESTRATOR owns the combined service/corpus/frontend deployment and PR #12 integration. The review site remains on main `4bda593`. The original actforgoa.org site and reporting service are outside this release.

Use the current code's service-only package with LAW's verified data-only package. Preserve old generations/originals, verify additions, and switch CURRENT last. Do not deploy LAW's stale service package. Credentials, raw archives and ledgers must stay out of Git and Vercel static files.

Preserve production usage and local evaluation reservations. The final local ledger has 182 attempts on 2026-10-26 and $0.634595 reserved for October, including its original $0.039154 baseline. Reservations are not provider charges. Reconcile shared baseline history, merge exactly once and retain backups; never overwrite production usage from a corpus package. Service-only packaging excludes the ledger.

Restored credit, corrected outputs and final verification are required before activation. This report records implementation and partial testing, not release approval.
