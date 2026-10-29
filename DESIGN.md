---
name: ActForGoa
description: An open Goan field guide in green and cream, with upright Figtree, real photography, and actual Arc controls.
colors:
  paper: "#f7f6ee"
  green: "#193e32"
  muted: "#56675c"
  line: "#d0d8ca"
  pale: "#e9eddf"
  white: "#fffef8"
  search-focus: "#dae3cf"
typography:
  display:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "clamp(44px, 4.5vw, 64px)"
    fontWeight: 650
    lineHeight: 1.15
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "48px"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  title:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "32px"
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: "-0.035em"
  body:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 450
    lineHeight: 1.6
  reading:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "17px"
    fontWeight: 450
    lineHeight: 1.9
  control:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "14px"
    fontWeight: 500
    lineHeight: 1.4
  search:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 450
    letterSpacing: "-0.01em"
rounded:
  control: "12px"
  panel: "24px"
  tag: "8px"
spacing:
  space-2: "0.5rem"
  space-3: "0.75rem"
  space-4: "1rem"
  space-5: "1.25rem"
  space-6: "1.5rem"
  space-8: "2rem"
  space-10: "2.5rem"
  space-12: "3rem"
  space-16: "4rem"
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.paper}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 16px"
  button-secondary:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 16px"
  search-field:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.search}"
    rounded: "{rounded.control}"
    padding: "0 16px"
  input:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 12px"
  textarea:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "12px"
  segmented-control:
    backgroundColor: "{colors.pale}"
    textColor: "{colors.muted}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "5px"
  segmented-control-selected:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
  navigation:
    textColor: "{colors.green}"
    padding: "0 8px"
  directory-tag:
    backgroundColor: "{colors.pale}"
    textColor: "{colors.green}"
    rounded: "{rounded.tag}"
    padding: "4px 10px"
  record-row:
    textColor: "{colors.green}"
    padding: "24px 0"
  morph-select:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.control}"
    padding: "0 36px 0 14px"
---

# Design System: ActForGoa

## Overview

**Creative North Star: "The Open Goan Field Guide"**

ActForGoa is a calm field guide rooted in local knowledge. Warm cream carries green text, upright Figtree, original photographs, and readable open records. Rounded controls and gentle shadows make actions easy to recognise without enclosing the content in another layer of panels.

The current local refinement uses the actual Arc UI sources from uiArc.dev. The shared theme changes their colour and typography while preserving component structure, semantics, states, and motion. The circular photograph homepage and the decorative stippled footer provide expression; reading, searching, and practical tasks remain restrained.

**Key Characteristics:**

- Warm cream, forest-green text, and pale green selection states.
- Upright self-hosted Figtree with moderate weights and clear hierarchy.
- Actual Arc controls, rounded corners, and gentle control shadows.
- Compact searches and open records with nearby source context.
- Original photography and a separately documented decorative footer illustration.

This records the uncommitted local implementation on 29 October 2026. It supersedes the Manrope wireframe system, the photo-background homepage composer, square controls, and fill-only field-focus guidance. It makes no deployment claim. Surface composition belongs in `.impeccable/surfaces/design-refinement.md`.

## Colors

### Primary

- **Forest green** (`green`) supplies primary text, filled actions, active controls, and carets.

### Neutral

- **Warm cream** (`paper`) is the continuous page ground and primary-action text.
- **Quiet green** (`muted`) supplies supporting copy and inactive control text.
- **Soft rule** (`line`) supplies full control borders and structural dividers.
- **Pale leaf** (`pale`) supplies segmented tracks, tags, and hover fills.
- **Control cream** (`white`) supplies fields, secondary buttons, and raised selections.
- **Selection leaf** (`search-focus`) supplies the final browser text-selection background, with green text. Despite its inherited variable name, it no longer defines SearchField focus.

Arc aliases resolve to these project tokens in `src/styles.css`. The foundation's unused accent themes and gradients are not part of this design. Its semantic danger token remains available to destructive actions and invalid fields. The rotating homepage phrase uses a local lighter-green accent; it is not a general-purpose second brand palette. Sidecar tonal ramps are generated inspection aids, not approved UI colours.

## Typography

Figtree Variable is imported locally through `@fontsource-variable/figtree` and mapped to the shared body, display, and Arc font roles. The global body weight is 450, labels 500, and headings 650. Font synthesis is disabled. The `em` and `i` elements remain semantically available but render upright.

| Role | Application |
| --- | --- |
| Display | Orbit headline uses the fluid display token, changing to `clamp(28px, 8vw, 46px)` below 700px. |
| Headline | Catalogue and detail headings use the headline token; compact layouts reduce them. AI and research-library titles use 36px; the map title uses 24px. |
| Title | Shared section headings use the title token. Record titles use 24px; topic choice links use 24px at weight 600 with 1.35 leading, reducing to 20px on phones. Their Arc link structure and states remain intact. |
| Body | General copy uses the body token. Metadata and compact supporting copy commonly use 13–14px. |
| Reading | Article prose uses the reading token within 70ch. Newsletter prose uses 17px with 1.7 leading; both become 16px on phones. Practical action steps use 18px with 1.7 leading. |
| Controls | Arc labels use the control token; SearchField text is 16px. Input and Textarea use 14px on desktop and 16px at 620px and below. The chat textarea explicitly remains 16px. |
| Navigation | Desktop labels use 14px at 500. The upright header wordmark is 28px at 700 with tight tracking, reducing to 26px on phones and 24px on map pages. |

**The Upright Type Rule.** Use upright type everywhere. Emphasis comes from weight, size, spacing, and position; never italic or oblique styling.

## Layout

The shared page shell is at most 1320px wide, with 48px side gutters, 32px below 1150px, and 20px at 620px and below. Reading narrows to a comfortable text measure. Catalogue results sit beside a 236px filter rail with a 48px gap; the rail yields to a compact layout below 850px. Resource rows remain open and separated by real structural rules.

Search composition is a field and a separate submit action with an 8px gap, without an extra enclosing visual shell. Catalogue search is bounded to 560px, directory and research-library filters to 520px, and the orbit search row to 620px. On narrow screens they shrink to available space. The AI composer uses its actual Arc Textarea with its action row below, inside an unstyled layout wrapper. Map search and tools compose the same Arc controls without an outer pill skin, and the date-period fieldset remains an open group without a panel shell.

The Arc SiteHeader is centered through its flexible navigation column while remaining the mounted `mega` variant. The bar is 80px high on wide screens and 72px below a 1400px header-container width, where it becomes a menu sheet. The map surface uses a 64px bar. These are overrides of the installed header, not a separate header implementation.

**The Open Page Rule.** Use spacing and structural rules to organise content. Compose the installed Arc controls directly; do not wrap them in a second decorative container or add a competing control skin.

## Elevation & Depth

Soft shadows belong to interactive controls, floating menus, and the map's floating tools. Open records, reading copy, and the main page ground remain flat. This replaces the previous flat-control rule. The shadows are diffuse and low contrast, with no hard offset edge.

### Shadow Vocabulary

- **Resting control** (`--shadow-resting`): `0 2px 4px rgb(25 62 50 / 5%), 0 5px 14px rgb(25 62 50 / 7%)`.
- **Field** (`--shadow-field`): `0 2px 4px rgb(25 62 50 / 4%), 0 5px 14px rgb(25 62 50 / 3%)`.
- **Floating** (`--shadow-floating`): `0 12px 36px rgb(25 62 50 / 12%), 0 2px 6px rgb(25 62 50 / 5%)`.
- **Header dropdown**: `0 16px 32px #193e3214`.

Map controls share the main Arc theme. Orbit photographs use their existing small photographic shadow, which is not a global card style.

Arc owns press springs, label transitions, moving segmented selections, expanding MorphSelect surfaces, and field feedback. Shared colour transitions use 160ms with `cubic-bezier(.22,1,.36,1)`. Preserve the components' reduced-motion handling; do not recreate it in surrounding wrappers. The orbit has its own existing animation and reduced-motion alternative.

## Shapes

The shared control radius is 12px and panel radius 24px. Segmented selections use the Arc component's control radius minus 4px. MorphSelect retains its native morphing rounded shape instead of being forced into the button radius. Its shape and list state are owned by the source component. The map shares the control radius and uses a 24px canvas, reducing the canvas to 20px on phones.

Photographs keep their existing subject-appropriate crops: orbit images have rounded square crops; content previews use a 1.6 ratio with 8px corners. Directory tags have 8px corners. These are specific treatments, not permission to enclose every content block.

**The Structural Line Rule.** Full control borders and horizontal section rules convey structure. Never use a decorative accent stripe along one side of a content block.

## Components

### Arc buttons and ButtonLink

Use the installed `Button` for actions. Primary pairs green with cream, secondary pairs control cream with a full soft border, and ghost is transparent. The copied source also supports a semantic danger variant; this is not an extra brand colour. Primary and secondary controls carry the resting shadow. Heights are 44px, 48px, and 52px for small, medium, and large sizes; wrap mode supports long labels. Standard horizontal padding is 16px, with 12px for small and 20px for large.

Secondary hover uses pale fill; primary hover and press lower opacity. Arc Motion owns width-aware press feedback and label transitions. Disabled states preserve the component's affordances. Non-text controls retain the shared 2px green keyboard outline with a 3px offset.

`ButtonLink` is a local anchor variant sharing the installed Button CSS, sizes, wrap token, and press spring. Internal destinations retain React Router links; external, download, and protocol destinations retain native anchors. Homepage topic tiles and guided destinations compose this component with layout-only sizing. It is not a separate visual skin.

### SearchField, Input, and Textarea

Use the actual installed Arc fields. The cream surface, full soft border, rounded corners, and field shadow belong to the component. Focus darkens the existing border to green without changing geometry. Hover can use pale fill. Do not restore the old fill-only focus or an additional outer search shell. SearchField retains its search icon, accessible label, clear action, and clear animation. Input and Textarea retain invalid, disabled, description, and error states.

**The Stable Focus Rule.** Change the existing field border colour on focus without changing its size. Preserve visible keyboard focus for actions and the native component's accessibility behavior.

### Selection controls

SegmentedControl uses a pale track, 5px inset, and a raised cream selection with green text. Labels do not change weight when selected. Arrow keys, Home/End, overflow scrolling, and reduced-motion behavior stay in the Arc implementation. Optional full-width layout shares available width and still permits narrow-screen scrolling.

MorphSelect supplies language, directory, and other single-choice selection where mounted. Its searchable expanding list, keyboard handling, live announcements, selected check, and floating elevation are part of the copied source. Switch and Checkbox use the actual registry sources and existing Radix/Motion dependencies. The satellite timeline and imagery-opacity controls use the actual Arc Slider, preserving keyboard interaction, pointer capture, value formatting, and reduced motion. Their labels and description relationships remain intact. Theme overrides supply green selected fills; do not substitute lookalike native or custom controls in changed UI.

### Navigation

The centered desktop navigation has plain upright labels and a small active underline. The current seven destinations are Home, Take action, Blog, Inspiring stories, Resources, About, and Directory; dropdowns keep their useful descriptions. Language and Search actions sit to the right. Desktop menus support click, pointer switching while open, arrows, Escape, and focus return; the narrow menu keeps its focus management. Preserve those behaviors when editing destinations.

### Records, tags, and source context

Records remain open rows or open grid items with a top rule, linked title, readable summary, and compact metadata. Directory tags use pale fill and wrap naturally. Keep source dates, original links, archival caveats, and verification state next to the record they qualify. Retain browsing history and scroll restoration when changing controls. Staff curation controls are authenticated UI, not a public record style.

**The Source Proximity Rule.** Keep original-source links and availability caveats near their claims. A prepared email is not a sent message, and decorative artwork is not documentary evidence.

### Footer and newsletters

`SiteFooter` places the stippled panorama above open link columns and a final structural rule. The landscape is generated decorative artwork, recorded in `public/assets/footer/goa-stippled-landscape.webp.json`; it is not a depiction of one verified place. It is hidden from assistive technology and contains no text. Original article photographs retain their own provenance.

`GoaLandscape` reuses that same artwork as an open transition after the circular homepage hero and as a small vignette beside catalogue headings. The heading treatment occupies existing whitespace without moving search or results down. Keep text and controls clear of the artwork; do not turn it into wallpaper or a new card surface. Crop the panorama responsively instead of shrinking its fine detail beyond recognition. Forms, reporting, chat, and the map do not gain decorative top blocks; the map workspace has no shared footer.

Newsletter reading is a single restrained column with issue date, historical-context note, original-issue/PDF actions, and prose before optional original-layout imagery. Transcription notes and source links remain visible. Original documents are evidence assets, not examples of the interface's typography rules.

### Evidence and limits

Inspected source: `src/styles.css`, both frontend font imports, the installed Arc CSS and ButtonLink/MorphSelect implementations, the added Slider source and satellite usage, `src/orbit-landing.css`, `src/topic-navigation.css`, `src/research.css`, `src/crm.css`, `src/directory.css`, `src/newsletters.css`, `src/satellite-layout.css`, and the footer source/provenance. Arc registry origins are recorded in `src/components/arc/PROVENANCE.md`.

Inspected supplied renders in `.impeccable/review`: `home-desktop-final.png`, `home-mobile-final.png`, `footer-desktop.png`, `newsletter-reader-mobile.png`, `library-desktop-final.png`, and `directory-select-desktop-final.png`. The library capture predates the header language-control replacement; the later homepage and directory captures plus current source establish MorphSelect there. These are local evidence, not production acceptance. This documentation pass did not rerun the app, detector, build, or end-to-end tests. Sidecar specimens are static visual translations, structurally checked but not separately browser-rendered; React components own their real interaction logic.

Not canonized: historical Manrope/wireframe captures, unused legacy selectors, and older image/prototype styles do not define the current system. Broad migration completeness and service readiness are outside this documentation pass.

## Do's and Don'ts

### Do

- Do use upright Figtree, green and cream, and the existing semantic theme aliases.
- Do use actual Arc source components and preserve their provenance, semantics, and motion.
- Do compose compact fields and separate actions without a second visual wrapper.
- Do keep open records, readable source context, and browser-local data ownership clear.
- Do preserve visible keyboard focus, reduced motion, routing, and browsing restoration.
- Do distinguish original photographs and source documents from decorative generated artwork.

### Don't

- Don't restore Manrope, the wireframe control theme, or the old photo-background composer.
- Don't add custom control skins, oversized search containers, or filled panels around ordinary reading content.
- Don't use italic or oblique text, decorative side stripes, or eyebrow labels.
- Don't turn Arc's unused demo themes and gradients into the project palette.
- Don't fabricate source content, biographies, photographs, contact verification, or service availability.
- Don't treat local screenshots or this documentation refresh as deployment or live-service acceptance.
