import json
from pathlib import Path
import re
import sqlite3
import threading
from urllib.parse import urlencode
import zvec
from .embeddings import Encoder, ROOT
from .extraction import safe_path
from .domains import document_domains, legal_authority_multiplier

IDENTIFIER = re.compile(r'^[a-zA-Z0-9-]{1,80}$')
STOP = set('a an the of in on at to from for is are was were be have has how why what which when where who does do can could would should explain tell me about and or with its it this that goa'.split())

class Library:
    def __init__(self, root=ROOT, index_root=None):
        self.root=Path(root);self.index=Path(index_root or self.root/'.research-index')
        self.generation=json.loads((self.index/'CURRENT.json').read_text())['generation']
        self.directory=self.generation_dir(self.generation)
        self.manifest=json.loads((self.directory/'manifest.json').read_text())
        self.encoder=Encoder()
        if self.encoder.fingerprint!=self.manifest['encoder_sha256']:
            raise ValueError('Embedding model differs from index; rebuild the index')
        self.vectors=zvec.open(str(self.directory/'zvec'),option=zvec.CollectionOption(read_only=True))
        self.lock=threading.Lock()
        self._domain_cache={}

    def generation_dir(self, generation=None):
        generation=generation or self.generation
        if not IDENTIFIER.fullmatch(generation):raise KeyError('Unknown index version')
        directory=self.index/'generations'/generation
        if not (directory/'manifest.json').is_file():raise KeyError('Unknown index version')
        return directory

    def connect(self, generation=None):
        db=sqlite3.connect(f'file:{self.generation_dir(generation)/"library.sqlite"}?mode=ro',uri=True)
        db.row_factory=sqlite3.Row
        return db

    def document(self, doc_id, generation=None, private=False):
        with self.connect(generation) as db:
            row=db.execute('SELECT metadata FROM documents WHERE id=?',(doc_id,)).fetchone()
        if not row:raise KeyError('Document not found')
        meta=json.loads(row['metadata'])
        if private:return meta
        keys=['id','title','url','retrieved_at','format','page_count','page_labels','quality','sha256','extraction_version','publisher_class','topics','legal_currency','rights_status','aliases','source_date_metadata','guide_verification','document_kind_hint']
        result={key:meta.get(key) for key in keys}
        result["domains"]=document_domains(meta)
        query=urlencode({'generation':generation or self.generation})
        result.update(original_url=f'/api/documents/{doc_id}/original?{query}',text_url=f'/api/documents/{doc_id}/text?{query}',generation=generation or self.generation)
        return result

    def pages(self, doc_id, generation=None, start=1, limit=10):
        self.document(doc_id,generation)
        with self.connect(generation) as db:
            return [dict(r) for r in db.execute('SELECT page,label,text,origin,warning FROM pages WHERE doc_id=? AND page>=? ORDER BY page LIMIT ?',(doc_id,start,limit))]

    def original(self, doc_id, generation=None):
        meta=self.document(doc_id,generation,private=True)
        path=safe_path(self.root,meta['raw_path'])
        if not path.is_file():raise KeyError('Original file is unavailable')
        return path,meta

    def domain_documents(self, generation=None):
        generation=generation or self.generation
        if generation not in self._domain_cache:
            with self.connect(generation) as db:
                rows=db.execute('SELECT id,metadata FROM documents').fetchall()
            self._domain_cache[generation]={row['id']:document_domains(json.loads(row['metadata'])) for row in rows}
        return self._domain_cache[generation]

    def domain_counts(self):
        domains=self.domain_documents()
        return {domain:sum(domain in values for values in domains.values()) for domain in ('legal','ecology')}

    def search(self, query, limit=8, doc_id=None, generation=None, domain='all'):
        if domain not in ('all','legal','ecology'):raise ValueError('Unknown library section')
        query=query.strip()
        if not query:return []
        generation=generation or self.generation
        if doc_id:self.document(doc_id,generation)
        domain_ids=None if domain=='all' else [identifier for identifier,domains in self.domain_documents(generation).items() if domain in domains and (not doc_id or identifier==doc_id)]
        if domain_ids is not None and not domain_ids:return []
        # IDs originate in the immutable index, but validate before filter interpolation.
        if domain_ids and any(not IDENTIFIER.fullmatch(identifier) for identifier in domain_ids):raise ValueError('Invalid indexed document identity')
        vector_filter=f"document = '{doc_id}'" if doc_id else None
        if domain_ids is not None:
            vector_filter="document in ("+','.join("'"+identifier+"'" for identifier in domain_ids)+")"
        terms=list(dict.fromkeys(t.lower() for t in re.findall(r'[^\W_]+',query,re.UNICODE) if len(t)>1 and t.lower() not in STOP))[:24]
        if not terms:terms=re.findall(r'[^\W_]+',query)[:8]
        if any(t in terms for t in ['mhadei','mahadayi','mandovi']):terms.extend(['mhadei','mahadayi','mandovi'])
        expression=' OR '.join('"'+t+'"' for t in dict.fromkeys(terms))
        with self.connect(generation) as db:
            conditions=[];parameters=[expression]
            if doc_id:conditions.append('c.doc_id=?');parameters.append(doc_id)
            if domain_ids is not None:
                conditions.append('c.doc_id IN ('+','.join('?' for _ in domain_ids)+')');parameters.extend(domain_ids)
            lexical=db.execute('SELECT p.id FROM passages p JOIN chunks c ON c.id=p.id WHERE passages MATCH ?'+
                ''.join(' AND '+condition for condition in conditions)+' ORDER BY bm25(passages,0,3,1) LIMIT 80',parameters).fetchall() if expression else []
            with self.lock:
                vector=self.encoder.encode([query])[0].tolist()
                collection=self.vectors if generation==self.generation else zvec.open(str(self.generation_dir(generation)/'zvec'),option=zvec.CollectionOption(read_only=True))
                semantic=collection.query(queries=zvec.Query(field_name='embedding',vector=vector),topk=80,
                    filter=vector_filter)
                if generation!=self.generation:del collection
            # Zvec COSINE scores are distances: identical vectors score zero.
            # Without any keyword evidence, require a stronger semantic match.
            semantic_limit=0.65 if lexical else 0.50
            scores={};channels={}
            for channel,ids in [('keyword',[r['id'] for r in lexical]),('semantic',[r.id for r in semantic if r.score<=semantic_limit])]:
                for rank,identifier in enumerate(ids,1):
                    scores[identifier]=scores.get(identifier,0)+1/(60+rank)
                    channels.setdefault(identifier,[]).append(channel)
            # Primary official sources receive a small relevance-bounded preference.
            for identifier in scores:
                row=db.execute('SELECT d.metadata FROM chunks c JOIN documents d ON d.id=c.doc_id WHERE c.id=?',(identifier,)).fetchone()
                if row:scores[identifier]*=legal_authority_multiplier(json.loads(row['metadata']),domain)
            results=[];counts={};seen_passages=[]
            for identifier in sorted(scores,key=lambda i:scores[i],reverse=True):
                row=db.execute('SELECT c.*,d.metadata,p.warning,p.label FROM chunks c JOIN documents d ON d.id=c.doc_id JOIN pages p ON p.doc_id=c.doc_id AND p.page=c.page WHERE c.id=?',(identifier,)).fetchone()
                if not row:continue
                if counts.get(row['doc_id'],0)>= (4 if doc_id else 2):continue
                words=re.findall(r'\w+',row['text'].lower())
                shingles=set(zip(words,words[1:]))
                if shingles and any(len(shingles & prior)/max(len(shingles | prior),1)>.9 for prior in seen_passages):continue
                seen_passages.append(shingles)
                counts[row['doc_id']]=counts.get(row['doc_id'],0)+1
                meta=json.loads(row['metadata']);qs=urlencode({'generation':generation,'page':row['page'],'passage':identifier})
                results.append({'id':identifier,'document_id':row['doc_id'],'page':row['page'],'label':row['label'],'start':row['start'],'end':row['end'],
                    'title':meta.get('title') or meta['url'],'url':meta['url'],'text':row['text'],'origin':row['origin'],'warning':row['warning'],
                    'retrieved_at':meta.get('retrieved_at'),'format':meta.get('format'),'matches':channels[identifier],
                    'domains':document_domains(meta),
                    **{key:meta.get(key) for key in ('publisher_class','legal_currency','source_date_metadata','guide_verification','document_kind_hint')},
                    'reader_url':f'/documents/{row["doc_id"]}?{qs}','generation':generation})
                if len(results)>=limit:break
        return results
