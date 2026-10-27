# Research answers: offline passage-selection proposal and falsifications

Status: offline proposal for LAW and QA review. No production implementation,
provider calls, budget changes, corpus access or release approval. The user testing
preview remains intact. The current public Anthropic release remains held.

## Decision requested

Review the smaller, selection-only candidate before any runtime implementation.
The model can return only status and ordered retained passage IDs. The app supplies
the entire immutable passage text, required header/context closure, citation,
source publication metadata and limitations. No generated factual text, arbitrary
substring, quote range or 35-word truncation is permitted in this candidate.

Short claims paired with quotations remain a comparative falsification record;
they are no longer the recommended next contract. Even excerpt-only equality
can remove the prefix in "ineligible" or omit a header's column meaning. The
smaller candidate removes those within-passage selection freedoms entirely.

Selecting complete retained text still cannot establish relevance or recover
qualifications absent from a chunk. It is useful evidence browsing, not a full
replacement for the user's conversational synthesis goal. LAW and QA must assess
useful directness and context preservation independently. No new model, provider
call, corpus access, public activation or preview switch is authorized here.

## What the captured failures establish

The medium and high Sonnet reports already passed citation identity, exact quote,
source-page access, generation, provider usage and accounting checks. Independent
review still found a changed botanical population and a sentence relying on
evidence attached to another paragraph.

The offline replay reads those original JSON bytes only after checking their
SHA-256 hashes. It does not open the corpus, resolve a native index, regenerate
answers, repair saved output or revise the historical result. It records two
short sentences sliced directly from the high-effort answer, with their original
paragraph offsets and their original local supports.

| Candidate check | Quantifier reversal | Misplaced range citation | Meaning of result |
| --- | --- | --- | --- |
| Existing exact quote checks | Passed historically | Passed historically | Excerpt exists, not entailment |
| Comparative 35-word claim plus exact excerpt | Still passes | Still passes | Shortness and pairing do not establish meaning |
| Excerpt-only text equality | Rejects transformation | Rejects transformation | Blocks rewriting; also rejects valid paraphrase |
| Semantic correctness | Still requires review | Still requires review | Never derived from the rows above |

All 12 original long paragraphs fail the comparative 35-word bound, including water
answers reviewers accepted. That is a contract mismatch, not twelve semantic
failures or proof of an improved model. Shortening existing output automatically
would risk removing qualifications, so the experiment does not do that.

The synthetic counterexamples also cover negation removal, a local survey widened
to a state, proposed policy described as implementation, and a copy fee described
as an application fee. All defeat short claim/exact quote pairing. A deliberately
cherry-picked exact quotation defeats text-equality checks too. These tests are
expected to expose limitations; passing them is not a release verdict.

LAW added two reproducible counterexamples, retained unchanged in the old
`audit_unit` experiment: selecting "eligible for support" from "The applicant is
ineligible for support." passes substring equality, and selecting only "Species"
under a required header ID passes while omitting "Endemic to". Neither is fixed
by calling the matched text exact. The revised replay records both failures and
the selection-only assembly of their full synthetic source passages.

## Smaller candidate data contract

The model output has exactly two fields:

```json
{"status": "selected", "passage_ids": ["retained-passage-a", "retained-passage-b"]}
```

`selected` requires a nonempty ordered subset of the retained IDs.
`insufficient_evidence` requires an empty list. Reject unknown IDs, duplicates,
wrong types, status mismatches and every additional field. No model-provided text,
quote, offsets, date, URL, title, scope interpretation or review verdict is allowed.
The finite retained evidence set bounds selection size; the comparative 35-word
claim restriction is not applied to source text. Do not truncate long passages.

The app assembles each selected passage with all transitive required context,
without asking the model to select the header or quote the right words from it.
Within a selected unit, dependencies precede their dependent context; selected
units retain model order. Shared required context can be repeated across units
so each unit remains self-contained; it is deduplicated within one unit. Reject
missing dependencies, cycles or document/generation/page mismatches, with no
partial acceptance. Display the whole retained header and caption text, including
column meanings. Do not interpret or calculate fragmented table values.

Illustrative app-owned shape after mechanical assembly:

```json
{
  "contract_version": "passage-selection-proposal-v2",
  "mode": "source_passages",
  "units": [{
    "passage": {
      "passage_id": "selected-passage-id",
      "text": "Entire retained source passage, unmodified and untruncated.",
      "provenance": {"reader_url": "server-resolved generation and passage URL"},
      "publication": {
        "state": "metadata",
        "year": 2025,
        "label": "Source publication year: 2025 (source metadata)"
      },
      "limitations": {}
    },
    "required_context": []
  }],
  "checks": {"mechanical": "valid", "semantic": "not_assessed"}
}
```

The example is structural, not source content. The app also retains actual source
document, generation, physical page, original passage offsets, label, source URL,
reader locator and date basis. Provenance and limitations belong to each passage,
including each header. The model never owns these fields or the checks. No factual
introduction, heading, summary, comparison, conclusion or transition is generated.

A whole retained chunk is not necessarily a complete sentence, paragraph, table
or evidentiary context. The prototype does not reconstruct missing neighboring
paragraphs/pages. Context completeness, including antecedents, exceptions and
qualifications, remains an independent gate. If the complete necessary context is
unavailable, an explicit limitation is required; the current assembler does not
automatically detect or explain every missing element. The prototype's `selected`
status means selection only, not "direct answer", "complete procedure" or
"sufficient evidence". Output must remain identified as source passages.

The review rubric separately labels direct, partial and unanswerable questions.
A generic warning cannot satisfy a partial case that needs a specific missing
element disclosed. Determining and presenting that limitation is an unresolved
runtime design requirement, not something this assembly test has solved. Do not
add a region-, species-, document-, question- or answer-specific workaround.

## Deterministic publication-year presentation

Attach a publication label to every source in a unit, including brief answers.
Resolve it from that exact source's metadata. Never ask the model to remember it
or borrow another source's date. Keep the label with its passage and citation;
frontend presentation requires a separate Impeccable and rendered review.

The prototype recognizes explicit publication fields: `prism.publicationDate`,
`citation_online_date`, `citation_publication_date` and `datePublished`. It accepts
strict year or calendar-date values and requires agreement on the year. It retains
the fields and values that produced the label. Generic `dc.date`, catalogue
titles, filenames, URL paths, upload dates, retrieval dates and years mentioned in
passage text cannot establish a publication year.

Recognized malformed or conflicting metadata produces "Source publication year
unresolved". Missing supported metadata produces "Source publication year not
established". The prototype reports a metadata-derived year, not an independently
verified publication date or publisher identity. A later ingestion change could add a reviewed typed
date record with evidence, but that is outside this proposal.

For the saved landscape passage, the two explicit publication fields agree on 2025.
The app can therefore supply that year without an LLM call. The action-plan
passage has no supported date metadata and remains unknown; its upload path must
not become its publication year. Publication year is not observation period,
reference year, commencement date, proof of legal currency or proof that a reported
figure still applies. Retain extraction and legal-currentness cautions independently.

## Prototype and reproducible evidence

`experiments/claim_evidence_contract.py` is standard-library-only code outside the
backend. No production module imports it. It preserves the failed substring
experiment and adds whole-passage selection, full required-context closure and
source-date presentation. None of those checks proves meaning.
Every result explicitly retains `semantic: not_assessed` and `release: hold`.

Run the 24 offline falsification tests:

```sh
python3 -m unittest discover -s experiments -p 'test_*.py' -v
```

Replay the immutable report pair, providing its private directory and a new output
path. The script refuses hash mismatches and output overwrite:

```sh
python3 experiments/claim_evidence_contract.py \
  --captured-report-directory /absolute/path/to/private/reports \
  --output /absolute/path/to/new/replay.json
```

Input medium capture SHA-256:
`39f9a2b4c1276e27c35a08d7c41bc03caa0e58f684cf9d17258269abd0f5fadb`

Input high capture SHA-256:
`bb9be999db8253428db92ec0a46f8f3e597fe21a000347b86b3a3ceb7e00f4e9`

Preserved v1 replay SHA-256 (before reviewer counterexamples and label correction):
`93e3009915f452cd246cc84d4f04ce7f13b8729fba22ee6f5483d76d29a402f0`

Revised v2 replay SHA-256 (adds selection assembly and reviewer counterexamples):
`12ddda15c4682aa33c76b1ad3e0cb73001473b80080681d590d77ea3e7e49aab`

LAW's independent review of the original `3c8378103` proposal, including the
counterexamples and rubric, has SHA-256:
`ef64fb6c16d74d8d63fb5bea8deac05fc0e44975c6b1659a36545157eeb1b0aa`

Raw captures and replay output stay private and out of Git/static deployment.
The replay retains the original reports' known status and never turns consumed
diagnostics into independent held-out cases. It spends nothing and reads no key,
environment file, ledger, SQLite database or native corpus.

## Falsifiable review rubric

Before candidate selection, independent reviewers must freeze a fresh set of
source-reviewed questions and retained complete blocks, separate from every
consumed capture, synthetic development probe and assembly fixture. For each
case, record its class (directly answerable, partially answerable or unanswerable),
required support IDs, necessary referents/scope/qualifications, expected limitation,
source-block budget and expected useful behavior. This revision creates no fresh
independent set and makes no claim that the rubric has passed.

A directly answerable control whose complete support fits the declared budget must
return a useful, relevant, complete passage with a working citation. Preserve
accepted positive controls such as the monsoon recharge statement and explicit
procedural steps. Empty output, irrelevant excerpts or unnecessary abstention fail
that case; reject-all behavior cannot pass the experiment.

Partial controls must disclose the specific missing element without completing it
from model knowledge. Unanswerable controls must not acquire a fabricated inference.
Evaluate inference-dependent comparisons separately: useful evidence browsing is
not a complete synthesized explanation. A mechanically valid empty selection can
still be an incorrect abstention, and a valid nonempty selection can still be useless.

Negative controls must include word-prefix removal, incomplete header meaning,
an obsolete rule without its withdrawal, exceptions on following paragraphs or
pages, partial tables, orphan antecedents, conflicting versions and irrelevant but
exact passages. Each must preserve the complete necessary context or provide an
explicit adequate limitation. Any material misleading scope, quantifier population,
negation, modality, geography/taxon, institutional role, procedure/fee type, date or
currency omission blocks progression. Exact strings cannot compensate for it.

Every displayed body and dependency must retain exact original offsets and correct
document, generation, page and reader locator. Altered text, absent required context,
wrong-source dates, untrusted model metadata and broken source links fail the case.
This offline dictionary assembler preserves supplied provenance but does not open
originals or check live links. Later verification must establish those properties
against actual source artifacts; copied metadata alone cannot establish them.

Independent reviewers judge relevance, referents, scope, conflicts and misleading
omissions using those frozen requirements. Unresolved disagreements remain failures.
Report correct useful answers, correct partial answers, justified abstentions,
unsupported claims, misleading omissions, wrong citations and unnecessary
abstentions separately by question class. Never trade one material failure for an
aggregate gain, nor infer semantic acceptance from mechanical validity or test
counts. Consumed captures and new independent controls remain separate reports.

## Review and implementation boundaries

The new selection replay uses deduplicated primary-support IDs from historical
outputs only as assembly fixtures. It is not a new model selector, independent
held-out evaluation, evidence of relevance or a repaired historical answer. The
synthetic across-chunk and irrelevant-selection controls intentionally remain
mechanically valid with semantic status unassessed and release held.

Before broader implementation, LAW and QA must review the revised exact head,
24 tests, new immutable replay and unresolved limitations against the rubric above.
Publication labels deliberately say "source metadata": the parser does not verify
publisher identity. Context selection must be assessed separately from output
structure; no word-count cap may silently remove a required qualification.

After a design is accepted, a separate implementation would change the provider
schema, prompt budgeting, native normalization, public response model, cache
contract version and client rendering together. Retain provider/model/effort and
generation identity. Recompute the reservation against the actual serialized
request/schema before dispatch. Preserve caps and single-attempt accounting.
Reusing old cached paragraph output under a new contract is prohibited.

Offline runtime and negative tests, independent relevance/context assessment,
and rendered desktop/phone checks would precede any new paid acceptance plan.
The coordinator must freeze preview dispatch and inspect fresh canonical totals
before proposing a budget or production reconciliation. No existing diagnostic
credit, cap increase, larger model, automatic retry or public activation is
authorized by this document.
