---
name: ActForGoa
description: A calm Goan field guide in warm paper, forest green, upright type, and real local photography.
colors:
  green: "#163f36"
  paper: "#f7f7ee"
  ink: "#203d34"
  muted: "#617167"
  line: "#d9ded2"
  yellow: "#ecd883"
  pale: "#e8eddf"
  white: "#fffef8"
  yellow-hover: "#ddc467"
  focus: "#b37d18"
  source-surface: "#e9eddf"
  summary-ink: "#5c6c60"
  topic-ink: "#64765f"
  footer-surface: "#e8ebdf"
typography:
  display:
    fontFamily: "'Literata Variable', serif"
    fontSize: "49px"
    fontWeight: 480
    lineHeight: 1.18
    letterSpacing: "-1.8px"
  headline:
    fontFamily: "'Literata Variable', serif"
    fontSize: "41px"
    fontWeight: 480
    lineHeight: 1.22
    letterSpacing: "-1.2px"
  title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "26px"
    fontWeight: 600
    letterSpacing: "-0.7px"
  card-title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "18px"
    fontWeight: 650
    lineHeight: 1.45
    letterSpacing: "-0.4px"
  body:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.8
  reading:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.95
  label:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "12px"
    fontWeight: 650
  search:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "14px"
    fontWeight: 400
  mobile-search:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 400
  mobile-summary:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.85
  metadata:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "10px"
    fontWeight: 400
    lineHeight: 1.5
  mobile-metadata:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  field: "4px"
  action: "5px"
  notice: "6px"
  search: "7px"
  card: "8px"
  spotlight: "10px"
  hero: "12px"
  chip: "20px"
spacing:
  compact: "8px"
  small: "12px"
  control: "16px"
  inset: "20px"
  content: "24px"
  group: "30px"
  section: "40px"
  wide: "48px"
  section-large: "56px"
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.action}"
    padding: "12px 19px"
  button-outline:
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.action}"
    padding: "12px 19px"
  button-search:
    backgroundColor: "{colors.yellow}"
    textColor: "{colors.green}"
    rounded: "{rounded.field}"
    padding: "0 16px"
  button-search-hover:
    backgroundColor: "{colors.yellow-hover}"
  search-field:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.search}"
    rounded: "{rounded.search}"
    padding: "7px 8px 7px 19px"
  text-field:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    typography: "{typography.search}"
    rounded: "{rounded.field}"
    padding: "13px"
  navigation:
    textColor: "{colors.ink}"
    padding: "12px 0"
  starter-chip:
    textColor: "{colors.paper}"
    rounded: "{rounded.chip}"
    padding: "7px 10px"
  record-card:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "23px"
  grouped-result:
    textColor: "{colors.ink}"
    padding: "24px 0"
  source-note:
    backgroundColor: "{colors.source-surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.notice}"
    padding: "17px 20px"
---

# Design System: ActForGoa

## Overview

**Creative North Star: "The Goan Field Guide"**

ActForGoa feels like a useful local field guide: calm, welcoming, and grounded in the place and people it serves. Warm paper and deep green give practical information a steady home. Upright editorial headings add character, while clear humanist text keeps searching, scanning, and reading straightforward.

Real Goan photographs supply the visual richness. Open lists, restrained borders, and pale green surfaces organise the information without making every section a card. Controls are simple and gently rounded. Source dates, historical context, and contact caveats sit close to the material they qualify.

**Key Characteristics:**

- Warm paper, forest green, and restrained sun yellow.
- Upright Literata headings with Manrope controls and body text.
- Real local photographs, with their source context retained.
- Open index rows, quiet cards, and generous reading space.
- Visible source context and honest interaction states.

This is a scan-mode record of the implemented system in `src/App.tsx` and `src/styles.css`, documented on 22 October 2026 after the finish review. The agreed language comes from `PRODUCT.md` and the chosen direction. Page-specific composition and modes remain in `.impeccable/surfaces/src-app-tsx.md`. Tokens above are normative; the role descriptions below explain their application.

## Colors

The palette combines vegetal darks with warm off-whites and a small amount of sun yellow. Source CSS uses hex colours; those exact values are retained in the frontmatter.

### Primary

- **Forest green** (`green`): the search-led introduction, primary action fills, selected topic filters, and strong navigational details.
- **Green ink** (`ink`): the default text colour, including open-list titles and page copy.

### Secondary

- **Sun yellow** (`yellow`): the search submit action. `yellow-hover` is its darker hover state.
- **Ochre focus** (`focus`): the visible keyboard outline, distinguished from ordinary selection.

### Neutral

- **Warm paper** (`paper`): the page ground and reversed text on green.
- **Card paper** (`white`): cards and form controls, slightly separated from the page ground.
- **Pale leaf** (`pale`): selected view controls, supporting panels, and the story spotlight.
- **Source leaf** (`source-surface`): source and verification notices.
- **Quiet green** (`muted`): secondary text and metadata; `summary-ink` and `topic-ink` preserve the existing card-specific text roles.
- **Soft rule** (`line`): card borders, index dividers, and control boundaries.
- **Footer paper** (`footer-surface`): the quiet full-width ending of the page.

**The Functional Accent Rule.** Use yellow for the search action and green for primary actions or selected filters. Use pale surfaces to group supporting information; do not use colour to imply that a contact is currently verified.

The sidecar includes synthesised tonal ramps for inspection in the design panel. They are visual aids, not additional application colours or an adopted palette scale.

## Typography

**Display font:** Literata Variable, with the implemented generic serif fallback.

**Body and control font:** Manrope Variable, with the implemented generic sans-serif fallback. The root disables synthetic font styling. No separate mono family is used.

The pairing is editorial but practical. Literata carries mission, page, and reading titles; Manrope carries section headings, record names, metadata, controls, and long-form body text. This is an observed hierarchy, not a mathematical modular scale.

### Hierarchy

| Role | Application |
| --- | --- |
| `display` | Home mission heading. Breakpoint sizes progress through 35px, 38px, 42px, and the base token; large screens use 54px. |
| `headline` | Catalogue, About, and contact page headings; phone versions use 32px. Reading detail titles use 42px with a 1.24 line-height, then 32px with 1.28 on phones. |
| `title` | Main section headings. Phone section headings use 22px; grouped result headings use 23px, reduced to 21px at 850px. |
| `card-title` | Grid record names. At 850px the intermediate layout uses 16px; phone cards use 19px. Open-list titles use 20px, then 18px on phones. |
| `body` / `reading` | General copy and reading paragraphs. Reading paragraphs have a 72ch maximum measure and 22px trailing space; phone reading text is 14px. |
| `label` | Standard action labels. Search submit labels are 13px at weight 700. |
| `search` / `mobile-search` | Search-entry text, including the final 850px override. Contact fields use 14px on larger screens and 16px at 620px. |
| `metadata` / `mobile-metadata` | Record type and location. The mobile role is also the final size for the documented source, status, byline, topic, filter, and footer roles. |
| `mobile-summary` | Card summaries at 850px and below. Related supporting copy and verification notices share this size while retaining their existing line-heights. |

The wordmark uses Manrope with a heavy main weight (850), a lighter “for” (430), tight tracking (-1.4px), and an ochre full stop. Its base size is 31px and phone size is 28px.

**The Upright Type Rule.** Keep every letter upright, including the wordmark, headings, quotes, labels, and decorative text. Use weight, size, and space for emphasis.

**The Mobile Reading Rule.** At widths up to 850px, keep search text at 16px, explanatory summaries and verification notices at 14px, and the documented status, byline, metadata, filter, and provenance roles at 12px. Let content grow vertically.

## Layout

A centred shell has a maximum width of 1280px. Default horizontal gutters are 48px per side; they become 28px at 1150px and 18px at 620px. Reused spaces are recorded in the frontmatter; the implementation also uses component-specific padding and gaps where content needs them.

| Breakpoint | Implemented response |
| --- | --- |
| At least 1500px | More room for introduction copy, a larger mission heading, and a taller photograph pairing. |
| Up to 1150px | Narrower shell gutters, smaller introduction padding, and reduced inter-column gaps. |
| Up to 850px | Catalogue filter rail becomes a horizontal scroller. Reading detail becomes a single main column. The topic index has two columns. Final search and supporting-text size overrides apply. |
| Up to 620px | Navigation becomes a disclosed vertical menu. Introduction and story photograph pairs stack. Card/result grids, contact fields, and participation links become single-column. |

The home resource grid uses three columns with a 25px base gap; result grids use two columns with a 20px gap. Phone grids use one column. The catalogue has a 218px topic rail and a flexible results column with a 44px base gap. A later source rule keeps that rail width at 218px until the single-column breakpoint; do not infer a 200px final rail from the earlier responsive declaration.

Reading detail allocates up to 760px to the main article with a separate supporting column. At narrower widths the aside follows the article. Long links and contact details wrap rather than widen the page. Horizontal overflow is intentional only for the compact filter rail and result-type controls.

Default queried “Everything” results are grouped as People & organisations, Guides & reading, Stories & projects, and About & action. Empty groups are omitted. Groups follow the rank of their first match; ranking within each group is preserved. Each group exposes its total match count. Group spacing is 44px, reduced to 36px at 850px. Directory, library, stories, and filtered-type views retain the regular grid/list treatment.

**The Source Proximity Rule.** Keep the source link, publication context, or availability caveat beside the record or contact it qualifies. Do not hide essential context to preserve a card height.

## Elevation & Depth

Depth is chiefly tonal: card paper on warm paper, pale support surfaces, and the dark green introduction. Cards, notices, buttons, and search fields have no box shadow. Photograph crops and light borders define their edges.

The expanded phone navigation has the only implemented shadow (`0 15px 25px #173c3212`). It sits above the page at z-index 20. The keyboard skip link sits above that layer at z-index 100 when focused.

**The Quiet Depth Rule.** Cards and content surfaces remain shadowless. The sole implemented shadow identifies the expanded mobile navigation as a layer above the page.

Motion is restrained. Card photograph hover scales the image to 1.025 over 250ms using `cubic-bezier(.16,1,.3,1)`. Other documented hover feedback is immediate colour, underline, or brightness. Reduced-motion preference disables animations and transitions and restores automatic scroll behavior. Do not infer a broader motion system from the single image transition.

## Shapes

Controls use modest corner rounding: the named field, action, notice, and search tokens distinguish their forms. Cards use the card radius, larger photograph pairings use spotlight or hero rounding, and starter/active-filter chips use the chip radius. The phone hero and spotlight both use the card radius.

Full card borders are fine and quiet (1px). Open result rows use horizontal rules and square corners. The topic index also uses horizontal dividers. Active desktop navigation and result-type controls use a short bottom underline; this represents selection rather than decoration along a container side.

**The Structural Line Rule.** Use a full border or a horizontal divider to express a real boundary. Never place a decorative accent stripe along a container edge.

## Components

### Buttons

Plain, compact actions with enough space to recognise their purpose. Standard actions use the `action` radius, a minimum height of 48px, the recorded padding, and an 18px label/icon gap. Green actions pair `green` and `paper`; outline actions stay transparent with a `line` border. Their hover filter is `brightness(1.12)`.

The sun-yellow search action is a separate variant: a minimum height of 47px, the `field` radius, 13px label text, and the recorded hover colour. On compact layouts its visible text hides while its accessible name remains. The phone search control is at least 44px high in catalogue forms; the hero has its own 43px implementation.

All keyboard-focusable controls use a 3px ochre outline with a 4px offset. Search input focus keeps its source-specific zero offset inside the shared field. Disabled buttons use opacity 0.55 and a waiting cursor; no additional error or pressed styling is defined for general buttons.

### Inputs / Fields

The search input and submit action live within one card-paper surface, using the `search` radius and a subdued green border. The catalogue search has a minimum height of 64px and an 850px maximum width; the hero version fills its own text column and removes the border. Input labels remain accessible even when visually hidden.

Contact inputs, selects, and textareas use the `field` radius, 13px padding, a 1px green-grey border, and a 47px minimum height. Labels sit above controls. Textareas resize vertically. Required states use native browser validation; a bespoke inline validation design has not been implemented.

### Navigation

The desktop header is a quiet horizontal row: wordmark on the left, text links and a bordered participation link on the right. The active destination receives a bottom line. Hover shifts link colour; keyboard focus remains explicit. At 620px a labelled 44px menu control reveals vertical links. The active phone destination uses heavier text instead of the desktop underline. Route changes close the menu.

### Chips and filters

Starter queries are small outlined pills on the green introduction, each ending with a directional arrow. Hover adds a lighter green fill and border. They are ordinary navigational links. Selected catalogue topic buttons use the green/paper pairing, while unselected hover uses pale leaf. An active filter becomes a pale chip with a remove control. Result-type buttons use a bottom line and weight change; the grid/list switch uses a pale selected background.

### Record cards and open rows

Cards use card paper, the `card` radius, a full border, and 23px base content padding. Type/location metadata precedes the title. Summaries are clamped to three lines; topic and forward action sit after a divider. Optional images fill their crop with `object-fit: cover`; base image height is 190px and phone height is 185px.

The list variant removes the fill and full outline, uses horizontal rules, and gives content 24px vertical padding. Its summaries are clamped to two lines with a 75ch maximum measure. Phone rows use 21px vertical padding. Contact rows can expose a telephone action and a nearby historical-source caveat. The grouped answer adds headings and counts above these same records; it does not introduce another card layer.

### Source and feedback surfaces

Source notices use a pale whole-surface fill, the `notice` radius, and the recorded padding. Strong lead text introduces the context. Verification notices follow the same quiet shape. Neither uses a side accent stripe.

Search progress and fallback messages appear near the result count. Empty results offer a broader search, filter removal guidance, and direct recovery links. Prepared-email feedback says that nothing has been sent and exposes the email-app action. Loading uses quiet pale placeholders without animation.

**The Honest State Rule.** Keep search progress, fallback, empty results, historical contact status, and prepared-email feedback explicit. A prepared email is not a sent message.

### Photography and editorial pairings

The river and community photographs retain their documentary character. Crops fill their allotted surface without decorative overlays or invented material. The river image and community story provide two different kinds of local evidence. The story heading begins directly, with no decorative eyebrow. New photography must retain provenance and appropriate alternative text; decorative duplicate card images remain hidden from assistive technology as in the implementation.

The sidecar contains ten scoped HTML/CSS specimens derived from these components. They demonstrate appearance and CSS interaction states without a React runtime; application navigation, filtering, search ranking, and form submission remain the responsibility of the real components.

## Do's and Don'ts

### Do

- Do preserve the warm paper, forest green, and real local photography.
- Do use the existing upright type families and let long content reflow.
- Do preserve the final mobile search, supporting-text, and metadata sizes.
- Do keep source context, dates, and contact caveats readable beside the relevant content.
- Do provide visible keyboard focus and retain reduced-motion behavior.
- Do use plain dividers and whole-surface fills for real structure.

### Don't

- Don't use italic or oblique styling anywhere, including wordmarks or quotations.
- Don't add decorative side stripes to cards, notices, quotes, or other containers.
- Don't replace local photography with fabricated scenes or decorative imitation material.
- Don't shrink mobile explanatory or provenance text to preserve a desktop composition.
- Don't add decorative eyebrow labels above the existing headings.
- Don't imply contact verification, message delivery, or service availability that the interface has not established.

Documentation evidence: current component and stylesheet source, the direction files, `reports/DESIGN-REVIEW.md`, and the supplied desktop, mobile, and grouped-search captures. The review's final ship disposition covers its three scored fixes. This documentation pass does not establish independent browser interaction, deployed behavior, archive completeness, or the current accuracy of contacts. Sidecar specimens have been structurally validated; they were not independently browser-rendered in this pass.
