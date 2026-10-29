# Coordinated review-site releases

The release coordinator owns promotion to `actforgoa-field-guide.vercel.app`. Feature chats prepare isolated commits or PRs and provide test and browser evidence. They must preserve other owners' features and avoid concurrent alias promotions. This workflow does not authorize replacing `actforgoa.org`.

Start from freshly fetched `origin/main`. Never release from the shared, dirty development checkout or from an old frozen snapshot. If approved live source is missing from Git, recover and reconcile it first. Keep private incident databases, credentials, photos, personal CRM notes and raw research archives outside source-control and deployment packages.

Before merging, run `npm test`, `npm run build`, the installed Impeccable workflow, and actual desktop and phone browser checks. Check the hero and sectioned feed, guided topic paths, CRM and archive, emergency actions, reporting controls and API health, guides, template export, search and any newly added routes. Preserve original-source links and uncertainty labels. A build alone is not visual verification.

For the cloud research/forms/editorial release, begin with `docs/CLOUD-IMPLEMENTATION-PLAN.md`, `docs/RESEARCH-CLOUD-HANDOFF.md` and `deploy/admin/README.md`. Include `/ask/legal`, `/ask/ecology`, `/admin`, `/blog` and `/blog/archive` in desktop/phone evidence. Promotion now also checks nonempty scoped research collections, the configured internal service and the public journal response. This does not prove live Anthropic answer accuracy or provision an editor account; those remain explicit acceptance steps. In the managed cloud, use `NODE_USE_ENV_PROXY=1 npm test` so the existing MCP integration test uses the supplied network proxy.

After the source is committed, save a JSON evidence record under ignored `.reports/`. Record `treeSha` from `git rev-parse HEAD^{tree}`, `desktop: true`, `mobile: true`, the checked route strings in `routes`, screenshot locations, test/build results, and the current live deployment ID as `previousDeploymentId`. Required route strings are listed in `scripts/deploy-review.mjs`. Evidence must describe checks that actually ran. The Git tree stays the same across an ordinary PR merge, so verification remains tied to the exact content.

Merge the reviewed PR, fetch the merged main into the clean release checkout, and run:

```sh
npm run release:review -- --check --evidence .reports/release-evidence.json
npm run release:review -- --evidence .reports/release-evidence.json
```

The release command rejects dirty or stale source, missing browser evidence and a changed live deployment; a shared Git lock serializes coordinator runs. It repeats tests/build and records source commit/tree in Vercel deployment metadata. The remote build uses explicit public API origins and does not change the review alias until ready. The staged URL must report a ready research API. The wrapper checks main, working-tree cleanliness and the existing deployment again after the remote build, then promotes that exact deployment and confirms the alias identity. Do not bypass a failure with a direct deployment. An old agent that ignores this command can still deploy, so the coordinator must also hold independent promotions while integrating.

After publishing, verify the public alias on desktop and phone, confirm new and retained routes, and record deployment ID plus commit in the release report. Report separately what is implemented, tested, merged and live. An unconfigured external service remains explicitly unavailable. Do not claim generated answers, dispatch, email delivery or current service availability without corresponding evidence.

Editorial acceptance must exercise draft creation, reopening, publishing, private revision, republishing and unpublishing through the hosted frontend. A ready `/api/admin/config` does not prove deeper article routes work. Plain Node function routing is distinct from Next.js catch-all routing: retain explicit handlers for `/api/admin/posts/:id` and `/api/admin/posts/:id/:action`. The release wrapper probes these routes anonymously and requires the service's 401 JSON response before promotion. This read-only check must not create posts or bypass authentication.

If a release process crashes, inspect the owner record in the shared Git `actforgoa-release.lock` directory and confirm that process has ended before removing the stale lock. Never remove an active owner's lock.


## Homepage routing cutover

The approved orbit homepage was published through project routing overrides while its source PR was separate. Preserve that source in the integrated release and verify both `/` and `/explore`. Record `vercel routes list --production --expand --project actforgoa-field-guide` and the production routing version alongside the deployment ID. Confirm no unexpected staged routing changes before editing. Alias identity alone cannot detect a rewrite serving another deployment.

After the accepted integrated deployment has been published by `release:review`, verify its immutable URL serves the native homepage and assets correctly. Only then retire the exact review-host overrides for root and `/explore`, preserving unrelated routes. Retire the old `/orbit-assets` proxy after confirming no active page depends on it; preserve it temporarily for open old tabs if necessary. Review the staged routing diff before publishing, save the previous version for rollback, and verify the public alias's HTML/assets, topic routing and desktop/phone UI after cutover. Do not remove an override while the alias still depends on it, change the original domain, or call an old asset deployment the integrated release.

## Root-only deployment exclusions

Keep backend-only exclusions anchored to the repository root (for example,
`/satellite/`). An unanchored `satellite/` also excludes
`api/admin/satellite/` from Vercel's upload, even when local entrypoint tests
pass. Inspect the deployed function inventory and probe every new route depth.
The release wrapper now requires authenticated-service 401 JSON responses for
all satellite actions and the job route before alias promotion. A SPA response
or platform 404 must fail this gate; no provider operation is performed.
