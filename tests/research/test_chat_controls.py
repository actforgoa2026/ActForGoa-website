"""Provider contracts and public cost controls; no live keys or paid calls."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
import json
import sqlite3
import httpx
from openai import OpenAI
import pytest
from backend.chat import (AnswerCache, ChatRequest, Message, prepare_answer,
                          answer_question, validate_answer, GroundedAnswer, MAX_PROMPT_BYTES, FRAMING_TOKEN_ALLOWANCE)
from backend.hosting import PublicLimits
from backend.providers import chat_config

@pytest.fixture
def config(monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','openrouter')
    monkeypatch.setenv('OPENROUTER_CHAT_MODEL','qwen/qwen3.7-flash')
    return chat_config()

@pytest.fixture
def evidence():
    return [{'id':'passage-1','title':'Khazan study','label':'Page 2',
             'text':'Sluice gates regulate tidal water in khazans.',
             'url':'https://example.org/study.pdf','generation':'generation-1',
             'raw_path':'private/path/not-for-model'}]

def completion(content,finish='stop'):
    return {'id':'fixture','object':'chat.completion','created':1,
            'model':'qwen/qwen3.7-flash','choices':[{'index':0,'finish_reason':finish,
            'message':{'role':'assistant','content':content}}]}

def test_openrouter_request_is_price_bounded_and_cited(config,evidence):
    captured=[]
    def handle(request):
        captured.append(request)
        return httpx.Response(200,json=completion(json.dumps({'status':'answered','paragraphs':[
            {'text':'Gates regulate tidal water.','citations':['passage-1']}]})))
    with OpenAI(api_key='fixture-only',base_url=config.base_url,max_retries=0,
                http_client=httpx.Client(transport=httpx.MockTransport(handle))) as client:
        answer=answer_question(client,config,prepare_answer(ChatRequest(question='How do khazans work?'),evidence))
    assert answer['citations']==evidence
    assert str(captured[0].url)=='https://openrouter.ai/api/v1/chat/completions'
    body=json.loads(captured[0].content)
    assert body['model']=='qwen/qwen3.7-flash' and body['max_tokens']==1800
    assert body['response_format']=={'type':'json_object'}
    assert body['reasoning']=={'enabled':False}
    assert body['provider']=={'only':['alibaba'],'allow_fallbacks':False,'require_parameters':True,
                             'data_collection':'deny','max_price':{'prompt':0.03,'completion':0.13,'request':0}}
    assert b'private/path' not in captured[0].content
    assert config.maximum_cost_microusd(26048)==1016

@pytest.mark.parametrize('payload,finish',[
    ('not JSON','stop'),
    (json.dumps({'status':'answered','paragraphs':[{'text':'Claim','citations':['invented']}]}),'stop'),
    (json.dumps({'status':'answered','paragraphs':[{'text':'Claim','citations':[]}]}),'stop'),
    (json.dumps({'status':'insufficient_evidence','paragraphs':[{'text':'Claim','citations':['passage-1']}]}),'stop'),
    (json.dumps({'status':'answered','paragraphs':[{'text':'Claim','citations':['passage-1']}]}),'length'),
])
def test_invalid_output_never_becomes_an_answer(config,evidence,payload,finish):
    with OpenAI(api_key='fixture-only',max_retries=0,http_client=httpx.Client(
            transport=httpx.MockTransport(lambda _:httpx.Response(200,json=completion(payload,finish))))) as client:
        with pytest.raises(ValueError):
            answer_question(client,config,prepare_answer(ChatRequest(question='Khazan water?'),evidence))

def test_multilingual_prompt_bound_preserves_question_and_recent_context(evidence):
    history=[Message(role='user' if i%2==0 else 'assistant',content='नदी'*1000) for i in range(8)]
    hits=[dict(evidence[0],id=f'passage-{i}',text='पाणी'*500) for i in range(10)]
    prepared=prepare_answer(ChatRequest(question='How does monsoon rainfall affect khazans?',history=history),hits)
    encoded=json.dumps(prepared.messages,ensure_ascii=False,separators=(',',':')).encode()
    assert len(encoded)<=MAX_PROMPT_BYTES
    assert prepared.input_token_bound==len(encoded)+FRAMING_TOKEN_ALLOWANCE<32000
    assert prepared.evidence and len(prepared.evidence)<10
    assert json.loads(prepared.messages[-1]['content'])['question'].startswith('How does monsoon')
    assert [e['id'] for e in json.loads(prepared.messages[-1]['content'])['evidence']]==[e['id'] for e in prepared.evidence]

def test_config_only_uses_reviewed_models_and_fixed_gateway(config,monkeypatch):
    monkeypatch.setenv('OPENROUTER_BASE_URL','https://untrusted.example/v1')
    assert chat_config().base_url=='https://openrouter.ai/api/v1'
    monkeypatch.setenv('OPENROUTER_CHAT_MODEL','expensive/unknown')
    with pytest.raises(ValueError,match='reviewed'):chat_config()

@pytest.mark.parametrize('url',['http://dashscope-intl.aliyuncs.com/compatible-mode/v1',
    'https://dashscope-intl.aliyuncs.com.evil.example/compatible-mode/v1',
    'https://secret@dashscope-intl.aliyuncs.com/compatible-mode/v1',
    'https://dashscope-intl.aliyuncs.com/compatible-mode/v1?forward=evil',
    'https://dashscope.aliyuncs.com/compatible-mode/v1'])
def test_direct_alibaba_credential_cannot_be_redirected(monkeypatch,url):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','qwen');monkeypatch.setenv('QWEN_BASE_URL',url)
    with pytest.raises(ValueError):chat_config()

def test_key_is_not_required_for_configuration_and_sdk_retries_are_disabled(config,monkeypatch):
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    assert config.client() is None
    monkeypatch.setenv('OPENROUTER_API_KEY','fixture-only')
    with config.client() as client:assert client.max_retries==0

def test_monthly_budget_survives_restart_and_concurrent_reservations(tmp_path):
    def reserve(_):return PublicLimits(tmp_path,chats_per_day=1000,monthly_usd='0.001').reserve_answer(100)
    with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(reserve,range(30)))
    assert sum(results)==10
    assert not PublicLimits(tmp_path,monthly_usd='0.001').reserve_answer(1)
    with sqlite3.connect(tmp_path/'answer-usage.sqlite') as db:
        assert db.execute('SELECT SUM(reserved_microusd) FROM spend').fetchone()[0]==1000
        assert db.execute('SELECT SUM(attempts) FROM usage').fetchone()[0]==10

def test_budget_rolls_over_by_utc_month_and_zero_disables(tmp_path,monkeypatch):
    import backend.hosting as hosting
    class January(datetime):
        @classmethod
        def now(cls,tz):return cls(2026,1,31,23,59,tzinfo=timezone.utc)
    class February(datetime):
        @classmethod
        def now(cls,tz):return cls(2026,2,1,0,0,tzinfo=timezone.utc)
    monkeypatch.setattr(hosting,'datetime',January)
    assert PublicLimits(tmp_path,monthly_usd='0.001').reserve_answer(1000)
    assert not PublicLimits(tmp_path,monthly_usd='0.001').reserve_answer(1)
    monkeypatch.setattr(hosting,'datetime',February)
    assert PublicLimits(tmp_path,monthly_usd='0.001').reserve_answer(1000)
    assert not PublicLimits(tmp_path/'zero',monthly_usd='0').reserve_answer(1)
    assert not PublicLimits(tmp_path/'daily-zero',chats_per_day=0).reserve_answer(1)

@pytest.mark.parametrize('budget',['-1','NaN','Infinity'])
def test_invalid_budget_fails_closed(tmp_path,budget):
    with pytest.raises(ValueError):PublicLimits(tmp_path,monthly_usd=budget)

def test_cache_expires_is_bounded_and_separates_model_generation_scope(config,evidence,monkeypatch):
    import backend.chat as chat
    now=[100.0];monkeypatch.setattr(chat.time,'monotonic',lambda:now[0])
    cache=AnswerCache(maximum=2,ttl=600)
    prepared=prepare_answer(ChatRequest(question='Khazan water?'),evidence)
    key=cache.key(config,prepared)
    answer={'paragraphs':[{'text':'Gates'}]};cache.put(key,answer);answer['paragraphs'].clear()
    copy=cache.get(key);assert copy['paragraphs'];copy['paragraphs'].clear();assert cache.get(key)['paragraphs']
    assert cache.key(replace(config,model='qwen/qwen3.8-flash'),prepared)!=key
    changed=prepare_answer(ChatRequest(question='Khazan water?'),[dict(evidence[0],generation='new')])
    assert cache.key(config,changed)!=key
    cache.put('2',{});cache.put('3',{});assert cache.get(key) is None
    cache.put(key,{'answer':'cached'});now[0]+=600;assert cache.get(key) is None

def test_brief_answer_has_separate_cache_and_enforced_bound(config,evidence):
    brief=prepare_answer(ChatRequest(question='Khazan water?',answer_style='brief'),evidence)
    standard=prepare_answer(ChatRequest(question='Khazan water?'),evidence)
    assert AnswerCache.key(config,brief)!=AnswerCache.key(config,standard)
    answer=GroundedAnswer.model_validate({'status':'answered','paragraphs':[{'text':'Gates regulate water.','citations':['passage-1']}]})
    assert validate_answer(answer,evidence,brief.answer_style)['status']=='answered'
    answer.paragraphs[0].text='word '*121
    with pytest.raises(ValueError,match='length bound'):validate_answer(answer,evidence,brief.answer_style)
    answer.paragraphs[0].text='Gates.';answer.paragraphs*=3
    with pytest.raises(ValueError,match='length bound'):validate_answer(answer,evidence,brief.answer_style)
    with pytest.raises(ValueError):ChatRequest(question='Khazan water?',answer_style='unbounded')

def test_prompt_retains_legal_provenance_without_internal_metadata(evidence):
    meta={'publisher_class':'government_or_court','legal_currency':'not_consolidated_or_legally_verified',
          'source_date_metadata':[{'field':'citation_publication_date','value':'2025-01-01'}],'topics':['water'],
          'page_context':'National report: Arunachal Pradesh. This section is not Goa.',
          'document_kind_hint':'report','guide_verification':{'status':'source_verified'}}
    prepared=prepare_answer(ChatRequest(question='What does the water policy require?'),[dict(evidence[0],**meta)])
    sent=json.loads(prepared.messages[-1]['content'])['evidence'][0]
    assert all(sent[k]==v for k,v in meta.items())
    assert 'raw_path' not in sent

def test_default_five_dollar_budget_is_enforced_across_instances(tmp_path):
    assert PublicLimits(tmp_path).reserve_answer(5_000_000)
    assert not PublicLimits(tmp_path).reserve_answer(1)

def test_legal_authority_preference_preserves_relevance_and_nonlegal_order():
    from backend.library import authority_score
    official={'publisher_class':'government_or_court'}
    commentary={'publisher_class':'civil_society_or_commentary'}
    assert authority_score(.02,official,True)>authority_score(.021,commentary,True)
    assert authority_score(.01,official,True)<authority_score(.03,commentary,True)
    assert authority_score(.02,official,False)==authority_score(.02,commentary,False)

def test_inline_internal_ids_are_removed_without_removing_facts(evidence):
    answer=GroundedAnswer.model_validate({'status':'answered','paragraphs':[{
        'text':'The policy (2025) proposes monitoring (passage-1). Read it [passage-1].',
        'citations':['passage-1']}]})
    result=validate_answer(answer,evidence)
    assert result['paragraphs'][0]['text']=='The policy (2025) proposes monitoring. Read it.'
    assert result['paragraphs'][0]['citations']==['passage-1']

def test_schema_bounded_partial_sentence_is_not_a_complete_answer(evidence):
    answer=GroundedAnswer.model_validate({'status':'answered','paragraphs':[{'text':'The application fee is the','citations':['passage-1']}]})
    with pytest.raises(ValueError,match='incomplete'):validate_answer(answer,evidence,'brief')

def test_selected_model_uses_strict_schema_correct_prices_and_disclosure(evidence,monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','openrouter');monkeypatch.delenv('OPENROUTER_CHAT_MODEL',raising=False)
    config=chat_config();captured=[]
    assert config.model=='openai/gpt-5.6-luna' and config.label=='OpenRouter and OpenAI'
    def handle(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200,json=completion(json.dumps({'status':'answered','paragraphs':[{'text':'Gates regulate water.','citations':['passage-1']}]})))
    with OpenAI(api_key='fixture-only',base_url=config.base_url,max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(handle))) as client:
        answer_question(client,config,prepare_answer(ChatRequest(question='Khazan water?',answer_style='brief'),evidence))
    body=captured[0];assert body['response_format']['type']=='json_schema'
    schema=body['response_format']['json_schema']['schema']
    assert '$defs' not in schema and schema['properties']['paragraphs']['maxItems']==1
    assert schema['properties']['paragraphs']['items']['properties']['citations']['items']['enum']==['passage-1']
    assert body['reasoning']=={'effort':'low'} and 'temperature' not in body
    assert body['provider']['only']==['openai'] and body['provider']['allow_fallbacks'] is False
    assert body['provider']['max_price']=={'prompt':.2,'completion':1.2,'request':0}
    assert config.maximum_cost_microusd(26048)==9410

@pytest.mark.parametrize('kind',['legislation_or_notification','official_procedure','SOP','final_policy'])
def test_legal_currency_limitation_is_returned_with_cited_legal_answer(evidence,kind):
    evidence[0]['document_kind_hint']=kind
    answer=GroundedAnswer.model_validate({'status':'answered','paragraphs':[{'text':'The saved Act requires permission.','citations':['passage-1']}]})
    result=validate_answer(answer,evidence,'brief')
    assert 'current consolidated status is not verified' in result['notice']
