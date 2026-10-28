# Cloud implementation verification

All development, indexing, builds and browser checks for this change ran in the cloud. This evidence supports the implementation PR; it is not a live deployment or a successful live Anthropic call.

- 178 TypeScript/Node tests passed with `NODE_USE_ENV_PROXY=1 npm test`.
- 118 research tests passed with `.venv/bin/python -m pytest tests/research -q`.
- Production TypeScript/Vite build passed. PDF creation is lazily loaded; pdfmake triggers Vite's standard large-chunk advisory.
- 36 route/layout/provenance browser checks passed with cloud Chromium, including desktop, 390px phones and selected 320/360px checks. No JavaScript page errors or horizontal body overflow remained.
- The actual disposable editorial service passed browser login, curation, draft privacy, publish, saved-edit isolation, republish and public journal flows. Independent backend/proxy checks verified paginated published lists, proxy-aware login limits, and a 90,000-character Devanagari draft.
- A real Zvec/MiniLM index of the five canonical draft guides (131 passages) supported legal/ecology source-search and document-reader checks. It is only test data and must never replace the full production corpus.
- Answer provenance screenshots use a clearly identified UI fixture. Provider behavior/citation tests use HTTP mocks. No live provider calls were made; source-attribution checks do not prove semantic accuracy.
- All 18 authored forms produced actual PDFs. The forms workstream checked desktop/phone downloads, Unicode, conditional content and long tables; see `../FORMS-CLOUD-20261028.md`.

`verification.json` records results and hashes of runtime source files. `browser-routes.json` and `browser-admin.json` record actual checked routes and widths. Screenshots contain only public data and a disposable QA account/story. The overview capture includes its transient loading state; successful service behavior is recorded separately in the browser flow evidence.

The installed Impeccable skill was unavailable in this cloud. Existing DESIGN.md/Arc components were followed and rendered screens were inspected. Exact Disco parity still needs the unavailable local reference. Current original-site, deployment, model-key and corpus restoration steps are in `../../docs/CLOUD-IMPLEMENTATION-PLAN.md`.

## Shipping review follow-up

The two fresh GitHub review findings are resolved by `ca66564` and `b222ceb`: stories cannot use the reserved archive route, and unsaved edits are protected during Back/Forward, router links and local tool changes. Saving prevents discard until its response completes. The combined Node suite and production build passed again. Research runtime files are unchanged, retaining the earlier 118-test result.

`browser-shipping.json` records 10 additional integrated checks against the real disposable admin backend on desktop (1440px) and phone (390px), with zero page errors. Back and Forward were each exercised against existing same-document history entries with both keep and discard choices. Draft saves remained private. `admin-history-guard-phone.png` shows the inspected phone dialog without overflow. Agent fixture checks separately covered an in-flight save; they do not substitute for the real-service checks.

Merge and deployment status are recorded separately in PR #90 and coordination issue #89. No deployment or paid provider call was performed during this follow-up.
