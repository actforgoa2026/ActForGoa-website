# Explicit Haiku low-effort comparison

Both medium-effort diagnostic runs ended with incomplete JSON at their output
limits. The latest used 12,000 output tokens, including 10,395 thinking tokens.
Those failed attempts remain recorded and counted; neither incomplete answer is
a semantic pass.

This candidate permits `low` only for the reviewed Haiku 5.5 model. The default
remains `medium`; Sonnet still permits only `medium` and `high`. The 12,000-token
Haiku bound, adaptive thinking, instructions, evidence, schema, citation guards,
rates, retries and timeouts are unchanged. Cache identities already distinguish
effort.

Low must be selected explicitly in both `ANTHROPIC_CHAT_EFFORT=low` and the frozen
plan's `effort` field. The evaluator now reads the actual runtime effort instead
of replacing it from the plan. A low plan with a medium runtime, or a low runtime
with an omitted/medium plan setting, fails before key, library or client access.
The same explicit environment/plan agreement applies to a Sonnet high run.
The request capture validates model/effort pairs and preserves low exactly.

Anthropic recommends low effort for chat while warning that lower effort may
skip checks in longer prompts. This is a comparison candidate with a quality
risk, not an accepted replacement. Verified against the official
[effort guidance](https://platform.claude.com/docs/en/build-with-claude/effort#recommended-effort-levels-for-claude-haiku-5-5)
on 28 October 2026 IST. The full 71-case acceptance gate and its frozen criteria
remain unchanged.

260 focused tests pass. They cover default-medium preservation, low-only Haiku
selection, invalid pairs, exact wire/report capture, cache separation, unchanged
reservations, and entrypoint refusal of a plan/runtime mismatch. Offline replay
matches the saved request bytes exactly; the candidate differs only by
`"effort":"medium"` becoming `"effort":"low"`. Capture SHA-256:
`ce2801b089fc2f1fe9b6ea1de7c46a630ae0d45df6c5cd77243389658b60ff97`.

The maximum reservations remain $0.009424 per request, $0.018848 for two and
$0.669104 for 71. Monthly $5, daily 100 attempts, provider 60 seconds and short
answer UI 75 seconds remain unchanged. No live request, native corpus access,
key/ledger modification, preview change or release occurred in this work.
Completion, latency and semantic accuracy still require fresh independent review.
