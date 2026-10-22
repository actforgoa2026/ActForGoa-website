---
name: ActForGoa
description: A restrained Goan field guide with large outlined choices, upright Manrope,
  real photography, and Arc controls.
colors:
  paper: "#f7f6ee"
  green: "#193e32"
  muted: "#56675c"
  line: "#d0d8ca"
  pale: "#e9eddf"
  white: "#fffef8"
  search-focus: "#dae3cf"
  link-button-hover: "#29523e"
  choice-border: "#9faea5"
typography:
  display:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: clamp(2.25rem, 4.5vw, 3.5rem)
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 48px
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 32px
    fontWeight: 800
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  feed-lead:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 36px
    fontWeight: 750
  header-label:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 13px
    fontWeight: 650
    letterSpacing: "-0.01em"
  wordmark:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 28px
    fontWeight: 800
    letterSpacing: "-0.04em"
  record-title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 24px
    fontWeight: 750
    lineHeight: 1.35
    letterSpacing: "-0.025em"
  body:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  reading:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 18px
    fontWeight: 450
    lineHeight: 1.75
  summary:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 16px
    fontWeight: 450
    lineHeight: 1.7
  control:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.4
  search:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 18px
    fontWeight: 550
    lineHeight: 1.6
    letterSpacing: "-0.01em"
  field:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "-0.01em"
  metadata:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 14px
    fontWeight: 550
    lineHeight: 1.5
  filter-label:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 16px
    fontWeight: 650
    lineHeight: 1.4
  guide-title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: clamp(2.25rem, 3.5vw, 3rem)
    fontWeight: 800
    lineHeight: 1.14
    letterSpacing: "-0.03em"
  reading-subhead:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 24px
    fontWeight: 750
    lineHeight: 1.35
  topic-title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: clamp(2rem, 4vw, 3rem)
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.03em"
  choice:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 20px
    fontWeight: 750
    lineHeight: 1.4
  choice-phone:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 18px
    fontWeight: 750
    lineHeight: 1.4
  home-choice-phone:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 16px
    fontWeight: 750
    lineHeight: 1.4
  choice-question:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: 24px
    fontWeight: 750
    lineHeight: 1.35
    letterSpacing: "-0.02em"
rounded:
  control: 4px
spacing:
  space-2: 0.5rem
  space-3: 0.75rem
  space-4: 1rem
  space-5: 1.25rem
  space-6: 1.5rem
  space-8: 2rem
  space-10: 2.5rem
  space-12: 3rem
  space-16: 4rem
  space-20: 5rem
  space-24: 6rem
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.paper}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: 0 16px
  button-secondary:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: 0 20px
  button-ghost:
    textColor: "{colors.muted}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: 0 16px
  search-field:
    backgroundColor: "{colors.pale}"
    textColor: "{colors.green}"
    typography: "{typography.search}"
    rounded: "{rounded.control}"
    padding: 8px
  search-field-focus:
    backgroundColor: "{colors.search-focus}"
  input:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.field}"
    rounded: "{rounded.control}"
    padding: 0 12px
  input-focus:
    backgroundColor: "{colors.pale}"
  textarea:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.field}"
    rounded: "{rounded.control}"
    padding: 12px
  textarea-focus:
    backgroundColor: "{colors.pale}"
  segmented-control:
    textColor: "{colors.muted}"
    typography: "{typography.control}"
    padding: 0 12px
  segmented-filter:
    textColor: "{colors.muted}"
    typography: "{typography.filter-label}"
    padding: 0 12px
  segmented-control-selected:
    backgroundColor: "{colors.pale}"
    textColor: "{colors.green}"
  navigation:
    textColor: "{colors.green}"
    padding: 0 8px
  record-row:
    textColor: "{colors.green}"
    padding: 24px 0
  choice-link:
    textColor: "{colors.green}"
    typography: "{typography.choice}"
    rounded: "{rounded.control}"
    padding: 24px
  home-choice:
    textColor: "{colors.green}"
    typography: "{typography.choice}"
    rounded: "{rounded.control}"
    padding: 24px
  topic-filter:
    textColor: "{colors.muted}"
    typography: "{typography.filter-label}"
    rounded: "{rounded.control}"
---

# Design System: ActForGoa

## Overview

**Creative North Star: "The Open Goan Field Guide"**

ActForGoa is a restrained, practical field guide. Warm paper, forest-green ink, upright Manrope, outline icons, and clear rules make the next step easy to find. Strong headings and large outlined choices provide hierarchy without decorative imagery or bright accent fields.

The visitor chooses a topic, identifies a need, and reaches a useful next action before browsing the related directory and reading. The menu should feel as direct as a public information kiosk, with plain words and generous targets. Original photographs continue to carry local character in the discovery feed and articles. Official Arc components provide the common controls and interaction behavior.

**Key Characteristics:**

- Warm paper, forest-green text, and a restrained neutral palette.
- Upright Manrope with clear page, section, choice, and reading hierarchy.
- Large outlined topic and action controls with Lucide outline icons.
- Plain visible labels and a topic-to-need-to-action progression.
- Original local photography in discovery and reading.
- Shared Arc controls, stable text-field focus, and browsing continuity.

This direction supersedes the colourful welcome area and filled illustration experiment. Normative values come from the current implementation; source and styling are still being polished. The surface brief owns page-specific order and flow. Documentation does not establish final browser review or deployment.

## Colors

### Primary

- **Forest green** (`green`) supplies primary text, action fills, caret, selection background, and keyboard focus.
- **Link-action hover** (`link-button-hover`) is the hover fill for anchor-based primary actions.

### Neutral

- **Warm paper** (`paper`) is the page ground and primary-button text.
- **Quiet green** (`muted`) supplies supporting text, metadata, and inactive control text.
- **Soft rule** (`line`) separates records and sections and defines existing input borders.
- **Choice border** (`choice-border`) makes large outlined destinations recognisable as controls.
- **Pale leaf** (`pale`) is the search fill, selected-control fill, and input or choice hover treatment.
- **Control paper** (`white`) is the resting input and textarea surface.
- **Search focus leaf** (`search-focus`) is the search form's focused fill.

Arc aliases map background to paper, foreground and accent to green, surface to white, surface-muted to pale, and text/border roles to muted/line. They do not introduce additional palette primitives. Generic themes in the Arc foundation are not part of this surface. Sidecar tonal ramps are inspection aids only.

**The Restrained Colour Rule.** Use the documented green and neutral roles. Do not restore yellow or pink welcome fields, hero flowers, or filled pictorial illustration families.

## Typography

Manrope Variable is the only implemented family, with a generic sans-serif fallback. Page and major section headings use weight 800; record titles and choice labels use 750. Reading copy uses 450. Font synthesis is disabled.

| Role | Implemented use |
| --- | --- |
| Display | Home mission heading from the frontmatter, with a 20ch measure; 36px on phones. |
| Headline | Catalogue and article headings at 48px/800; 36px on phones. |
| Topic title | Fluid 32–48px/800 topic or action heading; 32px on phones. |
| Guide title | Fluid 36–48px/800; 36px on phones. |
| Title | Major section headings at 32px/800; 28px on phones. |
| Choice question | Need-selection headings at 24px/750; 20px for topic questions on phones. |
| Choice | Large need and action labels at 20px/750, reducing to 18px on phones. Home labels use 18px at 1150px and 16px on phones. |
| Record title / feed lead | Ordinary records use 24px/750. Mixed-feed leads use 36px/750, reducing to 32px at 850px. |
| Body / summary | General copy uses 16px. Record summaries use 16px/450 with 1.7 leading; guide summaries use 18px/550 with 1.6 leading. |
| Reading | 18px/450 with 1.75 leading and a 66ch measure on phones and desktop. Reading h2 is 32px/800 and h3 is 24px/750; phone sizes are 28px and 22px. |
| Field / control | Search entry uses 18px/550. Contact entry remains 16px. Arc controls generally retain 14px/500; topic and feed/result filters use 16px/650. |
| Metadata | Record metadata, topic text, and detail bylines use 14px/550. Compact result counts and the auto-load utility label retain 12px. |
| Header | Navigation labels use 13px/650. The upright wordmark uses 28px/800, becoming 26px in the phone header. |

**The Upright Type Rule.** Use upright text throughout, including wordmarks, quotations, labels, and numerals. Emphasis comes from size, weight, and space.

**The Reading Hierarchy Rule.** Keep reading copy at 18px on phones and desktop. Separate headings through size, weight, and space; do not reduce body text to make more content fit.

## Layout

The centred shell is at most 1320px wide. Gutters are 48px by default, 32px at 1150px, and 20px at 620px. The actual Arc SiteHeader uses its own container queries: a 96px desktop bar becomes an 80px compact bar below a 1200px container width. Header gutters are 48px, then 32px, then 20px at 620px.

Home begins with the mission, a short plain-language introduction, and search, followed by eight outlined topic controls. The intro uses 52px top and 36px bottom spacing; on phones both are 32px. Search is at most 760px wide. The topic grid uses four columns, then two at 850px and below. Desktop home targets are at least 164px tall with 24px padding; padding becomes 20px at 1150px and 16px on phones while the height remains generous.

Need-choice grids use three columns, two at 850px, and one at 620px. Their controls are at least 120px tall with 24px padding, becoming 100px with 20px padding on phones. Final action destinations use two columns, then one on phones. Breadcrumbs and a clear heading sit above choices. Related people and useful reading follow the choice or action area, separated by horizontal rules and 48px of preceding space.

Mixed discovery batches keep a 1.3:1 lead arrangement: a larger image-led record spans two rows beside two text-led records. Remaining entries use three columns with 40px gaps, then two at 850px and one at 620px. Search grids use two columns until 620px. The catalogue filter rail is 236px wide, sticky at 120px, and separated from results by 48px; at 850px it becomes a horizontal scroller above results.

Standard articles allow a 760px reading column and separate aside. Practical guides use a 780px article column with a 72px gap, reducing to 40px at 1150px and one column at 850px. Listed guides show an open desktop contents list; smaller screens use a native disclosure before the body. Two-column reference tables stack into labelled rows at 620px; wider tables retain horizontal scrolling.

**The Open Page Rule.** Content records, reading, and source context stay on the page ground with spacing and structural rules. Outlined topic and action choices are interactive controls, not a general card-container system.

## Elevation & Depth

Content, photographs, choices, the header bar, and mobile sheet have no visible surface shadows. The functional desktop navigation dropdown uses a control-paper surface, a 1px border, 4px corners, and `0 16px 32px #193e3214` shadow. The mobile sheet uses a transparent-black scrim (`oklch(0% 0 0 / .16)`).

Arc primary buttons retain their subtle hover shadow (`0 1px 2px oklch(0% 0 0 / .035)`). This is a control response, not a direction for content panels. Textarea halo values resolve to transparent.

Motion stays functional: short colour transitions, button press feedback, segmented selection, search clearing, and SiteHeader transitions. Arc fast transitions use 160ms with `cubic-bezier(.22,1,.36,1)`; search and large choices use 120ms ease-out fill transitions. Components honour reduced motion, and the page disables CSS transitions, animations, and smooth scrolling for that preference. Do not add decorative page entrances or photograph zoom.

## Shapes

Controls use a 4px radius. Photographs and editorial structures remain square. Records begin with a horizontal rule and 24px top space, with no enclosing border or filled shell. Large destination controls have a complete 1px outline; selected and hover states are quiet fills. No single edge acts as decoration.

**The Structural Line Rule.** Horizontal rules may separate records or sections; complete borders may identify controls. Never add decorative side stripes to content containers.

## Components

### Topic, need, and action controls

Use the shared outlined choice treatment for topic navigation, need selection, and next actions. Keep the whole surface a real link with a visible label and directional icon. Labels name a recognisable topic or action, such as “Waste & recycling”, “Get extra rubbish collected”, or “Report illegal dumping”. Optional small text explains an external destination as “Opens the official service”. Downloads use the download icon; external actions use the external-link arrow.

`TopicIcon.tsx` maps the shared Lucide outline family to topics and actions. Use a 1.7 stroke with no filled illustration substitute. Home icons are 44px, becoming 40px on phones; topic-page and guide-heading icons are 52px, becoming 40px on phones. Need-choice icons use 40px, and catalogue filter icons use 28px. Adjacent visible labels provide the accessible names; decorative icons are hidden from assistive technology.

The topic route is `/topics/:slug/:actionId?/:choiceId?`. It supports a topic, a need, and an optional further choice before the final action links and short steps. Breadcrumbs expose the chosen path. The related directory and reading are below the choice/action area, with links to complete filtered results. Invalid paths offer a clear return to topic selection. Exact topic order and route content belong to the surface brief and `topic-flows.ts`.

**The Choice First Rule.** Present the next understandable choice before directory records and reading. A visitor should not need to interpret a result list to discover what action to take.

**The Picture and Label Rule.** Pair outline icons with plain visible labels. Icons support recognition but do not replace accessible names or translated content.

### Arc buttons and navigation

Use the installed Arc Button for button actions. Primary pairs green with paper; secondary uses the white control surface, a line-colour border, and green text; ghost is transparent with muted text and gains pale fill and green text on hover. Standard small, medium, and large heights are 44px, 48px, and 52px. Primary hover uses opacity 0.91 and press uses 0.84. Press scaling respects reduced motion.

Anchor actions keep real routing and link behavior. Their primary treatment has a 52px minimum height and 12px by 20px padding. Links, buttons, and comparable non-text controls use a 2px green keyboard outline with a 3px offset.

The official Arc SiteHeader keeps the nine categories Home, Take action, Blog, Inspiring stories, Resources, About, Work with us, Volunteer, and Community, plus Search. Take action and About disclose destinations; internal links use React Router. Desktop targets are 44px and current navigation has a 2px underline. The compact sheet retains the same destinations, locks background scrolling, and confines Tab focus to visible header controls. Escape restores trigger focus; route changes dismiss menus.

### SearchField, Input, and Textarea

Search uses a pale borderless outer form with 8px padding, a borderless field, and a green large Button. Focus changes the outer fill to search-focus. A permanent 44px clear slot prevents width shifts; clearing returns focus without scrolling. The field is labelled, and submit keeps its accessible name when visible text is hidden on compact screens.

Contact Input and Textarea retain their 1px border and white resting fill. Focus or hover changes the fill to pale without adding a new border or visible ring. Inputs are at least 48px tall with 12px horizontal padding. Textareas use 12px padding, a 110px minimum height, and vertical resize. The reason selector remains native; required validation is native.

**The Stable Focus Rule.** Text-entry focus changes fill and caret without a new border, visible ring, or size change. Links and buttons retain the Arc keyboard outline.

### SegmentedControl and filters

Use Arc SegmentedControl for result type, Grid/List, and discovery kind filters. The borderless track scrolls within its width. Selected items use pale fill and green text without changing weight. Items have a 44px minimum height and 12px horizontal padding, reducing to 10px at 380px. Arrow keys, Home, and End select and focus options; only the selected option is in the tab sequence. Overflow fades signal more options, and selection scrolls into view. Keyboard and reduced-motion selection changes are immediate.

Catalogue topic filters use Arc ghost buttons with 28px outline icons, 16px/650 labels, and a 60px minimum height. A selected filter has pale fill. A topic-only catalogue route may show the same need choices above its results.

### Records, source context, and browsing continuity

Records use muted metadata, a large linked title, a readable summary, and topic text. Normal image previews use a 1.6 aspect ratio; the first mixed-feed lead uses 1.4, and companion images are hidden. General grid summaries clamp to three lines and list summaries to two. Community descriptions have a five-line allowance and show all topics. Source publication dates remain useful historical context; internal crawl dates do not belong in the primary reading flow.

Original sources, useful links, and contact availability cautions remain available. Prepared-email feedback follows a rule and plainly says nothing has been sent. Presentation changes must not suggest current verification, guaranteed service availability, or successful delivery.

**The Source Proximity Rule.** Keep useful historical context and practical cautions near the information they qualify. Make detailed audit records optional; a prepared email is not a sent message.

The router uses ScrollRestoration after catalogue data is available. Search filtering and resubmission use `preventScrollReset`. Result layout and extent are cached per history entry. Records opened from catalogues, discovery, or topic routes retain a history-based return; direct entry retains a section link. The discovery feed also restores its kind, extent, and auto-load preference.

**The Browsing Continuity Rule.** Preserve scroll position when filtering or resubmitting a search. Returning to a catalogue history entry restores its expanded results and chosen layout.

### Practical guide presentation

Five listed practical guides remain authored drafts in the source data. Reader-facing presentation leads with the topic icon, title, summary, and useful content. `guide-presentation.ts` removes internal draft banners and editorial check codes from listed guides, rewrites relevant cautions as plain “Before you act” guidance, and simplifies internal research language. It does not establish legal review or current service verification.

Useful cautions, source citations, official-source links, and original source files remain intact. An optional “About this guide” disclosure after the body explains that review is continuing and links to detailed review notes. Source and verification registers remain available as supporting documents. The desktop contents list and mobile disclosure use the reader-facing headings. Templates, download/correction actions, and related guides remain in the aside. Two-column tables stack on phones while preserving semantics.

**The Reader Language Rule.** Show the person what to do, what to check, and where to go. Keep crawl dates, editorial review codes, and research-process language out of the primary guide flow while retaining useful cautions and optional audit detail.

### Mixed discovery feed and original photography

The current feed has 533 eligible entries: 242 resources, 138 stories, 104 organisations, and 49 volunteer contacts. Five resources are the listed practical guides; supporting registers are not listed feed entries. This is a catalogue snapshot, not a product limit. Each eligible record appears once in a deterministic mixed sequence.

The feed starts with 12 entries and appends batches of 12. Auto-loading observes a 400px margin and runs only while the document is visible. Pause/Resume and manual loading remain available. Manual loading announces additions and focuses the first new title without scrolling. Kind changes reset the visible extent. Periodic topic links enter the topic-choice flow. Batch spacing is 56px, reducing to 40px on phones.

Original article and story images come from the existing archive and retain source/rendition provenance. The first restored image is the lead; additional images form a two-column gallery with 24px gaps and natural height, becoming one column at 620px. Source alternative text can appear as a 14px muted caption. Missing original images remain reported; do not fabricate replacements. The home introduction has no hero photograph or decorative flower; photography continues in the feed and articles.

### Public record presentation

The route loader passes catalogue data through `publicRecord` before search, feed, cards, and reading. Presentation clears structured phone fields, removes phone/WhatsApp actions, and sanitises recognised numbers in titles, summaries, prose, document text, locations, image descriptions, and link labels. The original catalogue and archive retain their fields. This is presentation behavior, not deletion or access control for downloadable originals.

Community descriptions use original non-heading paragraphs and prioritise actual work over registration boilerplate, with an honest missing-description fallback. Do not invent biographies. Keep practical availability cautions without exposing internal processing language.

## Do's and Don'ts

### Do

- Do use restrained green and neutral roles, upright Manrope, and Lucide outline icons.
- Do make topic, need, and next-action choices large and plainly labelled.
- Do keep waste first among the eight home topics and treat wildlife help as one relevant need within its topic.
- Do preserve original photographs in discovery and articles.
- Do keep reading copy at 18px and provide a strong, consistent heading hierarchy.
- Do preserve Arc focus, keyboard behavior, search, feed controls, and history restoration.
- Do keep practical cautions and source access while making detailed audit material optional.
- Do preserve original source files and keep phone data out of record presentation.

### Don't

- Don't restore bright yellow/pink welcome fields, hero flowers, or filled illustration families.
- Don't make snake rescue the default emphasis of the homepage or all-topic navigation.
- Don't turn content records into enclosed panels because topic choices have borders.
- Don't use serif, italic, or oblique type, decorative side stripes, or eyebrow labels.
- Don't replace visible labels with icons or rely on colour alone for meaning.
- Don't expose crawl dates, editorial check codes, or research-process language as primary reader guidance.
- Don't invent biographies, photographs, contact details, service availability, or message-delivery claims.

Evidence: current App, TopicPage, topic-flows, TopicIcon, RecordCard, PracticalGuide, guide-presentation, public-record, stylesheet, Arc components, discovery state, and original-image provenance. Earlier colour-hierarchy captures describe a superseded direction. Current source remains in polish; this documentation pass makes no final visual, interaction, or deployment claim. Sidecar specimens are framework-free appearance examples, not substitutes for the React behavior.
