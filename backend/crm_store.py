"""Complete public CRM snapshot with read-only, paginated agent access."""
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import os

STATE=Path(os.getenv('ACTFORGOA_CRM_STATE','/workspace/.research-private/crm'))
STOP=set('a an and are at can do for from help how i in is me of on or please the to us what where which who with'.split())

def build_index(snapshot=STATE/'snapshot.json',destination=STATE/'crm.sqlite'):
    snapshot=Path(snapshot);destination=Path(destination)
    raw=snapshot.read_bytes();data=json.loads(raw)
    records=data['records'];ids=[r['record_id'] for r in records]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate CRM record identities')
    if not records or any(r['collection'] not in ('community','government') for r in records):raise ValueError('Invalid CRM snapshot')
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=destination.with_suffix('.building.sqlite')
    if temporary.exists():temporary.unlink()
    with sqlite3.connect(temporary) as db:
        db.execute('CREATE TABLE records(id TEXT PRIMARY KEY, collection TEXT NOT NULL, name TEXT NOT NULL, location TEXT NOT NULL, body TEXT NOT NULL)')
        db.execute('CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,name,organization,location,topics,description,tokenize="unicode61")')
        db.execute('CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT)')
        for record in records:
            location=' '.join(record.get(k,'') for k in ('goa_location','jurisdiction'))
            description=' '.join(record.get(k,'') for k in ('summary','role','how_to_help','referral_route','activity_verification_notes','notes'))
            db.execute('INSERT INTO records VALUES(?,?,?,?,?)',(record['record_id'],record['collection'],record['name'],location,json.dumps(record,ensure_ascii=False)))
            db.execute('INSERT INTO search VALUES(?,?,?,?,?,?)',(record['record_id'],record['name'],record.get('organization',''),location,record.get('focus_areas',''),description))
        metadata={'version':data['version'],'sha256':hashlib.sha256(raw).hexdigest(),'source_url':'https://actforgoa-field-guide.vercel.app/data/crm.json','records':len(records),'community':sum(r['collection']=='community' for r in records),'government':sum(r['collection']=='government' for r in records)}
        db.executemany('INSERT INTO metadata VALUES(?,?)',[(key,json.dumps(value)) for key,value in metadata.items()])
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('CRM index integrity failure')
    temporary.chmod(0o444);temporary.replace(destination)
    return metadata

def connect():
    if not (STATE/'crm.sqlite').is_file():raise FileNotFoundError('Full CRM index is not restored')
    db=sqlite3.connect((STATE/'crm.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    db.create_function('place_match',2,lambda value,place:bool(re.search(r'(?<!\w)'+re.escape(place)+r'(?!\w)',value or '',re.I)))
    return db

def stats():
    with connect() as db:return {row['key']:json.loads(row['value']) for row in db.execute('SELECT key,value FROM metadata')}

def search_records(query='',collection='community',location='',limit=20,offset=0):
    if collection not in ('community','government','all'):raise ValueError('Unknown collection')
    limit=min(100,max(1,int(limit)));offset=max(0,int(offset))
    terms=list(dict.fromkeys(t.lower() for t in re.findall(r'[^\W_]+',query,re.UNICODE) if t.lower() not in STOP))[:20]
    match=' OR '.join('"'+term+'"' for term in terms)
    clauses=[];parameters=[]
    if match:clauses.append('search MATCH ?');parameters.append(match)
    if collection!='all':clauses.append('r.collection=?');parameters.append(collection)
    if location:clauses.append('(place_match(r.location,?) OR place_match(r.name,?))');parameters.extend([location.strip()]*2)
    where=' WHERE '+' AND '.join(clauses) if clauses else ''
    join='records r JOIN search ON search.id=r.id' if match else 'records r'
    order='bm25(search,0,6,4,2,4,1),r.name' if match else 'r.name'
    with connect() as db:
        total=db.execute('SELECT count(*) FROM '+join+where,parameters).fetchone()[0]
        rows=db.execute('SELECT r.body FROM '+join+where+' ORDER BY '+order+' LIMIT ? OFFSET ?',parameters+[limit,offset]).fetchall()
    records=[json.loads(row['body']) for row in rows]
    return {'records':records,'total_matches':total,'next_offset':offset+len(records) if offset+len(records)<total else None,'collection':collection,'snapshot':stats()}

def read_record(record_id):
    with connect() as db:row=db.execute('SELECT body FROM records WHERE id=?',(record_id,)).fetchone()
    if not row:raise KeyError('CRM record not found')
    return {'record':json.loads(row['body']),'crm_url':'/directory/'+record_id,'snapshot':stats()}
