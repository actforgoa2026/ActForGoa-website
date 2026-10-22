# Practical guide design documentation

Reviewed on 22 October 2026 as an ordinary extension of the existing Read surface. The incumbent design system remains applicable. `DESIGN.md`, `.impeccable/design.json`, product context, and the surface brief were preserved; this pass changed no application code.

## Evidence checked

- Authority: `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`, and `.impeccable/surfaces/src-app-tsx.md`.
- Implemented source: `src/PracticalGuide.tsx`, `src/guides.ts`, `src/styles.css`, and the integration changes in `src/App.tsx`.
- Rendered evidence inspected: `.impeccable/review/desktop.png` at 1280 × 900, `.impeccable/review/mobile.png` at 390 × 844, and `.impeccable/review/mobile-section.png` at 390 × 844. These current captures show the farming guide, its review notice, reference table, and a reading section.
- The parent workflow reports a fresh finish-review disposition of ship, with no material fixes. This documentation pass is a source-and-capture comparison, not an independent deployment or interaction test.

## System comparison

| System commitment | Observed guide implementation |
| --- | --- |
| Warm paper and forest green | The guide inherits the existing page, text, and muted colours. Status and table headings use pale leaf; dividers use the existing line token. No new palette is introduced. |
| Upright editorial and humanist type | The existing Literata reading title and Manrope body hierarchy remain. Guide emphasis is explicitly upright. The sampled title, status, table, paragraphs, and list are upright in rendered captures. |
| Readable responsive detail layout | The guide reuses the existing detail layout and shell. Desktop has article and supporting links; phone has a flowing article. Long links wrap and tables have a contained horizontal scroller. |
| Quiet depth and structural lines | Review context uses a whole pale surface with modest rounding. Contents, tables, and downloads use horizontal dividers. No decorative side stripe or added shadow appears. |
| Source proximity and honest state | The draft status, source-check date, remaining review work, verification register, source register, downloads, and correction link are explicit. The guide is not presented as legally reviewed or as live-service verification. |

The guide adds local reading patterns: a contents disclosure, reference tables, downloadable templates, and related-guide links. Its summary is 17px on desktop and 16px at the 850px breakpoint; the status, table, and download roles use 14px. These are component choices for this reading extension, not a replacement type scale. The existing main reading measure, heading hierarchy, mobile gutters, focus styling, and reduced-motion rules remain in force.

No new raster asset is introduced by the guide extension. The existing photographic system needs no additional provenance entry for this change.

## Rules and limits

The Functional Accent, Upright Type, Mobile Reading, Source Proximity, Quiet Depth, Structural Line, and Honest State rules remain the authority. Source scanning of the changed UI files found no italic or oblique declarations, literal italic elements, or side-border declarations. The guide's `em` rule explicitly sets normal styling. Rendered samples show whole-surface notices and plain horizontal boundaries.

No material design-system drift was established by this bounded comparison. Existing detector advisories remain reported by the main finish workflow and were not promoted into design rules or repaired in this documentation pass. The unchanged sidecar still documents the incumbent component specimens; guide-specific patterns do not require system regeneration for this ordinary extension.

Legal accuracy, live service availability, download completeness, browser interaction, and deployed behavior are outside this documentation verdict and remain governed by their separate checks.
