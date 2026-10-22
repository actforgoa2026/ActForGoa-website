---
version: 1
slug: "src-app-tsx"
primary_target: "src/App.tsx"
related_targets: ["src/styles.css", "src/TopicPage.tsx", "src/topic-flows.ts", "src/components/TopicIcon.tsx", "src/components/RecordCard.tsx", "src/PracticalGuide.tsx", "src/guide-presentation.ts", "src/guides.ts", "src/components/arc/foundation.css", "src/components/arc/button/button.tsx", "src/components/arc/search-field/search-field.tsx", "src/components/arc/input/input.tsx", "src/components/arc/textarea/textarea.tsx", "src/components/arc/segmented-control/segmented-control.tsx", "src/components/arc/site-header/site-header.tsx", "src/components/arc/site-header/site-header.module.css", "src/discovery.ts", "src/public-record.ts"]
---

# Directory surface

Mode: Operate, with Read for the library and record pages.

## Direction contract

THESIS: Choose a topic, identify the need, and reach a clear next action before related people and reading. Search remains immediately available; returning preserves the visitor's place.

OWN-WORLD: A restrained, wireframe-style public information menu on warm paper, with forest-green text, upright Manrope, Lucide outline icons, and large outlined controls. Page and section headings use weight 800; ordinary record and choice labels use 750. Original photography remains in discovery and articles. Official Arc controls remain. The earlier yellow/pink welcome area, hero flower, and filled pictograms are superseded.

STORY: Recognise the mission, choose a broad topic, answer a simple need question, and choose the next action. Some needs have one further choice. Related organisations and reading follow below, with access to complete filtered results. Breadcrumbs show the path and a back link makes changing the choice easy. Wildlife help is one need within Nature & wildlife, not the homepage's default emphasis.

FIRST VIEWPORT: The official Arc SiteHeader keeps its original nine categories and Search action. The home introduction presents the mission, one plain supporting sentence, and a search form. Eight large outlined controls follow in this order: Waste & recycling, Water & environment, Community & rights, Nature & wildlife, Food & farming, Building & transport, Health & wellbeing, Culture & heritage. The home grid has four columns on desktop and two at 850px and below. Each control combines a label, outline topic icon, and directional arrow. There is no decorative hero photograph or flower; the mixed feed with original imagery follows the topic menu.

FORM: `/topics/:slug/:actionId?/:choiceId?` is the menu route. Six-choice need menus use three desktop columns; four-choice menus use two through choice-grid-pairs. Both use two columns at 850px and one at 620px. Final action destinations use two columns, then one on phones. Home choices remain at least 164px tall; ordinary need choices use at least 120px, becoming 100px on phones. Large outlines identify actual links and actions; reading records remain open ruled rows. Text-entry focus changes fill without new borders or visible rings; links and buttons retain Arc keyboard outlines. Reading copy is 18px/450 with 1.75 leading and a 66ch measure on all viewports.

FINISH: Corrected captures in .impeccable/review/wireframe-flow cover desktop 1440 × 1000, phone 390 × 844, and the actual app panel 508 × 724. Final finish review returned “ship” with no material fixes. Browser checks passed for topic → collection → type, reporting-link destinations, service navigation and back-scroll restoration, input focus, menu closing, guide contents navigation, and mobile tables. The build and 22 tests passed. No deployment has occurred. Keep DESIGN.md and its schema-version-2 samples aligned with the final source, preserve photo provenance, and retain the distinction between local verification and deployment. Earlier colour-hierarchy captures are superseded.

## Behavior commitments

The eight topic definitions and their needs live in topic-flows.ts. Waste currently offers reporting dumping, extra collection, recycling, composting, missed collection, and clean-up paths. Extra collection asks which kind of waste before its next actions. Other topics offer similarly direct choices. TopicPage places choices or next actions above people and reading, ranks relevant records for the chosen action, prioritises specified people and resources, and provides complete filtered-directory/library links. Invalid routes offer a return to topic selection. Official external services and downloads keep their real link semantics; the site does not claim to have submitted a report or arranged a service.

React Router ScrollRestoration runs with catalogue data available. Search query resubmission and topic/type filtering prevent scroll reset. Expanded-result limits and layout are cached per history entry. Grouped answers retain ranking and total match counts. Record links from topic routes carry catalogue-return state. Search clear reserves its slot and returns focus without scrolling. Segmented controls support arrow keys, Home, and End. SiteHeader menus close on route changes and Escape, restoring trigger focus on Escape. The compact sheet locks background scrolling and keeps Tab focus within visible header controls. During closing, PresenceLayer immediately makes the sheet and scrim inert and disables pointer events, so exit animation cannot intercept the next tap.

The discovery feed currently contains 533 eligible stories, resources, organisations, and volunteer contacts, excluding generic pages. It loads 12 at a time, automatically within the 400px observer margin while visible, with Pause/Resume and a manual fallback. Manual loading announces additions and focuses the first new title without scrolling. Filter, extent, and automatic-loading state restore per history entry. Mixed batches lead with a larger image-led item and two text-led companions, then a three/two/one-column grid. Periodic topic routes enter the menu flow.

Five listed authored practical guides remain drafts in their original source. Reader-facing presentation uses guide-presentation.ts to remove internal draft banners and review codes, replace code-bearing warnings with plain practical cautions, and simplify research-process wording. PracticalGuide uses the resulting headings for contents navigation. An optional “About this guide” disclosure after the body states that review continues and links to official sources and detailed review notes. Original guide and review files remain unchanged. Listed guides show a desktop contents list; support registers use a desktop disclosure. All guides use the mobile disclosure at 850px. Two-column tables stack at 620px; wider tables retain keyboard-scrollable regions.

Every catalogue record passes through public-record.ts: structured phone fields and phone/WhatsApp actions are removed, and recognised numbers in presentation prose and labels are sanitised. Originals remain intact. Community entries use source descriptions with five-line excerpts, all topics, and an honest missing-description fallback. Original photographs use archived renditions with provenance; later images form a two-column gallery that stacks on phones. Missing original images remain reported.

## Constraints

No serif, italic, or oblique type, decorative side stripes, filled illustration families, bright hero palette, fabricated documentary photographs, invented biographies, invented facts, or invented contact details. Outline icons always retain visible labels and accessible link names. Do not reintroduce phone data into record presentation. Keep source evidence separate from reader-facing copy. Preserve useful cautions and optional audit access without surfacing editorial codes or crawl dates as primary guidance. Real search, real links, honest empty and prepared-email states, readable mobile text, keyboard access, and reduced-motion support remain required. The contact reason selector remains native.

## Open decisions

Editorial ownership, ongoing contact verification, legal review of authored guides, production mail delivery, multilingual content, and production domain cutover.
