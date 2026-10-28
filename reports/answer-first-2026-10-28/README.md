# Answer first verification

The user requested a conversational answer grounded in the retrieved excerpts, with sources secondary. This change adds the editorial brief to the existing provider request, retains exact excerpt text with source locations, and prevents answer mode from silently becoming source search.

Validation on 28 October 2026:

- 121 Python research tests passed, including inspection of the actual HTTP request body sent through a mock Anthropic transport. Two complete excerpts, their qualifications and source locations reach the provider unchanged. Oversized excerpts are omitted whole rather than truncated; conversation history remains distinct from source evidence.
- 178 Node tests passed with `NODE_USE_ENV_PROXY=1 NODE_USE_SYSTEM_CA=1 npm test`.
- `npm run build` passed. The existing lazy PDF chunk size warning remains.
- `python3 tests/research/answer_first_browser.py --base-url http://127.0.0.1:4193` passed nine scenarios at 1440, 390 and 320 pixels, with no page errors. Checks cover answer-first order, collapsed sources, exact-passage navigation and return, follow-up context, failed generation and explicit source browsing while generation is unavailable.
- Rendered desktop and phone screenshots were inspected against the existing design guidance. The Impeccable skill was not installed in this executor; no Impeccable pass is claimed.

`browser.json` records the scenarios. The PNGs use explicitly synthetic API responses, not generated answers or private corpus data. `validation.json` hashes the three runtime files tested. No paid provider calls, full-corpus semantic acceptance or deployment occurred during these checks. The existing hybrid retriever is unchanged; the new brief guides evidence reading and selection within the answer request, not an additional retrieval model.

The active focused release owner must combine this change with the citation-contract corrections before validating and packaging the final runtime. Prior prompt acceptance does not transfer to these changed instructions. Full-corpus/accounting preservation, existing acceptance requirements and hosted verification remain required for activation.
