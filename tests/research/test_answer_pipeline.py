"""Two-stage mechanics with synthetic HTTP transports and in-memory budgets."""
import asyncio
from copy import deepcopy
from datetime import datetime,timezone
import json
import time

import httpx
import pytest

from backend.async_anthropic import AsyncAnthropicClient
from backend import answer_pipeline as pipeline
from backend.chat import ChatRequest, prepare_answer, AnswerCache
from backend.providers import chat_config
from tests.research.test_reconstruction import claim, response
from tests.research.test_anthropic_provider import anthropic_message


class Limits:
    def __init__(self, deny_phase=None, allow=True):
        self.receipts=[];self.deny_phase=deny_phase;self.allow=allow
    def preflight_pair(self,costs,day):
        assert costs==[9424,10624]
        return {'allowed':self.allow,'reason':'allowed' if self.allow else 'monthly_limit'}
    def reserve_stage(self,cost,day,parent,phase):
        result={'reserved':phase!=self.deny_phase,'reason':'reserved' if phase!=self.deny_phase else 'daily_limit',
                'parent_id':parent,'phase':phase,'cost_microusd':cost,'day':day,'receipt_id':'r'+str(len(self.receipts))}
        self.receipts.append(result)
        return result


class Transport(httpx.AsyncBaseTransport):
    def __init__(self,handler):self.handler=handler;self.requests=[];self.closed=False;self.cancelled=False
    async def handle_async_request(self,request):
        self.requests.append(request)
        try:return await self.handler(request,len(self.requests))
        except asyncio.CancelledError:
            self.cancelled=True;raise
    async def aclose(self):self.closed=True


def model_response(native, **kwargs):
    payload=anthropic_message(native,**kwargs)
    payload['usage'].update(cache_creation_input_tokens=0,cache_read_input_tokens=0)
    return httpx.Response(200,json=payload)


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','anthropic')
    monkeypatch.setenv('ANTHROPIC_CHAT_MODEL','claude-haiku-5-5')
    monkeypatch.setenv('ANTHROPIC_CHAT_EFFORT','low')
    monkeypatch.setenv('ANTHROPIC_ANSWER_PIPELINE','two_pass_v1')
    config=chat_config();request=ChatRequest(question='What do gates do?')
    prepared=prepare_answer(request,[{'id':'a','text':'Gates regulate tidal water. Design must follow Appendix C.'}],provider='anthropic')
    async def handler(_,n):
        return model_response({'status':'answered','paragraphs':[claim()]}) if n==1 else model_response(json.loads(response(claim())))
    transport=Transport(handler);limits=Limits();observed=[]
    def factory():return AsyncAnthropicClient('fixture-only',transport=transport)
    def run(**kwargs):
        return asyncio.run(pipeline.run_answer_pipeline(request,prepared,config,limits=limits,client_factory=factory,
                                                       observer=observed.append,**kwargs))
    return config,request,prepared,transport,limits,observed,run,factory


def test_two_exact_captured_calls_and_final_only_result(setup):
    _,_,prepared,transport,limits,observed,run,_=setup
    result=run();trace=result.trace
    assert trace['capture_version']==2 and trace['status']=='completed'
    assert len(transport.requests)==len(limits.receipts)==2 and transport.closed
    assert [p['state'] for p in trace['phases']]==['completed','completed']
    assert [p['provider_attempts'] for p in trace['phases']]==[1,1]
    assert all(p['usage_within_reservation'] for p in trace['phases'])
    for record,request in zip(trace['phases'],transport.requests):
        assert record['outgoing_request']['body_utf8'].encode()==request.content
    first=json.loads(transport.requests[0].content);second=json.loads(transport.requests[1].content)
    a=json.loads(first['messages'][-1]['content']);b=json.loads(second['messages'][-1]['content'])
    assert {k:b[k] for k in ('question','sources','evidence')}==a
    assert second['messages'][:-1]==first['messages'][:-1]
    assert trace['phases'][1]['source_equality']['complete_evidence_equal']
    assert trace['phases'][1]['compact_draft']==b['draft_answer']
    assert result.answer['paragraphs']==[{'text':'Gates regulate tidal water.','citations':['a']}]
    assert trace['assembly_offsets'][0]['start']==0
    saved=json.dumps(observed)
    assert 'fixture-only' not in saved and 'private diagnostic' not in saved and 'authorization' not in saved
    assert all('final_answer' not in item for item in observed if item['status']!='completed')
    assert trace['phases'][1]['final_output_diagnostic']['representation']=='reconstruction_paragraph_array'


@pytest.mark.parametrize('which',['draft','reconstruction'])
def test_reservation_refusal_stops_without_final_or_extra_dispatch(setup,which):
    _,_,_,transport,limits,_,run,_=setup;limits.deny_phase=which
    with pytest.raises(pipeline.PipelineFailure) as caught:run()
    assert caught.value.code=='reservation_refused'
    assert len(transport.requests)==(0 if which=='draft' else 1)
    assert 'final_answer' not in caught.value.trace and transport.closed


def test_pair_refusal_never_opens_transport_or_reserves(setup):
    _,_,_,transport,limits,_,run,_=setup;limits.allow=False
    with pytest.raises(pipeline.PipelineFailure,match='pair_allowance_refused'):run()
    assert not transport.requests and not limits.receipts


@pytest.mark.parametrize('phase',[1,2])
@pytest.mark.parametrize('failure',['http','stop','shape','usage'])
def test_each_stage_failure_preserves_reservations_and_no_draft_visibility(setup,phase,failure):
    _,_,_,transport,limits,_,run,_=setup;good=transport.handler
    async def handle(req,n):
        if n!=phase:return await good(req,n)
        if failure=='http':return httpx.Response(402,json={'error':'private upstream text'})
        if failure=='stop':return model_response({},stop='max_tokens')
        if failure=='shape':return model_response({'status':'answered','paragraphs':[{'text':'unanchored.'}]})
        result=await good(req,n);body=json.loads(result.content);body['usage']['output_tokens']=12001
        return httpx.Response(200,json=body)
    transport.handler=handle
    with pytest.raises(pipeline.PipelineFailure) as caught:run()
    assert len(transport.requests)==len(limits.receipts)==phase and transport.closed
    assert 'final_answer' not in caught.value.trace
    assert 'private upstream text' not in json.dumps(caught.value.trace)
    assert all(r['reserved'] for r in limits.receipts)


def test_insufficient_draft_still_gets_source_coverage_reconstruction(setup):
    _,_,_,transport,_,_,run,_=setup;good=transport.handler
    async def handle(req,n):
        if n==1:return model_response({'status':'insufficient_evidence','paragraphs':[]})
        return await good(req,n)
    transport.handler=handle
    result=run();assert len(transport.requests)==2 and result.answer['status']=='answered'


def test_compact_draft_overflow_stops_before_second_reservation(setup):
    _,_,_,transport,limits,_,run,_=setup
    async def handle(_,n):return model_response({'status':'answered','paragraphs':[claim('界'*2800+'.')]})
    transport.handler=handle
    with pytest.raises(pipeline.PipelineFailure) as caught:run()
    assert len(transport.requests)==len(limits.receipts)==1
    assert caught.value.trace['phases'][1]['state']=='failed' and 'final_answer' not in caught.value.trace


def test_stage_deadline_really_cancels_and_closes_io(setup,monkeypatch):
    _,_,_,transport,limits,_,run,_=setup
    monkeypatch.setattr(pipeline,'PROVIDER_STAGE_SECONDS',0.02)
    async def handle(*_):await asyncio.sleep(10)
    transport.handler=handle
    with pytest.raises(pipeline.PipelineFailure,match='provider_stage_timeout'):run()
    assert transport.cancelled and transport.closed and len(limits.receipts)==1 and len(transport.requests)==1


def test_transport_suppressed_timeout_cannot_publish_late_response(setup,monkeypatch):
    _,_,_,transport,limits,_,run,_=setup;good=transport.handler
    monkeypatch.setattr(pipeline,'PROVIDER_STAGE_SECONDS',.02)
    async def late(req,n):
        try:await asyncio.sleep(10)
        except asyncio.CancelledError:pass
        return await good(req,n)
    transport.handler=late
    with pytest.raises(pipeline.PipelineFailure,match='provider_stage_timeout') as caught:run()
    assert len(transport.requests)==len(limits.receipts)==1 and transport.closed
    assert 'final_answer' not in caught.value.trace


def test_already_expired_entry_time_never_reserves_or_dispatches(setup):
    _,_,_,transport,limits,_,run,_=setup
    with pytest.raises(pipeline.PipelineFailure,match='provider_deadline'):run(request_started_at=time.monotonic()-66)
    assert not limits.receipts and not transport.requests


def test_browser_disconnect_cancels_io_and_joins_before_return(setup):
    config,request,prepared,transport,limits,_,_,factory=setup
    async def scenario():
        entered=asyncio.Event();gone=False
        async def handle(*_):entered.set();await asyncio.sleep(10)
        async def disconnected():return gone
        transport.handler=handle
        task=asyncio.create_task(pipeline.run_answer_pipeline(request,prepared,config,limits=limits,
            client_factory=factory,disconnected=disconnected))
        await entered.wait();gone=True
        with pytest.raises(pipeline.PipelineFailure,match='client_disconnected'):await task
        assert transport.closed and transport.cancelled and len(transport.requests)==1
    asyncio.run(scenario())


def test_utc_change_after_reservation_cannot_dispatch(setup,monkeypatch):
    _,_,_,transport,limits,_,run,_=setup
    day=pipeline.utc_day();original=limits.reserve_stage
    def reserve(*args):
        receipt=original(*args);monkeypatch.setattr(pipeline,'utc_day',lambda:'2099-01-01');return receipt
    limits.reserve_stage=reserve
    with pytest.raises(pipeline.PipelineFailure,match='utc_day_changed'):run(expected_day=day)
    assert len(limits.receipts)==1 and not transport.requests


def test_cache_separates_pipeline_and_both_instruction_schema_identities(setup,monkeypatch):
    from dataclasses import replace
    import backend.reconstruction as reconstruction
    config,_,prepared,*_=setup
    key=AnswerCache.key(config,prepared)
    assert key!=AnswerCache.key(replace(config,pipeline='single_pass'),prepared)
    old=reconstruction.reconstruction_instructions
    monkeypatch.setattr(reconstruction,'reconstruction_instructions',lambda *a:old(*a)+' A new correction policy.')
    assert key!=AnswerCache.key(config,prepared)


def test_cancelled_native_worker_is_joined_not_abandoned():
    import threading
    entered=threading.Event();release=threading.Event();finished=threading.Event()
    def native():entered.set();release.wait();finished.set();return 1
    async def scenario():
        task=asyncio.create_task(pipeline.joined_native_call(native))
        while not entered.is_set():await asyncio.sleep(.001)
        task.cancel();await asyncio.sleep(.01)
        assert not task.done() and not finished.is_set()
        release.set()
        with pytest.raises(asyncio.CancelledError):await task
        assert finished.is_set()
    asyncio.run(scenario())


def test_cache_separates_request_document_scope_even_with_same_visible_evidence(setup):
    config,request,prepared,*_=setup
    scoped=prepare_answer(request.model_copy(update={'document_id':'doc-a','generation':'fixture'}),prepared.evidence,provider='anthropic')
    assert scoped.messages==prepared.messages
    assert AnswerCache.key(config,scoped)!=AnswerCache.key(config,prepared)


@pytest.mark.parametrize('phase',[1,2])
def test_disconnect_after_commit_before_send_keeps_receipt(setup,phase):
    config,request,prepared,transport,limits,_,_,factory=setup
    async def scenario():
        async def gone():return len(limits.receipts)>=phase
        with pytest.raises(pipeline.PipelineFailure) as caught:
            await pipeline.run_answer_pipeline(request,prepared,config,limits=limits,client_factory=factory,disconnected=gone)
        assert caught.value.code=='client_disconnected'
        assert len(limits.receipts)==phase and len(transport.requests)==phase-1 and transport.closed
        assert caught.value.trace['phases'][phase-1]['reservation_receipt']['reserved']
        assert 'final_answer' not in caught.value.trace
    asyncio.run(scenario())


def test_utc_crossing_during_dispatch_capture_stops_before_transport(setup,monkeypatch):
    config,request,prepared,transport,limits,_,_,factory=setup
    day=pipeline.utc_day()
    def observer(trace):
        if trace['phases'][0]['state']=='dispatched':monkeypatch.setattr(pipeline,'utc_day',lambda:'2099-01-01')
    with pytest.raises(pipeline.PipelineFailure) as caught:
        asyncio.run(pipeline.run_answer_pipeline(request,prepared,config,limits=limits,client_factory=factory,observer=observer,expected_day=day))
    assert caught.value.code=='utc_day_changed' and len(limits.receipts)==1 and not transport.requests
    phase=caught.value.trace['phases'][0]
    assert phase['provider_attempts']==0 and phase['dispatch_status']=='blocked_before_transport'


@pytest.mark.parametrize('phase',[1,2])
def test_failed_pretransport_capture_records_zero_calls_for_reserved_phase(setup,phase):
    config,request,prepared,transport,limits,_,_,factory=setup
    raised=False
    def observer(trace):
        nonlocal raised
        if trace['phases'][phase-1]['state']=='dispatched' and not raised:
            raised=True;raise OSError('private synthetic storage detail')
    with pytest.raises(pipeline.PipelineFailure) as caught:
        asyncio.run(pipeline.run_answer_pipeline(request,prepared,config,limits=limits,client_factory=factory,observer=observer))
    record=caught.value.trace['phases'][phase-1]
    assert record['provider_attempts']==0 and record['dispatch_status']=='blocked_before_transport'
    assert len(transport.requests)==phase-1 and len(limits.receipts)==phase and transport.closed
    assert record['reservation_receipt']['reserved'] and 'final_answer' not in caught.value.trace


def test_correction_late_response_after_disconnect_never_succeeds(setup):
    config,request,prepared,transport,limits,_,_,factory=setup;good=transport.handler
    async def scenario():
        entered=asyncio.Event();gone=False
        async def late(req,n):
            if n==2:
                entered.set()
                try:await asyncio.sleep(10)
                except asyncio.CancelledError:pass  # hostile transport suppresses cancellation
            return await good(req,n)
        transport.handler=late
        async def disconnected():return gone
        task=asyncio.create_task(pipeline.run_answer_pipeline(request,prepared,config,limits=limits,
            client_factory=factory,disconnected=disconnected))
        await entered.wait();gone=True
        with pytest.raises(pipeline.PipelineFailure) as caught:await task
        assert caught.value.code=='client_disconnected' and 'final_answer' not in caught.value.trace
        assert len(transport.requests)==2 and len(limits.receipts)==2 and transport.closed
    asyncio.run(scenario())


def test_transport_error_records_uncertain_receipt_without_redispatch(setup):
    _,_,_,transport,limits,_,run,_=setup
    async def broken(*_):raise httpx.ReadError('private transport detail')
    transport.handler=broken
    with pytest.raises(pipeline.PipelineFailure) as caught:run()
    assert len(limits.receipts)==len(transport.requests)==1 and transport.closed
    assert caught.value.trace['phases'][0]['dispatch_status']=='initiated_receipt_unconfirmed'
    assert 'private transport detail' not in json.dumps(caught.value.trace)


def test_failed_final_capture_never_leaves_final_in_failure_trace(setup):
    config,request,prepared,transport,limits,_,_,factory=setup
    observed=[]
    def observer(trace):
        if trace['status']=='completed':raise OSError('private storage detail')
        observed.append(trace)
    with pytest.raises(pipeline.PipelineFailure) as caught:
        asyncio.run(pipeline.run_answer_pipeline(request,prepared,config,limits=limits,client_factory=factory,observer=observer))
    assert caught.value.trace['status']=='failed' and 'final_answer' not in caught.value.trace
    assert 'final_answer' not in observed[-1] and len(transport.requests)==2 and transport.closed


@pytest.mark.parametrize('secret',['fixture-only','sk-ant-sensitive-fixture'])
@pytest.mark.parametrize('escaped',[False,True])
def test_credential_like_response_never_enters_diagnostic_or_public_answer(setup,secret,escaped):
    _,_,_,transport,_,observed,run,_=setup
    async def leaked(*_):
        output=json.dumps({'status':'answered','paragraphs':[claim(secret+'.')]})
        if escaped:output=output.replace(secret,''.join('\\u%04x'%ord(c) for c in secret))
        return model_response(output)
    transport.handler=leaked
    with pytest.raises(pipeline.PipelineFailure) as caught:run()
    assert secret not in json.dumps(caught.value.trace) and secret not in json.dumps(observed)
    assert len(transport.requests)==1 and transport.closed and 'final_answer' not in caught.value.trace
