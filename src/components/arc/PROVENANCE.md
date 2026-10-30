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

Goa theme tokens are supplied in src/styles.css. The 29 October local refinement restores the filled segmented track, spring-driven raised selection and bordered SearchField shell. Buttons retain Arc’s sizes, press motion, label transitions and states; the green/cream theme adds restrained offset shadows to secondary actions and inputs. Input focus darkens the border. The segmented control’s optional fullWidth layout shares available width and still scrolls on narrow screens. Keyboard selection, overflow fading and reduced-motion handling remain native Arc behavior.

Emil Kowalski's actual design-engineering skill informed the interaction pass: https://github.com/emilkowalski/skill/tree/main/skills/emil-design-eng. Local Impeccable supplies the design workflow and rendered review. The project keeps its approved upright type and stronger topic weights, rather than Arc's default typography. Brand copy and source titles remain intact.

SiteHeader uses React Router Links for local destinations and ordinary images in Vite. Its original demo is removed. Desktop dropdowns open on click, switch on pointer movement while open, support arrow navigation and Escape, and return focus without scrolling. The narrow menu traps focus while open. Static active indicators avoid shared-layout artifacts during scroll restoration; Goan typography and 44px targets replace the sample theme.


29 October 2026 satellite follow-up: DatePicker and Calendar were copied from the actual public registry at https://uiarc.dev/r/date-picker.json and https://uiarc.dev/r/calendar.json, including the Calendar use-today helper. Component behavior and Motion transitions are retained. The satellite wrapper converts date-only strings without UTC shifts, applies historical bounds, and places the trailing calendar against the right edge on narrow screens. Theme and stacking overrides are scoped to the satellite surface.

29 October additions use the unmodified public registry sources for [MorphSelect](https://uiarc.dev/r/morph-select.json), [Checkbox](https://uiarc.dev/r/checkbox.json) and [Switch](https://uiarc.dev/r/switch.json), with local import paths adjusted. The checkbox label gap is 8px to leave room for the site’s accessible focus outline. Retrieved through the official site's public manual-copy registry. Existing Radix and Motion dependencies are reused. Theme colors continue through foundation tokens.

`ButtonLink` is the local anchor variant of the installed Arc Button. It directly reuses the Button CSS variants, sizes, wrapping token and Motion press spring; it adds no alternate visual skin. Internal destinations use React Router Link and external/download destinations use a native anchor, preserving href, target, modifier-click and download semantics. Topic navigation uses this variant with layout-only sizing for the large homepage choices.

The satellite timeline and opacity controls use the actual [Slider](https://uiarc.dev/r/slider.json) source, retrieved 29 October 2026. Keyboard interaction, pointer capture, value formatting and reduced-motion handling are preserved.

The standalone Earth Engine workspace retains the accepted registry-derived date picker as `date-picker/inline-date-picker.tsx` with its companion CSS. The guide uses the portalled variant added in PR #115. Both reuse the same Arc Calendar and motion tokens; this keeps independently approved layouts intact during release reconciliation.

30 October 2026: standalone satellite disclosures use the actual [Accordion](https://uiarc.dev/r/accordion.json) registry source, copied unchanged with its Radix dependency. Existing Motion tokens are reused. Workspace-scoped layout uses one continuous group for supporting information.

## NOTES heritage flow integration (local, 30 October 2026)

Retained the current Arc ButtonLink, input, textarea, header and theme. Copied the existing installed Arc Alert and ConfirmMorph from the NOTES checkout for heritage draft status and undoable removal. The NOTES menus use the current ButtonLink directly, with their grid layout in mission.css.
