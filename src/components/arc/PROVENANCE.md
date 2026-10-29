# Arc component provenance

These components are the actual free component source from Arc UI (https://uiarc.dev), retrieved 22 October 2026 through its public registry, using its documented manual-copy workflow.

| Item | Registry source |
| --- | --- |
| SiteHeader | https://uiarc.dev/r/site-header.json |
| Foundation | https://uiarc.dev/r/arc-foundation.json |
| Motion tokens | https://uiarc.dev/r/arc-motion-tokens.json |
| Button | https://uiarc.dev/r/button.json |
| SearchField | https://uiarc.dev/r/search-field.json |
| SegmentedControl | https://uiarc.dev/r/segmented-control.json |
| Input | https://uiarc.dev/r/input.json |
| Textarea | https://uiarc.dev/r/textarea.json |

Goa theme tokens are supplied in src/styles.css. Requested adaptations: search shell has no border, text-field focus uses a background change, clear button has a 44px target and returns focus without scrolling, segmented controls have an open track without border/shadow, and keyboard changes use immediate selection rather than animated movement. Names, native controls, ARIA, label relationships, reserved clear-button space, overflow behavior and reduced-motion handling come from Arc.

Emil Kowalski's actual design-engineering skill informed the interaction pass: https://github.com/emilkowalski/skill/tree/main/skills/emil-design-eng. Local Impeccable supplies the design workflow and rendered review. The project keeps its approved upright type and stronger topic weights, rather than Arc's default typography. Brand copy and source titles remain intact.

SiteHeader uses React Router Links for local destinations and ordinary images in Vite. Its original demo is removed. Desktop dropdowns open on click, switch on pointer movement while open, support arrow navigation and Escape, and return focus without scrolling. The narrow menu traps focus while open. Static active indicators avoid shared-layout artifacts during scroll restoration; Goan typography and 44px targets replace the sample theme.


29 October 2026 satellite follow-up: DatePicker and Calendar were copied from the actual public registry at https://uiarc.dev/r/date-picker.json and https://uiarc.dev/r/calendar.json, including the Calendar use-today helper. Component behavior and Motion transitions are retained. The satellite wrapper converts date-only strings without UTC shifts, applies historical bounds, and places the trailing calendar against the right edge on narrow screens. Theme and stacking overrides are scoped to the satellite surface.
