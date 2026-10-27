"""Capture v2 on source-neutral fixtures and disposable SQLite ledgers only."""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime,timezone
import json
from pathlib import Path

import httpx
import pytest

from backend.async_anthropic import AsyncAnthropicClient
from backend import answer_pipeline
from backend.reconstruction import PIPELINE_SPEC
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.test_anthropic_acceptance import setup as legacy_setup
from tests.research.test_answer_pipeline import Transport,model_response


@pytest.fixture
def setup(legacy_setup,monkeypatch):
    plan,config,library,tmp=legacy_setup
    plan.update(pipeline='two_pass_v1',pipeline_spec=deepcopy(PIPELINE_SPEC),effort='low',max_output_tokens=12000)
    plan['stages']['test'].update(max_cases=2,max_attempts=4)
    config=replace(config,effort='low',max_output_tokens=12000,pipeline='two_pass_v1')
    monkeypatch.setattr(answer_pipeline,'utc_day',lambda:plan['date_utc'])
    transports=[]
    async def handler(request,n):
        payload=json.loads(json.loads(request.content)['messages'][-1]['content']);evidence=payload['evidence'][0]
        unit={'primary_support':{'citation_id':evidence['id'],'field':'text','quote':evidence['text']},'supports':[],
              'text':'Gates regulate tidal water.'}
        return model_response({'status':'answered','paragraphs':[unit if n==1 else {'claims':[unit]}]})
    handlers=[handler]
    def factory():
        transport=Transport(handlers[0]);transports.append(transport)
        return AsyncAnthropicClient('fixture-only',transport=transport)
    return plan,config,library,tmp,factory,transports,handlers


def run(setup):
    plan,config,library,tmp,factory,*_=setup
    context=acceptance.preflight(plan,'test',config)
    cases=acceptance.load_cases(context['stage'])
    return acceptance.run_cases(library,factory,None,config,cases,context,tmp/'capture-v2.json')


def test_v2_complete_wire_phase_receipts_and_exact_draft_capture(setup):
    plan,config,_,tmp,_,transports,_=setup
    context=acceptance.preflight(plan,'test',config)
    assert context['provider_attempt_ceiling']==4 and context['worst_reservation_microusd']==40096
    report=run(setup)
    assert report==json.loads((tmp/'capture-v2.json').read_text())
    assert report['capture_version']==2 and report['pipeline_spec']==PIPELINE_SPEC
    assert report['complete'] and report['attempts']==4 and report['entailment_acceptance']=='pending_human_review'
    assert len(transports)==2 and all(t.closed for t in transports)
    for entry,transport in zip(report['cases'],transports):
        assert entry['reserved_count']==2 and entry['accounting_matches'] and entry['usage_within_reservation']
        assert entry['mechanical_passed'] and entry['human_review']['status']=='pending'
        trace=entry['pipeline_trace']
        assert trace['status']=='completed' and len(trace['phases'])==2 and trace['final_answer']==entry['answer']
        for phase,request in zip(trace['phases'],transport.requests):
            assert phase['outgoing_request']['body_utf8'].encode()==request.content
            receipt=phase['reservation_receipt'];assert receipt['reserved'] and receipt['parent_id']==entry['parent_id']
            assert receipt['after']['day_attempts']==receipt['before']['day_attempts']+1
        draft=json.loads(json.loads(transport.requests[1].content)['messages'][-1]['content'])['draft_answer']
        assert draft==trace['phases'][1]['compact_draft']
    assert 'fixture-only' not in json.dumps(report) and 'private diagnostic' not in json.dumps(report)
    assert (tmp/'capture-v2.json').stat().st_mode & 0o777==0o600
    with pytest.raises(FileExistsError):
        acceptance.run_cases(setup[2],setup[4],None,config,acceptance.load_cases(context['stage']),context,tmp/'capture-v2.json')


@pytest.mark.parametrize('change',[
    lambda p:p.pop('pipeline'),lambda p:p['pipeline_spec'].update(correction_prompt_bytes=32000),
    lambda p:p['stages']['test'].pop('max_cases'),lambda p:p['stages']['test'].update(max_attempts=2),
])
def test_version_and_attempt_plan_mismatch_before_any_packet_or_key_read(setup,monkeypatch,change):
    plan,config,*_=setup;change(plan)
    monkeypatch.setattr(acceptance,'verify_packets',lambda _:pytest.fail('Must fail before artifact reads'))
    with pytest.raises(ValueError):acceptance.preflight(plan,'test',config)


def test_midnight_guard_preserves_unrun_case_and_spend(setup,monkeypatch):
    class Midnight(datetime):
        @classmethod
        def now(cls,tz):return cls(2026,10,27,23,59,0,tzinfo=timezone.utc)
    monkeypatch.setattr(acceptance,'datetime',Midnight)
    report=run(setup)
    assert report['cases']==[] and report['attempts']==0 and not report['complete']
    assert report['before']==report['after'] and not setup[5]


@pytest.mark.parametrize('phase',[1,2])
def test_v2_failure_keeps_receipts_and_available_diagnostics_without_final(setup,phase):
    handlers=setup[6];good=handlers[0]
    async def broken(request,n):
        if n==phase:return model_response({'status':'answered','paragraphs':[]},stop='max_tokens')
        return await good(request,n)
    handlers[0]=broken
    report=run(setup);entry=report['cases'][0]
    assert not report['complete'] and len(report['cases'])==1 and report['attempts']==phase
    assert entry['accounting_matches'] and entry['reserved_count']==phase and not entry['mechanical_passed']
    assert 'answer' not in entry and 'final_answer' not in entry['pipeline_trace']
    assert entry['pipeline_trace']['phases'][phase-1]['stop_reason']=='max_tokens'
    assert entry['human_review']['status']=='pending'


def test_missing_required_evidence_never_reserves_or_dispatches(setup):
    plan,config,library,tmp,factory,transports,_=setup
    context=acceptance.preflight(plan,'test',config);cases=acceptance.load_cases(context['stage'])
    cases[0]['required_evidence']=[{'any_of':['absent']}]
    report=acceptance.run_cases(library,factory,None,config,cases,context,tmp/'capture-v2.json')
    assert report['attempts']==0 and report['before']==report['after'] and not transports
    assert report['cases'][0]['failure_code']=='missing_required_evidence'


def test_no_evidence_is_zero_call_and_still_requires_correct_expected_behavior(setup):
    setup[2].search=lambda *_:[]
    report=run(setup);entry=report['cases'][0]
    assert entry['answer']['status']=='insufficient_evidence' and entry['no_evidence_before_dispatch']
    assert entry['accounting_matches'] and entry['mechanical_passed'] and not entry['expected_behavior_passed']
    assert not report['complete'] and report['attempts']==0 and report['before']==report['after']


def test_tampered_receipt_fails_exact_accounting(setup):
    report=run(setup);entry=report['cases'][0];trace=deepcopy(entry['pipeline_trace'])
    trace['phases'][1]['reservation_receipt']['after']['day_attempts']+=1
    assert not acceptance.phase_accounting(entry['ledger_before'],entry['ledger_after'],trace,setup[0]['date_utc'])


def test_persistence_failure_after_draft_prevents_second_dispatch(setup,monkeypatch):
    original=acceptance.save
    def failing_save(report,path):
        if report['cases'] and any(p.get('state')=='completed' for p in report['cases'][-1].get('pipeline_trace',{}).get('phases',[])):
            raise OSError('synthetic private failure')
        original(report,path)
    monkeypatch.setattr(acceptance,'save',failing_save)
    with pytest.raises(OSError):run(setup)
    assert len(setup[5])==1 and len(setup[5][0].requests)==1 and setup[5][0].closed
    saved=(setup[3]/'capture-v2.json').read_text()
    assert 'synthetic private failure' not in saved
