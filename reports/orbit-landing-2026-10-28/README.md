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
