# Cloud orchestration

The user appointed “Coordinate agent threads and PRs” (`01a181ad-56ba-70c2-93cd-1aa5185d007a`) as the primary cloud orchestrator on 2026-10-28. [Issue #89](https://github.com/actforgoa2026/ActForGoa-website/issues/89) holds the durable inbox, queue, ownership record and checkpoints. GitHub state is shared across cloud workspaces; do not depend on a particular VM surviving.

## Reporting and current work

The implementation ledger is [docs/CLOUD-IMPLEMENTATION-PLAN.md in PR #90](https://github.com/actforgoa2026/ActForGoa-website/blob/codex/cloud-integration-20261028/docs/CLOUD-IMPLEMENTATION-PLAN.md). Its owner records completed work, active work, remaining work, exact commits, tests and blockers. This coordination document defines responsibilities; issue #89 records the latest cross-chat status and release decisions. Update on meaningful changes, preserving active owners' edits and separating reported progress from committed, accepted and live work.

Snapshot: 28 October 2026, 14:17 IST. Read newer issue comments and PR heads before acting.

| Work | Owner | Current status | Next action |
| --- | --- | --- | --- |
| Coordination and reporting | Coordinate agent threads and PRs | Primary owner appointed; cloud and local chat reads work; GitHub is the available outbound channel | Collect exact-head handoffs and reconcile #90/#91 ownership |
| Research, forms and dashboard implementation | CLOUD | Active; reports 171 TypeScript tests and a successful build, with final fixes and browser checks ongoing | Push implementation commits and refreshed ledger to #90, with final evidence |
| Deployment access and service readiness | Resume unfinished work | Support owner reports Vercel/Anthropic authentication succeeds; Railway returns Cloudflare 403 before authentication can be verified | Continue cloud readiness investigation; return sanitized findings through #89 |
| Coordination documentation | Primary coordinator, PR #91 | Draft; ownership and reporting responsibilities recorded | Reconcile with #90 before landing |
| Existing research candidates | PRs #10, #12 and #17 | Held for unresolved acceptance and dependencies | Preserve offline-only restrictions and existing acceptance gates |
| Native app | PR #14 | Draft; separate platform validation required | Keep outside the web release until accepted |

At this snapshot, #90 head `2d76a713ba662f53c1b58f44841e3f52df9d1e1d` contains only the initial plan and AGENTS guidance. The implementation owner's newer working changes and test reports are not yet a reviewable pushed candidate. No feature merge or deployment is recorded by this coordination handoff. The support owner's [readiness report](https://github.com/actforgoa2026/ActForGoa-website/pull/90#issuecomment-6464589217) identifies review deployment `dpl_FzbANqhz96u2JNt2eb6fK4BDtS7c`; recheck it before any release.

## Communication

- Post material handoffs and blockers to issue #89, and code review feedback to the relevant PR. Read the latest checkpoint before claiming work.
- Cloud subagents use native agent messages during an active run, then return their exact commit and verification evidence to the coordinator.
- The existing hourly cloud automation in “Set up cloud orchestration” (`01a18192-3654-778b-9704-c9b2055f1059`) is the primary coordinator's reporting/review worker. It remains quiet when nothing actionable changes. It must not independently merge, deploy or promote an alias without an explicit primary-coordinator handoff in issue #89. Do not create a competing schedule. A GitHub comment is durable delivery, not an immediate wake-up.
- Cloud and local chat history can be read through the app, but direct cross-chat sending is not exposed in the current cloud session. Use the GitHub inbox for requests and acknowledgments; do not claim that a posted message has been read or that it wakes the recipient.
- Routine coordination uses GitHub. Keep the former local ORCHESTRATOR, LAW, ECO SYSTEM and QA chats paused unless the user explicitly resumes them. Do not poll the laptop or launch local browser/terminal sessions.
- Other existing chats can adopt this protocol when next resumed; this document does not migrate their unsent local files or wake them automatically.
- Scope begins with this repository. Register another repository only when the user assigns it.

## Handoff format

```text
Type: READY | BLOCKED | UPDATE | RELEASED
Owner / chat or agent ID:
Repository / PR / target branch:
Head SHA / tree SHA:
Scope:
Dependencies (PR + required head, if any):
Checks actually run and results:
Desktop/phone evidence for visual changes:
Blockers / next action:
Release intent: integration only | review site
```

Use PR number plus head SHA to identify a handoff. Do not repeat unchanged status messages. Keep private reports, CRM notes, credentials and raw archives out of GitHub; summarize validation without exposing private data.

## Integration

1. Read current GitHub state and the latest checkpoint; reconcile unfinished operations before retrying.
2. Inspect the actual diff, exact head, dependencies, required checks, review threads and owner evidence. Do not treat old test results or a READY message as acceptance.
3. Use an isolated checkout from freshly fetched main. Preserve other owners' changes and resolve dependencies before merging.
4. Merge only accepted, non-draft changes with expected-head protection. A changed head needs renewed review and validation.
5. Record PR/head, disposition, checks, merge SHA and next action. Keep implemented, tested, merged and live distinct.

The research acceptance restrictions recorded in issue #89 remain in force. A cloud migration does not authorize further paid provider calls, budget changes or release of rejected candidates.

## Review-site release

Follow [RELEASING.md](RELEASING.md), including actual tests/build, applicable acceptance and rendered desktop/phone checks, tree-bound evidence, the existing deployment identity, and `npm run release:review`. A passing unit suite does not establish semantic or visual acceptance.

The cloud coordinator is the single promotion owner. The release command's Git lock protects worktrees sharing one clone; it does **not** serialize separate local and cloud clones. An issue comment is also not an atomic distributed lock. Keep other promotion owners stopped. A future coordinator handoff must explicitly retire the prior owner before publishing.

The allowed review alias is `actforgoa-field-guide.vercel.app`. Changing `actforgoa.org` remains outside this handoff.

Credential readiness is specific to each environment. The current primary coordinator has ready Vercel, Railway and Anthropic bindings and an enforced unrestricted HTTP policy; this verifies configuration, not every service's authorization. The support chat has separately verified Vercel and Anthropic authentication, while Railway access remains unresolved. Older implementation/setup environments may still lack those bindings. Check the actual release executor before shipping. Do not copy secrets from the laptop or bypass network policy. Credentials alone do not clear corpus, semantic, browser or deployment gates.

## Resuming after interruption

Read issue #89 and current PRs first. Deduplicate by PR/head and processed comment IDs. Recheck any ambiguous merge or release against remote state before repeating it. Append a checkpoint only for a meaningful change. Notify the user for completion, failure, a meaningful development or required action; stay quiet for unchanged blockers.
