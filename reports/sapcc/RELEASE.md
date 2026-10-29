# Goa SAPCC release · 30 October 2026

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

The tested source was merged and its exact Git tree passed `npm run release:review` preflight and promotion. The wrapper checked fresh main, clean source, the shared release lock, previous deployment identity, service readiness and authenticated-route boundaries before promoting.

## Verified public release

- Feature PR: [#113](https://github.com/actforgoa2026/ActForGoa-website/pull/113), merged as `a08277b5f5ccaa5cf32e75eebfdf6731ac31c7c2`.
- Deployed Git tree: `db7aaaca64f84db00664e77649b4f778caa766ad`.
- Deployment: `dpl_BHVXg7q6p7YtbqgKkN3h84MbgNN6`, ready in production.
- Immutable build: https://actforgoa-field-guide-97k8f30q0-zakkrevitt-gmailcoms-projects.vercel.app.
- Public navigator: https://actforgoa-field-guide.vercel.app/climate-plan.

Public browser checks passed all SAPCC journeys, including source references, copied question/reference text, query/back navigation, chapter links, guide download and library/catalogue entry points. Responsive checks passed at 320, 390, 768 and 1440 CSS pixels. The retained-route suite passed all 20 routes on desktop and phone, with template PDF export, research/admin readiness and no browser errors. Public overview, topic, source and representative retained-route screenshots were visually inspected after promotion. No paid AI requests, report submissions or private account changes were made.

The release wrapper also passed staged read-only research status/search, nested admin and satellite authentication boundaries, newsletter PDF/image and MCP gates. The source PDF remains byte-identical with SHA-256 `d1b64d562f93c9cbabc39e1d4be65f0515a06734792cfa5ea4eebf9544ff3cc6`. The hosted research corpus was not migrated; SAPCC navigation and authored search are available in the frontend.

Machine-readable acceptance and deployment identities are in `.reports/sapcc-release/release-final.json`; public captures and checks are in `.reports/sapcc-release/live/`. This final documentation update changes only this report and the implementation ledger, both excluded by `.vercelignore`, so it does not require another deployment. The runtime source remains the merged commit above.
