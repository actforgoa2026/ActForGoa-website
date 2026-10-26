# Research release integration

Working tree: `/Users/zakkrevitt/.codex/worktrees/research-live/ActForGoa`. Based on main `04e721c`. Focused branch/PR pending final deployment verification.

Research API origin: `https://research-production-b579.up.railway.app`. Separate service ID `f3c5348d-3bfe-47b0-98a4-22428580937f` in project `512430bc-234d-4582-b4dd-47770e3c9114`; dedicated volume `b37ebdc4-355e-41e3-99e9-32421241a1ec`. Reporting service and its volume unchanged.

Status: initial Linux service running; 1.9 GB data transfer and checksummed verification in progress. Do not connect frontend until `/healthz` returns ready and the HTTP verification report is present. Cited generated answers are unavailable; secure API-key setup has not approved/saved a credential. Do not claim live-generated chat.

UI uses existing Manrope/Arc controls; 30 frontend tests,16 backend tests and build pass. Six real Goa HTTP queries pass locally with 30 passage identities, original PDF SHA256, every full-text page and original-page PNG checked. Fresh Impeccable review: ship at visual scope.

Integrate routes and memory provider from src/App.tsx without overwriting any newer work. Merge four entries in deploy/research/vercel-rewrites.json with existing Vercel routing; replace RESEARCH_SERVICE_HOST with research-production-b579.up.railway.app. Preserve existing reporting proxy and SPA fallback. No browser secret or VITE variable is required. The service allows writes from https://actforgoa-field-guide.vercel.app; preview chat submissions from other origins are intentionally refused.

Raw corpus/index/package are ignored and intentionally absent from Git. Local reproducible package .research-release/service and .research-release/data; checksums .research-release/files.json; corpus-manifest.json records the manifest digest. Only indexed public-source originals are transferred.
