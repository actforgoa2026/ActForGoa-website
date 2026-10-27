"""Auditable, additive recovery of aggregate answer reservations. No provider calls.

Run with dispatch disabled. A missing ledger requires explicit initialization;
no database is created by inspection. Receipts prevent duplicate imports. The
historical reservation amounts are not actual provider charges.
"""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(adjustment):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,119}', adjustment.get('receipt', '')):
        raise ValueError('A stable unique receipt ID is required')
    if adjustment.get('kind') not in ('reconstructed_conservative_reservations', 'verified_validation_delta'):
        raise ValueError('The adjustment must identify its provenance')
    if not re.fullmatch(r'[0-9a-f]{64}', adjustment.get('source_sha256', '')):
        raise ValueError('A source evidence SHA-256 is required')
    if not isinstance(adjustment.get('source_description'), str) or not adjustment['source_description'].strip():
        raise ValueError('Describe the source evidence and overlap calculation')
    for table in ('days', 'months'):
        rows = adjustment.get(table)
        if not isinstance(rows, dict):
            raise ValueError('Daily and monthly deltas must be objects')
        for period, amount in rows.items():
            if not isinstance(period, str) or type(amount) is not int or amount < 0:
                raise ValueError('Only nonnegative integer additions are permitted')
            if table == 'days':
                if date.fromisoformat(period).isoformat() != period:
                    raise ValueError('Use ISO UTC dates')
            elif not re.fullmatch(r'\d{4}-\d{2}', period) or date.fromisoformat(period + '-01').strftime('%Y-%m') != period:
                raise ValueError('Use ISO UTC months')
    if not sum(adjustment['days'].values()) + sum(adjustment['months'].values()):
        raise ValueError('An empty adjustment is not an import')


def snapshot(db):
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    result = {'days': {}, 'months': {}, 'receipts': []}
    for table, column, key in (('usage', 'attempts', 'days'), ('spend', 'reserved_microusd', 'months')):
        if table in tables:
            rows = db.execute(f'SELECT * FROM {table} ORDER BY 1').fetchall()
            if any(len(row) != 2 or type(row[1]) is not int or row[1] < 0 for row in rows):
                raise ValueError(f'Invalid existing {table} counters; refusing reconciliation')
            result[key] = dict(rows)
    if 'usage_imports' in tables:
        result['receipts'] = [row[0] for row in db.execute('SELECT receipt FROM usage_imports ORDER BY receipt')]
    return result


def inspect_ledger(path):
    path = Path(path)
    if not path.exists():
        return {'exists': False, 'days': {}, 'months': {}, 'receipts': []}
    with sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True) as db:
        return {'exists': True, **snapshot(db)}


def backup(path, destination):
    """Use SQLite's backup API, including committed WAL contents."""
    destination = Path(destination)
    # Never overwrite an audit copy, even for a duplicate receipt attempt.
    with destination.open('xb'):
        pass
    destination.chmod(0o600)
    with sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True) as source:
        with sqlite3.connect(destination) as target:
            source.backup(target)
    return digest(destination)


def reconcile(path, adjustment, evidence, audit_dir, *, apply=False, initialize_missing=False):
    validate(adjustment)
    if digest(evidence) != adjustment['source_sha256']:
        raise ValueError('Source evidence does not match its recorded SHA-256')
    path, audit_dir = Path(path), Path(audit_dir)
    before = inspect_ledger(path)
    if adjustment['receipt'] in before['receipts']:
        raise ValueError('Receipt already imported; refusing duplicate adjustment')
    report = {'adjustment': adjustment, 'before': before, 'applied': False}
    if not apply:
        return report
    if not before['exists'] and not initialize_missing:
        raise ValueError('Ledger is absent; explicit initialization is required')
    audit_dir.mkdir(parents=True, exist_ok=True)
    prefix = audit_dir / adjustment['receipt']
    # Preflight every destination before changing the genuine ledger.
    for suffix in ('.before.sqlite', '.after.sqlite', '.json'):
        if Path(str(prefix) + suffix).exists():
            raise FileExistsError('Audit destination already exists')
    if before['exists']:
        report['before_sha256'] = backup(path, str(prefix) + '.before.sqlite')
        backed_up = inspect_ledger(str(prefix) + '.before.sqlite')
        if backed_up != before:
            raise ValueError('Ledger changed during capture; disable dispatch and retry')
    path.parent.mkdir(parents=True, exist_ok=True)
    if not before['exists']:
        # Exclusive creation prevents silently adopting a concurrently created ledger.
        with path.open('xb'):
            pass
        path.chmod(0o600)
    with sqlite3.connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        current = snapshot(db)
        if current != {key: before[key] for key in current}:
            raise ValueError('Ledger changed since backup; no adjustment applied')
        db.execute('CREATE TABLE IF NOT EXISTS usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS spend(month TEXT PRIMARY KEY, reserved_microusd INTEGER NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS usage_imports(receipt TEXT PRIMARY KEY, imported_at TEXT NOT NULL, adjustment_json TEXT NOT NULL)')
        db.execute('INSERT INTO usage_imports VALUES (?,?,?)', (adjustment['receipt'], datetime.now(timezone.utc).isoformat(), json.dumps(adjustment, sort_keys=True)))
        for day, amount in adjustment['days'].items():
            db.execute('INSERT INTO usage VALUES (?,?) ON CONFLICT(day) DO UPDATE SET attempts=attempts+excluded.attempts', (day, amount))
        for month, amount in adjustment['months'].items():
            db.execute('INSERT INTO spend VALUES (?,?) ON CONFLICT(month) DO UPDATE SET reserved_microusd=reserved_microusd+excluded.reserved_microusd', (month, amount))
        expected = {key: dict(before[key]) for key in ('days', 'months')}
        for key in expected:
            for period, amount in adjustment[key].items():
                expected[key][period] = expected[key].get(period, 0) + amount
        actual = snapshot(db)
        if any(actual[key] != expected[key] for key in expected):
            raise ValueError('Post-import counters do not match additive deltas')
    report.update(applied=True, after=inspect_ledger(path))
    report['after_sha256'] = backup(path, str(prefix) + '.after.sqlite')
    with Path(str(prefix) + '.json').open('x') as out:
        json.dump(report, out, indent=2, sort_keys=True)
        out.write('\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--adjustment', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--audit-dir', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--initialize-missing', action='store_true')
    args = parser.parse_args()
    result = reconcile(args.ledger, json.loads(args.adjustment.read_text()), args.evidence, args.audit_dir,
                       apply=args.apply, initialize_missing=args.initialize_missing)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
