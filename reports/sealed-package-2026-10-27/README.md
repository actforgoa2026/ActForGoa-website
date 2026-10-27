# Sealed research package, 27 October 2026

The recovered research data now has a separately identified package with an accurate allowlist. This completes the bounded packaging repair. It does not authorize upload, deployment, replacement of a production volume, or generated answers.

Package: `/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-sealed-package-v1`

Package identity: `actforgoa-research-20261027-sealed-v1`. Current generation remains `20261027T065155-law-5bc5619b`; no corpus was regenerated. All three preserved earlier generations are included. The package contains 1,236 data files, 18 service files, four metadata/allowlist files, and `seal.json`: 1,259 files total. The seal covers the other 1,258 files and the exact directory list, including empty index directories. Those covered files total 3,442,070,201 logical bytes.

| Artifact | SHA-256 |
| --- | --- |
| `seal.json` | `26227d014c3c948f7d10f0d4d13dab4820d1b510d14772e95cb44f7361ab0249` |
| `manifest.json` | `ea7135bc57b912f6b5ef23135d1d60dd7226aab4a3cb8405e29e150862581006` |
| `files.json` | `6b2ed3ac358c8787989145fbd6c6c117de96feb00d8a00d842d3ce4aefb528a4` |
| `service-files.json` | `f0152d6409f86742e6e50a2edf2f9aa4d7dba533db132628e37789d83c616218` |
| `provenance.json` | `15ff39bd5652d6c243016c34eb4c8b16fd047cf664e974a346c75bc94fbd7cda` |

## Provenance and preservation

The byte-copy source was `/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-restoration-candidate`, anchored to its accepted outer `snapshot-files.json`, SHA-256 `2b86bf87e963fa1c2c5c6c3be894ba2c141777f5c330b0147e34c2daa2dcd095`. All 2,623 listed source files were checked after native child processes exited.

Current data came from `legal-package/data`; earlier generations came from `refreshed-data/.research-index/generations`. Existing `scripts/package_research.py --service-only` produced the service at runtime commit `c2bef796e2765d55ef767ecf7f9107661466d446`. The new data allowlist contains paths relative to `data`; the service allowlist is relative to `service`. Every copied data entry maps to the accepted outer source inventory. Credentials and genuine usage data are excluded.

The historical `legal-package/files.json` remains unchanged at SHA-256 `e5095ce040de7df04e37f6ab904d05592245e96d98c12ef3c1807000793b46dd`. Its one outdated vector hash is `8696f35db49d3ed73c0ab7c2650c5e22ca662945e1dd4853c2e314eb924af0ef`. The accepted source and new package contain the restored file with SHA-256 `4c8c86b4cf9768ef21d237201218e6b05369d2f91b92729ce7553a6c7c973185`. This package supplies a new honest allowlist without rewriting either historical manifest or the original altered snapshot. See the earlier [forensic report](../rti-offline-2026-10-27/README.md).

Available space was inspected before copying: 170,021,015,552 bytes. APFS clonefile copies preserved the source material; only owned temporary validation copies were removed. Neither preservation source nor sealed package was opened through Library, Zvec or SQLite. Parent processes used ordinary byte reads, hashes, JSON and file copies.

Zvec 0.8.0 changes HNSW metadata when a nominally read-only index closes. Native runtime checks therefore ran in subprocesses against disposable data and service copies. All native children completed before the new allowlists and seal were written. Further checks after sealing also used disposable copies, and the entire sealed package plus restoration source were verified again after child exit. The expected four scratch index changes stayed inside temporary copies.

## Results

| Generation | Documents | Pages | Exact passage slices and vector IDs checked |
| --- | ---: | ---: | ---: |
| `20261022T153326-3e2e65fe` | 1,153 | 20,473 | 80,344 |
| `20261022T155317-11b07ef4` | 1,156 | 21,110 | 82,555 |
| `20261022T155701-21661179` | 1,156 | 21,220 | 78,432 |
| `20261027T065155-law-5bc5619b` | 1,174 | 21,534 | 79,564 |

- All four SQLite integrity checks passed. All 320,895 passage slices match saved page offsets; all corresponding Zvec IDs and document associations match SQLite.
- All 1,174 distinct original documents resolve and match their recorded checksums.
- Hybrid khazan queries return both keyword and semantic matches for each generation, with exact citation slices.
- Current RTI V01, current SOP V16, and the preserved earlier SOP V16 support full text through the last page and original-PDF final-page rendering. These are backend checks; no browser or live-provider acceptance is claimed.
- The runtime child verified it imported the packaged backend. It did not initialize the application or usage ledger. Provider calls: zero.
- Backend suite: 70 passed, five existing SWIG/PyMuPDF warnings. The four added cases protect sealed/snapshot sources and report destinations before native index construction.
- Six reproduction-entry-point checks reject protected data, service and output paths reached through symlinks, before native imports.
- Exact evidence gate before and after sealing: **4/9**; broad smoke checks: **16/16**. Exit code 1 is the recorded failed acceptance result. The five RTI failures remain; no ranking, prompt, case or pass criterion changed.
- Final byte checks cover all 1,258 sealed entries, both new allowlists, exact file/directory coverage, all copied-source mappings, all 2,623 accepted restoration entries, and unchanged original/restoration historical manifests. Both native-child preservation reports show unchanged source bytes after exit.

`sealed-package.json` records package identities. `packaged-runtime.json` and `packaged-runtime-preservation.json` record the final copy-based runtime checks. `post-seal-gate.json` and its preservation report retain the failed answer-evidence gate. `final-byte-verification.json` records the final byte-only source/package audit. Earlier pre-seal results are retained separately.

## Reproduce without opening preserved indexes

Use the project research Python environment with the pinned backend dependencies. Run from this checkout; select a fresh output location outside preservation roots. These commands create disposable working copies and may return a failed evidence result without a preservation failure.

```sh
python scripts/evaluate_research_copy.py \
  --data-root '/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-sealed-package-v1/data' \
  --cases reports/recovery-2026-10-27/retrieval-evidence-cases.json \
  --output /tmp/actforgoa-sealed-rerun/gate.json

python reports/sealed-package-2026-10-27/check_package_copy.py \
  --package '/Users/zakkrevitt/Documents/ActForGoa Recovery/2026-10-27-sealed-package-v1' \
  --seal-sha256 26227d014c3c948f7d10f0d4d13dab4820d1b510d14772e95cb44f7361ab0249 \
  --output-dir /tmp/actforgoa-sealed-rerun/runtime
```

The package checker uses macOS APFS copies and launches `runtime_check.py` as its child. Do not run native checks directly on preserved directories. The evidence evaluator now rejects source/report paths beneath either `snapshot-files.json` or `seal.json`; the copy wrapper rejects report destinations there too. The runtime child resolves paths before checking data, service and output preservation markers. These are accidental-use guards; copying or removing markers is not a safe validation method.

Keep the sealed root immutable. Do not add reports, bytecode, credentials or usage files to it, and do not rerun the packager against it. Future running services require separate writable copies. The sealed package must never replace a production ledger or volume wholesale.

## Release boundary

This change contains evaluator guards, tests and compact verification evidence. Runtime/provider code, retrieval selection, UI, dependency pins, genuine usage accounting, deployment and main are unchanged. Raw archives and the sealed payload stay outside Git.

The release holds remain: failed exact evidence retrieval, incomplete live answer acceptance and provider-credit confirmation, and unreconciled local/production usage accounting. The previous reranker experiment stays rejected. No paid calls, ledger initialization/reset, corpus uploads, deployment or activation were performed. Coordinator review and later acceptance are required before any release; packaging integrity does not establish answer entailment or legal currency.
