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
