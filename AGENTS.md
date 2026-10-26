# ActForGoa integration

The user appointed the “ORCHESTRATOR” chat (`01a17774-6d09-7751-915c-3fbf3a8994c4`) to coordinate concurrent feature work, PRs, merges and review-site releases. During concurrent work, prepare an isolated commit/PR and give the coordinator the exact head, scope, dependencies and verification evidence. The coordinator owns the combined deployment unless the user directs otherwise.

- Start from freshly fetched `origin/main`; preserve newer features when resolving conflicts.
- The primary shared checkout can contain other agents' unfinished work. Do not reset, stash, sweep-commit or publish it. Use a suitable isolated worktree.
- Approved live features must be represented in Git before a later deployment. A frozen local snapshot alone is not a release branch.
- Follow `docs/RELEASING.md` and use `npm run release:review` for review-site promotion. Preserve guided topic paths, hero, discovery feed, emergency help, reporting, templates, guides, CRM and research as they land.
- Keep private report data, credentials, personal CRM notes and raw research archives out of Git and static deployments.
- Use the installed Impeccable skill and inspect the rendered desktop and phone result for visual changes. No italic/oblique text or decorative side stripes. Never launch Device Hub without explicit approval for that occasion.
- State separately what is implemented, tested, merged and live. The review alias is `actforgoa-field-guide.vercel.app`; changing the original `actforgoa.org` site requires a separate user decision.
