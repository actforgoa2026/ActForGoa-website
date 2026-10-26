# Reporting audit source handoff

Prepared 26 October 2026 for the release integration chat. This package was based on `origin/main` at `04e721c`. It restores the audited reporting service, shared validation and retry identity, nine reporting regressions, local run script, separate Railway deployment recipe and operational documentation. The frontend integration remains with the integration chat. No production deployment is part of this package.

## Source provenance

Original workspace: `/Users/zakkrevitt/code/ActForGoa`.

Audited source: `/Users/zakkrevitt/code/ActForGoa/.reports/frontend-release-2026-10-26`.

Newer frontend source selected by the integrator: `/Users/zakkrevitt/code/ActForGoa/.reports/discovery-release-2026-10-26`.

The following files are byte-identical between both frozen snapshots: the five reporting frontend files (`ReportIncident.tsx`, `ReportInbox.tsx`, `reporting.css`, `report-api.ts`, `use-report-draft-guard.tsx`), `server/reporting.ts`, both files under `shared/`, `src/catalogue-loader.ts`, `src/content-corrections.ts`, `src/search-navigation.ts`, `tsconfig.server.json`, `vite.config.ts`, and `vercel.json`. Their SHA-256 values are recorded in `reporting-source-provenance.json` beside this document. Both test files, `tests/reporting.test.ts` and `tests/audit-regressions.test.ts`, also match the newer discovery snapshot and the shared workspace.

Seven files are missing from the discovery snapshot and recovered here from the original workspace:

- `scripts/dev-reporting.mjs`
- `scripts/package-reporting.mjs`
- `deploy/reporting/Dockerfile`
- `deploy/reporting/railway.json`
- `deploy/reporting/package.json`
- `deploy/reporting/package-lock.json`
- `docs/REPORTING.md`

The backend, shared schema, retry identity, reporting tests, TypeScript server configuration and Vite proxy are unchanged from the verified source. The packaging script now copies three named source files instead of recursively copying `server/` and `shared/`, so another backend or local file cannot enter this service's deployment package. Documentation distinguishes prior release evidence from current integration checks. The root package scripts and Sharp dependency were applied as small changes to current main; unrelated frontend dependencies were not copied. Private reporting data is excluded by both `.gitignore` and `.vercelignore`; the separate backend deployment folder is excluded from Vercel.

Do not copy `.reports/deployment` as maintained source. The last deployed image contained a one-time, exact-ID and exact-description cleanup of two synthetic audit reports. The canonical Dockerfile here starts the server normally and omits that cleanup.

## Frontend integration requirements

The integration chat owns `App.tsx`, `main.tsx`, shared styles, hero/feed, guided topics, CRM, guides/templates and research. This package changes none of their implementation files.

- Keep the lazy `/report` and `/reports/review` routes and the public reporting entry under Take action. The review inbox is private.
- Preserve the native full-width category buttons in `ReportIncident.tsx`, `aria-pressed`, selected check mark, and 88px minimum height in `reporting.css`. The user explicitly rejected radio controls.
- Retain the data router because the draft guard uses `useBlocker`. Keep reporting routes independent of catalogue/model loading.
- Extend the frozen `needsCatalogue` predicate for restored `/topics/...` routes: current-main `TopicPage` receives the catalogue. Do not blindly retain the snapshot's older route list. CRM loads its own source; preserve its current-main behavior.
- Retain independent-page navigation and retry behavior when restoring topic routes. Keep unknown-filter recovery, collection-preserving search and explicit opt-in meaning search.
- Keep Vercel's SPA fallback exclusion for `/api/`, assets, data, models, guides and WASM. Missing API routes must not return the frontend HTML.
- Frontend production build requires `VITE_REPORT_API_ORIGIN=https://reports-production-42c8.up.railway.app`. Local development leaves it unset and uses the included Vite proxy.

The general website audit evidence remains at `reports/audit-2026-10-26/AUDIT.md` in the original workspace. It covers source-backed historical/legal corrections, emergency pathways, catalogue failure recovery, optional semantic loading, guide splitting, filter preservation, titles/focus, contact-form resets and readable line lengths. That evidence and `tests/audit-regressions.test.ts` belong with the complete recovered frontend; those tests cannot run against unmodified current main because their frontend helpers are absent there. Preserve corrections as a presentation layer, without changing archive evidence or overriding newer guide verification.

## Deployment identity and public configuration

These identifiers describe the audit release verified at `2026-10-26T09:02:55.451Z`, not the latest deployment after other chats' work.

| Item | Value |
| --- | --- |
| Site | `https://actforgoa-field-guide.vercel.app` |
| Audit frontend deployment | `dpl_BBrSnaBpJ7sMo87QZE4Rxe4nNioU` |
| Immutable audit frontend URL | `https://actforgoa-field-guide-lndm259vl-zakkrevitt-gmailcoms-projects.vercel.app` |
| Reporting API | `https://reports-production-42c8.up.railway.app` |
| Backend deployment | `fc6d3dda-8ab9-471e-a119-3d2ff2ef48bd` |
| Backend image | `sha256:f74108984ce6bb0f4d96a7a4db0ddbf73bf74267b2c266a6f4f1814bab0ac8f2` |
| Railway project | `actforgoa-reports`, `512430bc-234d-4582-b4dd-47770e3c9114` |
| Railway service | `reports`, `0b1b9b42-453d-420f-a8f5-0c30312860ac` |
| Railway production environment | `58d08288-6d66-48d7-a6a4-9e07370c814c` |
| Persistent volume | `/data`; database `/data/private/reports.sqlite`; one instance |

Backend public environment values:

```dotenv
NODE_ENV=production
PORT=4187
REPORT_HOST=0.0.0.0
REPORT_DATA_DIR=/data/private
REPORT_PUBLIC_ORIGIN=https://actforgoa-field-guide.vercel.app
REPORT_TRUST_RAILWAY_PROXY=true
```

`REPORT_REVIEW_TOKEN` must remain a separately provisioned server secret. No key is included in this branch, manifest or documentation. Proxy trust is limited to the previously verified isolated Railway HTTP ingress and is also gated by `RAILWAY_PROJECT_ID`; do not transfer it to an unverified host or add a direct/TCP ingress without reassessing that boundary.

Daily volume backups were verified with 518400-second retention. Post-audit manual backup ID: `49018352-3d8d-4a5b-adfb-aff19cadf69d`. Restoring a backup has not been tested.

## Verification boundaries

Current isolated package: 39 automated tests passed, including all nine reporting tests. Frontend and backend TypeScript checks passed. Both scripts passed syntax checks. A package smoke check confirmed exactly seven allowed files, exclusion of a synthetic private-file fixture and the old cleanup script, successful startup through the packaged CLI, a healthy configuration response and a 401 for anonymous inbox access. Its temporary process and database were removed after the check. Existing dependencies were reused through a symlink to avoid another installation on a nearly full disk. A clean dependency installation, Docker image build, frontend Vite build and browser walkthrough were not repeated for this package; the integration chat owns the final combined build and browser verification.

Reporting regressions cover atomic report/photo persistence across restart, EXIF removal, private inbox/photo authentication, absence of a public detail endpoint, deduplication and changed-payload conflict, validation and consent, image/count validation, exact-origin CORS and preflight, submission rate limiting, untrusted forwarding headers, stable cursor pagination, malformed updates, impossible dates and monotonic review revisions.

The prior audit release passed a full build and 57 tests, and reporter/inbox flows were inspected at 390 × 844 and 1440 × 1000. Synthetic production submission, API image upload, metadata removal, private review and persistence across a real service restart were verified. Both synthetic records were removed using exact identifiers and matching descriptions. This earlier evidence does not validate the later combined integration.

Remaining limits: Safari/VoiceOver and physical devices, GPS permission, physical camera and HEIC conversion, final native file-picker recheck, field Core Web Vitals, final saved PDF output and backup restoration were not verified. Review is manual with a shared key; there are no individual reviewer identities, notifications, public status lookup or automatic authority forwarding. SQLite has no application-level encryption or automatic retention/deletion policy. Historical sources and external-service availability retain the qualifications in the original audit and guide registers.
