"""Native Anthropic contracts using synthetic responses only; never live keys."""
from dataclasses import replace
import json
import sqlite3

import httpx
import pytest

from backend.anthropic_provider import (AnthropicAPIError, AnthropicClient, API_VERSION,
                                        INPUT_ALLOWANCE, native_schema)
from backend.chat import ChatRequest, Message, prepare_answer, answer_question, AnswerCache
from backend.hosting import PublicLimits
from backend.providers import chat_config


@pytest.fixture
def config(monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER', 'anthropic')
    monkeypatch.delenv('ANTHROPIC_CHAT_MODEL', raising=False)
    return chat_config()


@pytest.fixture
def prepared():
    evidence = [{'id': 'passage-1', 'title': 'Khazan study', 'label': 'Page 2',
                 'text': 'Sluice gates regulate tidal water in khazans.',
                 'url': 'https://example.org/study.pdf', 'generation': 'generation-1',
                 'raw_path': 'private/path/not-for-model'}]
    return prepare_answer(ChatRequest(question='How do khazans work?', answer_style='brief',
        history=[Message(role='user', content='Tell me about khazans.'),
                 Message(role='assistant', content='Earlier context is not evidence.')]), evidence,provider='anthropic')


def answer_payload(citation='passage-1'):
    return {'status': 'answered', 'paragraphs': [
        {'text': 'Gates regulate tidal water.', 'citations': [citation]}]}


def anthropic_message(payload=None, *, stop='end_turn', content=None):
    return {'id': 'fixture-only', 'type': 'message', 'role': 'assistant',
            'model': 'claude-haiku-5-5', 'stop_reason': stop, 'stop_details': None,
            'content': content if content is not None else [
                {'type': 'thinking', 'thinking': 'private diagnostic', 'signature': 'fixture'},
                {'type': 'text', 'text': json.dumps(payload if payload is not None else answer_payload())}],
            'usage': {'input_tokens': 1000, 'output_tokens': 250}}


def brief_message(payload=None, **kwargs):
    payload=answer_payload() if payload is None else payload
    if isinstance(payload,dict) and set(payload)=={'status','paragraphs'} and len(payload['paragraphs'])<=1:
        payload={'status':payload['status'],'paragraph':payload['paragraphs'][0] if payload['paragraphs'] else None}
    return anthropic_message(payload,**kwargs)


def test_native_request_keeps_schema_ids_history_and_cost_controls(config, prepared):
    requests = []
    def handle(request):
        requests.append(request)
        return httpx.Response(200, json=brief_message())
    with AnthropicClient('fixture-only', 'wrkspc_fixture', transport=httpx.MockTransport(handle)) as client:
        result = answer_question(client, config, prepared)
    assert result['citations'] == prepared.evidence
    assert len(requests) == 1
    request = requests[0]; body = json.loads(request.content)
    assert str(request.url) == 'https://api.anthropic.com/v1/messages'
    assert request.headers['authorization'] == 'Bearer fixture-only'
    assert request.headers['anthropic-version'] == API_VERSION == '2026-10-21'
    assert request.headers['anthropic-workspace-id'] == 'wrkspc_fixture'
    assert request.extensions['timeout'] == {'connect': 10, 'read': 60, 'write': 10, 'pool': 10}
    assert body['model'] == 'claude-haiku-5-5' and body['max_tokens'] == 3500
    assert body['system'].startswith(prepared.base_instructions)
    assert 'Every paragraphs entry' not in body['system']
    assert json.loads(body['system'].split('Return JSON conforming to this inline schema: ',1)[1])==body['output_config']['format']['schema']
    assert body['messages'] == prepared.messages[1:]
    assert body['thinking'] == {'type': 'adaptive'}
    assert body['service_tier'] == 'standard_only' and body['stream'] is False
    assert set(body) == {'model', 'max_tokens', 'system', 'messages', 'thinking', 'stream', 'output_config', 'service_tier'}
    assert body['output_config']['effort'] == 'medium'
    assert body['output_config']['format']['type'] == 'json_schema'
    schema = body['output_config']['format']['schema']
    assert set(schema['properties'])=={'status','paragraph'}
    assert schema['properties']['paragraph']['anyOf'][1]=={'type':'null'}
    paragraph = schema['properties']['paragraph']['anyOf'][0]
    assert paragraph['properties']['citations']['items']['enum'] == ['passage-1']
    assert paragraph['additionalProperties'] is False and schema['additionalProperties'] is False
    assert paragraph['properties']['citations']['minItems'] == 1
    assert all(key not in json.dumps(schema) for key in ('maxItems', 'maxLength', 'minLength'))
    assert prepared.schema['properties']['paragraphs']['maxItems'] == 1
    assert b'private/path' not in request.content and b'fixture-only' not in request.content
    assert 'private diagnostic' not in json.dumps(result)
    assert config.maximum_cost_microusd(26048) == 5174


def test_anthropic_is_opt_in_fixed_host_and_requires_reviewed_model(config, monkeypatch):
    monkeypatch.setenv('ANTHROPIC_BASE_URL', 'https://untrusted.example')
    assert chat_config().base_url == 'https://api.anthropic.com/v1'
    monkeypatch.setenv('ANTHROPIC_CHAT_MODEL', 'claude-unreviewed')
    with pytest.raises(ValueError, match='reviewed'):chat_config()
    monkeypatch.delenv('RESEARCH_CHAT_PROVIDER')
    assert chat_config().provider == 'openrouter'


def test_missing_key_and_optional_workspace(config, monkeypatch, prepared):
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    assert config.client() is None
    monkeypatch.setenv('ANTHROPIC_API_KEY', 'fixture-only')
    monkeypatch.setenv('ANTHROPIC_WORKSPACE_ID', 'wrkspc_fixture')
    with config.client() as client:
        assert client._http.headers['anthropic-workspace-id'] == 'wrkspc_fixture'
        assert client._http.follow_redirects is False
    def handle(request):
        assert 'anthropic-workspace-id' not in request.headers
        return httpx.Response(200, json=brief_message())
    with AnthropicClient('fixture-only', transport=httpx.MockTransport(handle)) as client:
        answer_question(client, config, prepared)


@pytest.mark.parametrize('status', [301, 307, 400, 401, 402, 403, 429, 500, 529])
def test_http_failures_are_sanitized_with_no_redirect_retry_or_fallback(config, prepared, status):
    calls = []
    def handle(request):
        calls.append(request)
        return httpx.Response(status, headers={'location': 'https://untrusted.example'},
                              json={'error': {'message': 'private diagnostic fixture-only'}})
    with AnthropicClient('fixture-only', transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(AnthropicAPIError) as error:answer_question(client, config, prepared)
    assert error.value.status_code == status and str(error.value) == 'Anthropic request failed'
    assert len(calls) == 1 and calls[0].url.host == 'api.anthropic.com'


@pytest.mark.parametrize('error_class', [httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError])
def test_transport_errors_are_sanitized_and_not_retried(config, prepared, error_class):
    calls = []
    def handle(request):
        calls.append(request)
        raise error_class('private diagnostic fixture-only', request=request)
    with AnthropicClient('fixture-only', transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(AnthropicAPIError) as error:answer_question(client, config, prepared)
    assert len(calls) == 1 and str(error.value) == 'Anthropic request failed'


@pytest.mark.parametrize('stop', ['refusal', 'max_tokens', 'model_context_window_exceeded', 'tool_use', 'pause_turn', None])
def test_only_completed_end_turn_answers_are_accepted(config, prepared, stop):
    with AnthropicClient('fixture-only', transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=brief_message(stop=stop)))) as client:
        with pytest.raises(ValueError, match='incomplete or declined'):answer_question(client, config, prepared)


@pytest.mark.parametrize('message', [
    [], {}, {'type': 'message', 'model': 'other-model', 'role': 'assistant'},
    {**brief_message(), 'stop_details': {'type': 'refusal', 'explanation': 'private diagnostic'}},
    brief_message(content=[]), brief_message(content=[{'type': 'thinking'}]),
    brief_message(content=[{'type': 'text', 'text': 123}]),
    brief_message(content=[{'type': 'tool_use', 'name': 'private diagnostic'}]),
    brief_message(content=[{'type': 'text', 'text': 'not JSON'}]),
    brief_message(answer_payload('invented')),
    brief_message({'status': 'answered', 'paragraphs': [{'text': 'No citation.', 'citations': []}]}),
    brief_message({'status': 'answered', 'paragraphs': [{'text': 'Incomplete sentence', 'citations': ['passage-1']}]}),
    brief_message({'status': 'answered', 'paragraphs': [{'text': 'x'*6001+'.', 'citations': ['passage-1']}]}),
    brief_message({'status': 'answered', 'paragraphs': [{'text': 'Too many citations.', 'citations': ['passage-1']*11}]}),
    brief_message({'status': 'answered', 'paragraphs': [], 'private diagnostic': 'fixture-only'}),
    brief_message({'status': 'answered', 'paragraphs': answer_payload()['paragraphs']*2}),
    brief_message({'status': 'insufficient_evidence', 'paragraphs': answer_payload()['paragraphs']}),
])
def test_malformed_unverified_and_overlong_answers_fail_closed(config, prepared, message):
    with AnthropicClient('fixture-only', transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=message))) as client:
        with pytest.raises(ValueError) as error:answer_question(client, config, prepared)
    assert 'private diagnostic' not in str(error.value) and 'fixture-only' not in str(error.value)


def test_split_text_blocks_and_abstention(config, prepared):
    payload = json.dumps({'status': 'insufficient_evidence', 'paragraph': None})
    message = brief_message(content=[{'type': 'redacted_thinking', 'data': 'private diagnostic'},
        {'type': 'text', 'text': payload[:20]}, {'type': 'text', 'text': payload[20:]}])
    with AnthropicClient('fixture-only', transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=message))) as client:
        result = answer_question(client, config, prepared)
    assert result['status'] == 'insufficient_evidence' and result['citations'] == []


def test_bound_covers_native_schema_and_rejects_unreviewed_tier_before_dispatch(config, prepared):
    assert 26048 + INPUT_ALLOWANCE < 100_000
    assert config.maximum_cost_microusd(100_000 - INPUT_ALLOWANCE) == 11750
    with pytest.raises(ValueError, match='price tier'):config.maximum_cost_microusd(100_001 - INPUT_ALLOWANCE)
    with pytest.raises(ValueError, match='schema exceeds'):native_schema({'description': 'x'*4097})
    def handle(_):raise AssertionError('Invalid bounds must prevent dispatch')
    with AnthropicClient('fixture-only', transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(ValueError, match='prompt exceeds'):
            answer_question(client, config, replace(prepared, input_token_bound=1))
        with pytest.raises(ValueError, match='schema exceeds'):
            answer_question(client, config, replace(prepared, schema={'description': 'x'*4097}))


def test_budget_and_cache_separate_provider_but_not_allowance(config, prepared, tmp_path, monkeypatch):
    anthropic_cost = config.maximum_cost_microusd(prepared.input_token_bound)
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER', 'openrouter')
    other = chat_config()
    other_cost = other.maximum_cost_microusd(prepared.input_token_bound)
    assert AnswerCache.key(config, prepared) != AnswerCache.key(other, prepared)
    assert PublicLimits(tmp_path).reserve_answer(other_cost)
    assert PublicLimits(tmp_path).reserve_answer(anthropic_cost)
    with sqlite3.connect(tmp_path/'answer-usage.sqlite') as db:
        assert db.execute('SELECT SUM(reserved_microusd) FROM spend').fetchone()[0] == other_cost + anthropic_cost
        assert db.execute('SELECT SUM(attempts) FROM usage').fetchone()[0] == 2
    assert PublicLimits(tmp_path).reserve_answer(5_000_000 - other_cost - anthropic_cost)
    assert not PublicLimits(tmp_path).reserve_answer(anthropic_cost)


def test_native_brief_roundtrip_preserves_exact_text_citations_and_word_bound(config,prepared):
    for count in (120,121):
        paragraph={'text':'word '*(count-1)+'end.','citations':['passage-1']}
        with AnthropicClient('fixture-only',transport=httpx.MockTransport(
                lambda _:httpx.Response(200,json=anthropic_message({'status':'answered','paragraph':paragraph})))) as client:
            if count==120:
                result=answer_question(client,config,prepared)
                assert result['paragraphs']==[paragraph] and result['citations']==prepared.evidence
            else:
                with pytest.raises(ValueError,match='length bound'):answer_question(client,config,prepared)


@pytest.mark.parametrize('payload',[
    {'status':'answered','paragraph':None},
    {'status':'insufficient_evidence','paragraph':answer_payload()['paragraphs'][0]},
    {'status':'answered','paragraph':answer_payload()['paragraphs']},
    {'status':'answered','paragraphs':answer_payload()['paragraphs']},
    {'status':'answered','paragraph':answer_payload()['paragraphs'][0],'extra':'private diagnostic'},
    {'status':'answered','paragraph':{'text':'Supported.','citations':['passage-1'],'extra':'private diagnostic'}},
])
def test_native_brief_rejects_wrong_shape_before_mapping(config,prepared,payload):
    with AnthropicClient('fixture-only',transport=httpx.MockTransport(
            lambda _:httpx.Response(200,json=anthropic_message(payload)))) as client:
        with pytest.raises(ValueError,match='native brief answer did not match'):
            answer_question(client,config,prepared)


def test_standard_native_array_and_prompt_are_unchanged(config,prepared):
    standard=prepare_answer(ChatRequest(question='How do gates regulate tides?'),prepared.evidence,provider='anthropic')
    payload={'status':'answered','paragraphs':answer_payload()['paragraphs']*2}
    def handle(request):
        body=json.loads(request.content)
        assert body['system']==standard.messages[0]['content']
        assert set(body['output_config']['format']['schema']['properties'])=={'status','paragraphs'}
        return httpx.Response(200,json=anthropic_message(payload))
    with AnthropicClient('fixture-only',transport=httpx.MockTransport(handle)) as client:
        assert answer_question(client,config,standard)['paragraphs']==payload['paragraphs']


def test_native_brief_actual_prompt_and_schema_fit_reserved_allowances(config,prepared):
    from backend.anthropic_provider import message_request,MAX_SCHEMA_BYTES
    from backend.chat import Message
    evidence=[dict(prepared.evidence[0],id=f'p-{i}',text='नदी '*300) for i in range(10)]
    request=ChatRequest(question='नदी '*400,answer_style='brief',history=[Message(role='user',content='पाणी '*700)])
    bounded=prepare_answer(request,evidence,provider='anthropic');body=message_request(config,bounded)
    messages=[{'role':'system','content':body['system']},*body['messages']]
    actual=len(json.dumps(messages,ensure_ascii=False,separators=(',',':')).encode())
    assert actual<=24000 and actual+2048==bounded.input_token_bound
    assert len(json.dumps(body['output_config']['format']['schema'],ensure_ascii=False,separators=(',',':')).encode())<=MAX_SCHEMA_BYTES
    assert config.maximum_cost_microusd(bounded.input_token_bound)<=5174
    with pytest.raises(ValueError,match='Missing native brief instructions'):
        message_request(config,replace(prepared,base_instructions=None))


def test_native_brief_budgets_final_contract_before_selecting_evidence(config):
    from backend.anthropic_provider import message_request
    evidence=[{'id':f'{i:029d}','text':'x'*(17030 if i==0 else 1),'title':'Saved source',
               'document_id':str(i),'url':'https://example.org/source'} for i in range(10)]
    request=ChatRequest(question='What does this saved source say?',answer_style='brief')
    prepared=prepare_answer(request,evidence,provider='anthropic');body=message_request(config,prepared)
    messages=[{'role':'system','content':body['system']},*body['messages']]
    actual=len(json.dumps(messages,ensure_ascii=False,separators=(',',':')).encode())
    assert actual<=24000 and prepared.input_token_bound==actual+2048
    ids=[e['id'] for e in prepared.evidence]
    wire=body['output_config']['format']['schema']
    assert wire['properties']['paragraph']['anyOf'][0]['properties']['citations']['items']['enum']==ids
    assert [e['id'] for e in json.loads(body['messages'][-1]['content'])['evidence']]==ids
    assert json.loads(body['system'].split('Return JSON conforming to this inline schema: ')[1])==wire
    # A caller cannot spend the framing reserve as extra prompt space.
    oversized=[*prepared.messages[:-1],{'role':'user','content':'x'*24000}]
    with pytest.raises(ValueError,match='reserved allowance'):
        message_request(config,replace(prepared,messages=oversized,input_token_bound=26048))
