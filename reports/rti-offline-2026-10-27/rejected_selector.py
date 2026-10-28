"""Rejected offline selection experiment; never imported by runtime code.

Preserve document slots and the first chosen passage. Use a second slot for
query concepts missing from the first passage, weighted by rarity within that
document's candidate pool. Prefer query terms outside the document title when
ordering that pair. This fails a held-out farming case and is not adopted.
"""
import math,re
from urllib.parse import urlencode
from collections import Counter
from backend.library import page_heading

def concepts(text):
 return {w[:5] if len(w)>5 else w for w in re.findall(r'[^\W_]+',text.lower(),re.UNICODE)}

def revise(record):
 output=[dict(h) for h in record['baseline']];by_doc={};changes=[]
 for n,h in enumerate(output):by_doc.setdefault(h['document_id'],[]).append(n)
 for doc,positions in by_doc.items():
  if len(positions)<2:continue
  first,second=positions[:2];pool=[c for c in record['candidates'] if c['doc_id']==doc]
  tokens={c['id']:concepts(c['text']) for c in pool};df=Counter(t for ts in tokens.values() for t in ts)
  uncovered=set(record['concepts'])-concepts(output[first]['text'])
  def gain(c):return sum(1+math.log((len(pool)+1)/(df[t]+1)) for t in uncovered & tokens[c['id']])
  ranked=sorted([c for c in pool if c['id']!=output[first]['id']],key=lambda c:(gain(c),c['score']),reverse=True)
  old=next(c for c in pool if c['id']==output[second]['id'])
  if not ranked or gain(ranked[0])<=gain(old):continue
  new=ranked[0];h=output[second];changes.append({'document':h['title'],'old_page':h['page'],'new_page':new['page'],'old_gain':gain(old),'new_gain':gain(new)})
  h.update({k:new[k] for k in ['id','page','label','start','end','text','origin','warning']});h['page_heading']=page_heading(new['page_context']);h['matches']=new['channels']
  h['reader_url']=f'/documents/{doc}?'+urlencode({'generation':h['generation'],'page':h['page'],'passage':h['id']})
  focus=set(record['concepts'])-concepts(h['title'])
  def focus_score(hit):return sum(1+math.log((len(pool)+1)/(df[t]+1)) for t in focus & concepts(hit['text']))
  if focus_score(h)>focus_score(output[first]):output[first],output[second]=output[second],output[first]
 return output,changes
