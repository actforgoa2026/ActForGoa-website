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


def native_payload(payload):
    """Explicit synthetic wire fixture; never used by runtime normalization."""
    from copy import deepcopy
    result=deepcopy(payload)
    units=result.get('paragraphs', [result.get('paragraph')])
    for unit in units:
        if isinstance(unit,dict) and 'citations' in unit:
            unit['supports']=[{'citation_id':c,'field':'text','quote':'regulate tidal water'}
                              for c in unit.pop('citations')]
            unit['primary_support']=unit['supports'].pop(0) if unit['supports'] else None
    return result


def anthropic_message(payload=None, *, stop='end_turn', content=None):
    return {'id': 'fixture-only', 'type': 'message', 'role': 'assistant',
            'model': 'claude-haiku-5-5', 'stop_reason': stop, 'stop_details': None,
            'content': content if content is not None else [
                {'type': 'thinking', 'thinking': 'private diagnostic', 'signature': 'fixture'},
                {'type': 'text', 'text': json.dumps(payload if payload is not None else native_payload(answer_payload()))}],
            'usage': {'input_tokens': 1000, 'output_tokens': 250}}


def brief_message(payload=None, **kwargs):
    payload=answer_payload() if payload is None else payload
    if isinstance(payload,dict) and set(payload)=={'status','paragraphs'} and len(payload['paragraphs'])<=1:
        payload={'status':payload['status'],'paragraph':payload['paragraphs'][0] if payload['paragraphs'] else None}
    return anthropic_message(native_payload(payload),**kwargs)


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
    assert body['model'] == 'claude-haiku-5-5' and body['max_tokens'] == 9000
    assert body['system'].startswith('You answer questions about Goa')
    assert 'Every paragraphs entry' not in body['system']
    assert 'Each object has text, primary_support and supports only' in body['system']
    assert 'inline schema' not in body['system']
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
    assert paragraph['properties']['supports']['items']['properties']['citation_id']['enum'] == ['passage-1']
    assert paragraph['additionalProperties'] is False and schema['additionalProperties'] is False
    assert paragraph['properties']['primary_support']['properties']['field']['enum'] == ['text']
    assert 'primary_support' in paragraph['required']
    assert all(key not in json.dumps(schema) for key in ('maxItems', 'maxLength', 'minLength'))
    assert prepared.schema['properties']['paragraphs']['maxItems'] == 1
    assert b'private/path' not in request.content and b'fixture-only' not in request.content
    assert 'private diagnostic' not in json.dumps(result)
    assert config.maximum_cost_microusd(26048) == 7924


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
    assert config.maximum_cost_microusd(100_000 - INPUT_ALLOWANCE) == 14500
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
                lambda _:httpx.Response(200,json=anthropic_message(native_payload({'status':'answered','paragraph':paragraph}))))) as client:
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
        with pytest.raises(ValueError,match='native answer did not match'):
            answer_question(client,config,prepared)


def test_standard_native_array_maps_claim_units_losslessly(config,prepared):
    standard=prepare_answer(ChatRequest(question='How do gates regulate tides?'),prepared.evidence,provider='anthropic')
    payload={'status':'answered','paragraphs':answer_payload()['paragraphs']*2}
    def handle(request):
        body=json.loads(request.content)
        assert body['system']==standard.messages[0]['content']
        assert set(body['output_config']['format']['schema']['properties'])=={'status','paragraphs'}
        return httpx.Response(200,json=anthropic_message(native_payload(payload)))
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
    assert config.maximum_cost_microusd(bounded.input_token_bound)<=7924
    with pytest.raises(ValueError,match='Missing native answer instructions'):
        message_request(config,replace(prepared,base_instructions=None))


def test_native_brief_budgets_final_contract_before_selecting_evidence(config):
    from backend.anthropic_provider import message_request
    evidence=[{'id':f'{i:029d}','text':'x'*(15500 if i==0 else 1),'title':'Saved source',
               'document_id':str(i),'url':'https://example.org/source'} for i in range(10)]
    request=ChatRequest(question='What does this saved source say?',answer_style='brief')
    prepared=prepare_answer(request,evidence,provider='anthropic');body=message_request(config,prepared)
    messages=[{'role':'system','content':body['system']},*body['messages']]
    actual=len(json.dumps(messages,ensure_ascii=False,separators=(',',':')).encode())
    assert actual<=24000 and prepared.input_token_bound==actual+2048
    ids=[e['id'] for e in prepared.evidence]
    wire=body['output_config']['format']['schema']
    assert wire['properties']['paragraph']['anyOf'][0]['properties']['supports']['items']['properties']['citation_id']['enum']==ids
    assert [e['id'] for e in json.loads(body['messages'][-1]['content'])['evidence']]==ids
    assert 'Each object has text, primary_support and supports only' in body['system']
    # A caller cannot spend the framing reserve as extra prompt space.
    oversized=[*prepared.messages[:-1],{'role':'user','content':'x'*24000}]
    with pytest.raises(ValueError,match='reserved allowance'):
        message_request(config,replace(prepared,messages=oversized,input_token_bound=26048))


def test_quote_contract_preserves_units_and_only_their_support_ids(config):
    from backend.anthropic_provider import normalize_native_answer
    evidence=[{'id':'water','text':'Annual recharge is 20 units.\nA local study.',
               'warning':'Machine OCR not manually verified.'},
              {'id':'forest','text':'The plateau supports reptiles.'}]
    prepared=prepare_answer(ChatRequest(question='What do these studies report?'),evidence,provider='anthropic')
    units=[{'text':'The study reports annual recharge of 20 units; the OCR is unverified.',
            'supports':[{'citation_id':'water','field':'text','quote':'Annual recharge is 20 units. A local study.'},
                        {'citation_id':'water','field':'warning','quote':'Machine OCR not manually verified.'}]},
           {'text':'The plateau supports reptiles.',
            'supports':[{'citation_id':'forest','field':'text','quote':'The plateau supports reptiles.'}]}]
    for unit in units:unit['primary_support']=unit['supports'].pop(0)
    result=json.loads(normalize_native_answer(json.dumps({'status':'answered','paragraphs':units}),prepared))
    assert result['paragraphs']==[{'text':units[0]['text'],'citations':['water']},
                                  {'text':units[1]['text'],'citations':['forest']}]
    assert not any('supports' in p for p in result['paragraphs'])


@pytest.mark.parametrize('mutation',[
    'unknown-id','cross-source','case-change','punctuation-change','ellipsis','empty','too-long',
    'unknown-field','hidden-origin','hidden-date','title','url','wrong-type','extra','metadata-only',
    'too-many-supports','too-many-units','no-units','mixed-invalid-unit','inline-id','rewritten-spacing',
])
def test_quote_contract_rejects_invented_or_unrepresented_support_without_salvage(prepared,mutation):
    from copy import deepcopy
    from backend.anthropic_provider import normalize_native_answer
    evidence=[dict(prepared.evidence[0],origin='pymupdf_reading_order',
                   source_date_metadata={'hidden_field':'Historical 2021 version'},
                   legal_currency='Current applicability unverified.'),
              {'id':'other','text':'Only a plateau study.'}]
    prepared=prepare_answer(ChatRequest(question='What do gates regulate?'),evidence,provider='anthropic')
    unit={'text':'Gates regulate tides.','supports':[
        {'citation_id':'passage-1','field':'text','quote':'regulate tidal water'}]}
    unit['primary_support']=unit['supports'].pop(0)
    payload={'status':'answered','paragraphs':[unit]};support=unit['primary_support']
    if mutation=='unknown-id':support['citation_id']='invented'
    elif mutation=='cross-source':support['citation_id']='other'
    elif mutation=='case-change':support['quote']='Regulate tidal water'
    elif mutation=='punctuation-change':support['quote']='regulate tidal water!'
    elif mutation=='ellipsis':support['quote']='Sluice gates ... in khazans.'
    elif mutation=='empty':support['quote']=' \n\t'
    elif mutation=='too-long':support['quote']='x'*601
    elif mutation=='unknown-field':support['field']='untrusted'
    elif mutation=='hidden-origin':support.update(field='origin',quote='pymupdf_reading_order')
    elif mutation=='hidden-date':support.update(field='source_date_metadata.hidden_field',quote='Historical 2021 version')
    elif mutation=='title':support.update(field='title',quote='Khazan study')
    elif mutation=='url':support.update(field='url',quote='example.org')
    elif mutation=='wrong-type':support['quote']=['regulate tidal water']
    elif mutation=='extra':support['private diagnostic']='fixture-only'
    elif mutation=='metadata-only':support.update(field='legal_currency',quote='Current applicability unverified.')
    elif mutation=='too-many-supports':unit['supports']=[deepcopy(support)]*10
    elif mutation=='too-many-units':payload['paragraphs']*=5
    elif mutation=='no-units':payload['paragraphs']=[]
    elif mutation=='inline-id':unit['text']='Gates regulate tides [passage-1].'
    elif mutation=='rewritten-spacing':unit['text']='  Gates regulate tides.'
    elif mutation=='mixed-invalid-unit':
        invalid=deepcopy(unit);invalid['primary_support']['quote']='Invented.';payload['paragraphs'].append(invalid)
    with pytest.raises(ValueError,match='native answer did not match the evidence contract') as error:
        normalize_native_answer(json.dumps(payload),prepared)
    assert 'private diagnostic' not in str(error.value)


def test_support_metadata_must_be_in_serialized_request(prepared):
    from backend.anthropic_provider import normalize_native_answer
    prepared.evidence[0]['warning']='OCR is unverified.'
    payload=native_payload(answer_payload());payload['paragraphs'][0]['supports'].append(
        {'citation_id':'passage-1','field':'warning','quote':'OCR is unverified.'})
    # Adding metadata after preparation must not make it evidence seen by the model.
    standard=replace(prepared,answer_style='standard')
    with pytest.raises(ValueError,match='evidence contract'):
        normalize_native_answer(json.dumps(payload),standard)


def test_explicit_source_provenance_quote_resolves_own_represented_source(prepared):
    from backend.anthropic_provider import normalize_native_answer
    evidence=[dict(prepared.evidence[0],source_date_metadata={'reviewed_locator_and_dates':'Saved version from 2021.'})]
    bounded=prepare_answer(ChatRequest(question='What does the saved source say?'),evidence,provider='anthropic')
    payload=native_payload(answer_payload());payload['paragraphs'][0]['supports'].append(
        {'citation_id':'passage-1','field':'source_date_metadata.reviewed_locator_and_dates','quote':'Saved version from 2021.'})
    assert json.loads(normalize_native_answer(json.dumps(payload),bounded))==answer_payload()


def test_native_contract_is_not_applied_to_other_providers(prepared):
    request=ChatRequest(question='How do khazans work?',answer_style='brief')
    regular=prepare_answer(request,prepared.evidence)
    for provider in ('openai','openrouter','qwen'):
        other=prepare_answer(request,prepared.evidence,provider=provider)
        assert other.messages==regular.messages and other.schema==regular.schema
        assert 'supports.citation_id' not in other.messages[0]['content']


def test_native_payload_withholds_catalogue_cues_without_changing_public_citations():
    from copy import deepcopy
    from backend.chat import evidence_payload
    item={'id':'p','text':'A lake contributes to recharge.','page_heading':'Wetlands',
          'warning':'Check the original.','title':'Hosted document', 'url':'https://example.org/report.pdf',
          'publisher_class':'act_for_goa','document_kind_hint':'article_report_or_index','topics':['water'],
          'document_id':'document','generation':'generation', 'retrieved_at':'2026-10-27',
          'legal_currency':'Unverified.', 'source_date_metadata':{'date_caution':'Date unknown.'},
          'guide_verification':{'limitations':'Saved source only.'}}
    original=deepcopy(item)
    prepared=prepare_answer(ChatRequest(question='What does the lake do?'),[item],provider='anthropic')
    payload=json.loads(prepared.messages[-1]['content']);source=next(iter(payload['sources'].values()))
    hidden={'title','url','publisher_class','document_kind_hint','topics'}
    assert not hidden & source.keys()
    assert source=={**{k:item[k] for k in ('document_id','generation','retrieved_at','legal_currency','source_date_metadata','guide_verification')},
                    'catalogue_scope_hint':item['title']}
    assert payload['evidence'][0]['text']==item['text'] and payload['evidence'][0]['page_heading']=='Wetlands'
    assert prepared.evidence==[original] and item==original
    for provider in (None,'openrouter','qwen','openai'):
        assert hidden <= next(iter(evidence_payload([item],provider=provider)['sources'].values())).keys()


@pytest.mark.parametrize('primary',[None,[],{}, {'citation_id':'passage-1','field':'warning','quote':'regulate tidal water'}])
def test_primary_text_object_cannot_be_missing_or_replaced_by_metadata(prepared,primary):
    from backend.anthropic_provider import normalize_native_answer
    payload=native_payload(answer_payload());unit=payload['paragraphs'][0]
    unit['supports']=[unit['primary_support']];unit['primary_support']=primary
    with pytest.raises(ValueError,match='evidence contract'):
        normalize_native_answer(json.dumps(payload),replace(prepared,answer_style='standard'))


@pytest.mark.parametrize('support',[
    {'citation_id':'passage-1','field':'text','quote':'Unseen source text.'},
    {'citation_id':'other','field':'text','quote':'regulate tidal water'},
    {'citation_id':'passage-1','field':'title','quote':'Khazan study'},
    {'citation_id':'passage-1','field':'catalogue_scope_hint','quote':'Khazan study'},
])
def test_valid_primary_cannot_mask_invalid_additional_support(prepared,support):
    from backend.anthropic_provider import normalize_native_answer
    payload=native_payload(answer_payload());payload['paragraphs'][0]['supports']=[support]
    with pytest.raises(ValueError,match='evidence contract'):
        normalize_native_answer(json.dumps(payload),replace(prepared,answer_style='standard'))



def test_standard_scope_policy_is_generic_and_keeps_provider_style_boundaries(config,prepared):
    from backend.anthropic_provider import message_request
    systems=[]
    for question in ('How does occurrence differ from endemism?', 'How does rainfall reach the aquifer?'):
        request=ChatRequest(question=question)
        native=prepare_answer(request,prepared.evidence,provider='anthropic')
        body=message_request(config,native);systems.append(body['system'])
        assert 'without unrequested numerical examples' in body['system']
        assert 'Retain entity, habitat, taxonomic, geographic and time qualifiers' in body['system']
        assert 'at most four paragraphs and 350 words; omit unrelated background' not in body['system']
        assert json.loads(body['messages'][-1]['content'])['question']==question
        assert body['max_tokens']==9000 and body['thinking']=={'type':'adaptive'}
        assert 'without unrequested numerical examples' not in prepare_answer(request,prepared.evidence).messages[0]['content']
    assert systems[0]==systems[1]  # No question-specific branch or baked-in answer.
    assert 'without unrequested numerical examples' not in message_request(config,prepared)['system']
