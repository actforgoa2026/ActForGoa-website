"""Capture all known development questions on a guarded disposable copy."""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.evaluate_research_copy import is_preserved

def protected(path):
    return is_preserved(path) or Path(path).resolve().is_relative_to(Path.home()/'Documents/ActForGoa Recovery')
p=argparse.ArgumentParser(); p.add_argument('--data-root',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
if protected(a.data_root) or protected(a.output):p.error('Use the disposable-copy wrapper')
from backend.library import Library
from scripts.evaluate_research import CASES
original=json.loads((ROOT/'reports/recovery-2026-10-27/retrieval-evidence-cases.json').read_text())
prior=json.loads((ROOT/'reports/rti-offline-2026-10-27/held-out-cases.json').read_text())
frozen=json.loads((ROOT/'reports/evidence-selection-2026-10-27/frozen-cases.json').read_text())
cases=[{**c,'group':'original'} for c in original['cases']]
cases += [{**c,'group':'prior','fee_id':prior['cases'][0]['required_any_of'][0], 'required_evidence':[{'any_of':c['required_any_of']}]} for c in prior['cases']]
cases += [{**c,'group':'previous_frozen'} for c in frozen['cases']]
cases += [{'id':f'smoke-{i}','question':q,'terms':t,'group':'smoke'} for i,(q,t) in enumerate(CASES)]
library=Library(a.data_root); results=[]
for case in cases:
 captured={}
 def capture(frame,event,_):
  if event=='return' and frame.f_code is Library.search.__code__:
   v=frame.f_locals
   captured.update(terms=v['terms'],generation=v['generation'], candidates=[{**dict(row),'meta':meta,'baseline_score':v['relevance'](identifier),'rrf':v['scores'][identifier],'channels':v['channels'][identifier]} for identifier,(row,meta) in v['candidates'].items()])
 sys.setprofile(capture)
 try:hits=library.search(case['question'],8 if case['group']=='smoke' else 10)
 finally:sys.setprofile(None)
 results.append({'case':case,'hits':hits,**captured})
with library.connect() as db:
 expected={i for c in cases for g in c.get('required_evidence',[]) for i in g['any_of']}
 doc_ids={db.execute('SELECT doc_id FROM chunks WHERE id=?',(i,)).fetchone()[0] for i in expected}
 docs=[]
 for doc_id in sorted(doc_ids):
  meta=library.document(doc_id,private=True); path,_=library.original(doc_id)
  assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256']
  rows=[dict(r) for r in db.execute('SELECT * FROM chunks WHERE doc_id=? ORDER BY page,start',(doc_id,))]
  docs.append({'metadata':meta,'chunks':rows})
a.output.write_text(json.dumps({'generation':library.generation,'known_cases':results,'source_documents':docs},indent=2)+'\n')
print(json.dumps({'cases':len(cases),'source_documents':len(docs)}))
