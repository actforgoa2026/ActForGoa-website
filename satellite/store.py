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
        if 'request' not in {row[1] for row in self.db.execute('PRAGMA table_info(jobs)')}:
            self.db.execute('ALTER TABLE jobs ADD COLUMN request TEXT')
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

    def start(self, actor, request=None):
        job = str(uuid.uuid4())
        with self.lock, self.db:
            self.db.execute('DELETE FROM jobs WHERE created < ?',((datetime.now(timezone.utc)-timedelta(days=30)).isoformat(),))
            self.db.execute('INSERT INTO jobs(id,actor,status,created,result,request) VALUES(?,?,?,?,NULL,?)',
                (job,actor,'running',datetime.now(timezone.utc).isoformat(),json.dumps(request) if request else None))
        return job

    def finish(self, job, result, failed=False):
        with self.lock, self.db:
            self.db.execute('UPDATE jobs SET status=?,result=? WHERE id=?', ('failed' if failed else 'complete',json.dumps(result,allow_nan=False),job))

    def get(self, job, actor):
        with self.lock:
            row = self.db.execute('SELECT status,created,result,request FROM jobs WHERE id=? AND actor=?', (job,actor)).fetchone()
        if not row:
            raise DomainError('not_found', 'Comparison not found for this account.', 404)
        return {'id':job,'status':row[0],'created_at':row[1],'result':json.loads(row[2]) if row[2] else None,
                'request':json.loads(row[3]) if row[3] else None}

    def history(self, actor, query):
        clauses, values = ['actor=?','created>=?'], [actor,(datetime.now(timezone.utc)-timedelta(days=30)).isoformat()]
        if query.intent:
            clauses.append("json_extract(request,'$.intent')=?"); values.append(query.intent.value)
        if query.query.strip():
            clauses.append("(coalesce(json_extract(request,'$.question'),'') || ' ' || coalesce(json_extract(result,'$.summary.headline'),'')) LIKE ? ESCAPE '\\'")
            term=query.query.strip().replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
            values.append('%'+term+'%')
        # Filter the actual observation interval, not the date the job was run.
        if query.start_date:
            clauses.append("julianday(json_extract(result,'$.observation_interval.after'))>=julianday(?)")
            values.append(query.start_date.isoformat()+'T00:00:00+05:30')
        if query.end_date:
            clauses.append("julianday(json_extract(result,'$.observation_interval.before'))<julianday(?)")
            values.append((query.end_date+timedelta(days=1)).isoformat()+'T00:00:00+05:30')
        # Select only small metadata fields: history never loads all saved PNGs.
        columns = ['summary','observation_interval','freshness','area','evidence.common_usable_fraction',
                   'canopy_presence.state','classification.state','error']
        extracts=','.join("json_extract(result,'$."+key+"')" for key in columns)
        with self.lock:
            rows=self.db.execute('SELECT id,status,created,request,'+extracts+' FROM jobs WHERE '+
                ' AND '.join(clauses)+' ORDER BY created DESC,id DESC LIMIT ? OFFSET ?',
                [*values,query.limit+1,query.offset]).fetchall()
        items=[]
        for row in rows[:query.limit]:
            parsed=[json.loads(value) if value and index<4 else value for index,value in enumerate(row[4:])]
            items.append({'id':row[0],'status':row[1],'created_at':row[2], 'request':json.loads(row[3]) if row[3] else None,
                **dict(zip(columns,parsed))})
        return {'items':items,'next_offset':query.offset+query.limit if len(rows)>query.limit else None,
                'retention_days':30,'scope':'Your saved investigations only; not statewide monitoring coverage.'}

    def close(self):
        self.db.close()
