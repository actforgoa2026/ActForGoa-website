"""New fixed-medium identity; no provider, corpus, keys or live ledgers."""
import asyncio
from copy import deepcopy
from dataclasses import replace

import pytest

from backend import reconstruction
from backend.chat import AnswerCache
from backend.evidence_plan import PLAN_PROTOCOL, FINAL_INTERNAL_PROTOCOL
from backend.paragraph_slots import PARAGRAPH_PROTOCOL
from backend.phase_effort import (PIPELINE_VERSION, EFFORT_POLICY, PhasePolicyError,
    local_plan_adapter, phase_policy_metadata)
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.test_answer_pipeline import setup
from tests.research.test_anthropic_acceptance import setup as legacy_setup
from tests.research.test_two_pass_acceptance import setup as acceptance_setup


@pytest.mark.parametrize('change', [
    lambda p:p.update(pipeline='single_final_v1'),
    lambda p:p['pipeline_spec'].update(version='single_final_v1'),
    lambda p:p['pipeline_spec'].update(capture_version=12),
    lambda p:p.update(effort_policy='single_final_high_v1'),
    lambda p:p['pipeline_spec'].update(effort_policy='single_final_high_v1'),
    lambda p:p.update(phase_efforts={'reconstruction':'high'}),
    lambda p:p['pipeline_spec'].update(phase_efforts={'reconstruction':'high'}),
    lambda p:p.update(phase_efforts={'reconstruction':'low'}),
    lambda p:p['pipeline_spec'].update(phase_efforts={'reconstruction':'medium','draft':'low'}),
    lambda p:p.update(base_config_effort='high'),
    lambda p:p['pipeline_spec'].update(base_config_effort='high'),
])
def test_v1_high_and_mixed_metadata_fail_before_sensitive_access(acceptance_setup,monkeypatch,change):
    plan,config,*_=acceptance_setup;change(plan)
    def no_access(*_):pytest.fail('Stale identity must fail before packet, native, key or ledger access')
    for name in ('verify_packets','inspect_ledger','dotenv_values'):monkeypatch.setattr(acceptance,name,no_access)
    with pytest.raises(ValueError):acceptance.preflight(plan,'test',config)


@pytest.mark.parametrize('change',[
    {'pipeline_version':'single_final_v1'},
    {'effort_policy':'single_final_high_v1'},
    {'pipeline_version':'single_final_v1','effort_policy':'single_final_high_v1'},
    {'base_config_effort':'high'},
])
@pytest.mark.parametrize('actual_effort',['medium','high'])
def test_owned_transport_rejects_stale_context_even_with_matching_old_body(setup,change,actual_effort):
    config,request,original,transport,_,_,_,factory=setup
    prepared=reconstruction.prepare_reconstruction(request,original,local_plan_adapter())
    body=reconstruction.reconstruction_message_request(config,prepared)
    body['output_config']['effort']=actual_effort
    context={'pipeline_version':PIPELINE_VERSION,'effort_policy':EFFORT_POLICY,'base_config_effort':'medium',
        'phase':'reconstruction','paragraph_protocol':PARAGRAPH_PROTOCOL,'answer_style':'standard',
        'plan_protocol':PLAN_PROTOCOL,'final_internal_protocol':FINAL_INTERNAL_PROTOCOL,**change}
    def no_callback(*_):pytest.fail('Stale policy must fail before capture or I/O')
    async def scenario():
        async with factory() as client:
            with pytest.raises(PhasePolicyError):
                await client.send(body,on_request=no_callback,on_response=no_callback,**context)
    asyncio.run(scenario())
    assert not transport.requests and transport.closed


def test_historical_high_cache_cannot_supply_medium_answer(setup,monkeypatch):
    config,_,original,*_=setup
    current=AnswerCache.key(config,original)
    historical=deepcopy(reconstruction.reconstruction_cache_identity(original,PIPELINE_VERSION))
    historical['spec'].update(version='single_final_v1',capture_version=12,
        effort_policy='single_final_high_v1',phase_efforts={'reconstruction':'high'})
    with monkeypatch.context() as patched:
        patched.setattr(reconstruction,'reconstruction_cache_identity',lambda *_:deepcopy(historical))
        old=AnswerCache.key(replace(config,pipeline='single_final_v1'),original)
    cache=AnswerCache();cache.put(old,{'fixture':'unaccepted historical high result'})
    assert current!=old and cache.get(current) is None
    with pytest.raises(ValueError):AnswerCache.key(replace(config,pipeline='single_final_v1'),original)


def test_current_readiness_names_one_fixed_medium_call(acceptance_setup):
    plan,config,*_=acceptance_setup
    ready=acceptance.preflight(plan,'test',config)
    assert PIPELINE_VERSION=='single_final_v2' and EFFORT_POLICY=='single_final_medium_v1'
    assert reconstruction.pipeline_spec()['capture_version']==13
    assert phase_policy_metadata()['phase_efforts']=={'reconstruction':'medium'}
    assert ready['provider_attempt_ceiling']==2 and ready['worst_reservation_microusd']==21248
    assert reconstruction.pipeline_spec()['provider_call_count']==1
    assert reconstruction.pipeline_spec()['answer_workflow']=='single_final_full_evidence_v1'
