# Listing layout refinement

26 October 2026. The user requested a single reading column for organisation and contact listings, with the former right-hand content below the description, a narrower measure, and consistent contact, map and website icons.

## Implemented scope

Archive records whose kind is `organisation` or `contact`, and individual CRM records, now use a centred shell with a maximum width of 680px. Existing responsive page gutters remain in force. Archive contact, source and correction sections follow the article in normal document order; related records use one column. CRM public contacts follow the description, tags and photograph, with verification and research sections next and the browser-local relationship workspace below the complete record.

`ListingLink` supplies labelled Lucide outline icons at 18px with a 1.7 stroke and a minimum 44px link height. Email, phone, map, website, social, participation and source actions share this treatment. Icons are hidden from assistive technology, visible text supplies the link purpose, and long labels wrap. Email and phone actions retain their native URL schemes; web destinations open in a new tab. Shared listing-card actions also inherit these icons.

Archive details consolidate email, website, map, location and other available links in “Contact & location”. Full details retain all distinct email addresses and locations. Original-source and public-directory links stay together, and a directory-source URL equal to the public API URL is no longer repeated. The copy-link control now uses the same icon size and stroke throughout the shared detail renderer.

CRM details retain all valid distinct email and phone values, the website, map and participation routes, and available Instagram, Facebook, LinkedIn, X and YouTube links. The former repeated place/contact actions are consolidated; place evidence remains in “Place & work sources”. Historical deceased-record restrictions, contact and availability caveats, verification disclosures, photographs and provenance remain. Archive phone suppression is unchanged; this refinement preserves the CRM's existing contact behavior.

Record data, original descriptions, historical context, catalogue back-navigation, clipboard behavior, relationship save handlers, backup import/export and local-storage boundaries are unchanged. The source catalogue and research data were not edited.

## Relationship to the design system

This is a scoped Read/Operate refinement within the existing warm-paper, forest-green, upright Manrope and Arc system. It introduces no palette, font, decorative panel or side stripe.

`DESIGN.md` still describes the general reading layout as an article up to 760px wide beside a separate aside. That remains the implemented layout for ordinary article details; the new 680px single-column listing variant is the user's explicit exception. Story and guide layouts and reading content are outside this change. `PRODUCT.md`, `DESIGN.md`, the design sidecar and surface briefs were preserved rather than refreshed as a side effect.

## Verification and limits

- The parent reports 104 automated tests passing and a successful TypeScript/Vite production build. This documentation pass did not rerun those commands.
- Parent browser checks covered desktop at 1440px, tablet at 768px and phone at 390px with production fonts loaded, and found no horizontal overflow on the inspected routes.
- Captures are in `.impeccable/review/listing-single-column/`: Anish Sousa desktop, full-page desktop, tablet and phone; WAG desktop, phone and phone contact actions; CRM desktop and phone. This documentation pass inspected `anish-desktop.png`, `wag-mobile-contacts.png` and `crm-desktop.png`, confirming the narrow column, contacts below the description, consistent icons and CRM notes below the record.
- `detector.json` has zero primary findings and two typography advisories for the inherited CRM 38px and 30px sizes. Both sizes exist in the base commit; this refinement does not introduce them.
- Source inspection found no added italic/oblique styling or decorative side-border rules. `git diff --check` passed.
- Final independent finish review returned `ship` after inspecting all nine required captures. Two CRM captures were retaken at document top to remove retained scroll/focus state; no further source fixes were requested. These local checks do not establish current service availability, contact delivery or production deployment.

## Integration notes

- Branch: `codex/listing-single-column`.
- Base: `3858a45754bd467c4fdc23598b2f4e9a3c30a782` (`3858a45`), matching the inspected merge base with `origin/main`.
- Changed source: `src/App.tsx`, `src/CRM.tsx`, `src/CRMDirectoryInfo.tsx`, `src/DirectoryInfo.tsx`, `src/crm.css`, `src/directory.css`; new shared component: `src/ListingLink.tsx`.
- No dependency, environment, schema or data changes. No migration or configuration step is required.
- Status at documentation time: local work only; not pushed, merged or deployed. The release coordinator owns combined deployment under the repository's integration rules.
