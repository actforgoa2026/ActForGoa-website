# Direct Anthropic research answers

This opt-in adapter uses `claude-haiku-5-5` through Anthropic's native Messages API. It does not change the default provider, retrieval, source documents or interface. The key stays on the server; no environment file belongs in Git, tests, a service artifact or the frontend. A configured key establishes neither credit availability nor answer quality.

## Reviewed upstream contract (2026-10-27)

| Setting | Contract | Official reference |
| --- | --- | --- |
| Model and standard pricing | `claude-haiku-5-5`; input $0.10 and output $0.50 per million tokens for prompts up to 100,000 tokens | [Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview) |
| Endpoint | `POST https://api.anthropic.com/v1/messages`; top-level system instructions, user/assistant history, `max_tokens=6000`, `stream=false`, `service_tier=standard_only` | [Messages](https://platform.claude.com/docs/en/api/messages/create) |
| Authentication | Bearer API key; optional `anthropic-workspace-id` for a workspace-scoped key, required for an unscoped key | [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication) |
| API version | `anthropic-version: 2026-10-21`; no temperature, top-p or top-k | [Versioning](https://platform.claude.com/docs/en/api/versioning) |
| Thinking | Adaptive thinking, `output_config.effort=medium`; thinking shares the output-token cap | [Effort guidance](https://platform.claude.com/docs/en/build-with-claude/effort) |
| Structured output | `output_config.format={type: json_schema, schema: ...}` | [JSON outputs and supported constraints](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) |

The native schema uses `text`, a required `primary_support` object constrained to the passage text field, and zero to nine additional `supports` per claim unit. A support contains an exact selected `citation_id`, a whitelisted field, and a contiguous quote of at most 600 characters. Brief answers use one closed nullable `paragraph` object; standard answers use one to four `paragraphs` objects. The native field instructions and structured-output schema agree, without duplicating the entire schema in the prompt. Strict local validation requires 1–10 supports per paragraph including the primary text support, and quote matches with whitespace normalization only. Supported provenance fields are `warning`, `legal_currency`, `source_date_metadata.reviewed_locator_and_dates`, `source_date_metadata.date_caution`, and `guide_verification.limitations`. Resolution uses the actual serialized request, never hidden library metadata, arbitrary titles or hosting URLs. Each valid unit maps unchanged to one public paragraph with only its own supporting citation IDs. Invalid units reject the whole response; none are combined, dropped or truncated. The native prompt omits URL, publisher class, document-kind hint and topic labels. It retains the original title only as `catalogue_scope_hint` for document identity, jurisdiction and version context. This hint cannot establish authorship, publication dates, advocacy/official status or current law and is not eligible quote support. Full public citation metadata stays unchanged, as do other providers. Caveats stay attached to the relevant text-supported unit; unsupported definitions are omitted. Existing strict Pydantic, 120-word, complete-sentence and citation checks still run. Exact quotations establish source identity, not factual entailment; independent claim review remains required.

Only completed `end_turn` responses without stop details are accepted. Text is read by block type; thinking is discarded. Refusals, truncation, unexpected models, unsupported content, malformed responses and schema failures fail closed. No native tools, provider citations, web search or message prefilling are requested.

## Reservation calculation

All providers share the existing SQLite allowance: $5 per UTC month and 100 attempts per UTC day. Selection of another provider or use of account credits does not create another allowance, erase failed attempts, or refund existing reservations. Production and local evaluation accounting must be reconciled separately before live validation; synthetic tests use temporary ledgers only.

For Anthropic, the reserved input count is:

```
serialized message UTF-8 bytes (at most 24,000)
+ existing framing allowance (2,048)
+ native schema allowance (4,096)
+ native format/system allowance (4,096)
= at most 34,240 reserved input tokens
```

The final provider-specific prompt, including native claim-support instructions, is built before history/evidence trimming. API and acceptance call sites pass the configured provider to preparation, so the captured evidence is the evidence actually sent. Before dispatch, the adapter independently requires the actual serialized messages to fit 24,000 bytes and leaves the full 2,048 framing allowance intact. The separate native schema must fit 4,096 bytes. A bound above the 100,000-token reviewed price tier is rejected. At the maximum current prompt size, the reservation is `ceil(34,240 × 0.10 + 6,000 × 0.50) = 6,424` micro-USD, or $0.006424. Smaller prompts reserve less. All 6,000 output tokens are reserved at the output rate, including thinking. We request no prompt-cache writes, priority tier, batch processing or paid tools; cached-input discounts are not assumed. Application answer-cache hits make no provider call and consume no new reservation.

This is a conservative operational estimate, not an exact bill or a provider-guaranteed tokenization bound. Anthropic documents an injected format prompt without a maximum size. Before activation, compare reported input/output usage against the reserved bound on the authorized live cases, including the largest multilingual/schema case. A new model, format, tokenizer, cache policy or pricing tier requires review. Taxes, hosting and unrelated account usage are outside this inference reservation.

One reservation precedes one POST. The HTTP transport has zero retries, refuses redirects, ignores environment proxy routing and pins the host. Connection/write/pool timeouts are 10 seconds and read timeout is 60 seconds; these are transport timeouts, not a promise to abort a billed provider computation on browser disconnect. A cancellation, timeout, refusal, invalid answer or provider error keeps its reservation. No automatic second provider or retry is attempted. Upstream bodies and transport diagnostics are replaced with static error messages; the API returns the existing safe failure response and keeps search/document endpoints usable.

## Configuration and verification

Set `RESEARCH_CHAT_PROVIDER=anthropic`, `ANTHROPIC_CHAT_MODEL=claude-haiku-5-5` and provision `ANTHROPIC_API_KEY` securely. Use `ANTHROPIC_WORKSPACE_ID` only as needed for the key's scope. Direct calls can use the intended Anthropic organization's credits; subscription-credit eligibility and linking are governed by [Anthropic's API-credit rules](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers). No balance is inferred from the key being present.

The mock tests assert native headers/body, unsupported-schema conversion, strict local validation, no redirects/retries/fallback, bounded reservations across provider switches, error/cancellation charging, cache behavior and full-source access. The end-to-end fixture builds synthetic PDFs through the real MiniLM/Zvec/FTS pipeline, then checks cited slices, originals by SHA-256, final-page text and rendered PDF images. These tests establish the integration contract, not live model support, available credits, factual entailment or corpus acceptance.

Coordinator-owned live acceptance still requires the reconciled genuine ledger, real-source retrieval checks, bounded provider calls with reported usage, claim review, full-document navigation and the final integrated service artifact's exact source identity. Do not open a sealed package through Zvec during adapter verification; use disposable synthetic fixtures. No deployment or public answer activation follows from passing mock tests alone.
