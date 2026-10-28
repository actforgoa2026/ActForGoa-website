# Research backend cloud handoff

The cloud branch implements scoped legal/ecology retrieval and one-call Anthropic answers. It has not activated or replaced the live research service. The local orchestrator owns key wiring, corpus restoration, acceptance and review-site release.

## API contract

- `GET /api/status`: existing readiness/generation/stats plus `provider: "anthropic"`, `domains: ["legal", "ecology"]`, `domain_counts`, `outside_context_supported: true`, `answer_mode: "library_first"`, and `chat_unavailable_reason`.
- `GET /api/search?q=...&domain=legal|ecology|all`: defaults to `all`; response echoes `domain`. Domain filters apply before both FTS5 and Zvec retrieval. Results include `domains`, legal-currency and guide-verification metadata.
- `POST /api/chat`: existing question/history/document/generation plus `domain` and `include_outside_context` (default true). Keeps `status`, `paragraphs` and `citations`; adds `coverage: full|partial|none`, `domain`, `library_notice`, and nullable `outside_context: {text, provenance: "model_knowledge", notice}`.
- An answer with no library support has `status: "insufficient_evidence"`, empty library paragraphs/citations, and may have clearly separated general AI context. This context is not a web search or a verified external source. Fully covered answers cannot include it. Disabling it avoids provider calls when no evidence is found.

The backend validates exact supporting quotes and citation identity, bounds answer length, retains source warnings and instructs the model to preserve duties, dates, population scope and uncertainty. These are attribution checks, not proof that every generated sentence is entailed. Live semantic acceptance is still required.

## What data is actually available in the cloud

The checkout contains canonical authored guides, seed registers and reviewed-source manifests. It does **not** contain the ignored full original corpus, metadata directory, prior index generations or production usage ledger. The cloud smoke index contains five authored draft guides and 131 passages. It must never replace the existing full public library.

Use the local coordinator's retained, checksum-verified corpus and accounting checkpoint. The previous live ecology generation and the later legal candidate were different; select by verified generation/manifest and source bytes, not merely by folder name. Preserve older published generations and originals for existing citation links. Do not open sealed preservation copies in native SQLite/Zvec; work on disposable copies.

## Add legal material without replacing ecology

There are two supported paths, depending on which source data the coordinator restores:

1. For the complete raw/metadata corpus, add guides with `python scripts/ingest_legal_guides.py --data-root /path/to/working-data --guide-root /path/to/checkout/corpus/guides`, then run `python scripts/build_research_index.py --data-root /path/to/working-data --ocr-pages 0`. This rebuild includes **all** available metadata, not only the guides. The guides carry authored-draft provenance and do not masquerade as official law.
2. For a packaged live index plus the retained verified official-source archive, run `python scripts/refresh_verified_legal_sources.py --base-root /path/to/live-data-copy --source-root /path/to/verified-source-copy --output-root /path/to/new-working-data`. This inherited tool checks the 26 reviewed originals by SHA-256, adds/reconciles their source metadata and passages, retains the old generation and publishes a new one only on success. Missing or mismatched bytes are a hard failure. Reviewed originals retain their legal-currency limitations.

The second path does not by itself add newly authored guide files; use a complete corpus rebuild if those must join the same generation. Do not run the full builder against a packaged corpus containing only raw/index files and no complete metadata: that could produce an incomplete replacement. Review document counts, domain counts, representative search results and original links before packaging.

Legacy index generations need no in-place schema migration. Sections derive from existing title/topic/provenance metadata where explicit domain labels are absent. This conservative classifier can miss a poorly catalogued document; verify and improve metadata in a new generation when needed. A section count does not assert exhaustive/current legal coverage.

## Preserve accounting and wire the provider

1. Keep dispatch disabled (`RESEARCH_CHAT_ENABLED=0`) while staging. Back up the existing durable `.research-usage/answer-usage.sqlite` with the coordinator's normal checkpoint procedure. Preserve its usage, spend, stage receipts and reconciliation receipts.
2. Reconcile only verified, non-overlapping validation deltas with `backend.usage_reconciliation` and unique receipts; the inherited utility supports read-only inspection and requires explicit initialization for a truly new ledger. Do not invent/import the same reservations twice or overwrite the production ledger with a test fixture.
3. Keep `RESEARCH_DATA_ROOT=/data/research`, the current dedicated Railway volume/service, `RESEARCH_PUBLIC_ORIGIN=https://actforgoa-field-guide.vercel.app`, and `RESEARCH_PUBLISH_CORPUS=1`. Preserve the existing `/api` rewrites and reporting service.
4. Through the existing secret store, supply server-only `ANTHROPIC_API_KEY`. The adapter contacts only `https://api.anthropic.com/v1/messages`, inherits normal proxy/TLS configuration, disables redirects, and does not retry automatically. No key is needed in Vercel/browser code.
5. Set `ANTHROPIC_CHAT_MODEL=claude-haiku-5-5`, `RESEARCH_MONTHLY_BUDGET_USD=5`, `RESEARCH_DAILY_ANSWER_LIMIT=100`, and `RESEARCH_REQUIRE_EXISTING_USAGE=1`. The model/rates were retained from the prior integration; verify availability and pricing when activating. Unknown model rates fail closed. The new runtime cannot raise the established $5/100 caps through these settings.
6. Preserve the ledger at the same data root. Missing accounting disables chat while leaving search available. Each dispatch now uses the existing atomic stage-reservation mechanism with a unique opaque receipt; failed calls and rejected answers remain charged. Do not reset the budget to get acceptance tests through.

## Fresh package and acceptance

Package the **new integrated source** using `python scripts/package_research.py --data-root /path/to/verified-working-data --output /path/to/fresh-release --stage-data`. Use a fresh output directory. This allowlist copies runtime/backend/model files and the selected index/originals; it excludes keys, unrelated raw archives and usage ledgers. Never redeploy an old sealed service package. Upload indexed data additively to the existing volume, preserving the older generations and separately preserved ledger.

Before enabling generated answers, check `/healthz`, `/api/status` domain counts, legal/ecology scoped queries, original source readers and old saved citation URLs. Confirm the existing ledger has capacity. Then enable `RESEARCH_CHAT_ENABLED=1` on the selected candidate service and perform a small, budgeted live acceptance set:

- A legal question whose official source includes a duty, an exception and a date; verify each against the cited text.
- An ecology question involving geographical/population scope; verify that Goa, Western Ghats and mere occurrence are not conflated.
- A partial-answer question: supported information stays under the library section, missing details are stated, and any general context is labeled outside the library.
- A no-match question with outside context enabled and disabled; no fabricated citations or web-search claims.
- A follow-up question and an unavailable/usage-limit response; search and original documents remain usable.

Inspect concise synthesis manually; passing quote validation alone does not establish semantic accuracy. Keep the exact response/citation and reservation evidence without exposing credentials or personal data. If acceptance fails, disable chat and retain charged reservations. The previous experimental multi-stage Anthropic pipeline was not accepted, and its failed results are not evidence for this new single-call implementation.

Finally run the integrated desktop/phone checks and `npm run release:review` through the root coordinator. Report code implemented, fixture tests passed, live-provider acceptance, deployment and alias verification separately.
