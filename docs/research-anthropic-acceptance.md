# Bounded Anthropic acceptance plan

Prepared only; this document does not authorize provider calls or publication. The one-call connectivity/schema/accounting calibration is complete. It is not acceptance of the final retrieval candidate. LAW owns retrieval and `prepare_answer` compaction; this harness changes neither.

## Frozen inputs and stages

Use `tests/research/anthropic-acceptance-plan.template.json` as a local plan, outside Git. Root supplies the exact final integrated commit, approved disposable data-copy path, expected canonical-ledger snapshot and a separate authorization reference for each stage. The template deliberately has null values for these fields and cannot execute as checked in. Generation is expected to be `20261027T065155-law-5bc5619b`; a changed generation requires a revised reviewed plan.

| Stage | Cases | Classification and gate |
| --- | ---: | --- |
| Critical | 15 | Five known legal regressions, six known ecological regressions and four explicit abstentions. Review before proceeding. |
| Remaining regressions | 40 | The rest of the original Goa set, including follow-up context. Review before independent assessment. |
| Independent held-out | 12 | LAW's separately source-reviewed packet; read only after final-head freeze and root authorization. |
| Total | 67 maximum new calls | Original 55 retained exactly once, plus 12 independent cases. |

The existing 50 Goa questions and five legal questions were previously inspected or used in model/retrieval development. Their four abstention cases are explicit safety/coverage checks, not independent generalization evidence. Failed, omitted and unrun cases remain visible; an incomplete run is never a pass.

LAW supplied metadata only for the 12 new questions: packet `reports/passage-selection-2026-10-27/assessment-cases.json` in its `research-passage-selection` worktree, SHA-256 `7420098b89731896c4689f1b16bfb5003f41b98a0e302756b0d6de9d96c26d9f`, covering four additional official documents. The contract is `{generation,cases}`; cases contain question/style, required evidence alternatives and source-review records with saved text, offsets, physical pages and original hashes. This preparation has not read those contents. The checker hashes bytes without parsing questions; only authorized execution loads them. LAW freezes the candidate before first offline assessment. Preserve every assessment regression and do not retune against this packet while retaining its independent label. Later fixes require a new independent packet.

## Source-reviewed regression expectations

These checks derive from the recorded [legal claim review](../reports/legal-answer-review.md), [ecological failure review](../reports/openrouter-chat-validation.md) and reviewed evidence fixture. They describe saved-source support, not certification of current consolidated law. The final answer must cite its own exact supporting passage, even when the fact appears elsewhere in the same document.

| Case | Claim and coverage checks |
| --- | --- |
| RTI | Retrieve/cite the manual's physical-page-7 non-BPL application-fee statement (`e5d0e7777a79a19cf17cced54e173507`). Do not substitute the illustrative additional-fee example, cover or SMS text. Preserve applicant condition, source version and untested current gateway/procedure caveat. A safe refusal to invent a fee is still a coverage failure when the indexed source answers the question. |
| TCP | Keep PDA development permission, TCP technical clearance and Municipal/Panchayat building licence attached to their distinct authorities. Reviewed passages include `6453618429d81ad36ea31f0be7ecfe06` and `d0afba61a78bf1e1b5827ce778c5f1be`. Never slash-combine the authorities into a shared issuer of technical clearance. Preserve current-applicability uncertainty. |
| Farming | The saved revised scheme's reporting provision (`49c4df829e149d7df512df066a379ae0`) governs destination, working-day deadline, Annexure I and photographs. Assessment officers must not become alternative application destinations. A Krishi Card claim requires its own provision (`491bdce0608f55429949dadfbf6b11c1`). Keep scheme/version/eligibility and later-amendment limits. |
| Institutional dogs | Saved SOP provisions (`7e2890b60d2eaff0d9e31cc713895154`, `d42390295a29bf9be2ff42e33d5a5630`) do not establish a private relocation right, current shelter capacity or implementation. Preserve later-court-order and responsible-authority limitations. |
| Parra | Final notification passage `64eed0b3b39365cd0a949e93c0901765` must not be confused with a draft, other wetlands, property transfer or parcel boundaries. Any area claim needs its complete prose support, unit and site. |
| climate-08 | Read chronology before alleging contradiction: a prior evidence gap followed by a later analysis is not itself inconsistent. Distinguish observations, projections, assessment dates and uncertainty. |
| biodiversity-03 | Do not transfer plateau-wide reptile breeding to seasonal pools or another animal group. Exact habitat scale and taxonomic scope must match each citation. |
| terrain-05 | Do not assert a questionable national-coast climate/tsunami statement as an established Goa-specific causal claim. Preserve geography, attribution and uncertainty, or omit it. |
| water-04 | Separate statewide resource assessments from local wells and contamination. Reject other-state figures, mismatched units/years and numerical inference from fragmented tables. |
| water-02 | Keep monsoon/dry-season timing, estuary location and measurement type distinct. Rainfall, river discharge and salinity are not interchangeable observations. |
| scope-01 | Recorded occurrence in Goa and Western Ghats endemism do not establish Goa endemism. Preserve the source's territorial definition. |
| Four abstentions | Unknown real-time salinity, unpublished comprehensive animal coordinates, an unmeasured well and an instruction to fabricate research must produce `insufficient_evidence` with no fabricated paragraphs/citations. |

For the other 40 questions, reviewers must establish support from the captured supplied passages. No blanket expected factual answer has been invented for questions whose source coverage has not been reviewed. A missing answerable detail is recorded as a coverage problem, separately from unsupported claims.

## Accounting and execution contract

The canonical local ledger is the reconciled `validation/.research-usage/answer-usage.sqlite` under the October 27 usage-reconciliation folder. The completed calibration left 182 historical October 26 attempts, one October 27 attempt, and 638,065 micro-USD reserved for October. Root must capture an exact fresh snapshot before each authorized stage; no initialization, reset, provider-specific allowance, refund or import occurs in this harness. Production remains separate until root imports only the verified validation delta, once.

The daily limit remains 100, leaving at most 99 October 27 attempts after calibration. All 67 planned cases fit; no unused slots authorize retries or extra questions. At the current maximum prompt reservation of 5,174 micro-USD per call, the three stages reserve at most 77,610 + 206,960 + 62,088 = 346,658 micro-USD. Combined with the calibration baseline this is at most 984,723 micro-USD, below the unchanged $5 monthly limit. Actual reservations depend on each prepared prompt. The evaluator rechecks daily/monthly capacity, UTC date and exact ledger identity before running, and checks ledger continuity before every case.

The direct evaluator runs the final `Library.search` → `prepare_answer` → `PublicLimits.reserve_answer` → `answer_question` stack. It mirrors the API's follow-up query rule and uses the same native adapter; no answer cache masks a provider call. Each dispatched request has exactly one prior reservation. Request/response protocol facts, numeric token usage, stop reason, sanitized error category, selected evidence, citation IDs, answer and accounting delta are recorded. Raw thinking, authentication headers, key values and upstream error bodies are excluded. Thinking tokens share the output cap; cache writes remain disabled. Reported usage must fit the reserved input/output counts, including cached-input counts if reported.

A missing required reviewed passage aborts before spending. A provider error, refusal, truncation, invalid citation/schema, unexpected abstention, usage overrun, ledger discrepancy or UTC-day change stops the stage. Reservations remain charged. There is no automatic retry, fallback, continuation or overwrite of an existing report. Root reviews the failed case and remaining scope before authorizing a new stage; do not silently rerun completed cases. A process interruption can leave a reserved but unfinished entry; reconcile it against the ledger before another run.

Only an explicitly marked disposable data copy may be opened through Library/Zvec. The marker `.acceptance-disposable.json` contains `{"disposable_for_acceptance":true,"generation":"<approved generation>"}`. Never mark or open a sealed preservation source to satisfy this check. The checker also verifies `CURRENT.json`, exact source commit, clean tracked files and frozen packet hashes. Preparation and synthetic tests do not open the genuine index or ledger.

Check a fully populated local plan without inference using `python scripts/evaluate_anthropic_acceptance.py --plan <local-plan.json> --stage critical`. This checks metadata and hashes; it does not parse held-out questions or open Library. Only after separate root authorization, add `--execute --output <new-report.json> --key-env-file <primary-.env.local>`. The path is safe to pass; the key value must never be passed as an argument. Further stages require fresh baseline and authorization fields. Do not invoke execution while LAW's final candidate is still under review.

## Actual claim review and release disposition

Every emitted factual paragraph starts with pending human review. For every case, split compound sentences into atomic claims and record: claim text; its paragraph's citation IDs; exact supporting text within those cited slices; verdict; and rationale. Allowed dispositions are supported, supported with stated limits, unsupported, contradicted, missing requested detail, or appropriately abstained. The reviewer must assess geographic/taxonomic/habitat scope, chronology, measurement units/date, policy-versus-implementation, legal currentness and extraction limitations. Never use an uncited page opening or another passage to rescue a claim. A copied quote is evidence to inspect, not automatic entailment.

Keep the generated run report immutable. Store the signed review separately with run-report SHA-256, runtime head/generation, case/paragraph/claim IDs, reviewer, date, coverage findings and decision. Independent held-out results remain reported separately from development/regression and abstention results. Require all planned cases completed, all claims reviewed, no material unsupported/contradicted assertion, no failed explicit abstention, and no unresolved required legal coverage. A structurally valid but substantively wrong answer fails. These requirements may hold release even if aggregate recall improves.

The script verifies exact citation page slices, full page counts/text and original hashes; it is not HTTP/UI acceptance. Root still coordinates real `/api/chat` and document-route checks, citation navigation/highlights, follow-ups, original files/pages and return state at desktop/phone sizes using the required visual workflow. Preserve the original design system. Any additional paid UI or multilingual/max-prompt boundary calls require separate bounded authorization within remaining allowance. The initial 67 English-dominant cases do not by themselves establish the provider's hidden-format overhead at every multilingual boundary.

Only root can approve the final integrated service artifact, corpus source identities, production delta import, generated-answer activation and review-site publication. No broader paid run, corpus upload or deployment has occurred while preparing this plan.
