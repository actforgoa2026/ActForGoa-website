# Original table context in cited answers

A retrieved table continuation can contain species and region values while its column heading is in an earlier chunk. Interpreting those values without the heading can produce a plausible but unsupported answer. The source-context correction supplies the actual earlier indexed excerpt as a separate citation.

Search ranking, the original ten selected passage IDs, text, offsets, source metadata and reader links stay unchanged. For a visibly tabular fragment, retrieval may attach one existing same-page chunk containing an explicit table caption, aligned textual column labels and the first numbered data row. Column labels must cover the visible row fields. The association stops at intervening prose, headings, different-width rows or wrapped cells; it does not infer a heading from a document title or from the row values.

The answer request includes both exact source excerpts and a `context_ids` dependency. A paragraph citing the continuation must cite its header too. Native answers must quote actual header text; a metadata-only quote cannot satisfy the dependency. The visible request and local citation records must agree on these dependencies before dispatch and response acceptance. Header and continuation are budgeted together under the existing 24,000-byte message limit. Neither source text nor a generated answer is silently rewritten.

The supplementary citation uses its existing document, generation, page, passage ID and offsets. The existing source reader therefore opens the real header excerpt. No index mutation, new model, price, spending limit, paid retry or UI change is included.

## Validation

- 251 research tests passed, with five existing SWIG deprecation warnings.
- Paired offline checks used the unchanged 72-query corpus: 9 original, 15 prior, 20 previously frozen, 12 consumed assessment and 16 smoke questions. Both short and standard native request formats retain their prior results: 9/9, 12/15, 19/20, 12/12 and 16/16. There are no new retrieval or prompt-retention failures.
- Every primary and supplementary passage remains an exact indexed page slice with a resolvable reader locator. Native schema, message and cost bounds pass.
- The previously failing bird-table continuation now receives the original caption and `Species` / `Endemic to` columns. Its standard request is 22,495 bytes. The groundwater request remains 21,365 bytes.
- Replaying the prior captured outputs without a provider call retains the supported groundwater answer and rejects the bird-table answer that omitted the required heading citation.
- Independent review covered missing column labels, incomplete labels, wrong-section carryover, normal continuation and visible/local dependency mismatches.

See `reports/source-context-2026-10-27/validation.json` for source and evidence hashes. The reproducible offline evaluator is `scripts/evaluate_source_context.py`; it requires an explicitly marked disposable corpus and rejects preservation locations before native imports.

## Remaining limits

This is conservative same-page context recovery for recognizable numbered tables, not complete table reconstruction. Unrecognized, cross-page, wrapped or ambiguous layouts do not acquire an inferred header. Numeric values from table fragments remain prohibited. Supplying a genuine header does not establish claim entailment or current legal status.

Four prior strict-ID/usefulness gaps remain recorded: two fee cases, a dog-authority case and a licensing-bodies case. They are not converted to passes. Fresh generated-answer review and public-site verification are still required before AI activation.
