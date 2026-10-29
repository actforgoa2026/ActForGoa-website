# Private live research workspace

This workspace serves actual Vite development modules and a locally editable FastAPI answer workflow. It does not serve a static deployment or proxy generated answers from the production answer endpoint. Vite serves source on demand; a revision poll refreshes the frontend after source edits. Uvicorn reloads backend code. The workbench saves answer instructions, query vocabulary, passage count and reasoning effort for the next request without restarting, building or deploying.

The source index is read-only and remains hosted. Local retrieval interpretation calls its search endpoint, then the local generation pipeline selects complete passages, applies the current prompt and validates exact citations. Changing the corpus, chunking or embedding index still requires a separate candidate index; the workspace does not pretend the full corpus exists locally.

A Vercel running sandbox relays authenticated browser requests over outbound HTTPS to this cloud executor. The gateway blocks unauthenticated HTML, source and API access. Its invitation fragment is exchanged for an HttpOnly, Secure, SameSite=Lax cookie. Invite/relay secrets are outside Git under `/workspace/.research-private/`, with owner-only filesystem permissions. Provider credentials remain in the original managed executor. No arbitrary shell, provider key or quota-editing API is exposed in the browser.

The user explicitly approved up to $2 **additional** dev AI spend on 29 October 2026. `/workspace/.research-private/allowance.json` controls the amount and expiry; it is not browser-editable. The separate SQLite ledger is `/workspace/.research-private/usage/answer-usage.sqlite`. Reservations, including failed answers, persist. Never delete or reset it. No allowance file means no paid dev calls. Production's ledger, budget and runtime are unchanged.

The running sandbox was extended to about five hours from creation. The gateway URL and sandbox session ID are in `/workspace/.research-private/connection.json`. It is session-based: the sandbox, relay worker and local services must all be running. The source and dev ledger persist in this executor; a stopped sandbox must be resumed or replaced and its invitation renewed through the existing account, never represented as permanently online.

After gateway setup, run with the repository Python environment:

```sh
.venv/bin/python dev/start_private.py
```

The initial session was started as three separate supervised tool sessions: backend 8093, Vite 4176, and `dev/relay_worker.py`. Stop those before using the combined launcher. Gateway management uses Vercel's sandbox REST API with the existing project's scoped credential; never copy provider secrets into it. Its only files are the gateway and its own access secrets. The prior public preview alias's anonymous access override was revoked.

One bounded live answer for the original bar scenario passed: four cited paragraphs, four cited sources, about 1.2 seconds retrieval and 12.9 seconds provider time at medium effort. Its conservative reservation remains in the dev ledger. This is a connectivity/contract smoke check, not broad semantic acceptance. Settings were changed and restored through the private gateway without a build/deployment. Unauthenticated API access returned 401; authenticated pages served `/@vite/client` source.

## Full CRM snapshot

The complete published CRM snapshot is local at `/workspace/.research-private/crm/snapshot.json`, with a read-only SQLite/FTS5 index at `crm.sqlite`. Version `directory-2026-10-23`: 499 community and 2,768 government records (3,267 total); SHA256 `838df16f19bf43bd3b9929b70e5e2a7ab6242254c707dc6c4aa3af45b2e5013e`. This is the full current published snapshot, not a claim that all real-world organisations or later CRM edits are covered. Personal CRM notes and private workflow data are excluded.

The private workbench includes CRM search. Read-only agent-facing endpoints are `/api/dev/crm/stats`, `/api/dev/crm/search?q=...&collection=community&location=...&limit=20&offset=0`, and `/api/dev/crm/records/{record_id}`. Empty queries browse the complete selected collection with pagination; government/all are explicit collection choices. Responses retain provenance and verification status. Reading or searching does not contact organisations or send data to an AI provider.

## Full research corpus restore

The full research corpus has not yet been restored here. Railway management access is blocked: the configured credential binding targets `backboard.railway.app`, while the documented API at `backboard.railway.com/graphql/v2` returns `Not Authorized` with the current environment configuration. The user has been asked to correct the credential destination; no token should be pasted into chat.

Once a complete read-only export is accessible, run `scripts/restore_agent_corpus.py --source <export-root> --destination /workspace/.research-private/corpus/<generation>`. The importer checks every original against document metadata, rejects symlinked index content, copies only the immutable generation/indexed originals, and exports every document's full extracted page text and catalogue. It never copies the production usage ledger. `READY.json` is written only after the source and copied database checksums agree and all document text has been exported. This importer is prepared but has not been run on the missing full corpus.
