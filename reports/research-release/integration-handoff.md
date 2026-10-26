# Research release integration

The research backend is live and verified at https://research-production-b579.up.railway.app. `/healthz` returns ready and `/api/status` reports Zvec + FTS5 + reciprocal rank fusion, generation `20261022T155701-21661179`. The integration coordinator owns Vercel alias promotion.

Working tree: `/Users/zakkrevitt/.codex/worktrees/research-live/ActForGoa`; branch `codex/research-live`; PR https://github.com/ZakKrevitt/ActForGoa/pull/8. Application code is commit `a37c428bb2d272093580666c69d91541749b54e9`, including reporting main `f26ad87`. The final evidence commit adds this report and the frontend HTTP-verifier option; use the current PR head when integrating.

Deployment `c903cf22-f5ec-4b4f-ade4-fbcdbbab1598` is SUCCESS. Separate research service `f3c5348d-3bfe-47b0-98a4-22428580937f` in project `512430bc-234d-4582-b4dd-47770e3c9114` uses dedicated volume `b37ebdc4-355e-41e3-99e9-32421241a1ec`, mounted at `/data`. The existing reporting service and volume were not changed.

All 1,172 transferred files match their SHA256 checksums: 1,156 originals plus index and pointer files, 2,055,701,262 bytes. The corpus contains 21,220 pages/sections and 78,432 searchable passages. `remote-integrity.json` records complete verification; `corpus-manifest.json` records manifest SHA256 `afa9e3264dde6c1d496017770edf9c41ee0edabf709bd53a2aea5bba8576b64b`. The temporary transfer SSH key was revoked and its local key files deleted.

`public-http-verification.json` records six real Goa queries, all 30 exact passage identities, a full PDF SHA256, all 20 extracted-text pages and an original-page PNG against the live API. These are retrieval and citation-identity checks, not factual-entailment evaluation. Generated answers remain unavailable: the secure API-key flow did not approve/save a credential; the live service returns the explicit 503 source-search fallback. Do not claim live-generated chat.

The UI uses existing Manrope/Arc controls. Validation passed: 39 combined frontend/reporting tests, 18 research backend tests and production build. Desktop and phone browser checks covered real source search, citation navigation, full-document reading and preserved search state. Fresh Impeccable review: ship at visual scope. Existing extraction-quality and publication-rights caveats remain documented in RESEARCH.md.

Integrate routes and memory provider from `src/App.tsx` without overwriting newer work. Merge the four entries in `deploy/research/vercel-rewrites.json` with existing Vercel routing, replacing RESEARCH_SERVICE_HOST with research-production-b579.up.railway.app. Preserve reporting proxy and SPA fallback. No browser secret or VITE variable is required. The service allows writes from https://actforgoa-field-guide.vercel.app; other browser origins are refused. After deploying the combined site, run:

```sh
python3 scripts/verify_research_http.py https://actforgoa-field-guide.vercel.app --frontend --output reports/research-release/frontend-http-verification.json
```

Raw corpus/index/package are ignored and absent from Git. The local reproducible package is `.research-release/service` plus `.research-release/data`; checksums are in `.research-release/files.json`. Only indexed public-source originals were transferred. Python for independent tests: `/Users/zakkrevitt/.codex/worktrees/ecology-research-chat/ActForGoa/.venv/bin/python`; run `-m pytest tests/research -q` from this worktree so modules resolve from this checkout.
