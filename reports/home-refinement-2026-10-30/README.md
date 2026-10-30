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

Protected local evidence: `.reports/home-refinement/` contains `layout.json`, `routes.json`, screenshots at four widths, `design-scan.txt`, test/build logs and the release evidence. Local ports 4176 and 4197 remain available throughout.

## Published and verified

- Public site: https://actforgoa-field-guide.vercel.app/.
- Source: [PR138](https://github.com/actforgoa2026/ActForGoa-website/pull/138), merged as `00c34d494ed2699f6b9793cf86f40c1efce657dc`.
- Runtime tree: `e33879ef6843c537aac03c69001e25c70e91c175`.
- Vercel deployment: `dpl_D5QinYMGKHoHPe7rof1Jwb5mkgCb`.
- Immutable URL: https://actforgoa-field-guide-h349fx0lt-zakkrevitt-gmailcoms-projects.vercel.app.
- Rollback baseline: `dpl_6Z5f6f1ZbXeXzJaY5qnGcdFdwZsH`.

The guarded release repeated all 281 tests and the production build, then passed staged research, editorial/staff authentication, public satellite readiness/session, map configuration, newsletter and MCP probes before promotion. The existing nonfatal Vercel `vite/client` function-transpilation diagnostic remains; the build and deployed service gates passed. The reader owner's documentation-only update was reconciled before publication without changing the tested runtime files. No guard was bypassed.

Final public verification covers forty successful route renders (twenty desktop and phone), all three category headings, all four expanded field-guide sections, actual carousel next/previous and pause state, the stationary exact heading and the shared footer mask. Published desktop/phone screenshots were inspected; no horizontal overflow or computed italic type was found. The artwork overlaps the links with a 605px illustration area on the checked desktop. Both local previews returned HTTP200 after publication. Original WordPress, backend settings and stored data are unchanged.

Final evidence: `.reports/home-refinement/{live-identity.json,live-routes.json,published-home.png,published-footer.png,published-phone.png,published-full-phone.png,release.log}`. This completion record is documentation only and excluded from deployment uploads.
