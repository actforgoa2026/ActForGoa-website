# Goa satellite service

Read [the consolidation plan](../../docs/GOA-MAP-INTELLIGENCE-PLAN.md) for product scope and acceptance. This service is exploratory, not an automated allegation or alert system.

Local launch from the repository root:

```sh
python -m venv .venv
.venv/bin/pip install -r deploy/satellite/requirements.txt
.venv/bin/python -m satellite.run
```

The launcher loads ignored `.env.local` without overriding injected variables. Do not use a shell `source` command to load credentials. Runtime listens on `0.0.0.0:${PORT:-8092}`. Use one worker and one replica. Access logs are off; provider errors and secret values are not echoed.

| Service variable | Purpose |
| --- | --- |
| `CDSE_CLIENT_ID`, `CDSE_CLIENT_SECRET` | Copernicus Data Space Sentinel Hub OAuth client credentials |
| `ANTHROPIC_API_KEY` | Natural-language interpretation; existing provider connection may be reused |
| `SATELLITE_ANTHROPIC_MODEL` | Defaults to `claude-haiku-5-5`; verify model access before activation |
| `OPENAI_API_KEY` | Optional Decisions image classification with `gpt-6-luna`; absent key is shown as unavailable |
| `SATELLITE_CLASSIFIER` | Defaults to `openai-decisions`. `anthropic` explicitly opts into Anthropic vision; `auto` uses OpenAI when configured, otherwise Anthropic. Failed calls never retry on another provider. |
| `SATELLITE_VISION_MODEL` | Anthropic vision only; defaults to `claude-sonnet-5-5` |
| `SATELLITE_RESEARCH_ORIGIN` | Optional exact HTTPS origin of the existing research search service; requires explicit ecology-domain confirmation in `/api/search`. No research generation calls. |
| `SATELLITE_SERVICE_TOKEN` | At least 32 random characters, shared only with the authenticated admin backend |
| `SATELLITE_MCP_TOKEN` | Separate token, at least 32 random characters, for intended MCP clients |
| `SATELLITE_DATA_DIR` | Persistent private directory, e.g. `/data/satellite`; jobs and usage reservations |
| `RAILWAY_PUBLIC_DOMAIN` | Railway-provided hostname used to permit the hosted MCP endpoint |

The admin backend receives `SATELLITE_API_ORIGIN` (exact HTTPS origin) and the same `SATELLITE_SERVICE_TOKEN`. Browser calls remain under `/api/admin/satellite/*`, so the existing HttpOnly session cookie and CSRF checks apply. No browser receives either provider keys or the service token. Existing admin deployment must be repackaged to include `server/satellite-proxy.ts`; Vercel retains the existing `ADMIN_API_ORIGIN` transport.

Production packaging after committing tested source:

```sh
python scripts/package-satellite.py --output .reports/satellite-release
```

Deploy the resulting `service/` directory to a **new** Railway service, with a persistent `/data/satellite` volume. Do not replace research or reporting. Add service-only variables through secure configuration; never copy injected credential placeholders into another deployment. `/healthz` is liveness only. Authenticated `/status` reports credential presence, not proven provider authorization. Verify real calls before saying retrieval is ready.

Routes: `GET /status`, `POST /plan`, `POST /catalog`, `POST /compare`, `GET /jobs/{id}`, `POST /history`. Non-health REST routes require `Authorization: Bearer <service token>` plus a verified `X-Actor-ID` supplied by the admin server. Jobs and history can be read only by their actor. History returns metadata, not PNG bodies; date filters overlap actual acquisition intervals. `/mcp` uses a separate bearer token and a separate job namespace; the four original tools use the same service logic. The MCP SDK is pinned below 2. No arbitrary URLs, filesystem save paths or evalscripts are accepted.

Persistent limits reserve 30 plans, 100 catalog operations, 10 comparisons and 10 image-classification attempts per UTC day for the whole satellite service, including failed attempts. A comparison revalidates its catalog and consumes a catalog reservation. Each catalog operation permits at most three pages; at most one comparison runs concurrently. These are request caps, not a currency budget; verify pricing/account limits before enabling broader use. They do not reset or modify the existing research usage ledger. Jobs interrupted by a restart fail explicitly instead of rerunning paid requests. Results older than 30 days are removed on startup and when starting a comparison; history excludes expired entries. Existing job databases migrate without resetting reservations or completed results.

Tests: `.venv/bin/python -m pytest tests/satellite -q`, `NODE_USE_ENV_PROXY=1 npm test`, `npm run build`. Mocked provider tests establish contracts, not real imagery accuracy. Before review-site promotion: actual CDSE OAuth/catalog/process, Decisions inference, named-user browser auth, desktop/phone checks, and representative Goa evaluation. Use the repository's coordinated release workflow; no independent alias promotion.

For a bounded live catalog check, run `.venv/bin/python scripts/validate-satellite-live.py --bbox 73.82 15.48 73.83 15.49 --start-date 2026-09-18 --end-date 2026-10-28 --output .reports/cdse-catalog`. To retrieve a pair, use a new output directory and add `--before-id` and `--after-id` with exact IDs returned by the catalog. There are no automatic retries or model calls. Reports include response status, processing units when supplied, provenance, grid checks and numeric evidence; raw imagery stays in the chosen private directory. See [the real provider validation](../../reports/satellite-live-2026-10-28/README.md).

The development `Dockerfile` accepts an optional BuildKit `proxy_ca` secret for managed development networks. Build with `--secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt` when needed. The CA is mounted only during installation and is not copied into the image. The production packager selects `Dockerfile.railway`, because Railway's current builder rejects secret mounts even when they are optional. This file uses normal verified package downloads.

For the separate satellite frontend, run `node scripts/package-satellite-app.mjs --output <new-directory>` from clean committed source. It builds a satellite-only React entry and stages the existing named-account authentication plus proxy; it excludes the research corpus, public catalogue, accounts and credentials. Deploy its `service/` directory to a separate service with `/data/admin`, `ADMIN_PUBLIC_ORIGIN`, `SATELLITE_API_ORIGIN` and the shared server-only `SATELLITE_SERVICE_TOKEN`. The browser and authenticated proxy share one origin. The existing editorial service is untouched.

Upload each allowlisted service directory with `railway up <package>/service --path-as-root --no-gitignore` and explicit project, environment and service IDs. The last flag is required to include the generated frontend bundle, which is intentionally ignored by Git. Never use this flag against the repository root. See [the standalone release](../../reports/satellite-standalone-2026-10-28/README.md).

After an authorized OpenAI key is configured, the separate bounded smoke command is `.venv/bin/python scripts/validate-satellite-decisions.py --recorded-run .reports/cdse-live-20261028-bundled --output .reports/decisions-live-20261028`. It loads `.env.local` without overriding injected values, verifies existing TIFF hashes/provenance, and makes one Decisions call without new CDSE retrieval. Use a new output directory. A fixed private ledger reserves one validation attempt per UTC day, including failures; do not reset it or automatically replay failed requests. Inspect the sanitized report before copying reviewed evidence into Git.
