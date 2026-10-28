# Staff curation and editorial handoff — 28 October 2026

Source: `26a447bfea5d7c3d2129b160ba0130a4ed64d504` on `codex/internal-tools-shipping`, based on merged main `821e3b2`. This report-only follow-up does not change the runtime.

## Behavior

Signed-in editors and admins see a star alongside public directory entries, archive/resource cards, and their detail pages. A compact staff bar links to `/admin?tool=community&view=picks`. Visitors see the resulting relevance-scoped ordering without staff controls or curator identities. Explicit alternative directory sorts remain respected.

The dashboard searches the same shared team picks and shows the curator/date. A star or unstar in either surface refreshes the other, including an already-open tab. The shared list is not a personal bookmark system. Session and CSRF credentials remain in HttpOnly cookies/in-memory state; cross-tab storage contains only a change notification. Unauthorized, expired and failed writes never claim a saved change. Non-catalogue source registers do not offer unsupported stars.

## Verification

178 Node tests and the production build pass. The two JSON browser reports record 17 checks against a real disposable local admin service: signed-out visibility and write rejection, public ranking, website-to-dashboard synchronization in both directions, resource/detail consistency, desktop and 390/320px layouts, logout, failed/expired writes, and draft/publish/private-revision/unpublish behavior. No browser page errors occurred. Final small guards hide stars for unlisted source registers and refresh dashboard data after same-user reauthentication; the build was repeated afterward.

The PNGs are cloud-local browser captures. They show a disposable Preview Editor account and sample blog content; none is production data. Existing Impeccable surface contracts and DESIGN.md were read and the captures inspected. The Impeccable skill itself is unavailable here, so no complete Impeccable workflow is claimed.

## Deployment continuation

The user explicitly selected ORCHESTRATOR’s working local access for shipping. This cloud environment has a ready Railway binding, but its configured GraphQL endpoint returns a Cloudflare 403 before authentication. No production service, account, environment variable or alias was changed here. Vercel was last verified at `dpl_FzbANqhz96u2JNt2eb6fK4BDtS7c`; re-read current live state before release.

1. Integrate this PR with current main, preserving concurrent research changes. Run the applicable final checks on the integrated tree.
2. Follow `deploy/admin/README.md` to package the exact committed source, deploy the separate editorial service with one replica and persistent `/data`, and provision the user's named accounts securely. Local test credentials and SQLite are not part of the package and must not be deployed.
3. Set server-only Vercel `ADMIN_API_ORIGIN`; set service `ADMIN_PUBLIC_ORIGIN` to the review-site origin and `ADMIN_BEHIND_FRONTEND_PROXY=true`.
4. Verify hosted login, website stars, dashboard search/picks, two-tab synchronization, anonymous ordering/privacy, and blog draft/publish/unpublish. Check desktop and phone. Preserve the original archive.
5. Use `release:review` and its exact-tree evidence/alias guards for `actforgoa-field-guide.vercel.app` only. Coordinate with the active release. Keep AI answers disabled until their existing acceptance passes; this editorial request grants no research budget increase or acceptance waiver.
6. Return the working `/admin` and `/blog` links, confirm named-account access without exposing credentials, and show hosted screenshots.
