"""Private job results and persistent request reservations; single-worker service."""
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sqlite3
import threading
import uuid
from .domain import DomainError
from .evidence_query import spatial_match
from shapely.geometry import shape


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.RLock()
        self.db.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS quota(day TEXT, operation TEXT, used INTEGER NOT NULL, PRIMARY KEY(day,operation));
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, actor TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL, result TEXT);
        CREATE TABLE IF NOT EXISTS observations(actor TEXT NOT NULL, cache_key TEXT NOT NULL, created TEXT NOT NULL,
            spectral BLOB NOT NULL, provenance TEXT NOT NULL, PRIMARY KEY(actor,cache_key));
        ''')
        if 'request' not in {row[1] for row in self.db.execute('PRAGMA table_info(jobs)')}:
            self.db.execute('ALTER TABLE jobs ADD COLUMN request TEXT')
        self.db.execute("UPDATE jobs SET status='failed', result=? WHERE status='running'", (json.dumps({'error': 'The service restarted. Start a new comparison.', 'code': 'interrupted'}),))
        self.db.execute('DELETE FROM jobs WHERE created < ?', ((datetime.now(timezone.utc)-timedelta(days=30)).isoformat(),))
        self._prune_observation_jobs()
        self._prune_observations()
        self.db.commit()

    def _prune_observation_jobs(self):
        # These jobs are transport envelopes for timeline retrieval, not saved
        # investigations. The reusable raw cache has its own 30-day retention.
        self.db.execute("DELETE FROM jobs WHERE json_extract(request,'$.kind')='observation' AND created<?",
                        ((datetime.now(timezone.utc)-timedelta(days=1)).isoformat(),))

    def _prune_observations(self):
        self.db.execute('DELETE FROM observations WHERE created < ?',
                        ((datetime.now(timezone.utc)-timedelta(days=30)).isoformat(),))
        # Bound retained raw imagery as well as age. Oldest entries are discarded
        # before a new browser request can grow the cache without limit.
        rows = self.db.execute('SELECT actor,cache_key,length(spectral) FROM observations ORDER BY created DESC,actor,cache_key').fetchall()
        total = 0
        for index, (actor, key, size) in enumerate(rows):
            total += size
            if index >= 60 or total > 128 * 1024 * 1024:
                self.db.execute('DELETE FROM observations WHERE actor=? AND cache_key=?', (actor, key))

    def observation(self, actor, key):
        with self.lock:
            row = self.db.execute('SELECT spectral,provenance,created FROM observations WHERE actor=? AND cache_key=? AND created>=?',
                (actor, key, (datetime.now(timezone.utc)-timedelta(days=30)).isoformat())).fetchone()
        if row is None:
            return None
        return row[0], json.loads(row[1]), row[2]

    def cache_observation(self, actor, key, spectral, provenance):
        if len(spectral) > 16_000_000:
            raise DomainError('imagery_too_large', 'This observation exceeds the retained imagery limit.', 502)
        with self.lock, self.db:
            self.db.execute('INSERT OR REPLACE INTO observations VALUES(?,?,?,?,?)',
                (actor, key, datetime.now(timezone.utc).isoformat(), spectral, json.dumps(provenance, allow_nan=False)))
            self._prune_observations()

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
            self._prune_observation_jobs()
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
        clauses, values = ['actor=?','created>=?', "coalesce(json_extract(request,'$.kind'),'comparison')!='observation'"], [actor,(datetime.now(timezone.utc)-timedelta(days=30)).isoformat()]
        if query.intent:
            clauses.append("json_extract(request,'$.intent')=?"); values.append(query.intent.value)
        if query.query.strip():
            clauses.append("(coalesce(json_extract(request,'$.question'),'') || ' ' || coalesce(json_extract(result,'$.summary.headline'),'') || ' ' || coalesce((SELECT group_concat(json_extract(value,'$.text'),' ') FROM json_each(jobs.result,'$.summary.statements')),'')) LIKE ? ESCAPE '\\'")
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
                [*values,301 if query.area else query.limit+1,0 if query.area else query.offset]).fetchall()
        items=[]
        scan_truncated = bool(query.area and len(rows) > 300)
        selected = shape(query.area.grid()['geometry']) if query.area else None
        for row in rows[:300] if query.area else rows:
            parsed=[json.loads(value) if value and index<4 else value for index,value in enumerate(row[4:])]
            item={'id':row[0],'status':row[1],'created_at':row[2], 'request':json.loads(row[3]) if row[3] else None,
                **dict(zip(columns,parsed))}
            if selected is not None:
                match = spatial_match(selected, item['request'], item['area'])
                if match is None:
                    continue
                item['spatial'] = match
            items.append(item)
        page = items[query.offset:query.offset+query.limit] if query.area else items[:query.limit]
        has_more = len(items) > (query.offset+query.limit if query.area else query.limit)
        return {'items':page,'next_offset':query.offset+query.limit if has_more else None,
                'scan_truncated':scan_truncated,
                'retention_days':30,'scope':'Your saved investigations only; not statewide monitoring coverage.'}

    def evidence_rows(self, actor, query):
        """Extract bounded metadata in SQLite; never deserialize image bodies."""
        clauses = ['actor=?', "status='complete'", 'created>=?',
                   "coalesce(json_extract(request,'$.kind'),'comparison')!='observation'",
                   "julianday(json_extract(result,'$.observation_interval.after'))>=julianday(?)",
                   "julianday(json_extract(result,'$.observation_interval.before'))<julianday(?)"]
        values = [actor, (datetime.now(timezone.utc)-timedelta(days=30)).isoformat(),
                  query.start_date.isoformat()+'T00:00:00+05:30',
                  (query.end_date+timedelta(days=1)).isoformat()+'T00:00:00+05:30']
        if query.intent:
            clauses.append("json_extract(request,'$.intent')=?")
            values.append(query.intent.value)
        columns = {'summary':20000, 'observation_interval':2000, 'area':100000,
                   'evidence.state':100, 'evidence.common_usable_fraction':40,
                   'evidence.metrics':3000, 'evidence.water_change':3000, 'evidence.candidates_truncated':10,
                   'canopy_presence':4000, 'classification.state':100, 'classification.provider':100,
                   'classification.model':200, 'classification.answers':3000, 'classification.scope':4000,
                   'before.catalog_scene_id':250, 'after.catalog_scene_id':250,
                   'before.acquired_at':2000, 'after.acquired_at':2000}
        extracts = []
        for name, maximum in columns.items():
            field = "json_extract(result,'$." + name + "')"
            if name == 'area':
                extracts.append(f'CASE WHEN {field} IS NULL THEN NULL WHEN length({field})<={maximum} THEN {field} ELSE \'{{"geometry":null}}\' END')
            else:
                extracts.append(f'CASE WHEN length({field})<={maximum} THEN {field} ELSE NULL END')
        extracts.append("json_array_length(result,'$.evidence.candidates.features')")
        object_fields = {'summary','observation_interval','area','evidence.metrics','evidence.water_change','canopy_presence',
                         'classification.answers','classification.scope','before.acquired_at','after.acquired_at'}
        with self.lock:
            rows = self.db.execute('SELECT id,created,request,' + ','.join(extracts) +
                ' FROM jobs WHERE ' + ' AND '.join(clauses) + ' ORDER BY created DESC,id DESC LIMIT 301', values).fetchall()
        records = []
        for row in rows[:300]:
            data = {name: json.loads(value) if name in object_fields and value is not None else value
                    for name, value in zip(columns, row[3:-1])}
            records.append({'id':row[0], 'created_at':row[1], 'request':json.loads(row[2]) if row[2] else None,
                            **data, 'vegetation_candidate_count':row[-1]})
        return records, len(rows)>300

    def close(self):
        self.db.close()
