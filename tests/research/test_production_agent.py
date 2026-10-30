"""Production SDK boundaries. Disposable data only; no paid provider calls."""
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
import httpx
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request
from backend.agent_protocol import MODEL, request_bound
from backend.hosting import PublicLimits, UsageLedgerUnavailable, RequestSizeLimit
from backend.production_agent import ProductionAgent, Run
from backend.research_agent import ResearchTools, validate_answer

@pytest.fixture
def gateway(tmp_path):
    root=tmp_path/'prod';root.mkdir()
    ledger=root/'.research-usage';ledger.mkdir()
    with sqlite3.connect(ledger/'answer-usage.sqlite') as db:
        db.execute('CREATE TABLE usage(day TEXT PRIMARY KEY,attempts INTEGER NOT NULL)')
        db.execute('CREATE TABLE spend(month TEXT PRIMARY KEY,reserved_microusd INTEGER NOT NULL)')
        db.execute('INSERT INTO usage VALUES (?,?)',('2026-10-28',158))
        db.execute('INSERT INTO spend VALUES (?,?)',('2026-10',16_460_183))
    obj=object.__new__(ProductionAgent)
    obj.state=root/'agent';obj.state.mkdir();obj.runs={};obj.api_key='server-test-key';obj.transport=None
    obj.limits=PublicLimits(ledger,require_existing=True,hackathon_allowance=True)
    return obj

def payload():return {'model':MODEL,'max_tokens':4096,'messages':[{'role':'user','content':'question'}]}
def snapshot(gateway):
    with sqlite3.connect(gateway.limits.root/'answer-usage.sqlite') as db:
        return dict(db.execute('SELECT * FROM usage')),dict(db.execute('SELECT * FROM spend')),db.execute('SELECT count(*) FROM stage_reservations').fetchone()[0]

def request(token,body,host='127.0.0.1',origin=None):
    raw=json.dumps(body).encode();sent=False
    async def receive():
        nonlocal sent
        if sent:return {'type':'http.disconnect'}
        sent=True;return {'type':'http.request','body':raw,'more_body':False}
    headers=[(b'host',b'127.0.0.1:8091'),(b'x-api-key',token.encode()),(b'anthropic-beta',b'test-beta')]
    if origin:headers.append((b'origin',origin.encode()))
    return Request({'type':'http','http_version':'1.1','method':'POST','scheme':'http','path':'/internal-agent/v1/messages','headers':headers,'client':(host,5000),'server':('127.0.0.1',8091)},receive)

def test_every_attempt_gets_a_unique_production_receipt_and_preserves_failures(gateway):
    run=Run();a=gateway.reserve(run,payload());b=gateway.reserve(run,payload())
    assert a['receipt_id']!=b['receipt_id'] and run.reserved==2*request_bound(payload())
    usage,spend,count=snapshot(gateway)
    day=datetime.now(timezone.utc).date().isoformat()
    assert usage['2026-10-28']==158 and usage[day]==2 and count==2
    assert spend['2026-10']==16_460_183+run.reserved
    # No model-success requirement or refund path: these two failures stay counted.
    assert not (gateway.state/'accounting').exists()

def test_missing_ledger_never_initializes_or_dispatches(gateway):
    (gateway.limits.root/'answer-usage.sqlite').rename(gateway.limits.root/'saved.sqlite')
    with pytest.raises(UsageLedgerUnavailable):gateway.reserve(Run(),payload())
    assert not (gateway.limits.root/'answer-usage.sqlite').exists()

def test_each_sdk_request_uses_server_key_and_charges_before_transport(gateway):
    token='opaque';run=Run();gateway.runs[token]=run
    calls=[]
    def upstream(req):
        assert snapshot(gateway)[2]==len(calls)+1
        assert req.headers['x-api-key']=='server-test-key' and req.headers['anthropic-beta']=='test-beta'
        calls.append(req);return httpx.Response(500,json={'error':{'message':'synthetic failure'}})
    gateway.transport=httpx.MockTransport(upstream)
    async def exercise():
        for _ in range(2):
            response=await gateway.messages(request(token,payload()))
            assert response.status_code==500
            assert response.headers['x-should-retry']=='false'
            async for _ in response.body_iterator:pass
    asyncio.run(exercise())
    assert len(calls)==len(run.receipts)==2
    assert 'server-test-key' not in (gateway.state/'provider-receipts.jsonl').read_text()

def test_gateway_rejects_public_clients_origin_expired_or_unknown_token(gateway):
    gateway.runs['valid']=Run()
    for req in [request('valid',{},host='10.0.0.4'),request('valid',{},origin='https://actforgoa-field-guide.vercel.app'),request('missing',{})]:
        with pytest.raises(HTTPException) as error:gateway.authorize(req)
        assert error.value.status_code==403
    gateway.runs['valid'].active=False
    with pytest.raises(HTTPException):gateway.authorize(request('valid',{}))

def test_per_investigation_and_monthly_bounds_stop_before_dispatch(gateway):
    with pytest.raises(HTTPException):gateway.reserve(Run(ceiling=1),payload())
    with sqlite3.connect(gateway.limits.root/'answer-usage.sqlite') as db:db.execute('UPDATE spend SET reserved_microusd=49999999')
    with pytest.raises(HTTPException):gateway.reserve(Run(),payload())

def test_unpriced_payloads_never_receive_a_receipt(gateway):
    for extra in ({'model':'another-model'},{'service_tier':'fast'},{'tools':[{'type':'web_search_20250305'}]},{'messages':[{'role':'user','content':[{'type':'image'}]}]}):
        with pytest.raises(ValueError):gateway.reserve(Run(),{**payload(),**extra})
    assert not (gateway.state/'provider-receipts.jsonl').exists()

def test_only_loopback_transport_can_use_larger_payload():
    app=FastAPI();app.add_middleware(RequestSizeLimit)
    @app.post('/internal-agent/echo')
    async def echo(request:Request):return {'bytes':len(await request.body())}
    for host,expected in [('127.0.0.1',200),('10.0.0.4',413)]:
        with TestClient(app,client=(host,50)) as client:assert client.post('/internal-agent/echo',content=b'a'*80000).status_code==expected

@pytest.fixture
def corpus(tmp_path,monkeypatch):
    from backend import crm_store
    prior=crm_store.STATE;monkeypatch.setattr(crm_store,'STATE',prior)
    index=tmp_path/'index';index.mkdir();generation='test-generation'
    (index/'manifest.json').write_text(json.dumps({'stats':{'documents':2,'pages':3}}))
    with sqlite3.connect(index/'library.sqlite') as db:
        db.execute('CREATE TABLE documents(id TEXT PRIMARY KEY,metadata TEXT)')
        db.execute('CREATE TABLE pages(doc_id TEXT,page INTEGER,label TEXT,text TEXT,origin TEXT,warning TEXT)')
        db.execute('CREATE TABLE chunks(id TEXT,doc_id TEXT,page INTEGER,start INTEGER,end INTEGER,text TEXT)')
        for name,topics in [('legal','law'),('eco','ecology')]:
            meta={'id':name,'title':name,'topics':[topics],'url':'https://example.org/'+name,'format':'pdf','page_count':2 if name=='legal' else 1,'raw_path':'secret-internal-path'}
            db.execute('INSERT INTO documents VALUES(?,?)',(name,json.dumps(meta)))
        db.executemany('INSERT INTO pages VALUES(?,?,?,?,?,?)',[('legal',1,'Page 1','Goa building permission '+'text '*5000,'native',''),('legal',2,'Page 2','Conditions apply.','native',''),('eco',1,'Page 1','Wetland biodiversity evidence.','native','')])
    lib=SimpleNamespace(root=tmp_path,generation=generation,generation_dir=lambda g:index)
    limits=PublicLimits(tmp_path/'accounting',require_existing=True)
    return ProductionAgent(lib,limits,tmp_path/'agent','synthetic').corpus()

def test_complete_readers_page_cursor_and_exact_citation(corpus):
    assert corpus.catalogue()['total_matches']==2
    results=corpus.search('building permission')['results'];assert results
    result=corpus.read_document('legal',1,0,1000);text=result['pages'][0]['text']
    while result['next_cursor'] and result['next_cursor']['page']==1:
        result=corpus.read_document('legal',**result['next_cursor'],max_chars=1000);text+=result['pages'][0]['text']
    assert text==corpus.pages('legal',1,1)[0]['text'] and result['next_cursor']=={'page':2,'offset':0}
    assert 'raw_path' not in corpus.document('legal')
    readers=ResearchTools(corpus);e=readers.read({'document_id':'legal','page':2})['pages'][0]
    answer=validate_answer({'paragraphs':[{'text':'Conditions apply.','supports':[e['id']]}],'clarification':None,'followups':[],'limitation':None},readers,'all')
    assert answer['citations'][0]['text']=='Conditions apply.'
    with pytest.raises(ValueError):ResearchTools(corpus,'ecology').read({'document_id':'legal'})


def starter_answer(corpus):
    readers=ResearchTools(corpus)
    e=readers.read({'document_id':'eco','page':1})['pages'][0]
    return validate_answer({'paragraphs':[{'text':'Wetland biodiversity evidence.','supports':[e['id']]}],'clarification':None,'followups':['What does this mean?'],'limitation':None},readers,'all')


def test_reviewed_examples_preserve_citations_and_do_not_use_accounting(corpus,gateway):
    from backend.example_answers import ExampleAnswers,EXAMPLES
    from backend.chat import ChatRequest
    gateway.examples=ExampleAnswers(gateway.state,'runtime-v1','crm-v1')
    gateway.library=SimpleNamespace(generation=corpus.generation)
    gateway.corpora={corpus.generation:corpus}
    req=ChatRequest(question=EXAMPLES[0]);answer=starter_answer(corpus)
    assert gateway.cached_answer(req) is None
    gateway.examples.approve(req,answer,corpus,review_note='Fixture support reviewed')
    gateway.reserve(Run(),payload())  # Existing charged attempt must remain unchanged.
    baseline=snapshot(gateway)
    result=gateway.cached_answer(req)
    assert result['paragraphs']==answer['paragraphs'] and result['citations']==answer['citations']
    assert result['followups']==answer['followups'] and result['agent']['model_calls']==0
    assert result['timings']['provider_ms']==0 and result['cache']['hit']
    assert snapshot(gateway)==baseline
    (gateway.limits.root/'answer-usage.sqlite').rename(gateway.limits.root/'offline.sqlite')
    assert gateway.cached_answer(req)['cache']['hit']


def test_example_cache_scope_expiry_runtime_and_source_invalidation(corpus,tmp_path):
    from backend.example_answers import ExampleAnswers,EXAMPLES
    from backend.chat import ChatRequest,Message
    from datetime import timedelta
    cache=ExampleAnswers(tmp_path,'runtime','crm');req=ChatRequest(question=EXAMPLES[0])
    now=datetime.now(timezone.utc);answer=starter_answer(corpus)
    path=cache.approve(req,answer,corpus,review_note='Fixture',now=now)
    assert cache.get(req,corpus,now=now)
    for changes in ({'history':[Message(role='user',content='My private situation')]},{'domain':'ecology'},{'include_outside_context':False},{'question':EXAMPLES[0]+' in Panaji'}):
        assert cache.get(req.model_copy(update=changes),corpus,now=now) is None
    assert cache.get(req,corpus,now=now+timedelta(days=8)) is None
    assert ExampleAnswers(tmp_path,'new-runtime','crm').get(req,corpus) is None
    assert ExampleAnswers(tmp_path,'runtime','new-crm').get(req,corpus) is None
    old=corpus.source_digest;corpus.source_digest='changed'
    assert cache.get(req,corpus) is None
    corpus.source_digest=old
    data=json.loads(path.read_text());data['answer']['paragraphs'][0]['text']='Changed'
    path.write_text(json.dumps(data));assert cache.get(req,corpus) is None
    answer['citations'][0]['text']='Not the original'
    with pytest.raises(ValueError):cache.approve(req,answer,corpus,review_note='Bad source')


def test_batched_retrieval_preserves_scopes_cursors_and_read_source_validation(corpus):
    readers=ResearchTools(corpus,'ecology')
    result=readers.batch({'queries':['wetland','biodiversity'],'limit':2})
    assert len(result['reads'])==1
    evidence=result['reads'][0]['pages'][0]
    assert evidence['document_id']=='eco' and evidence['id'] in readers.citable_ids
    answer=validate_answer({'paragraphs':[{'text':'Wetland biodiversity evidence.','supports':[evidence['id']]}],'clarification':None,'followups':[],'limitation':None},readers,'ecology')
    assert answer['citations'][0]['text']=='Wetland biodiversity evidence.'
    scoped=ResearchTools(corpus,'all','legal')
    result=scoped.batch({'queries':['building permission'],'limit':2})
    assert all(p['document_id']=='legal' for r in result['reads'] for p in r['pages'])
    assert result['reads'][0]['next_cursor']['offset']==6000
    assert not ResearchTools(corpus,'legal').batch({'queries':['wetland'],'limit':2})['reads']
    with pytest.raises(ValueError):readers.batch({'queries':['a','b','c','d']})


def test_tool_timing_contains_no_source_content(corpus,monkeypatch):
    monkeypatch.setattr("backend.research_agent.create_sdk_mcp_server",lambda **kwargs:kwargs)
    readers=ResearchTools(corpus)
    server=readers.server()
    # Exercise the registered async MCP handler, not just its underlying function.
    async def invoke():
        handler=next(tool.handler for tool in server['tools'] if tool.name=='search_and_read')
        result=await handler({'queries':['wetland'],'limit':1})
        return result
    asyncio.run(invoke())
    assert readers.trace[-1]['tool']=='search_and_read'
    assert readers.trace[-1]['elapsed_ms']>=0
