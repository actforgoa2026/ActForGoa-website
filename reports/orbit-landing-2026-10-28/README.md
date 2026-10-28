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
