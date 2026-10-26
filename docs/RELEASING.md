# Coordinated review-site releases

The release coordinator owns promotion to `actforgoa-field-guide.vercel.app`. Feature chats prepare isolated commits or PRs and provide test and browser evidence. They must preserve other owners' features and avoid concurrent alias promotions. This workflow does not authorize replacing `actforgoa.org`.

Start from freshly fetched `origin/main`. Never release from the shared, dirty development checkout or from an old frozen snapshot. If approved live source is missing from Git, recover and reconcile it first. Keep private incident databases, credentials, photos, personal CRM notes and raw research archives outside source-control and deployment packages.

Before merging, run `npm test`, `npm run build`, the installed Impeccable workflow, and actual desktop and phone browser checks. Check the hero and sectioned feed, guided topic paths, CRM and archive, emergency actions, reporting controls and API health, guides, template export, search and any newly added routes. Preserve original-source links and uncertainty labels. A build alone is not visual verification.

After the source is committed, save a JSON evidence record under ignored `.reports/`. Record `treeSha` from `git rev-parse HEAD^{tree}`, `desktop: true`, `mobile: true`, the checked route strings in `routes`, screenshot locations, test/build results, and the current live deployment ID as `previousDeploymentId`. Required route strings are listed in `scripts/deploy-review.mjs`. Evidence must describe checks that actually ran. The Git tree stays the same across an ordinary PR merge, so verification remains tied to the exact content.

Merge the reviewed PR, fetch the merged main into the clean release checkout, and run:

```sh
npm run release:review -- --check --evidence .reports/release-evidence.json
npm run release:review -- --evidence .reports/release-evidence.json
```

The release command rejects dirty or stale source, missing browser evidence and a changed live deployment; a shared Git lock serializes coordinator runs. It repeats tests/build and records source commit/tree in Vercel deployment metadata. Do not bypass a failure with a direct deployment. An old agent that ignores this command can still deploy, so the coordinator must also hold independent promotions while integrating.

After publishing, verify the public alias on desktop and phone, confirm new and retained routes, and record deployment ID plus commit in the release report. Report separately what is implemented, tested, merged and live. An unconfigured external service remains explicitly unavailable. Do not claim generated answers, dispatch, email delivery or current service availability without corresponding evidence.

If a release process crashes, inspect the owner record in the shared Git `actforgoa-release.lock` directory and confirm that process has ended before removing the stale lock. Never remove an active owner's lock.
