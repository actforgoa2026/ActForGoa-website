---
name: ActForGoa
description: An open Goan field guide with warm paper, green ink, upright typography, real photography, and Arc controls.
colors:
  paper: "#f7f6ee"
  green: "#193e32"
  muted: "#56675c"
  line: "#d0d8ca"
  choice-border: "#9faea5"
  pale: "#e9eddf"
  white: "#fffef8"
  search-focus: "#dae3cf"
  link-button-hover: "#29523e"
typography:
  display:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "clamp(42px, 4.6vw, 64px)"
    fontWeight: 800
    lineHeight: 1.14
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "48px"
    fontWeight: 750
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "32px"
    fontWeight: 750
    lineHeight: 1.25
    letterSpacing: "-0.035em"
  feed-lead:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "36px"
    fontWeight: 750
  header-label:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "13px"
    fontWeight: 750
    letterSpacing: "-0.01em"
  record-title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "24px"
    fontWeight: 750
    lineHeight: 1.35
    letterSpacing: "-0.025em"
  topic:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 800
    lineHeight: 1.35
  topic-phone:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "15px"
    fontWeight: 800
    lineHeight: 1.35
  body:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 550
    lineHeight: 1.6
  reading:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "17px"
    fontWeight: 550
    lineHeight: 1.9
  summary:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 550
    lineHeight: 1.8
  control:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: 1.4
  search:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 550
    lineHeight: 1.6
    letterSpacing: "-0.01em"
  field:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 550
    lineHeight: 1.4
    letterSpacing: "-0.01em"
  metadata:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "13px"
    fontWeight: 650
    lineHeight: 1.6
  hero-question:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 650
    lineHeight: 1.5
  home-action:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "28px"
    fontWeight: 800
    lineHeight: 1.25
  discovery-record:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "22px"
    fontWeight: 750
    lineHeight: 1.35
  discovery-topic:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "20px"
    fontWeight: 750
    lineHeight: 1.4
  discovery-topic-description:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "15px"
    fontWeight: 550
    lineHeight: 1.6
  discovery-heading-phone:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "26px"
    fontWeight: 800
    lineHeight: 1.3
  topic-description:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "13px"
    fontWeight: 650
    lineHeight: 1.4
  topic-description-phone:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "12px"
    fontWeight: 650
    lineHeight: 1.4
  guided-choice:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "20px"
    fontWeight: 750
    lineHeight: 1.4
  guided-choice-phone:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "18px"
    fontWeight: 750
    lineHeight: 1.4
  satellite-body:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 450
    lineHeight: 1.6
  satellite-title:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "24px"
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  satellite-control:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "14px"
    fontWeight: 600
  satellite-search:
    fontFamily: "'Figtree Variable', sans-serif"
    fontSize: "15px"
    fontWeight: 450
  satellite-provider-credit:
    fontFamily: "Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 500
rounded:
  control: "4px"
  question-entry: "24px"
  satellite-control: "14px"
  satellite-status: "16px"
  satellite-results: "20px"
  satellite-map: "24px"
  satellite-search: "999px"
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
  space-20: "5rem"
  space-24: "6rem"
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
    padding: "0 20px"
  button-ghost:
    textColor: "{colors.muted}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 16px"
  search-field:
    backgroundColor: "{colors.pale}"
    textColor: "{colors.green}"
    typography: "{typography.search}"
    rounded: "{rounded.control}"
    padding: "8px"
  search-field-focus:
    backgroundColor: "{colors.search-focus}"
  input:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.field}"
    rounded: "{rounded.control}"
    padding: "0 12px"
  input-focus:
    backgroundColor: "{colors.pale}"
  textarea:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.field}"
    rounded: "{rounded.control}"
    padding: "12px"
  textarea-focus:
    backgroundColor: "{colors.pale}"
  segmented-control:
    textColor: "{colors.muted}"
    typography: "{typography.control}"
    padding: "0 12px"
  segmented-control-selected:
    backgroundColor: "{colors.pale}"
    textColor: "{colors.green}"
  navigation:
    textColor: "{colors.green}"
    padding: "0 8px"
  topic-link:
    textColor: "{colors.green}"
    typography: "{typography.topic}"
    rounded: "{rounded.control}"
    padding: "12px"
  guided-choice:
    textColor: "{colors.green}"
    typography: "{typography.guided-choice}"
    rounded: "{rounded.control}"
    padding: "24px"
  record-row:
    textColor: "{colors.green}"
    padding: "24px 0"
  question-entry:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.hero-question}"
    rounded: "{rounded.question-entry}"
    padding: "12px 12px 8px 20px"
    width: "min(100%, 720px)"
  question-entry-focus:
    backgroundColor: "{colors.pale}"
  satellite-map-action:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.satellite-control}"
    rounded: "{rounded.satellite-control}"
    padding: "0 12px"
    height: "44px"
  satellite-map-action-selected:
    backgroundColor: "{colors.green}"
    textColor: "{colors.white}"
  satellite-search:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.satellite-search}"
    rounded: "{rounded.satellite-search}"
    padding: "6px"
    width: "min(100%, 460px)"
---

# Design System: ActForGoa

## Overview

**Creative North Star: "The Open Goan Field Guide"**

ActForGoa is an open, calm field guide. Warm paper carries green ink, large upright headings, useful local information, and real photographs. The page earns its structure through typography, generous space, and horizontal rules.

The approved refinement keeps the original warm-paper and green palette, with stronger upright typography. Topic browsing, reading, and contact actions share one continuous page ground. On the homepage, the heading and question composer sit over real local photography. Official Arc components provide consistent controls and interaction behavior, with the project’s colours, type, and modest corner radius applied through the foundation tokens.

The satellite investigation surface has an expressly approved exception to the guide defaults: upright Figtree, rounded floating map controls, soft functional shadows, and a map that occupies most of the viewport. It retains the same green and cream palette, installed Arc behavior, source proximity, and bans on italic type and decorative side stripes. This exception applies only while the satellite map surface is mounted; other guide surfaces keep their existing system.

**Key Characteristics:**

- Continuous warm paper and forest-green text.
- Strong upright Manrope across guide surfaces, including mission, article, and feed headings; upright Figtree in the scoped satellite surface.
- Bordered topic choices with strong labels and helpful descriptions; open resource rows.
- Real local photographs with square crops.
- Shared Arc control behavior with fill-based text-field focus.

This document records the user-approved refinement in `src/styles.css`, `src/App.tsx`, `src/home-hero.css`, the hero components, and `src/components/arc/`. It replaces the preceding boxed visual system. Frontmatter values are normative; page-specific composition lives in the matching surface brief.

## Colors

### Primary

- **Forest green** (`green`) is the primary text, action fill, caret, selection background, and shared keyboard-focus colour.

### Neutral

- **Warm paper** (`paper`) is the continuous page background and Arc primary-button text.
- **Quiet green** (`muted`) is supporting text, metadata, and inactive control text.
- **Soft rule** (`line`) is the divider and existing input-border colour.
- **Choice outline** (`choice-border`) is the restored neutral full border around homepage topic choices and guided action links; it is not a new accent palette.
- **Pale leaf** (`pale`) identifies search, selected controls, and input focus/hover.
- **Control paper** (`white`) is the resting input and textarea surface, plus photograph-caption text.
- **Search focus leaf** (`search-focus`) is the search form’s focused fill.
- **Link-action hover** (`link-button-hover`) is the pointer-hover fill for anchor-based primary actions.

Project aliases map Arc `background` to paper, `foreground` and `accent` to green, `surface` to white, `surface-muted` to pale, and text/border roles to muted/line. These are semantic aliases, not extra palette primitives. The shared foundation contains other default palettes and themes; their presence does not make them part of this implemented surface. The sidecar’s generated tonal ramps are inspection aids only.

## Typography

Manrope Variable is the default guide font family, with a generic sans-serif fallback; the satellite exception below is separately scoped. It supplies mission and article headings, the header, topic links, records, controls, and body text. The serif import has been removed. Body copy uses weight 550, most explicit page, record, and feed headings use 750, and the homepage hero and action headings use 800. The global heading fallback is also 800. Control labels use 700 and header navigation uses 750. Font synthesis is disabled.

| Role | Implemented use |
| --- | --- |
| Display | Homepage word wheel and “in Goa” share the fluid frontmatter display scale; at 620px and below it becomes `clamp(30px, 8.2vw, 42px)`. |
| Headline | Page/detail titles at weight 750; 36px on phones. |
| Discovery | Record and tool titles use 22px; topic links use 20px with 15px descriptions. Section headings use 28px, reducing to 26px on phones. |
| Header label | Desktop navigation uses 13px at weight 750. Dropdown destination labels use 15px at weight 750, with 13px descriptions. Compact top-level rows use 750 and child links use 650. |
| Title | Section headings use 32px at weight 750, reducing to 28px on phones. The homepage action heading uses the separate home-action role, reducing to 24px at 850px. |
| Topic | Homepage choice titles use 16px at weight 800 with 1.35 leading, becoming 15px at 620px. Descriptions use 13px at weight 650 with 1.4 leading, becoming 12px on phones. Inner guided choices use 20px at weight 750, becoming 18px on phones; their question headings use 24px, becoming 20px. |
| Record title | 24px at weight 750 in both grid and list layouts, including phones. |
| Body / summary | General copy and record summaries use 16px at weight 550; summaries keep 1.8 leading. |
| Reading | 17px at weight 550, with 1.9 leading and a 70ch measure, becoming 16px on phones. |
| Field / control | Text entry uses 16px at inherited weight 550; the hero question uses 650. Arc labels use 14px at weight 700; the search submit override uses 16px at 750. |
| Metadata | Record type, dates, and topic metadata use 13px at weight 650. Result counts use 13px with inherited body weight. Hero captions and the composer hint are compact exceptions at 12px and 650. |

The Arc header wordmark is the single upright string “actforgoa.” in Manrope at weight 800, 28px, with -0.04em tracking. It becomes 26px when the header container is at most 620px. The footer retains its separate wordmark styling.

### Satellite type exception

The mounted satellite surface uses the self-hosted Figtree Variable family from `@fontsource-variable/figtree`. Its body, title, control, and search roles are prefixed `satellite-` in frontmatter. The compact page title becomes 22px at 620px; evidence and history headings use 26px at weight 650. The header wordmark uses 24px at weight 700, with navigation and action labels at weight 600. Search entry becomes 16px on phones. The map status uses 14px text, reducing to 12px on phones; an acquisition date uses weight 650 within that existing bubble. Google attribution is a provider exception: the app-owned credit remains upright Arial at 14px and weight 500, while map-rendered branding and attribution retain the provider's treatment. These exceptions do not change guide typography.

**The Upright Type Rule.** Use upright text throughout, including the wordmark, quotations, labels, and numerals. Emphasis comes from size, weight, and space.

## Layout

The centred page shell is at most 1320px wide. Side gutters are 48px by default, 32px at 1150px, and 20px at 620px. The actual Arc SiteHeader has its own container queries: its bar is 96px tall and switches to an 80px compact bar below a 1200px container width. Header gutters are 48px, then 32px below 1200px, then 20px at 620px. Old global header selectors do not define the mounted Arc component.

The homepage hero layers its heading, supporting line, and rounded question composer over a full-width photograph within the page shell. Its height comes from the content and padding, not a separate fixed-height photo column. The content is centred with 18px top, 24px side, and 62px bottom padding; the composer is at most 720px wide. Captions and carousel controls sit inside the lower edge over a dark scrim. At 620px and below, the photograph spans the viewport and content padding becomes 14px 20px 72px; the supporting line stays visible. A short-phone rule at heights up to 740px reduces top and bottom padding to 18px and 66px.

Immediately below, the emergency action shares the “What do you care about?” heading row on larger screens. On phones it follows that heading at full width. All eight bordered topic choices follow in four columns with 8px gaps, changing to two columns at 850px. Each choice is at least 82px tall, with 12px padding that becomes 10px on phones. The restored-topic captures show the question, photo controls, emergency action, and all eight topics within the 1408×800 desktop and 390×844 phone viewports. Parent browser measurements place the phone choices’ lower edge at 835px; at 375×667 the choices extend to 861px and scroll naturally. The sectioned discovery feed follows.

Guided action choices use three columns and 16px gaps, with two columns when there are two or four choices. At 850px all choice grids use two columns; at 620px they use one column with 12px gaps. Discovery uses named sections with equal three-column grids and 32px gaps. At 1000px grids become two columns, and at 620px one column. People use open two-column rows and topics use a two-column link index, both stacking on phones. Search grids use two columns until 620px. Related-record grids keep their existing separate responsive rules.

The catalogue has a 236px sticky filter rail, offset 120px below the sticky header, and a flexible results column with a 48px gap. At 850px the rail becomes a horizontal scroller and the layout becomes one column. Grouped answers retain headings, total match counts, and 48px between groups. Empty groups disappear; each group and its members follow retrieval ranking. Reading details allow up to 760px for the article and a separate aside; the aside follows the article on smaller screens.

### Satellite layout exception

The satellite map shell has 16px side gutters, reducing to 8px at 620px, with a compact 64px Arc header above it. The map height is `calc(100svh - 140px)` with a 480px minimum and no maximum; below 760px it becomes `calc(100svh - 170px)`. Search floats at the upper left and drawing, location, expansion, and zoom controls at the right. At 760px the search spans the available width and the tools move to a second row. The floating place list scrolls within `min(400px, 55svh)`. Supporting investigation sections retain a 1120px maximum width below the map. Expanded mode uses the viewport and keeps imagery captions, opacity controls, and provider attribution available. The surface brief owns the route-specific sequence and environmental-context placement.

**The Open Page Rule.** Keep the introduction, editorial pairings, records, and source context on the page ground. Use spacing and structural rules instead of enclosing them in panels.

## Elevation & Depth

The page, photographs, record rows, source notices, header bar, and mobile sheet have no visible surface shadows. Structure comes from the paper ground, fine horizontal rules, and image boundaries. The functional desktop dropdown is an exception: a white surface with a 1px border, 4px corners, and `0 16px 32px #193e3214` shadow separates navigation from the page. Its mobile counterpart uses a transparent-black scrim (`oklch(0% 0 0 / .16)`) behind the sheet. Homepage headings, captions, credits, and carousel controls use white text over the photograph. A layered dark-green scrim supplies contrast: `linear-gradient(180deg, rgb(10 28 20 / 25%), rgb(10 28 20 / 12%) 55%, rgb(10 28 20 / 70%)), rgb(10 28 20 / 50%)`. Captions do not use text shadows; the white composer retains green text.

Arc primary buttons retain the foundation’s subtle hover shadow (`0 1px 2px oklch(0% 0 0 / .035)`). This belongs to a control response, not a panel system. The foundation’s larger generic shadow tokens are not a direction for new page surfaces; the header dropdown uses its explicit project override. Textarea halo values resolve to transparent; they are not visible focus rings.

Motion follows Arc’s shared presets: short colour transitions, width-aware button press feedback, a moving segmented selection, search-clear entry/exit, and the SiteHeader’s dropdown and sheet transitions. CSS fast transitions use 160ms with `cubic-bezier(.22,1,.36,1)`; the outer search fill changes in 120ms ease-out. Components honour reduced motion, and the page disables CSS transitions, animations, and smooth scrolling under that preference. The homepage uses one shared 4000ms beat: words roll over 620ms with `cubic-bezier(.76,0,.24,1)`, and photographs crossfade over 900ms ease-in-out on every second beat. The carousel behavior is specified below. Reduced motion disables autoplay, word movement, width transitions, and photo fades. Do not add photograph zoom or decorative page entrances.

### Satellite elevation exception

Satellite controls use soft shadows to separate actions from map detail. The scoped resting shadow is `0 2px 6px rgb(25 62 50 / 6%)`; the floating search and results surface use `0 12px 36px rgb(25 62 50 / 12%), 0 2px 6px rgb(25 62 50 / 5%)`. Existing map zoom controls and the status bubble use `0 2px 8px #193e3214`. These shadows are functional map layers and do not expand the guide's content-panel vocabulary. Arc state transitions and reduced-motion handling remain in force.

## Shapes

Controls share the project’s 4px radius, except the user-requested conversational homepage composer, which uses 24px corners and a circular send button. Photograph crops and editorial structures are square. Topic and guided action choices use a full 1px neutral border and the shared 4px control corners; their resting fill stays on the paper ground. Records have a top rule and 24px top space; they have no filled card shell, surrounding border, or internal panel padding. List rows use 24px vertical space. Segmented items resolve to square corners inside a borderless control because their source radius is the control radius minus 4px.

The satellite exception uses its scoped corner tokens for controls, status, place results, and the map frame. The map frame reduces to the results radius on phones. The floating search is a pill with a circular 44px submit action; drawing, location, expansion, and zoom actions use the satellite control radius. The investigation fieldset below the map shares the map radius, a full line-colour border, and control-paper fill. No rounded treatment is applied to the geographic imagery itself or provider attribution.

**The Structural Line Rule.** Horizontal rules may separate records or sections; existing control borders may define inputs. Never add decorative side stripes to content containers.

## Components

### Satellite investigation controls

The satellite surface keeps installed Arc buttons and SearchField. Floating search has a stable full line-colour border, control-paper fill, 6px padding, and a 460px maximum width on larger screens. Drawing, location, and expansion controls use 44px targets, control-paper fill, and green text; active drawing reverses to green with control-paper text. The existing keyboard outline and field focus behavior remain. The selected-area status bubble also carries the acquisition date whenever a dated overlay is present; the full source caption and opacity control remain below the map. Preserve Google map branding and attribution during drawing and in expanded mode. The app-owned Google credit uses only the provider typography exception recorded above.

**The Satellite Scope Rule.** Keep Figtree, the enlarged map, rounded floating controls, and soft map-control shadows scoped to the satellite investigation surface. Preserve the shared palette, upright text, Arc behavior, dated imagery context, and visible provider attribution.

Evidence for this scoped exception: `src/satellite-layout.css`, `src/satellite.css`, `src/Satellite.tsx`, `src/SatelliteMap.tsx`, `src/satellite-main.tsx`, and the satellite selectors in `src/components/arc/site-header/site-header.module.css`; approval is recorded in `.impeccable/surfaces/src-satellite-tsx.md`. Supplied desktop and phone captures under `/Users/zakkrevitt/.codex/visualizations/2026/10/29/01a187dd-561f-78f3-a682-18ae44896002/` (`google-map-desktop-final.jpg` and `google-map-phone-final.jpg`) were inspected for this documentation. They show the map layout, typography, palette, floating controls, visible acquisition date, and unobscured Google attribution on desktop and phone. This documentation pass makes no deployment claim.

### Arc buttons and navigation

Use the installed `Button` for button actions. The implemented variants are primary, ghost, and secondary. Secondary uses the white control surface, a line-colour border, and green text; the feed’s manual-load control uses its large size. Standard heights are 44px, 48px, and 52px for small, medium, and large controls. Primary pairs green with paper; ghost is transparent with muted text, gaining pale fill and green text on hover/press. Primary hover uses opacity 0.91 and the subtle resting shadow; press uses opacity 0.84. Button press scale comes from Arc Motion and respects reduced motion.

Anchor actions preserve routing and links; their primary treatment uses a 52px minimum height, 12px × 20px padding, and the shared control radius. Header actions use the SiteHeader’s own 44px controls; the separate page anchor treatment is not the header sizing rule.

The shared foundation sets keyboard focus on links, buttons, and comparable non-text controls to a 2px green outline with a 3px offset. Pointer focus does not introduce that outline.

### Arc SiteHeader

The installed free Arc SiteHeader is mounted with `variant="mega"`, sticky positioning, the original nine top-level categories, and a primary Search link. The categories are Home, Take action, Blog, Inspiring stories, Resources, About, Work with us, Volunteer, and Community. Take action and About disclose their related destinations; other items navigate directly. Internal destinations use React Router links.

Desktop navigation uses 44px targets, 13px labels at weight 750, and a 2px current-item indicator. Take action offers Report an infraction, Emergency services, contribution, Green Viksit Goa, Amche Mollem, and Donations. About offers the overview, Newsletters, Annual reports, and Press coverage. Each dropdown is a 336px single-column list anchored 8px below its trigger and kept within the header edges. The surface has 8px padding; links use 8px vertical and 12px horizontal padding, 15px labels, 13px descriptions, and a 44px minimum target height. Labels align through a shared icon gutter when an icon is present. A viewport height limit allows the list to scroll on short screens. A closed dropdown opens by clicking or ArrowDown; pointer movement switches an already open menu. Escape restores focus to its trigger, and outside clicks or route changes dismiss it.

Below a 1200px header-container width, navigation becomes an overlay sheet with the same nine categories. Rows are at least 52px high; child links are at least 44px. Take action and About expand in place. The sheet locks background scrolling, keeps Tab focus among visible header controls, and closes through its scrim, Escape, route navigation, or a wider layout. Escape restores focus to the menu button. Reduced-motion handling remains in the actual Arc component.

### SearchField, Input, and Textarea

Use the installed Arc fields. The homepage uses an Arc Textarea in a 24px rounded composer with a stable 1px border, fill-based focus, two-line entry, and a circular Arc send button. Enter submits; Shift+Enter adds a line; blank questions cannot submit. The question selects the best matching homepage topic and opens its guided menu. Unclear questions stay in the composer with a link to the topic choices. Other search forms retain a pale borderless outer form with 8px padding, a borderless inner field, and a green large Button. Its focus-within fill changes to `search-focus`. The accessible field label is visually hidden in this composition. A permanent 44px slot prevents the clear action from changing the input width; clearing returns focus without scrolling. Search submit keeps its accessible label when its visible text hides on compact layouts.

Contact Input and Textarea retain their existing 1px borders and white resting fill. Focus/hover changes the fill to pale without adding a new border or visible ring. Inputs are at least 48px tall with 12px horizontal padding. Textareas have 12px padding, a 110px minimum height, and vertical resize. Contact labels use 14px at weight 750 through the page override; the shared Arc label token is 700. The current reason selector remains a native select. Required validation is native; the page does not supply custom Arc error messages.

**The Stable Focus Rule.** Text-entry focus changes the fill and caret without adding a new border, visible ring, or size change. Links and buttons retain the shared Arc keyboard outline.

### Homepage photo hero

The source-backed carousel contains Vagator, Arambol Festival, and farming photographs. Its six phrases are “Volunteer in Goa”, “Build in Goa”, “Create in Goa”, “Recycle in Goa”, “Culture in Goa”, and “Health in Goa”. A single beat drives the word and photo indices; words change each beat and photographs every second beat. The word slot measures the live word, retains enough width for the outgoing word during the roll, then shrinks after 620ms. Font loading and resizing trigger remeasurement. The heading exposes the current whole phrase as its accessible label while decorative word spans are hidden from assistive technology.

Autoplay runs only when enabled, the document is visible, the hero intersects the viewport through an observer configured with a 25% threshold, the carousel controls are not hovered, and the next photograph has loaded. Only hovering the controls temporarily suspends the timer; hovering the photograph or composer does not. Focusing a link, button, input, textarea, or select inside the hero sets a persistent pause, except for the pause/play control itself. Programmatic focus on the heading does not pause it. Previous/next and qualifying touch swipes also pause persistently; play resumes explicitly. Swipes require more than 40px of horizontal travel with less than 40px vertical travel, and do not start on interactive elements. Photo navigation is disabled with fewer than two usable images. Failed images are excluded; an all-image failure shows “For the Goa we love.” Caption announcements are polite while paused or under reduced motion and off while autoplay is enabled.

Reduced motion starts with a static phrase and photograph, removes the play control, and retains manual navigation. Manual photo selection moves the shared beat by two, keeping the word and photo sequence coordinated. The current photo caption links to its source or related record. Vagator additionally shows its creator, licence link, and cropped-image disclosure. Captions, credits, 44px navigation targets, and the numeric counter sit over the bottom scrim; the counter hides on phones.

The composer uses local intent matching in `src/home-search.ts` to enter the same topic root as its homepage button. Emergency requests enter the existing emergency page. Unclear or competing needs retain the question and offer a link to the topic choices; catalogue search remains available from the header. It uses the 24px corner token, a stable 1px line-colour border, a 48px-high two-line textarea that can resize to 160px, and a circular 44px send button. It changes to pale fill on focus without adding a ring or border. Enter submits, Shift+Enter adds a line, input composition is respected, and blank questions cannot submit.

The carousel uses 2,560–3,072px originals, served as 800, 1,600 and 2,400px WebP variants without upscaling. `public/assets/hero/provenance.json` records sources, dimensions, checksums, transformations and credits. Vagator is by Vyacheslav Argenberg under CC BY 4.0, with visible attribution and a licence link. Arambol Festival and agriculture photographs come from existing ActForGoa assets. The former river image was 768px at source and is no longer used in the hero.

### SegmentedControl and topic filters

Use the installed Arc SegmentedControl for result type, Grid/List, and the discovery feed’s Everything, Guides & resources, People & services, and Stories filters. The track is borderless and scrolls inside its own width. Selected items receive a pale highlight and green text without changing weight. Controls use 44px minimum item height and 12px horizontal padding, reduced to 10px at 380px. Arrow keys, Home, and End select and focus items; only the selected item is in the tab sequence. Overflow fades indicate additional options, and selection scrolls into view. Keyboard and reduced-motion selection changes do not animate the highlight.

Catalogue topic filters are Arc ghost buttons. Their selected state uses a pale fill and weight 750. Home topic navigation is a separate set of bordered choice buttons that leads to the restored guided topic routes. Starter queries are underlined text links with 44px minimum height, not pills.

### Restored topic choices and guided routes

The homepage uses the eight flows in `src/topic-flows.ts` in their source order: Waste & recycling, Water & environment, Community & rights, Nature & wildlife, Food & farming, Building & transport, Health & wellbeing, and Culture & heritage. Each choice shows the source label and short description, a 26px topic icon, and a trailing arrow. The arrow hides at 1150px and the topic icon hides at 620px, leaving readable text on phones. Discovery topic links retain their separate open index and now enter the same guided routes.

The route is `/topics/:slug/:actionId?/:choiceId?`. Selecting a topic shows “What would you like to do?” and its action choices; actions with children show their specific follow-up question. Selecting a leaf shows the configured destination links and, where supplied, “How to get started” steps. For example, Waste & recycling leads to Get extra rubbish collected, then Household rubbish. Breadcrumbs and the final “Choose a different…” link preserve the path back through the choices. Missing topics or actions show an unavailable-option state with a route home. A topic-only search view also exposes the corresponding choices.

Inner choices use 40px icons, at least 120px height, 24px padding, 20px gaps, and 20px labels at weight 750. At 620px, height is at least 100px, padding is 20px, gap is 16px, and labels are 18px. Topic page headings use fluid 32–48px type at weight 800 and a 52px icon, reduced to 40px on phones. Destination links use two columns on larger screens and one on phones. Steps remain an ordered list, with 18px text and 1.7 leading within a 70ch measure.

The full border uses `choice-border`. Hover changes it to green with pale fill; active choices use the line-colour fill. Keyboard focus follows the shared green outline. Colour and border transitions are 120ms ease-out and disappear under reduced motion. These bounded navigation controls do not introduce filled content cards, side stripes, or a new colour world.

People and reading remain below the choices with source context. Curated people are selected across the chosen action branch; waste actions without curated people may use relevant search results. Curated reading and linked records lead a deduplicated set of up to six items. The extracted shared `RecordCard` preserves catalogue-history state from `/topics/` routes, so opening a record and returning retains the guided context. `src/TopicPage.tsx`, `src/topic-flows.ts`, `src/topic-records.ts`, `src/topic-navigation.css`, `src/components/TopicIcon.tsx`, and `src/components/RecordCard.tsx` own this restored behavior.

### Records, notices, and browsing continuity

Open records begin with metadata, a large linked title, a readable description, and topic text. Ordinary image previews and discovery story images use a consistent 1.6 aspect ratio. Discovery guides and documents are text-led; people use open rows. General grid summaries clamp to three lines and list summaries to two within 72ch. Organisation and volunteer descriptions use a five-line allowance. Reviewed archive cards show up to three work tags, followed by archival context; CRM rows show three combined tags and details retain the complete set of reviewed and original focus areas.

Source notices are open text with an icon and strong lead. Verification notes sit between horizontal rules. Prepared-email feedback also starts after a rule and explicitly says nothing has been sent.

**The Source Proximity Rule.** Keep historical dates, original-source links, and contact caveats close to the records they qualify. A prepared email is not a sent message.

The router uses ScrollRestoration after catalogue data is available. Topic/type changes and query resubmission on the search route use `preventScrollReset`. Layout and expanded-result limits are cached per history entry; cached semantic results prevent unnecessary restoration churn. A record opened from a catalogue or guided topic route exposes a history-based “Back to results” action; direct entry retains a link to its section. Preserve these behaviors when composing new catalogue controls.

**The Browsing Continuity Rule.** Preserve scroll position when filtering or resubmitting a query on search. Returning to a catalogue history entry restores its expanded results and chosen layout.

### Sectioned discovery feed

Home discovery starts with practical guides, then local people and organisations, topic navigation, editable templates and tools, photo-led stories, documents and handbooks, and ways to participate. Later sections add the remaining topics, an incident-form link, a building checklist, and a case log. These support links point to existing routes; they are separate from catalogue record counts. Filtered views keep the selected record types and omit unrelated support sections.

`buildDiscoverySections` partitions the deterministic catalogue sequence into guides, people, stories and documents, with up to three records per section. Authored practical guides stay in the guide group even when they include template documents. Each eligible record appears once. The full sequence is built before pagination, so appending records never inserts them above previously read content. Source dates, draft status and historical contact caveats remain visible.

Every section starts with a full-width 2px structural rule, a 28px heading, a short explanation and a collection link where applicable. Space between sections is 64px (48px on phones). Guide, document and story grids use equal columns: three on desktop, two below 1000px and one below 620px. Stories use equal 1.6-ratio original image crops. People use open ruled rows with identity and topics beside the description on desktop, stacking in DOM order on phones. Topic navigation is a two-column index with descriptions and live catalogue counts; tools and participation links use compact open three-column groups. No decorative side stripes, italic text or boxed panels are introduced.

The feed starts at 12 records and appends 12 at a time. Automatic loading observes a marker 400px below the viewport and only runs while the document is visible. Pause/Resume and a manual “Show more to explore” fallback remain available. Manual loading announces additions and focuses the first new record without moving the scroll. The four filters reset the displayed extent to 12. The bounded tab-local cache retains extent, filter and automatic-loading preference per history entry before ScrollRestoration measures the page.

Implementation: `src/discovery.ts`, `src/DiscoveryLinks.tsx`, `src/discovery.css`, and `DiscoveryFeed` in `src/App.tsx`. The hero, shared record renderer and source catalogue are outside this change.

### Record presentation and original photography

The route loader maps every catalogue record through `publicRecord` before it reaches search, feed, cards, or reading views. The presentation copy clears structured phone fields, removes phone/WhatsApp link actions, and strips recognised phone numbers from titles, summaries, prose, document text, locations, and link labels. The original catalogue and archive retain their fields. This is a presentation rule, not deletion or access control for the underlying downloadable data.

Organisation descriptions use original non-heading paragraphs, prioritising the actual work over registration boilerplate, with a maximum of about 620 characters. A missing biography explicitly says that the source listing has not provided a description; do not fabricate one. Volunteer descriptions retain locality and the 2018 source context. Historical availability caveats and original-source routes remain visible even when phone actions are absent.

Original story/resource photographs are restored by `scripts/restore_article_images.py` from the existing crawl. The script uses recorded media and content images, archived WordPress renditions, and gallery references; it does not invent image URLs. The first restored image becomes the lead. Later images render in a two-column article gallery with 24px gaps and natural height, becoming one column at 620px. Non-empty source alternative text appears as a 14px muted caption. Preserve source, rendition, archive path, retrieval time, and file hash in the image map. Missing archived images remain explicitly reported rather than replaced with invented scenes.

The sidecar specimens are framework-free visual translations of the actual components. Their CSS reflects the settled appearance; the real React components own keyboard selection, clear behavior, routing, state caches, and Motion transitions.

## Do's and Don'ts

### Do

- Do preserve the open paper ground, green ink, and real local photographs.
- Do use Manrope across guide surfaces and the installed Arc components, including SiteHeader, with project overrides; apply the documented Figtree exception only to the satellite surface.
- Do keep satellite map controls, dated-overlay context, and provider attribution readable over imagery.
- Do preserve the feed’s automatic, paused, manual, and restored states.
- Do keep the stronger type hierarchy, readable record titles, and text fields at 16px.
- Do keep text-entry focus stable and preserve shared keyboard focus on actions.
- Do preserve browsing position, expanded results, and the selected layout through history navigation.
- Do keep source context and contact caveats visible, while keeping phone data out of record presentation.

### Don't

- Don't restore the boxed green introduction, filled record cards, or pale story panel.
- Don't reintroduce the withdrawn brown, pink, and yellow palette, colourful filled topic tiles, a dark header, yellow search buttons, or ochre focus outlines.
- Don't add a new focus border, visible ring, or layout shift to text fields.
- Don't use serif, italic, or oblique type anywhere.
- Don't add decorative side stripes, eyebrow labels, or fabricated local imagery.
- Don't invent organisation biographies or replace missing original photographs with fabricated images.
- Don't imply current contact verification or successful message delivery without evidence.

Evidence: current stylesheets, App, hero components, photo manifest and provenance, restored topic routes and record helpers, Arc SiteHeader and controls, route loader, discovery builder, browsing caches, public-record presentation helpers, and image-restoration code/report. All nine supplied `.impeccable/review/restored-topics/` captures were inspected: `desktop-home.png`, `mobile-home.png`, `small-phone-home.png`, `tablet-home.png`, `desktop-waste.png`, `desktop-report.png`, `mobile-waste.png`, `mobile-collection.png`, and `mobile-household.png`. They show the current topic buttons and guided menus. Earlier hero-bold and hero-carousel captures are historical composition evidence.

The parent reports 62 automated tests and browser journeys passing; `menu-checks.json` records the seven non-waste menu checks with no overflow, and the supplied detector report has zero primary findings. Its advisories cover the restored neutral choice border, compact type, and inherited hero scrim. `reports/TOPIC-RESTORATION-HANDOFF.md` records the parent’s successful TypeScript/Vite production build, with `index-CaOemWGg.js` and `index-BHzalREE.css`, and the frozen runtime snapshot at `.reports/topic-restoration-2026-10-26`. Runtime/test hashes were checked by the parent. This pass did not rerun that build or those tests. Deployment is held while the release coordinator consolidates changes. Sidecar specimens are structurally checked, not separately browser-rendered; this documentation makes no live-deployment claim.


### Integrated directory and research extensions

The sourced directory extension retains the open-page layout, source proximity and upright Manrope. Seven credited photographs use a 1.9 crop in cards and natural proportions in details. Exact source identities bridge archive records into the CRM; reviewed descriptions supplement archival prose while dates and availability cautions remain. See `reports/DIRECTORY-DESIGN-NOTES.md` for scoped evidence and unchanged typography advisories.

The research library uses existing Arc controls and page-level evidence links at `/ask` and `/documents/:id`. Source context, extraction warnings and original downloads remain adjacent to results. App-lifetime memory preserves a question when opening and returning from a source. The interface distinguishes available source search from unavailable generated answers when the server has no configured key. See `reports/research-release/design-documentation.md` and the combined integration captures for verification.

### CRM search and filter refinement

The CRM uses large shared Arc buttons for collections and quick contact/follow-up filters. Work, place and record-type controls are visible; evidence and outreach controls remain under More filters. Counts respect the query and every other filter. Active criteria can be removed individually or cleared without losing the search. Collections preserve deliberate criteria. Best match is the default sort, prioritising name matches; a blank query falls back to alphabetical order.

Collection buttons form four columns on desktop and two on compact screens. At 850 px and below, a View records action focuses the result count and scrolls to the list. Quick-filter buttons have a 52 px minimum height, and selected filters use a check icon with the existing pale fill. Removable filter buttons wrap long labels. Phone sort and export actions share a row. No new type family, palette, content container, decorative stripe or motion vocabulary is introduced. Scoped verification and captures are recorded in `reports/crm-discovery/README.md`.

### Staff curation while browsing

Authenticated staff see a compact pale-green curation bar and 44px star buttons beside directory/resource titles. Filled ochre stars indicate shared team picks; ordinary visitors see neither staff controls nor curator identities. The existing dashboard search and Team picks view manage the same records, with a link back to normal browsing. Desktop rows and phone layouts retain source qualifications and contact actions. No typography family, decorative side stripe, or italic text was introduced. Local rendered captures and the scoped finish review are in `reports/internal-tools-2026-10-28/`; hosted acceptance remains pending.
