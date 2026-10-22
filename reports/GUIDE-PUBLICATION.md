# Practical guide publication

Prepared 22 October 2026 for the separate ActForGoa field-guide review website.

Published at [actforgoa-field-guide.vercel.app](https://actforgoa-field-guide.vercel.app/library). Vercel deployment `dpl_EP6Pgw7ys3VA5kCKAjK5i7Wa8Gm1` returned READY and updated the existing production alias. The original `actforgoa.org` domain and hosting are separate and were not changed.

## Scope

Five practical guides cover reporting, building, farming, animal welfare and environmental protection. The last three use 42 citation labels for 39 distinct official URLs and add nine templates. The complete guide set has 17 downloadable templates and public source/verification registers.

The guides are labelled drafts in library cards and article pages. Legal currency, current local implementation, parcel classifications and live service availability remain open where indicated. Twenty new topic-specific verification flags are recorded alongside the earlier reporting/building checks. Publishing these drafts does not establish those outstanding facts.

Raw research PDFs, downloaded pages, OCR, metadata and the search database remain local. Only authored explanatory content, templates and official links are published. The original 600-entry archive and semantic vectors are preserved; authored guides are added to keyword search, library browsing and homepage recommendations.

## Verification

- Production build and all 11 automated tests pass.
- Tests check citation definitions, internal routes, downloads, distinct section anchors, review flags, keyword discovery and original archive integrity.
- All 24 guide/register/template downloads return HTTP 200 from the public production alias and match their generated local file hashes.
- Browser inspection at 1280 × 900 and 390 × 844: readable content, no horizontal page overflow, upright type, visible draft status and working section navigation.
- Library shows 242 records, with the five practical guides first. A browser search for Krishi Card registration returns the farming guide first in guides/reading.
- Impeccable detector: no primary findings; 48 advisory findings concerning documented token alignment, mostly in incumbent CSS. Fresh review recorded separately.
- Corpus audit: checksums, text derivatives, PDF page sequences and SQLite integrity pass. Fresh guide source provenance and limitations are in `corpus/research/guide-drafts-next/validation.json`.
- Live browser verification confirms the farming and animal-welfare pages, draft status, navigation and mobile layout. Fresh design review disposition is ship; documentation review preserved the incumbent system.

No complaint, form, message or service enquiry was submitted. Source-listed contacts have not been called. No claim is made of clinician/legal sign-off or accessibility conformance certification.

## Reproduction

Edit the canonical `corpus/guides/` files, run `python3 scripts/publish_guides.py`, then `npm test` and `npm run build`. Commit canonical and generated files together. The Vercel build uses generated assets; the raw corpus is excluded by `.vercelignore`.
