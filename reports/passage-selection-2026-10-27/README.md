# Complementary corpus passages and bounded provenance

27 October 2026. The frozen candidate improves original exact-evidence recall from **4/9 to 9/9**, and the separately frozen assessment from **11/12 to 12/12**, without losing any baseline pass. Four older development questions still miss their specified passages. This is offline source recall, not generated-answer acceptance, current-law verification or a release authorization.

Candidate code was frozen at `6fea94e0f22bf7f2646799d1e0af3e048f15d361`, integrated through `05840d4ac794445971213bc09ccaa4438aed2328`. Runtime changes are `2a10957` (selection) and `919304c` (prompt compaction). Later commits contain reports only. All candidate code hashes are in `candidate-freeze.json`. The baseline is `9d705d946cbdc55ad0d9bda4cfb9f243f76b177c`. The corpus remains generation `20261027T065155-law-5bc5619b`; it was not rebuilt.

## What changes

Hybrid keyword/vector retrieval still chooses the candidate pool and document slots. Within each document's one or two available slots, selection jointly maximizes coverage of requested details outside the document title, with a relevance preference to preserve stronger hybrid matches. Standard English Snowball stemming replaces the development selector's improvised prefixes: `notify` and `notifications` remain distinct, while `applicant` and `application` share a stem. A request-local stemmer avoids shared mutable state. Duplicate filtering runs again after selection, with bounded backfill from the original pool. Explicit single-document searches keep their existing behavior.

This addresses the observed cover-page/introductory-passage competition, rather than changing topic weights or adding question/ID exceptions. It does not repair every document-selection or semantic paraphrase failure. The only new service dependency is the small pure-Python `snowballstemmer==3.0.1`, pinned in both requirement files. The locally tested cross-encoder and additional embeddings are not in the service, dependencies or runtime packaging.

`prepare_answer` now stores identical document provenance once in a `sources` object. Each evidence item retains its exact text, passage ID, physical page/label, offsets, page heading and extraction warning, and references its source entry. Source keys include document ID, generation, title, official URL, dates, publisher class, legal-currency warnings, topics and verification metadata. Different versions or caveats are never merged. Instructions explicitly require reading the referenced metadata and citing passage IDs only. No private paths enter the prompt. The 24,000-byte cap and conservative token allowance are unchanged.

Compaction alone does not fix an exact-evidence case in this packet. On the selected results it preserves 21 additional passages across the 72 questions within the same cap. More retained text is not itself proof of better answers. Provider acceptance must check the new source-reference layout.

## Frozen evidence and results

All original 9, prior 15 and prior 20 questions are known development/regression evidence. They were iterated on; `development-variants.json` discloses the tested families and failures. Embedding-only, cross-encoder-only, field-score and several document/slot variants lost reviewed support and were rejected. No aggregate gain was treated as sufficient while a baseline pass was lost.

Before the final candidate assessment, 12 new questions were source-reviewed across four additional official documents: tree preservation, individual farmer registration, the AWBI August 2025 reporting letter, and the Forest Department's public-services notification. The question/locator/text-hash/original-hash packet was frozen in commit `2740e02` (original pre-rebase commit `c25bd65`). SHA-256 remains `7420098b89731896c4689f1b16bfb5003f41b98a0e302756b0d6de9d96c26d9f`. No assessment question was searched before the candidate freeze. It was evaluated once; no code or expectation was changed afterward. The same agent reviewed the sources and built the candidate, so this is not independent human validation or a representative relevance benchmark.

| Set | Baseline | Compaction only | Selection only | Combined candidate |
| --- | ---: | ---: | ---: | ---: |
| Original exact cases | 4/9 | 4/9 | 9/9 | 9/9 |
| Prior fifteen | 10/15 | 10/15 | 12/15 | 12/15 |
| Prior twenty | 19/20 | 19/20 | 19/20 | 19/20 |
| Frozen twelve | 11/12 | 11/12 | 12/12 | 12/12 |
| Broad smoke checks | 16/16 | 16/16 | 16/16 | 16/16 |

Exact support is measured both before and after the real prompt budget. `final-assessment.json` retains each mode's retrieved IDs, prompt IDs, support flags, prompt bytes and token bound. Expected IDs and prior relative-order conditions were not weakened. There are **zero baseline regressions**. All 288 mode/case checks preserve exact saved-page slices, reader locators, duplicate limits, the general two-passage cap, bounded prompt and citation-schema consistency. Maximum combined prompt is 23,933 bytes. Eleven distinct source originals match their checksums and complete saved text was checked. No new PDF visual or browser verification is claimed.

All **149 backend tests pass**, including source-identity/currentness round trips, retained Unicode text, immutable input, conflicting source-caveat separation, source-reference citation rejection, complementary detail selection, concurrent stemming and pre-native preservation guards. Five existing SWIG/PyMuPDF warnings remain. The fresh environment install attempt timed out downloading a transitive PyPI wheel; tests used the existing pinned research environment with the added dependency installed only in this worktree's isolated target directory.

Local paired search timing after the first sample: baseline median 49 ms and candidate median 97 ms. This is one sequential local run, not a randomized latency comparison or a production capacity measurement. No paid calls, genuine ledger operations, deployment, main merge, UI changes or Device Hub use occurred.

## Remaining claim-level gaps

The exact failed IDs remain failures. The following review considers only the actual surviving prompt text; it does not alter the frozen expected sets. Full locators, source hashes and relevant saved slices are in `remaining-case-evidence.json`.

- **`held-fee-1`: amount for a non-BPL Goa online RTI applicant.** The specified manual page 7 does not receive a document slot. The [saved Goa portal FAQ](https://www.rtionline.goa.gov.in/FAQ), passage `6beb1ebe2e03b602bc1184416cde6681`, supports payment of the prescribed fee and payment modes, but gives no amount. The returned [ICAR-CCARI page](https://ccari.res.in/rti.html), `9306790c5c53f27ea915c7cd1564a065`, states Rs 10 for its own institution and payment route; it is not equivalent proof of the Goa state portal fee. No equivalent amount support is present. A safe response must say the retrieved portal evidence does not establish the amount, or abstain from the numeric answer. It must not transplant ICAR fees or pollution-consent tables into the portal procedure.
- **`held-fee-2`: payment methods and the application charge in the Goa RTI guide.** The [FAQ](https://www.rtionline.goa.gov.in/FAQ) passage above supports internet banking, ATM/debit, Master/Visa credit/debit and UPI. The returned [manual](https://rtionline.goa.gov.in/Applicant_Module_User_Manual.pdf) passages `8cc4a696018cfcdd6e82c9ff7228af21` (page 12) and `cd0e94264831653dd6c7927e997516dd` (page 18) discuss additional-payment examples, not the initial charge. No equivalent initial-fee support survives. A supported partial answer can attribute those payment modes to the FAQ and explicitly leave the application amount unresolved. It must not call the illustrative Rs 25 the initial fee, or claim the missing manual's RuPay detail from memory.
- **`held-dogs`: responsibility for handling school-premises dogs under the institutional SOP.** The required page-5 chain concerning Animal Husbandry/sterilization and onward shelters is absent. The surviving [institutional SOP](https://awbi.gov.in/uploads/regulations/176431409245SOP-11282025001522.pdf) passage `1a0e7e2717e3659c1a45962f4c1c7b89` (page 6) says local/municipal authorities must ensure removed dogs go only to designated shelters. `0f01b1b3c2b6afaa88fabaeae87ab6c5` (page 10) identifies District Magistrate monitoring and reports to AWBI through State departments. These support specific limited duties, not the full capture/handling chain. General ABC Rules staff provisions are not a substitute for a school-specific authorization. A partial answer may name those exact duties and say the retrieved text does not identify the full handling procedure. Private capture, an unconditional relocation instruction, current court position and actual shelter capacity remain unsupported.
- **`frozen-licensing-bodies`: A2/A3 authority mapping.** The expected PDF page-1 ID is absent, but equivalent support is present: the [saved TCP procedure webpage](https://tcp.goa.gov.in/procedure-to-obtain-the-permission/), `f60143b3aa99a916174be95136c59e5d`, and [2010 regulations](https://tcp.goa.gov.in/wp-content/uploads/2017/GLDBCR_2010/regulations/1011-24-SI-OG.pdf), `e0ea390e4eae2675631cb10ef03d60bf` (page 109), explicitly map A2 to the Municipal Council building licence and A3 to the Village Panchayat building licence. The [2018 compilation](https://tcp.goa.gov.in/wp-content/uploads/2018/12/Gldbcr_2010_original-_Amm2018sept-with_appeal-fee.pdf), `7c18f9fd0c845da268745e0e91ef1c88` (page 152), also states that mapping. A source-qualified answer to this specific mapping is supported. It must keep TCP technical clearance separate and preserve current-law limitations. The strict ID metric still records failure.

Generated-answer QA should test these boundaries clause by clause, including safe partial answers/abstention for the first three and exact distinct approvals for the fourth. This review is not a finding that the model actually follows them.

## Preservation and reproduction

Every Library/Zvec/SQLite access used a guarded disposable APFS byte copy. The wrapper copies only the research index and originals, removes provider configuration from the child environment, waits for native process exit, hashes the source again, and removes only its owned scratch directory. New review children reject sealed/snapshot paths and anything below `Documents/ActForGoa Recovery`, including symlinks, before native imports. No genuine ledger was copied or initialized.

All 1,236 source data files stayed at fingerprint `4011a4c5331357f96552b04d4f9ce3307c5a7865e0d091a36ed602e67c4186eb`. Expected Zvec close-time metadata writes affected one discarded scratch index only. The final byte-only audit independently matched **all 1,258 sealed entries**, their exact directory/file coverage, and seal SHA-256 `26227d014c3c948f7d10f0d4d13dab4820d1b510d14772e95cb44f7361ab0249`. Preserved source, service, originals and manifests were not modified.

Use the pinned research dependencies and a new output path outside preservation roots. An independent rerun now reuses an already inspected assessment; it is not a new held-out set.

```sh
python reports/passage-selection-2026-10-27/run_copy.py \
  --source '/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-sealed-package-v1/data' \
  --task evaluate --output /tmp/actforgoa-passage-independent/evaluation.json
python -m pytest tests/research -q
```

The wrapper refuses existing output files. `candidate-freeze.json` verifies runtime hashes and the assessment packet before queries. Compact evidence is tracked here; full immutable outputs and development captures remain under this worktree's `.reports/passage-selection/`. Their manifest identifies unadopted model artifacts and all intermediate results. No raw corpus, vector package, credential or usage ledger is added to Git.

Coordinator owns integration and live acceptance. The service must install the new pinned stemmer and QA the compact source-reference prompt using actual Anthropic answers before deployment. Research remains held until that independent review and the other release checks pass.
