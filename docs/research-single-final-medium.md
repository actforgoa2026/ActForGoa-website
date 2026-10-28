# Fixed-medium single-final candidate

This is one offline completion hypothesis, not an accuracy result or release approval. The previous fixed-high single-final request reached its 12,000-token output limit with all reported output tokens attributed to thinking, then failed strict final JSON validation at53.18seconds. No final answer was captured. This candidate changes the sole final request to fixed medium effort under a new identity.

## Exact scope

Only two production files change from `c874a69e7781c57254e54c4eb2b6920fd51512e9` (tree `f85ce2b7c1da6ae26af71be16dc879dff9d340a5`):

- `backend/phase_effort.py`: pipeline `single_final_v2`, policy `single_final_medium_v1`, fixed `reconstruction: medium`.
- `backend/reconstruction.py`: capture version13.

The base environment effort remains medium. Workflow remains `single_final_full_evidence_v1`; the strict integer provider call count stays1. The canonical local empty adapter and non-generated provenance stay unchanged. Omitted configuration still uses the separate legacy path. This does not silently upgrade a configured v1 service.

For identical prepared input, the only request-body difference is `output_config.effort`, from high to medium. Final instructions, schema, complete selected evidence, question, retained history, scope and local adapter remain identical. There are no async client, HTTP route, harness, retrieval, citation, normalization or accounting changes. There is no fallback, retry, additional generation, source trimming or validation relaxation.

Haiku5.5, adaptive thinking, 12,000 output tokens, 24,000 native-selection bytes, 36,000 final-message bytes and 4,096 schema bytes remain. The original-entry65-second overall clock, sole65-second stage/read,10-second connection/write/pool limits and75-second UI limit remain. Shared limits stay $5/month and100attempts/UTCday; every failed reservation remains charged. A maximum final reservation remains10,624micro-USD, with no assumed medium-effort discount.

## Verification map

The [G01–G12 safety map](research-single-final-answers.md#guard-preservation-map) remains applicable. Existing matrices are adapted to the new allowed phase effort and current identity without removing failure categories. In particular:

| Control | Adaptation |
| --- | --- |
| Actual wire parity | The12 synthetic profiles in `test_single_final.py` dispatch through the owned fake HTTPX transport. Each captured medium request is copied locally and only its effort is reset to high; the resulting complete wire hash must match the immutable `single-final-v12-wire-parity.json` baseline. Prompt, schema and original-payload hashes are independently checked unchanged. The baseline fixture is never rewritten. |
| Wrong effort | Previously allowed high is now a rejection case; medium is the positive sole-call assertion. Low/xhigh/max/missing effort and in-place/copy mutations still reject. |
| Stale policy | `test_single_final_medium.py` rejects v1, capture12, high-policy/high-phase and mixed metadata before packet/key/native/ledger access. Direct owned-transport tests reject stale context for both high and medium bodies before callbacks/I/O. |
| Cache separation | An explicitly reconstructed historical high identity cannot supply the new medium result; a real stale pipeline key is rejected. |
| Detached policy | Existing callback/export mutation controls still cannot alter the trusted fixed policy. Generic native high rejection and legacy allowlists remain unchanged. |
| Request counts and budget | Existing single receipt/send, advisory/atomic race, strict counts, cancellation, exact UTC and failure-charge tests remain. Readiness still reserves at most21,248micro-USD for two cases. |
| Source and answer protections | Own-claim support, context/publication/year checks, strict JSON, credentials, source bytes, late-return rejection and no-cache failure tests are unchanged apart from selecting the new identity. |

LAW's12 profiles are valid synthetic full-transport tests. They are distinct from ECO's12 real-source builder comparisons. Three ECO authored pre-retained-history profiles exceed the unchanged24,000-byte native limit and must remain early refusals. Twelve builder comparisons must never be described as twelve valid native dispatches. This implementation does not open those private sources or alter those fixtures.

## Prior evidence and release boundary

Official [effort guidance](https://platform.claude.com/docs/en/build-with-claude/effort#recommended-effort-levels-for-claude-haiku-55) identifies medium as Haiku5.5's default. [Thinking cost guidance](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#cost-control), checked2026-10-28, describes effort as a soft control and lowering it as one remedy for output-limit exhaustion. It does not guarantee completion or preserve accuracy.

V11 medium final requests completed within the same output cap, but their semantic review failed. In water04 the statutory design requirement was “shall be as per Annexure V”; Appendix C belongs only to a synthetic fixture. The lake antecedent, table measure/citation and herbaceous-population failures also remain binding expectations. V11 contained a generated plan, so its successful completion does not establish behavior for the new local-empty input. No prior acceptance transfers.

Independent design and exact-source reviews precede any separately authorized diagnostic. The bounded diagnostic may run at most two predeclared cases once; its harness stops per case on runtime failure. Independent full semantic review follows the bounded process. Any semantic failure blocks all later stages. An accepted diagnostic case counts once within the unchanged71-case set. The3 distinct HTTP journeys and at least4 unspent launch attempts remain required;4 is a capacity floor, not four mandatory calls.

This is the final effort-tuning hypothesis in this sequence. A failure ends this path and requires offline source-to-claim representation assessment before any new proposal. There is no next effort/prompt sweep, cap increase, accepted-case replay or authorization to deploy.
