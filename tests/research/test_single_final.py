"""Single-final contract negatives; fictional sources and disposable budgets only."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import threading

import httpx
import pytest

from backend import answer_pipeline as pipeline, reconstruction
from backend.chat import AnswerCache, ChatRequest, Message, prepare_answer
from backend.hosting import PublicLimits
from backend.phase_effort import (local_plan_adapter, phase_policy_metadata,
    validate_local_plan_adapter, validate_policy_metadata)
from backend.source_spans import (encoded, original_baseline, verify_single_final_wire_binding,
    verify_wire_binding)
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.test_answer_pipeline import setup, model_response
from tests.research.test_reconstruction import claim
from tests.research.span_fixtures import select_response
from tests.research.test_stage_allocation import clock
from tests.research.test_stage_reservations import clock as ledger_clock, ledger, DAY
from tests.research.test_two_pass_acceptance import setup as acceptance_setup
from tests.research.test_anthropic_acceptance import setup as legacy_setup


@pytest.mark.parametrize('mutation', ['instructions', 'missing_base', 'history_content',
    'history_role', 'history_order', 'question', 'style', 'document', 'generation'])
def test_original_identity_fails_before_payload_observation_or_reservation(setup, mutation):
    config, _, _, transport, limits, _, _, _ = setup
    request = ChatRequest(question='What do gates do?', history=[
        Message(role='user', content='जल gates?'), Message(role='assistant', content='Goa’s gates.')])
    original = prepare_answer(request, [{'id':'a','text':'Gates regulate tidal water.'}], provider='anthropic')
    if mutation == 'instructions':original.messages[0]['content'] += ' changed'
    if mutation == 'missing_base':original.base_instructions = ''
    if mutation == 'history_content':original.messages[1]['content'] += ' changed'
    if mutation == 'history_role':original.messages[1]['role'] = 'assistant'
    if mutation == 'history_order':original.messages[1:-1] = original.messages[1:-1][::-1]
    if mutation == 'question':request = request.model_copy(update={'question':'A different question?'})
    if mutation == 'style':request = request.model_copy(update={'answer_style':'brief'})
    if mutation in ('document','generation'):
        original.request_scope['document_id' if mutation == 'document' else 'generation'] = 'changed'
    observed=[]
    def no_client():pytest.fail('Identity failure must precede credential/client access')
    with pytest.raises(pipeline.PipelineFailure):
        asyncio.run(pipeline.run_answer_pipeline(request,original,config,limits=limits,
            client_factory=no_client,observer=observed.append))
    assert not limits.receipts and not transport.requests
    assert all('prepared_original' not in value and 'final_answer' not in value for value in observed)


@pytest.mark.parametrize('style',['standard','brief'])
@pytest.mark.parametrize('history',['empty','ascii','unicode'])
@pytest.mark.parametrize('scoped',[False,True])
def test_actual_single_wire_preserves_full_selected_input(setup,style,history,scoped):
    config,_,_,transport,limits,_,_,factory=setup
    request=ChatRequest(question='What do gates do?',answer_style=style,
        history=[] if history=='empty' else [Message(role='user',content='Goa gates?' if history=='ascii' else 'Goa’s जल gates?')],
        document_id=('a'*24+'-'+'b'*12) if scoped else None,generation='generation-fixture' if scoped else None)
    original=prepare_answer(request,[{'id':'a','text':'Gates regulate tidal water.'}],provider='anthropic')
    before=deepcopy(original)
    async def handler(actual,n):
        wrapper=json.loads(json.loads(actual.content)['messages'][-1]['content'])
        paragraph={'claims':[claim()]}
        value={'status':'answered',**({'paragraph':paragraph} if style=='brief' else {'paragraphs':[paragraph]})}
        return model_response(select_response(value,wrapper))
    transport.handler=handler
    result=asyncio.run(pipeline.run_answer_pipeline(request,original,config,limits=limits,client_factory=factory))
    assert original==before and len(transport.requests)==len(limits.receipts)==1
    actual=transport.requests[0];body=json.loads(actual.content)
    pinned=json.loads(Path(__file__).with_name('single-final-v12-wire-parity.json').read_text())
    historical=next(item for item in pinned['cases'] if item['id']==f'{style}-{history}-{scoped}')
    assert body['output_config']['effort']=='medium'
    high=deepcopy(body);high['output_config']['effort']='high'
    historical_wire=httpx.Request('POST',str(actual.url),json=high).content
    assert hashlib.sha256(historical_wire).hexdigest()==historical['body_sha256']
    assert len(historical_wire)==historical['body_bytes']
    assert body != high  # Sole reviewed wire delta; high baseline fixture is immutable.
    assert hashlib.sha256(body['system'].encode()).hexdigest()==historical['system_sha256']
    assert hashlib.sha256(encoded(body['output_config']['format']['schema'])).hexdigest()==historical['schema_sha256']
    assert hashlib.sha256(original.messages[-1]['content'].encode()).hexdigest()==historical['selected_payload_sha256']
    prepared=reconstruction.prepare_reconstruction(request,original,local_plan_adapter())
    expected=reconstruction.reconstruction_message_request(config,prepared)
    assert actual.content==httpx.Request('POST',str(actual.url),json=expected).content
    baseline=original_baseline(original.messages[-1]['content'],original.messages[1:-1],original.request_scope)
    proof=verify_single_final_wire_binding(actual.content.decode(),baseline,prepared.span_registry_sha256)
    assert proof['wire_count']==1 and proof['generated_plan'] is False and proof['plan_origin']=='local_empty'
    assert proof['actual_request_body_sha256']==hashlib.sha256(actual.content).hexdigest()
    assert body['messages'][:-1]==original.messages[1:-1]
    assert result.trace['prepared_original']==baseline
    assert result.trace['local_adapter']==reconstruction.pipeline_spec()['local_adapter']
    assert AnswerCache.key(config,original)
    # The historical genuine-two-wire proof is deliberately still strict.
    with pytest.raises(ValueError):
        verify_wire_binding(actual.content.decode(),baseline,prepared.span_registry_sha256,phase='reconstruction')


@pytest.mark.parametrize('value', [None, [], {'status':'planned','points':[],'units':[]},
    {'status':'insufficient_evidence','points':[{}],'units':[]},
    {'status':'insufficient_evidence','points':[],'units':[{}]},
    {'status':'insufficient_evidence','points':[]},
    {'status':'insufficient_evidence','points':[],'units':[],'extra':False},
    {'units':[],'points':[],'status':'insufficient_evidence'},
    {'status':'insufficient_evidence','points':(),'units':[]}])
def test_adapter_accepts_only_canonical_exact_shape_and_types(value):
    with pytest.raises(ValueError):validate_local_plan_adapter(value)


@pytest.mark.parametrize('refs', [[0],[True],[False],[0.0],['0'],[-1],[1]])
def test_nonempty_model_plan_refs_are_rejected_without_rewriting(setup,refs):
    _,_,_,transport,limits,_,run,_=setup;good=transport.handler
    async def handler(actual,n):
        response=await good(actual,n);payload=response.json()
        value=json.loads(payload['content'][-1]['text']);value['paragraph_1']['claims'][0]['plan_refs']=refs
        return model_response(value)
    transport.handler=handler
    with pytest.raises(pipeline.PipelineFailure) as caught:run()
    phase=caught.value.trace['phases'][0]
    if type(refs[0]) is int and refs[0]>=0:
        assert phase['final_output_diagnostic']['answer']['paragraph_1']['claims'][0]['plan_refs']==refs
    else:
        assert 'final_output_diagnostic' not in phase  # Strict envelope rejected before capture.
    assert 'final_answer' not in caught.value.trace and len(limits.receipts)==len(transport.requests)==1


@pytest.mark.parametrize('location',['top','spec'])
@pytest.mark.parametrize('count',[True,False,1.0,0,2,'1',None])
def test_count_is_strict_before_packet_or_key_or_ledger_access(acceptance_setup,monkeypatch,location,count):
    plan,config,*_=acceptance_setup
    (plan if location=='top' else plan['pipeline_spec'])['provider_call_count']=count
    def no_access(*_):pytest.fail('Invalid count must fail before sensitive access')
    for name in ('verify_packets','inspect_ledger','dotenv_values'):monkeypatch.setattr(acceptance,name,no_access)
    with pytest.raises(ValueError):acceptance.preflight(plan,'test',config)


@pytest.mark.parametrize('change',[lambda p:p['local_adapter']['provenance'].update(generated_plan=0),
    lambda p:p['local_adapter']['provenance'].update(generated_plan=True),
    lambda p:p['local_adapter']['provenance'].update(plan_origin='model'),
    lambda p:p['local_adapter'].update(sha256='0'*64),
    lambda p:p.update(plan_input_mode='generated_plan')])
def test_adapter_metadata_is_strict_and_detached(change):
    value=phase_policy_metadata();before=deepcopy(value);change(value)
    with pytest.raises(ValueError):validate_policy_metadata(value)
    assert phase_policy_metadata()==before


@pytest.mark.parametrize('cost',[-1,True,False,0.5,'10',None,1<<63,[1]])
def test_single_preflight_invalid_cost_never_creates_ledger(tmp_path,ledger_clock,cost):
    root=tmp_path/'absent'
    with pytest.raises(ValueError):PublicLimits(root).preflight_single(cost,DAY)
    assert not root.exists()


def test_single_preflight_is_read_only_and_pair_stays_exactly_two(tmp_path,ledger_clock):
    limits=PublicLimits(tmp_path/'absent',chats_per_day=1,monthly_usd='0.010624')
    result=limits.preflight_single(10624,DAY)
    assert result['required_attempts']==1 and result['required_cost_microusd']==10624 and result['allowed']
    assert result['version']=='afg-single-preflight-v1' and not limits.root.exists()
    assert limits.preflight_pair([0,0],DAY)['reason']=='daily_limit'
    for costs in ([1], [1,2,3]):
        with pytest.raises(ValueError):limits.preflight_pair(costs,DAY)
    assert limits.reserve_stage(10624,DAY,'1'*32,'reconstruction')['reserved']
    path=limits.root/'answer-usage.sqlite';before=path.read_bytes()
    assert limits.preflight_single(0,DAY)['reason']=='daily_limit'
    assert limits.preflight_single(0,'2026-10-26')['reason']=='day_mismatch'
    assert path.read_bytes()==before and ledger(limits.root)['days']=={DAY:1}


@pytest.mark.parametrize('cap',['daily','monthly'])
def test_single_preflight_race_is_rechecked_atomically(tmp_path,ledger_clock,cap):
    barrier=threading.Barrier(2)
    def reserve(i):
        limits=PublicLimits(tmp_path,chats_per_day=1 if cap=='daily' else 100,
            monthly_usd='0.000001' if cap=='monthly' else '5')
        advisory=limits.preflight_single(1,DAY);barrier.wait(timeout=2)
        return advisory,limits.reserve_stage(1,DAY,f'{i:032x}','reconstruction')
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(reserve,[1,2]))
    assert all(a['allowed'] for a,_ in results) and sum(r['reserved'] for _,r in results)==1
    assert next(r for _,r in results if not r['reserved'])['reason']==cap+'_limit'
    assert ledger(tmp_path)['days']=={DAY:1} and ledger(tmp_path)['months']=={'2026-10':1}


@pytest.mark.parametrize('boundary',['response_observer','normalization','final_observer'])
def test_late_final_work_never_returns_answer(setup,clock,monkeypatch,boundary):
    config,request,original,transport,limits,_,_,factory=setup
    normalize=pipeline.normalize_reconstruction
    def late(*args,**kwargs):
        result=normalize(*args,**kwargs);clock.now=165;return result
    if boundary=='normalization':monkeypatch.setattr(pipeline,'normalize_reconstruction',late)
    def observer(value):
        if ((boundary=='final_observer' and value['status']=='completed') or
            (boundary=='response_observer' and value['phases'][0].get('provider_http_status')==200)):
            clock.now=165
    with pytest.raises(pipeline.PipelineFailure,match='provider_deadline') as caught:
        asyncio.run(pipeline.run_answer_pipeline(request,original,config,limits=limits,
            client_factory=factory,observer=observer))
    assert 'final_answer' not in caught.value.trace and len(transport.requests)==len(limits.receipts)==1
    assert transport.closed


def test_original_payload_reordering_is_refused_before_reservation(setup):
    config,request,original,transport,limits,_,_,factory=setup
    value=json.loads(original.messages[-1]['content'])
    original.messages[-1]['content']=encoded(dict(reversed(list(value.items())))).decode()
    with pytest.raises(pipeline.PipelineFailure):
        asyncio.run(pipeline.run_answer_pipeline(request,original,config,limits=limits,client_factory=factory))
    assert not limits.receipts and not transport.requests and transport.closed
