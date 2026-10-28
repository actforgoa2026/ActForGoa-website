# Internal editorial service

This is a separate Node 24 service for the ActForGoa dashboard. It uses built-in SQLite and crypto; it never reads reporting credentials or private incident data. Accounts, password hashes, sessions, curated stars, draft articles, published snapshots and audit events live on a persistent private volume. The frontend remains on the existing review site.

## Run in the cloud checkout

Run `node --import tsx server/admin.ts`. The default port is 4188 and development frontend origin is `http://127.0.0.1:4173`. Proxy `/api/admin/*`, `/api/curation`, `/api/blog`, and `/api/blog/*` from the frontend to this service. Authentication uses a host-only HttpOnly cookie scoped to `/api/admin`; use same-origin frontend rewrites in production, not a cross-site API URL.

Configuration:

| Variable | Meaning |
| --- | --- |
| `ADMIN_DATA_DIR` | Private persistent directory, default ignored `.reports/admin`; production `/data/admin`. |
| `ADMIN_PUBLIC_ORIGIN` | Exact frontend HTTPS origin in production. |
| `ADMIN_HOST` | Bind address, production `0.0.0.0`. |
| `ADMIN_PORT` / `PORT` | Service port, default 4188. |
| `ADMIN_CATALOG_ROOT` | Root containing the packaged public snapshots, default working directory. |
| `ADMIN_TRUST_RAILWAY_PROXY` | Set `true` only behind Railway's edge with `RAILWAY_PROJECT_ID` present to use its `X-Real-IP` for login throttling. |
| `ADMIN_BEHIND_FRONTEND_PROXY` | Set `true` for the Vercel same-origin relay. Its shared egress address is not an end-user identity; this mode uses account and global login limits without the per-client bucket. |

## Provision and revoke individual accounts

On the service with its persistent volume attached:

```sh
node --import tsx server/admin-accounts.ts add curator@example.org 'Curator Name' editor
node --import tsx server/admin-accounts.ts revoke curator@example.org
```

The add/reset command prompts without echoing the password in an interactive terminal. For an automated secure session it reads a password from stdin. Never put passwords in shell arguments, source files, browser storage or command logs. `add` on an existing email resets its credentials and revokes all sessions. `revoke` immediately disables the account and its sessions. There is no public signup, email delivery or recovery service. Each provisioned editor/admin can curate and manage articles; account provisioning remains an operator CLI action. The role label reserves a future account-management UI and does not grant access to the separate incident inbox.

Sessions expire after 12 hours; cookies are Secure in production, HttpOnly and SameSite=Strict. Authenticated writes require the session's `X-CSRF-Token`. State-changing cross-origin requests are rejected. Passwords use salted scrypt; persisted session tokens are SHA-256 hashes. Login attempts are limited to 12 per account in a 15-minute window, with a 150-attempt global cap and two concurrent password checks. Direct mode additionally limits the client address; set `ADMIN_BEHIND_FRONTEND_PROXY=true` behind Vercel so one client cannot consume a shared relay-address bucket for the whole team. Arbitrary forwarded-IP headers are never trusted. No shared default password is created.

## Editorial behavior

- New stars must identify a record in the deployed catalog/CRM/guide snapshots. Admins can see and remove stale stars; public curation only returns currently resolvable IDs, never editor details. Apply stars after relevance matching and filters, using `prioritizeStarred` from the shared contract.
- Draft updates use an integer `version`; stale saves/publishes/deletes return 409 without overwriting the other editor. The UI should retain the unsaved text and let the editor reload deliberately.
- Saving an already published article does not replace its public version. Only the explicit publish endpoint replaces the published snapshot. The live URL remains reserved until republishing; unpublish removes public access immediately. A published article must be unpublished before deletion.
- Body content is Markdown. The consuming UI must disable raw HTML and permit only safe link/image protocols. The service returns data, never executable article HTML.
- Public `/api/blog` and `/api/blog/:slug` contain published snapshots only. Private author emails, audit trails, password hashes and drafts never appear in these responses.
- Article list endpoints omit bodies and accept `q` (up to 200 characters), `limit` (default 50, maximum 100) and an opaque `cursor`. Admin lists additionally accept `status=all|draft|published`. Responses include `nextCursor` and filtered `total`; admin lists include global `counts: {draft, published}` for the overview. Reset the cursor when filters change. Fetch a full article by ID/slug before editing/reading it. This keeps list responses bounded even for large articles.

## Deploy

Prepare an allowlisted staging directory with this folder's `package.json`, `package-lock.json`, `Dockerfile` and `railway.json` at its root; copy `server/admin.ts`, `server/admin-store.ts`, `server/admin-accounts.ts`, `shared/admin.ts`, `public/data/catalog.json`, `public/data/crm.json`, and `src/content/guide-records.json` preserving paths. Do not stage `.reports`, env files, incident data or raw research archives.

Use one replica with a persistent volume mounted at `/data`; do not share this SQLite file across containers. Set production variables, deploy, then provision named accounts using the service's private shell. `/api/admin/config` is the readiness endpoint. Frontend rewrites must preserve `Cookie`, `Set-Cookie`, and `X-CSRF-Token`. Repackage the public source snapshots whenever their record identities change. Back up the SQLite database with its backup API or after a clean shutdown; copying only the live main file may miss its WAL. Never commit backups or package them as frontend assets.

The service and tests are implemented in the cloud. A working deployment, persistent volume, account provisioning and an end-to-end hosted login check are required before declaring the dashboard live.
