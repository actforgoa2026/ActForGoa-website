---
version: 1
slug: "design-refinement"
primary_target: "src/styles.css"
related_targets: ["src/components/arc", "src/orbit-landing.css", "src/topic-navigation.css", "src/research.css", "src/crm.css", "src/satellite-layout.css", "src/newsletters.css", "src/site-footer.css"]
---
# Green and cream local redesign

Mode: Operate for searching, directory, forms, and satellite tools; Read for sources and newsletters; Persuade for the homepage introduction.

## Direction contract

THESIS: Make the next action obvious through actual Arc controls, readable hierarchy, and open space for the content.

OWN-WORLD: Forest green and warm cream, self-hosted upright Figtree, rounded Arc controls, full quiet borders, and gentle diffuse shadows. Real Goa photography and the circular homepage animation retain the identity. The footer adds a separately documented decorative stipple landscape.

STORY: Enter a compact topic search or choose one of eight icon-led topics, follow a practical route, and inspect source evidence. Start a conversation from the separate AI route. Browse the directory or source library with the same control language. Satellite investigation keeps the map alongside a scrollable analysis panel on desktop. Analyse, Results and Saved evidence use Arc SegmentedControl; dates use the actual Arc DatePicker and Calendar, and timeline/opacity use Arc Slider. On phones the search and drawing controls sit above a taller map, followed by analysis in ordinary document flow. The phone analysis panel does not scroll independently. No extra visual skin encloses the workspace.

FIRST VIEWPORT: Homepage centers the rotating heading, short introduction, compact Arc SearchField and separate Search button, example questions, and conversation link within the existing photo orbit. The next section presents eight large Arc ButtonLink topic choices; their icons remain visible on phones. The header centers desktop navigation between brand and actions and changes to its menu below a 1400px container width. Catalogue searches stay near their headings at normal control height and bounded width. The AI route uses centered headings and Arc domain tabs, a plain layout around its Textarea, and an action row below. The satellite map follows a compact 64px header, with an explicit expand control and visible provider attribution.

FORM: User-pinned refinement informed initially by Airbnb's clear hierarchy and reusable controls, resolved to actual uiArc.dev components everywhere a control is new or changed. Green/cream theme tokens and layout composition supply the project character. No alternate control skin or extra search/composer container. Standard searches stay compact; a conversation textarea may be taller for its task. Figtree remains upright; no decorative side stripes or eyebrow labels. Records and reading keep structural rules and source proximity.

FINISH: Local-only work; no commit, push, or deployment is authorised by this refinement. A build does not establish visual quality. Keep desktop and phone rendered checks, current source, Arc provenance, and raster provenance together. Do not launch Device Hub.

## Implemented evidence

- `src/components/arc/PROVENANCE.md` records Button, Input, Textarea, SearchField, SegmentedControl, SiteHeader, MorphSelect, Switch, Checkbox, Slider, foundation/motion sources, and the local ButtonLink adapter.
- `src/styles.css` supplies Figtree, green/cream aliases, 12px control corners, 44/48/52px button heights, and gentle field/control shadows.
- Catalogue, directory, research-library, and orbit search widths are 560px, 520px, 520px, and 620px respectively, shrinking to the available space.
- `src/SiteFooter.tsx` and `src/site-footer.css` own the open footer. `public/assets/footer/goa-stippled-landscape.webp.json` records the generated decorative illustration and its use boundary.
- `src/newsletters.css` supplies an upright readable column, archival context, and source/download actions with optional original-layout evidence.

## Rendered review and limitations

Documentation inspected the supplied homepage desktop/phone, desktop footer, phone newsletter reader, compact library search, and expanded directory MorphSelect captures in `.impeccable/review`. The library capture's earlier language selector is superseded by the current source and later homepage/directory renders. Other captures in this folder can predate final control changes and should be checked against source before reuse.

This pass updates the design records and sidecar from current code; it does not rerun the detector, build, browser interaction suite, or service checks. A final implementation/behavior verdict belongs to the review owner. Satellite retrieval, generated-answer readiness, contact verification, and deployment status are not inferred from these visuals. Historical wireframe-flow verdicts are retained as historical evidence only.
