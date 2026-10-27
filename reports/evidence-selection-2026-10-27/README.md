# Rejected field-weighted retrieval candidate

27 October 2026. One bounded offline candidate was assessed and rejected. Runtime retrieval remains unchanged. The candidate recovers two known fee questions but loses both previously passing farming questions and one newly frozen payment-verification question. No second candidate or retuning followed the frozen-set results.

Branch: `codex/research-evidence-selection`, based on research integration `9cf0b706f851a47bb33a7f78bd5bbecf864c33a7`. Corpus generation remains `20261027T065155-law-5bc5619b`. No provider, ledger, UI, dependency, ingestion, index, main or production change was made. This is report-only evidence; service code does not import the candidate.

## Frozen scope

The original nine exact-evidence cases and the previously inspected fifteen held-out cases were treated as known development/regression evidence. Their questions, expected passage IDs and prior relative-order constraints were retained.

Before implementing or assessing the candidate, twenty separate source-reviewed questions were frozen in commit `4682f10`. They cover initial fees, portal steps, payment verification, additional charges, farming, institutional dogs, building permissions and wetland ownership. Each records the exact reviewed passage, page/offset locator, text hash, original hash and source URL. This set includes eleven distinct supporting passages beyond the previously inspected case expectations; source overlap still limits independence. It is a small source-recall check, not a representative general relevance benchmark.

- Frozen fixture SHA-256: `86863c2ec6b8888d4a1bd41304b6e6fc079119cdb8904348090dcb475e9f2b88`.
- Candidate SHA-256 before the sole assessment: `e40797db4509e01ba9f8a8f58df62e2e9fbdbce7473215dc230ea5956b81ac42`.
- Unchanged runtime `backend/library.py` SHA-256: `1449933aeff9ec08501b428f42bdc2b79a939caf889c53f0d444fb337da989c8`.

`freeze.json`, `design.md` and `assessment-plan.json` record the sequence and predetermined specification. `candidate_runs: 0` in the immutable freeze record describes the time of freezing; the final evaluation records one assessment. The new questions are now known evidence and must be treated as such in future work.

## Candidate and results

The candidate replaces only the existing coverage boost with field-weighted lexical scoring. Titles contribute document context; body term frequency is length-normalized and saturated. Complete words replace five-letter-prefix coverage in this component. Existing reciprocal-rank fusion, authority preference, candidate pool, two-passage cap, duplicate filtering and prompt limits remain. This pointwise scoring does not reuse the rejected second-passage novelty selector or cross-encoder. Parameters were fixed once; no topic, document, page, question or passage ID appears in ranking behavior.

| Evaluation set | Existing runtime | Candidate |
| --- | ---: | ---: |
| Original reviewed cases | 4/9 | 4/9 |
| Previously inspected fifteen cases | 10/15 | 10/15 |
| New frozen source-reviewed questions | 19/20 | 18/20 |
| Existing broad smoke checks | 16/16 | 16/16 |

The candidate gained `rti-non-bpl` and `held-fee-1`, but regressed `legal-farm`, `held-farm` and `frozen-verify-result`. All twelve candidate failures are retained in the machine-readable summary. The repair gate failed with exit 1. No expected evidence was changed to improve these counts.

## What failed

The change can repair document selection for a specific query but does not reliably find the requested relationship within the document:

- In `held-fee-1`, the manual receives no baseline slot. The candidate moves its reviewed non-BPL fee passage to global rank 4 before caps, and includes it in the prompt. This demonstrates that the relevant document was present in the original candidate union.
- Four of the five original RTI phrasings still miss the fee passage. For the compound question, the cover and login instructions occupy the manual's two slots; the fee passage is rank 61 before caps. For the short fee question, cover/SMS passages still win and the fee passage is rank 31. Field weighting does not resolve generic source words versus the initial-fee procedure.
- For both farming questions, the reviewed reporting/deadline passage remains in the pool, at candidate rank 4 or 6. Two page-2 scheme passages take the document's slots first. In `legal-farm`, the second page-2 passage scores 0.06718 against 0.05765 for the required page-4 reporting passage. This is a substantive regression despite intact citation bytes, and does not repeat the earlier “notify”/“notifications” collision.
- In the frozen payment-verification case, page 15's additional-payment confirmation displaces page 10's initial-payment status and registration number. The candidate scores are 0.08622 and 0.08338 respectively. Similar vocabulary across different procedural stages still causes the wrong evidence to fill the cap.
- The frozen building-licence question fails both versions: the reviewed page-1 authority mapping is excluded after two other passages from that document. The expected set remains frozen; another returned passage would require separate source review before being accepted as an alternative.

These observations diagnose selection failures, not generated-answer errors. There were no model calls. Any further approach needs a separately bounded experiment and fresh source-reviewed assessment; this task does not try another weight, feature or selector after seeing the failures.

## Integrity and validation

All 120 paired result sets retain exact saved-page slices, working reader locators, at most two passages per document and the existing near-duplicate threshold. Every score uses evidence after the real `prepare_answer` budget. Maximum observed prompt size was 23,977 bytes against the unchanged 24,000-byte limit; citation-schema IDs match the prepared evidence exactly. Prompt-budget survival is included in pass/fail rather than checked only at retrieval.

All expected passage IDs resolve. All frozen text/offset/original hashes match the source review. Seven distinct source originals were checksum-verified, complete saved text was read through their last pages, and their original PDFs' final pages rendered. This is offline library validation, not browser, provider-answer or current-law acceptance.

Six synthetic experiment tests passed, with five existing SWIG/PyMuPDF warnings. They verify preservation guards before native imports, including symlink paths, complete-word behavior, document caps and cross-document duplicate filtering. The runtime remains byte-identical to the integration base already independently verified with 70 backend tests; that suite was not rerun to imply candidate acceptance.

The first source-capture attempt failed before opening an index because the diagnostic filename shadowed Python's `inspect` module. Renaming that report-only script fixed the import. Its disposable copy was discarded and preserved source bytes remained unchanged. This was infrastructure setup before the candidate existed; it was not an extra candidate assessment.

## Preservation and reproduction

Source: `/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-sealed-package-v1/data`. Source inventory fingerprint before and after each native child: `4011a4c5331357f96552b04d4f9ce3307c5a7865e0d091a36ed602e67c4186eb` across 1,236 data files.

`run_copy.py` uses the existing preservation inventory/guards, copies index and originals to an owned disposable APFS directory, strips provider environment variables, runs the child, waits for full exit, and checks the preserved source again. Expected close-time Zvec writes stayed in disposable copies. No preservation directory was opened through Library/Zvec/SQLite; no genuine usage file was copied or initialized. Reports remain outside the sealed root.

`final-preservation.json` records the final byte-only audit of all 1,258 seal entries and exact directories, all 2,623 restoration entries, all 2,623 original entries with only the previously recorded altered vector hash, and both unchanged historical manifests. The source seal remains `26227d014c3c948f7d10f0d4d13dab4820d1b510d14772e95cb44f7361ab0249`.

For an independent rerun of this exact rejected candidate, use the pinned research Python environment and a new report path outside preservation roots. Do not tune the candidate or fixture based on this already inspected set.

```sh
python reports/evidence-selection-2026-10-27/run_copy.py \
  --source '/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-sealed-package-v1/data' \
  --task evaluate \
  --output /tmp/actforgoa-fielded-independent/evaluation.json

python -m pytest reports/evidence-selection-2026-10-27/test_experiment.py -q
```

The evaluator refuses to overwrite an existing report. Exit 1 is expected for the rejected candidate; a preservation mismatch is a separate error. The inspection helper also uses the wrapper and is limited to known cases/source text.

Full durable evidence lives at `/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-evidence-selection`. `full-evaluation.json` has SHA-256 `96bfb9c43197ed7d84d99a1b263f8e31f10d858b72ad1f8db23d955465ab74ae`; the compact tracked summary retains per-case before/after prompt IDs, failures and relevant ranking details. The bundle also preserves source-capture evidence outside Git. `HANDOFF.md` and `evidence-files.json` provide final commit/PR identities and complete evidence checksums.

Generated answers remain held for retrieval and answer quality, provider credit/live acceptance and usage reconciliation. No paid call, genuine ledger operation, corpus upload, deployment, activation or main merge occurred. Coordinator owns integration and release. This report must not be merged as a runtime retrieval change.
