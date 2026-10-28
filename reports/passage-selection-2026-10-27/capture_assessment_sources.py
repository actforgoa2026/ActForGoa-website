"""Source inspection for a fresh frozen assessment, without retrieval queries."""
import argparse,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.evaluate_research_copy import is_preserved

def protected(path):
    return is_preserved(path) or Path(path).resolve().is_relative_to(Path.home()/'Documents/ActForGoa Recovery')
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if protected(a.data_root) or protected(a.output):p.error('Use disposable-copy wrapper')
from backend.library import Library
library=Library(a.data_root);docs=[]
for doc_id in ['5374dd62fd73bd8f3dac0ff4-d9b098c6e83c','4feaf0959f7e282012f02efd-23ae7783e3e8','1ab326b64c72218272d9ecd2-d743fb422534','065ad37b84bdfb0354f1c42f-663da92d89f4']:
 path,meta=library.original(doc_id);assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256']
 with library.connect() as db:chunks=[dict(r) for r in db.execute('SELECT * FROM chunks WHERE doc_id=? ORDER BY page,start',(doc_id,))]
 docs.append({'metadata':meta,'chunks':chunks})
a.output.write_text(json.dumps({'generation':library.generation,'documents':docs,'queries_run':0},indent=2)+'\n')
print('Captured 4 sources, no queries run')
