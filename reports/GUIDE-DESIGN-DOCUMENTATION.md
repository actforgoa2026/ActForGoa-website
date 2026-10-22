# Practical guide design documentation

Updated on 22 October 2026 for the website after integration of upstream `41cfbba` (`Merge pull request #1 from ZakKrevitt/codex/goa-ui-refinement`). This report supersedes its earlier assessment of the pre-merge guide appearance. The current authority is the user-approved Open Goan Field Guide: Manrope throughout, open paper surfaces, Arc controls, and preserved browsing continuity.

The practical guides are an ordinary extension of the current Read surface. This documentation pass preserved `DESIGN.md`, `.impeccable/design.json`, product context, and the surface brief. It changed no application code and did not rerun context loading or the detector.

## Evidence checked

- Current authority: `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`, and `.impeccable/surfaces/src-app-tsx.md`.
- Guide implementation: `src/PracticalGuide.tsx`, `src/guides.ts`, `src/styles.css`, and the guide integration in `src/App.tsx` and `src/main.tsx`.
- Supporting source: the mounted Arc SiteHeader styles, Arc foundation overrides, `src/public-record.ts`, and `scripts/publish_guides.py`.
- Fresh rendered evidence inspected: `.impeccable/review/merged-desktop.png` at 1280 × 900, `.impeccable/review/merged-mobile.png` at 390 × 844, and `.impeccable/review/merged-mobile-section.png` at 390 × 844. These show the farming guide, the current header, open review status, reference-table heading, and an anchored reading section.
- The parent workflow reports that the section-navigation history issue was fixed and browser-verified. The current source contains that fix. The broader merged finish review is tracked separately; the earlier pre-merge ship verdict is not reused as evidence for this revision.

## System comparison

| System commitment | Observed guide implementation |
| --- | --- |
| Continuous warm paper and green ink | The guide inherits the current page, text, muted, and divider tokens. Review status sits on the paper ground between horizontal rules. No new palette is introduced. |
| Upright Manrope throughout | Manrope supplies the guide title, headings, paragraphs, controls, and metadata. The current font import contains no Literata. The sampled title, status, table heading, paragraphs, and list are upright in the new captures. |
| Open page and structural lines | Contents, review context, supporting sections, downloads, and reference rows use horizontal rules. The guide has no enclosing panel, decorative side stripe, or added content shadow. Pale table-heading fill serves tabular hierarchy. |
| Responsive reading layout | The guide reuses the current detail layout: up to 760px for the article plus supporting links on desktop, then a flowing single column. Phone gutters are 20px. Long links wrap; wide reference tables have a contained horizontal scroller. |
| Arc navigation and browsing continuity | The current sticky Arc SiteHeader remains mounted. A guide reached from catalogue or discovery uses the Arc ghost Button to return through history. Section links replace the guide's current history entry and retain its route state. |
| Source proximity and phone-free presentation | Draft status, source-check date, open legal/service checks, source and verification registers, downloads, and correction routes remain explicit. Public guides use official directory/contact-page routes in place of source-listed phone numbers. Canonical research and original catalogue data remain separate. |

The guide inherits the current 48px/650 page title, reduced to 36px on phones, and the 17px reading role with a 70ch measure, reduced to 16px on phones. Reading section headings are 28px on desktop and 24px on phones; guide subheadings use 20px. Its summary is 17px on desktop and 16px at 850px. Status, table, and download text use 14px. These are component uses of the incumbent hierarchy, not a replacement type scale.

Guide section headings reserve 120px above the scroll target so the sticky header does not obscure the destination. The contents links use `replace` and preserve `location.state`, keeping the guide's Back control connected to the original catalogue or discovery entry after a section jump. Direct arrivals retain the library fallback. This records the implemented behavior; the browser verification belongs to the parent workflow.

The guide extension introduces no new raster asset. The merged site's original-photo restoration and its existing provenance map remain part of the current authority; this pass neither changes those assets nor independently verifies every restored photograph.

## Rules and limits

The Open Page, Upright Type, Stable Focus, Structural Line, Browsing Continuity, and Source Proximity rules remain the authority. The earlier Literata pairing, boxed notice treatment, yellow search action, and ochre focus descriptions are superseded and must not guide future extensions.

The bounded source scan found no italic or oblique declarations, literal italic elements, or side-border declarations in the guide component, guide adapter, and current application stylesheet. Guide emphasis explicitly uses normal styling. Rendered samples show upright Manrope and open, horizontally ruled review context. Existing Arc focus and reduced-motion behavior are inherited; this pass does not independently retest every control state.

No material mismatch between the guide extension and the current design system was established. The previous version of this report had become stale after the approved upstream refinement; that report drift is corrected here. Existing design-system documentation and sidecar specimens remain untouched. Detector advisories and the full merged finish review are handled separately and are not promoted into new design rules by this report.

Legal accuracy, live service availability, download completeness, deployed behavior, full-site phone sanitisation, and image-restoration completeness remain governed by their separate checks. This is a source-and-capture documentation comparison, not independent evidence of those outcomes.
