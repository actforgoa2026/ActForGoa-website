"""Read-only access to a complete, hash-verified local corpus. No provider calls."""
import json
import hashlib
import os
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlencode
from .domains import document_domains
from .retrieval_intent import expand_retrieval_query

STATE = Path(os.getenv('ACTFORGOA_DEV_STATE', str(Path.home()/'.local/share/actforgoa-research-dev')))
STOP = set('a an the in on to for of is are can how what which where i want with and do about apply please need could would should it that this we my'.split())

def readonly(path):
    db = sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro&immutable=1', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    return db

class LocalCorpus:
    def __init__(self, root=None):
        self.root = Path(root or STATE/'corpus/20261027T065155-law-5bc5619b')
        self.ready = json.loads((self.root/'READY.json').read_text())
        self.generation = self.ready['generation']
        self.index = self.root/'.research-index/generations'/self.generation
        self.manifest = json.loads((self.index/'manifest.json').read_text())
        with self.connect() as db:
            self.documents = {r['id']:json.loads(r['metadata']) for r in db.execute('SELECT * FROM documents')}
            self.exclusions={}
            reviews=json.loads(Path(__file__).with_name('source_review.json').read_text())
            for review in reviews['answer_exclusions']:
                row=db.execute('SELECT * FROM chunks WHERE id=? AND doc_id=?',(review['passage_id'],review['document_id'])).fetchone()
                if row and hashlib.sha256(row['text'].encode()).hexdigest()==review['text_sha256']:
                    self.exclusions.setdefault((row['doc_id'],row['page']),[]).append((row['start'],row['end'],review['reason']))
        self.domains = {k:document_domains(v) for k,v in self.documents.items()}

    def connect(self): return readonly(self.index/'library.sqlite')

    def document(self, doc_id):
        if doc_id not in self.documents: raise KeyError('Document not found')
        meta = dict(self.documents[doc_id])
        query = urlencode({'generation':self.generation})
        return {**meta, 'domains':self.domains[doc_id], 'generation':self.generation,
                'reader_url':f'/documents/{doc_id}?{query}',
                'original_url':f'/api/documents/{doc_id}/original?{query}',
                'text_url':f'/api/documents/{doc_id}/text?{query}'}

    def catalogue(self, query='', domain='all', offset=0, limit=20):
        if domain not in ('all','legal','ecology'): raise ValueError('Unknown collection')
        terms = query.casefold().split()
        matches = [self.document(k) for k,v in self.documents.items()
                   if (domain=='all' or domain in self.domains[k]) and
                   all(t in json.dumps({x:v.get(x) for x in ('title','url','topics','publisher_class')},ensure_ascii=False).casefold() for t in terms)]
        matches.sort(key=lambda x:(-sum(t in x.get('title','').casefold() for t in terms),x.get('title','').casefold(), x['id']))
        limit=min(100,max(1,limit));offset=max(0,offset)
        rows=matches[offset:offset+limit]
        return {'documents':rows,'total_matches':len(matches),'next_offset':offset+len(rows) if offset+len(rows)<len(matches) else None,'generation':self.generation}

    def pages(self, doc_id, start=1, limit=10):
        self.document(doc_id)
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT page,label,text,origin,warning FROM pages WHERE doc_id=? AND page>=? ORDER BY page LIMIT ?', (doc_id,max(1,start),min(50,max(1,limit))))]

    def evidence(self, doc_id, page, start=0, end=None):
        meta=self.document(doc_id);rows=self.pages(doc_id,page,1)
        if not rows or rows[0]['page']!=page:raise KeyError('Page not found')
        row=rows[0];end=min(len(row['text']),end if end is not None else len(row['text']))
        start=max(0,min(start,end));identifier=f'{doc_id}:p{page}:{start}:{end}'
        exclusions=[reason for a,b,reason in self.exclusions.get((doc_id,page),[]) if start<b and end>a]
        return {**meta,**row,'id':identifier,'document_id':doc_id,'text':row['text'][start:end],
                'start':start,'end':end,'matches':['keyword'],
                'answer_excluded':bool(exclusions) or 'Corrupted character extraction' in (row['warning'] or ''),'warning':' '.join(filter(None,[row['warning'],*exclusions])),
                'reader_url':f'/documents/{doc_id}?'+urlencode({'generation':self.generation,'page':page,'passage':identifier})}

    def read_document(self, doc_id, page=1, offset=0, max_chars=18000):
        """Lossless cursor: even an oversized page can be read to its very end."""
        doc=self.document(doc_id);max_chars=min(24000,max(1000,max_chars))
        rows=self.pages(doc_id,page,1)
        if not rows or rows[0]['page']!=page:raise KeyError('Page not found')
        text=rows[0]['text'];offset=max(0,offset);end=min(len(text),offset+max_chars)
        if offset>len(text):raise ValueError('Offset outside page')
        evidence=self.evidence(doc_id,page,offset,end)
        next_cursor={'page':page,'offset':end} if end<len(text) else {'page':page+1,'offset':0} if page<doc['page_count'] else None
        return {'document':doc,'pages':[evidence],'next_cursor':next_cursor,'full_text_url':doc['text_url']}

    def search(self, query, limit=8, doc_id=None, domain='all', offset=0):
        if domain not in ('all','legal','ecology'):raise ValueError('Unknown collection')
        if doc_id:self.document(doc_id)
        query=expand_retrieval_query(query)
        terms=list(dict.fromkeys(t.lower() for t in re.findall(r'[^\W_]+',query) if t.lower() not in STOP))[:24]
        if not terms:return {'results':[],'total_matches':0,'next_offset':None,'generation':self.generation,'domain':domain}
        clauses=['page_search MATCH ?'];args=[' OR '.join('"'+t+'"' for t in terms)]
        ids=[doc_id] if doc_id else [k for k in self.documents if domain=='all' or domain in self.domains[k]]
        if doc_id and domain!='all' and domain not in self.domains[doc_id]:ids=[]
        clauses.append('doc_id IN ('+','.join('?' for _ in ids)+')');args+=ids
        where=' AND '.join(clauses);limit=min(30,max(1,limit));offset=max(0,offset)
        with readonly(self.root/'agent-search.sqlite') as db:
            count=db.execute('SELECT count(*) FROM page_search WHERE '+where,args).fetchone()[0]
            rows=db.execute('SELECT doc_id,page,text FROM page_search WHERE '+where+' ORDER BY bm25(page_search,0,0,4,1),doc_id,CAST(page AS INTEGER) LIMIT ? OFFSET ?',args+[limit,offset]).fetchall()
        results=[]
        for r in rows:
            text=r['text'];positions=[text.casefold().find(t) for t in terms];first=min((p for p in positions if p>=0),default=0)
            start=max(0,first-350)
            results.append(self.evidence(r['doc_id'],int(r['page']),start,min(len(text),start+2400)))
        return {'results':results,'total_matches':count,'next_offset':offset+len(rows) if offset+len(rows)<count else None,'generation':self.generation,'domain':domain}

    def original(self, doc_id):
        doc=self.document(doc_id);path=(self.root/doc['raw_path']).resolve()
        if not path.is_relative_to((self.root/'corpus/raw').resolve()):raise ValueError('Unsafe original path')
        return path,doc
