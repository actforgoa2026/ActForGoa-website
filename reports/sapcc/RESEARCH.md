# Goa SAPCC research integration · 30 October 2026

The user requested SAPCC questions with source links in the resident research assistant. The hosted library already contained the exact retained government PDF, but its two-page and sideways-table extraction contained excessive whitespace and interleaved text. A baseline rooftop-solar question returned no evidence. The source refresh and document-focused budget fix address that failure.

## Source and answer behavior

- Original SHA-256: `d1b64d562f93c9cbabc39e1d4be65f0515a06734792cfa5ea4eebf9544ff3cc6`, 111 physical PDF pages.
- New generation: `20261030-sapcc-native-v2`; document `d1b64d562f93c9cbabc39e1d-dc16e9345778`.
- The extractor reads each printed half independently, corrects native sideways orientation and retains table-cell positions. All 111 pages passed a non-whitespace character-multiset audit against the original native PDF text, with no missing or extra characters. This verifies preservation, not semantic completeness; rendered health and power pages were also inspected.
- Scanned committee minutes on physical pages 99–110 remain in the reader and original PDF but are excluded from answer evidence. No OCR or reconstructed cross-page rows are claimed.
- All 1,173 other documents, 21,423 pages and 78,987 chunks/FTS rows remain byte-equivalent in their SQL values. Both local and hosted staging checks preserve the original generation files; prior published citations remain available.
- Document conversations budget each complete passage plus its required context independently, preventing one overfull document group from discarding every passage. General collection grouping, model, prompts, output limits, provider and quotas are unchanged.
- Plan conversations disable outside-library AI context. Topic drafts require a user action to send. Following a citation and returning preserves the conversation and edited follow-up.

## Validation and release

The current source passes 190 backend tests, including native table/character regression checks and a whole-context budgeting test. The local index passes six scoped preparation cases, three general SAPCC searches and three retained research searches. Frontend checks cover plan entry points, correct document/version payloads, no automatic model submission, citation navigation, draft preservation and source-only mode at 320, 390, 768 and 1440 CSS pixels. Model calls are mocked in those repeatable UI checks; actual hosted answer acceptance is recorded separately.

The source retains the current Figtree/Arc design. Desktop and phone captures were inspected; the one detector pass found 16 pre-existing advisory token findings in climate-plan styles and no new material defect. Required retained-route checks passed on desktop and phone, including template PDF export. No Device Hub was used.

Detailed evidence, staged-index preservation hashes, character audit, screenshots and live acceptance are retained under ignored `.reports/sapcc-research/`. Two baseline paid attempts used the existing production ledger: heat/health answered with citations; solar exposed the defect above. They remain counted. No accepted historical research cases were repeated. Final runtime, frontend deployment, ledger counters and public answer results will be recorded after release.
