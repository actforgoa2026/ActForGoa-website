# Research extension design documentation

Date: 26 October 2026

Documentation outcome: the research search and document reader extend the incumbent ActForGoa system. No new visual world or system-wide token change is established by this release. Canonical `DESIGN.md`, `.impeccable/design.json`, configuration, and source files are preserved by this documentation pass.

## Authority and scope

The current visual authority supplied for this extension is `reports/research-release/current-design-reference.md`, checked against `src/styles.css`, the installed Arc components, and the finished captures. `PRODUCT.md` supplies product purpose and durable constraints: useful public browsing, preserved source material, source provenance, accessible controls, upright Manrope, and no decorative side stripes. Its older visual and release statements are not current release evidence.

The reviewed implementation is `src/Research.tsx` and `src/research.css`, with routing and Resources navigation integration in `src/App.tsx`. The search surface is Operate; the full-document surface is Read. These task-specific roles and the arrangements below do not redefine the global system.

Impeccable's documentation playbook was read for this fresh pass. The existing session context and supplied finish review were used without rerunning context or the detector. This report records evidence for an ordinary extension; it does not refresh or replace the existing design-system files.

## Comparison with the incumbent system

| System element | Finished extension | Evidence |
| --- | --- | --- |
| Page ground and palette | Retains warm paper, green text, muted supporting copy, pale selection fills, and soft structural rules through existing variables. No new palette primitives are introduced. | `src/styles.css`, `src/research.css`, all six captures |
| Typography | Uses upright Manrope and the incumbent strong title hierarchy. Research and reader titles use 48px, weight 750, and -0.035em tracking; phone titles use 36px. | Research heading rules; initial and reader captures |
| Reading measure | Full extracted text uses 17px with 1.9 leading and a maximum 72ch measure, reducing to 16px on phones. The current reference supports the 17px desktop and 16px phone reading sizes. The research measure is a local layout choice. | Document-text rules; reader captures |
| Source hierarchy | Page/format metadata, an 18px linked source title, 14px excerpt, extraction caution, passage disclosure, and full-document link stay together in each open row. | Source component and result captures |
| Controls | Reuses installed Arc Button, Input, Textarea, and SegmentedControl. The original download remains a real anchor with the established primary link treatment. | Imports and rendered controls in `src/Research.tsx` |
| Material and separation | Uses page-ground rows and horizontal rules. The expanded passage surface and original-page border support inspecting source content. No surrounding result-card shell, decorative side stripe, or new panel-shadow language appears. | Research CSS and all captures |
| Navigation | Extends the existing Arc Resources menu with Reading library and Research library. Resources stays active for `/ask` and `/documents/:id`; the existing header and footer remain. | `src/App.tsx` diff; captured header/footer |
| Source emphasis | A cited span uses the existing pale fill, green text, and a fine line outline. The highlight follows text rather than creating a sideflag container. | Mark rules; reader captures |

The source rows' compact metadata and excerpts serve evidence scanning; the full reader has the larger reading scale. The extension's 15px supporting copy and 26px intermediate headings remain local choices. The fresh finish reviewer found the detector's notices for these sizes advisory, with no material hierarchy failure in the supplied renders.

## Layout and responsive behavior

The extension uses the existing centred shell and gutters. The main content and evidence aside form a two-column layout with a 260px aside and 56px gap. At 1050px, these become 230px and 36px; at 850px, the aside follows the main content with a structural top rule. This preserves the incumbent reading-detail pattern.

At 620px and below, the composer action takes the available width, document download actions stack, page controls remain on one row, and long source and document titles wrap. The supplied 390px captures show the entire flow within the viewport width. Full-page captures include the document top, content, and footer without blank or malformed regions. The long phone result and reader images were also inspected at original resolution.

## Component and state evidence

The initial state makes the task clear with a labelled question field, Find sources / Ask with citations mode control, primary action, and three starter questions. The evidence aside explains source access and extraction limits without competing with the composer.

The results state keeps source entries open, with a visible full-document route and a separate passage disclosure. The captured unavailable-answer state explicitly says answers are not configured and continues to show source results. It supplies no fabricated answer.

The reader separates original download, full-text download, and publisher actions. Page navigation, the page jump input, and the Read text / Original page control remain distinct. The captured text view shows the cited passage in context, with extraction notes and document-version disclosure nearby. The original-page view exists in source but is not the displayed reader state in these six captures.

Source inspection confirms app-lifetime research memory, return links, labelled controls, status/alert roles, and existing Arc primitives. These facts describe implementation; this documentation pass did not independently exercise their browser behavior.

## Evidence inventory and limits

| Capture under `.impeccable/review/` | Documented state |
| --- | --- |
| `initial-desktop.png` | Desktop initial search and starter questions |
| `mobile.png` | Phone initial search, stacked action and following aside |
| `desktop.png` | Desktop source results with unavailable cited-answer message |
| `results-mobile.png` | Phone source results, continued composer and source context |
| `reader-desktop.png` | Desktop extracted-text reader with cited-span highlight |
| `reader-mobile.png` | Phone extracted-text reader, page controls and following aside |

`reports/research-release/finish-review.md` records a fresh reviewer disposition of `ship`, with no material visual fixes. This documentation comparison agrees that the supplied extension retains the incumbent identity. Screenshot inspection and source inspection do not establish live generated-answer quality, functional end-to-end behavior, deployment, legal currency, or source availability. No browser session, deployment, secret access, build, or test run was performed by this documenter.

## Pre-existing documentation drift

The branch's canonical `DESIGN.md` is older than the supplied current reference. Among the observable differences, it specifies 18px/450 reading copy, 400 body weight, and 800 page headings, while the current reference describes the newer 17px/550 reading role, 550 body weight, and 750 page headings. `PRODUCT.md` still says reading copy stays 18px on phones and desktop and contains an older release-status account.

The session also reports a stale `.impeccable/design.json` sidecar. It remains at schema version 2 with its existing generation timestamp of `2026-10-22T21:00:14.605895Z`; this pass does not treat that timestamp alone as a full drift diagnosis. The stale-sidecar finding is retained rather than repaired.

No refresh, overwrite, merge, sidecar regeneration, or new qualitative design decision was requested or performed. The research-specific evidence is contained in this report so that this ordinary extension does not silently change the canonical system.
