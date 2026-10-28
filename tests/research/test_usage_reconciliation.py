"""Synthetic accounting fixtures only. Never open a genuine usage ledger."""
from datetime import datetime, timezone
import sqlite3
import pytest
from backend.hosting import PublicLimits
from backend.usage_reconciliation import backup, digest, inspect_ledger, reconcile


@pytest.fixture
def fixture(tmp_path):
    evidence = tmp_path / 'source.md'
    evidence.write_text('Synthetic fixture, not recovered usage evidence.')
    change = {'receipt': 'test-recovery-v1', 'kind': 'reconstructed_conservative_reservations',
              'source_sha256': digest(evidence), 'source_description': 'Synthetic test only; no overlap.',
              'days': {'2026-10-26': 182}, 'months': {'2026-10': 634595}}
    return tmp_path / 'ledger.sqlite', evidence, change, tmp_path / 'audit'


def test_inspection_does_not_create_ledger_and_initialization_is_explicit(fixture):
    path, evidence, change, audit = fixture
    assert not reconcile(path, change, evidence, audit)['applied']
    assert not path.exists() and not audit.exists()
    with pytest.raises(ValueError, match='explicit initialization'):
        reconcile(path, change, evidence, audit, apply=True)
    report = reconcile(path, change, evidence, audit, apply=True, initialize_missing=True)
    assert report['after']['days'] == change['days']
    assert report['after']['months'] == change['months']
    assert report['after_sha256'] == digest(audit / 'test-recovery-v1.after.sqlite')


def test_additive_import_preserves_existing_periods_and_cannot_repeat(fixture):
    path, evidence, change, audit = fixture
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
        db.executemany('INSERT INTO usage VALUES (?,?)', [('2026-10-26', 4), ('2026-10-27', 3)])
        db.execute('CREATE TABLE spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL)')
        db.executemany('INSERT INTO spend VALUES (?,?)', [('2026-09', 999), ('2026-10', 39154)])
    report = reconcile(path, change, evidence, audit, apply=True)
    assert report['after']['days'] == {'2026-10-26': 186, '2026-10-27': 3}
    assert report['after']['months'] == {'2026-09': 999, '2026-10': 673749}
    assert inspect_ledger(audit / 'test-recovery-v1.before.sqlite') == report['before']
    change['months']['2026-10'] = 1
    with pytest.raises(ValueError, match='already imported'):
        reconcile(path, change, evidence, audit / 'retry', apply=True)
    assert inspect_ledger(path) == report['after']


def test_failure_rolls_back_receipt_and_all_deltas(fixture):
    path, evidence, change, audit = fixture
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL)')
        db.execute("CREATE TRIGGER fail_import BEFORE INSERT ON spend BEGIN SELECT RAISE(ABORT, 'test failure'); END")
    before = inspect_ledger(path)
    with pytest.raises(sqlite3.IntegrityError, match='test failure'):
        reconcile(path, change, evidence, audit, apply=True)
    assert inspect_ledger(path) == before


def test_backup_includes_committed_wal_rows(fixture):
    path, _, _, audit = fixture
    with sqlite3.connect(path) as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
        db.execute("INSERT INTO usage VALUES ('2026-10-26',7)")
        db.commit()
        backup(path, path.with_name('backup.sqlite'))
    assert inspect_ledger(path.with_name('backup.sqlite'))['days'] == {'2026-10-26': 7}


@pytest.mark.parametrize('invalid', [-1, True, 1.5, '100'])
def test_invalid_deltas_never_mutate_ledger(fixture, invalid):
    path, evidence, change, audit = fixture
    change['months']['2026-10'] = invalid
    with pytest.raises(ValueError):
        reconcile(path, change, evidence, audit, apply=True, initialize_missing=True)
    assert not path.exists()


def test_source_hash_mismatch_refuses_import(fixture):
    path, evidence, change, audit = fixture
    evidence.write_text('Changed evidence')
    with pytest.raises(ValueError, match='SHA-256'):
        reconcile(path, change, evidence, audit, apply=True, initialize_missing=True)
    assert not path.exists()


def test_historical_attempts_survive_and_recovered_spend_counts_toward_same_cap(fixture, monkeypatch):
    import backend.hosting as hosting
    class Today(datetime):
        @classmethod
        def now(cls, tz):
            return cls(2026, 10, 27, tzinfo=timezone.utc)
    monkeypatch.setattr(hosting, 'datetime', Today)
    _, evidence, change, audit = fixture
    root = audit.parent / 'usage'
    path = root / 'answer-usage.sqlite'
    reconcile(path, change, evidence, audit, apply=True, initialize_missing=True)
    limiter = PublicLimits(root, chats_per_day=1)
    assert not limiter.reserve_answer(4_365_406)
    assert limiter.reserve_answer(4_365_405)
    assert not PublicLimits(root).reserve_answer(1)
    assert not limiter.reserve_answer(0)
    assert inspect_ledger(path)['days'] == {'2026-10-26': 182, '2026-10-27': 1}
    assert inspect_ledger(path)['months'] == {'2026-10': 5_000_000}
