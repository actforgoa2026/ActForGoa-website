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
from .passage_selection import document_focus, retrieval_focus, select_passages
from .source_context import preceding_prose_chunk, preceding_table_chunk, tabular_lines

IDENTIFIER = re.compile(r'^[a-zA-Z0-9-]{1,80}$')
STOP = set('a an the of in on at to from for is are was were be have has how why what which when where who does do can could would should explain tell me about and or with its it this that goa s sources source say says evidence research known'.split())
LEGAL_TERMS = {'law','laws','legal','act','acts','rule','rules','regulation','regulations','notification','amendment','gazette','permit','permission','crz','court','tribunal','rti'}

def authority_score(score, meta, legal_query):
    # A small relevance-bounded preference; authority is not proof of legal currency.
    return score * (1.15 if legal_query and meta.get('publisher_class')=='government_or_court' else 1)

def page_heading(text):
    """Scope hints only: prose outside a cited chunk must not become uncited evidence."""
    headings=[]
    for line in text.splitlines():
        line=line.strip();letters=[c for c in line if c.isalpha()]
        if not 3<=len(letters) or len(line)>140:continue
        if sum(c.isupper() for c in letters)/len(letters)>=.65 or re.match(r'^\d+(?:\.\d+)+\.?\s+\D',line):
            headings.append(line)
    return '\n'.join(headings[:6])[:500]

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
        focus=document_focus(query)
        named_document_condition=focus!=retrieval_focus(query)
        focus_terms=terms if focus==query else [t.lower() for t in re.findall(r'[^\W_]+',focus,re.UNICODE) if len(t)>1 and t.lower() not in STOP]
        query_concepts={t[:5] if len(t)>5 else t for t in focus_terms}
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
            candidates={}
            for identifier in scores:
                row=db.execute('SELECT c.*,d.metadata,p.warning,p.label,substr(p.text,1,1400) AS page_context FROM chunks c JOIN documents d ON d.id=c.doc_id JOIN pages p ON p.doc_id=c.doc_id AND p.page=c.page WHERE c.id=?',(identifier,)).fetchone()
                if row:candidates[identifier]=(row,json.loads(row['metadata']))
            legal_query=bool(LEGAL_TERMS.intersection(terms))
            # RRF alone can over-rank passages matching one generic term in both
            # channels. Reward coverage of the question's distinct concepts too.
            def relevance(identifier):
                row,meta=candidates[identifier]
                # Titles identify the requested document; they remain metadata,
                # never support for an answer's substantive claims.
                ranked_text=row['text']+(' '+meta.get('title','') if named_document_condition else '')
                words=re.findall(r'[^\W_]+',ranked_text.lower(),re.UNICODE)
                # Light prefix matching joins variants such as estuary/estuarine.
                concepts={w[:5] if len(w)>5 else w for w in words}
                coverage=len(query_concepts & concepts)/max(len(query_concepts),1)
                return (scores[identifier]+.05*coverage**2)*max(legal_authority_multiplier(meta,domain),1.15 if legal_query and meta.get('publisher_class')=='government_or_court' else 1)
            ranked=sorted(candidates,key=relevance,reverse=True)

            def distinct(identifiers):
                selected=[];counts={};seen_passages=[]
                for identifier in identifiers:
                    row,_=candidates[identifier]
                    if identifier in selected or counts.get(row['doc_id'],0)>=(4 if doc_id else 2):continue
                    words=re.findall(r'\w+',row['text'].lower())
                    shingles=set(zip(words,words[1:]))
                    if shingles and any(len(shingles & prior)/max(len(shingles | prior),1)>.9 for prior in seen_passages):continue
                    seen_passages.append(shingles)
                    counts[row['doc_id']]=counts.get(row['doc_id'],0)+1
                    selected.append(identifier)
                    if len(selected)>=limit:break
                return selected

            selected=distinct(ranked)
            if not doc_id:
                revised=select_passages(query,candidates,selected,{i:relevance(i) for i in candidates},STOP)
                # Recheck cross-document duplicates after joint selection and
                # backfill only from the same bounded hybrid candidate pool.
                selected=distinct(revised+ranked)
            def citation(row, meta, matches):
                identifier=row['id']
                qs=urlencode({'generation':generation,'page':row['page'],'passage':identifier})
                result = {'id':identifier,'document_id':row['doc_id'],'page':row['page'],'label':row['label'],'start':row['start'],'end':row['end'],
                    'title':meta.get('title') or meta['url'],'url':meta['url'],'text':row['text'],'origin':row['origin'],'warning':row['warning'],
                    'page_heading':page_heading(row['page_context']),
                    'domains':document_domains(meta),
                    'retrieved_at':meta.get('retrieved_at'),'format':meta.get('format'),'matches':matches,
                    **{key:meta.get(key) for key in ('publisher_class','legal_currency','source_date_metadata','topics','document_kind_hint','guide_verification')},
                    'reader_url':f'/documents/{row["doc_id"]}?{qs}','generation':generation}
                from .source_review import answer_exclusion
                reason = answer_exclusion(result)
                if reason:
                    result['warning'] = ' '.join(filter(None, [result['warning'], reason]))
                return result

            results=[]
            for identifier in selected:
                row,meta=candidates[identifier]
                result=citation(row,meta,channels[identifier])
                if row['start'] or len(tabular_lines(row['text']))>=2:
                    page=db.execute('SELECT text FROM pages WHERE doc_id=? AND page=?',(row['doc_id'],row['page'])).fetchone()
                    siblings=db.execute('SELECT c.*,p.warning,p.label,substr(p.text,1,1400) AS page_context FROM chunks c JOIN pages p ON p.doc_id=c.doc_id AND p.page=c.page WHERE c.doc_id=? AND c.page=? ORDER BY c.start',(row['doc_id'],row['page'])).fetchall()
                    contexts=[preceding_prose_chunk(page['text'],row['start'],row['end'],siblings)]
                    if len(tabular_lines(row['text']))>=2:
                        contexts.append(preceding_table_chunk(page['text'],row['start'],row['end'],siblings))
                    contexts={context['id']:context for context in contexts if context is not None and context['id']!=identifier}
                    if contexts:
                        result['supporting_context']=[citation(context,meta,['source_context']) for context in contexts.values()]
                results.append(result)
                if len(results)>=limit:break
        return results
