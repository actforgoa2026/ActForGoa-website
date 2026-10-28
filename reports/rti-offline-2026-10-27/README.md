# Offline RTI follow-up and preservation incident

Runtime retrieval remains unchanged. A candidate selection change fixed the original RTI cases but lost reviewed farming evidence in a frozen held-out question, so it was rejected. During validation, the installed Zvec 0.8.0 library also changed one preserved index file on close despite `read_only=True`. The exact accepted bytes were recovered into a separate restoration candidate; the original copy and all accepted manifests were left untouched.

Branch: `codex/rti-retrieval-offline`, based on research integration `ab6a19ce45af750f68235852be3a10f9dc0c5e60`. Corpus generation remains `20261027T065155-law-5bc5619b`. No corpus generation, runtime selection change, paid call, genuine ledger change, merge, deployment or production operation was performed. Four new tests cover the disposable-copy evaluator. No visual surface changed.

## Retrieval decision

The trial preserved the documents and their result slots. Within a document already receiving two slots, it retained the first selected passage and chose a complementary second passage for query concepts absent from the first. It weighted those concepts by rarity within that document's candidates, then preferred query concepts outside the document title when ordering the pair. It used no model, topic-specific rule, case text or passage ID in selection behavior. Candidate capture, corpus, search caps and `prepare_answer` limits were unchanged.

The original five RTI questions are development cases, not held-out evidence. Before testing the selector, 15 additional cases were frozen: six fee paraphrases, five contrasting RTI needs and four legal paraphrases. Their SHA-256 is `b9a137599f7eb3971e3bb7a9b8d8a75c80c8fdec5ea5223c1b00314a955d9757`. The candidate was not retuned after these cases exposed the regression.

| Check | Existing runtime | Rejected candidate |
| --- | ---: | ---: |
| Original exact evidence cases | 4/9 | 9/9 |
| Original non-RTI legal evidence | 4/4 | 4/4 |
| Existing broad smoke checks | 16/16 | 16/16 |
| Frozen held-out cases | 10/15 | 11/15 |
| Held-out fee questions | 2/6 | 4/6 |
| Contrasting RTI needs | 5/5 | 5/5 |

The higher aggregate score is not acceptable because `held-farm` regressed. For “Under Goa Shetkari Adhar Nidhi, whom must a farmer notify about crop damage and by when?”, the existing search puts reviewed passage `49c4df829e149d7df512df066a379ae0` on physical page 4 in the model prompt. The trial replaces it with `be330c4949ea5664d3094a240bfe1361` on page 5, concerning grievances and superseded notifications. Five-character prefix matching conflates “notify” with “notifications”: the weighted gain for the wrong passage is 3.927 versus 3.308 for the reporting/deadline passage. Word novelty does not identify the requested reporting relationship.

Two held-out RTI fee phrasings also remain unsuccessful. In `held-fee-1`, the fee passage is in the candidates but the manual receives no final document slot, so a within-document change cannot rescue it. In `held-fee-2`, “application charge” and “payment methods” favor additional-payment examples; the lexical method does not distinguish the initial fee from subsequent charges. The held-out institutional-dog paraphrase fails in both versions and is a separate pre-existing gap. None of these expected sets was weakened.

All 40 evaluated result sets retain the exact document-slot sequence and two-passage-per-document cap. Every returned citation matches its saved page slice and reader locator. Neither version introduces near-duplicate results under the existing shingle threshold. Required evidence is scored after the real prompt budget, not only after retrieval. These checks do not establish answer entailment or current legal applicability.

Measured locally after warming the encoder: normal baseline search median **32.5 ms**, p95 **144.6 ms**, across 120 calls. The diagnostic prototype including profiler capture and selection measured median **32.3 ms**, p95 **64.0 ms**, across 40 calls. Selection alone took median **1.13 ms**, p95 **3.62 ms**. These are different diagnostic sample sets, not evidence that the prototype is faster. Railway latency was not tested.

Evidence: `evaluation.json`, `held-out-cases.json`, `rejected_selector.py` and `evaluate_candidate.py`. The experiment lives in reports only; backend code does not import it. The diagnostic refuses to open a path within a preservation snapshot. No retrieval PR is proposed.

## Preservation incident and cause

I initially treated the library's `read_only` option as a guarantee that the preservation copy could not change. That assumption was wrong. The coordinator's byte-only snapshot verification at approximately 07:12 UTC had matched all 2,623 files. After this follow-up's library objects closed, a byte audit found exactly one changed file:

`legal-package/data/.research-index/generations/20261027T065155-law-5bc5619b/zvec/3/embedding.index.1.proxima`

| Identity | SHA-256 |
| --- | --- |
| Accepted snapshot file | `4c8c86b4cf9768ef21d237201218e6b05369d2f91b92729ce7553a6c7c973185` |
| Changed file, preserved as evidence | `4a39df4854b045f73cd9bc78bcbbf03ad52f3ca671ee18f2b4f19286ae017a56` |
| Recovered exact accepted file | `4c8c86b4cf9768ef21d237201218e6b05369d2f91b92729ce7553a6c7c973185` |

The file remains 157,696,000 bytes. Only eight bytes changed, within three fields: the footer CRC32C at offset 1,064,832, its update timestamp at 1,064,880, and the HNSW chunk timestamp at 1,081,440. The accepted timestamp is `2026-10-27T07:03:08Z`; the changed timestamp is `2026-10-27T07:25:56Z`. No graph, vector or document bytes differ in this incident. All other 2,622 snapshot files still matched, including all originals, all four SQLite databases and all earlier generations.

A disposable-copy reproduction confirmed the boundary: SHA-256 stayed unchanged after open and search, then changed on object destruction/close. The pinned [Zvec 0.8.0 interface close implementation](https://github.com/alibaba/zvec/blob/7b7532784a781e20541b4e315919e6abc6ff0ecb/src/core/interface/index.cc#L628) skips its explicit flush in read-only mode but still invokes streamer cleanup. The [HNSW chunk close implementation](https://github.com/alibaba/zvec/blob/7b7532784a781e20541b4e315919e6abc6ff0ecb/src/core/algorithm/hnsw/hnsw_chunk.cc#L131) unconditionally flushes; that updates the chunk time and refreshes the storage footer. The [index format implementation](https://github.com/alibaba/zvec/blob/7b7532784a781e20541b4e315919e6abc6ff0ecb/src/include/zvec/core/framework/index_format.h#L174) updates the footer timestamp and CRC32C. This explains why the higher-level read-only setting did not preserve file bytes.

Upstream main at `aed80691a84ee31ebad1caa2efa6c693f879a3f4` has a dirty-state guard in chunk close. It was inspected only; no dependency upgrade or untested runtime fix was adopted. Network activity was limited to reading public upstream code for this incident, with no corpus ingestion or provider calls.

## Exact recovery without replacing the accepted copy

`recover_known_metadata.py` reconstructs this specific file at a new output path. It verifies the changed whole-file hash and existing CRC, restores the two recorded timestamps, recalculates raw-seed-zero CRC32C for the 128-byte footer, and requires the resulting whole-file SHA-256 to equal the accepted hash. It refuses existing output paths and preservation-snapshot destinations. Three nearby timestamp candidates were tried; only `07:03:08Z` produced the pre-existing accepted whole-file hash. This is exact byte recovery, not a newly accepted index checksum.

The separate full restoration candidate is:

`/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-restoration-candidate`

All **2,623 accepted snapshot entries** match there. Its copied `snapshot-files.json` remains `2b86bf87e963fa1c2c5c6c3be894ba2c141777f5c330b0147e34c2daa2dcd095`. It has never been opened through Zvec. The original `/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27` still contains the one changed file, preserved for inspection; it was not overwritten or rebaselined. The coordinator retains the release hold and decides how to reconcile preservation locations.

The accepted snapshot also contains an older internal package allowlist: `legal-package/files.json` records `8696f35d…` for this file, while the subsequently accepted outer snapshot records `4c8c86b4…`. This mismatch predates the new incident and is consistent with the same close-time behavior during earlier validation. Exact outer-snapshot recovery does not repair that historical inner allowlist. Both manifests remain unchanged. A future deployable package needs a new, explicitly recorded allowlist after all native handles close, followed by validation on a copy.

Evidence: `read-only-integrity-incident.json`, `close-mutation-reproduction.json`, `exact-index-recovery.json`, `restoration-candidate.json`, `nested-manifest-audit.json` and the preserved forensic files outside Git. Both changed and recovered index bytes are retained at `/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-rti-followup/forensics/`; see `forensic-artifacts.json`. A final byte-only audit after the protected evaluation again matched all 2,623 restoration-candidate entries and confirmed the original copy still has exactly its recorded single mismatch.

## Verified mitigation and handoff

Use `scripts/evaluate_research_copy.py` for the evidence gate. Its parent reads ordinary bytes only, copies the index and originals to a temporary working directory, runs the evaluator in a child process, waits for full process exit, and then checks source hashes. It excludes credentials and usage data, refuses reports inside preservation snapshots, and deletes only its owned temporary directory.

The real-corpus run preserved all **1,191 source files**. The child copy's one Proxima file changed on exit, exactly as expected, and was discarded. The original gate still reports **4/9 exact evidence and 16/16 smoke**, with exit 1 for the known failures. The guard's source fingerprint is identical before and after child exit: `a17c95eb18ce5fe20b4baccb83718e619b27931da42bbb96a8fcaf109e0f7c2c`.

```sh
python scripts/evaluate_research_copy.py \
  --data-root '/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-restoration-candidate/legal-package/data' \
  --cases reports/recovery-2026-10-27/retrieval-evidence-cases.json \
  --output /path/outside-preservation/protected-copy-gate.json
```

Backend tests: **66 passed**, including child failure with a close-time write, unexpected source mutation detection, protected report destination rejection and symlink rejection. The existing five PyMuPDF/SWIG warnings remain. Test ledgers are synthetic temporary fixtures; no genuine usage database was opened, initialized, imported or reset.

For future verification and deployment preparation: keep preservation sources sealed from Library/Zvec; work on distinct copies; let all processes close before hashing; never copy runtime index files back into the preservation source; publish a new package identity only after its final byte-only allowlist is recorded. A runtime volume is a working copy, not the checksum-preserved archive. Corpus uploads must continue to preserve its existing usage ledger and historical generations. This workflow is verified locally; no production change or live acceptance follows from it.

The recorded 182 attempts on October 26 and $0.634595 October reservations remain unresolved accounting evidence under the existing reconciliation plan. No allowance was reset to perform this follow-up.
