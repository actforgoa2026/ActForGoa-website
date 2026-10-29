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

## Spending is paused

The cloud dev workspace records a previous paid bar-query smoke test, but its reservation amount is not in this Mac's files. The authoritative files remain `/workspace/.research-private/allowance.json` and `/workspace/.research-private/usage/answer-usage.sqlite` in that executor. They are not the production ledger. The remaining portion of the approved additional $2 is therefore unknown. No new paid call was made in this local setup, and no accounting directory/zero baseline was created.

`backend/local_budget.py` fails closed unless a reconciled ledger and checksum-bound receipt exist. When enabled, it enforces one lifetime $2 total across all months, without resets/refunds; each actual provider HTTP attempt, including SDK retries, must reserve its conservative input/output cost atomically before dispatch. Failed attempts retain their reservation. The SDK's own session budget is a second guard, not the authoritative accounting mechanism. The backend alone holds the real key; the SDK receives a temporary localhost proxy capability.

To unblock: obtain a final, checkpointed export of the existing cloud DEV ledger and its allowance/provenance, after stopping that paid writer. Review the identity, existing receipts, amount and expiry. Then `dev/reconcile_dev_budget.py --help` describes the explicit import; supply the verified SHA256 and preserved allowance expiry. The importer rejects missing/inconsistent receipts, an over-cap ledger, a live WAL, or an existing local accounting directory. Never pass a production ledger, fabricate a zero baseline, or renew an expired allowance without authorization. Do not resume paused agents to obtain it. The workflow is prepared but actual Claude SDK generation remains unverified until this prerequisite is met.

## Focused validation and state

Twelve focused Python checks pass, including exhaustive catalogue/CRM enumeration, read-only SQLite behavior, lossless oversized pages, source exclusions, quote rejection, concurrent budget reservations and blocked paid chat. Eighteen relevant existing Node checks and TypeScript checking pass. Browser checks exercised keyword search, original PDF/full-text reading, new-tab links, Agonda authority lookup, live setting save/restore and responsive 1440/390/320 layouts. The UI explicitly says paid answers are paused.

Implementation is local on `codex/research-agent-local`, based on PR #106 at `2f73438295f0e1186267626f59ad642a2ade7d9b`. Shared unfinished work is untouched. No production build, deployment, merge, paused-agent activation or full release checklist ran. Cloud-specific historical setup remains in `PRIVATE-WORKSPACE.md`; its earlier missing-corpus statement does not describe this completed Mac copy.
