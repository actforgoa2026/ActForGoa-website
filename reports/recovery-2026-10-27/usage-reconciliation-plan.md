# Usage accounting reconciliation before enabling answers

This is a recovery plan, not a restored ledger. No production or local evaluation usage database has been created, reset, imported or modified during corpus recovery. Backend tests use separate synthetic temporary databases; those are not accounting evidence. The recovered corpus and its package must contain no `.research-usage` directory. Answers must remain disabled until accounting and the independent answer-quality gates are resolved.

## Evidence preserved

The last recorded local evaluation ledger contained:

- UTC day `2026-10-26`: **182 attempted answers**.
- UTC month `2026-10`: **634,595 micro-USD ($0.634595)** of conservative reservations.
- That monthly total already includes the earlier **39,154 micro-USD ($0.039154)** baseline. Do not add that baseline to the local total again.

The source is the committed release handoff at `114331928b7b46232973288fa277f96cd7821d13`, retained by integration `5fa9953aa851e837f2e1a88cd04d2bd3351321cd`, in `reports/openrouter-chat-validation.md`. These are reservation totals, not provider charges. They are a historical accounting floor and do not prove that later usage was zero.

The actual local database is missing from the searched locations. Temporary pytest databases are synthetic fixtures and must never be imported. Production's persistent ledger was not inspected during this recovery; its state and any overlap with local evaluation remain unknown. Provider account balance, key allowance and provider charges are separate quantities, and cannot replace these reservations.

## Concrete procedure for the release owner

1. Keep paid-answer dispatch disabled. Locate any genuine local ledger backup first. Preserve its bytes and hash it before examining it; do not overwrite production with it.
2. Back up the production database using SQLite's backup API while paid dispatch is disabled. Record service, volume, absolute path, schema, hash and the date of capture without exporting credentials or private user data. Never replace that database as part of a corpus upload.
3. Inspect the separate daily attempt and monthly reservation rows. Check whether any previous import receipt or release log establishes that the local evaluation total was already imported, wholly or partly. Compare against the recorded floor above and any later verified records. Do not assume that matching totals prove common origin.
4. Prefer transaction-level reconciliation if a genuine local backup is recovered. If only the recorded aggregate survives, label the adjustment explicitly as a reconstructed conservative reservation, not recovered transactions or actual billed usage. Retain the cited evidence and the operator's calculation alongside the receipt.
5. With no reliable evidence of overlap, conservatively reserve the full local 634,595 micro-USD in addition to verified production October reservations. Do not subtract the 39,154 baseline from that local total; its provenance must be proven before netting anything against production. This may over-reserve but must not undercount. Verified later local usage also needs accounting before activation.
6. Record the 182 historical attempts against **2026-10-26**, preserving existing production attempts and any verified later attempts. Do not carry them into October 27's daily allowance as though they occurred then. Keep an immutable audit record because the current limiter may prune earlier daily rows on subsequent reservations.
7. Apply any adjustment in one SQLite transaction with an explicit, unique import receipt such as `local-evaluation-recovery-20261026-v1`. Record source evidence hashes and applied deltas; refuse a duplicate receipt. Update existing counters additively only after resolving any proven overlap. Do not replace or zero counters. Back up the resulting database and verify the receipt and totals before changing answer availability.
8. The $5 monthly cap stays unchanged. Even before production or later usage is counted, the known local reservation leaves at most **$4.365405** for October. If reconciliation consumes the allowance, keep paid answers unavailable; do not raise/reset the budget to complete tests.

A future month has a new allowance under the existing policy, but does not erase missing October history. No claim of restored accounting, live acceptance or deployment follows from reconstructing the document corpus.
