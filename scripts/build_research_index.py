"""Build an immutable full-text + Zvec generation, publishing only on success."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import zvec
from backend.embeddings import Encoder, ROOT
from backend.extraction import extract_source, VERSION, text_quality_warning
from backend.domains import document_domains

def build(root=ROOT, index_root=None, ecology_only=False, ocr_pages=40):
    root=Path(root); index=Path(index_root or root/'.research-index')
    index.mkdir(parents=True,exist_ok=True)
    generation=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    out=index/'generations'/generation;out.mkdir(parents=True)
    encoder=Encoder()
    cache=sqlite3.connect(index/'embeddings.sqlite')
    cache.execute('CREATE TABLE IF NOT EXISTS vectors (key TEXT PRIMARY KEY, vector BLOB NOT NULL)')
    db=sqlite3.connect(out/'library.sqlite')
    db.executescript('''
    CREATE TABLE documents(id TEXT PRIMARY KEY, metadata TEXT NOT NULL);
    CREATE TABLE pages(doc_id TEXT, page INTEGER, label TEXT, text TEXT, origin TEXT, warning TEXT, PRIMARY KEY(doc_id,page));
    CREATE TABLE chunks(id TEXT PRIMARY KEY, doc_id TEXT, page INTEGER, start INTEGER, end INTEGER, text TEXT, origin TEXT);
    CREATE INDEX chunk_document ON chunks(doc_id);
    CREATE VIRTUAL TABLE passages USING fts5(id UNINDEXED, title, text, tokenize='unicode61');
    ''')
    vectors=zvec.create_and_open(str(out/'zvec'),zvec.CollectionSchema(name='research',
        fields=[zvec.FieldSchema('document',zvec.DataType.STRING)],
        vectors=[zvec.VectorSchema('embedding',zvec.DataType.VECTOR_FP32,dimension=384,
            index_param=zvec.HnswIndexParam(metric_type=zvec.MetricType.COSINE))]))
    seed_path=root/'corpus/ecology-seeds.json'
    seeds={s['url'] for s in json.loads(seed_path.read_text())} if seed_path.exists() else set()
    records=[json.loads(p.read_text()) for p in sorted((root/'corpus/metadata').glob('*.json'))]
    # Fully scanned, short ecological documents get OCR before image-only covers in long reports.
    records.sort(key=lambda r:(r['url'] not in seeds,not (r.get('extraction_status')=='needs_ocr' and r.get('page_count',999)<=50),r.get('title','')))
    seen=set();errors=[];stats=Counter();budget=[ocr_pages];pending=[]
    def flush():
        if not pending:return
        keys=[hashlib.sha256((encoder.fingerprint+text).encode()).hexdigest() for _,text in pending]
        values=[cache.execute('SELECT vector FROM vectors WHERE key=?',(key,)).fetchone() for key in keys]
        missing=[i for i,v in enumerate(values) if not v]
        if missing:
            embedded=encoder.encode([pending[i][1] for i in missing])
            for i, vector in zip(missing,embedded):
                values[i]=(vector.tobytes(),);cache.execute('INSERT OR REPLACE INTO vectors VALUES(?,?)',(keys[i],vector.tobytes()))
        docs=[zvec.Doc(id=row['id'], fields={'document':row['doc_id']},
            vectors={'embedding':np.frombuffer(value[0],dtype=np.float32).tolist()}) for (row,_),value in zip(pending,values)]
        result=vectors.insert(docs)
        if result and any(not status.ok() for status in result):
            raise RuntimeError('Zvec insertion failed')
        cache.commit();pending.clear()
    for r in records:
        if r.get('status') not in ('downloaded','authored') or r.get('inclusion_status','').startswith('excluded') or r.get('extraction_status')=='blocked_html':continue
        if ecology_only and r['url'] not in seeds:continue
        if r['sha256'] in seen:stats['duplicate_urls']+=1;continue
        try:
            doc_id,pages=extract_source(root,r,improve=r['url'] in seeds,ocr_budget=budget)
        except Exception as error:
            errors.append({'source_id':r['id'],'url':r['url'],'error':str(error)[:300]});continue
        seen.add(r['sha256'])
        metadata={**r,'id':doc_id,'source_id':r['id'],'extraction_version':VERSION,'page_count':len(pages),
                  'page_labels':'physical_pdf_pages' if r.get('format')=='pdf' else 'document_sections',
                  'quality':{'low_text_pages':sum(len(p['text'].strip())<60 for p in pages),'ocr_pages':sum(p['origin'].startswith('ocr') for p in pages)},
                  'ecology_source':r['url'] in seeds,'aliases':[{'url':a['url'],'title':a.get('title')} for a in records if a.get('sha256')==r['sha256']]}
        metadata['domains']=document_domains(metadata)
        db.execute('INSERT INTO documents VALUES(?,?)',(doc_id,json.dumps(metadata)))
        for page in pages:
            quality_warning=text_quality_warning(page['text'])
            if quality_warning:page['warning']=quality_warning
            db.execute('INSERT INTO pages VALUES(?,?,?,?,?,?)',(doc_id,page['page'],page['label'],page['text'],page['origin'],page['warning']))
            stats['pages']+=1;stats['low_text_pages']+=len(page['text'].strip())<60;stats['ocr_pages']+=page['origin'].startswith('ocr')
            if quality_warning:stats['corrupt_pages_excluded_from_search']+=1;continue
            for left,right,text in encoder.chunks(page['text']):
                chunk_id=hashlib.sha256(f'{doc_id}:{page["page"]}:{left}:{right}'.encode()).hexdigest()[:32]
                row={'id':chunk_id,'doc_id':doc_id,'page':page['page']}
                db.execute('INSERT INTO chunks VALUES(?,?,?,?,?,?,?)',(chunk_id,doc_id,page['page'],left,right,text,page['origin']))
                db.execute('INSERT INTO passages VALUES(?,?,?)',(chunk_id,r.get('title',''),text))
                # Body first: never truncate evidence merely to fit a long document title.
                pending.append((row,text));stats['chunks']+=1
                if len(pending)>=24:flush()
        stats['documents']+=1
        if stats['documents']%10==0:
            db.commit();print(json.dumps(dict(stats)),flush=True)
    flush();vectors.optimize();vectors.flush();del vectors
    db.commit()
    assert db.execute('SELECT count(*) FROM chunks').fetchone()[0]==stats['chunks']
    db.close();cache.close()
    manifest={'generation':generation,'created_at':datetime.now(timezone.utc).isoformat(),'encoder':'all-MiniLM-L6-v2 quantized, mean pooling, normalized',
              'encoder_sha256':encoder.fingerprint,'extraction_version':VERSION,'stats':dict(stats),'errors':errors,
              'scope':'ecology' if ecology_only else 'full_corpus','ocr_attempts':ocr_pages-budget[0]}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    if not stats['chunks']:raise RuntimeError('No searchable passages; previous generation retained')
    temp=index/'CURRENT.tmp';temp.write_text(json.dumps({'generation':generation}));temp.replace(index/'CURRENT.json')
    print(json.dumps(manifest,indent=2),flush=True)
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ecology-only',action='store_true');parser.add_argument('--ocr-pages',type=int,default=40)
    parser.add_argument('--data-root',type=Path,default=ROOT);parser.add_argument('--index-root',type=Path)
    args=parser.parse_args();build(root=args.data_root,index_root=args.index_root,ecology_only=args.ecology_only,ocr_pages=args.ocr_pages)
