"""Explicit import of the FINAL dev ledger; never accepts production accounting.

Obtain a complete export from /workspace/.research-private/usage only after stopping
its paid writer. This command is intentionally not part of start_local.py.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.local_corpus import STATE

def reconcile(source, expected_sha256, expires_at, prior_workspace_stopped, state=STATE):
    if not prior_workspace_stopped:raise ValueError('The previous dev writer must be stopped before a final transfer')
    source=Path(source).resolve();destination=Path(state)/'accounting'
    raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    if sha!=expected_sha256:raise ValueError('Export checksum mismatch')
    if datetime.fromisoformat(expires_at)<=datetime.now(timezone.utc):raise ValueError('Expired allowance')
    if any(Path(str(source)+s).exists() for s in ('-wal','-journal')):raise ValueError('Export must be checkpointed and closed')
    with sqlite3.connect(source.as_uri()+'?mode=ro&immutable=1',uri=True) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Invalid ledger')
        spent=db.execute('SELECT sum(reserved_microusd) FROM spend').fetchone()[0]
        attempts=db.execute('SELECT sum(attempts) FROM usage').fetchone()[0]
        receipts=[json.loads(r[0]) for r in db.execute('SELECT receipt_json FROM stage_reservations')]
        if not receipts or attempts!=len(receipts) or spent!=sum(r['cost_microusd'] for r in receipts):raise ValueError('Incomplete dev reservation history')
        if not 0<spent<=2_000_000:raise ValueError('Not the bounded additional dev ledger')
    if destination.exists():raise ValueError('Accounting already exists; never overwrite or reset it')
    destination.mkdir(mode=0o700,parents=True)
    shutil.copy2(source,destination/'cloud-dev.sqlite');(destination/'cloud-dev.sqlite').chmod(0o444)
    shutil.copy2(source,destination/'answer-usage.sqlite');(destination/'answer-usage.sqlite').chmod(0o600)
    with sqlite3.connect(destination/'answer-usage.sqlite') as db:
        db.execute('CREATE TABLE local_dev_baseline(source_sha256 TEXT NOT NULL)');db.execute('INSERT INTO local_dev_baseline VALUES (?)',(sha,))
        db.execute('CREATE TABLE sdk_reservations(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,reserved_microusd INTEGER NOT NULL)')
    receipt={'scope':'additional-dev-2026-10-29','cap_microusd':2_000_000,'source_sha256':sha,'prior_reserved_microusd':spent,'prior_attempts':attempts,'prior_workspace_stopped':True,'expires_at':expires_at,'reconciled_at':datetime.now(timezone.utc).isoformat()}
    (destination/'reconciliation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return {'prior_attempts':attempts,'reserved_usd':spent/1e6,'remaining_usd':(2_000_000-spent)/1e6}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--final-cloud-dev-ledger',required=True);p.add_argument('--sha256',required=True);p.add_argument('--expires-at',required=True);p.add_argument('--prior-workspace-stopped',action='store_true')
    a=p.parse_args();print(json.dumps(reconcile(a.final_cloud_dev_ledger,a.sha256,a.expires_at,a.prior_workspace_stopped)))
