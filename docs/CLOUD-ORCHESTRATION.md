# Cloud orchestration

The cloud orchestrator chat `01a18192-3654-778b-9704-c9b2055f1059` coordinates ActForGoa integration under the user's 2026-10-28 handoff. [Issue #89](https://github.com/actforgoa2026/ActForGoa-website/issues/89) holds the durable inbox, queue, ownership record and checkpoints. GitHub state is shared across cloud workspaces; do not depend on a particular VM surviving.

## Communication

- Post material handoffs and blockers to issue #89, and code review feedback to the relevant PR. Read the latest checkpoint before claiming work.
- Cloud subagents use native agent messages during an active run, then return their exact commit and verification evidence to the coordinator.
- The coordinator's scheduled cloud check runs hourly and stays quiet when nothing actionable changes. A GitHub comment is durable delivery, not an immediate wake-up.
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

At setup, GitHub coordination works but the managed environment lacks Vercel deployment credentials and allowed Vercel API access. Cloud promotion stays blocked until supported environment configuration is ready. Do not copy secrets from the laptop or bypass the network policy. Keep deployment evidence and claims separate from code merges.

## Resuming after interruption

Read issue #89 and current PRs first. Deduplicate by PR/head and processed comment IDs. Recheck any ambiguous merge or release against remote state before repeating it. Append a checkpoint only for a meaningful change. Notify the user for completion, failure, a meaningful development or required action; stay quiet for unchanged blockers.
