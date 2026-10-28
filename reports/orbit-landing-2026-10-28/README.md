# Secondary Goa chat landing page

Route: `/explore`. Cosmos-inspired above-the-fold treatment with three concentric photo rings rotating in 90, 150 and 240 seconds, central question composer, suggested prompts, pause/resume and reduced-motion support. Uses existing ActForGoa photo assets. No generated imagery or new model calls. The composer transfers a draft into the existing `/ask` conversation; the visitor still sends it there, subject to existing availability gates.

Validated with actual Chromium at 1440×900, 390×844 and 320×844. `qa.json` records loaded images, no horizontal overflow or page errors, animation durations, pause and question transfer. Reduced-motion uses no animation. Screenshots capture each size. Production build and all 178 Node tests pass. Live model output was not tested. Installed Impeccable skill is unavailable in this executor.

Implemented and tested; not merged or deployed. Existing release coordinator retains review-site promotion ownership.

## Live route publication

The user subsequently explicitly authorized shipping at `https://actforgoa-field-guide.vercel.app/explore` and requested upright photos. Source commit `755177e` removes tile tilt while preserving orbit speeds. Production build passed; public Chromium evidence is in `live-qa.json` and `live-*.png` (all photos loaded, no horizontal overflow/page errors, pause/resume, draft transfer and reduced-motion checks).

Published as a scoped Vercel project routing update in existing project `prj_4BRx1f4MrLFE5p6Ljnhkp33TOltz`; **no production deployment/alias promotion**. Existing production target remains `dpl_FzbANqhz96u2JNt2eb6fK4BDtS7c`. The isolated static asset deployment is `dpl_4VzSLExLmufsCCJ9HvNohACTbFXu`, built with `vite build --base=/orbit-assets/` from `755177e`. Upload contains the generated index and top-level JS/CSS/font assets only; source data and archived photos continue to load from the existing public site.

Internal origin alias: `actforgoa-explore-assets.vercel.app` (alias-specific public access exception for these public static files; project-wide deployment protection unchanged). Active routing version: `bc71d1f7-c609-46ec-b305-e6b9f776be6d`:

- Route `5e24f99d-63b6-4dcf-a7a0-be4e45b91e8d`: host `actforgoa-field-guide.vercel.app`, `^/explore/?$` → `https://actforgoa-explore-assets.vercel.app/index.html`.
- Route `94bf18e7-a5ea-45a0-ad4b-3d9b168ff70d`: same host, `^/orbit-assets/(.*)$` → `https://actforgoa-explore-assets.vercel.app/$1`.

A future integrated deployment must explicitly retire these two project routing rules after verifying its native `/explore`; otherwise the isolated page keeps precedence. Do not overwrite unrelated staged routing changes. Before this feature there were no project routing rules. The existing site's optional `/api/curation` returns 404 and falls back normally; no new API service was published. AI generation itself was not exercised.

### Entrance and no-eyebrow update

User follow-up source `ce0b0ed` removes the eyebrow entirely, records the no-eyebrow preference in `AGENTS.md`, and adds a three-second spiral entrance. Scene scale settles from 1.16 to 1; ring and matching counter animations start at 5× playback and ease quadratically to 1× after 3000ms, keeping images upright. Reduced-motion disables the entrance and orbit animation.

Build passed. Local and public Chromium checks confirm initial playback >1, exact 1× after three seconds, all matching counter animations settled and zero eyebrow elements. The internal asset alias now serves deployment `dpl_8LKejjCqfL5fdVNoDx77d6YPeEtn` at the same public `/explore` route. Existing production target and route rules are unchanged.

### Full revolutions and photo depth

Source `27285db` (including `a94cd0b`) is live at `/explore` through isolated deployment `dpl_8RDqSrA9CZafsYWEpDX9qRGUAqqo`. The entrance now integrates animation time explicitly: inner/middle/outer rings complete 3/2.5/2 full revolutions in three seconds and then retain their original 90/150/240-second periods. Matching counter rotations keep tiles upright. Pausing also pauses the entrance progression. Photo sizes are 62–78px inside, 86–102px in the middle and 116–132px outside. No eyebrows.

Production build and public Chromium checks pass at 1440/390/320px, covering loaded photos, no horizontal overflow/page errors, pause/resume, exact draft transfer and reduced motion. Live measured entrance turns after settling: approximately 3.04, 2.52 and 2.01. Existing production target and project routing definitions are unchanged.

### Rolling headline and shared navigation

User follow-up source `a9f8e4a` is published at `/explore` via isolated deployment `dpl_36ZVhBLW4cF3MNmmsBhUe7WebRdj`. Reuses the homepage's exact `Header` / `SiteHeader`, including desktop dropdowns, language selector, search and mobile accordion menu. Explore's former simplified header is removed. Scene height accounts for the shared header.

The headline reads “A place to” and rolls through “find local help.”, “protect nature.”, “know your rights.”, “take local action.” and “care for Goa.” every four seconds. Outgoing text rotates up and out while the incoming text rolls in from below, using clipped perspective, blur and opacity. Stable accessible heading text avoids repeated screen-reader announcements; the document title uses that label. Pause motion pauses the headline too; reduced-motion presents a stationary first phrase. No eyebrows.

Production build passed. Public Chromium navigation checks at 1440/390/320px confirm one header, no horizontal overflow, Resources dropdown/accordion, correct legal destination, and keyboard dismissal. `headline-qa.json` checks all five phrases fit each viewport, pause and reduced-motion; `headline-*.png` capture desktop/phone states. Existing production target and scoped routing definitions remain unchanged.

### New main homepage — user-authorized publication

The user explicitly requested this become the main homepage header, retaining the main user paths and remaining content below and using the original homepage search behavior. Local source `1ca0e0c` composes `OrbitLanding embedded` above all eight topic-path buttons, emergency help and the unchanged `DiscoveryFeed`. Both hero submit and suggested questions use the shared `searchDestination` helper and navigate to `/search?q=…`; the optional conversation link still opens `/ask`.

Entrance boost is reduced by 70% to .9/.75/.6 turns in three seconds, then the normal 90/150/240-second periods. Photo collection now has 42 unique archive photos, assigned without replacement to the 39 tiles. No generated images or paid inference.

Live isolated deployment: `dpl_AfenrgMxRbbxqHQCjuF2fMASeBSp`. Active project routing version: `2e8e015b-ac52-4c67-bfe6-e66ca3070f4b`. New root route `7ff31abb-9b89-4c3c-89d0-de36bf52a435` maps host `actforgoa-field-guide.vercel.app`, `^/$` to the existing isolated origin's `/index.html`. The `/explore` and `/orbit-assets/*` rules are retained. No production alias promotion; existing backend/deployment remains untouched. A future integrated homepage deployment must retire all three scoped overrides after verifying native routes.

All 178 Node tests and production build pass. Actual public Chromium at 1440/390/320px verifies one header/main, loaded photos, exactly 39 unique tiles, no horizontal overflow/page errors, eight path buttons, retained feed, a working waste-topic path and exact `/search?q=waste+collection+near+Panaji` submission. Live entrance measurements after settling: .94/.77/.61 turns including normal orbit motion, playback rate 1. Evidence: `home-qa.json`, `home-*.png`, `home-paths-*.png` in this workspace report directory.

Shell GitHub push access expired during this follow-up. Source was synchronized through the connected GitHub contents API instead: commits `06770c9` (hero/search), `6a45736` (42-photo collection), `79dab98` (homepage composition). These remote commits contain the same feature text as local `1ca0e0c`; local and remote commit IDs differ. PR #98 remains open for eventual source integration; live publication is through the bounded project route update.

### Cosmos source investigation: spiral flow and navigation fade

Inspected the actual public client modules from Cosmos, including `https://www.cosmos.so/_next/static/chunks/2sd0cwht6lyv2.js` and the landing configuration loaded by the live page. The effect is a continuous inward spiral sampled by arc length, not rigid concentric ring rotations. The source config uses eight turns, radius-based size attenuation, entry/exit fades, baseVelocity .32, a 24× burst with 700ms ramp-up and 3200ms quadratic decay, and scroll boost. Canvas rendering also turns tiles along path tangents; this adaptation preserves the user's explicit upright-photo requirement and gentler intensity instead.

Local source `71a69c2` introduces an independently computed equal-distance spiral (`src/orbit-motion.ts`) with four turns adapted to the 39 distinct tiles, continuous depth scaling, wraparound fades and a reduced burst. Initial speed starts at 1×, ramps toward a measured 5.21× at 700ms, then settles to 1× by 3200ms. Shared ring transforms are disabled. Navigation overlays the scene with a 165–190px opaque-to-transparent paper gradient, so photos extend behind it without a hard cutoff. Dropdown/mobile menu surfaces remain readable.

Remote source was synchronized through GitHub API in `70c6b5f`, `2a085f9`, `a735e6f`, `ec734aa`; it matches the local feature text. Live asset deployment: `dpl_2jZiMe2bDLbgga2fr5YXRCXYiR1s`. Existing root/explore/asset project routes and production backend target are unchanged.

Validation: production build; mathematical equal-distance path checks (<.01% variation in equal-length steps); ramp-up/settle checks; actual Chromium pause and reduced-motion checks; all 39 tiles change radius individually. Navigation background is transparent and the gradient overlays the scene from viewport top. Desktop/390/320px checks preserve unique images, eight topic buttons, feed and exact standard homepage search routing. Evidence: `spiral-flow-qa.json`, updated `home-qa.json` and screenshots.

### Immediate arrival burst, larger main paths and revised wording

Local `231f82d` (remote `3ecf3c5` including helper/hero updates) removes the 700ms ramp: motion begins at 7.9× when the photos have decoded, then only decelerates to 1× by 3200ms. This prevents image loading from consuming the opening burst. Public Chromium measured roughly 179px/s at arrival and 25px/s at rest; pause and reduced-motion pass. This supersedes the previous ramp-up description.

Local `f1fce7f` (remote `0446a77` including preceding CSS/flow/translation updates) enlarges the eight main-path cards: desktop minimum 132px with 20px labels, 15px descriptions and 34px icons; phones use 18px labels and 14px descriptions, with one column at the narrowest widths. Restores exact earlier user labels “Community and Youth” and “Biodiversity”, plus “Youth care & community support”, recovered from the HOME MENU chat. Internal topic keys are preserved. Hindi/Konkani draft translations are updated. Other unpublished HOME MENU work (support subpaths, schemes and navigation enhancements) remains owned by that workstream; this change does not claim those features shipped.

Hero heading/composer is shifted upward by 30px on desktop and 20px on phones. Current isolated deployment: `dpl_6r9oafbneujYTFNdGjbYukNmbZsK`. All 178 tests and production build pass. Public desktop/390/320 checks verify larger unclipped cards, revised labels, topic navigation, exact hero offsets and no horizontal overflow; homepage search/path/feed checks remain passing. Evidence: `card-copy-qa.json`, `arrival-speed-qa.json`, updated homepage screenshots. Existing root/explore/asset routing and backend production target are unchanged.
