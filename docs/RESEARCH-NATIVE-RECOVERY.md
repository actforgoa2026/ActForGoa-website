# Cloud recovery of native research history

28 October 2026. This supersedes the initial claim that all historical acceptance
inputs were unavailable. The initial inspection covered current main only; the
remote research branches contain substantial recoverable evidence. No user file
transfer is needed for the recovered material.

## Recovered without changing expectations

Fetched the remote research branches and pinned PR #88's exact head,
`0c234e6f53dce24632875cc1f58f0c4dd302078a`. An isolated, detached cloud reference
checkout is at `/workspace/actforgoa-native-reference`. Current main remains
`a786df50a9f69663c0e68751accc6d136890715a`; no old runtime was merged into it.

The following raw-file hashes agree with the historical acceptance plan:

| Input | Cases | SHA-256 |
| --- | ---: | --- |
| `tests/research/goa-chat-cases.json` | 50 | `5ad99abb3c643763bfdf0db356601c8d8cde3d6be17ea0ae32e8a304bf382939` |
| `tests/research/legal-chat-cases.json` | 5 | `1ee50fd40b504962015cb9d6fa5a1fb8526fabcb53d845555265a5143070d0bc` |
| `reports/passage-selection-2026-10-27/assessment-cases.json` | 12 | `7420098b89731896c4689f1b16bfb5003f41b98a0e302756b0d6de9d96c26d9f` |

That recovers **67 of 71** semantic cases. The twelve assessment cases are consumed
historical cases, not a fresh independent set. Their original file/classification
is retained unchanged; this recovery does not restore independence. The four
additional boundary cases remain required and unrecovered. A four-entry
`remaining-case-evidence.json` also exists, but its entries belong to earlier
assessment work; it is not substituted for the missing boundary cases.

Also recovered the original template, freeze record, neutral claim-fidelity
controls, native adapter, final preparation code and acceptance documentation.
`experiments/recovered_native_inputs.json` pins twelve raw files. Original copies
stay in ignored `.reports/recovered-research-history/` and a separately verified
`.reports/recovered-research-history-verified/`; no raw captures/source archives
are added to Git.

Reproduce into a new directory using only local Git objects:

```sh
python3 experiments/recover_native_history.py \
  --repository /workspace/actforgoa-claim-assessment \
  --output-directory /workspace/actforgoa-claim-assessment/.reports/new-recovery
```

The script verifies every file's byte length/hash and the 50+5+12 counts before
writing. It refuses an existing output directory. It runs no recovered application
code, makes no network requests and accesses no credentials or ledgers.

## Native baseline findings

The original one-call path has the specified 24,000-byte original messages,
36,000-byte final messages, 4,096-byte schema, 12,000 output tokens and original
65-second clock including retrieval. The recovered code/docs retain a single
atomic reservation and sole dispatch with no retry/fallback/repair. This is source
inspection plus the tests below, not production verification or renewed acceptance.
The current main implementation is a separate simplified path with different
limits; the earlier main-vs-required mismatch remains a real integration concern.

The native draft already had **duty** and **scope** roles, alongside condition,
exception, quantity and date. The native final code validates selected-source
identity, declared context, publication acknowledgments and exact assembly. None
of this proves the meaning of prose. Existing authored controls explicitly show
incorrect wording surviving exact-support validation. Adding those same role
labels again would not be a demonstrated correction.

The native support limits are **10 total supports** per unit/assembled paragraph
and **600 characters per selected source span**. The initial new offline prototype
mistakenly borrowed current main's 6/1,600 limits. It now uses the native 10/600
limits without changing production. The earlier 621-character source section is
preserved in full; its method and total clauses are separate original spans that
must both be explicitly selected. No response repair, evidence truncation,
automatic support expansion or support bundling is introduced.

## Offline native checks actually run

Against untouched PR #88 code:

```sh
/workspace/ActForGoa-website/.venv/bin/python -m pytest \
  tests/research/test_single_final.py \
  tests/research/test_single_final_medium.py \
  tests/research/test_claim_fidelity_controls.py \
  tests/research/test_evidence_plan.py -q
```

**181 passed.** These are existing fake-transport/temporary-ledger tests, not model
calls, semantic acceptance, effort comparisons or a production-accounting check.
The neutral controls' deliberately wrong prose is expected to pass mechanical
validation; their test success documents that limitation.

The new `experiments/native_context_budget_probe.py` constructs the three recovered
full-page packs in standard and brief styles through PR #88's actual pure native
builders. It fixes the historical model/effort configuration, creates no client,
does not dispatch, and touches no ledger. It rejects a dirty/wrong reference
checkout and refuses to report success if original preparation drops a supplied
page. It does not modify source relationships or claim to recreate historical
retrieval profiles.

| New development pack | Original messages, standard/brief | Final messages, standard/brief | Schema, standard/brief |
| --- | --- | --- | --- |
| Avian context and denominator conflict | 20,335 / 20,693 | 21,824 / 21,760 | 1,852 / 1,575 |
| Lake identity and functions | 11,317 / 11,675 | 12,566 / 12,502 | 1,614 / 1,337 |
| Additional storage-design source pages | 23,135 / 23,493 | 24,729 / 24,665 | 1,925 / 1,648 |

All six retain every supplied page and fit the existing byte limits. Output stays
12,000 tokens. These are six new development profiles with empty history, not the
missing fourteen historical profiles or the full 71-case set. Do not generalize
the sizing result. Report `.reports/source-context-assessment/native-builder-v1.json`
has SHA-256 `0f9fe24446ba96863e6479509ac1fc6c4184342046f3024d87c65e400c2b1354`.

Reproduce with no provider calls:

```sh
/workspace/ActForGoa-website/.venv/bin/python experiments/native_context_budget_probe.py \
  --reference-checkout /workspace/actforgoa-native-reference \
  --input-directory .reports/source-context-assessment \
  --output .reports/source-context-assessment/new-native-builder.json
```

## Matching annexure obligation recovered from source

The saved regulations' full-text route yielded 558,408 bytes of extracted text.
Physical page 118 (printed page 113) contains the matching substance: recharge
permission in areas designated by Goa's Water Resource Department, followed by a
requirement that the structures and design follow Annexure V (27.V). The text
contains extraction spacing in “shall b e”; offsets preserve it exactly.

This recovers the relevant source rule, not the historical diagnostic's raw answer
or exact selected span. The original regulations PDF and current consolidated
legal applicability have not been independently verified in this continuation.
The full document also exposes Annexure V text; “details unavailable in this
supplied page” must not become “the corpus has no annexure.”

A separately pinned input and explicit `--include-annexure-duty` option add two
probes to the prior seven. The preserving prose states both permission and the
mandatory design condition, then distinguishes missing page-level details and
unverified currency. The negative states only permission and an unavailable
annexure. Both select both source spans; both pass structure; semantic review must
reject the negative because the obligation disappears. This directly falsifies
closure alone on a matching source obligation, beyond the earlier additional
storage-design example.

```sh
python3 experiments/source_context_probe.py \
  --input-directory .reports/source-context-assessment \
  --include-annexure-duty \
  --output .reports/source-context-assessment/new-nine-case-packet.json
```

Original v1/v2 reports and their hashes remain untouched. V3 corrects span limits;
v4 includes the two explicitly added annexure probes. No old result is silently
rewritten. All nine retain semantic unassessed/release hold. The experiment suite
with explicit source inputs still runs 75 tests with one unavailable frozen-capture
skip; the source replay test now checks the additional pair as well.

## Remaining evidence, without substituting new requirements

Searching fetched remote branch trees and their relevant case/plan JSON blobs did
not recover the unsealed dependency draft, completed historical diagnostic/review
captures, four extra boundary-case definitions or exact three generated-answer
HTTP journey definitions. The source-search/full-document verification script is
available, but it is distinct from those three HTTP gates and is not substituted
for them. Cloud handoff summaries and GitHub comments were read without waking,
sending to or executing on the stopped local threads.

The full 71 semantic cases, three HTTP checks, separate launch capacity/checks and
real ledger reconciliation remain mandatory. No missing case is replaced, deleted,
marked passed or reconstructed from an invented expectation. The last reported
accounting checkpoints remain unverified. No model, effort, prompt, judge, repair
or retry sweep was run. Public chat remains off; there is no semantic acceptance,
merge or production launch verification from this work.

Nine-case v4 packet SHA-256: `d2e1fdd3a98b3d1a0c8b3b0eb0a3052c0262999d28f8c93917c92708d433c552`.
