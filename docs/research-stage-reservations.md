# Stage reservation receipts

`PublicLimits.reserve_stage` adds an atomic receipt for one provider phase.
`PublicLimits.preflight_pair` provides a read-only advisory check for two phases.
Neither function calls a provider, captures question/evidence text, starts a
pipeline, imports accounting, or changes the configured limits. Defaults remain
100 attempts per UTC day and 5,000,000 microUSD per month.

The existing `reserve_answer` implementation and boolean interface are unchanged.
Legacy and stage calls use the same `usage` and `spend` counters. Legacy calls do
not acquire phase identities or create stage receipts.

## Admission

```python
receipt = limits.reserve_stage(cost_microusd, expected_day, parent_id, phase)
if receipt['reserved']:
    # Persist this receipt in the phase capture, recheck cancellation/deadline/day,
    # and only then allow the separately owned pipeline to attempt transport.
    ...
```

- `cost_microusd`: a nonnegative Python integer within SQLite's signed integer
  range. Boolean, float and string coercion is rejected.
- `expected_day`: a valid canonical `YYYY-MM-DD` date supplied by the parent
  request. Do not refresh it to authorize a second phase after UTC rollover.
- `parent_id`: a newly generated random UUID hex string, exactly 32 lowercase
  hexadecimal characters. Do not derive it from a question, person or client ID.
- `phase`: exactly `draft` or `reconstruction`.

The JSON-ready result has these fixed fields:

```json
{
  "version": "afg-stage-reservation-v1",
  "reserved": true,
  "reason": "reserved",
  "parent_id": "11111111111111111111111111111111",
  "phase": "draft",
  "expected_day": "2026-10-27",
  "day": "2026-10-27",
  "month": "2026-10",
  "cost_microusd": 9424,
  "before": {"day_attempts": 0, "month_reserved_microusd": 0},
  "after": {"day_attempts": 1, "month_reserved_microusd": 9424},
  "receipt_id": "22222222222222222222222222222222"
}
```

The IDs above are synthetic examples. Real receipt IDs are generated randomly.
`before` and `after` describe the exact selected day/month counters within the
transaction, not a whole-ledger snapshot and not provider transmission or usage.

The UTC clock is read after `BEGIN IMMEDIATE` succeeds. Admission then checks
expected day, duplicate parent/phase, daily cap and monthly cap, in that order.
Successful aggregate increments and the complete receipt are committed in the
same short transaction. `stage_reservations` has a persistent unique parent/phase
key and a unique receipt ID. No network work or await occurs inside a transaction.

Refusals return `reserved: false`, `receipt_id: null`, unchanged `before`/`after`
and one reason: `day_mismatch`, `duplicate`, `daily_limit`, or `monthly_limit`.
They add no counters or receipt rows. A duplicate never returns the old success
as permission to send again, even if its requested cost or day changes. Always
inspect `reserved`; a refusal dictionary itself is truthy in Python.

Invalid input, schema or counter values raise `ValueError`. Lock/storage failures
raise `sqlite3.Error`. The SQLite lock wait is bounded to 250 ms and is not retried.
No exception authorizes dispatch. A commit acknowledgement failure may leave a
committed receipt: capture the uncertainty, send nothing, and let the coordinator
reconcile it. Never automatically retry, reuse a receipt to send later, or refund
a committed charge, including cancellation before any provider request.

## Advisory pair preflight

```python
advisory = limits.preflight_pair([draft_max_microusd, reconstruction_max_microusd], expected_day)
```

The first argument is a list or tuple of exactly two nonnegative integers, with
their sum within SQLite's signed integer range. It accepts no boolean coercion.
The result is:

```json
{
  "version": "afg-stage-preflight-v1",
  "allowed": true,
  "reason": "allowed",
  "expected_day": "2026-10-27",
  "day": "2026-10-27",
  "month": "2026-10",
  "observed": {"day_attempts": 0, "month_reserved_microusd": 0},
  "required_attempts": 2,
  "required_cost_microusd": 20048
}
```

The alternate reasons are `day_mismatch`, `daily_limit` and `monthly_limit`.
There is no receipt or dispatch authority. Multiple request pairs may pass this
check before one consumes the remaining capacity. Each subsequent stage still
needs its own successful `reserve_stage`; losing capacity for reconstruction
does not refund the draft charge or authorize returning the draft.

For an existing ledger, SQLite `mode=ro` and a read transaction give an exact
observed snapshot. The schema read acquires that snapshot before UTC is checked.
Committed WAL state is included; immutable SQLite mode is not used. No counters,
receipt rows or schema are written. Ordinary SQLite read coordination may occur.

An absent new ledger is explicitly treated as zero without creating any path;
its clock is read after the absence probe because no ledger transaction exists.
A completely empty new database is also zero, including the empty file left by
an initial refused reservation. The helper cannot determine whether an external
actor deleted or emptied an earlier ledger; preservation and recovery remain
coordinator responsibilities. An existing ledger disappearing after the probe,
a dangling symlink, malformed or partially missing schema, invalid counters or
an unavailable lock fail closed. Missing one aggregate table is never interpreted
as zero for that counter.

## Verification and ownership

```sh
python -m pytest tests/research/test_stage_reservations.py \
  tests/research/test_hosting.py tests/research/test_usage_reconciliation.py -q
```

Tests use synthetic temporary ledgers only. They cover exact receipts, atomic
rollback, uncertain commit acknowledgement, duplicates across processes and UTC
days, concurrent daily/monthly admission, deterministic competing pair barriers,
UTC change while waiting for the write lock, read-only/WAL preflight, corruption,
lock refusal and legacy compatibility. No real ledger or provider is exercised.

The pipeline owner remains responsible for capture persistence, request/body cost
bounds, pre-dispatch day/deadline/disconnect checks, known versus uncertain send
counts, final response/cache rules and no retry. These receipts establish a
committed reservation, not that a request was sent or an answer was correct.
