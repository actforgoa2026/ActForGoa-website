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
