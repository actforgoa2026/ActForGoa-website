# Local research workspace

The Mac workspace runs at <http://127.0.0.1:4276/ask>, with a loopback-only backend on port 8093. Research and catalogue/CRM have equal desktop width. On phones the panes stack. This is local development, with Vite HMR and Uvicorn reload; no build, deployment or hosted answer proxy is involved.

From `/Users/zakkrevitt/.codex/worktrees/research-agent-local/ActForGoa`:

```sh
.venv/bin/python dev/start_local.py
```

The isolated environment is already installed. For another environment, install `dev/requirements-local.txt` in a virtual environment and run `npm ci --ignore-scripts`. The launcher reads only `ANTHROPIC_API_KEY` from the existing server `.env.local` at `/Users/zakkrevitt/code/ActForGoa/.env.local`; it never prints or copies the value. The frontend does not inherit provider credentials. Port 4276 avoids another pre-existing process on 4176. Stop only this launcher's process group when restarting.

## Complete data and provenance

The authoritative local source is `/Users/zakkrevitt/.codex/worktrees/research-accounting/ActForGoa/.reports/anthropic-acceptance-20261027/data`. Its current manifest, SQLite tables and read-only live status endpoint agree on generation `20261027T065155-law-5bc5619b`:

| Data | Verified count |
| --- | ---: |
| Indexed documents and checksum-verified originals | 1,174 |
| Extracted pages | 21,534 |
| Original indexed passages | 79,564 |
| Low-text pages | 2,379 |
| OCR pages | 153 |
| Corrupt pages excluded by the original search | 56 |
| Duplicate source URLs | 25 |
| Public community CRM records | 499 |
| Public government CRM records | 2,768 |

The independent development copy is `/Users/zakkrevitt/.local/share/actforgoa-research-dev/corpus/20261027T065155-law-5bc5619b`. It contains every indexed original, all 16 immutable index files, per-document metadata, all extracted page text with page markers, and the complete catalogue. `READY.json` and `SOURCE-SHA256.json` record verification. Source and copied database SHA256 are both `c6d80208581f3776d2cfaa2cfe3ff08e026bd055be1c2a574461934fa52d870f`. Files are mode 0444 and directories 0555. SQLite readers also use read-only connections. No production usage/accounting file was copied.

The broader original archive is independently preserved at `/Users/zakkrevitt/.local/share/actforgoa-research-dev/original-archive`: 4,782 files from `/Users/zakkrevitt/code/ActForGoa/corpus`, excluding `.DS_Store`. This includes older/supplemental originals and extraction artefacts beyond the current indexed set. `ARCHIVE-SHA256.json` verifies all copied files. The archive uses separate APFS copy-on-write files, not hardlinks; original sources remain untouched. This file count is not an additional document count or an assertion that supplemental files belong to the current index.

The complete public CRM snapshot and read-only index are in `/Users/zakkrevitt/.local/share/actforgoa-research-dev/crm`. Version `directory-2026-10-23`, 3,267 records, SHA256 `838df16f19bf43bd3b9929b70e5e2a7ab6242254c707dc6c4aa3af45b2e5013e`, fetched from <https://actforgoa-field-guide.vercel.app/data/crm.json> and matching the repository snapshot. All public record fields, source URLs, verification dates/status and provenance notes remain present. Personal CRM notes/browser storage were not read or copied. Published contacts are not automatically current or independently verified.

## Agent and iteration

`backend/research_agent.py` uses Claude Agent SDK 0.2.174 with six read-only MCP tools: browse catalogue, search documents, read documents/pages, query CRM, read a CRM record, and request clarification. Built-in shell/filesystem tools, skills, plugins, persisted sessions and project/user setting discovery are disabled. The agent can make distinct searches, inspect complete pages through lossless continuation cursors, and ask a question for the next conversation turn.

`dev/agent-prompt.txt` is read on every answer. The Tune pane saves answer style, extra search terms and effort for the next request. Backend retrieval edits reload through Uvicorn; frontend edits update through Vite. Source text and original indexes remain immutable. Local retrieval searches every extracted page using FTS5 plus the existing premises-query expansion. The original vector index is preserved but not activated here; this runtime does not claim production hybrid-search parity.

Evidence retains generation, document ID, page, exact character span, source URL and warnings. The original manual source-review exclusions and corrupt-page warnings prevent those spans being used in answers. Every returned citation must identify retrieved/read evidence and include an exact quote from it. This validates traceability, not semantic correctness. Existing takeaway/deeper-detail rendering, follow-ups, document readers, new-tab references and location-based authority lookup remain available.

## Dev accounting reconciled; original allowance expired

On 30 October 2026 IST, the user authorized obtaining the existing dev accounting from the cloud chat “AI.” Its dev backend/relay were already stopped, with no in-flight requests. It exported a complete SQLite backup of `/workspace/.research-private/usage/answer-usage.sqlite`, together with the original `/workspace/.research-private/allowance.json`. No production accounting was involved. The export preserved four attempts and $0.441196 reserved, leaving $1.558804 under the original $2 cap. Every receipt and the gzip/SQLite hashes were verified before the explicit import.

The sealed imported baseline is `~/.local/share/actforgoa-research-dev/accounting/cloud-dev.sqlite`, SHA256 `97253d2d54c6d6cddbf80e1bf973e6f877d414245882947c461b6f068be5cae6`. The active continuation is `answer-usage.sqlite` beside it. All four original reservation rows remain identical. The cloud source was not changed; its file SHA256 differs because the export used SQLite's backup API, with every table row compared by the exporter.

One live local end-to-end request through Vite → backend → Claude Agent SDK → the bounded Anthropic proxy returned HTTP 502 after 20.59 seconds, without a verified answer. It reserved seven provider attempts totaling $1.282389. Total accounting is now 11 attempts and **$1.723585 reserved**, leaving **$0.276415**. These are conservative reservations, not a claim of actual invoiced cost. Failed/unknown attempts have not been refunded. No paid retry followed.

The imported allowance expired at **2026-10-29 18:54:01 UTC / 30 October 00:24:01 IST**. Its expiry and $2 cap were not extended. Status now explicitly reports expiry while retaining the exact balance, and chat rejects requests before dispatch. A successful live generated answer remains unverified; the remaining allowance is not currently authorized for dispatch under the preserved expiry.

`backend/local_budget.py` fails closed unless a reconciled ledger and checksum-bound receipt exist. When enabled, it enforces one lifetime $2 total across all months, without resets/refunds; each actual provider HTTP attempt, including SDK retries, must reserve its conservative input/output cost atomically before dispatch. Failed attempts retain their reservation. The SDK's own session budget is a second guard, not the authoritative accounting mechanism. The backend alone holds the real key; the SDK receives a temporary localhost proxy capability.

Do not run the importer again: the local accounting directory already exists and must never be overwritten. Further paid testing requires explicit renewed authorization with an adequate remaining allowance; carry forward every existing reservation. The cloud export envelope, original backup, live failure response and accounting audit are retained privately in `.reports/sdk-local-e2e/`. Export provenance also lives beside the ledger. No accounting, credentials or raw research data is tracked in Git.

## Focused validation and state

Runtime correction `bf00575` forwards the SDK's `anthropic-beta` and `anthropic-version` headers together with its body, following [Anthropic's gateway contract](https://code.claude.com/docs/en/llm-gateway-protocol). The initial proxy omitted those headers. This was a real compatibility defect; without the missing original per-attempt response trace, it is not proven to be the sole cause of the live failure. Safe local diagnostics now retain provider status/reservation IDs and SDK result subtype/tool names without credentials, prompts or source text. SDK-reported cost, when available, is an estimate separate from the conservative ledger.

Fifteen focused Python checks pass, including exhaustive catalogue/CRM enumeration, read-only SQLite behavior, lossless oversized pages, source exclusions, quote rejection, concurrent reservations, expired-budget blocking and proxy header forwarding using a synthetic upstream. A separate unpaid test boots the actual installed SDK subprocess against a localhost fixture and successfully executes all six tools, including two distinct searches, page reading, complete CRM-record reading, clarification and exact-quote validation. This is transport/tool validation, not live model acceptance. TypeScript checking passes. Current HTTP checks confirm the UI, Vite client/modules, font, catalogue and Agonda CRM endpoints return 200; expired chat returns 503 without changing accounting. The launcher uses Vite's runner config loader so configuration reloads do not rely on shared temporary bundle files.

Earlier browser checks exercised keyword search, original PDF/full-text reading, new-tab links, Agonda authority lookup, live setting save/restore and responsive 1440/390/320 layouts; eighteen relevant Node checks also passed during the initial setup. Those were not repeated as a release checklist. The present follow-up changes backend/accounting and development startup, not the interface design.

Implementation is local on `codex/research-agent-local`, based on PR #106 at `2f73438295f0e1186267626f59ad642a2ade7d9b`. Shared unfinished work is untouched. No production build, deployment, merge, paused-agent activation or full release checklist ran. Cloud-specific historical setup remains in `PRIVATE-WORKSPACE.md`; its earlier missing-corpus statement does not describe this completed Mac copy.
