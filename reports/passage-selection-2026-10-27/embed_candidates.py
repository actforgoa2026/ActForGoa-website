"""Development-only representations of captured text, with no index or provider access."""
import json,sys,re,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from backend.embeddings import Encoder
p=ROOT/'.reports/passage-selection';data=json.loads((p/'capture.json').read_text())
encoder=Encoder(); texts=set(); segments={}; focuses={}
for record in data['known_cases']:
 texts.add(record['case']['question'])
 for row in record['candidates']:
  title=row['meta'].get('title','');texts.add(title)
  # Short overlapping spans let answer-bearing text survive long OCR/table prefixes.
  words=re.findall(r'\S+',row['text']); wins=[' '.join(words[i:i+64]) for i in range(0,len(words),48)]
  segments[row['id']]=wins;texts.update(wins)
  tt=set(re.findall(r'[^\W_]+',title.lower()));focus=' '.join(t for t in record['terms'] if t not in tt)
  focuses[record['case']['id']+':'+row['doc_id']]=focus;texts.add(focus)
texts=sorted(texts);vectors=[];started=time.monotonic()
for i in range(0,len(texts),32):
 vectors.extend(encoder.encode(texts[i:i+32]))
 if i%512==0:print(f'{i}/{len(texts)}',flush=True)
np.savez_compressed(p/'representations.npz',texts=texts,vectors=np.array(vectors))
(p/'representation-map.json').write_text(json.dumps({'segments':segments,'focuses':focuses,'model_sha256':encoder.fingerprint,'seconds':time.monotonic()-started}))
print('complete',time.monotonic()-started)
