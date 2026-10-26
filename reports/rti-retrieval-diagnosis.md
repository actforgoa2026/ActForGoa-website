# RTI retrieval diagnosis and rejected reranker experiment

26 October 2026. Runtime `e274f85`; corpus `20261026T131818-law-23a2e6a6`. Offline only: no paid provider calls, source changes, index rebuild or deployment. The usage ledger remained at 182 attempts and $0.634595 conservatively reserved.

## Decision

Keep production retrieval unchanged and the RTI acceptance gate open. The fee passage is indexed and already retrieved as a keyword candidate. This is a ranking/selection failure, not missing ingestion. The general reranker tested below improves RTI but loses reviewed evidence in other cases. A higher aggregate score does not justify those regressions.

## Exact cause

For the existing compound RTI question, passage `e5d0e7777a79a19cf17cced54e173507` is the official applicant manual's physical page 7. It contains the explicit non-BPL application fee in prose.

| Manual passage | Keyword rank | Dense rank | Query concepts matched in body | Combined score |
| --- | ---: | ---: | ---: | ---: |
| Cover, page 1 (`3ff91ad9…`) | 15 | 3 | 4 of 8 | 0.0480 |
| SMS examples, page 18 (`262d4ddf…`) | 12 | 10 | 3 of 8 | 0.0405 |
| Fee, page 7 (`e5d0e777…`) | 14 | Outside top 300 | 2 of 8 | 0.0191 |

Reciprocal-rank fusion rewards cover/SMS passages for appearing in both channels. The body-coverage boost also favors their repeated query words. The two-passage document cap then fills with cover/SMS results and excludes page 7. Raising the candidate count alone cannot fix this: page 7 is already in the candidate pool. The complete cited passage is preserved correctly in the reader.

Earlier exploratory changes used rare-term conjunctions, title-inclusive coverage, a cover penalty and within-document novelty. They did not reliably recover the fee; rare river aliases could also dominate the focused channel. These experiments were discarded, and none is part of production retrieval. No source ID, page number or answer has been hardcoded into ranking.

## Local relevance-model experiment

Tested the [Sentence Transformers MS MARCO MiniLM L6 cross-encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) at pinned revision `233902d25c440f23af6f7d6e94d2946bac0bee0a`, using its official quantized ONNX export and the existing ONNX Runtime dependency. This experiment scores question/passage pairs locally. The downloaded model and experimental code remain outside runtime packaging and Git.

The experiment replaced only the final candidate ordering: descending cross-encoder logit, with existing relevance as a tie-break. Candidate retrieval, duplicate filtering, document caps and citation slices remained unchanged. Input paired the question with title plus exact passage text, with a 384-token limit, batches of eight and two CPU threads. Exact model/tokenizer hashes and result checks are in [the machine-readable report](rti-retrieval-diagnosis.json).

- Ran all 16 existing retrieval smoke queries, five legal questions and 50 ecology questions, then four additional RTI phrasings: 75 queries total.
- Both baseline and reranker passed all 16 coarse smoke checks. All 75 reranked result sets retained exact page-slice integrity. The ecology queries were not newly scored against human relevance judgments.
- The original RTI question recovered manual pages 4 and 7 at result ranks 3 and 4, and the fee survived prompt budgeting. Four of five RTI phrasings recovered the reviewed fee passage; the keyword-style phrasing still failed.
- The revised farming scheme's page 4 reporting destination/deadline passage disappeared from the top ten. Both reviewed institutional school-dog SOP passages disappeared from the dog results, with an older municipalities-act excerpt ranking first. These are losses of reviewed evidence, not tested model-answer failures.
- Median end-to-end retrieval time rose from 0.096 seconds to 1.568 seconds on this Mac; reranked p95 was 1.840 seconds. Railway latency and memory were not measured.

## Stronger offline gate

Added `tests/research/retrieval-evidence-cases.json` and `scripts/evaluate_retrieval_evidence.py`. The gate runs the existing 16 smoke checks and nine exact-evidence cases: five RTI phrasings plus TCP, farming, institutional dogs and Parra. It verifies cited slices and checks that reviewed evidence survives the actual model-prompt budget, not merely that it appears in search results. The corpus generation and passage existence are validated before scoring.

| Gate | Baseline | Experimental reranker |
| --- | ---: | ---: |
| Existing term-coverage smoke checks | 16/16 | 16/16 |
| RTI fee evidence in prepared prompt | 0/5 | 4/5 |
| Other reviewed legal evidence retained | 4/4 | 2/4 |
| Total exact-evidence cases | 4/9 | 6/9 |

The baseline gate deliberately exits nonzero while the RTI gap remains. Its tests also reject mismatched citation slices and evidence that is retrieved but later dropped from the bounded prompt. A missing expected passage can sometimes have a valid alternative; that alternative needs review before changing the expected set. This gate is a regression aid, not a complete relevance benchmark or legal-currency certification.

Reproduce against the verified corpus without any API credential:

```sh
python scripts/evaluate_retrieval_evidence.py \
  --data-root /path/to/refreshed-data-20261026-v2 \
  --output .research-release/retrieval-evidence.json
```

All 60 backend tests pass. No frontend/runtime change was made in this follow-up. Live model acceptance, the RTI correction, remaining claim issues and deployment remain blocked as recorded in [the release validation report](openrouter-chat-validation.md).
