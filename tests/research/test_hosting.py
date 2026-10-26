import sqlite3
import pytest
from backend.hosting import public_config,PublicLimits,RequestSizeLimit
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

def test_public_configuration_is_explicit(monkeypatch):
    monkeypatch.setenv('RESEARCH_PUBLIC_ORIGIN','https://actforgoa-field-guide.vercel.app')
    monkeypatch.delenv('RESEARCH_PUBLISH_CORPUS',raising=False)
    with pytest.raises(ValueError):public_config()
    monkeypatch.setenv('RESEARCH_PUBLISH_CORPUS','1')
    monkeypatch.setenv('RAILWAY_PUBLIC_DOMAIN','research.example.up.railway.app')
    origin,hosts=public_config()
    assert origin=='https://actforgoa-field-guide.vercel.app'
    assert 'research.example.up.railway.app' in hosts and '*' not in hosts
    monkeypatch.setenv('RESEARCH_ALLOWED_HOSTS','*')
    with pytest.raises(ValueError):public_config()

def test_public_limits_persist_attempt_budget(tmp_path):
    limiter=PublicLimits(tmp_path,search_per_minute=2,chats_per_day=2)
    assert limiter.allow_search() and limiter.allow_search() and not limiter.allow_search()
    assert limiter.reserve_answer() and limiter.reserve_answer() and not limiter.reserve_answer()
    assert not PublicLimits(tmp_path,chats_per_day=2).reserve_answer()
    with sqlite3.connect(tmp_path/'answer-usage.sqlite') as db:assert db.execute('SELECT attempts FROM usage').fetchone()[0]==2

def test_request_size_limit_rejects_streaming_body():
    async def echo(request:Request):return JSONResponse({'bytes':len(await request.body())})
    app=Starlette(routes=[Route('/api/chat',echo,methods=['POST'])]);app.add_middleware(RequestSizeLimit,maximum=16)
    with TestClient(app) as client:
        assert client.post('/api/chat',content=b'hello').json()=={'bytes':5}
        assert client.post('/api/chat',content=(b'1234567890' for _ in range(2))).status_code==413
