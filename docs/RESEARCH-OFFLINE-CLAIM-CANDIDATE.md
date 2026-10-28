# Offline source-to-claim candidate, 28 October 2026

Status: reviewable experiment; production runtime unchanged; no semantic acceptance
or paid-call authorization. This supersedes the recommendation to replace answers
with passage selection in RESEARCH-CLAIM-EVIDENCE-PROPOSAL.md for this workstream.

## Verified baseline and evidence limits

Fresh remote main: `a786df50a9f69663c0e68751accc6d136890715a`.
PR #88 remote head: `0c234e6f53dce24632875cc1f58f0c4dd302078a`.
The working branch begins at current main, preserving the later answer-first UI.
The historical capture reviews, unsealed dependency assessment, complete frozen
71 semantic cases and three HTTP journeys are unavailable here. No historical
capture or acceptance expectation has been edited or replayed. Existing tracked
experiments are available, but are not the missing private reports. No persistent
research ledger has been inspected; last reported totals remain unverified.

Current main differs materially from the user's historical native contract:
`backend/anthropic_answers.py` declares 28,000 prompt bytes and 1,800 output tokens;
its HTTP client has a 60-second timeout. `backend/chat.py` budgets the complete
serialized payload against that single prompt bound. It does not independently
enforce 24,000-byte original native input, 36,000-byte final messages or a
4,096-byte schema. A request timeout alone does not establish a 65-second deadline
including retrieval. Do not dispatch this runtime as though those limits were
verified. This candidate changes none of these values, provider settings, ledgers,
reservation behavior, retries, caches or UI.

## Assessment and correction

Exact quotation checks establish occurrence, not entailment. Whole-passage
closure additionally overincludes unrelated text; finer spans reduce that problem
but introduce source-review work. Neither establishes correct wording. The
reported 14-profile sizing result cannot be reproduced or generalized to the
complete acceptance set without its artifacts. The defensible assessment result
is therefore rejection of dependency closure as a sufficient correction, with
complete-set sizing and source relationship discovery still unassessed.

The smallest offline candidate pairs each conversational factual claim with
explicit original support IDs and explicit evidence entries for subject, modality,
measure, population, date, conditions and uncertainty. Empty facet entries mean
no supporting span selected, not permission to resolve ambiguity from memory.
These entries help a reviewer compare the wording with the source; they are not
new labels claimed to fix meaning. The candidate permits natural paraphrase and
multi-source synthesis. It neither emits quotation templates nor rewrites prose.

Source-reviewed spans retain original passage text and original offsets. Existing
context dependencies must be recorded explicitly, with their source rationale
reviewed before use. The prototype takes supplied relationships; it does not infer
antecedents or reconstruct tables. Missing dependencies fail validation instead
of silently adding citations. Every support keeps its own ID; no bundling to evade
support limits and no truncation. The offline prototype has no provider schema or
runtime support-limit change. A runtime design must fit all existing caps or
return a specific limitation; fitting this small experiment proves no such fit.

`experiments/claim_review_candidate.py` checks offsets, IDs, cycles, explicit
closure and facet/support membership. It hashes the complete pack and claims so
later review cannot accidentally apply to edited wording. This proves only
structural validity relative to the supplied pack. It cannot establish whether
a dependency is missing from that pack, whether offsets match an original PDF,
or whether a source is relevant, current or correctly interpreted.

A separate reasoned reviewer decision records each claim/facet as preserved,
not applicable, failed or unresolved. Any failure or unresolved judgment blocks
that review. Even a complete favorable facet review retains release hold:
question coverage, relevance, omissions, conflicts, useful abstention and the
unchanged launch gates still require independent assessment. There is no automated
semantic judge, second provider call, repair, fallback or retry.

## Counterexamples and verification

The added synthetic development probes deliberately show mechanically valid
complete support paired with semantically wrong conversational wording:

- Mandatory compliance weakened to unavailable annexure details.
- Avian survey in 2019 broadened to Goa today, with an uncertain 104/16 denominator
  silently turned into individual birds.
- Complete table headers and rows paired with a wrong fee measure.
- Eligibility and prior approval changed into universal eligibility and later approval.

Explicit missing antecedent and table-row selections fail without modifying the
selection. Cycles and invalid offsets fail. A natural approval paraphrase remains
mechanically valid and semantically unassessed; reject-all or quote-only behavior
is not treated as success. These are synthetic probes inspired by the supplied
failure descriptions, not recovered quotations or new independent acceptance
cases. The intentionally wrong paraphrases passing mechanics are a recorded
limitation, not a successful automatic fix.

Run `python3 -m unittest discover -s experiments -p 'test_*.py' -q`.
The existing tests and acceptance expectations are unchanged. This experiment is
not imported by the backend and makes no network requests.

## Review boundary and next evidence

Review the candidate contract and counterexamples before considering runtime
integration. It is defensible as an auditable review workflow, not as an automatic
semantic guarantee for public answers. An unattended runtime correction is still
unproven; changing only instructions or adding facet labels is insufficient.

To complete the historical assessment, transfer the preserved capture reviews,
unsealed dependency artifact and frozen acceptance manifest through cloud storage,
without restarting stopped local chats. Review source identity, all required
relationships and complete-set sizing against those exact bytes. Then decide
whether claim-level review provides sufficient evidence for a bounded runtime
candidate. Preserve the 71 semantic cases, three HTTP checks and distinct launch
checks without substitution or weakened expectations.

No paid call until offline review and explicit authorization of a bounded
acceptance run. Before any such call reconcile the actual persistent ledgers;
do not reset or refund attempts. Preserve one call/atomic reservation, no automatic
fallback/repair/retry, 24,000/36,000/4,096 byte limits, 12,000 total output tokens
including thinking, 65 seconds including retrieval, $5/month and 100 attempts per
UTC day. Acceptance must precede real Goa question/citation/full-document checks
and desktop/phone verification on the actual production alias. No visual changes
were made, so Impeccable and rendered review were not invoked here.
