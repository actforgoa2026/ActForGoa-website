"""SDK research with the existing production ledger and a loopback-only gateway.

Never imports development accounting. Every HTTP model attempt (including retries,
errors and structured-output work) reserves before dispatch. No refund path exists.
"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
from time import perf_counter
from uuid import uuid4
import httpx
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from .agent_corpus import AgentCorpus, readonly
from .agent_protocol import MODEL, MAX_REQUEST_MICROUSD, request_bound
from . import crm_store
from .hosting import UsageLedgerUnavailable
from .research_agent import run_agent
from .example_answers import ExampleAnswers, EXAMPLES, runtime_digest
from .chat import ChatRequest

MAX_CALLS=12
MAX_RUN_MICROUSD=3_000_000

@dataclass
class Run:
    identifier: str=field(default_factory=lambda:uuid4().hex)
    receipts: list=field(default_factory=list)
    reserved: int=0
    ceiling: int=MAX_RUN_MICROUSD
    active: bool=True
    provider_ms: float=0

class ProductionAgent:
    def __init__(self, library, limits, state, api_key, transport=None):
        self.library=library;self.limits=limits;self.state=Path(state);self.api_key=api_key
        self.transport=transport;self.runs={};self.corpora={}
        self.state.mkdir(mode=0o700,parents=True,exist_ok=True)
        snapshot=Path(__file__).with_name('data')/'crm.json'
        if not snapshot.is_file():snapshot=Path(__file__).resolve().parents[1]/'public/data/crm.json'
        digest=hashlib.sha256(snapshot.read_bytes()).hexdigest()
        crm_store.STATE=self.state/'crm'/digest
        if not (crm_store.STATE/'crm.sqlite').exists():crm_store.build_index(snapshot,crm_store.STATE/'crm.sqlite')
        if crm_store.stats()['sha256']!=digest:raise ValueError('CRM snapshot integrity mismatch')
        self.examples=ExampleAnswers(self.state,runtime_digest(),digest)
        self.corpus(library.generation)

    def corpus(self, generation=None):
        generation=generation or self.library.generation
        if generation in self.corpora:return self.corpora[generation]
        index=self.library.generation_dir(generation)
        source=index/'library.sqlite'
        # A separate derived index; never write/open the original corpus through Zvec.
        with source.open('rb') as handle:digest=hashlib.file_digest(handle,'sha256').hexdigest()
        folder=self.state/'page-search'/digest;folder.mkdir(parents=True,exist_ok=True)
        search=folder/'pages.sqlite'
        if not search.is_file():
            temporary=folder/(uuid4().hex+'.sqlite')
            with readonly(source) as db,sqlite3.connect(temporary) as target:
                target.execute('CREATE VIRTUAL TABLE page_search USING fts5(doc_id UNINDEXED,page UNINDEXED,title,text,tokenize="unicode61")')
                docs={row['id']:json.loads(row['metadata']) for row in db.execute('SELECT id,metadata FROM documents')}
                for row in db.execute('SELECT doc_id,page,text FROM pages ORDER BY doc_id,page'):
                    target.execute('INSERT INTO page_search VALUES(?,?,?,?)',(row['doc_id'],row['page'],docs[row['doc_id']].get('title',''),row['text']))
                if target.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Page search integrity failure')
                if target.execute('SELECT count(*) FROM page_search').fetchone()[0]!=db.execute('SELECT count(*) FROM pages').fetchone()[0]:raise ValueError('Incomplete page index')
            temporary.chmod(0o444);temporary.replace(search)
        corpus=AgentCorpus(self.library.root,generation,index,search)
        corpus.source_digest=digest
        self.corpora[generation]=corpus
        return corpus

    def record(self, **fields):
        # No questions, evidence, credentials or provider response bodies in this ledger.
        path=self.state/'provider-receipts.jsonl'
        fd=os.open(path,os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
        with os.fdopen(fd,'a') as out:out.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),**fields})+'\n')

    def authorize(self, request):
        if (not request.client or request.client.host not in ('127.0.0.1','::1')
            or request.url.hostname not in ('127.0.0.1','localhost') or request.headers.get('origin')):
            raise HTTPException(403,'Internal SDK transport only')
        run=self.runs.get(request.headers.get('x-api-key',''))
        if run is None or not run.active:raise HTTPException(403,'Internal SDK transport only')
        return run

    def reserve(self, run, payload):
        amount=request_bound(payload)
        if not run.active or len(run.receipts)>=MAX_CALLS or run.reserved+amount>run.ceiling:
            raise HTTPException(429,'This investigation reached its bounded allowance.',headers={'x-should-retry':'false'})
        receipt=self.limits.reserve_stage(amount,datetime.now(timezone.utc).date().isoformat(),uuid4().hex,'draft')
        if not receipt['reserved']:
            raise HTTPException(429,'The production answer allowance is unavailable.',headers={'x-should-retry':'false'})
        run.receipts.append(receipt['receipt_id']);run.reserved+=amount
        self.record(event='reserved',run=run.identifier,receipt=receipt['receipt_id'],reserved_microusd=amount)
        return receipt

    async def count_tokens(self, request):
        self.authorize(request)
        return {'input_tokens':len(await request.body())+16384}

    async def messages(self, request):
        run=self.authorize(request)
        try:
            payload=await request.json()
            output=payload.get('max_tokens',4096)
            if type(output) is not int:raise ValueError('Invalid output bound')
            payload['max_tokens']=min(4096,output)
            receipt=self.reserve(run,payload)
        except (ValueError,UsageLedgerUnavailable):
            raise HTTPException(429,'The model request cannot be safely accounted.',headers={'x-should-retry':'false'}) from None
        client=httpx.AsyncClient(timeout=70,follow_redirects=False,transport=self.transport)
        headers={'x-api-key':self.api_key,'anthropic-version':request.headers.get('anthropic-version','2023-06-01'),'content-type':'application/json'}
        if request.headers.get('anthropic-beta'):headers['anthropic-beta']=request.headers['anthropic-beta']
        started=perf_counter()
        try:
            upstream=await client.send(client.build_request('POST','https://api.anthropic.com/v1/messages',headers=headers,json=payload),stream=True)
        except BaseException:
            self.record(event='connection_failed',run=run.identifier,receipt=receipt['receipt_id'])
            run.provider_ms+=(perf_counter()-started)*1000
            await client.aclose();raise HTTPException(502,'Provider connection failed; reservation retained.',headers={'x-should-retry':'false'}) from None
        self.record(event='provider_response',run=run.identifier,receipt=receipt['receipt_id'],status=upstream.status_code)
        async def stream():
            try:
                async for block in upstream.aiter_bytes():yield block
            finally:
                run.provider_ms+=(perf_counter()-started)*1000
                await upstream.aclose();await client.aclose()
        return StreamingResponse(stream(),status_code=upstream.status_code,media_type=upstream.headers.get('content-type','application/json'),headers={'x-should-retry':'false'})

    def cached_answer(self, request):
        started=perf_counter()
        if not hasattr(self,'examples'):return None
        # Explicit old-generation questions remain scoped; never cross generations.
        corpus=self.corpus(request.generation)
        answer=self.examples.get(request,corpus)
        if answer is not None:
            answer['timings']={'total_ms':round((perf_counter()-started)*1000,2),'provider_ms':0,'tool_ms':0,'model_calls':0}
            self.record(event='example_cache_hit',generation=corpus.generation,total_ms=answer['timings']['total_ms'],model_calls=0)
        return answer

    def cached_examples(self):
        corpus=self.corpus()
        return [q for q in EXAMPLES if self.examples.get(ChatRequest(question=q),corpus) is not None]

    async def answer(self, request):
        started=perf_counter()
        capacity=self.limits.preflight_single(MAX_REQUEST_MICROUSD,datetime.now(timezone.utc).date().isoformat())
        if not capacity['allowed']:raise HTTPException(429,'The remaining production allowance cannot cover an investigation.')
        _,cap=self.limits.effective_limits(capacity['day'])
        run=Run(ceiling=min(MAX_RUN_MICROUSD,cap-capacity['observed']['month_reserved_microusd']))
        token=secrets.token_urlsafe(48);self.runs[token]=run
        try:
            corpus=await asyncio.to_thread(self.corpus,request.generation)
            config={'extra_retrieval_terms':'','answer_brief':'','effort':'medium'}
            answer=await asyncio.wait_for(run_agent(request,corpus,config,'http://127.0.0.1:'+os.getenv('PORT','8091')+'/internal-agent',token,run.ceiling/1e6,state=self.state,retain_content=False),110)
            private=answer.pop('_dev')
            answer['timings']={'total_ms':round((perf_counter()-started)*1000,2),'provider_ms':round(run.provider_ms,2),'tool_ms':round(sum(c.get('elapsed_ms',0) for c in private['tool_calls']),2),'model_calls':len(run.receipts)}
            answer['agent']={'engine':'claude-agent-sdk','run_id':run.identifier,'model':MODEL,'tools':[c['tool'] for c in private['tool_calls']], 'model_calls':len(run.receipts),'citation_validation':'read-source IDs; original passages or labelled official guidance summaries'}
            self.record(event='completed',run=run.identifier,tools=answer['agent']['tools'],model_calls=len(run.receipts),reserved_microusd=run.reserved,timings=answer['timings'],tool_timings=[{k:c[k] for k in ('tool','elapsed_ms') if k in c} for c in private['tool_calls']])
            return answer
        finally:
            run.active=False;self.runs.pop(token,None)
            self.record(event='closed',run=run.identifier,model_calls=len(run.receipts),reserved_microusd=run.reserved,total_ms=round((perf_counter()-started)*1000,2),provider_ms=round(run.provider_ms,2))
