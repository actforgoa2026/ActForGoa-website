---
name: ActForGoa landing
description: A spacious Goan source-library landing page in warm paper, forest ink, upright Manrope and stippled illustration.
colors:
  ink: "#193e32"
  action-hover: "#2a5544"
  lime: "#d5f878"
  paper: "#f7f6ee"
  white: "#fffef8"
  muted: "#54685b"
  line: "#d4dacd"
  navigation: "#efefe5"
  leaf: "#e9eddf"
  control-hover: "#e7ece3"
  selected: "#e9efdf"
  question: "#eff1e9"
  field-focus: "#eef2e4"
typography:
  display:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "clamp(70px, 7.6vw, 118px)"
    fontWeight: 450
    lineHeight: 1.05
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "clamp(48px, 5.3vw, 80px)"
    fontWeight: 500
    lineHeight: 1.04
    letterSpacing: "-0.04em"
  title:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "21px"
    fontWeight: 650
    lineHeight: 1.3
    letterSpacing: "-0.025em"
  body:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "17px"
    fontWeight: 500
    lineHeight: 1.6
  answer:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "14px"
    fontWeight: 500
    lineHeight: 1.75
  label:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "15px"
    fontWeight: 650
    lineHeight: 1.4
  input:
    fontFamily: "'Manrope Variable', sans-serif"
    fontSize: "16px"
    fontWeight: 500
    lineHeight: 1.4
rounded:
  source-link: "6px"
  tab: "9px"
  compact: "12px"
  action: "14px"
  composer: "17px"
  navigation: "18px"
  answer: "22px"
  resource: "26px"
  pill: "100px"
spacing:
  space-2: "8px"
  space-3: "12px"
  space-4: "16px"
  space-5: "20px"
  group: "24px"
  panel: "28px"
  inset: "32px"
  column: "60px"
  section-phone: "80px"
  section-desktop: "135px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.action}"
    padding: "15px 22px"
    height: "52px"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
    textColor: "{colors.paper}"
  button-light:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.action}"
    padding: "15px 22px"
    height: "52px"
  button-light-hover:
    backgroundColor: "#e8eddd"
    textColor: "{colors.ink}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "46px"
  example-tab:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.tab}"
    padding: "11px 12px"
    height: "44px"
  example-tab-selected:
    backgroundColor: "{colors.selected}"
    textColor: "{colors.ink}"
  source-link:
    textColor: "{colors.ink}"
    rounded: "{rounded.source-link}"
    padding: "9px"
    height: "44px"
  navigation:
    backgroundColor: "{colors.navigation}"
    textColor: "{colors.ink}"
    rounded: "{rounded.navigation}"
    padding: "11px 14px 11px 24px"
    height: "64px"
  answer-window:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.answer}"
  resource-preview:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.resource}"
    padding: "12px 32px 35px"
  question-composer:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.composer}"
    padding: "13px 14px 13px 23px"
    width: "680px"
  question-input:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.input}"
    padding: "10px 0"
---

# Design System: ActForGoa landing

## Overview

**Creative North Star: "Goa's knowledge, in the open"**

The landing page gives local knowledge room to speak. Warm paper, forest ink and upright Manrope create a spacious editorial surface; fine stippled Goa illustrations add a recognisable sense of place. Large headings and concrete explanations lead to an existing AI service, original documents, practical guides and local organisations.

The user-pinned Butter reference supplies the floating navigation, generous intervals and staged scroll choreography. ActForGoa supplies the content, palette, artwork and actual product screenshots. Soft depth belongs to the product preview, source sheets and interactive surfaces. Lime marks selected narrative passages; it is not a general backdrop for every component.

**Key Characteristics:**

- Warm paper and forest ink, with deliberate lime passages.
- Upright self-hosted Manrope and large, lightly weighted display type.
- Natural illustration proportions, open compositions and generous section spacing.
- Actual Arc buttons, anchor buttons and input with preserved semantics and provenance.
- Visible source links, explicit illustrative examples and a complete reduced-motion flow.

This system is scoped to `landing/`. The main application keeps its separate root `DESIGN.md` and Figtree system. The chosen surface sequence, publication scope and verification state live in `.impeccable/surface.md`. This is a source-based documentation pass dated 30 October 2026; it does not certify deployment or final rendered acceptance.

## Colors

### Primary

- **Forest ink** (`ink`) is the main text, primary-action fill, dark narrative surface and footer ground.
- **Deep leaf hover** (`action-hover`) gives the primary action a restrained response to pointer hover.

### Secondary

- **Bright lime** (`lime`) separates the source promise and action passage from the continuous paper ground. It also supplies the footer wordmark dot and motion-control hover.

### Neutral

- **Warm paper** (`paper`) is the page ground and text on dark surfaces.
- **Raised paper** (`white`) identifies answer examples, the product preview and the closing composer.
- **Quiet green** (`muted`) supports descriptions without introducing a neutral grey voice.
- **Soft rule** (`line`) marks genuine boundaries between sections, rows and control regions.
- **Navigation paper** (`navigation`) is the floating header's solid, lightly differentiated surface.
- **Pale leaf** (`leaf`) is the resource section and product-preview toolbar ground.
- **Control leaf** (`control-hover`) is the Arc ghost-control hover fill.
- **Selected leaf** (`selected`) marks the chosen example question.
- **Question paper** (`question`) separates a question from its answer.
- **Focused paper** (`field-focus`) identifies focus within the closing composer.

The source stylesheet contains a few local illustration, document and border colours. Those do not expand the reusable palette. Sidecar tonal ramps are generated inspection aids, not additional approved UI colours.

**The Contrast Pair Rule.** Place forest text on paper or lime, and paper text on forest. Keep the primary action easy to distinguish from its surrounding surface.

## Typography

Manrope Variable is loaded from the local `@fontsource-variable/manrope` package in `src/main.tsx`. The fallback is sans-serif; font synthesis is disabled. Body copy defaults to weight 500, with the display headline at 450 and selected titles and actions at 650. The wordmark uses its own heavier weight.

The frontmatter records the recurring roles. The hero's display scale is a deliberate part of the pinned reference; it is not a new global type scale for the application. The large Ask, Check and Act headings reach `clamp(110px, 14vw, 210px)` within their dedicated narrative panels. Main section headings use the headline role; the live product introduction has a smaller `clamp(44px, 4.3vw, 64px)` heading.

At 599px and below, the current hero uses `clamp(34px, 10.2vw, 58px)` at weight 500 with 1.08 leading. Common section headings become 44px; answer prose remains 14px with 1.75 leading. The closing input uses 16px on phones. Compact source-sheet labels and navigation metadata are implementation details, not a body-copy standard. Answer prose is bounded to 65ch and the FAQ to 62ch.

**The Upright Type Rule.** Use upright type everywhere. Emphasis comes from weight, size, spacing and position; never italic or oblique styling.

**The Concrete Copy Rule.** Headings and actions say what the visitor can ask, read, find or do. Do not add eyebrow labels, provider-brand claims or small abstract fragments around them.

## Layout

The desktop page is a continuous full-width composition with a recurring 6.6vw gutter and generous section intervals. The default section spacing is recorded in the frontmatter. Supporting two-column sections use a `.9fr / 1.3fr` split with a 60px gap; the example pairs an illustration with a `1fr / 2.15fr` answer area. Resource selection pairs a `1.05fr / 1fr` accordion and preview. These ratios belong to this surface, not the application shell.

At 1200px and below, gutters and column gaps tighten. Below 900px the product preview, secondary links and FAQ stack, the hero becomes content-height, and pinned narratives become ordinary vertical sections. The resource pair stacks at 599px. Phone sections use 22px gutters and the header uses 16px side offsets. The closing composer is bounded to 680px and shrinks with the viewport.

The header floats 24px from the desktop top. The main navigation is a left group and the primary action a right group. After 180px of scrolling, desktop link width collapses while the menu button remains available. The desktop links are removed below 900px; the menu panel provides their destinations. The footer uses open columns and one structural closing rule.

**The Natural Proportion Rule.** Preserve raster width-to-height relationships and motif aspect ratios at every breakpoint. Panoramas may extend beyond the viewport and crop at the edges; they must not stretch. The AI screenshot uses its original 16:9 ratio with `object-fit: contain`.

## Elevation & Depth

The page combines flat reading areas with soft, offset shadows on objects that intentionally sit above the paper. The navigation, answer window, product screenshot and source sheets each have their own elevation. Regular reading and accordion rows use spacing and horizontal rules instead of separate raised cards.

### Shadow Vocabulary

- **Floating navigation:** `0 5px 25px #193e3205` keeps the header light.
- **Expanded menu:** `0 18px 40px #193e3226` separates the open menu from the page.
- **Answer window:** `0 28px 60px -15px #193e3220` lifts the example as one product-like object.
- **Product preview:** `0 30px 65px #193e3220`, rising to `0 35px 65px #193e3230` on hover.
- **Source sheet:** `0 25px 40px #193e3215` separates the fanned documents.
- **Composer:** `0 14px 30px #193e3208` marks the final place to enter a question.
- **Map preview:** `0 20px 55px #00000026` separates the real satellite-map screenshot from its forest section.

Scroll choreography uses GSAP and ScrollTrigger, with Lenis smoothing only while motion is enabled. Desktop source panels pin for a staged statement, document fan and answer reveal; the Ask, Check, Act passage scrolls horizontally. The shared CSS easing is `cubic-bezier(.16,1,.3,1)` and Arc feedback uses `cubic-bezier(.2,0,0,1)` with 160ms colour transitions and an 80ms press interval. Arc owns its own press and label motion.

**The Complete Static Flow Rule.** Reduced motion and the persistent Pause motion preference expose every narrative section in document order. Disabling animation must never hide the source fan, example answer or later journey panels.

## Shapes

Corners distinguish interaction scale. Actions, tabs and source links have compact curves; answer and resource surfaces are broader. The wordmark and landscape remain open on the page. The source-sheet corners and slight rotations support the paper metaphor without making all content into documents.

The motif sprite uses separate natural regions: palm and cow keep a `.892857` aspect ratio; temple and wave keep `1.136364`. Do not force these organic forms into equal squares. The panorama retains its source proportions; the generated motifs and panorama are decoration, not evidence of a specific place.

**The Structural Line Rule.** Full control borders and horizontal section rules convey structure. Never use a decorative accent stripe along one side of a content block.

## Components

### Arc actions and example controls

`Button`, `ButtonLink` and `Input` in `src/arc/` are copied from the existing installed Arc sources. `src/arc/PROVENANCE.md` records registry origins and inherited changes. `ButtonLink` retains native anchor semantics for these external destinations and shares the Arc button styles and press behavior. The local action treatment supplies forest fill, paper text, its compact curved shape and an arrow icon. Hover lifts the action slightly; disabled states and reduced-motion handling remain owned by the component.

Ghost buttons drive the menu, examples, resources, FAQ and motion preference. Example buttons expose selection through `aria-pressed`; resources and FAQ expose their expanded state with `aria-expanded` and `aria-controls`. The copied source also supports variants not mounted here. Do not promote unmounted variants into the landing palette or claim this page implements an Arc menu or accordion component: those compositions use Arc Button primitives.

### Floating navigation

The upright wordmark sits beside visible desktop links and an Arc icon button. An expanded forest menu uses large, divided destination rows. Escape closes the menu and returns focus to its trigger. Keep its accessible labels, expanded state and control relationship intact. The main AI action stays visible in the separate right group as desktop links collapse. At 360px and below, its visible label becomes “Ask AI” while its accessible name remains “Ask ActForGoa AI”; the target retains a 44px minimum height.

### Illustrative answer window and source links

A single raised paper window contains example selection, question, answer, nearby source links and the next action. The visible footer reads “Illustrative walkthrough · explore the real sources.” Each example links to the research library and an existing topic destination; these are useful routes, not fabricated citations to a generated answer. Selection updates the answer within a polite live region.

Source links are compact outlined anchors with an icon and external-direction arrow. They wrap as a group and normally use a 44px minimum target. The compact answer in a short desktop viewport reduces source/action targets to 36px. This existing compact exception is documented, not certified as a new accessibility standard.

**The Source Proximity Rule.** Keep source links and uncertainty beside the claims they qualify. Distinguish illustrative examples, real product screenshots and generated decoration in both visible copy and provenance.

### Satellite map showcase

The map section uses forest ink as its ground, paper headings and a light primary action. “See how Goa is changing.” introduces comparison across two dates and AI-assisted investigation of tree cover, wetlands and land use. The concise caveat remains adjacent: the analysis is experimental, clouds and image resolution limit visibility, and findings require review and confirmation on the ground.

The real `/map` screenshot is a single linked image at its original 1440×1000 proportions (`36 / 25`), bounded to 1160px. It carries the map provider attribution within the captured interface. Its radius is 22px on desktop and 10px at 700px and below; the surrounding section stacks using the existing heading grid. This is a product preview, not a fabricated change analysis or a field-verified finding.

### Resource and FAQ disclosures

Resources use three open rows with a selected description and adjacent illustrated preview. Exactly one resource is selected; the preview follows that selection. The FAQ allows its active answer to close. Horizontal rules convey grouping, while icons supplement the visible labels. Preserve the current direct links and the cautions about historical material, extraction gaps, interpretation and contact availability.

### Closing question composer

The final form combines an installed Arc Input, search icon and Arc submit button in the landing's broad composer surface. The input retains an associated, visually hidden label, required state and 2000-character maximum. Submission opens the existing `/ask` route with `q` and `start=ai`; an empty trimmed value disables the action. The form does not generate an answer in the landing page. Focus changes the outer paper fill; the field remains borderless within that composition.

### Evidence and limits

Inspected implementation: `src/App.tsx`, `src/styles.css`, `src/main.tsx`, the mounted Arc Button, ButtonLink and Input sources and styles, `src/arc/PROVENANCE.md`, and the four raster provenance sidecars under `public/assets/`.

`ai-homepage.webp` is recorded as a screenshot of the existing AI homepage captured on 30 October 2026 at 1280×720. `goa-motifs.webp` is generated decorative artwork. `goa-panorama.webp` reuses the prior generated landscape and its provenance; the inherited provenance's asset-name field identifies its original filename. The original values have not been rewritten by this documentation pass. `map-homepage.webp` is recorded as a real 1440×1000 capture of the live `/map` surface on 30 October 2026, with Google attribution retained. Its provenance states that no comparison or paid AI request was made.

The release owner reports completed landing checks at desktop 1440px, phone 390px and 320px, and tablet 768px, with captures in the repository’s `.reports/landing/`: `desktop.png`, `mobile.png`, `mobile-320.png` and `tablet.png`, plus `mobile-menu.png` and `mobile-form.png`. The reviewer returned ship for the scoped corrections after the narrow-phone CTA fix: earlier AI/resources, natural image proportions and removal of provider-brand copy. This acceptance covers the implementation before the later map section. The map section’s new rendered review remains pending at this documentation update.

This documentation pass did not repeat the detector, build or browser checks. It records source inspection and the release owner’s reported evidence; publication remains pending. Sidecar specimens are self-contained static visual translations; the React components remain the authority for actual behavior.

## Do's and Don'ts

### Do

- Do keep this Manrope system scoped to the landing surface.
- Do use the actual installed Arc sources and preserve their semantics, states and provenance.
- Do preserve natural image proportions and distinguish decorative artwork from source evidence.
- Do use concrete copy and keep original-source links and practical uncertainty visible.
- Do retain keyboard focus, labelled controls and the complete reduced-motion reading flow.
- Do keep AI actions connected to the existing service and examples visibly illustrative.

### Don't

- Don't replace the main application's Figtree design system with this landing system.
- Don't use italic or oblique text, eyebrow labels or decorative side stripes.
- Don't stretch images, force organic motifs into square silhouettes or invent product screenshots.
- Don't restore AI-provider branding or small abstract copy fragments removed by the user.
- Don't imply that curated sources guarantee correct answers, current rules or available contacts.
- Don't treat documentation or source inspection as final rendered acceptance or publication evidence.
