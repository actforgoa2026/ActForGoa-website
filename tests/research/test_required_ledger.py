"""Required accounting tests use disposable ledgers only, never production data."""
from datetime import datetime, timezone
import sqlite3
from uuid import uuid4

import pytest
from backend.hosting import PublicLimits, UsageLedgerUnavailable


def reserve(limits, cost=10):
    return limits.reserve_stage(cost,datetime.now(timezone.utc).date().isoformat(),uuid4().hex,'draft')


def initialized(tmp_path):
    assert reserve(PublicLimits(tmp_path))['reserved']
    return tmp_path/'answer-usage.sqlite'


def test_required_ledger_cannot_be_recreated_after_a_successful_reservation(tmp_path):
    path=initialized(tmp_path)
    limits=PublicLimits(tmp_path,require_existing=True,chats_per_day=2)
    assert reserve(limits)['reserved']
    assert not reserve(limits)['reserved']
    path.unlink()
    assert not limits.existing_ledger_ready()
    with pytest.raises(UsageLedgerUnavailable):reserve(limits)
    with pytest.raises(UsageLedgerUnavailable):limits.reserve_answer(10)
    with pytest.raises(UsageLedgerUnavailable):limits.preflight_single(10,datetime.now(timezone.utc).date().isoformat())
    assert not path.exists()


@pytest.mark.parametrize('state',['missing_directory','empty_file','counterless_schema','wrong_schema','corrupt_file','negative_counter'])
def test_required_accounting_is_never_initialized_or_repaired_implicitly(tmp_path,state):
    root=tmp_path/'ledger'
    path=root/'answer-usage.sqlite'
    if state!='missing_directory':root.mkdir()
    if state=='empty_file':path.touch()
    if state=='counterless_schema':
        with sqlite3.connect(path) as db:
            db.executescript('CREATE TABLE usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL); CREATE TABLE spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL);')
    if state=='wrong_schema':
        with sqlite3.connect(path) as db:db.execute('CREATE TABLE unrelated(secret TEXT)')
    if state=='corrupt_file':path.write_bytes(b'not a SQLite ledger')
    if state=='negative_counter':
        initialized(root)
        with sqlite3.connect(path) as db:db.execute('UPDATE spend SET reserved_microusd=-1')
    before=path.read_bytes() if path.exists() else None
    limits=PublicLimits(root,require_existing=True)
    assert not limits.existing_ledger_ready()
    with pytest.raises(UsageLedgerUnavailable):reserve(limits)
    assert (path.read_bytes() if path.exists() else None)==before
    if state=='missing_directory':assert not root.exists()


def test_existing_legacy_monthly_counters_do_not_need_stage_receipts(tmp_path):
    # The prior monthly implementation had usage/spend without stage_reservations.
    day=datetime.now(timezone.utc).date().isoformat();path=tmp_path/'answer-usage.sqlite'
    with sqlite3.connect(path) as db:
        db.executescript('CREATE TABLE usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL); CREATE TABLE spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL); CREATE TABLE reconciliation_receipts(receipt TEXT PRIMARY KEY);')
        db.execute('INSERT INTO usage VALUES (?,?)',(day,7))
        db.execute('INSERT INTO spend VALUES (?,?)',(day[:7],12345))
        db.execute("INSERT INTO reconciliation_receipts VALUES ('historical-import')")
    limits=PublicLimits(tmp_path,require_existing=True)
    assert limits.existing_ledger_ready()
    result=reserve(limits,45)
    assert result['before']=={'day_attempts':7,'month_reserved_microusd':12345}
    assert result['after']=={'day_attempts':8,'month_reserved_microusd':12390}
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT receipt FROM reconciliation_receipts').fetchone()[0]=='historical-import'
        assert db.execute('SELECT count(*) FROM stage_reservations').fetchone()[0]==1
