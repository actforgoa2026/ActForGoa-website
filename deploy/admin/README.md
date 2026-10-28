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

## Provision and revoke individual accounts

On the service with its persistent volume attached:

```sh
node --import tsx server/admin-accounts.ts add curator@example.org 'Curator Name' editor
node --import tsx server/admin-accounts.ts revoke curator@example.org
```

The add/reset command prompts without echoing the password in an interactive terminal. For an automated secure session it reads a password from stdin. Never put passwords in shell arguments, source files, browser storage or command logs. `add` on an existing email resets its credentials and revokes all sessions. `revoke` immediately disables the account and its sessions. There is no public signup, email delivery or recovery service. Each provisioned editor/admin can curate and manage articles; account provisioning remains an operator CLI action. The role label reserves a future account-management UI and does not grant access to the separate incident inbox.

Sessions expire after 12 hours; cookies are Secure in production, HttpOnly and SameSite=Strict. Authenticated writes require the session's `X-CSRF-Token`. State-changing cross-origin requests are rejected. Passwords use salted scrypt; persisted session tokens are SHA-256 hashes. Login attempts are limited across account and client in a 15-minute window, with a global cap and two concurrent password checks. No shared default password is created.

## Editorial behavior

- New stars must identify a record in the deployed catalog/CRM/guide snapshots. Admins can see and remove stale stars; public curation only returns currently resolvable IDs, never editor details. Apply stars after relevance matching and filters, using `prioritizeStarred` from the shared contract.
- Draft updates use an integer `version`; stale saves/publishes/deletes return 409 without overwriting the other editor. The UI should retain the unsaved text and let the editor reload deliberately.
- Saving an already published article does not replace its public version. Only the explicit publish endpoint replaces the published snapshot. The live URL remains reserved until republishing; unpublish removes public access immediately. A published article must be unpublished before deletion.
- Body content is Markdown. The consuming UI must disable raw HTML and permit only safe link/image protocols. The service returns data, never executable article HTML.
- Public `/api/blog` and `/api/blog/:slug` contain published snapshots only. Private author emails, audit trails, password hashes and drafts never appear in these responses.

## Deploy

Prepare an allowlisted staging directory with this folder's `package.json`, `package-lock.json`, `Dockerfile` and `railway.json` at its root; copy `server/admin.ts`, `server/admin-store.ts`, `server/admin-accounts.ts`, `shared/admin.ts`, `public/data/catalog.json`, `public/data/crm.json`, and `src/content/guide-records.json` preserving paths. Do not stage `.reports`, env files, incident data or raw research archives.

Use one replica with a persistent volume mounted at `/data`; do not share this SQLite file across containers. Set production variables, deploy, then provision named accounts using the service's private shell. `/api/admin/config` is the readiness endpoint. Frontend rewrites must preserve `Cookie`, `Set-Cookie`, and `X-CSRF-Token`. Repackage the public source snapshots whenever their record identities change. Back up the SQLite database with its backup API or after a clean shutdown; copying only the live main file may miss its WAL. Never commit backups or package them as frontend assets.

The service and tests are implemented in the cloud. A working deployment, persistent volume, account provisioning and an end-to-end hosted login check are required before declaring the dashboard live.
