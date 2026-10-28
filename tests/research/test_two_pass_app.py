"""HTTP path checks using synthetic evidence, temp ledgers and fake provider I/O."""
import asyncio
import json
import threading

import httpx
import pytest
from fastapi.testclient import TestClient

from backend import app as app_module
from backend.async_anthropic import AsyncAnthropicClient
from backend.usage_reconciliation import inspect_ledger
from tests.research.test_answer_pipeline import Transport, model_response
from tests.research.test_reconstruction import claim
from tests.research.span_fixtures import select_response


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','anthropic')
    monkeypatch.setenv('ANTHROPIC_CHAT_MODEL','claude-haiku-5-5')
    monkeypatch.setenv('ANTHROPIC_CHAT_EFFORT','medium')
    monkeypatch.setenv('ANTHROPIC_ANSWER_PIPELINE','two_pass_v9')
    monkeypatch.delenv('RESEARCH_PUBLIC_ORIGIN',raising=False)
    monkeypatch.setenv('RESEARCH_USAGE_ROOT',str(tmp_path/'usage'))
    monkeypatch.setenv('RESEARCH_MONTHLY_ANSWER_BUDGET_USD','5')
    monkeypatch.setenv('RESEARCH_DAILY_ANSWER_LIMIT','100')
    evidence=[{'id':'a','text':'Gates regulate tidal water. Design must follow Appendix C.'}]
    class Library:
        generation='fixture'
        manifest={'stats':{}}
        def __init__(self,*args):self.queries=[]
        def search(self,*args):self.queries.append(args);return evidence
    monkeypatch.setattr(app_module,'Library',Library)
    transports=[]
    async def handler(request,n):
        body=json.loads(request.content);brief='paragraph' in body['output_config']['format']['schema']['properties']
        unit=claim() if n==1 else {'claims':[claim('Design must follow Appendix C.',quote='Design must follow Appendix C.')]}
        native={'status':'answered',**({'paragraph':unit} if brief else {'paragraphs':[unit]})}
        native=select_response(native,json.loads(body['messages'][-1]['content']))
        return model_response(native)
    handlers=[handler]
    def factory():
        transport=Transport(handlers[0]);transports.append(transport)
        return AsyncAnthropicClient('fixture-only',transport=transport)
    app=app_module.create_app(tmp_path,async_client_factory=factory)
    return app,evidence,transports,handlers,tmp_path/'usage'/'answer-usage.sqlite'


def test_http_final_only_cache_styles_history_and_source_search(setup):
    app,evidence,transports,_,ledger=setup
    with TestClient(app) as client:
        assert client.get('/api/status').json()['answer_pipeline']=='two_pass_v9'
        question={'question':'What do the sources say about these gates?'}
        answer=client.post('/api/chat',json=question)
        assert answer.status_code==200 and answer.json()['paragraphs'][0]['text']=='Design must follow Appendix C.'
        assert answer.headers['cache-control']=='private, no-store'
        assert 'draft' not in answer.text and 'claims' not in answer.text
        assert client.post('/api/chat',json=question).json()==answer.json() and len(transports)==1
        assert client.post('/api/chat',json={**question,'answer_style':'brief'}).status_code==200
        follow={'question':'What about design?','history':[{'role':'user','content':question['question']},
                                                       {'role':'assistant','content':answer.json()['paragraphs'][0]['text']}]}
        for _ in range(2):assert client.post('/api/chat',json=follow).status_code==200
        assert len(transports)==4 and all(len(t.requests)==2 and t.closed for t in transports)
        body=json.loads(transports[2].requests[1].content)
        assert body['messages'][:-1]==follow['history']
        assert app.state.library.queries[-1][0].startswith('What about design? What do')
        assert client.get('/api/search',params={'q':'gates'}).json()['results']==evidence
        assert client.post('/api/chat',json=question,headers={'origin':'https://evil.example'}).status_code==403
    assert sum(inspect_ledger(ledger)['days'].values())==8


def test_http_second_phase_failure_never_returns_or_caches_draft(setup):
    app,_,transports,handlers,ledger=setup;good=handlers[0]
    async def broken(request,n):
        return await good(request,n) if n==1 else httpx.Response(500,json={'secret':'private provider message'})
    handlers[0]=broken
    with TestClient(app) as client:
        question={'question':'What do gates do?'}
        failed=client.post('/api/chat',json=question)
        assert failed.status_code==502 and 'Gates regulate' not in failed.text and 'private provider' not in failed.text
        handlers[0]=good
        assert client.post('/api/chat',json=question).status_code==200
        assert len(transports)==2
    assert sum(inspect_ledger(ledger)['days'].values())==4


@pytest.mark.parametrize('style',['standard','brief'])
@pytest.mark.parametrize('phase',[1,2])
def test_duplicate_final_json_never_reaches_http_answer_or_cache(setup,style,phase):
    app,_,transports,handlers,ledger=setup;good=handlers[0]
    async def broken(request,n):
        response=await good(request,n)
        if n!=phase:return response
        payload=response.json()
        text=payload['content'][-1]['text']
        payload['content'][-1]['text']=text.replace('"status":','"status":"hidden-fixture","status":',1)
        return httpx.Response(200,json=payload)
    handlers[0]=broken
    with TestClient(app) as client:
        question={'question':'What do gates do?','answer_style':style}
        failed=client.post('/api/chat',json=question)
        assert failed.status_code==502
        assert 'Gates regulate' not in failed.text and 'hidden-fixture' not in failed.text
        assert len(transports)==1 and len(transports[0].requests)==phase
        handlers[0]=good
        assert client.post('/api/chat',json=question).status_code==200
        assert len(transports)==2 and len(transports[1].requests)==2
    assert sum(inspect_ledger(ledger)['days'].values())==phase+2


def test_no_evidence_has_no_provider_or_budget_write(setup):
    app,evidence,transports,_,ledger=setup;evidence.clear()
    with TestClient(app) as client:
        result=client.post('/api/chat',json={'question':'What evidence exists?'})
        assert result.status_code==200 and result.json()['status']=='insufficient_evidence'
    assert not transports and not ledger.exists()


def scope():
    return {'type':'http','http_version':'1.1','asgi':{'version':'3.0'},'method':'POST',
            'scheme':'http','path':'/api/chat','raw_path':b'/api/chat','query_string':b'',
            'headers':[(b'host',b'testserver'),(b'content-type',b'application/json')],
            'client':('127.0.0.1',1234),'server':('testserver',80),'root_path':''}


def test_actual_asgi_disconnect_cancels_provider_and_does_not_cache(setup):
    app,_,transports,handlers,ledger=setup;good=handlers[0]
    async def scenario():
        entered=asyncio.Event();incoming=asyncio.Queue();sent=[]
        async def slow(request,n):
            if n==2:entered.set();await asyncio.sleep(10)
            return await good(request,n)
        handlers[0]=slow
        await incoming.put({'type':'http.request','body':json.dumps({'question':'What do gates do?'}).encode()})
        async def send(message):sent.append(message)
        async with app.router.lifespan_context(app):
            task=asyncio.create_task(app(scope(),incoming.get,send))
            await asyncio.wait_for(entered.wait(),1)
            await incoming.put({'type':'http.disconnect'})
            await asyncio.wait_for(task,1)
            assert transports[0].closed and transports[0].cancelled
            assert next(m['status'] for m in sent if m['type']=='http.response.start')==499
            assert b'Gates regulate' not in b''.join(m.get('body',b'') for m in sent)
            handlers[0]=good
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://testserver') as client:
                assert (await client.post('/api/chat',json={'question':'What do gates do?'})).status_code==200
            assert len(transports)==2
    asyncio.run(scenario())
    assert sum(inspect_ledger(ledger)['days'].values())==4


def test_entry_deadline_includes_body_and_retrieval_before_dispatch(setup,monkeypatch):
    app,_,transports,_,ledger=setup
    monkeypatch.setattr(app_module,'PROVIDER_DEADLINE_SECONDS',.01)
    async def scenario():
        messages=[]
        async def receive():
            await asyncio.sleep(.025)
            return {'type':'http.request','body':b'{"question":"What do gates do?"}'}
        async def send(message):messages.append(message)
        async with app.router.lifespan_context(app):
            await app(scope(),receive,send)
        assert next(m['status'] for m in messages if m['type']=='http.response.start')==504
    asyncio.run(scenario())
    assert not transports and not ledger.exists()


def test_native_cancellation_joins_worker_and_releases_chat_slot(setup):
    app,_,transports,handlers,ledger=setup
    entered=threading.Event();release=threading.Event();finished=threading.Event()
    async def scenario():
        async with app.router.lifespan_context(app):
            original=app.state.library.search
            def blocked(*args):entered.set();release.wait();finished.set();return original(*args)
            app.state.library.search=blocked
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://testserver') as client:
                task=asyncio.create_task(client.post('/api/chat',json={'question':'What do gates do?'}))
                while not entered.is_set():await asyncio.sleep(.001)
                task.cancel();await asyncio.sleep(.01)
                assert not task.done() and not finished.is_set()
                release.set()
                with pytest.raises(asyncio.CancelledError):await task
                assert finished.is_set() and not transports and not ledger.exists()
                app.state.library.search=original
                assert (await client.post('/api/chat',json={'question':'What do gates do?'})).status_code==200
    asyncio.run(scenario())
