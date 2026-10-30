# Homepage refinement

The user's correction restores the original credited Goa photo carousel around the exact centered mission heading, groups existing topic destinations into Climate, Civic and Culture, expands the field-guide sections with descriptive copy, and blends a taller footer illustration into its links. The separate AI homepage and the previous NOTES actions, public map and Google heritage pin form are preserved.

The carousel uses actual Arc buttons, previous/next/pause controls, eight-second photo rotation, a stationary heading, hover/focus pausing, offscreen/document visibility handling, reduced-motion support, image-failure fallback and the existing touch-swipe handler. Search remains below the photograph. The footer uses the original decorative artwork with a CSS fade over its stippled edge; no new image, source claim or asset licence is introduced.

## Verification before publication

- All 281 Node tests pass; the production build passes with the existing chunk-size advisory.
- Desktop1440, tablet768 and phone390/320 layouts have no horizontal overflow or computed italic type. The h1 center differs from the carousel center by less than0.01px. All three original photos load, and all fourteen topic routes plus the Climate Action Plan remain present once in their category groups.
- Actual autoplay advances the photograph while the heading stays unchanged. Previous/next controls and pause/play work. “Plant trees” search still opens biodiversity. The direct Lovable destination is preserved.
- Forty local route renders cover home, explore, waste, directory/archive, emergency, report, farming guide, template, research/all/legal/ecology, admin, blog/archive, a source document, heritage, satellite map, climate plan and AI on desktop/phone. Async routes were awaited before inspection.
- Actual Impeccable workflow and rendered review were used. Regex scan of changed UI files finds zero anti-patterns; type-ramp advisories are deliberate surface scale choices for the restored hero and enlarged sections. Existing Arc controls and Figtree/cream/forest styling are retained. Source checks find no added italic/oblique or side-stripe styling.
- Physical phone gestures and Safari were not tested. Reduced-motion handling is preserved in source; the host preference was not changed. No report/story submission, paid model request, backend change or Device Hub use occurred.

Protected local evidence: `.reports/home-refinement/` contains `layout.json`, `routes.json`, screenshots at four widths, `design-scan.txt`, test/build logs and the release evidence. Publication and final public checks are recorded below when complete. Local ports4176/4197 remain available throughout.
