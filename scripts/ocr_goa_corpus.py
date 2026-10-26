"""Optional bounded, single-worker English OCR; native extraction remains unchanged."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
from ingest_goa_corpus import ROOT,C,dump,now
ap=argparse.ArgumentParser();ap.add_argument('--max-pages',type=int,default=60);ap.add_argument('--max-document-pages',type=int,default=15);a=ap.parse_args()
for binary in ['pdftoppm','tesseract']:
 if not shutil.which(binary):ap.error(f'{binary} is required')
(C/'ocr').mkdir(exist_ok=True)
rows=[json.loads(p.read_text()) for p in (C/'metadata').glob('*.json')]
rows=[r for r in rows if r.get('format')=='pdf' and r.get('extraction_status')=='needs_ocr' and r.get('page_count',999)<=a.max_document_pages and not r.get('ocr_pages_path') and (r['publisher_class']!='act_for_goa' or 'Charter' in r.get('title',''))]
rows.sort(key=lambda r:(0 if 'tcp.goa' in r['url'] else 1,r.get('page_count',999)))
count=0;env={**os.environ,'OMP_THREAD_LIMIT':'1'}
for r in rows:
 if count+r['page_count']>a.max_pages:continue
 results=[]
 for n in range(1,r['page_count']+1):
  with tempfile.TemporaryDirectory(prefix='goa-corpus-ocr-') as tmp:
   prefix=Path(tmp)/'page'
   try:
    subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-r','160','-gray','-scale-to','2400','-singlefile','-png',str(ROOT/r['raw_path']),str(prefix)],check=True,capture_output=True,timeout=60)
    out=subprocess.run(['tesseract',str(prefix)+'.png','stdout','-l','eng','--psm','3'],check=True,capture_output=True,text=True,timeout=60,env=env)
    results.append({'page':n,'text':out.stdout,'method':'tesseract eng psm3, 160dpi raster capped at 2400px','quality':'machine OCR, not verified; non-English content may be unreadable'})
   except Exception as e:results.append({'page':n,'text':'','error':str(e)[:300]})
  count+=1
  print(f'{count}: {r["id"]} page {n}/{r["page_count"]}',flush=True)
 path=C/'ocr'/f'{r["id"]}.json';dump(path,results)
 # Re-read so independent metadata enrichment is not clobbered.
 mp=C/'metadata'/f'{r["id"]}.json';updated=json.loads(mp.read_text());updated.update(ocr_pages_path=str(path.relative_to(ROOT)),ocr_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),ocr_at=now(),ocr_status='machine_ocr_unverified',ocr_language='eng',ocr_pages_completed=sum(bool(x['text'].strip()) for x in results))
 dump(mp,updated)
print(json.dumps({'ocr_pages_attempted':count,'language':'eng','parallel_workers':1}),flush=True)
