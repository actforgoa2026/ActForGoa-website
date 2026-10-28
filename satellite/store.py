"""Private job results and persistent request reservations; single-worker service."""
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sqlite3
import threading
import uuid
from .domain import DomainError


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.RLock()
        self.db.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS quota(day TEXT, operation TEXT, used INTEGER NOT NULL, PRIMARY KEY(day,operation));
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, actor TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL, result TEXT);
        ''')
        self.db.execute("UPDATE jobs SET status='failed', result=? WHERE status='running'", (json.dumps({'error': 'The service restarted. Start a new comparison.', 'code': 'interrupted'}),))
        self.db.execute('DELETE FROM jobs WHERE created < ?', ((datetime.now(timezone.utc)-timedelta(days=30)).isoformat(),))
        self.db.commit()

    def reserve(self, operation, maximum):
        day = datetime.now(timezone.utc).date().isoformat()
        with self.lock, self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT used FROM quota WHERE day=? AND operation=?', (day,operation)).fetchone()
            if row and row[0] >= maximum:
                raise DomainError('daily_limit', 'The satellite service reached its daily request limit. Try after the next UTC day begins.', 429)
            self.db.execute('INSERT INTO quota VALUES(?,?,1) ON CONFLICT(day,operation) DO UPDATE SET used=used+1', (day,operation))

    def start(self, actor):
        job = str(uuid.uuid4())
        with self.lock, self.db:
            self.db.execute('INSERT INTO jobs VALUES(?,?,?,?,NULL)', (job,actor,'running',datetime.now(timezone.utc).isoformat()))
        return job

    def finish(self, job, result, failed=False):
        with self.lock, self.db:
            self.db.execute('UPDATE jobs SET status=?,result=? WHERE id=?', ('failed' if failed else 'complete',json.dumps(result,allow_nan=False),job))

    def get(self, job, actor):
        with self.lock:
            row = self.db.execute('SELECT status,created,result FROM jobs WHERE id=? AND actor=?', (job,actor)).fetchone()
        if not row:
            raise DomainError('not_found', 'Comparison not found for this account.', 404)
        return {'id':job,'status':row[0],'created_at':row[1],'result':json.loads(row[2]) if row[2] else None}

    def close(self):
        self.db.close()
