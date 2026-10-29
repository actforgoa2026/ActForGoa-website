# Goa SAPCC research assistant

The resident question flow is live at [Ask about Goa’s climate plan](https://actforgoa-field-guide.vercel.app/ask/ecology?document=d1b64d562f93c9cbabc39e1d-dc16e9345778&generation=20261030-sapcc-native-v2). The climate-plan overview, individual topics and general research assistant link to it. Topic links prepare a draft; they do not submit a model request automatically.

## Release identities

PRs #119, #121 and #122 are merged. Final runtime source is `977c55a4ebbef9d1a609c24ca6c260fdff213ef5`, tree `9267959833fe3ff7e14a31bb388868528fedd28e`. The prior SDK release and newer map, Explore and satellite source remain integrated.

- Research backend: `986679ef-46fd-4a65-9086-01085913e051`, with all 23 packaged backend files verified against the running service.
- Frontend: `dpl_ENfoDDJTZrG7wAmJQvsC2Qo8AR4f`, promoted through `release:review` to the existing field-guide alias.
- Immutable frontend: `https://actforgoa-field-guide-eh36is5sb-zakkrevitt-gmailcoms-projects.vercel.app`.
- Active generation: `20261030-sapcc-native-v2`; document `d1b64d562f93c9cbabc39e1d-dc16e9345778`.

The original domain and satellite deployments are outside this release. This record changes documentation only and requires no further deployment.

## Sources and behavior

The government PDF was already present in the hosted corpus. Its original SHA-256 remains `d1b64d562f93c9cbabc39e1d4be65f0515a06734792cfa5ea4eebf9544ff3cc6`: 9,222,768 bytes, 111 physical PDF pages. The public download matches that checksum, and the previous edition remains accessible at its original document ID and generation.

The native extractor separates printed spreads and rotated table cells. Every non-whitespace native character on all 111 pages passed a multiset preservation audit. This establishes character preservation, not universal semantic correctness. Original power and water table pages were also rendered and inspected. Scanned committee minutes on physical pages 99–110 remain available in the reader and PDF but cannot support generated answers. No OCR, reconstructed cross-page rows or corrected financial totals are claimed.

The Claude Agent SDK reads complete native SAPCC spreads and bounded adjacent original table pages within its existing 24,000-character tool limit. Original headers and surrounding table evidence stay attached to citations, including after subsequent reads. Document-scoped catalogue, search and read tools stay within the chosen edition; CRM tools remain available in general research. Discovery snippets omit citation IDs until a source read. The strict read-source validator remains enabled. The retained fallback also budgets complete passage/context groups independently within its original input bound.

Plan questions disable outside-library context, distinguish proposals from evidence of delivery, and offer rainwater, heat/health and solar starters. Citations open source readers in a separate tab. Conversations, edited follow-up drafts and clarifications are preserved while navigating; reloading clears the existing app-memory conversation store.

## Verification

All 255 frontend tests, 221 research tests and the production build pass. `release:review` repeated the frontend suite/build and checked staged API routing before promotion. Six scoped SDK searches, six fallback preparation checks, three general SAPCC searches and three retained research searches passed without model calls.

Browser checks cover SAPCC entry points, correct source/version payloads, no automatic submissions, source-only mode, citation navigation, draft preservation and clarification history at 320, 390, 768 and 1440 CSS pixels. Repeatable transport checks use mocked model responses and real source APIs. The current Figtree/Arc interface was inspected on desktop and phone, with no overflow, italic styling or decorative side stripes. Impeccable’s one detector pass found only existing advisory token findings. No Device Hub was used.

Hosted semantic acceptance:

- Solar: 14.86 seconds, four SDK model calls, original pages 12 and 41–43. The answer correctly identifies the barriers/gaps column and retains proposal/status caveats.
- Rainwater: 25.10 seconds, six SDK model calls. The answer links its INR25 crore/three-year salinity entry to page 50, distinguishes government measures from a household rule, and states its limited coverage.
- Heat/health delivery: a real question submitted through the public browser composer, four SDK model calls. It distinguishes proposed, planned and ongoing entries from completed work. Desktop/390px captures, the cited reader and preservation of an edited follow-up passed.

All 14 returned citation passages match the public passage API exactly. The full original download and old-edition reader pass. After promotion, all 20 retained routes passed on desktop and phone, including local template PDF export, with no browser errors. These are bounded acceptance cases, not a guarantee that every generated answer is semantically correct.

## Failed attempts and accounting

Two initial baseline calls used the original extraction: heat/health answered; rooftop solar exposed the fallback’s evidence-budget defect. During the SDK release, two responses failed manual review: a table gap was called a success indicator without the preceding header, and a budget was cited to the wrong page. A later water attempt was correctly rejected because it cited an unread discovery snippet. All failed responses and reservations remain retained; only changed source-context/discovery inputs were retried. Historical accepted research cases were not repeated.

The activation backup is `/data/research/.research-usage/backups/sapcc-20261029T203306Z`. All 20 prior usage imports and 42 pre-activation stage receipts remain identical, and historical daily counters are unchanged. This activation/release added 30 SDK model reservations, including 16 belonging to failed or rejected attempts. Together with the two earlier baseline requests, this task used 32 model reservations. Final UTC October29 total: 69 attempts; October conservative reservations: $32.664589 of the approved $50 cap; 72 stage receipts. These are conservative reservations, not invoiced spend. No development ledger was imported or reset; the dated limits and credentials are unchanged. Temporary SAPCC SSH access was revoked and its local key removed.

## Preservation and rollback

All 1,173 unrelated documents, 21,423 pages and 78,987 chunk/FTS rows match the pre-refresh canonical SQL hash `232e62f2b12f5ae3f2a7d24c51a76ac12a8499a90a356bb613aa001a96bb15db`. The complete active corpus has 1,174 documents, 21,534 pages and 79,548 chunks. Original source SQL and the other old-generation index files remain unchanged.

The derived old-generation ANN file `zvec/3/embedding.index.1.proxima` changed its hash at the first deployment handoff. Comparison with the matching retained local baseline finds only ten differing bytes in one 256KiB block: two stored timestamp values match the hosted file’s 2026-10-29 20:33:43 UTC modification time, plus a four-byte value. All other 601 blocks are identical. The audit therefore does not claim byte identity for that derived cache file. Source SQL, original PDF bytes, old citations and all unrelated source rows pass independently; no cache file was overwritten to conceal the difference.

Rollback frontend: `dpl_47zN5Y9MpUzWmeMkY8FyJzWhhX2g`. Pre-SAPCC SDK backend: `274f19ca-335a-4b39-8988-49ae195b6fac`; previous generation: `20261027T065155-law-5bc5619b`. Retain both generations and the production ledger during any rollback. Application rollback must never restore old usage counters. Runtime-only packages exclude source data, credentials and accounting.

Detailed transcripts, exact source checks, screenshots, package manifests, preservation hashes and failed attempts are retained under ignored `.reports/sapcc-research/`.
