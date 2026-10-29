"""Lifetime dev allowance with explicit additive grants and preserved accounting.

Missing reconciliation or ledger always fails closed. No runtime creates, resets,
refunds or rolls over accounting. Every provider attempt is reserved before sending.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
from .local_corpus import STATE

CAP = 2_000_000
RENEWAL_ID = 'user-approved-additional-2usd-2026-10-30'
MODEL = 'claude-sonnet-5-5'

class BudgetUnavailable(ValueError):pass

class DevBudget:
    def __init__(self, state=STATE):self.state=Path(state)/'accounting'

    def receipt(self, require_active=True):
        try:
            receipt=json.loads((self.state/'reconciliation.json').read_text())
            source=self.state/'cloud-dev.sqlite'
            if receipt['scope']!='additional-dev-2026-10-29' or receipt['cap_microusd']!=CAP or receipt['prior_workspace_stopped'] is not True:raise ValueError()
            if hashlib.sha256(source.read_bytes()).hexdigest()!=receipt['source_sha256']:raise ValueError()
            with self.connect() as db:
                has_grants=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='dev_allowance_grants'").fetchone()
                grants=db.execute('SELECT id,additional_microusd,source_sha256,reconciliation_sha256 FROM dev_allowance_grants').fetchall() if has_grants else []
            if grants:
                original_sha=hashlib.sha256((self.state/'reconciliation.json').read_bytes()).hexdigest()
                if grants!=[(RENEWAL_ID,2_000_000,receipt['source_sha256'],original_sha)]:raise ValueError()
                receipt={**receipt,'cap_microusd':CAP+2_000_000,'original_expires_at':receipt['expires_at'],'expires_at':None,'renewal_id':RENEWAL_ID}
            expired=bool(receipt['expires_at']) and datetime.fromisoformat(receipt['expires_at'])<=datetime.now(timezone.utc)
            if require_active and expired:raise BudgetUnavailable('The original dev allowance has expired; paid calls are paused. Existing reservations are preserved.')
            return receipt
        except BudgetUnavailable:raise
        except (OSError,KeyError,ValueError):raise BudgetUnavailable('Paid answers are paused: the existing cloud dev reservations have not been reconciled locally.') from None

    def connect(self):
        try:return sqlite3.connect((self.state/'answer-usage.sqlite').resolve().as_uri()+'?mode=rw',uri=True,timeout=5,isolation_level=None)
        except sqlite3.Error:raise BudgetUnavailable('The reconciled dev ledger is unavailable; paid calls are paused.') from None

    def status(self):
        try:
            receipt=self.receipt(require_active=False)
            with self.connect() as db:
                spent=db.execute('SELECT coalesce(sum(reserved_microusd),0) FROM spend').fetchone()[0]
                baseline=db.execute('SELECT source_sha256 FROM local_dev_baseline').fetchone()[0]
            if baseline!=receipt['source_sha256'] or spent<receipt['prior_reserved_microusd']:raise BudgetUnavailable('Dev accounting does not match its reconciled baseline.')
            cap=receipt['cap_microusd']
            expired=bool(receipt['expires_at']) and datetime.fromisoformat(receipt['expires_at'])<=datetime.now(timezone.utc)
            reason='The original dev allowance has expired; paid calls are paused. Existing reservations are preserved.' if expired else (None if spent<cap else 'The approved dev allowance is reserved.')
            return {'ready':not expired and spent<cap,'cap_usd':cap/1e6,'reserved_usd':spent/1e6,'remaining_usd':max(0,cap-spent)/1e6,'expires_at':receipt['expires_at'],'reason':reason}
        except (BudgetUnavailable,sqlite3.Error,TypeError,KeyError) as error:
            return {'ready':False,'cap_usd':2,'reserved_usd':None,'remaining_usd':None,'reason':str(error) if isinstance(error,BudgetUnavailable) else 'Dev accounting is unavailable.'}

    def reserve(self, amount):
        receipt=self.receipt()
        if type(amount) is not int or amount<=0:raise ValueError('Invalid reservation')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                spent=db.execute('SELECT coalesce(sum(reserved_microusd),0) FROM spend').fetchone()[0]
                baseline=db.execute('SELECT source_sha256 FROM local_dev_baseline').fetchone()[0]
                if baseline!=receipt['source_sha256'] or spent<receipt['prior_reserved_microusd']:raise BudgetUnavailable('Dev baseline mismatch')
                if spent+amount>receipt['cap_microusd']:raise BudgetUnavailable('The remaining dev allowance cannot cover this request. Its dispatch was blocked.')
                now=datetime.now(timezone.utc);identifier=uuid4().hex
                db.execute('INSERT INTO sdk_reservations VALUES (?,?,?)',(identifier,now.isoformat(),amount))
                db.execute('INSERT INTO spend VALUES (?,?) ON CONFLICT(month) DO UPDATE SET reserved_microusd=reserved_microusd+excluded.reserved_microusd',(now.strftime('%Y-%m'),amount))
                db.execute('INSERT INTO usage VALUES (?,1) ON CONFLICT(day) DO UPDATE SET attempts=attempts+1',(now.date().isoformat(),))
                db.commit();return identifier
            except BaseException:
                db.rollback();raise

def request_bound(payload):
    # Standard Sonnet 5.5 rates checked 2026-10-29: $2/$10 per million.
    # Reserve at $4 input (covers 1h cache writes), $10 output, plus 10%.
    # UTF-8 bytes conservatively bound text tokens; include framing overhead.
    # Only text/custom tools are allowed; server tools/images have other charges.
    if payload.get('model')!=MODEL:raise ValueError('Unreviewed model')
    if any(k in payload for k in ('speed','service_tier')):raise ValueError('Unreviewed pricing tier')
    for t in payload.get('tools',[]):
        if t.get('type','custom')!='custom':raise ValueError('Server tools are disabled')
    def inspect(value):
        if isinstance(value,dict):
            if value.get('type') in ('image','document','container_upload'):raise ValueError('Only text evidence is supported')
            for item in value.values():inspect(item)
        elif isinstance(value,list):
            for item in value:inspect(item)
    inspect(payload)
    size=len(json.dumps(payload,ensure_ascii=False).encode())
    output=payload.get('max_tokens')
    if size>160000 or type(output) is not int or not 1<=output<=4096:raise ValueError('Provider request exceeds local limits')
    return ((size+16384)*4+output*10)*11//10+1
