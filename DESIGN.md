---
name: ActForGoa
description: An open Goan field guide with warm paper, green ink, upright typography, real photography, and Arc controls.
colors:
  paper: "#f7f6ee"
  green: "#193e32"
  muted: "#56675c"
  line: "#d0d8ca"
  pale: "#e9eddf"
  white: "#fffef8"
  search-focus: "#dae3cf"
  link-button-hover: "#29523e"
typography:
  display:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "clamp(42px, 4.5vw, 68px)"
    fontWeight: 650
    lineHeight: 1.12
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "48px"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "32px"
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: "-0.035em"
  feed-lead:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "36px"
    fontWeight: 650
  header-label:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "13px"
    fontWeight: 650
    letterSpacing: "-0.01em"
  record-title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "24px"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-0.025em"
  topic:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "18px"
    fontWeight: 750
    lineHeight: 1.4
  topic-phone:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 750
    lineHeight: 1.4
  body:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  reading:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.9
  summary:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.8
  control:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "14px"
    fontWeight: 500
    lineHeight: 1.4
  search:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "-0.01em"
  field:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "-0.01em"
  metadata:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  control: "4px"
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
  record-row:
    textColor: "{colors.green}"
    padding: "24px 0"
---

# Design System: ActForGoa

## Overview

**Creative North Star: "The Open Goan Field Guide"**

ActForGoa is an open, calm field guide. Warm paper carries green ink, large upright headings, useful local information, and real photographs. The page earns its structure through typography, generous space, and horizontal rules.

The approved refinement removes the boxed introduction and card panels. Search, topic browsing, reading, and contact actions share one continuous page ground. Official Arc components provide consistent controls and interaction behavior, with the project’s colours, type, and modest corner radius applied through the foundation tokens.

**Key Characteristics:**

- Continuous warm paper and forest-green text.
- Upright Manrope throughout, including mission, article, and feed headings.
- Large, strong topic labels and open resource rows.
- Real local photographs with square crops.
- Shared Arc control behavior with fill-based text-field focus.

This document records the user-approved refinement in `src/styles.css`, `src/App.tsx`, and `src/components/arc/`. It replaces the preceding boxed visual system. Frontmatter values are normative; page-specific composition lives in the matching surface brief.

## Colors

### Primary

- **Forest green** (`green`) is the primary text, action fill, caret, selection background, and shared keyboard-focus colour.

### Neutral

- **Warm paper** (`paper`) is the continuous page background and Arc primary-button text.
- **Quiet green** (`muted`) is supporting text, metadata, and inactive control text.
- **Soft rule** (`line`) is the divider and existing input-border colour.
- **Pale leaf** (`pale`) identifies search, selected controls, and input focus/hover.
- **Control paper** (`white`) is the resting input and textarea surface, plus photograph-caption text.
- **Search focus leaf** (`search-focus`) is the search form’s focused fill.
- **Link-action hover** (`link-button-hover`) is the pointer-hover fill for anchor-based primary actions.

Project aliases map Arc `background` to paper, `foreground` and `accent` to green, `surface` to white, `surface-muted` to pale, and text/border roles to muted/line. These are semantic aliases, not extra palette primitives. The shared foundation contains other default palettes and themes; their presence does not make them part of this implemented surface. The sidecar’s generated tonal ramps are inspection aids only.

## Typography

Manrope Variable is the only implemented font family, with a generic sans-serif fallback. It supplies mission and article headings, the header, topic links, records, controls, and body text. The serif import has been removed. Display and page headings use weight 650; font synthesis is disabled.

| Role | Implemented use |
| --- | --- |
| Display | Fluid home heading from the frontmatter; 42px at 850px and 43px with 1.15 leading on phones. |
| Headline | Page/detail titles at weight 650; 36px on phones. |
| Feed lead | First item in each mixed batch uses 36px at weight 650, reducing to 32px at 850px. |
| Header label | Desktop navigation uses 13px at weight 650. Menu destination headings use 18px at weight 650. |
| Title | Section headings; 28px on phones. Grouped result headings use 28px, reducing to 24px. |
| Topic | 18px at weight 750 on desktop; 20px in the two-column 1150px layout; 16px at the same weight on phones. |
| Record title | 24px at weight 650 in both grid and list layouts, including phones. |
| Body / summary | General copy uses 16px; record summaries use 15px with 1.8 leading. |
| Reading | 17px with 1.9 leading and a 70ch measure, becoming 16px on phones. |
| Field / control | Text entry uses 16px. Arc control labels generally use 14px at weight 500; search submit uses 16px at weight 650. |
| Metadata | Type, dates, source status, and result counts use 12px. |

The Arc header wordmark is the single upright string “actforgoa.” in Manrope at weight 800, 28px, with -0.04em tracking. It becomes 26px when the header container is at most 620px. The footer retains its separate wordmark styling.

**The Upright Type Rule.** Use upright text throughout, including the wordmark, quotations, labels, and numerals. Emphasis comes from size, weight, and space.

## Layout

The centred page shell is at most 1320px wide. Side gutters are 48px by default, 32px at 1150px, and 20px at 620px. The actual Arc SiteHeader has its own container queries: its bar is 96px tall and switches to an 80px compact bar below a 1200px container width. Header gutters are 48px, then 32px below 1200px, then 20px at 620px. Old global header selectors do not define the mounted Arc component.

The home introduction is an open 1.4:1 text/photograph grid with a 64px gap and 64px vertical space. Its unrounded photograph is 510px tall. The phone introduction stacks with a 32px gap and a 250px photograph. The topic index and mixed discovery feed follow directly. The previous fixed story spotlight and three-resource selection are no longer mounted on Home.

The topic index uses four columns, becoming two at 1150px. Desktop topic rows are at least 100px tall; compact rows are at least 88px. In mixed discovery batches the first three records form a 1.3:1 lead arrangement: one large lead spans two rows beside two text-led records. Remaining records use a three-column grid with 40px gaps. At 850px discovery grids become two columns with 32px gaps; at 620px all discovery rows become one column. Search grids use two columns until 620px. Related-record grids keep their existing separate responsive rules.

The catalogue has a 236px sticky filter rail, offset 120px below the sticky header, and a flexible results column with a 48px gap. At 850px the rail becomes a horizontal scroller and the layout becomes one column. Grouped answers retain headings, total match counts, and 48px between groups. Empty groups disappear; each group and its members follow retrieval ranking. Reading details allow up to 760px for the article and a separate aside; the aside follows the article on smaller screens.

**The Open Page Rule.** Keep the introduction, editorial pairings, records, and source context on the page ground. Use spacing and structural rules instead of enclosing them in panels.

## Elevation & Depth

The page, photographs, record rows, source notices, header bar, and mobile sheet have no visible surface shadows. Structure comes from the paper ground, fine horizontal rules, and image boundaries. The functional desktop dropdown is an exception: a white surface with a 1px border, 4px corners, and `0 16px 32px #193e3214` shadow separates navigation from the page. Its mobile counterpart uses a transparent-black scrim (`oklch(0% 0 0 / .16)`) behind the sheet. The river caption uses a small text shadow for contrast (`0 2px 5px` in green).

Arc primary buttons retain the foundation’s subtle hover shadow (`0 1px 2px oklch(0% 0 0 / .035)`). This belongs to a control response, not a panel system. The foundation’s larger generic shadow tokens are not a direction for new page surfaces; the header dropdown uses its explicit project override. Textarea halo values resolve to transparent; they are not visible focus rings.

Motion follows Arc’s shared presets: short colour transitions, width-aware button press feedback, a moving segmented selection, search-clear entry/exit, and the SiteHeader’s dropdown and sheet transitions. CSS fast transitions use 160ms with `cubic-bezier(.22,1,.36,1)`; the outer search fill changes in 120ms ease-out. Components honour reduced motion, and the page disables CSS transitions, animations, and smooth scrolling under that preference. Do not add photograph zoom or decorative page entrances.

## Shapes

Controls share the project’s 4px radius. Photograph crops and editorial structures are square. Records have a top rule and 24px top space; they have no filled card shell, surrounding border, or internal panel padding. List rows use 24px vertical space. Segmented items resolve to square corners inside a borderless control because their source radius is the control radius minus 4px.

**The Structural Line Rule.** Horizontal rules may separate records or sections; existing control borders may define inputs. Never add decorative side stripes to content containers.

## Components

### Arc buttons and navigation

Use the installed `Button` for button actions. The implemented variants are primary, ghost, and secondary. Secondary uses the white control surface, a line-colour border, and green text; the feed’s manual-load control uses its large size. Standard heights are 44px, 48px, and 52px for small, medium, and large controls. Primary pairs green with paper; ghost is transparent with muted text, gaining pale fill and green text on hover/press. Primary hover uses opacity 0.91 and the subtle resting shadow; press uses opacity 0.84. Button press scale comes from Arc Motion and respects reduced motion.

Anchor actions preserve routing and links; their primary treatment uses a 52px minimum height, 12px × 20px padding, and the shared control radius. Header actions use the SiteHeader’s own 44px controls; the separate page anchor treatment is not the header sizing rule.

The shared foundation sets keyboard focus on links, buttons, and comparable non-text controls to a 2px green outline with a 3px offset. Pointer focus does not introduce that outline.

### Arc SiteHeader

The installed free Arc SiteHeader is mounted with `variant="mega"`, sticky positioning, the original nine top-level categories, and a primary Search link. The categories are Home, Take action, Blog, Inspiring stories, Resources, About, Work with us, Volunteer, and Community. Take action and About disclose four destinations each; other items navigate directly. Internal destinations use React Router links.

Desktop navigation uses 44px targets, 13px labels at weight 650, and a 2px current-item indicator. Take action offers contribution, Green Viksit Goa, Amche Mollem, and Donations. About offers the overview, Newsletters, Annual reports, and Press coverage. Dropdown content uses two columns, 20px padding, and 18px destination labels. A closed dropdown opens by clicking or ArrowDown; pointer movement switches an already open menu. Escape restores focus to its trigger, and outside clicks or route changes dismiss it.

Below a 1200px header-container width, navigation becomes an overlay sheet with the same nine categories. Rows are at least 52px high; child links are at least 44px. Take action and About expand in place. The sheet locks background scrolling, keeps Tab focus among visible header controls, and closes through its scrim, Escape, route navigation, or a wider layout. Escape restores focus to the menu button. Reduced-motion handling remains in the actual Arc component.

### SearchField, Input, and Textarea

Use the installed Arc fields. Search has a pale borderless outer form with 8px padding, a borderless inner field, and a green large Button. Its focus-within fill changes to `search-focus`. The accessible field label is visually hidden in this composition. A permanent 44px slot prevents the clear action from changing the input width; clearing returns focus without scrolling. Search submit keeps its accessible label when its visible text hides on compact layouts.

Contact Input and Textarea retain their existing 1px borders and white resting fill. Focus/hover changes the fill to pale without adding a new border or visible ring. Inputs are at least 48px tall with 12px horizontal padding. Textareas have 12px padding, a 110px minimum height, and vertical resize. Contact labels use 14px at weight 650. The current reason selector remains a native select. Required validation is native; the page does not supply custom Arc error messages.

**The Stable Focus Rule.** Text-entry focus changes the fill and caret without adding a new border, visible ring, or size change. Links and buttons retain the shared Arc keyboard outline.

### SegmentedControl and topic filters

Use the installed Arc SegmentedControl for result type, Grid/List, and the discovery feed’s Everything, Guides & resources, People & services, and Stories filters. The track is borderless and scrolls inside its own width. Selected items receive a pale highlight and green text without changing weight. Controls use 44px minimum item height and 12px horizontal padding, reduced to 10px at 380px. Arrow keys, Home, and End select and focus items; only the selected item is in the tab sequence. Overflow fades indicate additional options, and selection scrolls into view. Keyboard and reduced-motion selection changes do not animate the highlight.

Catalogue topic filters are Arc ghost buttons. Their selected state uses a pale fill and weight 650. Home topic navigation is a separate open index: large, bold links between rules. Starter queries are underlined text links with 44px minimum height, not pills.

### Records, notices, and browsing continuity

Open records begin with metadata, a large linked title, a readable description, and topic text. Ordinary image previews use a 1.6 aspect ratio; the first mixed-feed lead uses 1.4, while its two companion images are hidden. General grid summaries clamp to three lines and list summaries to two within 72ch. Organisation and volunteer descriptions use a five-line allowance and show all topics, giving their work more room.

Source notices are open text with an icon and strong lead. Verification notes sit between horizontal rules. Prepared-email feedback also starts after a rule and explicitly says nothing has been sent.

**The Source Proximity Rule.** Keep historical dates, original-source links, and contact caveats close to the records they qualify. A prepared email is not a sent message.

The router uses ScrollRestoration after catalogue data is available. Topic/type changes and query resubmission on the search route use `preventScrollReset`. Layout and expanded-result limits are cached per history entry; cached semantic results prevent unnecessary restoration churn. A record opened from a catalogue exposes a history-based “Back to results” action; direct entry retains a link to its section. Preserve these behaviors when composing new catalogue controls.

**The Browsing Continuity Rule.** Preserve scroll position when filtering or resubmitting a query on search. Returning to a catalogue history entry restores its expanded results and chosen layout.

### Mixed discovery feed

The current catalogue supplies 528 eligible feed entries: 237 resources, 138 stories, 104 organisations, and 49 volunteer contacts. This is a catalogue snapshot, not a hard-coded product limit; generic pages are excluded. A deterministic kind cadence mixes reading and people, prioritising the established featured records and records with photography, then publication date and title. Each eligible record appears once.

The feed starts at 12 entries and appends batches of 12. Automatic loading observes a marker 400px below the viewport and runs only while the document is visible. Pause/Resume auto-load remains available; “Show more to explore” is always the manual fallback while records remain. Manual loading announces the number added and moves focus to the first new title without scrolling. The four kind filters reset the displayed extent to 12. The first eight batches include a ruled topic route between groups, and the final state confirms that the collection has been explored.

Batch spacing is 56px, reducing to 40px on phones. Topic routes have full horizontal rules, 32px vertical padding, and 28px headings; phone values are 24px. The feed remembers its extent, kind filter, and automatic-loading preference per history entry in a bounded tab-local cache. Returning from a record restores those values before ScrollRestoration measures the page.

### Record presentation and original photography

The route loader maps every catalogue record through `publicRecord` before it reaches search, feed, cards, or reading views. The presentation copy clears structured phone fields, removes phone/WhatsApp link actions, and strips recognised phone numbers from titles, summaries, prose, document text, locations, and link labels. The original catalogue and archive retain their fields. This is a presentation rule, not deletion or access control for the underlying downloadable data.

Organisation descriptions use original non-heading paragraphs, prioritising the actual work over registration boilerplate, with a maximum of about 620 characters. A missing biography explicitly says that the source listing has not provided a description; do not fabricate one. Volunteer descriptions retain locality and the 2018 source context. Historical availability caveats and original-source routes remain visible even when phone actions are absent.

Original story/resource photographs are restored by `scripts/restore_article_images.py` from the existing crawl. The script uses recorded media and content images, archived WordPress renditions, and gallery references; it does not invent image URLs. The first restored image becomes the lead. Later images render in a two-column article gallery with 24px gaps and natural height, becoming one column at 620px. Non-empty source alternative text appears as a 14px muted caption. Preserve source, rendition, archive path, retrieval time, and file hash in the image map. Missing archived images remain explicitly reported rather than replaced with invented scenes.

The sidecar specimens are framework-free visual translations of the actual components. Their CSS reflects the settled appearance; the real React components own keyboard selection, clear behavior, routing, state caches, and Motion transitions.

## Do's and Don'ts

### Do

- Do preserve the open paper ground, green ink, and real local photographs.
- Do use Manrope throughout and the installed Arc components, including SiteHeader, with project overrides.
- Do preserve the feed’s automatic, paused, manual, and restored states.
- Do keep topic labels strong, record titles readable, and text fields at 16px.
- Do keep text-entry focus stable and preserve shared keyboard focus on actions.
- Do preserve browsing position, expanded results, and the selected layout through history navigation.
- Do keep source context and contact caveats visible, while keeping phone data out of record presentation.

### Don't

- Don't restore the boxed green introduction, filled record cards, or pale story panel.
- Don't reintroduce yellow search buttons or ochre focus outlines.
- Don't add a new focus border, visible ring, or layout shift to text fields.
- Don't use serif, italic, or oblique type anywhere.
- Don't add decorative side stripes, eyebrow labels, or fabricated local imagery.
- Don't invent organisation biographies or replace missing original photographs with fabricated images.
- Don't imply current contact verification or successful message delivery without evidence.

Evidence: current stylesheet, App, Arc SiteHeader and controls, route loader, discovery builder, browsing caches, public-record presentation helpers, and image-restoration code/report. The existing refinement captures show earlier composition, including superseded serif text and header; they do not verify the latest typography, navigation, sanitisation, or gallery. Current source is normative for this update. Sidecar snippets are structurally checked, not separately browser-rendered, and documentation does not independently verify live behavior or deployment.