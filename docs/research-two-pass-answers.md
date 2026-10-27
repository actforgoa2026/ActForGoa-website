# Corpus-grounded reconstruction pipeline

Implementation for review; not a statement that AI answers are enabled or accepted. The coordinator owns integration, live calls, canonical accounting and site activation. Earlier failed semantic captures remain failed. Source-first retrieval and the full 71-case final-answer review gate are unchanged.

## Explicit configuration

`ANTHROPIC_ANSWER_PIPELINE=two_pass_v1` requires `RESEARCH_CHAT_PROVIDER=anthropic`, `ANTHROPIC_CHAT_MODEL=claude-haiku-5-5`, `ANTHROPIC_CHAT_EFFORT=low` and the existing 12,000-token output limit. Omission retains the separate `single_pass` path. There is no automatic fallback, retry, third call or different model. Existing secure key/workspace provisioning remains server-only.

The API and acceptance harness both call `backend.answer_pipeline.run_answer_pipeline`. The first call uses the existing native draft contract. Invalid, refused or incomplete drafts stop. A mechanically valid insufficient-evidence draft still reaches reconstruction so supported requested content can be recovered.

Reconstruction receives the exact complete prepared source records, evidence, question, retained history and request scope, plus an explicitly untrusted compact draft containing only status and normalized paragraph text/citation IDs. It cannot retrieve again or silently shorten evidence. The draft is capped at 8,192 UTF8 bytes; complete correction messages at 36,000 bytes. Overflow stops before reserving the second call. The original 24,000-byte first-stage bound remains.

Each reconstructed paragraph contains claim units, each with its own exact passage and required source-context support. The server joins claim text with one space and unions citations without adding connecting prose. Publication label/year acknowledgement remains paragraph-local; supports are deduplicated with a ten-support paragraph ceiling. Existing public paragraph, text and style guards still apply. The final response retains the public citation and reader-link format. The cache contains only the reconstructed final, bound to pipeline version, both prompts/schemas/configurations and prepared evidence/history. Failed correction never returns or caches the draft.

These are mechanical guards, not an entailment judge. An exact quote can accompany a wrong claim. Authored controls deliberately preserve that failure for scope, quantity, date, table measure, missing coverage and mandatory conditions. A model correction score does not count as independent acceptance.

## Execution and accounting

Each request owns its asynchronous provider transport. Each phase has a 30-second cancellation deadline and shares a 65-second provider/no-new-dispatch deadline measured from HTTP entry, including request-body, corpus retrieval and preparation time. Browser disconnect cancels active provider I/O, prevents the next phase and blocks final publication/cache. The existing 75-second UI timeout is unchanged.

The synchronous native corpus search cannot safely be forcibly cancelled. A cancelled request retains ownership and joins that worker before releasing its slot. It then rechecks deadline/disconnect before any provider work. This is not a hard 65-second total HTTP or native-work completion guarantee. Actual HTTP latency remains a separate live acceptance check; cancelling local I/O does not prove the provider stopped billable computation.

The shared $5/month and 100-attempt/day limits remain. Complete-pair preflight is read-only and advisory; each phase needs its own atomic `reserve_stage` receipt. Concurrent consumption can refuse reconstruction after a charged draft. Committed reservations remain after errors, cancellation, missing usage or uncertain transmission. A duplicate parent/phase receipt cannot authorize another send. UTC is checked by the ledger after its lock and again immediately before dispatch. No transaction spans provider I/O.

At the currently reviewed rates and fixed maximum bounds, draft reserves at most 9,424 micro-USD; reconstruction 10,624; a pair 20,048 ($0.020048). Actual smaller packets reserve less. Seventy-one complete pairs reserve at most 1,423,408 micro-USD and normally require 142 provider attempts, so evaluation must span UTC-day stages. These are conservative reservations, not actual invoice totals. Prices, schema/token overhead and reported usage still need the existing live checks.

## Capture v2 and frozen plans

Historical plans/captures remain single-pass unless explicitly versioned. New plans must contain `pipeline: "two_pass_v1"`, the exact shared `PIPELINE_SPEC`, and for each UTC-day stage separate `max_cases` (equal to selected packet count) and `max_attempts` (at least twice that count, at most 100). The environment must independently select the same pipeline/model/effort/output bound. Existing exact-head, generation, ledger and execution-authorization checks still run before key loading or native access. Planning only hashes question packets.

The harness starts no new pair within 65 seconds of UTC reset. Mid-pair rollover stops before the next dispatch, retaining receipts and unrun cases. Reports cannot resume or overwrite a prior path. Every phase records exact safe outgoing bytes/hash/config, parent/phase identity, receipt and counters, state, known dispatch initiation or transmission uncertainty, available usage/stop metadata and timings. Reconstruction adds the exact compact draft, evidence/history equality proof, input binding, safe raw structured final output, deterministic assembly offsets and normalized answer. Raw thinking, credentials and arbitrary error bodies are excluded. A failed capture write stops further work.

Final claim/coverage review remains pending even after mechanics pass. Before enabling a testing preview, the coordinator must inspect the frozen code, review a bounded real-model diagnostic, and finish the API/conversation checks. Public activation additionally needs the complete 71-case gate, genuine ledger reconciliation, actual desktop/phone verification and public alias checks. Existing guides and source search remain independently usable.
