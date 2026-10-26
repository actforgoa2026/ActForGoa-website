---
version: 1
slug: "src-app-tsx"
primary_target: "src/App.tsx"
related_targets: ["src/styles.css", "src/components/arc/foundation.css", "src/components/arc/button/button.tsx", "src/components/arc/search-field/search-field.tsx", "src/components/arc/input/input.tsx", "src/components/arc/textarea/textarea.tsx", "src/components/arc/segmented-control/segmented-control.tsx", "src/components/arc/site-header/site-header.tsx", "src/components/arc/site-header/site-header.module.css", "src/discovery.ts", "src/discovery.css", "src/DiscoveryLinks.tsx", "src/public-record.ts", "src/HomeCarousel.tsx", "src/HomeHeroWordWheel.tsx", "src/home-hero.css", "src/content/hero-photos.json", "public/assets/hero/provenance.json", "src/TopicPage.tsx", "src/topic-flows.ts", "src/topic-records.ts", "src/topic-navigation.css", "src/components/TopicIcon.tsx", "src/components/RecordCard.tsx"]
---

# Directory surface

Mode: Operate, with Read for the library and record pages.

## Direction contract

THESIS: A practical question becomes sourced people, reading, and action. Search is immediately usable; browsing a result and returning preserves the visitor's place.

OWN-WORLD: The user-approved refinement is an open Goan field guide: continuous warm paper, forest-green text, upright Manrope only, with no serif type, real local photography, stronger type, larger topic labels, and official Arc controls. Body weight is 550, most explicit headings are 750, hero and action headings are 800, controls are 700, and header labels are 750. The original paper, green, muted, line, pale, and white palette remains approved; the temporary brown, pink, and yellow palette is withdrawn. Typography, spacing, and horizontal rules provide structure. No boxed green introduction, card panels, pale story container, yellow search button, or ochre focus treatment remains normative.

STORY: Recognise the mission, type a need or follow a topic through its restored action and follow-up menus, inspect sourced answers, and return without losing expanded results, chosen layout, or scroll position. Dates, sources, and historical contact caveats stay visible.

FIRST VIEWPORT: The sticky paper Arc SiteHeader precedes a high-resolution photograph with the animated “[word] in Goa” heading, supporting line, and 720px-maximum rounded question composer over it. White captions, attribution, and carousel controls sit inside the lower image edge over a dark scrim. On phones the photograph spans the viewport and the supporting line remains visible. The emergency action sits in the topic-heading row on larger screens and follows the heading at full width on phones. All eight bordered topic choices, each with a strong title and description, follow immediately in four columns with 8px gaps, changing to two at 850px. Choices are at least 82px tall. The 1408×800 desktop and 390×844 phone captures show all eight within the first viewport; parent measurements place the phone bottom at 835px. At 375×667 the choices extend to 861px and scroll naturally. The question routes to sourced search results.

FORM: The approved refinement supersedes the earlier boxed composition. The original field-guide seed, 13ed79d5bc46dc62, is historical context; the user's explicit approval of the revised homepage determines the current direction. The homepage composer stays over the photograph. Restored topic navigation uses full-border choice controls while resource rows and story pairings stay open. This is an exact restoration of the earlier guided menus, not a new visual-world selection. Resource components are ruled editorial rows with no panel shell. Official Arc SiteHeader, Button, SearchField, Input, Textarea, SegmentedControl, and foundation provide real controls. Home continues into a sectioned discovery feed after the topic index; it no longer mounts the fixed three-resource selection or separate spotlight. Text-entry focus changes fill without new borders or visible rings; links and buttons retain Arc keyboard outlines.

FINISH: Document the actual shipped source and supplied refinement captures in DESIGN.md and its schema-version-2 sidecar. Preserve real-image provenance. Distinguish documentation checks from interaction and deployment evidence.

## Behavior commitments

React Router ScrollRestoration runs with catalogue data available. Search-route query resubmission and topic/type filtering prevent scroll reset. Expanded-result limits and layout are cached per history entry. Grouped answers retain ranking and total match counts. Search clear keeps a reserved slot and returns focus without scrolling. Segmented controls support arrow keys, Home, and End. SiteHeader menus close on route changes and Escape, restoring trigger focus on Escape. The compact sheet locks background scrolling and keeps Tab focus within visible header controls.

The discovery feed groups eligible records into practical guides, people and organisations, stories, and documents. Clear section headings, full-width horizontal dividers and collection links make the progression explicit. Equal guide/document/story grids alternate with open people rows, topic indexes, editable templates, participation links and further checklists. All supporting links resolve to existing page routes. Records remain unique; support links are not included in catalogue counts. The complete section sequence is deterministic before pagination, so loading more never moves earlier records. The feed retains 12-record additions, visible-document automatic loading within 400px of the marker, Pause/Resume, manual focus and announcements, type filters, and history restoration.

Every displayed catalogue record passes through public-record.ts: structured phone fields and phone/WhatsApp actions are removed, and recognised numbers in record prose are sanitised. Originals remain intact. Community entries use richer original descriptions, five-line excerpts, three reviewed work tags, archival context, and an honest missing-biography fallback. CRM details preserve every combined original and reviewed focus tag. Original article photographs use restored archived renditions with provenance; later images form a two-column gallery that stacks on phones. Missing original images remain reported.

## Constraints

No serif, italic, or oblique text, decorative side stripes, fabricated local imagery, invented biographies, invented facts, or invented contact details. Do not reintroduce phone data into record presentation. Keep the source content separate from its presentation. Real search, real links, honest empty and prepared-email states, readable mobile text, keyboard access, and reduced-motion support remain required. The native contact reason selector is retained.

## Open decisions

Editorial ownership, ongoing contact verification, production mail delivery, multilingual content, and production domain cutover.


## Hero refinement, 26 October 2026

User requested a high-resolution photo carousel, a ChatGPT-style rounded question entry, and the main actions above the fold. The composer is the intentional 24px-radius exception to other Arc controls, with a stable border, pale focus fill, and circular 44px send button. `src/HomeCarousel.tsx`, `src/HomeHeroWordWheel.tsx`, `src/home-hero.css`, and `src/content/hero-photos.json` own this composition. Keep photograph provenance in `public/assets/hero/provenance.json`.

The Dizko-derived word wheel cycles Volunteer, Build, Create, Recycle, Culture, and Health before “in Goa” on a shared 4000ms beat. Words roll for 620ms; photographs crossfade for 900ms every second beat. The measured word slot keeps both outgoing and incoming words intact and responds to font loading and resizing. Autoplay waits for the next photograph to load, requires an intersecting hero observed at a 25% threshold and a visible document, and temporarily stops while controls are hovered. Focus on interactive hero elements, manual navigation, and swiping pause persistently until Play; the rotation control is exempt from focus pausing. Programmatic heading focus does not stop arrival autoplay. Reduced motion disables autoplay and transitions, removes Play, and retains manual controls. Failed photos are excluded, and all-photo failure gets a text fallback. Captions announce politely while paused or reduced-motion and remain silent during enabled autoplay.

Current captures in `.impeccable/review/restored-topics/` show the original palette, stronger type, preserved hero, and restored topic buttons and menus. All nine supplied captures were inspected. Hero content padding is now 18px 24px 62px on desktop and 14px 20px 72px at 620px; the short-phone rule keeps 18px top and 66px bottom padding. The hero photos, question composer, shared animation clock, and motion controls remain intact. Earlier hero-bold and hero-carousel captures are historical.


## Discovery sections, 26 October 2026

The user requested clearer sections and dividers, consistent grids, and more types of resources throughout the scroll, taking inspiration from Dizko’s alternating content types. They chose practical help first, with variety as scrolling continues. Use `src/discovery.css` and `src/DiscoveryLinks.tsx` for this surface; preserve the current hero and shared catalogue behavior.


## Restored topic navigation, 26 October 2026

The user requested the earlier topic buttons and exact guided menus restored. Keep the existing eight flows and `/topics/:slug/:actionId?/:choiceId?` route hierarchy. Topic pages expose action choices and contextual follow-up choices, destination links, authored steps, people, and reading. Breadcrumbs and explicit back links return to the preceding choice. Topic-only search pages expose the same choices, and the separate discovery-topic index routes into them. The shared `RecordCard` retains catalogue-history state from topic routes. Preserve the concurrent discovery and reporting work.

Homepage choices have the original full neutral `#9faea5` border, 4px corners, an 82px minimum height, 12px padding, 16px titles at weight 800, and 13px descriptions at 650. On phones padding becomes 10px, titles 15px, and descriptions 12px; icons hide at 620px and arrows at 1150px. Inner choices use 40px icons, 120px minimum height, 24px padding, and 20px labels at 750; at 620px these become 100px, 20px, and 18px. Their grid is three columns, or two for two/four options, then two at 850px and one at 620px. Hover uses pale fill and green borders; press uses the line-colour fill. Keep the original palette and stronger text.

Evidence: nine restored-topics captures, `menu-checks.json`, and `detector.json` with zero primary findings. The parent reports 62 tests and browser journeys passing. The parent’s `reports/TOPIC-RESTORATION-HANDOFF.md` confirms the final TypeScript/Vite build passed with `index-CaOemWGg.js` and `index-BHzalREE.css`; the frozen runtime snapshot is `.reports/topic-restoration-2026-10-26`, with runtime/test hashes checked by the parent. This documentation pass did not rerun those checks. Deployment is held during release coordination. No new concept seed or unrelated cleanup is part of this restoration.
