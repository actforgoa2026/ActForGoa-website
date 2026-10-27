# Corpus answers in main search

The submitted main-search question now requests a brief answer from the same saved-corpus API as the research conversation. It appears before the catalogue filters and articles; existing emergency access remains above it. No web-search tools are involved. Each paragraph requires a valid citation and each source link opens the archived document at its cited passage.

## Interface and cost behavior

- Calls only same-origin `/api/status` and `/api/chat`; the OpenRouter credential remains on the research server.
- Requests `answer_style: brief`. The backend must support this field and enforce the brief response limit before release.
- Successful answers remain in a small, ten-minute in-memory cache so source navigation does not repeat a model call.
- Cancels obsolete queries; an unavailable provider, rejected citation, timeout, or exhausted allowance leaves catalogue results usable.
- The research link pre-fills the question. Document readers offer a return to the originating search and its URL filters.
- Provider and monthly allowance configuration, shared evaluation and backend rollout belong to the coordinated ECO release. This frontend does not independently activate the provider.

## Verified legal-source refresh

`refresh_verified_legal_sources.py` builds a new isolated generation from the saved originals and the 26-entry guide verification register. It does not fetch live pages or modify the previous generation. New originals must match the reviewed SHA-256 values. Legal classifications and the register's limitations travel with evidence metadata.

Final generation: `20261026T131818-law-23a2e6a6` (supersedes the first local draft).

- 1,174 documents, 21,534 pages and 79,564 passages.
- 18 new original versions: 17 missing official sources plus the newer verified TCP index page.
- Seven existing originals receive provenance enrichment; one previously empty SOP extraction is replaced in the new generation using the reviewed OCR.
- All 26 register originals reconciled; 25 have searchable text. V22 is an image map retained as an original only.
- All 1,174 original checksums verified. Cited passages match exact page slices; previous-generation citations remain readable.
- Two PIB releases need native article extraction because their content is wrapped in an HTML form. The recovered text matches the reviewed text hashes.

Machine-readable details and source-specific limits: `reports/legal-source-reconciliation.json`.

The local data package was produced with `scripts/package_research.py --stage-data`. Its `files.json` SHA-256 is `9e03caf9af14bb5775fbf9154982dd562d80dc698ee0a13a9a0839ffcc9828f4`. Raw files and indexes are intentionally excluded from Git/static deployment. Use the validated v2 data package, not the superseded draft or its older service runtime.

## Coordinated rollout

1. Integrate ECO's validated backend, brief schema and shared budget configuration with this frontend.
2. Merge new data into the persistent research volume, preserving previous generations and the usage ledger. Switch `CURRENT.json` last; never replace the whole volume.
3. Complete the shared ecology and focused legal answer review, including citation navigation and original downloads.
4. Promote through the repository's review-site release workflow. Check the public status reports OpenRouter ready and the new generation, then verify a real cited answer in the browser.

## Remaining source limits

This refresh reconciles evidence; it does not certify consolidated current law. Parcel boundaries on V22 need map/local expert interpretation. Later amendments, commencement, court orders and applicability still need case-specific confirmation. Current local fees/forms, live agency or rescue availability, shelter capacity and clinical protocols cannot be established from archived text alone. The existing public verification register retains these distinctions.

## Checks

- 113 frontend tests pass, including five new client checks for citation validation, brief API usage, cache behavior, provider unavailability/budget errors, cancellation, and preservation of legal-source notices.
- Two new research tests pass for immutable refresh, form-wrapped article recovery, OCR migration, older citation access, and refusal to publish mismatched bytes.
- Production build passes.
- Changed-target Impeccable detector returns no findings. Rendered answer checked at 1440×1000, 1280×720 and 390×844; no horizontal overflow or italic/oblique text. Phone failure and result states also inspected.
- A real cached provider response renders with two cited paragraphs. Opening source 2 reaches PDF page 698 and highlights the cited passage; the back link preserves the question and Guides filter. The research handoff pre-fills the question.
- Insufficient-evidence and unavailable-provider client behavior are covered by automated checks; these do not substitute for the shared backend quality evaluation.
- The backend legal-source notice is validated and visibly retained below the answer; the real Parra response was inspected at all three viewport sizes.
- Fresh finish review and live activation are recorded separately when completed; a passing build is not proof of deployment.
