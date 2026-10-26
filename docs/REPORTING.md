# Private incident reporting

Verified deployed on 26 October 2026 at https://actforgoa-field-guide.vercel.app/report, with the private inbox at /reports/review. Vercel serves the frontend; an isolated Railway service stores reports and photos on a persistent volume. Nothing is published or forwarded to an authority automatically. This records that audited release, not the status of a later deployment.

This source-control package restores the backend and operational tooling. The frontend routes, reporting components and general website audit changes are being restored separately by the release integration chat. See [the integration handoff](REPORTING-INTEGRATION.md) for exact provenance, configuration and verification boundaries. This package alone does not add `/report` or `/reports/review` to the current-main frontend.

## Run

Use Node 24. `npm ci`, then `npm run dev`. This starts Vite on `127.0.0.1:4173` and the reporting service on `127.0.0.1:4187`. Ctrl-C stops both. If needed, `npm run dev:web` and `npm run dev:reports` run them independently. `REPORT_PORT` overrides the backend port for both processes.

- Submit: http://127.0.0.1:4173/report (also under Take action).
- Review: http://127.0.0.1:4173/reports/review.
- The local reviewer key is generated at `.reports/reviewer-token`. Open that file locally and paste its contents into the Review key field. Do not put it in a URL, commit it or use a `VITE_` environment variable.
- Reports, normalized photos, review notes and review history live in `.reports/reports.sqlite`. These files are private and ignored by Git and Vercel. The directory is created with owner-only permissions; the SQLite file and token are mode 0600. SQLite is not encrypted at rest; use host/disk encryption and restricted filesystem access.
- Local mode visibly identifies itself, including on receipts. It does not contact a live review team.

## Reporter flow

1. Choose illegal burning, illegal dumping, illegal tree cutting, water pollution, or another concern. Describe observations without claiming a legally confirmed violation.
2. Attach up to three optional JPG, PNG or WebP photos, no more than 8 MiB each. Invalid images and images above 40 megapixels are rejected. HEIC must be exported to JPG first. The server decodes, auto-orients, resizes to at most 2048px, and re-encodes photos as JPEG without embedded metadata. Originals are not retained; the form tells reporters to keep them for official complaints.
3. Enter a place or landmark and the observation date/time. GPS is optional, explicitly requested by the user, and has manual-coordinate and written-location alternatives. Coordinates and any accuracy estimate are shown before sending. No map/geocoding provider receives the location.
4. Optionally supply an email; consent to private review and submit. A receipt appears only after the database transaction commits. The client reuses an idempotency key on retries. Drafts remain in memory while moving between steps; they are not saved to browser storage, and a confirmation protects unfinished drafts on internal navigation and tab unload. The same exact payload keeps its retry identity even after returning to earlier steps.

Reviewers can read all fields and photos, add a private note and set New, In review, Resolved or Closed. Updates check the previous modification timestamp to prevent silent overwrites and append a review event. The review key is held only in tab memory. Shared-key authentication is intended for a small initial reviewer group; it does not identify individual reviewers. There is no email notification or public status lookup.

## Storage and API

The service uses Node's SQLite module with WAL and transactions. Report records and image BLOBs commit together. Parameterized SQL, bounded request size, two concurrent uploads, image decoding and re-encoding, a honeypot, and a submission-attempt limit are implemented. The built-in limit is 20 attempts per client per hour and persists in the database. Socket addresses are used by default. Only the isolated Railway production service opts into its edge-supplied X-Real-IP header; no TCP proxy or other service shares that environment. Raw addresses are hashed before storage. Do not enable proxy trust on other hosts without verifying their ingress boundary. Invalid submissions do not store partial reports. Unexpected server errors do not expose database paths or report contents.

All API responses are `no-store`. The submission endpoint returns only a reference and timestamp. Reading the inbox or a photo and changing a status requires the reviewer bearer token. There is no public report-detail endpoint. Cross-origin browser requests are permitted only from the configured REPORT_PUBLIC_ORIGIN, including explicit preflight headers for uploads and authenticated review. Other origins receive 403. The frontend VITE_REPORT_API_ORIGIN is a public service URL, never a secret.

## Hosting this service

The existing Vercel site is static. Deploying only its `dist` folder does not activate submissions. The form detects an unavailable reporting API, retains the in-memory draft and disables sending. The Vercel fallback excludes `/api/`, so missing APIs are not disguised as HTML success responses.

The included service can serve the built site and API together on a persistent Node 24 host, behind an HTTPS reverse proxy:

```sh
npm ci
npm run build
NODE_ENV=production \
REPORT_PUBLIC_ORIGIN=https://reports.example.org \
REPORT_DATA_DIR=/persistent/private/actforgoa-reports \
REPORT_STATIC_DIR=dist \
REPORT_REVIEW_TOKEN="$ACTFORGOA_REVIEW_SECRET" \
npm run start:reports
```

Use a securely provisioned random secret of at least 32 characters in `ACTFORGOA_REVIEW_SECRET`; the example domain must be replaced with the actual origin. The service refuses production startup without a token and HTTPS origin. It binds to loopback by default; configure `REPORT_HOST` only for the hosting network boundary. Run a single service instance against the durable volume. Ephemeral serverless disk is not a supported database location. For the deployed Vercel frontend, VITE_REPORT_API_ORIGIN points directly to the reporting API. Photos bypass serverless request-body limits. The API allows only the production site origin. Local development leaves this variable empty and uses the Vite proxy.

The site administrator must operate the review inbox manually. Reports have no automatic expiry or deletion policy; records remain until administratively removed. Daily Railway volume backups are configured with six-day retention. Storage is SQLite on the private persistent volume; the application does not add database encryption. Review ownership, retention and public privacy terms remain organizational decisions. If the group grows, replace the shared key with named reviewer accounts. No authority forwarding or external notification destination has been configured.

## Verification of the original audited release

- `npm test`: 57 tests passed, including report/photo persistence across a service restart; deduplication; private inbox/photo access; invalid fields; invalid image contents; photo-count limits; missing consent; future times; cross-origin requests; rate limiting; status updates and conflict protection.
- `npm run build`: passed frontend and server type checks and the frontend production build.
- Browser: category, written location and manual coordinates, review, consent, submission, receipt download, rejected reviewer key, authenticated photo read, and status update tested with a clearly labeled synthetic report. The final native file-picker check could not be repeated because Chrome file-URL access was disabled and the Mac locked; upload/metadata stripping and private image rendering were verified through the API and inbox. No real allegation or contact was submitted.
- Desktop and phone visual evidence is in `.impeccable/review/reporting/`. Device GPS permission, physical phone camera behavior, HEIC conversion, remain outside the browser-emulation checks. Hosted submission, private photo access, review changes and persistence across a real service restart were verified separately on production.
- Full-frame portrait and landscape previews and the full-photo dialog were checked at phone and desktop sizes. Escape closes the dialog and returns focus to the photo control. The Impeccable reviewer scored both requested fixes resolved (complete photo viewing and the first-viewport privacy explanation), with disposition `ship` for that fix-list verdict.

## Production operations

- Railway project: `actforgoa-reports` (`512430bc-234d-4582-b4dd-47770e3c9114`). Service `reports` (`0b1b9b42-453d-420f-a8f5-0c30312860ac`), production environment `58d08288-6d66-48d7-a6a4-9e07370c814c`.
- API: https://reports-production-42c8.up.railway.app. Health check: `/api/reports/config`, returning `available: true, local: false`.
- Volume `/data`, application data `/data/private/reports.sqlite`; one service instance. Daily backup schedule verified through Railway API, retention 518400 seconds.
- Reviewer secret is stored in the Railway environment and locally in `.reports/production-reviewer-token` (0600). Never put it in a URL or frontend environment variable. Open that local file to sign into the private review screen.
- `node scripts/package-reporting.mjs` prepares a source allowlist in `.reports/deployment`; it includes no database, token, test photos or research archive. Deploy with `railway up .reports/deployment --path-as-root --project 512430bc-234d-4582-b4dd-47770e3c9114 --service reports --environment production --detach --json`.
- Vercel production environment variable: `VITE_REPORT_API_ORIGIN=https://reports-production-42c8.up.railway.app`.
- The audit frontend was deployed from a frozen source snapshot in `.reports/frontend-release-2026-10-26`. Its manifest and verification evidence are in `reports/reporting-audit-2026-10-26/` in the original shared workspace. Those evidence files are not included in this focused source package.
- The final audit service image runs an idempotent cleanup for exactly two synthetic audit IDs, additionally checking their full synthetic description before deleting anything. Its source is retained in the audit evidence. Future normal packages omit this one-time cleanup.
- Cursor pagination preserves older pages when new reports arrive. Review revisions advance monotonically; stale saves receive 409. Unsaved notes are protected on navigation, sign out and refresh.

Railway ingress contract: https://docs.railway.com/networking/public-networking/specs-and-limits. Backup behavior: https://docs.railway.com/volumes/backups.
