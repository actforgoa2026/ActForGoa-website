# Bounded Haiku response capacity

The `36d7938` diagnostic stopped on its first request with `max_tokens`: 9,000
output tokens, including 7,373 thinking tokens, left an incomplete final JSON
answer. That failed attempt remains counted. The second question was not run,
and no semantic judgment is made about the incomplete response.

Haiku's application output bound is now 12,000 tokens. Sonnet remains at 9,000.
Anthropic documents a 128K maximum for Haiku 5.5 and rates of $0.10 input / $0.50
output per million tokens up to 100,000 input tokens. Thinking and final response
share the output limit. Verified 28 October 2026 IST against the official
[model overview](https://platform.claude.com/docs/en/models/haiku-5-5/overview) and
[effort documentation](https://platform.claude.com/docs/en/build-with-claude/effort).

The model, medium effort, adaptive thinking, instructions, schemas, retrieval,
evidence guards and no-retry behavior are unchanged. Native answer cache keys
include the configured output bound so a prior-capacity answer cannot mask a new
configuration. Other providers' cache identities are unchanged.

Every evaluation plan must explicitly specify `max_output_tokens`, and preflight
rejects disagreement with the configured value. Allowed plan bounds are 9,000 or
12,000 for Haiku and 9,000 for Sonnet. The CLI uses the genuine application config;
it cannot override that config with the plan. A historical 9,000-token Haiku plan
is rejected on this 12,000-token runtime before key, library or client access.
Historical artifacts remain unchanged and belong to their historical runtime.
An absent bound fails closed. The tracked historical plan template now states
its existing 9,000-token bound explicitly; a current run needs a new reviewed
12,000-token plan. Reports and check results record the effective bound.

249 focused tests pass. New checks cover plan/config mismatch, missing and
unreviewed bounds, early refusal of mismatched historical plans, native wire identity, cache
separation, explicit report identity and conservative reservations. The existing
provider timeout assertions still pass.

Offline replay of the saved request matches its captured bytes exactly. The
candidate serialized request differs only by `"max_tokens":9000` becoming
`"max_tokens":12000`. All ten passages, instructions, schema and conversation
context are unchanged. Capture SHA-256:
`d872dbc4f9be3ecdf25a543a52a116a20520a9fa2e920a7eb9179cdbaf142cd5`.

| Conservative reservation | Micro-USD | USD |
| --- | ---: | ---: |
| Captured water request | 9257 | 0.009257 |
| Maximum bounded request | 9424 | 0.009424 |
| Two maximum requests | 18848 | 0.018848 |
| 71 maximum requests | 669104 | 0.669104 |

The $5 monthly and 100-attempt daily limits are unchanged. The 60-second provider
and 75-second short-answer UI timeouts are also unchanged. More token capacity
does not prove completion, latency or accuracy. No paid calls, native corpus
access, key/ledger changes or preview/release actions were made for this candidate.
