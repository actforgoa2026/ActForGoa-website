# Standalone satellite release, 28 October 2026

**Live app:** https://satellite-app-production.up.railway.app/map

**Sign-in:** https://satellite-app-production.up.railway.app/admin

The user authorized deployment, then deferred copying CDSE credentials from the cloud environment locally and asked what could work without them. The separate app is live with an authenticated, persistent, explicitly labeled recorded real comparison. New Railway imagery retrieval remains unconfigured and unverified. This is not a new provider retrieval or a live accuracy evaluation.

## Deployed services

New project `e119f1f6-f1c7-4a58-a33c-0ea536dcfdce`, production environment `178f97df-ed3d-4d66-94ac-f86797aa736c`. Infrastructure and variables were configured through `https://backboard.railway.com/graphql/v2`; allowlisted source packages were uploaded by Railway CLI.

| Component | Source | Deployment | Persistent mount |
| --- | --- | --- | --- |
| Satellite API | `fe935ed` | `2fe8f800-6e48-4f5d-bd21-5ffcd750c6e6` | `/data/satellite` |
| Satellite frontend and authenticated proxy | `78e7fe4` | `a35e78c0-03e9-4fb8-ba8a-6e2285cb7400` | `/data/admin` |

Both deployments report SUCCESS and their HTTPS health checks return 200. Exact service, volume and environment identities are in [railway-state.json](railway-state.json); source hashes are in the two package manifests. The satellite deployment's CLI message contains an erroneous short revision string from the upload command; `satellite-package-manifest.json` identifies the actual committed source, `fe935ed`.

ORCHESTRATOR retained ownership of the combined review-site release and explicitly excluded PR #95. No existing research/editorial/reporting service, Vercel environment, review alias or actforgoa.org was changed. Source was pushed to the existing PR #95 branch without resetting other work. The PR is not merged to main.

## What is usable

- A dedicated satellite entry, named-account sign-in and same-origin authenticated admin proxy. Provider tokens never enter the browser. The app exposes only auth and satellite API routes, plus its own static assets.
- A separate satellite account for the user, created without copying/resetting the editorial account. Login details are in a local mode-0600 private file outside Git. No passwords or service tokens are in this report.
- Private saved history and reopening of the verified 10/20 October comparison. The two PNG hashes exactly match the earlier validation, and the original numeric measurements and acquisition/retrieval times are retained.
- Visible recorded-example provenance and link to the original verification. Import performs no raw-raster reconstruction, new imagery retrieval or model inference. It does not consume or reset provider quotas.
- The recorded pair has 100% common usable coverage and no vegetation-loss patches meeting the exploratory thresholds. This does not establish absence of tree removal, individual-tree counts or field accuracy.
- New imagery retrieval is disabled until CDSE is configured. Question interpretation is disabled without Anthropic. AI image decisions remain unavailable without OpenAI; no automatic key-creation flow or provider substitution ran.

## Checks actually performed

72 satellite Python tests, 182 Node tests, production build, standalone build and server TypeScript check pass. Existing dependency deprecations and bundle-size warnings remain.

Hosted Chromium checks at 1440×1000, 390×844 and 320×740 passed named-account login, saved-result opening, reopening after reload, recorded-provenance visibility, exact PNG hashes, unchanged numeric evidence and unavailable-AI states. Phone contexts used mobile/touch emulation and synthesized touch activation; no physical phone or Device Hub was used. Page errors, horizontal overflow and rendered italic/oblique elements were absent. [Browser evidence](recorded-browser.json), [phone capture](recorded-full-390.png), [desktop capture](recorded-full-1440.png).

The app account survived an app-service restart. The saved comparison survived a satellite-service restart and was then reopened through the hosted frontend. Satellite SQLite has mode 0600 on its persistent volume. Unauthenticated access returns 401, another actor receives 404 for the saved job and sees an empty history, and missing CSRF returns 403. Cookies are Secure, HttpOnly and SameSite=Strict. [Authentication](hosted-auth.json), [privacy](hosted-privacy.json).

Impeccable source detection found no primary findings. It recorded type-ramp advisories and pre-existing map/error colours. The rendered detector flagged the cream background, which is the user's explicitly committed warm-paper palette, so it is not a defect. The project's generated design sidecar is stale; it was reported and left unchanged. Rendered inspection found no decorative side stripes or italic type.

## Failed checks retained

The first satellite build failed because Railway's current builder rejects optional `type=secret` Docker mounts. The separate `Dockerfile.railway` fixes that while preserving the development Dockerfile. The first app build omitted the Git-ignored generated bundle; uploading only the allowlisted package with `--no-gitignore` fixed it. These were hosting/package failures, not provider calls.

An initial browser reload sequence timed out waiting for the result label. A focused reproduction returned successful session/history/job responses and reopened correctly. The final three-width run explicitly waits for readiness after reload and passes; no server/page error was observed. This record does not claim exhaustive browser or accessibility coverage.

## Remaining work

Securely configure real `CDSE_CLIENT_ID` and `CDSE_CLIENT_SECRET` in the satellite service, redeploy it, then perform a bounded new hosted catalog and imagery comparison. The existing cloud bindings are not local credentials and injected placeholders must not be copied into Railway. The user deferred local credential entry; no fresh provider check was attempted.

`OPENAI_API_KEY` can be configured separately later; the previously failed key-creation connector must not be retried automatically. Natural-language planning, ecology context, statewide coverage, place/parcel joins, FIRMS and field validation are not established by this release. Saved results retain the existing 30-day policy.
