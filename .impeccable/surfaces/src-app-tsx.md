---
version: 1
slug: "src-app-tsx"
primary_target: "src/App.tsx"
related_targets: ["src/styles.css", "src/components/arc/foundation.css", "src/components/arc/button/button.tsx", "src/components/arc/search-field/search-field.tsx", "src/components/arc/input/input.tsx", "src/components/arc/textarea/textarea.tsx", "src/components/arc/segmented-control/segmented-control.tsx", "src/components/arc/site-header/site-header.tsx", "src/components/arc/site-header/site-header.module.css", "src/discovery.ts", "src/public-record.ts"]
---

# Directory surface

Mode: Operate, with Read for the library and record pages.

## Direction contract

THESIS: A practical question becomes sourced people, reading, and action. Search is immediately usable; browsing a result and returning preserves the visitor's place.

OWN-WORLD: The user-approved refinement is an open Goan field guide: continuous warm paper, forest-green text, upright Manrope only, with no serif type, real local photography, larger topic labels, and official Arc controls. Typography, spacing, and horizontal rules provide structure. No boxed green introduction, card panels, pale story container, yellow search button, or ochre focus treatment remains normative.

STORY: Recognise the mission, type a need or choose a topic, inspect grouped answers, and return without losing expanded results, chosen layout, or scroll position. Dates, sources, and historical contact caveats stay visible.

FIRST VIEWPORT: The sticky official Arc SiteHeader carries the original nine categories and Search action. Take action and About open desktop dropdowns; below a 1200px header-container width the same categories appear in a mobile sheet. A large upright mission heading and pale search form sit directly on paper beside the square-cropped river photograph. Underlined starter links follow the field. The topic index uses strong 18px/750 desktop labels, 20px at the two-column intermediate breakpoint, and 16px/750 phone labels.

FORM: The approved refinement supersedes the earlier boxed composition. The original field-guide seed, 13ed79d5bc46dc62, is historical context; the user's explicit approval of the revised homepage determines the current direction. Search and story pairings are open. Resource components are ruled editorial rows with no panel shell. Official Arc SiteHeader, Button, SearchField, Input, Textarea, SegmentedControl, and foundation provide real controls. Home continues into a mixed discovery feed after the topic index; it no longer mounts the fixed three-resource selection or separate spotlight. Text-entry focus changes fill without new borders or visible rings; links and buttons retain Arc keyboard outlines.

FINISH: Document the actual shipped source and supplied refinement captures in DESIGN.md and its schema-version-2 sidecar. Preserve real-image provenance. Distinguish documentation checks from interaction and deployment evidence.

## Behavior commitments

React Router ScrollRestoration runs with catalogue data available. Search-route query resubmission and topic/type filtering prevent scroll reset. Expanded-result limits and layout are cached per history entry. Grouped answers retain ranking and total match counts. Search clear keeps a reserved slot and returns focus without scrolling. Segmented controls support arrow keys, Home, and End. SiteHeader menus close on route changes and Escape, restoring trigger focus on Escape. The compact sheet locks background scrolling and keeps Tab focus within visible header controls.

The discovery feed currently contains 528 eligible stories, resources, organisations, and volunteer contacts, excluding generic pages. It adds 12 entries at a time, automatically within 400px of the marker while visible, with Pause/Resume and a manual fallback. Manual loading announces additions and focuses the first new title without scrolling. Its filter, extent, and automatic-loading state restore per history entry. Mixed batches lead with one larger image-led item and two text-led companions, then a three/two/one-column responsive grid and periodic topic routes.

Every displayed catalogue record passes through public-record.ts: structured phone fields and phone/WhatsApp actions are removed, and recognised numbers in record prose are sanitised. Originals remain intact. Community entries use richer original descriptions, five-line excerpts, all topics, and an honest missing-biography fallback. Original article photographs use restored archived renditions with provenance; later images form a two-column gallery that stacks on phones. Missing original images remain reported.

## Constraints

No serif, italic, or oblique text, decorative side stripes, fabricated local imagery, invented biographies, invented facts, or invented contact details. Do not reintroduce phone data into record presentation. Keep the source content separate from its presentation. Real search, real links, honest empty and prepared-email states, readable mobile text, keyboard access, and reduced-motion support remain required. The native contact reason selector is retained.

## Open decisions

Editorial ownership, ongoing contact verification, production mail delivery, multilingual content, and production domain cutover.
