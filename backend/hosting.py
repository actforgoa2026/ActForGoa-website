"""Explicit public-host configuration and bounded public-service operations."""
from collections import deque
from contextlib import closing, contextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import json
import os
import re
import sqlite3
import threading
import time
from urllib.parse import urlsplit
from uuid import uuid4
from starlette.responses import JSONResponse

STAGE_RESERVATION_VERSION = 'afg-stage-reservation-v1'
STAGE_PREFLIGHT_VERSION = 'afg-stage-preflight-v1'
STAGE_LOCK_TIMEOUT_SECONDS = 0.25
SQLITE_MAX_INTEGER = (1 << 63) - 1


class UsageLedgerUnavailable(Exception):
    """Dispatch is disabled; no historical accounting may be initialized."""


def _stage_tables(db):
    # The first read establishes the read snapshot used by preflight before its
    # clock check. Existing reconciliation tables are allowed alongside these.
    tables = {row[0] for row in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    if not tables:
        return tables  # New, completely empty database; no historical counters.
    if not {'usage', 'spend'} <= tables:
        raise ValueError('Invalid stage reservation schema')
    for table, key, value in [('usage', 'day', 'attempts'), ('spend', 'month', 'reserved_microusd')]:
        columns = db.execute('SELECT name, type, "notnull", pk FROM pragma_table_info(?)', (table,)).fetchall()
        if (len(columns) != 2 or columns[0][0:2] != (key, 'TEXT') or columns[0][3] != 1
                or columns[1] != (value, 'INTEGER', 1, 0)):
            raise ValueError('Invalid stage reservation schema')
    if 'stage_reservations' in tables:
        columns = db.execute('SELECT name, type, "notnull", pk FROM pragma_table_info(?)', ('stage_reservations',)).fetchall()
        expected = [('parent_id', 'TEXT', 1, 1), ('phase', 'TEXT', 1, 2),
                    ('receipt_id', 'TEXT', 1, 0), ('receipt_json', 'TEXT', 1, 0)]
        unique_columns = [tuple(row[0] for row in db.execute(
            'SELECT name FROM pragma_index_info(?) ORDER BY seqno', (index[1],)))
            for index in db.execute('PRAGMA index_list(stage_reservations)').fetchall()
            if index[2] and not index[4]]
        if columns != expected or ('receipt_id',) not in unique_columns:
            raise ValueError('Invalid stage reservation receipt schema')
    return tables


def _stage_snapshot(db, day, month, tables):
    day_row = db.execute('SELECT attempts FROM usage WHERE day=?', (day,)).fetchone() if 'usage' in tables else None
    month_row = db.execute('SELECT reserved_microusd FROM spend WHERE month=?', (month,)).fetchone() if 'spend' in tables else None
    snapshot = {'day_attempts': day_row[0] if day_row else 0,
                'month_reserved_microusd': month_row[0] if month_row else 0}
    if any(type(value) is not int or not 0 <= value <= SQLITE_MAX_INTEGER for value in snapshot.values()):
        raise ValueError('Invalid stage reservation counters')
    return snapshot


def _preserved_tables(db):
    """Validate an existing ledger without requiring optional receipt tables.

    Legacy monthly ledgers with only usage/spend remain compatible. An empty
    file, empty schema or counterless replacement is not preserved accounting.
    """
    try:
        tables = _stage_tables(db)
        if not {'usage', 'spend'} <= tables:
            raise ValueError('Missing preserved counters')
        for table, column in [('usage', 'attempts'), ('spend', 'reserved_microusd')]:
            values = [row[0] for row in db.execute(f'SELECT {column} FROM {table}')]
            if not values or any(type(value) is not int or not 0 <= value <= SQLITE_MAX_INTEGER for value in values):
                raise ValueError('Invalid preserved counters')
        return tables
    except (sqlite3.Error, ValueError):
        raise UsageLedgerUnavailable('Existing answer accounting is unavailable.') from None


def _validate_stage_cost(cost_microusd):
    if type(cost_microusd) is not int or not 0 <= cost_microusd <= SQLITE_MAX_INTEGER:
        raise ValueError('Invalid stage reservation cost')


def _validate_stage_day(expected_day):
    if type(expected_day) is not str or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', expected_day):
        raise ValueError('Invalid expected UTC day')
    try:
        date.fromisoformat(expected_day)
    except ValueError:
        raise ValueError('Invalid expected UTC day') from None


def _validate_stage_request(cost_microusd, expected_day, parent_id, phase):
    _validate_stage_cost(cost_microusd)
    _validate_stage_day(expected_day)
    if type(parent_id) is not str or not re.fullmatch(r'[0-9a-f]{32}', parent_id):
        raise ValueError('Stage parent identity must be opaque lowercase hexadecimal')
    if type(phase) is not str or phase not in ('draft', 'reconstruction'):
        raise ValueError('Invalid reservation phase')


class RequestSizeLimit:
    def __init__(self, app, maximum=65536):self.app=app;self.maximum=maximum
    async def __call__(self, scope, receive, send):
        if scope['type']!='http' or scope['method'] not in ('POST','PUT','PATCH'):
            return await self.app(scope,receive,send)
        messages=[];size=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            size+=len(message.get('body',b''))
            if size>self.maximum:
                return await JSONResponse({'detail':'Request is too large.'},status_code=413)(scope,receive,send)
            messages.append(message)
            if not message.get('more_body',False):break
        async def buffered_receive():
            return messages.pop(0) if messages else await receive()
        await self.app(scope,buffered_receive,send)

def public_config():
    origin=os.getenv('RESEARCH_PUBLIC_ORIGIN','').rstrip('/')
    if not origin:return None,['localhost','127.0.0.1','testserver']
    url=urlsplit(origin)
    if url.scheme!='https' or not url.hostname or url.path or url.query or url.fragment or url.username:
        raise ValueError('RESEARCH_PUBLIC_ORIGIN must be an HTTPS origin')
    if os.getenv('RESEARCH_PUBLISH_CORPUS')!='1':
        raise ValueError('Public research requires RESEARCH_PUBLISH_CORPUS=1')
    hosts=['localhost','127.0.0.1','healthcheck.railway.app',url.hostname]
    for host in os.getenv('RESEARCH_ALLOWED_HOSTS','').split(',')+[os.getenv('RAILWAY_PUBLIC_DOMAIN','')]:
        host=host.strip()
        if host and (host=='*' or '/' in host or ':' in host):raise ValueError('Research hosts must be exact hostnames')
        if host:hosts.append(host)
    return origin,hosts

class PublicLimits:
    """Single-instance aggregate limits. No client identifiers are collected."""
    def __init__(self, root, search_per_minute=120, chats_per_day=100, monthly_usd='5', require_existing=False, release_allowance=False):
        self.root=Path(root);self.search_limit=search_per_minute;self.chat_limit=chats_per_day
        self.require_existing=require_existing
        amount=Decimal(str(monthly_usd))
        if not amount.is_finite() or amount<0:raise ValueError('Monthly answer budget must be non-negative')
        self.monthly_limit=int(amount*1_000_000)
        self.release_allowance=release_allowance
        self.searches=deque();self.lock=threading.Lock()

    def effective_limits(self, day):
        # Explicit user authorization for this launch only. Evaluate against the
        # transaction's UTC date so an already-running service expires correctly.
        daily = 160 if self.release_allowance and day == '2026-10-28' else self.chat_limit
        monthly = 15_300_000 if self.release_allowance and day[:7] == '2026-10' else self.monthly_limit
        return daily, monthly

    def _open_ledger(self, *, write):
        path=self.root/'answer-usage.sqlite'
        if self.require_existing:
            # mode=rw is enforced on every reservation, eliminating the gap
            # between a startup/readiness check and a later missing volume.
            try:
                return sqlite3.connect(path.resolve().as_uri()+('?mode=rw' if write else '?mode=ro'),
                                       uri=True,timeout=STAGE_LOCK_TIMEOUT_SECONDS,isolation_level=None)
            except sqlite3.Error:
                raise UsageLedgerUnavailable('Existing answer accounting is unavailable.') from None
        if write:self.root.mkdir(parents=True,exist_ok=True)
        return sqlite3.connect(path,timeout=STAGE_LOCK_TIMEOUT_SECONDS,isolation_level=None)

    def existing_ledger_ready(self):
        if not self.require_existing:return True
        try:
            with closing(self._open_ledger(write=False)) as db:
                db.execute('BEGIN')
                try:_preserved_tables(db)
                finally:db.rollback()
            return True
        except (UsageLedgerUnavailable,sqlite3.Error):
            return False

    @contextmanager
    def _ledger(self, *, write):
        try:
            with closing(self._open_ledger(write=write)) as db:
                yield db
        except sqlite3.Error:
            if self.require_existing:
                raise UsageLedgerUnavailable('Existing answer accounting is unavailable.') from None
            raise
    def allow_search(self):
        now=time.monotonic()
        with self.lock:
            while self.searches and self.searches[0]<now-60:self.searches.popleft()
            if len(self.searches)>=self.search_limit:return False
            self.searches.append(now);return True
    def reserve_answer(self, cost_microusd=0):
        # Charge the conservative maximum before dispatch. Failures/timeouts still count.
        # SQLite serializes reservations across concurrent processes and survives restarts.
        if not isinstance(cost_microusd,int) or cost_microusd<0:raise ValueError('Invalid cost reservation')
        if self.require_existing:
            result=self.reserve_stage(cost_microusd,datetime.now(timezone.utc).date().isoformat(),uuid4().hex,'draft')
            return result['reserved']
        self.root.mkdir(parents=True,exist_ok=True)
        today=datetime.now(timezone.utc).date().isoformat()
        month=today[:7]
        daily_limit,monthly_limit=self.effective_limits(today)
        with self.lock,sqlite3.connect(self.root/'answer-usage.sqlite') as db:
            db.execute('CREATE TABLE IF NOT EXISTS usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL)')
            db.execute('BEGIN IMMEDIATE')
            count=db.execute('SELECT attempts FROM usage WHERE day=?',(today,)).fetchone()
            if (count[0] if count else 0)>=daily_limit:return False
            spend=db.execute('SELECT reserved_microusd FROM spend WHERE month=?',(month,)).fetchone()
            if (spend[0] if spend else 0)+cost_microusd>monthly_limit:return False
            db.execute('INSERT INTO usage VALUES (?,1) ON CONFLICT(day) DO UPDATE SET attempts=attempts+1',(today,))
            db.execute('INSERT INTO spend VALUES (?,?) ON CONFLICT(month) DO UPDATE SET reserved_microusd=reserved_microusd+excluded.reserved_microusd',(month,cost_microusd))
            # Preserve historical attempts for reconciliation across provider changes.
            # Only today's row contributes to the daily allowance.
        return True

    def reserve_stage(self, cost_microusd, expected_day, parent_id, phase):
        """Commit a phase receipt and its charge together, or authorize nothing.

        Only opaque request IDs and fixed phase names are accepted. Refused
        results carry no receipt ID and do not update counters or receipt rows.
        A duplicate never returns the earlier success as permission to dispatch.
        This method performs no network work and has no retry or refund path.
        """
        _validate_stage_request(cost_microusd, expected_day, parent_id, phase)
        # SQLite, rather than the instance lock, serializes this operation with
        # legacy reservations and other processes. Bound waiting for its lock.
        with self._ledger(write=True) as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                # Read the clock only after acquiring the write transaction: a
                # reservation waiting across UTC midnight must not charge yesterday.
                day = datetime.now(timezone.utc).date().isoformat()
                month = day[:7]
                daily_limit, monthly_limit = self.effective_limits(day)
                tables = _preserved_tables(db) if self.require_existing else _stage_tables(db)
                before = _stage_snapshot(db, day, month, tables)
                result = {
                    'version': STAGE_RESERVATION_VERSION,
                    'reserved': False, 'reason': 'day_mismatch',
                    'parent_id': parent_id, 'phase': phase,
                    'expected_day': expected_day, 'day': day, 'month': month,
                    'cost_microusd': cost_microusd,
                    'before': before, 'after': dict(before), 'receipt_id': None,
                }
                if day != expected_day:
                    db.rollback()
                    return result
                if 'stage_reservations' in tables and db.execute(
                    'SELECT 1 FROM stage_reservations WHERE parent_id=? AND phase=?',
                    (parent_id, phase),
                ).fetchone():
                    result['reason'] = 'duplicate'
                elif before['day_attempts'] >= daily_limit:
                    result['reason'] = 'daily_limit'
                elif before['month_reserved_microusd'] + cost_microusd > monthly_limit:
                    result['reason'] = 'monthly_limit'
                else:
                    after = {'day_attempts': before['day_attempts'] + 1,
                             'month_reserved_microusd': before['month_reserved_microusd'] + cost_microusd}
                    if any(value > SQLITE_MAX_INTEGER for value in after.values()):
                        raise ValueError('Stage reservation counters exceed the storage range')
                    db.execute('CREATE TABLE IF NOT EXISTS usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
                    db.execute('CREATE TABLE IF NOT EXISTS spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL)')
                    db.execute('''CREATE TABLE IF NOT EXISTS stage_reservations(
                        parent_id TEXT NOT NULL,
                        phase TEXT NOT NULL CHECK(phase IN ('draft','reconstruction')),
                        receipt_id TEXT NOT NULL UNIQUE,
                        receipt_json TEXT NOT NULL,
                        PRIMARY KEY(parent_id, phase)
                    )''')
                    result.update(reserved=True, reason='reserved', after=after, receipt_id=uuid4().hex)
                    db.execute('INSERT INTO usage VALUES (?,1) ON CONFLICT(day) DO UPDATE SET attempts=attempts+1', (day,))
                    db.execute('INSERT INTO spend VALUES (?,?) ON CONFLICT(month) DO UPDATE SET reserved_microusd=reserved_microusd+excluded.reserved_microusd', (month, cost_microusd))
                    db.execute('INSERT INTO stage_reservations VALUES (?,?,?,?)',
                               (parent_id, phase, result['receipt_id'],
                                json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False)))
                    db.commit()
                    return result
                db.rollback()
                return result
            except BaseException:
                # If commit was uncertain, never return a receipt or authorize
                # dispatch. Rollback cannot undo an already committed charge.
                if db.in_transaction:
                    db.rollback()
                raise

    def preflight_pair(self, costs_microusd, expected_day):
        """Read-only advisory capacity for two phases, never dispatch authority.

        Absence is observed without creating directories or a database. For an
        existing database, read its schema to acquire the snapshot before reading
        UTC. Another process can consume capacity immediately after this returns;
        reserve_stage remains the sole authority for each subsequent dispatch.
        """
        if type(costs_microusd) not in (list, tuple) or len(costs_microusd) != 2:
            raise ValueError('Pair preflight requires exactly two costs')
        return self._preflight_costs(costs_microusd, expected_day, 2)

    def preflight_single(self, cost_microusd, expected_day):
        """Read-only one-stage advice; reserve_stage alone authorizes dispatch."""
        _validate_stage_cost(cost_microusd)
        return self._preflight_costs([cost_microusd], expected_day, 1)

    def _preflight_costs(self, costs_microusd, expected_day, required_attempts):
        for cost in costs_microusd:
            _validate_stage_cost(cost)
        total = sum(costs_microusd)
        _validate_stage_cost(total)
        _validate_stage_day(expected_day)
        path = self.root / 'answer-usage.sqlite'
        if self.require_existing:
            with self._ledger(write=False) as db:
                db.execute('BEGIN')
                try:
                    _preserved_tables(db)
                finally:
                    db.rollback()
        try:
            path.lstat()
        except FileNotFoundError:
            if self.require_existing:
                raise UsageLedgerUnavailable('Existing answer accounting is unavailable.') from None
            day = datetime.now(timezone.utc).date().isoformat()
            observed = {'day_attempts': 0, 'month_reserved_microusd': 0}
        else:
            # mode=ro cannot initialize or change the ledger, including if it
            # disappears between lstat and connect. Never use immutable mode:
            # committed WAL reservations must remain visible to this read.
            with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True,
                                         timeout=STAGE_LOCK_TIMEOUT_SECONDS,
                                         isolation_level=None)) as db:
                db.execute('BEGIN')
                try:
                    tables = _preserved_tables(db) if self.require_existing else _stage_tables(db)
                    day = datetime.now(timezone.utc).date().isoformat()
                    observed = _stage_snapshot(db, day, day[:7], tables)
                finally:
                    db.rollback()
        reason = 'allowed'
        daily_limit, monthly_limit = self.effective_limits(day)
        if day != expected_day:
            reason = 'day_mismatch'
        elif observed['day_attempts'] + required_attempts > daily_limit:
            reason = 'daily_limit'
        elif observed['month_reserved_microusd'] + total > monthly_limit:
            reason = 'monthly_limit'
        return {'version': STAGE_PREFLIGHT_VERSION if required_attempts == 2 else 'afg-single-preflight-v1',
                'allowed': reason == 'allowed', 'reason': reason,
                'expected_day': expected_day, 'day': day, 'month': day[:7],
                'observed': observed, 'required_attempts': required_attempts, 'required_cost_microusd': total}
