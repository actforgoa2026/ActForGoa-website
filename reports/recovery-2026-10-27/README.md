# Research corpus recovery, 27 October 2026

The refreshed corpus has been reconstructed and packaged for review. Its SQLite file is byte-identical to the recorded missing refreshed SQLite. The complete old package was not found: the rebuilt Zvec index and package have a new generation and new hashes. Nothing was deployed or enabled.

The isolated branch is `codex/research-recovery-20261027`, based exactly on PR #17 head `5fa9953aa851e837f2e1a88cd04d2bd3351321cd`. This change adds recovery evidence and a read-only verifier only. No runtime, retrieval-ranking or visual code changed. The coordinator owns integration and release.

## Recovered identity

| Item | Value |
| --- | --- |
| New generation | `20261027T065155-law-5bc5619b` |
| Recorded missing generation | `20261026T131818-law-23a2e6a6` |
| Documents / pages / passages | 1,174 / 21,534 / 79,564 |
| Recovered and historical SQLite SHA-256 | `c6d80208581f3776d2cfaa2cfe3ff08e026bd055be1c2a574461934fa52d870f` |
| Verified legal register SHA-256 | `c749c28dad082b084291fe425bfadfba37c22777910e5035bcb82a78e3eb2dcd` |
| Embedding model SHA-256 | `afdb6f1a0e45b715d0bb9b11772f032c399babd23bfc31fed1c170afc848bdb1` |
| Current package `files.json` SHA-256 | `e5095ce040de7df04e37f6ab904d05592245e96d98c12ef3c1807000793b46dd` |
| Historical package `files.json` SHA-256, not recovered | `9e03caf9af14bb5775fbf9154982dd562d80dc698ee0a13a9a0839ffcc9828f4` |
| Durable payload manifest SHA-256 | `0e7499391b4ec61d13d09bc59baf2b792cfe04379d5cdee30950a536ca1e65b0` |

SQLite byte identity preserves all text, metadata, document IDs, passage IDs, offsets and FTS contents recorded in that database. It does not establish identity of the historical vector files or complete package. New generation identity is intentional; do not relabel it as the historical generation. Existing URLs pinned to the missing October 26 generation will still need explicit migration or a separately reviewed compatibility decision. No silent alias has been added.

## Exact locations

The durable recovery root is:

`/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27`

- `refreshed-data/` contains the new corpus plus all three retained baseline generations, originals and recovery extraction caches.
- `legal-package/data/` contains the current generation and its 1,174 indexed originals. It has 1,191 files and 2,096,777,301 logical bytes.
- `legal-package/service/` contains the PR #17 runtime code and bundled embedding model.
- `legal-package/files.json` is the relative-path checksum allowlist; `manifest.json` retains the original worktree staging paths as provenance. Use the durable paths above to open this copy.
- `source-inputs/` preserves 102 public source-input files: the register, 26 original/metadata/text sets, available page extracts and reviewed OCR. These are a separate recovery input set, not part of the service upload.
- `provenance/` contains preflight input hashes, the baseline pointer, the recovery-only evidence fixture, source-copy hashes and a narrowly scoped Git archive of the extraction/index/runtime code at `5fa9953`.
- `payload-files.json` hashes 2,607 files across those four payload directories, totaling 5,612,058,404 logical bytes. APFS clones were used; logical size is not additional physical disk consumption.
- `reports/` and the final snapshot manifest are added after the recovery evidence commit. The final snapshot manifest excludes itself.

Working copy:

`/Users/zakkrevitt/.codex/worktrees/research-recovery-20261027/ActForGoa/.research-release/recovery`

Keep the durable directory when cleaning managed worktrees. Do not treat `legal-package/data/` as a replacement for an existing production volume: it intentionally omits old generations and all usage accounting. Any future upload must preserve the volume's existing index generations, originals and usage database.

## Inputs and preservation

The surviving baseline is `/Users/zakkrevitt/.codex/worktrees/ecology-research-chat/ActForGoa`, with active generation `20261022T155701-21661179`. It has 1,156 documents, 21,220 pages and 78,432 passages. The primary checkout `/Users/zakkrevitt/code/ActForGoa` supplied the 26 hash-verified legal source sets. Both were used as read-only inputs.

The previous refreshed-data and legal-package directories were absent from the bounded search of managed worktrees, code, Documents/Codex, Downloads, Desktop and accessible temporary directories. Some OS-protected trash/temp paths were inaccessible and were not bypassed. No genuine local usage ledger was found; pytest fixtures were excluded from recovery evidence.

All 85 preflight input hashes still matched after reconstruction. All files in the three retained baseline generations were copied byte-for-byte and checked:

| Generation | Documents | Pages | Passages | SQLite SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `20261022T153326-3e2e65fe` | 1,153 | 20,473 | 80,344 | `a40cef0a565fd1048143a02d813f447eafb5359d04917d708148e767f523927a` |
| `20261022T155317-11b07ef4` | 1,156 | 21,110 | 82,555 | `5b4c6958bc3b8d511ad70bb3c47502e5c360d015fc35b73fed1dd857381d6a56` |
| `20261022T155701-21661179` | 1,156 | 21,220 | 78,432 | `74b6798b056936cc4a972024a05efc6c8fc582537bbee07552c731bc01b8d49e` |

The old V16 document ID `493ffb4c35a00be1f1f28e9b-91ac6cb7fd84` remains readable in its old generation. The reviewed OCR version is `493ffb4c35a00be1f1f28e9b-c9efabb977ca` in the recovered generation. Source IDs were not rewritten. V22 is still an original map with zero searchable passages; recovery does not turn it into reliable extracted evidence.

## Verification and remaining failures

- All four SQLite generations passed `integrity_check`; all their chunk offsets match exact saved page slices and all FTS rows match their chunks.
- All 1,174 distinct originals match recorded SHA-256 values. The current Zvec collection opens read-only and reports 79,564 vectors. Every vector ID, document field, dimension, finite value and unit norm was checked. All 78,432 inherited vectors match the baseline exactly; all 1,132 appended vectors match a replay of their original 24-passage ingestion batches exactly.
- All 26 reviewed source mappings reconcile. All eight distinct passage IDs referenced by the nine evidence cases exist with exact page slices.
- The staged package's 1,191 data files match its checksum allowlist, with no unlisted files. No symlinks, environment files or usage databases are included.
- The durable payload was hashed and 2,500 recovered/package files were compared with their working copies; all 102 source-input copies were verified. The durable package reopened and returned a result through both keyword and semantic search. Full saved text and original PDF access were exercised for the 18-page RTI manual and 13-page institutional SOP, including their last pages. These are library-level offline checks, not browser or live HTTP acceptance.
- Backend tests: **62 passed**, with five existing PyMuPDF/SWIG deprecation warnings. Provider tests use mock transports and synthetic temporary accounting databases. No genuine ledger was created or modified.
- On the staged package: **16/16 broad retrieval checks pass; 4/9 reviewed-evidence cases pass**. All returned citation slices match saved pages. The five RTI fee phrasings still fail to retain the reviewed fee passage in the actual model prompt. TCP, farming, institutional dogs and Parra retain their reviewed evidence. This reproduces the known failing baseline, not a release gate pass.
- `retrieval-evidence-cases.json` changes only the generation field from the historical fixture after verifying every reviewed locator. Questions, passage IDs and pass conditions are unchanged. The historical tracked fixture remains untouched.

The first additional embedding comparison used single-passage batches and failed byte equality: cosine similarities for the eight reviewed passages were 0.99836–0.99889. Replaying the original ingestion batches produced exact equality. The verifier therefore compares inherited vectors to their preserved originals and replays appended vectors with their original batch composition. It does not weaken the exact comparison with a looser numerical threshold.

No network ingestion, paid provider calls, production-volume changes, budget reset/import, chat activation, merge or deployment occurred. No UI was changed or visually accepted, and Device Hub was not used. Existing answer-entailment failures, provider-credit availability and live acceptance remain separate work.

## Reproduction

Use the research Python environment at `/Users/zakkrevitt/.codex/worktrees/ecology-research-chat/ActForGoa/.venv/bin/python`. Recorded dependencies: Zvec 0.8.0, ONNX Runtime 1.31.0, Tokenizers 0.23.3, PyMuPDF 1.28.2, Beautiful Soup 4.15.0, lxml 6.1.3. This environment and the archived code performed the recovery; no dependency upgrades occurred.

From the recovery branch, use explicit paths:

```sh
python scripts/refresh_verified_legal_sources.py \
  --base-root /Users/zakkrevitt/.codex/worktrees/ecology-research-chat/ActForGoa \
  --source-root /Users/zakkrevitt/code/ActForGoa \
  --output-root /path/to/a-new-empty-output

python reports/recovery-2026-10-27/verify_recovery.py \
  --data-root .research-release/recovery/refreshed-data \
  --input-state reports/recovery-2026-10-27/input-state.json \
  --output /path/to/new-integrity-report.json \
  --cases-output /path/to/new-generation-cases.json

python scripts/evaluate_retrieval_evidence.py \
  --data-root .research-release/recovery/legal-package/data \
  --cases reports/recovery-2026-10-27/retrieval-evidence-cases.json \
  --output /path/to/new-retrieval-report.json
```

The refresh script copies the active baseline only. To reproduce this preservation bundle, additionally copy the two earlier generation directories without changing their contents, as done here. The verifier also compares those three preserved generations against the input baseline. The retrieval command intentionally exits 1 for the five known RTI failures. Do not retry it as a paid model test.

## Accounting handoff

Read [usage-reconciliation-plan.md](usage-reconciliation-plan.md) before any later activation. Preserve the recorded **182 attempts on 2026-10-26 and $0.634595 in October reservations**, including the earlier $0.039154 baseline. Production usage is separate and was not inspected. The recorded values are not provider charges or proof of zero later usage. Reconcile once, conservatively and with an audit receipt; do not fabricate recovered transactions or replace production accounting.
