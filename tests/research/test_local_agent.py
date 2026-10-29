"""Focused local-only checks. Never call a model or touch production accounting."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import pytest
pytest.importorskip('claude_agent_sdk', reason='Optional local research SDK environment')
from fastapi.testclient import TestClient
from backend.local_corpus import LocalCorpus, STATE
if not (STATE/'corpus/20261027T065155-law-5bc5619b/READY.json').is_file():
    pytest.skip('Complete private local corpus is not installed in this executor', allow_module_level=True)
from backend.local_budget import DevBudget, BudgetUnavailable, request_bound, MODEL
from backend.research_agent import ResearchTools, validate_answer, agent_options
from backend import crm_store
from backend.local_agent_app import app
from dev.reconcile_dev_budget import reconcile

@pytest.fixture(scope='module')
def corpus():return LocalCorpus()

@pytest.fixture
def accounted(tmp_path):
    source=tmp_path/'export.sqlite'
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE spend(month TEXT PRIMARY KEY,reserved_microusd INTEGER NOT NULL)')
        db.execute('CREATE TABLE usage(day TEXT PRIMARY KEY,attempts INTEGER NOT NULL)')
        db.execute('CREATE TABLE stage_reservations(receipt_json TEXT NOT NULL)')
        db.execute('INSERT INTO spend VALUES (?,?)',('2026-10',200000))
        db.execute('INSERT INTO usage VALUES (?,?)',('2026-10-29',1))
        db.execute('INSERT INTO stage_reservations VALUES (?)',(json.dumps({'cost_microusd':200000}),))
    sha=hashlib.sha256(source.read_bytes()).hexdigest();expiry=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()
    state=tmp_path/'state';reconcile(source,sha,expiry,True,state)
    return DevBudget(state),source,sha,expiry

def test_manifest_matches_every_document_page_and_passage(corpus):
    with corpus.connect() as db:
        assert {t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ('documents','pages','chunks')}=={'documents':1174,'pages':21534,'chunks':79564}
        assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
        with pytest.raises(sqlite3.OperationalError):db.execute('DELETE FROM pages')
    seen=[]
    for offset in range(0,1174,100):seen += [d['id'] for d in corpus.catalogue(offset=offset,limit=100)['documents']]
    assert len(seen)==len(set(seen))==1174
    assert len(list((corpus.root/'agent-documents').glob('*.txt')))==1174
    assert all(p.stat().st_mode&0o222==0 for p in corpus.root.rglob('*') if p.is_file())

def test_oversized_page_can_be_read_completely_without_losing_offsets(corpus):
    with corpus.connect() as db:doc,page,full=db.execute('SELECT doc_id,page,text FROM pages ORDER BY length(text) DESC LIMIT 1').fetchone()
    collected='';offset=0
    while True:
        result=corpus.read_document(doc,page,offset,max_chars=1000)
        evidence=result['pages'][0];assert evidence['text']==full[evidence['start']:evidence['end']]
        collected+=evidence['text'];cursor=result['next_cursor']
        if not cursor or cursor['page']!=page:break
        offset=cursor['offset']
    assert collected==full

def test_crm_whole_snapshot_and_location_boundaries():
    crm_store.STATE=STATE/'crm'
    for collection,total in [('community',499),('government',2768)]:
        ids=[]
        for offset in range(0,total,100):ids += [r['record_id'] for r in crm_store.search_records('',collection,limit=100,offset=offset)['records']]
        assert len(ids)==len(set(ids))==total
    results=crm_store.search_records('', 'government','Agonda',100)['records']
    assert any(r['name']=='Village Panchayat Agonda' for r in results)
    assert all('Shantagonda' not in r['name'] for r in results)

def test_missing_reconciliation_never_creates_a_ledger(tmp_path):
    gate=DevBudget(tmp_path);assert gate.status()['remaining_usd'] is None
    with pytest.raises(BudgetUnavailable):gate.reserve(1)
    assert not (tmp_path/'accounting').exists()

def test_import_cannot_overwrite_or_reset_accounting(accounted):
    gate,source,sha,expiry=accounted
    with pytest.raises(ValueError):reconcile(source,sha,expiry,True,gate.state.parent)
    assert gate.status()['remaining_usd']==1.8

def test_concurrent_attempts_cannot_exceed_total_allowance(accounted):
    gate,*_=accounted
    def reserve(_):
        try:return gate.reserve(700000)
        except BudgetUnavailable:return None
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(reserve,range(4)))
    assert sum(r is not None for r in results)==2
    assert gate.status()['reserved_usd']==1.6
    assert gate.status()['remaining_usd']==.4

def test_failed_call_reservation_persists_and_missing_ledger_stays_closed(accounted):
    gate,*_=accounted;gate.reserve(100000)
    assert DevBudget(gate.state.parent).status()['reserved_usd']==.3
    (gate.state/'answer-usage.sqlite').rename(gate.state/'retained.sqlite')
    assert not gate.status()['ready']
    with pytest.raises(BudgetUnavailable):gate.reserve(100)
    assert not (gate.state/'answer-usage.sqlite').exists()

def test_provider_bound_and_unpriced_features():
    payload={'model':MODEL,'max_tokens':1000,'messages':[{'role':'user','content':'building permission'}]}
    assert request_bound(payload)>10000
    for changed in ({'model':'other'},{'speed':'fast'},{'tools':[{'type':'web_search_20250305'}]},{'max_tokens':5000}):
        with pytest.raises(ValueError):request_bound({**payload,**changed})

def test_sdk_readers_multi_search_and_exact_quote_validation(corpus):
    r=ResearchTools(corpus)
    r.search({'query':'building permission','limit':3})
    second=r.search({'query':'change of use','limit':3})
    e=second['results'][0];r.read({'document_id':e['document_id'],'page':e['page'],'max_chars':5000})
    raw={'paragraphs':[{'text':'A bounded test statement.','supports':[{'citation_id':e['id'],'quote':e['text'][:40]}]}],'clarification':'Which village or town?','limitation':None,'followups':['What documents are needed?']}
    assert validate_answer(raw,r,'all')['clarification']=='Which village or town?'
    raw['paragraphs'][0]['supports'][0]['quote']='A fabricated quotation that is not present.'
    with pytest.raises(ValueError):validate_answer(raw,r,'all')
    o=agent_options(r,'Test prompt','http://127.0.0.1:8093/provider','local-capability',0)
    assert o.tools==[] and o.setting_sources==[] and len(o.allowed_tools)==6
    assert o.env['ANTHROPIC_API_KEY']=='local-capability'

def test_premises_query_keeps_existing_intent_expansion(corpus):
    results=corpus.search('I want to build a bar in Agonda. What permissions apply?',3)['results']
    assert any('Building Construction' in e['title'] for e in results)

def test_preserved_answer_exclusions_survive_page_retrieval(corpus):
    r=ResearchTools(corpus);(doc,page),spans=next(iter(corpus.exclusions.items()))
    evidence=r.read({'document_id':doc,'page':page})['pages'][0]
    assert evidence['answer_excluded'] and spans[0][2] in evidence['warning']
    raw={'paragraphs':[{'text':'Claim','supports':[{'citation_id':evidence['id'],'quote':evidence['text'][:30]}]}],'clarification':None,'limitation':None,'followups':[]}
    with pytest.raises(ValueError):validate_answer(raw,r,'all')

def test_http_search_read_budget_gate_and_private_origin(monkeypatch,tmp_path):
    monkeypatch.setattr('backend.local_agent_app.budget',DevBudget(tmp_path))
    with TestClient(app) as client:
        assert client.get('/api/status').json()['chat_ready'] is False
        assert client.post('/api/chat',json={'question':'Building permission'}).status_code==503
        assert client.post('/api/dev/config',json={},headers={'origin':'https://example.org'}).status_code==403
        assert client.get('/api/status',headers={'host':'evil.example'}).status_code==403
        assert client.post('/provider/v1/messages',json={}).status_code==403
        result=client.get('/api/search',params={'q':'building permission','limit':1}).json()['results'][0]
        doc=result['document_id'];page=result['page']
        assert client.get('/api/documents/'+doc+'/pages',params={'start':page,'limit':1}).json()['pages'][0]['page']==page
        assert client.get('/api/documents/'+doc+'/text').status_code==200
        assert client.get('/api/dev/crm/search?collection=community&limit=1').json()['total_matches']==499

def test_expiry_preserves_visible_accounting_and_blocks_reservation(accounted):
    gate,*_=accounted
    path=gate.state/'reconciliation.json';receipt=json.loads(path.read_text())
    receipt['expires_at']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
    path.write_text(json.dumps(receipt))
    status=gate.status()
    assert not status['ready'] and status['reserved_usd']==.2 and status['remaining_usd']==1.8
    assert 'expired' in status['reason']
    with pytest.raises(BudgetUnavailable,match='expired'):gate.reserve(100)
    assert gate.status()['reserved_usd']==.2

def test_proxy_preserves_sdk_protocol_headers_and_reserves_before_dispatch(accounted,monkeypatch):
    import httpx
    from backend import local_agent_app as local
    gate,*_=accounted;sent=[];events=[]
    monkeypatch.setattr(local,'budget',gate)
    monkeypatch.setenv('ANTHROPIC_API_KEY','synthetic-server-key')
    monkeypatch.setattr(local,'provider_diagnostic',lambda **fields:events.append(fields))
    class FakeUpstream:
        def __init__(self,**kwargs):pass
        def build_request(self,method,url,**kwargs):return httpx.Request(method,url,**kwargs)
        async def send(self,request,**kwargs):
            assert gate.status()['reserved_usd']>.2
            sent.append(request)
            return httpx.Response(200,content=b'{"ok":true}',headers={'content-type':'application/json','request-id':'synthetic-request','x-should-retry':'false'})
        async def aclose(self):pass
    monkeypatch.setattr(local.httpx,'AsyncClient',FakeUpstream)
    with TestClient(app) as client:
        response=client.post('/provider/v1/messages?beta=true',json={'model':MODEL,'max_tokens':100,'messages':[{'role':'user','content':'Synthetic test'}]},headers={'x-api-key':local.PROXY_TOKEN,'anthropic-beta':'context-management-2025-06-27','anthropic-version':'2023-06-01','cookie':'must-not-forward'})
    assert response.status_code==200 and response.headers['request-id']=='synthetic-request'
    assert len(sent)==1 and str(sent[0].url)=='https://api.anthropic.com/v1/messages'
    assert sent[0].headers['anthropic-beta']=='context-management-2025-06-27'
    assert sent[0].headers['anthropic-version']=='2023-06-01'
    assert sent[0].headers['x-api-key']=='synthetic-server-key' and 'cookie' not in sent[0].headers
    assert events[0]['event']=='provider_response' and events[0]['status']==200

def test_proxy_missing_accounting_blocks_without_retry_or_provider(monkeypatch,tmp_path):
    from backend import local_agent_app as local
    monkeypatch.setattr(local,'budget',DevBudget(tmp_path))
    monkeypatch.setattr(local,'provider_diagnostic',lambda **fields:None)
    def never_provider(**kwargs):raise AssertionError('Must not create a provider client')
    monkeypatch.setattr(local.httpx,'AsyncClient',never_provider)
    with TestClient(app) as client:
        response=client.post('/provider/v1/messages',json={'model':MODEL,'max_tokens':100,'messages':[]},headers={'x-api-key':local.PROXY_TOKEN})
    assert response.status_code==429 and response.headers['x-should-retry']=='false'
