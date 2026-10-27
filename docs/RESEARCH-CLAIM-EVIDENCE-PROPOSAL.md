# Research answers: claim and evidence contract proposal

Status: offline proposal for LAW and QA review. No production implementation,
provider calls, budget changes, corpus access or release approval. The user testing
preview remains intact. The current public Anthropic release remains held.

## Decision requested

Approve a bounded implementation experiment that separates each short claim from
its exact supporting excerpt and makes publication-year presentation app-owned.
Do not approve ordinary generated paraphrases for public release on the strength
of this format. The replay below disproves that inference.

My recommended next experiment is an excerpt-first response: the model selects
relevant source material; the app supplies its exact text, citation, date and
limitations. Generated short paraphrases can remain in evaluation packets for
comparison. If the product requires free paraphrase in the public answer, retain
the existing semantic acceptance hold until a separate reviewed method establishes
acceptable behavior. This proposal neither chooses nor funds another model.

The tradeoff is explicit: copying source wording eliminates the observed rewriting
of a quantified population, but can still mislead through selection or missing
context. It also cannot always provide a fluent direct explanation. LAW and QA
must evaluate usefulness and context preservation, not merely exact text identity.

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
| Proposed 35-word claim plus exact excerpt | Still passes | Still passes | Shortness and pairing do not establish meaning |
| Excerpt-only text equality | Rejects transformation | Rejects transformation | Blocks rewriting; also rejects valid paraphrase |
| Semantic correctness | Still requires review | Still requires review | Never derived from the rows above |

All 12 original long paragraphs fail the proposed 35-word bound, including water
answers reviewers accepted. That is a contract mismatch, not twelve semantic
failures or proof of an improved model. Shortening existing output automatically
would risk removing qualifications, so the experiment does not do that.

The synthetic counterexamples also cover negation removal, a local survey widened
to a state, proposed policy described as implementation, and a copy fee described
as an application fee. All defeat short claim/exact quote pairing. A deliberately
cherry-picked exact quotation defeats text-equality checks too. These tests are
expected to expose limitations; passing them is not a release verdict.

## Candidate data contract

Use a versioned internal response, separate from the existing paragraphs contract.
Each unit has one intended proposition and its own supports. A provisional bound
of 35 words and a maximum of four units limits answer size; it does not determine
whether a sentence contains one proposition. Review the limit against necessary
legal and ecological qualifications before enforcing it in a product.

The model selects a primary passage and exact excerpt. Additional passages are
allowed only as explicit support for that unit, including required table headers.
The app resolves each excerpt to original passage character offsets and retains
document, generation, page, passage ID and reader URL. Ambiguous repeated matches
must be disambiguated by an explicit range or rejected. No punctuation changes,
ellipsis insertion or silent quote repair are allowed.

For the experimental paraphrase lane, each unit also has model-generated claim
text. For the recommended excerpt-first lane, the answer body is the resolved
source text; the model cannot supply an independent factual introduction, heading,
conclusion or transition. Use fixed non-factual app text where needed. Long excerpts
that cannot preserve qualifications within the chosen bounds must lead to the
source reader or an explicit evidence limitation, not automatic truncation.

Illustrative server-owned shape after validation:

```json
{
  "contract_version": "claim-evidence-proposal-v1",
  "mode": "source_excerpts",
  "units": [{
    "body": "Unmodified text resolved from a selected source excerpt.",
    "supports": [{
      "passage_id": "selected-passage-id",
      "start": 0,
      "end": 60,
      "reader_url": "server-resolved generation and passage URL",
      "publication": {
        "state": "metadata",
        "year": 2025,
        "label": "Source publication year: 2025 (publisher metadata)"
      }
    }],
    "checks": {"mechanical": "valid", "semantic": "not_assessed"}
  }]
}
```

The example is structural, not source content. The model must not set checks,
reader URLs, dates, legal currency, review status or release decisions. Citation
links are derived only from that unit's validated supports. A citation elsewhere
in the answer cannot support this unit. Multi-source comparisons and inferences
need their own support set and separate review; an "inference" label does not
make an unsupported inference acceptable.

Preserve whole-passages access and required header context. Header identity does
not establish safe numerical interpretation of incomplete table rows. Keep the
existing restrictions on table calculations and incomplete extracted procedures.
Do not add a region-, species-, document-, question- or answer-specific rule.

## Deterministic publication-year presentation

Attach a publication label to every source in a unit, including brief answers.
Resolve it from that exact source's metadata. Never ask the model to remember it
or borrow another source's date. Keep the label with its claim/excerpt and citation;
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
verified publication date. A later ingestion change could add a reviewed typed
date record with evidence, but that is outside this proposal.

For the saved landscape passage, the two explicit publisher fields agree on 2025.
The app can therefore supply that year without an LLM call. The action-plan
passage has no supported date metadata and remains unknown; its upload path must
not become its publication year. Publication year is not observation period,
reference year, commencement date, proof of legal currency or proof that a reported
figure still applies. Retain extraction and legal-currentness cautions independently.

## Prototype and reproducible evidence

`experiments/claim_evidence_contract.py` is standard-library-only code outside the
backend. No production module imports it. It demonstrates quote resolution, own
unit context, date derivation and the inability of those checks to prove meaning.
Every result explicitly retains `semantic: not_assessed` and `release: hold`.

Run the 14 offline falsification tests:

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

Initial replay SHA-256:
`93e3009915f452cd246cc84d4f04ce7f13b8729fba22ee6f5483d76d29a402f0`

Raw captures and replay output stay private and out of Git/static deployment.
The replay retains the original reports' known status and never turns consumed
diagnostics into independent held-out cases. It spends nothing and reads no key,
environment file, ledger, SQLite database or native corpus.

## Review and implementation boundaries

Before broader implementation, ask LAW to assess quantifier population, scope,
negation, procedural role, source date and complete-context preservation. Ask QA
to challenge cross-unit citation borrowing, conflicting dates, malformed spans,
duplicate quotes, prompt injection in source text, cache separation and the known
exact-but-misleading excerpt. Include correct paraphrases and useful long answers
as controls so rejecting everything cannot count as success.

After a design is accepted, a separate implementation would change the provider
schema, prompt budgeting, native normalization, public response model, cache
contract version and client rendering together. Retain provider/model/effort and
generation identity. Recompute the reservation against the actual serialized
request/schema before dispatch. Preserve caps and single-attempt accounting.
Reusing old cached paragraph output under a new contract is prohibited.

Offline runtime and negative tests, independent relevance/entailment assessment,
and rendered desktop/phone checks would precede any new paid acceptance plan.
The coordinator must freeze preview dispatch and inspect fresh canonical totals
before proposing a budget or production reconciliation. No existing diagnostic
credit, cap increase, larger model, automatic retry or public activation is
authorized by this document.
