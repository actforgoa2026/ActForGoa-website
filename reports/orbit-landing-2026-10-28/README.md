# Secondary Goa chat landing page

Route: `/explore`. Cosmos-inspired above-the-fold treatment with three concentric photo rings rotating in 90, 150 and 240 seconds, central question composer, suggested prompts, pause/resume and reduced-motion support. Uses existing ActForGoa photo assets. No generated imagery or new model calls. The composer transfers a draft into the existing `/ask` conversation; the visitor still sends it there, subject to existing availability gates.

Validated with actual Chromium at 1440×900, 390×844 and 320×844. `qa.json` records loaded images, no horizontal overflow or page errors, animation durations, pause and question transfer. Reduced-motion uses no animation. Screenshots capture each size. Production build and all 178 Node tests pass. Live model output was not tested. Installed Impeccable skill is unavailable in this executor.

Implemented and tested; not merged or deployed. Existing release coordinator retains review-site promotion ownership.
