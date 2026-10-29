# Goa SAPCC release preparation · 30 October 2026

The user authorized shipping the reviewed resident navigator. The release is isolated in `codex/goa-sapcc-release`, based on freshly fetched main `60844a309130dcb0355a6689fba7af949314e082`. The primary dirty checkout is preserved. The target is the existing `actforgoa-field-guide.vercel.app` review alias.

## Source scope

Includes the unchanged government PDF and provenance, authored resident guide/index, `/climate-plan` and its catalogue alias, library/search integration, reproducible guide generator, source-reference tests and verification records. Corpus raw files, extracted pages, SQLite databases, private data and credentials are excluded. The local corpus addition from the original task remains separate; this frontend release does not migrate the hosted research index.

The feature inherits the newer main-branch Figtree/Arc theme. Its PDF action uses the installed Arc ButtonLink and its search uses the current SearchField styling. No shared styling, service routing, provider settings, budgets, accounts or storage changed.

## Validation

- 248 Node tests passed; production build passed with the existing pdfmake chunk-size warning.
- SAPCC browser journeys passed at 320, 390, 768 and 1440 CSS pixels, including rapid typing, query/history restoration, copy, exact spread links, chapter navigation, downloads and catalogue-independent loading.
- Desktop and phone regression checks cover the required release routes, original-document reading, directory, reporting controls, guide, templates, research, admin sign-in and journal. Template PDF export passed in separate browser contexts. No report submission, private account mutation or paid AI request was made.
- The first regression harness attempted the hidden desktop export control on the phone layout; it was corrected to follow “Review & save” before “Save PDF”. This was a test-navigation correction, with no template code change.
- Current release-integration review: `ship`; see `RELEASE-REVIEW.md`. Sixteen design-token advisories were assessed, with no material visual mismatch. Documentation comparison is in `RELEASE-DESIGN.md`.
- Source scans and actual rendered checks found no italic/oblique text, decorative side stripes or horizontal overflow in the changed surface. Device Hub was not used.

Detailed logs, screenshots, tree-bound release evidence and final deployment records are under ignored `.reports/sapcc-release/`. The earlier files in this folder retain the 29 October local implementation evidence. Those older test counts, Manrope styling notes and undeployed status do not describe this release integration.

## Deployment boundary

The previous design release completed before this promotion. Its recorded live deployment is `dpl_7SttWKGsgEXUhymZSAXytvyyfGzL`. Root and `/explore` routing overrides are disabled; the older versioned-asset compatibility route remains enabled. No routing override changes are part of SAPCC.

Merge the tested source, bind `.reports/sapcc-release/evidence.json` to that Git tree, and use `npm run release:review` for preflight and promotion. The wrapper checks fresh main, clean source, the shared release lock, previous deployment identity, service readiness and authenticated-route boundaries before promoting. A final live record is written only after public desktop/phone verification.
