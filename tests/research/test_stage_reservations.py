"""Only synthetic temporary ledgers. Never open an application usage directory."""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing
from pathlib import Path
import sqlite3
import threading
import time

import pytest

import backend.hosting as hosting
from backend.hosting import PublicLimits

DAY = '2026-10-27'
PARENT = '1' * 32
CONNECT = sqlite3.connect


@pytest.fixture
def clock(monkeypatch):
    class Clock(datetime):
        day = DAY
        @classmethod
        def now(cls, tz):
            assert tz is timezone.utc
            return datetime.fromisoformat(cls.day + 'T12:00:00+00:00')
    monkeypatch.setattr(hosting, 'datetime', Clock)
    return Clock


def ledger(root):
    path = Path(root) / 'answer-usage.sqlite'
    if not path.exists():
        return {'days': {}, 'months': {}, 'receipts': []}
    with CONNECT(path) as db:
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        return {
            'days': dict(db.execute('SELECT day,attempts FROM usage')) if 'usage' in tables else {},
            'months': dict(db.execute('SELECT month,reserved_microusd FROM spend')) if 'spend' in tables else {},
            'receipts': [json.loads(r[0]) for r in db.execute('SELECT receipt_json FROM stage_reservations ORDER BY receipt_id')]
                        if 'stage_reservations' in tables else [],
        }


def test_success_receipt_commits_with_exact_counters(tmp_path, clock):
    limits = PublicLimits(tmp_path)
    result = limits.reserve_stage(9424, DAY, PARENT, 'draft')
    assert result == {
        'version': 'afg-stage-reservation-v1', 'reserved': True, 'reason': 'reserved',
        'parent_id': PARENT, 'phase': 'draft', 'expected_day': DAY, 'day': DAY, 'month': '2026-10',
        'cost_microusd': 9424, 'before': {'day_attempts': 0, 'month_reserved_microusd': 0},
        'after': {'day_attempts': 1, 'month_reserved_microusd': 9424}, 'receipt_id': result['receipt_id'],
    }
    assert len(result['receipt_id']) == 32 and int(result['receipt_id'], 16) >= 0
    state = ledger(tmp_path)
    assert state == {'days': {DAY: 1}, 'months': {'2026-10': 9424}, 'receipts': [result]}
    result['before']['day_attempts'] = 999
    assert ledger(tmp_path)['receipts'][0]['before']['day_attempts'] == 0


def test_dated_release_allowance_expires_in_running_process(tmp_path,clock):
    limits=PublicLimits(tmp_path,release_allowance=True)
    clock.day='2026-10-28'
    assert limits.effective_limits(clock.day)==(150,15_000_000)
    assert limits.reserve_stage(5_000_001,clock.day,'a'*32,'draft')['reserved']
    clock.day='2026-10-29'
    assert limits.effective_limits(clock.day)==(100,15_000_000)
    # Seed only synthetic counters, including today's exhausted100attempts.
    with CONNECT(tmp_path/'answer-usage.sqlite') as db:
        db.execute('INSERT INTO usage VALUES (?,100)',(clock.day,))
    assert not limits.preflight_single(1,clock.day)['allowed']
    assert limits.reserve_stage(1,clock.day,'b'*32,'draft')['reason']=='daily_limit'
    clock.day='2026-11-01'
    assert limits.effective_limits(clock.day)==(100,5_000_000)
    assert limits.reserve_stage(5_000_001,clock.day,'c'*32,'draft')['reason']=='monthly_limit'
    assert limits.reserve_stage(5_000_000,clock.day,'d'*32,'draft')['reserved']
    assert limits.reserve_stage(1,clock.day,'e'*32,'draft')['reason']=='monthly_limit'
    assert ledger(tmp_path)['months']=={'2026-10':5_000_001,'2026-11':5_000_000}


def test_release_allowance_requires_explicit_opt_in(tmp_path,clock):
    clock.day='2026-10-28'
    limits=PublicLimits(tmp_path)
    assert limits.effective_limits(clock.day)==(100,5_000_000)
    assert limits.reserve_stage(5_000_001,clock.day,'a'*32,'draft')['reason']=='monthly_limit'


def test_duplicate_does_not_reauthorize_and_other_phase_is_independent(tmp_path, clock):
    limits = PublicLimits(tmp_path)
    first = limits.reserve_stage(10, DAY, PARENT, 'draft')
    duplicate = PublicLimits(tmp_path).reserve_stage(999, DAY, PARENT, 'draft')
    assert not duplicate['reserved'] and duplicate['reason'] == 'duplicate'
    assert duplicate['receipt_id'] is None and duplicate['before'] == duplicate['after'] == first['after']
    second = limits.reserve_stage(20, DAY, PARENT, 'reconstruction')
    assert second['reserved'] and second['receipt_id'] != first['receipt_id']
    assert second['before'] == first['after']
    assert second['after'] == {'day_attempts': 2, 'month_reserved_microusd': 30}


@pytest.mark.parametrize('kind', ['daily', 'monthly'])
def test_authoritative_refusal_does_not_change_rows(tmp_path, clock, kind):
    limits = PublicLimits(tmp_path, chats_per_day=1 if kind == 'daily' else 100, monthly_usd='0.000010')
    assert limits.reserve_stage(10, DAY, PARENT, 'draft')['reserved']
    before = ledger(tmp_path)
    result = limits.reserve_stage(1, DAY, PARENT, 'reconstruction')
    assert result['reason'] == kind + '_limit' and not result['reserved']
    assert result['receipt_id'] is None and result['before'] == result['after']
    assert ledger(tmp_path) == before


def test_rollover_and_duplicate_identity_survive_month_boundary(tmp_path, clock):
    clock.day = '2026-10-31'
    limits = PublicLimits(tmp_path)
    assert limits.reserve_stage(10, clock.day, PARENT, 'draft')['reserved']
    before = ledger(tmp_path)
    clock.day = '2026-11-01'
    result = limits.reserve_stage(20, '2026-10-31', PARENT, 'reconstruction')
    assert result['reason'] == 'day_mismatch' and result['day'] == clock.day and result['month'] == '2026-11'
    assert result['before'] == result['after'] == {'day_attempts': 0, 'month_reserved_microusd': 0}
    assert ledger(tmp_path) == before
    assert limits.reserve_stage(10, clock.day, PARENT, 'draft')['reason'] == 'duplicate'
    assert ledger(tmp_path) == before
    assert limits.reserve_stage(20, clock.day, PARENT, 'reconstruction')['reserved']
    assert ledger(tmp_path)['days'] == {'2026-10-31': 1, '2026-11-01': 1}
    assert ledger(tmp_path)['months'] == {'2026-10': 10, '2026-11': 20}


class ConnectionProxy:
    def __init__(self, connection, after_execute=None, commit=None):
        self.connection = connection
        self.after_execute = after_execute
        self.commit_hook = commit
    def __getattr__(self, name):
        return getattr(self.connection, name)
    def execute(self, sql, *args):
        result = self.connection.execute(sql, *args)
        if self.after_execute:
            self.after_execute(sql)
        return result
    def commit(self):
        if self.commit_hook:
            return self.commit_hook(self.connection)
        return self.connection.commit()


def test_utc_is_checked_after_write_lock_acquisition(tmp_path, clock, monkeypatch):
    locked = []
    def acquired(sql):
        if sql == 'BEGIN IMMEDIATE':
            locked.append(True)
            clock.day = '2026-10-28'
    monkeypatch.setattr(hosting.sqlite3, 'connect', lambda *a, **k: ConnectionProxy(CONNECT(*a, **k), acquired))
    result = PublicLimits(tmp_path).reserve_stage(10, DAY, PARENT, 'draft')
    assert locked and result['reason'] == 'day_mismatch' and result['day'] == '2026-10-28'
    assert ledger(tmp_path) == {'days': {}, 'months': {}, 'receipts': []}


def test_transaction_failure_rolls_back_receipt_and_counters(tmp_path, clock):
    limits = PublicLimits(tmp_path)
    limits.reserve_stage(1, DAY, PARENT, 'draft')
    with CONNECT(tmp_path / 'answer-usage.sqlite') as db:
        db.execute("CREATE TRIGGER fail_receipt BEFORE INSERT ON stage_reservations BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END")
    before = ledger(tmp_path)
    with pytest.raises(sqlite3.IntegrityError, match='synthetic failure'):
        limits.reserve_stage(2, DAY, PARENT, 'reconstruction')
    assert ledger(tmp_path) == before


@pytest.mark.parametrize('committed', [False, True])
def test_commit_ack_failure_never_returns_authorization_or_refunds(tmp_path, clock, monkeypatch, committed):
    def fail(connection):
        if committed:
            connection.commit()
        raise sqlite3.OperationalError('synthetic commit acknowledgement failure')
    with monkeypatch.context() as scoped:
        scoped.setattr(hosting.sqlite3, 'connect', lambda *a, **k: ConnectionProxy(CONNECT(*a, **k), commit=fail))
        with pytest.raises(sqlite3.OperationalError):
            PublicLimits(tmp_path).reserve_stage(12, DAY, PARENT, 'draft')
    state = ledger(tmp_path)
    if committed:
        assert state['days'] == {DAY: 1} and state['months'] == {'2026-10': 12}
        assert len(state['receipts']) == 1
        assert PublicLimits(tmp_path).reserve_stage(12, DAY, PARENT, 'draft')['reason'] == 'duplicate'
    else:
        assert state == {'days': {}, 'months': {}, 'receipts': []}


def test_failure_after_reservation_retains_charge(tmp_path, clock):
    with pytest.raises(RuntimeError):
        PublicLimits(tmp_path).reserve_stage(17, DAY, PARENT, 'draft')
        raise RuntimeError('synthetic cancellation before transport')
    assert ledger(tmp_path)['months'] == {'2026-10': 17}
    assert PublicLimits(tmp_path).reserve_stage(17, DAY, PARENT, 'draft')['reason'] == 'duplicate'


@pytest.mark.parametrize('cost', [-1, True, False, 0.5, '10', None, 1 << 63])
def test_invalid_cost_does_not_create_ledger(tmp_path, clock, cost):
    root = tmp_path / 'unused'
    with pytest.raises(ValueError):
        PublicLimits(root).reserve_stage(cost, DAY, PARENT, 'draft')
    assert not root.exists()


@pytest.mark.parametrize('field,value', [('expected_day', '2026-02-30'), ('expected_day', '2026-10-27Z'),
                                        ('expected_day', True), ('parent_id', 'a person or question'),
                                        ('parent_id', 'A' * 32), ('parent_id', PARENT + '\n'),
                                        ('phase', 'correction'), ('phase', True)])
def test_invalid_identity_or_date_does_not_create_ledger(tmp_path, clock, field, value):
    request = {'cost_microusd': 1, 'expected_day': DAY, 'parent_id': PARENT, 'phase': 'draft'}
    request[field] = value
    root = tmp_path / 'unused'
    with pytest.raises(ValueError):
        PublicLimits(root).reserve_stage(**request)
    assert not root.exists()


def test_zero_cost_still_consumes_one_attempt(tmp_path, clock):
    result = PublicLimits(tmp_path).reserve_stage(0, DAY, PARENT, 'draft')
    assert result['after'] == {'day_attempts': 1, 'month_reserved_microusd': 0}


def test_threaded_reservations_have_transaction_exact_snapshots(tmp_path, clock):
    def reserve(i):
        return PublicLimits(tmp_path, chats_per_day=7).reserve_stage(i + 1, DAY, f'{i:032x}', 'draft')
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(reserve, range(24)))
    accepted = sorted((r for r in results if r['reserved']), key=lambda r: r['before']['day_attempts'])
    assert len(accepted) == 7
    previous = {'day_attempts': 0, 'month_reserved_microusd': 0}
    for receipt in accepted:
        assert receipt['before'] == previous
        assert receipt['after'] == {'day_attempts': previous['day_attempts'] + 1,
                                    'month_reserved_microusd': previous['month_reserved_microusd'] + receipt['cost_microusd']}
        previous = receipt['after']
    assert all(r['reason'] == 'daily_limit' for r in results if not r['reserved'])
    assert len(ledger(tmp_path)['receipts']) == 7


def test_concurrent_duplicate_is_charged_once(tmp_path, clock):
    def reserve(_):
        return PublicLimits(tmp_path).reserve_stage(20, DAY, PARENT, 'draft')
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(reserve, range(16)))
    assert sum(r['reserved'] for r in results) == 1
    assert all(r['reason'] == 'duplicate' and r['receipt_id'] is None for r in results if not r['reserved'])
    assert ledger(tmp_path)['days'] == {DAY: 1}


def _process_reserve(arguments):
    root, parent = arguments
    class Fixed(datetime):
        @classmethod
        def now(cls, tz):
            return datetime.fromisoformat(DAY + 'T12:00:00+00:00')
    hosting.datetime = Fixed
    return PublicLimits(root, chats_per_day=3).reserve_stage(9, DAY, parent, 'draft')


def test_processes_share_budget_and_duplicate_protection(tmp_path):
    context = multiprocessing.get_context('spawn')
    with ProcessPoolExecutor(max_workers=4, mp_context=context) as pool:
        results = list(pool.map(_process_reserve, [(str(tmp_path), f'{i % 4:032x}') for i in range(12)]))
    assert sum(r['reserved'] for r in results) == 3
    assert ledger(tmp_path)['days'] == {DAY: 3}
    assert ledger(tmp_path)['months'] == {'2026-10': 27}
    assert len(ledger(tmp_path)['receipts']) == 3


def test_legacy_and_stage_reservations_share_limits(tmp_path, clock):
    limits = PublicLimits(tmp_path, chats_per_day=3, monthly_usd='0.000030')
    assert limits.reserve_answer(10) is True
    stage = limits.reserve_stage(10, DAY, PARENT, 'draft')
    assert stage['before'] == {'day_attempts': 1, 'month_reserved_microusd': 10}
    assert limits.reserve_answer(10) is True
    assert limits.reserve_answer(0) is False
    assert limits.reserve_stage(0, DAY, PARENT, 'reconstruction')['reason'] == 'daily_limit'
    assert ledger(tmp_path)['days'] == {DAY: 3} and ledger(tmp_path)['months'] == {'2026-10': 30}
    assert len(ledger(tmp_path)['receipts']) == 1


def test_legacy_boolean_cost_behavior_is_unchanged(tmp_path, clock):
    assert PublicLimits(tmp_path).reserve_answer(True) is True
    assert ledger(tmp_path)['months'] == {'2026-10': 1}


def test_default_caps_and_exact_pair_preflight(tmp_path, clock):
    limits = PublicLimits(tmp_path / 'absent')
    assert limits.chat_limit == 100 and limits.monthly_limit == 5_000_000
    assert limits.preflight_pair([9424, 10624], DAY) == {
        'version': 'afg-stage-preflight-v1', 'allowed': True, 'reason': 'allowed',
        'expected_day': DAY, 'day': DAY, 'month': '2026-10',
        'observed': {'day_attempts': 0, 'month_reserved_microusd': 0},
        'required_attempts': 2, 'required_cost_microusd': 20048,
    }
    assert not limits.root.exists()


def test_preflight_observes_both_caps_without_mutation(tmp_path, clock):
    limits = PublicLimits(tmp_path, chats_per_day=3, monthly_usd='0.000030')
    limits.reserve_stage(10, DAY, PARENT, 'draft')
    path = tmp_path / 'answer-usage.sqlite'
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert limits.preflight_pair([10, 10], DAY)['allowed']
    assert limits.preflight_pair([10, 11], DAY)['reason'] == 'monthly_limit'
    assert PublicLimits(tmp_path, chats_per_day=2).preflight_pair([0, 0], DAY)['reason'] == 'daily_limit'
    assert limits.preflight_pair([0, 0], '2026-10-26')['reason'] == 'day_mismatch'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    assert len(ledger(tmp_path)['receipts']) == 1


def test_preflight_cannot_authorize_against_later_capacity_race(tmp_path, clock):
    limits = PublicLimits(tmp_path, chats_per_day=2)
    assert limits.preflight_pair([1, 1], DAY)['allowed']
    limits.reserve_answer(1)
    assert limits.reserve_stage(1, DAY, PARENT, 'draft')['reserved']
    assert limits.reserve_stage(1, DAY, PARENT, 'reconstruction')['reason'] == 'daily_limit'
    assert ledger(tmp_path)['days'] == {DAY: 2}


@pytest.mark.parametrize('cap', ['daily', 'monthly'])
def test_competing_pairs_pass_preflight_then_one_second_stage_is_refused(tmp_path, clock, cap):
    after_preflight = threading.Barrier(2)
    after_first_reservation = threading.Barrier(2)
    def pair(i):
        limits = PublicLimits(tmp_path, chats_per_day=3 if cap == 'daily' else 100,
                              monthly_usd='0.000003' if cap == 'monthly' else '5')
        advisory = limits.preflight_pair([1, 1], DAY)
        after_preflight.wait(timeout=2)
        first = limits.reserve_stage(1, DAY, f'{i:032x}', 'draft')
        after_first_reservation.wait(timeout=2)
        second = limits.reserve_stage(1, DAY, f'{i:032x}', 'reconstruction')
        return advisory, first, second
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(pair, [1, 2]))
    assert all(advisory['allowed'] and first['reserved'] for advisory, first, _ in results)
    assert sum(second['reserved'] for _, _, second in results) == 1
    refused = next(second for _, _, second in results if not second['reserved'])
    assert refused['reason'] == cap + '_limit' and refused['receipt_id'] is None
    assert ledger(tmp_path)['days'] == {DAY: 3} and ledger(tmp_path)['months'] == {'2026-10': 3}
    assert len(ledger(tmp_path)['receipts']) == 3


def test_day_change_during_real_write_lock_wait_refuses_old_day(tmp_path, clock, monkeypatch):
    limits = PublicLimits(tmp_path)
    limits.reserve_stage(1, DAY, PARENT, 'draft')
    before = ledger(tmp_path)
    waiting = threading.Event()
    class WaitingConnection(ConnectionProxy):
        def execute(self, sql, *args):
            if sql == 'BEGIN IMMEDIATE':
                waiting.set()
            return super().execute(sql, *args)
    monkeypatch.setattr(hosting.sqlite3, 'connect', lambda *a, **k: WaitingConnection(CONNECT(*a, **k)))
    with CONNECT(tmp_path / 'answer-usage.sqlite') as blocker:
        blocker.execute('BEGIN IMMEDIATE')
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(limits.reserve_stage, 2, DAY, PARENT, 'reconstruction')
            assert waiting.wait(timeout=1)
            clock.day = '2026-10-28'
            blocker.commit()
            result = future.result(timeout=1)
    assert result['reason'] == 'day_mismatch' and not result['reserved']
    assert result['day'] == '2026-10-28' and ledger(tmp_path) == before


def test_read_snapshot_is_acquired_before_preflight_clock(tmp_path, clock, monkeypatch):
    PublicLimits(tmp_path).reserve_stage(1, DAY, PARENT, 'draft')
    def acquired(sql):
        if sql.startswith('SELECT name FROM sqlite_master'):
            clock.day = '2026-10-28'
    monkeypatch.setattr(hosting.sqlite3, 'connect', lambda *a, **k: ConnectionProxy(CONNECT(*a, **k), acquired))
    result = PublicLimits(tmp_path).preflight_pair([1, 1], DAY)
    assert result['reason'] == 'day_mismatch' and result['day'] == '2026-10-28'
    assert ledger(tmp_path)['days'] == {DAY: 1}


@pytest.mark.parametrize('costs', [True, [True, 1], [1, False], [1], [1, 2, 3], [-1, 2], [0.5, 2], ['1', 2], [1 << 62, 1 << 62]])
def test_invalid_preflight_inputs_do_not_create_files(tmp_path, clock, costs):
    root = tmp_path / 'absent'
    with pytest.raises(ValueError):
        PublicLimits(root).preflight_pair(costs, DAY)
    assert not root.exists()


@pytest.mark.parametrize('schema', [
    'CREATE TABLE usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)',
    'CREATE TABLE spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL)',
    'CREATE TABLE unrelated(value TEXT)',
    'CREATE TABLE usage(day TEXT PRIMARY KEY, attempts TEXT NOT NULL); CREATE TABLE spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL)',
    'CREATE TABLE usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL); CREATE TABLE spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL); CREATE TABLE stage_reservations(parent_id TEXT, phase TEXT, receipt_id TEXT, receipt_json TEXT)',
])
def test_partial_or_invalid_schema_fails_closed(tmp_path, clock, schema):
    path = tmp_path / 'answer-usage.sqlite'
    with CONNECT(path) as db:
        db.executescript(schema)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    limits = PublicLimits(tmp_path)
    with pytest.raises(ValueError, match='schema'):
        limits.preflight_pair([1, 1], DAY)
    with pytest.raises(ValueError, match='schema'):
        limits.reserve_stage(1, DAY, PARENT, 'draft')
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_corrupt_counter_values_fail_closed(tmp_path, clock):
    limits = PublicLimits(tmp_path)
    limits.reserve_stage(1, DAY, PARENT, 'draft')
    with CONNECT(tmp_path / 'answer-usage.sqlite') as db:
        db.execute("UPDATE spend SET reserved_microusd='broken'")
    before = ledger(tmp_path)
    with pytest.raises(ValueError, match='counters'):
        limits.preflight_pair([1, 1], DAY)
    with pytest.raises(ValueError, match='counters'):
        limits.reserve_stage(1, DAY, PARENT, 'reconstruction')
    assert ledger(tmp_path) == before


def test_disappearing_existing_ledger_is_not_reclassified_as_new(tmp_path, clock, monkeypatch):
    limits = PublicLimits(tmp_path)
    limits.reserve_stage(1, DAY, PARENT, 'draft')
    path = tmp_path / 'answer-usage.sqlite'
    def disappeared(*args, **kwargs):
        path.unlink()  # Synthetic race after lstat, before the mode=ro open.
        return CONNECT(*args, **kwargs)
    monkeypatch.setattr(hosting.sqlite3, 'connect', disappeared)
    with pytest.raises(sqlite3.OperationalError):
        limits.preflight_pair([1, 1], DAY)
    assert not path.exists()


def test_empty_new_database_and_dangling_symlink(tmp_path, clock):
    limits = PublicLimits(tmp_path)
    assert limits.reserve_stage(1, '2026-10-26', PARENT, 'draft')['reason'] == 'day_mismatch'
    assert limits.preflight_pair([1, 1], DAY)['allowed']
    assert ledger(tmp_path) == {'days': {}, 'months': {}, 'receipts': []}
    other = tmp_path / 'other'
    other.mkdir()
    (other / 'answer-usage.sqlite').symlink_to(other / 'missing')
    with pytest.raises(sqlite3.OperationalError):
        PublicLimits(other).preflight_pair([1, 1], DAY)
    assert not (other / 'missing').exists()


def test_readonly_preflight_sees_committed_wal(tmp_path, clock):
    limits = PublicLimits(tmp_path)
    limits.reserve_stage(1, DAY, PARENT, 'draft')
    with CONNECT(tmp_path / 'answer-usage.sqlite') as writer:
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute('PRAGMA wal_autocheckpoint=0')
        writer.execute('UPDATE usage SET attempts=99')
        writer.execute('UPDATE spend SET reserved_microusd=4999999')
        writer.commit()
        result = limits.preflight_pair([1, 1], DAY)
        assert not result['allowed']
        assert result['observed'] == {'day_attempts': 99, 'month_reserved_microusd': 4999999}


@pytest.mark.parametrize('operation', ['reserve', 'preflight'])
def test_lock_timeout_fails_closed_and_does_not_retry(tmp_path, clock, monkeypatch, operation):
    limits = PublicLimits(tmp_path)
    limits.reserve_stage(1, DAY, PARENT, 'draft')
    before = ledger(tmp_path)
    monkeypatch.setattr(hosting, 'STAGE_LOCK_TIMEOUT_SECONDS', 0.02)
    with CONNECT(tmp_path / 'answer-usage.sqlite') as blocker:
        blocker.execute('BEGIN EXCLUSIVE')
        start = time.monotonic()
        with pytest.raises(sqlite3.OperationalError, match='locked'):
            if operation == 'reserve':
                limits.reserve_stage(2, DAY, PARENT, 'reconstruction')
            else:
                limits.preflight_pair([1, 2], DAY)
        assert time.monotonic() - start < 1
        blocker.rollback()
    assert ledger(tmp_path) == before
