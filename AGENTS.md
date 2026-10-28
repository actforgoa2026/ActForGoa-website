# ActForGoa integration

## Current cloud handoff

Start every resumed task by reading `docs/CLOUD-IMPLEMENTATION-PLAN.md`. It is the current work ledger, ownership map and continuation plan. The user moved feature development into the cloud on 28 October 2026 and asked the local worker group to pause, then explicitly authorized the local ORCHESTRATOR to wire existing credentials/services and ship the completed cloud PR. Keep feature implementation and heavy parallel work in the cloud; do not restart the old local worker group or heartbeat. Update the ledger when work changes state, recording exact commits, checks, blockers and next actions. Cloud root owns integration/acceptance; the resumed local orchestrator owns focused shipping as described in the ledger.

The “ORCHESTRATOR” chat (`01a17774-6d09-7751-915c-3fbf3a8994c4`) contains prior release evidence and the destination for the focused local shipping handoff. During concurrent feature work, prepare an isolated commit/PR and give the cloud coordinator the exact head, scope, dependencies and verification evidence. Use the current ledger to determine who owns the next release; do not promote independently.

- Start from freshly fetched `origin/main`; preserve newer features when resolving conflicts.
- The primary shared checkout can contain other agents' unfinished work. Do not reset, stash, sweep-commit or publish it. Use a suitable isolated worktree.
- Approved live features must be represented in Git before a later deployment. A frozen local snapshot alone is not a release branch.
- Follow `docs/RELEASING.md` and use `npm run release:review` for review-site promotion. Preserve guided topic paths, hero, discovery feed, emergency help, reporting, templates, guides, CRM and research as they land.
- Keep private report data, credentials, personal CRM notes and raw research archives out of Git and static deployments.
- Use the installed Impeccable skill and inspect the rendered desktop and phone result for visual changes. No italic/oblique text or decorative side stripes. Never launch Device Hub without explicit approval for that occasion.
- State separately what is implemented, tested, merged and live. The review alias is `actforgoa-field-guide.vercel.app`; changing the original `actforgoa.org` site requires a separate user decision.
