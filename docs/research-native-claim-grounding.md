# Native answer grounding candidate

This candidate addresses three observed answer failures: reversing a quantified
population relationship, omitting an available source publication year, and citing
a passage that supports only part of a paragraph. It is not semantic acceptance
or authorization to enable public AI answers.

## Runtime changes

- Native Anthropic instructions require paragraph-local support for every clause,
  preserve the direction of quantified relationships, and keep useful supported
  answers while identifying the specific missing evidence.
- A shared pure helper derives a year label only from explicit publication fields:
  `prism.publicationDate`, `citation_online_date`, `citation_publication_date`, and
  `datePublished`. It accepts a valid four-digit year or Gregorian date in
  `YYYY-MM-DD` / `YYYY/MM/DD` form. Malformed values or conflicting years remain
  unresolved. Retrieval dates, generic `dc.date`, titles, and prose annotations do
  not become publication years. Different valid dates in one year agree at this
  year-only granularity.
- Native model-visible sources include this label alongside unchanged raw
  metadata. A paragraph citing such a source must include an exact full-label
  support for that deduplicated model-visible source record. Multiple passages
  referencing the same record may share this support within the paragraph;
  distinct records each need support even when their year and label are identical.
  If resolved, the paragraph text must include the year as a separate number. The
  model is instructed to attribute that year to publication, not observation or
  current legal force. The guard applies to every cited source with the label;
  it does not guess which claims are quantitative. Missing acknowledgments reject
  the whole output; the adapter does not insert text or salvage paragraphs.
- Publication labels are re-derived before dispatch and normalization. Altered
  labels fail validation. Original paragraph text is still preserved losslessly.

Retrieval, source selection, public source records, model selection, effort,
provider endpoint, retry behavior, token caps, and spending controls are unchanged.
Both already-supported native models use the same contract. Other providers do
not receive this new annotation. There is no dependency on the offline auditor.

## Verification

The focused provider, publication, chat-control and acceptance suites passed:
**220 tests**, with five existing PyMuPDF SWIG deprecation warnings. Tests cover
invalid/conflicting metadata, source immutability, brief/standard output, both
model configurations, missing or borrowed date support, altered labels and
lossless normalization, shared-source acknowledgment and preserved context-text
requirements. A deliberate counterexample demonstrates that genuine
quotes and a correctly acknowledged year can still accompany a false assertion.

Four saved-capture compaction fixtures compared this candidate with integration
base `f6703eabbe6ac3990d05c537aa390d460a6e3156`. They used explicit empty history
and brief/standard styles; this is not a replay of the original serialized prompt.
All retained passage records and identities were unchanged: ten water passages
and eleven species passages, including the supplied table header.

| Fixture | Prompt bytes before | Prompt bytes after | Schema bytes after |
| --- | ---: | ---: | ---: |
| water, standard | 21365 | 22123 | 1707 |
| water, brief | 21723 | 22481 | 1708 |
| species, standard | 22495 | 23329 | 1777 |
| species, brief | 22853 | 23687 | 1778 |

These are below the existing 24000-byte prompt and 4096-byte schema limits.
No native corpus access or provider calls were made for these checks.

The acceptance harness also records the actual validated request and supplied
field names, retained conversation history, and exact outgoing UTF-8 body with
its byte length and SHA-256. The body contains the actual system instructions,
messages, visible evidence and schema. Mock transport tests prove unchanged
request objects, headers and body bytes for both models and answer styles.
Unknown or credential-like payloads are refused with a fixed status only;
headers, generated reasoning and upstream error bodies are not saved. No-dispatch
and unavailable captures are explicit. These diagnostics do not change the
application runtime or establish semantic correctness.

## Still required

The numeric guard cannot establish correct attribution, observation dates,
entailment, source authenticity or legal currency. Prompt instructions do not
prove that population reversal or unsupported conclusions are fixed. The
coordinator must inspect fresh exact-head answers against their actual local
evidence, including the known water/species failures, legal controls, follow-ups
and brief answers. A semantic pass, integration checks and rendered test-site
verification remain required before claiming readiness or public release.
