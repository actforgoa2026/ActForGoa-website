# ActForGoa integration

## Current cloud handoff

Start every resumed task by reading `docs/CLOUD-IMPLEMENTATION-PLAN.md`. It is the implementation ledger, ownership map and continuation plan. Keep feature implementation and heavy parallel work in the cloud. Update the ledger when work changes state, recording exact commits, checks, blockers and next actions.

The user appointed **Coordinate agent threads and PRs** (`01a181ad-56ba-70c2-93cd-1aa5185d007a`) as the continuing cloud release coordinator. Use [coordination issue #89](https://github.com/actforgoa2026/ActForGoa-website/issues/89) for durable handoffs and release ownership; it is not an instant wake-up mechanism. CLOUD owns PR #90 implementation and its bounded source landing under the user's subsequent “ship it” instruction. The primary coordinator retains combined deployment ownership. The existing hourly automation is a reporting/review worker, not an independent release owner. No concurrent alias promotions.

The former local **ORCHESTRATOR** (`01a17774-6d09-7751-915c-3fbf3a8994c4`), LAW, ECO SYSTEM and QA remain paused. Their retained corpus/accounting evidence can support a focused handoff, but do not automatically resume those chats or the old heartbeat. The earlier local shipping proposal in this chat is superseded by the current cloud coordinator handoff. Keep environment readiness specific to the executor; configured credentials in another chat do not transfer here.

- Start from freshly fetched `origin/main`; preserve newer features when resolving conflicts.
- The primary shared checkout can contain other agents' unfinished work. Do not reset, stash, sweep-commit or publish it. Use a suitable isolated worktree.
- Approved live features must be represented in Git before a later deployment. A frozen local snapshot alone is not a release branch.
- Follow `docs/RELEASING.md` and use `npm run release:review` for review-site promotion. Preserve guided topic paths, hero, discovery feed, emergency help, reporting, templates, guides, CRM and research as they land.
- Keep private report data, credentials, personal CRM notes and raw research archives out of Git and static deployments.
- Use the installed Impeccable skill and inspect the rendered desktop and phone result for visual changes. No italic/oblique text or decorative side stripes. Never launch Device Hub without explicit approval for that occasion.
- State separately what is implemented, tested, merged and live. The review alias is `actforgoa-field-guide.vercel.app`; changing the original `actforgoa.org` site requires a separate user decision.

## User design preference

Never add eyebrow labels above headings. Do not use uppercase eyebrow text. The user explicitly requires no eyebrows, including on the orbit landing page.
