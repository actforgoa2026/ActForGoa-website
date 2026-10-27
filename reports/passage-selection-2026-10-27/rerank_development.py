"""Offline development scores on text captured from a disposable corpus copy."""
import json,sys,re,time,hashlib
from pathlib import Path
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));p=ROOT/'.reports/passage-selection';model=p/'reranker'
assert hashlib.sha256((model/'model_qint8_arm64.onnx').read_bytes()).hexdigest()=='3573b6b9593cb2f75987a31815d409ca3dd8808629118fd20451bb1a5d90cec7'
assert hashlib.sha256((model/'tokenizer.json').read_bytes()).hexdigest()=='d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66'
options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
session=ort.InferenceSession(str(model/'model_qint8_arm64.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
tokenizer=Tokenizer.from_file(str(model/'tokenizer.json'));tokenizer.enable_truncation(max_length=384);tokenizer.enable_padding(pad_id=0,pad_token='[PAD]')
a=np.load(p/'representations.npz');vec=dict(zip(a['texts'],a['vectors']));mp=json.loads((p/'representation-map.json').read_text());data=json.loads((p/'scored-candidates.json').read_text());start=time.monotonic()
for rec in data['known_cases']:
 pairs=[];loc=[];query=rec['case']['question'];q=vec[query]
 for row in rec['candidates']:
  title=row['meta'].get('title','');segments=mp['segments'][row['id']];focus=vec[mp['focuses'][rec['case']['id']+':'+row['doc_id']]]
  body=' '.join(row['text'].split())
  # Full passage plus independently selected short evidence spans. Preserve title
  # as context in each pair; all output citations remain complete original slices.
  spans=[body,max(segments,key=lambda s:vec[s]@q),max(segments,key=lambda s:vec[s]@focus)]
  for field,span in zip(['whole','short_full','short_focus'],spans):
   pairs.append((query,title+'\n'+span));loc.append((row,field))
 for i in range(0,len(pairs),8):
  batch=tokenizer.encode_batch(pairs[i:i+8]);inputs={'input_ids':np.array([e.ids for e in batch],dtype=np.int64),'attention_mask':np.array([e.attention_mask for e in batch],dtype=np.int64),'token_type_ids':np.array([e.type_ids for e in batch],dtype=np.int64)}
  logits=session.run(None,{s.name:inputs[s.name] for s in session.get_inputs()})[0].reshape(-1)
  for (row,field),value in zip(loc[i:i+8],logits):row['ce_'+field]=float(value)
 print(rec['case']['id'],round(time.monotonic()-start,1),flush=True)
 (p/'cross-scored-candidates.json').write_text(json.dumps(data))
print('done',time.monotonic()-start)
