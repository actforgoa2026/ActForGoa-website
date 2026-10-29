# SAPCC design documentation check

Completed 29 October 2026 after the mobile first-viewport correction. This is an ordinary extension of the existing ActForGoa library and practical-guide reading system, in Read mode. No new visual world or durable system change was approved or introduced.

The installed Impeccable documenter definition and `reference/document.md` were used. The context workflow ran for `src/ClimatePlan.tsx`; `PRODUCT.md`, `DESIGN.md`, the design sidecar, the surface direction contract, the final implementation, and incumbent Arc components were compared. No interview or concept round was repeated because the parent supplied the settled scope and confirmed resident-focused direction.

## Outcome

The implementation inherits the established system. `DESIGN.md`, `.impeccable/design.json`, and `PRODUCT.md` are preserved. The route's structure, local type sizes, and responsive adaptations remain surface-specific; they have not been promoted into global tokens or rules.

| System characteristic | Finished implementation and evidence |
| --- | --- |
| Palette | The page inherits warm paper `--paper`, forest green `--green`, supporting `--muted`, structural `--line`, and pale selected/search fills from `src/styles.css`. No competing palette or image surface is introduced. |
| Type | Upright Manrope is inherited. Titles use 48px at weight 750, becoming 36px on phones; section/action headings use 28/22px, becoming 24/20px; reading text uses 17px with 1.85 leading, becoming 16px. These are local reading adaptations, not changes to the shared ramp. |
| Open page and structural lines | Topic, measure, chapter, reference, and source-fact rows sit on the continuous page ground. Horizontal rules separate content. The rendered views contain no filled content cards or decorative side stripes. |
| Controls and focus | Search uses the installed Arc `SearchField`, a visible label, 16px input, pale fill, fill-based focus, and reserved clear-action space. Copy and empty-state recovery use Arc `Button`. PDF and route actions retain anchors. The installed 4px control radius and keyboard focus conventions remain in force. |
| Reading and wayfinding | Overview topics use two columns on desktop and one on phones. Detail pages pair a 244px wayfinding rail with a reading column up to 760px; the rail becomes a native disclosure below 760px. Source facts stack below 620px. |
| Source proximity | Each selected measure includes named agencies and an adjacent exact-spread link. Printed numbers remain distinct from physical PDF page numbers. Source notes distinguish the guide, source edition, retrieval date, extraction limits, and current-delivery uncertainty. |

The build expresses the existing Upright Type, Open Page, Structural Line, Stable Focus, Source Proximity, and Browsing Continuity rules. The labelled search and three link-based views serve the authored climate index; they do not change the library's submit-search composition or Arc's shared behavior.

## Rendered evidence inspected

All paths below are under `.impeccable/review/sapcc/`. These were opened directly as local images; no browser or Device Hub was used in this documentation pass.

| Capture | Observation |
| --- | --- |
| `desktop-viewport.png` | The library breadcrumb, title, short introduction, edition, PDF action, views, labelled search, and first topic rows appear together at 1440 × 1000. |
| `mobile-viewport.png` | At 390 × 844 the first topic title, arrow, and start of its description are visible. Grouping the PDF action with its metadata and shortening the introduction resolve the recorded first-viewport promise. |
| `desktop-water.png` | The topic rail, readable article, two selected measures, adjacent source references, resident question, copy action, and connected topics form a coherent reading sequence. |
| `mobile-water.png` | The same information stacks without an enclosing panel; topic switching becomes a disclosure, and source numbers remain readable beside or below their links. |
| `desktop-source.png` | Source facts use open ruled rows, followed by readable explanatory sections and source/download actions. |
| `mobile-source.png` | Fact labels and values stack naturally; source caveats and reading-guide download remain available. |
| `incumbent-library.png` | The same paper, green ink, upright type, Arc search treatment, open ruled records, and shared header establish the extension's visual continuity. |

`reports/sapcc/finish-review.md` records the initial mobile issue and the reviewer's final `ship` disposition for that resolved fix. This documentation check does not enlarge that verdict into a new whole-surface review.

The supplied `browser-checks.json` reports successful journeys, equal viewport and document widths at 320, 390, 768, and 1440 pixels, and no computed italic/oblique styles or sideflag borders in the checked main content. `design-scan.json` has no findings. The new TSX and CSS were inspected directly for italic/oblique styling, decorative side borders, and pseudo-element decorations; none were found. The detector, browser journeys, build, and tests were not rerun by this documenter.

## Product and source boundaries

`docs/climate/README.md` and `reports/sapcc/VERIFICATION.md` preserve the government PDF, local retention and public linking distinction, 13 resident topics, 26 selected measures, chapter access, and the limitations of extraction and historical status. The UI presents an authored guide and practical questions, with source links, rather than asserting live delivery. This is consistent with the product's practical-help and source-provenance commitments. This pass inspected the presentation and documentation, not every underlying factual claim or every PDF spread.

No raster assets ship with this addition, and no comp was required for this scoped, code-led extension. Screenshots are verification evidence rather than production imagery.

## Pre-existing drift left unchanged

The shared header has a narrow-phone wrapping rule at container widths up to 480px in `src/components/arc/site-header/site-header.module.css`: automatic height, a full-width brand row, and language/search/menu actions below. The existing `DESIGN.md` describes the general 80px compact header without this later exception, and its sidecar header specimen does not depict the language selector. This is pre-existing documentation drift outside SAPCC's write boundary; neither the functioning shared header nor the incumbent design files were changed or recanonized here.

The design document's prior test counts and deployment paragraph remain dated evidence for earlier work. Current SAPCC validation and its undeployed status are recorded in `reports/sapcc/VERIFICATION.md`, not inferred from those older notes.

Files written by this pass: this report and an appended check result in `.impeccable/surfaces/climate-plan.md`. Unrelated work is preserved.
