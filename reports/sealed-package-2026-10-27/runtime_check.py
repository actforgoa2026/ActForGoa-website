import argparse,hashlib,json,sqlite3,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--service-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
for candidate in (a.data_root, a.service_root, a.output):
 resolved=candidate.resolve()
 if any((parent/marker).is_file() for parent in (resolved,*resolved.parents) for marker in ('snapshot-files.json','seal.json')):
  p.error('Native checks require disposable data and service copies, with reports outside preservation roots')
sys.path.insert(0,str(a.service_root.resolve()))
import backend.library,zvec,pymupdf
from backend.library import Library
assert Path(backend.library.__file__).resolve().is_relative_to(a.service_root.resolve())
started=time.monotonic();lib=Library(a.data_root);checks=[];raw_hashes={}
for folder in sorted((a.data_root/'.research-index/generations').iterdir()):
 gen=folder.name
 with lib.connect(gen) as db:
  assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  docs=[json.loads(r[0]) for r in db.execute('SELECT metadata FROM documents')]
  page_count=db.execute('SELECT count(*) FROM pages').fetchone()[0];chunk_count=db.execute('SELECT count(*) FROM chunks').fetchone()[0]
  assert db.execute('SELECT count(*) FROM passages').fetchone()[0]==chunk_count
  key=None;page_text=None;count=0
  for row in db.execute('SELECT * FROM chunks ORDER BY doc_id,page,start'):
   page_key=(row['doc_id'],row['page'])
   if page_key!=key:
    page=db.execute('SELECT text FROM pages WHERE doc_id=? AND page=?',page_key).fetchone();assert page is not None
    page_text=page['text'];key=page_key
   assert page_text[row['start']:row['end']]==row['text'];count+=1
  assert count==chunk_count
  vector_rows=list(db.execute('SELECT id,doc_id FROM chunks'))
 for doc in docs:
  original,_=lib.original(doc['id'],gen)
  if doc['raw_path'] not in raw_hashes:
   with original.open('rb') as f:raw_hashes[doc['raw_path']]=hashlib.file_digest(f,'sha256').hexdigest()
  assert raw_hashes[doc['raw_path']]==doc['sha256']
 collection=zvec.open(str(folder/'zvec'),option=zvec.CollectionOption(read_only=True))
 assert collection.stats.doc_count==chunk_count
 for offset in range(0,len(vector_rows),256):
  batch=vector_rows[offset:offset+256];fetched=collection.fetch([r['id'] for r in batch],include_vector=False)
  assert set(fetched)=={r['id'] for r in batch}
  assert all(fetched[r['id']].fields['document']==r['doc_id'] for r in batch)
 del collection
 hits=lib.search('How do khazan sluice gates manage saline water?',8,generation=gen)
 assert hits and any(set(h['matches'])=={'keyword','semantic'} for h in hits)
 for h in hits:
  page=lib.pages(h['document_id'],gen,h['page'],1)[0]
  assert page['text'][h['start']:h['end']]==h['text']
 checks.append({'generation':gen,'documents':len(docs),'pages':page_count,'chunks':chunk_count,'sqlite_integrity':'ok','exact_slices_verified':count,'vector_ids_and_document_fields_verified':len(vector_rows),'hybrid_probe_passed':True,'sqlite_sha256':hashlib.sha256((folder/'library.sqlite').read_bytes()).hexdigest()})
readers=[]
for doc_id,gen in [('2e0577bc1234b3edf3cd31d8-d413eb87182d',lib.generation),('493ffb4c35a00be1f1f28e9b-c9efabb977ca',lib.generation),('493ffb4c35a00be1f1f28e9b-91ac6cb7fd84','20261022T155701-21661179')]:
 doc=lib.document(doc_id,gen);pages=lib.pages(doc_id,gen,1,doc['page_count']);assert len(pages)==doc['page_count'] and pages[-1]['page']==doc['page_count']
 path,_=lib.original(doc_id,gen)
 with pymupdf.open(path) as pdf:
  assert len(pdf)==doc['page_count'];pdf[-1].get_pixmap(matrix=pymupdf.Matrix(.25,.25))
 readers.append({'document_id':doc_id,'generation':gen,'pages_read':len(pages),'original_and_last_page_accessible':True})
report={'packaged_backend_imported':True,'generation':lib.generation,'generations':checks,'unique_originals_verified':len(raw_hashes),'document_reader_checks':readers,'encoder_sha256':lib.encoder.fingerprint,'seconds':round(time.monotonic()-started,3),'provider_calls':0,'app_or_usage_initialized':False,'scope':'All native access was confined to disposable data and service copies. Parent verifies preserved sources after this process exits.'}
assert not (a.data_root/'.research-usage').exists()
a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'generations':len(checks),'originals':len(raw_hashes),'exact_slices':sum(x['chunks'] for x in checks)}))
