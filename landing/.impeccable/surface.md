---
version: 1
slug: "actforgoa-landing"
primary_target: "landing/src/App.tsx"
related_targets: ["landing/src/styles.css", "landing/src/main.tsx", "landing/src/arc", "landing/public/assets", "landing/public/credits.html"]
---

# ActForGoa landing

Mode: Persuade. A separate `/landing` surface for the existing ActForGoa AI service, source library, practical guides, public directory and satellite-map investigation. Product truth remains in the repository root `PRODUCT.md`; the reusable visual system for this surface is `landing/DESIGN.md` with extensions in `landing/.impeccable/design.json`.

## Direction contract

THESIS: Give people a concrete route from a local Goa question to cited material, useful organisations and practical action.

OWN-WORLD: The user-pinned Butter reference supplies spacious grotesk typography, floating navigation, soft product depth and deliberate scroll intervals. The page translates this into upright Manrope, warm paper, forest ink, stippled Goa artwork and a lime interruption. This is an intentionally scoped landing system; the main application's Figtree system is retained.

STORY: Meet Goa, see the real AI homepage, inspect labelled examples, explore satellite-map investigation, choose practical resources, understand the source library, then move through Ask, Check and Act. The current implementation places the AI preview, examples and resources earlier as requested. A later ordering pass remains separate.

FIRST VIEWPORT: A floating header, central stippled cow, smaller desktop palm and temple, two-line “Answers for Goa. Backed by sources.” headline, concrete explanatory copy and primary AI action. The panorama closes the first scene. Phone composition removes the side motifs and keeps image proportions natural.

FORM: Code-led adaptation of the pinned reference. No new direction tournament or qualitative interview is needed for this documentation handoff: the existing direction and subsequent user corrections supply the language. The source-library passage pins on desktop and resolves through a statement, document fan and answer. A later horizontal passage stages Ask, Check and Act. Narrow screens and reduced motion use a complete vertical flow.

FINISH: Documentation is based on the implemented source as inspected on 30 October 2026. The release owner completed desktop 1440px, phone 390px/320px and tablet 768px checks; the reviewer returned ship for the scoped fixes after the narrow-phone CTA correction. The user subsequently requested the map section. Its new rendered review and publication remain pending in this handoff. This pass did not rerun the detector.

## Current section order

1. Hero (`#top`).
2. Place-name strip.
3. Real AI homepage preview (`#ai-preview`).
4. Interactive illustrative examples (`#in-action`).
5. Satellite map and image analysis (`#map-analysis`).
6. Practical guides, directory and source library (`#resources`).
7. Source-library promise and its limits (`#source-promise`).
8. Staged source-library explanation (`#intelligence`).
9. Ask panel (within `#ask-check-act`).
10. Check panel (within `#ask-check-act`).
11. Act panel (within `#ask-check-act`).
12. Other ActForGoa destinations (`#more`).
13. Questions and source caveats (`#questions`).
14. Question composer (`#start`).
15. Open footer.

## Latest accepted corrections

- Keep natural image and illustration proportions, including the original product screenshot ratio.
- Bring the AI demo and resources earlier in the page.
- Add the map-analysis section after examples and before resources, using a real map screenshot and an explicit experimental-analysis caveat.
- At 360px and below, show “Ask AI” in the header while retaining the accessible name “Ask ActForGoa AI” and a 44px minimum target.
- Use direct, concrete copy; remove AI-provider branding and small abstract fragments.
- Preserve the no-italics, no-eyebrows and no-side-stripes requirements.
- Use the actual installed Arc controls, with copied source and provenance.
- Keep examples visibly illustrative, source uncertainty clear and links connected to the existing destinations.

## Destination and behavior contract

The principal action opens `https://actforgoa-field-guide.vercel.app/ai`. Example questions and the final form open the existing `/ask` route with the original question and `start=ai`. The landing page itself makes no live model requests. The map preview opens the existing `/map` service. Its real 1440×1000 capture preserves Google attribution and introduces dated imagery, measurements and AI-assisted investigation of canopy, wetlands and land use. The current status checked by the release owner was `imagery_ready=true`, `classification_ready=true`, `planner_ready=false`; no AI call was made. This is a bounded status observation, not proof that every analysis capability is available or correct. Research, topic, directory, climate, story, participation and MCP links use the existing service's routes.

The source library is described as community-gathered and curated, with no open-web search for the agent. The FAQ explicitly preserves historical-document, extraction-gap, interpretation and contact-availability caveats. Do not convert the illustrative examples into claims of verified advice.

Motion follows the system preference and a locally persisted pause preference. The desktop pinning and horizontal journey are disabled for the static reading flow. Focusing an offscreen horizontal panel switches to the paused vertical flow and brings the focused item into view. Header Escape handling returns focus to the menu trigger. Source and example links remain ordinary anchors.

## Scope and provenance

The user has approved shipping this separate `/landing` surface before the later reordering pass. That approval supersedes the original local-demo-only boundary for this route. It does not make the documentation a record of a completed publication. The main application and its global design documentation are outside this documentation write scope.

Inherited direction evidence: `/Users/zakkrevitt/code/ActForGoa/.impeccable/surfaces/demos-actforgoa-homepage-src-app-tsx.md` and `/Users/zakkrevitt/code/ActForGoa/.reports/butter-homepage-research/direction.md`. Those files describe the earlier demo and its then-current no-deployment constraint. Current authorization and corrections above supersede that stage while preserving the pinned visual reference.

Artwork evidence: `landing/public/assets/goa-panorama.webp.json`, `landing/public/assets/goa-motifs.webp.json`, `landing/public/assets/ai-homepage.webp.json`, `landing/public/assets/map-homepage.webp.json`, plus the visible `credits.html` link. Arc origins are in `landing/src/arc/PROVENANCE.md`. This provenance includes inherited descriptions of controls not mounted on this surface; only Button, ButtonLink and Input are used here.

## Verification state

Source inspection confirms the current 15-part order, map placement and caveat, destination wiring, example labels, source caveats, natural image ratios, compact phone CTA, Arc imports and reduced-motion alternative.

The release owner reports completed desktop 1440px, phone 390px/320px and tablet 768px checks. Evidence lives in `.reports/landing/desktop.png`, `mobile.png`, `mobile-320.png`, `tablet.png`, `mobile-menu.png` and `mobile-form.png`. The independent reviewer returned ship for the requested corrections, including the final compact-phone action. These checks preceded the map addition; its new desktop/phone render review is pending. Build and publication results remain with the release owner and are not inferred from the captures.

No Device Hub use is required or authorised by this handoff.

Final review update: the finish reviewer scored the new map section’s mobile spacing correction resolved and returned ship. Map evidence is `.reports/landing/map-desktop.png` and `map-mobile.png` in the release checkout. Publication is the remaining release step.
