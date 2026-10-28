# Recovering answer reservation accounting

Answer limits remain aggregate across providers: $5 per UTC month and 100
attempts per UTC day by default. Switching models or rebuilding a corpus must
not reset them. Failed calls keep their conservative reservation. Historical
daily rows are retained; only today's row limits today's attempts.

`RESEARCH_USAGE_ROOT` optionally selects a persistent directory containing
`answer-usage.sqlite`, independently of disposable research-index copies.
Without it the existing `<RESEARCH_DATA_ROOT>/.research-usage` location remains.
Never point paid validation at an empty temporary ledger or package the usage
directory with public research files. The directory is ignored by Git.

## Reconciliation

Keep paid dispatch disabled. Follow the provenance and overlap procedure in
`reports/recovery-2026-10-27/usage-reconciliation-plan.md`. The surviving local
record describes 182 attempts on 2026-10-26 and 634595 micro-USD reserved in
October, including its earlier 39154 baseline. These are reconstructed
conservative reservations, not recovered transactions or actual charges.

Create an adjustment JSON containing `receipt` (a unique stable ID), `kind`
(`reconstructed_conservative_reservations` or `verified_validation_delta`),
`source_sha256`, `source_description` (including any overlap decision), `days`
(UTC dates mapped to attempt additions), and `months` (UTC months mapped to
micro-USD additions). Hash the exact evidence file supplied to the command.

Run `python -m backend.usage_reconciliation --ledger /absolute/path/answer-usage.sqlite
--adjustment /absolute/path/adjustment.json --evidence /absolute/path/evidence.md
--audit-dir /absolute/path/audit` first. This inspects without creating a ledger.
Add `--apply` only after inspecting the genuine ledger and the proposed additions.
A verified missing ledger also requires `--initialize-missing`.

The helper checks the evidence hash, uses SQLite's backup API (including committed
WAL rows), refuses duplicate receipts, and adds counters and the receipt in one
transaction. It checks for changes between capture and import and preserves
before/after snapshots and a JSON receipt without overwriting existing audit
files. If a failure occurs after commit but before the after-backup/report is
saved, inspect `usage_imports` and capture another backup; do not apply a new
receipt to retry the same import. Dispatch must remain disabled during capture
and reconciliation.

## Local provider validation

With production answers disabled, copy the reconciled production backup to a
dedicated validation directory and use that explicit usage root. Record the
fork baseline and its hash. All live attempts, including failures, use the normal
limiter against this ledger. After testing, freeze validation and import only
the additive delta since that baseline into production with a unique receipt
and hashed evidence. Preserve any independent production usage. Never replace
production with the validation copy, import the original baseline twice, or
activate public answers while validation reservations remain unaccounted for.
