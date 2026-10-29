---
version: 1
slug: climate-plan
primary_target: src/ClimatePlan.tsx
related_targets: [src/climate-plan.css, src/climate-plan.ts, src/content/climate-plan.json]
---
# Goa climate plan navigation

Mode: Read. An extension of the existing ActForGoa library and practical-guide reading system.

## Direction contract

THESIS: Help a reader find the part of Goa's climate plan that relates to their life, then inspect the source.

OWN-WORLD: Inherit the warm paper, green ink, upright Figtree, Arc fields and buttons, and open ruled rows. Residents read outdoors or on phones; preserve the light, readable page ground.

STORY: Start with a familiar topic, read selected proposals, see agencies named in the plan, and open the exact PDF spread. A separate chapter index exposes the entire document.

FIRST VIEWPORT: Library breadcrumb, clear title and short introduction, source and edition information, PDF action, then topic/chapter/source navigation and a labelled search. The first topic rows are visible without an oversized hero. Detail pages use the existing reading-column and wayfinding-rail arrangement, stacking on phones.

FORM: A topic-led library guide with chapter index and exact source links. This is a scoped extension of the library's established composition; no concept roll or new visual world. Search covers the authored index and selected actions, not every PDF word. Query and view state survive shared URLs and browser history.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Source requirements

Use the government NITI for States copy downloaded 29 October 2026, cover period 2023–2033, publication 26 April 2023. Keep 111 physical PDF pages distinct from printed page numbers; most PDF pages are two-page spreads. Proposals and historical status labels are not a live progress tracker. The GSBB source URL failed retrieval. Local source is retained in docs; public links use the government host. No new imagery or translations.

## Documentation check · 29 October 2026

The installed Impeccable documenter compared the final `ClimatePlan` implementation with `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`, the incumbent Arc controls, and seven supplied desktop/mobile captures including the library reference. The final 390 × 844 overview exposes the first topic title, arrow, and description; the finish reviewer scored the recorded mobile correction resolved with disposition `ship`.

This remains an ordinary extension. The finish contract's DESIGN.md requirement is satisfied by comparing and preserving the incumbent design system, without regenerating its files. Palette, upright typography, open ruled rows, focus behavior, and source proximity remain coherent. No shipping raster assets were introduced. The report at `reports/sapcc/design-documentation.md` records the evidence, review limits, and pre-existing narrow-phone header documentation drift; that drift was not repaired in this task.

## Release integration · 30 October 2026

Ported onto fresh main after the approved Arc/Figtree update. Source content and navigation structure are retained. The PDF action uses the installed Arc ButtonLink; SearchField inherits its current cream fill and border focus. Search is capped at 560px and heading weights follow the current moderate hierarchy. Earlier review notes describe the 29 October local build; release captures and checks are recorded separately.

## Release documentation check · 30 October 2026

The installed Impeccable documenter compared the release source on main `60844a3` with the current `PRODUCT.md`, `DESIGN.md`, design sidecar, shared theme, Arc ButtonLink/SearchField/Button, and six supplied desktop/phone captures under `.impeccable/review/sapcc-release/`. Current Figtree, 650-weight headings, compact cream search with border focus, open ruled content, and nearby source references preserve the incumbent system. The first topic and its source reference are visible in the 390 × 844 release viewport.

`reports/sapcc/RELEASE-REVIEW.md` records `ship` for this release integration. The release scan has sixteen token advisories assessed as nonmaterial by that review; it does not have zero findings. These local reading-size and navigation-radius adaptations remain surface-specific. `reports/sapcc/RELEASE-DESIGN.md` records the inspected evidence and limits. The canonical design and product files are unchanged, and no shipping raster was introduced; the existing footer retains its decorative provenance.

The 29 October SAPCC style observations are historical and superseded by this release check. Supplied browser checks pass; the parent reports 248 passing tests and a passing build. This documentation pass did not rerun those checks, open a browser or Device Hub, or establish deployment. The ordinary-extension review and documentation are complete at the recorded pre-deployment scope.
