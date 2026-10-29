"""Record the user's 30 October additive $2 approval without changing past rows.

This explicit one-time operation is never called by the server or its launcher.
The renewed allowance is budget-limited; the user did not impose a new expiry.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.local_budget import DevBudget, RENEWAL_ID
from backend.local_corpus import STATE

AUTHORIZATION='Renew the dev allowance with up to $2 more and get the local Claude agent working end to end. Preserve all existing accounting and don’t deploy.'

def renew(state=STATE):
    gate=DevBudget(state);receipt=gate.receipt(require_active=False)
    if receipt.get('renewal_id'):raise ValueError('This approval has already been recorded; never add it twice')
    status=gate.status()
    if status['reserved_usd'] is None:raise ValueError('Existing accounting is unavailable')
    backup=gate.state/'before-renewal-2026-10-30.sqlite'
    if backup.exists():raise ValueError('Renewal backup already exists; inspect the prior operation before continuing')
    with gate.connect() as db:
        with sqlite3.connect(backup) as saved:db.backup(saved)
        backup.chmod(0o400)
        db.execute('BEGIN IMMEDIATE')
        try:
            spent=db.execute('SELECT sum(reserved_microusd) FROM spend').fetchone()[0]
            original=sum(json.loads(r[0])['cost_microusd'] for r in db.execute('SELECT receipt_json FROM stage_reservations'))
            local=db.execute('SELECT coalesce(sum(reserved_microusd),0) FROM sdk_reservations').fetchone()[0]
            if spent!=original+local:raise ValueError('Reservation history does not reconcile')
            db.execute('CREATE TABLE dev_allowance_grants(id TEXT PRIMARY KEY, additional_microusd INTEGER NOT NULL, source_sha256 TEXT NOT NULL, reconciliation_sha256 TEXT NOT NULL, authorized_at TEXT NOT NULL, authorization TEXT NOT NULL, reserved_before_microusd INTEGER NOT NULL, expires_at TEXT)')
            db.execute('INSERT INTO dev_allowance_grants VALUES (?,?,?,?,?,?,?,NULL)',(RENEWAL_ID,2_000_000,receipt['source_sha256'],hashlib.sha256((gate.state/'reconciliation.json').read_bytes()).hexdigest(),datetime.now(timezone.utc).isoformat(),AUTHORIZATION,spent))
            db.commit()
        except BaseException:
            db.rollback();raise
    return gate.status()

if __name__=='__main__':print(json.dumps(renew()))
