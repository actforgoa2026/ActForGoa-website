# Guided topic restoration handoff

Source snapshot: `/Users/zakkrevitt/code/ActForGoa/.reports/topic-restoration-2026-10-26`

Runtime source is frozen and build-tested. Design documentation is being synchronised before the final seal. Source hashes are in `source-manifest.json`.

## Source identity and release status

- Working checkout HEAD: `878421e6f515a4fe3e3aa6d9c008e6310f8034ef`, with the current approved hero, stronger typography, original palette, discovery sections, reporting and guide corrections in the working tree.
- Restored menu logic originates from the previously merged topic work at `21d7362` / merge `9b827c1`, found in upstream history.
- Upstream at capture: `04e721cd3ad1a8daebc90c84d3cedb3ccbaf07f7`. CRM is not layered into this snapshot; the release orchestrator owns that integration.
- No commit, PR, Vercel deployment or alias promotion was made by this restoration turn. Independent publishing is held at the release coordinator's request.
- This full snapshot preserves the tested local runtime. Use the focused changes below to integrate rather than replacing unrelated upstream work.

## Focused restoration

- Restore `src/TopicPage.tsx`, `src/topic-flows.ts`, `src/topic-records.ts`, and `src/components/TopicIcon.tsx`.
- `src/App.tsx`: add `/topics/:slug/:actionId?/:choiceId?`, homepage explanatory buttons, and topic-specific choices in unqueried filtered catalogues. Keep its current hero, discovery, reporting, template and guide routes.
- `src/components/RecordCard.tsx`: extracted the current local card unchanged except recognising topic routes for Back to results. Retains source dates, draft labels, historical availability caveats and public-record sanitisation.
- `src/catalogue-loader.ts`: direct topic URLs load the public catalogue. `src/DiscoveryLinks.tsx`: topic links lead to topic menus.
- `src/topic-navigation.css`: larger bordered homepage and submenu buttons; `src/home-hero.css`: compacted hero padding to make room. Original paper/green palette and bold upright Manrope retained.
- Restored `18-service-enquiry.txt` in BOTH `corpus/guides/templates` and `public/guides/templates`; include its entry in `src/content/templates.json`.
- `src/template-model.ts`: a fillable greeting is a form block, not an uneditable note. `src/template-catalogue.ts`: standalone template labels fall back to their parsed title. Existing templates retain their behavior.
- Tests: `tests/topic-flows.test.ts` covers all menu leaves, destination/record/anchor/download integrity, curated services and cold route loading. `tests/guides.test.ts` and `tests/templates.test.ts` expect 18 templates; the template suite validates all filled text and DOCX exports.
- `src/guide-presentation.ts` was NOT created or changed. The local current guide presentation, draft status and verification caveats remain. The old upstream `guideForReaders` test was not copied into the restored topic test file because that separate helper is absent from this runtime. Preserve or reconcile that independent reader feature in the integrated checkout as appropriate.

## Verification

- `npm test`: 62 passed, 0 failed.
- `npm run build`: passed TypeScript app/server checks and Vite production build.
- Output main JS `index-CaOemWGg.js`; main CSS `index-BHzalREE.css`.
- 8 topics, 21 follow-up questions, 66 outcomes, 95 topic/menu/outcome URLs.
- Browser verified each topic on direct loads; waste -> collection -> household -> collection-service anchor -> service detail -> Back to results; dumping report branch; cold household URL resolves Bavish, V Recycle and Goa Waste Management Corporation.
- Desktop 1408x800, phone390x844, small phone375x667, tablet768x1024 inspected. No horizontal overflow. All eight homepage choices end at y835 on390x844; shorter phones scroll naturally.
- Evidence in `.impeccable/review/restored-topics/`: desktop-home, mobile-home, small-phone-home, tablet-home, desktop-waste, desktop-report, mobile-waste, mobile-collection, mobile-household PNGs; menu-checks.json and detector.json.
- Impeccable detector: zero primary findings; advisories describe restored neutral border/compact descriptions and inherited hero scrim/type exceptions. Changed visual source has no italic/oblique styling or decorative side stripes.
- Fresh finish reviewer found no material code or pixel defects; design-document update and final verdict pending.

## Snapshot exclusions

No environment files, credentials, node_modules, report submission data, research archive or Device Hub use. Files were APFS cloned to avoid a large disk allocation. Dependencies can be reused from the primary checkout for verification; the snapshot has the exact package lockfile.
