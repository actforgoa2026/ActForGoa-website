# Research hosting

The research API runs as a separate Railway service. It never uses the reporting service or its database. The Vercel site calls same-origin `/api/status`, `/api/search`, `/api/documents/...` and `/api/chat`, forwarded through external rewrites. Keep reporting rewrites and other routes intact.

## Package and deploy

1. Build and verify an immutable generation locally. Keep original files and older published generations in backups.
2. Run `python scripts/package_research.py --data-root /path/to/corpus-checkout --stage-data`. The ignored `.research-release/service` contains only runtime code, pinned requirements, the bundled embedding model and Docker configuration. `.research-release/data` contains only the current generation and its indexed original files. The staging command uses APFS clones on macOS to avoid duplicating gigabytes. `files.json` records every file checksum; `manifest.json` records the generation and manifest checksum. Omitting `--stage-data` instead creates a compressed archive.
3. Use a dedicated service with a dedicated persistent volume mounted at `/data`. Upload the staged data directory to `/data/research`. Do not upload `.env.local`, CRM data, reports or unrelated archives.
4. Set `RESEARCH_PUBLIC_ORIGIN` to the exact frontend HTTPS origin, `RESEARCH_PUBLISH_CORPUS=1`, `RESEARCH_DATA_ROOT=/data/research`, and `RESEARCH_DAILY_ANSWER_LIMIT=100`. Railway supplies `RAILWAY_PUBLIC_DOMAIN`; optional `RESEARCH_ALLOWED_HOSTS` accepts comma-separated exact hostnames. Wildcards are rejected.
5. Deploy `.research-release/service` with `railway up ... --path-as-root`, explicit research service/project/environment selectors. One replica and one worker are required for this embedded index and aggregate limiter. `/healthz` must return `ready:true` before frontend promotion.
6. First-volume bootstrap only: Railway's volume file tools require an active deployment. A temporary service package can use `/api/status` as its health check, which truthfully reports `search_ready:false` before data arrives. Keep frontend rewrites disconnected. Upload data, restore the checked-in `/healthz` configuration and redeploy before release. Revoke any temporary SSH transfer key afterward.
7. Replace `RESEARCH_SERVICE_HOST` in `vercel-rewrites.json`, inserting the four entries before the site's existing SPA fallback. Do not replace the complete Vercel configuration or reporting API proxy. No client-side API key or `VITE_*` research secret is needed.
8. Run `python scripts/verify_research_http.py https://your-api-origin` and repeat with the frontend origin and `--frontend` after integration. The frontend flag checks its four same-origin API rewrites; `/healthz` is only on the backend. Verify desktop and phone research/document views.

The packaged runtime includes the local embedding model; queries do not need an embedding provider. Zvec and SQLite are opened read-only. Rebuild into a new generation and switch `CURRENT.json` only after the complete data is present, then restart. Retain earlier generations and their originals for already-published citations. A persisted volume is not a backup; keep the local checksummed archive and configure volume snapshots through the hosting account's normal backup process.

## Generated answers

Source search, extracted text, original downloads and rendered PDF pages work without an OpenAI key. `/api/status` reports `chat_ready:false`, and `/api/chat` returns a clear 503 until a server-only `OPENAI_API_KEY` has been securely provisioned. Set it through the secure setup flow or the hosting secret store, never a command argument, repository file or frontend variable. `OPENAI_CHAT_MODEL` defaults to `gpt-5-mini`. Restart after adding the key and run a separate live-provider answer/citation test; fixture tests are not evidence of live chat.

The daily answer limit reserves attempts before provider calls and persists across restarts. Aggregate search is limited to 120 requests per minute; search concurrency is four and answer concurrency is two. Request bodies are limited to 64 KiB. These bounds protect a small public service but are not user authentication or a distributed abuse-control system. Cross-origin browser writes are rejected; API access itself remains public.

## Sources and operational limits

The user-authorized release publishes the indexed public-source corpus. Available source provenance and rights metadata are retained, including unknown rights; indexing does not assert ownership, legal currency, or a redistribution licence. Originals are served as attachments, and archived HTML is never trusted application HTML. PDF page numbers refer to physical pages. English OCR and extraction may contain errors; original pages remain available for checking tables and numbers. Review and update the collection as sources change.

References: [Railway volumes](https://docs.railway.com/volumes), [Railway CLI deployments](https://docs.railway.com/cli/up).
