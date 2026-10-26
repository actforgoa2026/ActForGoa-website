# Directory integration design notes

Source review on 26 October 2026 for `codex/directory-enrichment-integration`, rebased onto `f26ad87606c032ecac479c9f8028dacddce5e5a8` after CRM PR #5 and reporting PR #6. This is an ordinary extension of the current restrained Goan field guide. It does not establish a new visual direction or replace `PRODUCT.md`, `DESIGN.md`, the surface brief, or `.impeccable/design.json`.

## System preserved

- `src/directory.css` reuses the existing pale, rule and muted colour variables and inherits upright Manrope from `src/styles.css`. It introduces no new palette or font family.
- Tags use the established 4px control radius. Records, photos and direct actions remain on the open page ground without a new enclosing panel, shadow or decorative side stripe.
- Tags, locations and action labels use 14px text. Direct actions have a 44px minimum height, visible labels and Lucide outline icons. Photo credits use 12px text; this is an implementation fact and a detector advisory, not a new global type token.
- Square-cornered photo previews use a 1.9 aspect ratio. Archive list previews use a 180px square column on desktop and stack at 620px with a 1.9 crop. Detail photographs retain natural proportions. CRM row photos are capped at 320px and CRM detail photos at 680px.
- The incumbent Upright Type, Restrained Colour, Open Page, Structural Line and Source Proximity rules still apply. No changes to their normative tokens or sidecar specimens are required for this extension.

## Integration behavior

`DirectoryInfo.tsx` and `CRMDirectoryInfo.tsx` share the credited-photo component and presentation stylesheet. Archive cards and details show at most three work tags. CRM rows also show at most three, while CRM details use the `full` flag to show every merged tag. `crmDirectoryTags` combines reviewed labels with the existing source focus areas, retaining reviewed labels first and removing duplicates case-insensitively. This preserves Goa Foundation's four original specialisms and Anthony de Souza's fourth Biodiversity tag. Archive tags lead to exact filters at `/directory/archive?tag=...`; CRM tags lead to a cross-collection text search at `/directory?collection=all&q=...`. These are deliberately different retrieval behaviors. Archive details remain at `/read/:id`; the CRM retains `/directory` and `/directory/:recordId`.

Archive summaries prefer the reviewed, source-linked description when present in `src/content/directory-details.json`, then use the original paragraph or missing-description fallback. Three entries currently have this override. CRM rows and details continue to display the existing research summary. Credits retain links to the organisation source page; failed photos disappear without removing the text entry.

The CRM bridge requires an explicit record mapping, organisation type and exact expected source URL. Its 59 mappings do not join records by name or approximate location. Seven photos and five reviewed addresses extend matching organisations. CRM direct actions keep the existing research website, participation and Instagram routes, add eligible project links, and offer public email where available. Map actions are name/address searches, not matched place IDs. Deceased historical records do not receive the new outreach actions; other historical entries retain their source contact caveats. Research data, verification notes and relationship storage remain outside this presentation change.

## Documentation drift retained in scope notes

The existing `PRODUCT.md` capability paragraph and `DESIGN.md` Public record presentation section describe organisation summaries as original source paragraphs. The reviewed archive-summary override above is the extension-specific exception. `DESIGN.md` Records, source context, and browsing continuity and the surface brief still say community entries show all topics; archive cards/details and CRM rows display at most three work tags, while CRM details retain the full merged set. The general 1.6 image-preview description also needs the directory-specific crop exception recorded above. These are factual differences, not approval for a new visual world; system files remain untouched under this review's write boundary.

The CRM's pre-existing 12px, 22px, 30px and 38px typography advisories are not repaired or promoted into global tokens. The new 12px photo-credit advisory is retained for rendered review rather than legitimised by changing the normative type ramp. The system documents' earlier wireframe captures and 22-test statement describe that earlier review, not the present integration.

## Evidence and limits

Checked current `PRODUCT.md`, `DESIGN.md`, the App surface brief, sidecar narrative/specimen inventory, `src/styles.css`, `src/directory.css`, `src/DirectoryInfo.tsx`, `src/CRMDirectoryInfo.tsx`, `src/crm-directory.ts`, `src/components/RecordCard.tsx`, and the integration diffs in App, CRM, CRM styling/model and public-record presentation. Source contains no new italic/oblique styling or decorative side-stripe container in this extension.

The coordinator reports 48 tests passed after the final tag-preservation fix. The integration build, browser checks and screenshot inventory are recorded in `DIRECTORY-ENRICHMENT.md`; this documentation pass did not rerun them. Desktop and phone captures exist in `.impeccable/review/directory-integration/`. The finish reviewer owns the rendered verdict after recapture. This note does not independently establish visual quality, interaction correctness or deployment.

Final screenshot evidence uses the production preview with bundled Manrope verified loaded. Earlier development captures were superseded because the shared dependency symlink caused a local development font-serving restriction. No product tokens or source were changed for this verification correction.

The finish reviewer completed a fresh full review of the corrected production-preview captures and returned `ship` with no material fixes for the scoped directory extension.
