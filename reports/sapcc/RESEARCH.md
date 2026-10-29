# Goa SAPCC research integration · 30 October 2026

The user requested SAPCC questions with source links in the resident research assistant. The hosted library already contained the exact retained government PDF, but its two-page and sideways-table extraction contained excessive whitespace and interleaved text. A baseline rooftop-solar question returned no evidence. The source refresh and document-focused budget fix address that failure.

## Source and answer behavior

- Original SHA-256: `d1b64d562f93c9cbabc39e1d4be65f0515a06734792cfa5ea4eebf9544ff3cc6`, 111 physical PDF pages.
- New generation: `20261030-sapcc-native-v2`; document `d1b64d562f93c9cbabc39e1d-dc16e9345778`.
- The extractor reads each printed half independently, corrects native sideways orientation and retains table-cell positions. All 111 pages passed a non-whitespace character-multiset audit against the original native PDF text, with no missing or extra characters. This verifies preservation, not semantic completeness; rendered health and power pages were also inspected.
- Scanned committee minutes on physical pages 99–110 remain in the reader and original PDF but are excluded from answer evidence. No OCR or reconstructed cross-page rows are claimed.
- All 1,173 other documents, 21,423 pages and 78,987 chunks/FTS rows remain byte-equivalent in their SQL values. Both local and hosted staging checks preserve the original generation files; prior published citations remain available.
- The retained fallback budgets each complete passage plus its required context independently, preventing one overfull document group from discarding every passage. The current Claude Agent SDK reads full native pages, keeps document-scoped catalogue/search/read tools within the selected edition, blocks CRM citations in those conversations and rejects explicitly excluded scanned minutes. General research retains its catalogue and CRM tools; model, system prompt, provider and production quotas are preserved.
- Plan conversations disable outside-library AI context. Topic drafts require a user action to send. Source links open a separate tab and preserve the conversation. Returning from the full-plan reader preserves an edited follow-up, and clarifications remain in subsequent question history.

## Validation and release

The reconciled SDK source passes 219 backend tests and 255 frontend tests, including native table/character regression checks and a whole-context budgeting test. The local index passes six scoped fallback preparation cases, three general SAPCC searches and three retained research searches. The SDK additionally passes six full-page scoped searches and rejects all 12 incomplete minute pages as citation evidence. Frontend checks cover plan entry points, correct document/version payloads, no automatic model submission, citation navigation, draft preservation and source-only mode at 320, 390, 768 and 1440 CSS pixels. Model calls are mocked in those repeatable UI checks; actual hosted answer acceptance is recorded separately.

The source retains the current Figtree/Arc design. Desktop and phone captures were inspected; the one detector pass found 16 pre-existing advisory token findings in climate-plan styles and no new material defect. Required retained-route checks passed on desktop and phone, including template PDF export. No Device Hub was used.

Detailed evidence, staged-index preservation hashes, character audit, screenshots and live acceptance are retained under ignored `.reports/sapcc-research/`. Two baseline paid attempts used the existing production ledger: heat/health answered with citations; solar exposed the defect above. They remain counted. No accepted historical research cases were repeated. Final runtime, frontend deployment, ledger counters and public answer results will be recorded after release.

PR #119 contains the SAPCC integration. The parallel SDK release in PR #118 is reconciled into this isolated branch for compatibility checks. Its owner has completed the SDK release and cleared ownership in issue #89. Final main b905a5e is reconciled; SAPCC activation and hosted acceptance can now proceed. The old service package is superseded and must not be deployed.

## Hosted source-context correction

Runtime ebb35bf and generation 20261030-sapcc-native-v2 were activated after a WAL-safe production ledger backup, preserving the completed SDK release. The first two scoped SDK questions returned exact source links but failed manual semantic review: solar labelled a barriers/gaps cell as a success indicator without its preceding header page; water cited page 49 for a budget printed on page 50. Both responses and all ten model-call reservations remain retained and rejected. Frontend promotion is held.

The reader now supplies complete native SAPCC spreads and bounded adjacent original table pages within the existing 24,000-character tool limit. It does not reconstruct rows or edit source text. Required read context remains attached to citations, including after another page read, so headers and adjacent table values cannot lose their source links. Other document extractions retain their existing paging behavior. The two changed source-context questions require fresh hosted acceptance; prior attempts are not overwritten.

The corrected solar question passed source review on runtime d594ddc in 14.86 seconds, with four model calls and original pages 12/41–43 attached. The corrected water attempt was safely rejected by citation validation: diagnostics identify a page-69 search-snippet ID absent from the read-source set. No invalid answer reached the interface. Document-scoped discovery now withholds citation IDs and passage URLs until a full read; the validator remains strict. This follow-up changes discovery metadata, not source passages, accounting or the accepted solar table context. The failed water attempt remains charged and retained.
