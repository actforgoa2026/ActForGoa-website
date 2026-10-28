# ActForGoa integration

The user appointed the cloud orchestrator chat “Coordinate agent threads and PRs” (`01a181ad-56ba-70c2-93cd-1aa5185d007a`) on 2026-10-28 to coordinate concurrent feature work, PRs, merges, review-site releases and reporting. The former local “ORCHESTRATOR” and its coordinated local chats are paused for this handoff. Use [coordination issue #89](https://github.com/actforgoa2026/ActForGoa-website/issues/89) as the durable agent inbox and follow [the cloud coordination protocol](docs/CLOUD-ORCHESTRATION.md). During concurrent work, prepare an isolated commit/PR and provide the exact head, scope, dependencies and verification evidence there. The cloud coordinator owns combined deployment unless the user directs otherwise; do not wake or repeatedly poll paused local chats.

Read `docs/CLOUD-IMPLEMENTATION-PLAN.md` in the current implementation branch when present; PR #90 contains that work ledger. Keep implementation ownership with its active workers. The existing hourly automation in “Set up cloud orchestration” is a reporting/review worker, not an independent merge or release owner. It needs an explicit coordinator handoff in issue #89 before merging or promoting anything.

- Start from freshly fetched `origin/main`; preserve newer features when resolving conflicts.
- The primary shared checkout can contain other agents' unfinished work. Do not reset, stash, sweep-commit or publish it. Use a suitable isolated worktree.
- Approved live features must be represented in Git before a later deployment. A frozen local snapshot alone is not a release branch.
- Follow `docs/RELEASING.md` and use `npm run release:review` for review-site promotion. Preserve guided topic paths, hero, discovery feed, emergency help, reporting, templates, guides, CRM and research as they land.
- Keep private report data, credentials, personal CRM notes and raw research archives out of Git and static deployments.
- Use the installed Impeccable skill and inspect the rendered desktop and phone result for visual changes. No italic/oblique text or decorative side stripes. Never launch Device Hub without explicit approval for that occasion.
- State separately what is implemented, tested, merged and live. The review alias is `actforgoa-field-guide.vercel.app`; changing the original `actforgoa.org` site requires a separate user decision.
