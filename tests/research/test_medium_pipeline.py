"""Explicit current base-medium and fixed phase identity; no provider, keys, corpus or live ledgers."""
import asyncio
from copy import deepcopy
from dataclasses import replace

import pytest

from backend import answer_pipeline,providers,reconstruction
from backend.chat import AnswerCache
from backend.span_draft import prepare_span_draft,span_draft_message_request
from backend.reconstruction import prepare_reconstruction,reconstruction_message_request
from tests.research.test_answer_pipeline import setup


@pytest.mark.parametrize('pipeline,effort',[
    ('single_final_v2','low'),('single_final_v2','high'),('single_final_v1','medium'),('two_pass_v12','medium'),('two_pass_v12','low'),('two_pass_v12','high'),('two_pass_v12','xhigh'),('two_pass_v12','max'),('two_pass_v12','invalid'),('two_pass_v11','medium'),('two_pass_v11','low'),('two_pass_v11','high'),('two_pass_v10','medium'),('two_pass_v10','low'),('two_pass_v9','medium'),('two_pass_v9','low'),('two_pass_v8','medium'),('two_pass_v8','low'),('two_pass_v7','medium'),('two_pass_v7','low'),('two_pass_v6','medium'),('two_pass_v6','low'),('two_pass_v5','medium'),('two_pass_v5','low'),('two_pass_v4','medium'),('two_pass_v4','low'),('two_pass_v3','low'),('two_pass_v3','medium'),
    ('two_pass_v2','medium'),('two_pass_v1','medium')])
def test_environment_does_not_silently_upgrade_old_versions_or_low_effort(setup,monkeypatch,pipeline,effort):
    monkeypatch.setenv('ANTHROPIC_ANSWER_PIPELINE',pipeline)
    monkeypatch.setenv('ANTHROPIC_CHAT_EFFORT',effort)
    with pytest.raises(ValueError):providers.chat_config()


@pytest.mark.parametrize('change',[
    {'effort':'low'},{'effort':'high'},{'effort':'xhigh'},{'effort':'max'},{'effort':'invalid'},{'pipeline':'single_final_v1'},{'pipeline':'two_pass_v12'},{'pipeline':'two_pass_v11'},{'pipeline':'two_pass_v10'},{'pipeline':'two_pass_v5'},{'pipeline':'two_pass_v4'},{'pipeline':'two_pass_v3'},
    {'model':'claude-sonnet-5-5'},{'provider':'openrouter'},{'max_output_tokens':11999}])
def test_every_two_phase_entry_rejects_mismatched_configuration_before_keys_or_sends(setup,monkeypatch,change):
    config,request,original,transport,limits,_,_,_=setup
    bad=replace(config,**change)
    old_getenv=providers.os.getenv
    def no_keys(name,*args):
        if name in ('ANTHROPIC_API_KEY','ANTHROPIC_WORKSPACE_ID'):
            pytest.fail('Configuration must fail before key/workspace access')
        return old_getenv(name,*args)
    monkeypatch.setattr(providers.os,'getenv',no_keys)
    with pytest.raises(ValueError):bad.async_client()
    draft=prepare_span_draft(request,original)
    correction=prepare_reconstruction(request,original,{'status':'insufficient_evidence','points':[],'units':[]})
    with pytest.raises(ValueError):span_draft_message_request(bad,draft)
    with pytest.raises(ValueError):reconstruction_message_request(bad,correction)
    def no_client():pytest.fail('Invalid configuration must not open transport')
    with pytest.raises(answer_pipeline.PipelineFailure,match='pipeline_configuration'):
        asyncio.run(answer_pipeline.run_answer_pipeline(request,original,bad,limits=limits,client_factory=no_client))
    assert not limits.receipts and not transport.requests


def test_current_cache_cannot_reuse_prior_v3_low_identity(setup,monkeypatch):
    config,_,original,*_=setup
    cache=AnswerCache()
    # Source-neutral replay of the prior version's otherwise identical cache
    # identity, not transfer or acceptance of any historical model response.
    with monkeypatch.context() as m:
        m.setattr(reconstruction,'PIPELINE_VERSION','two_pass_v3')
        m.setattr(reconstruction,'PIPELINE_SPEC',{**deepcopy(reconstruction.PIPELINE_SPEC),'version':'two_pass_v3'})
        previous=AnswerCache.key(replace(config,pipeline='two_pass_v3',effort='low'),original)
    current=AnswerCache.key(config,original)
    cache.put(previous,{'fixture':'old result'})
    assert previous!=current and cache.get(current) is None
    with pytest.raises(ValueError):AnswerCache.key(replace(config,pipeline='two_pass_v3'),original)


def test_medium_configuration_and_caps_remain_fixed(setup):
    config,request,original,transport,limits,_,run,_=setup
    with pytest.raises(ValueError):span_draft_message_request(config,prepare_span_draft(request,original))
    correction=reconstruction_message_request(config,prepare_reconstruction(request,original,{'status':'insufficient_evidence','points':[],'units':[]}))
    assert correction['output_config']['effort']=='medium'
    assert correction['max_tokens']==12000
    assert answer_pipeline.maximum_answer_cost(config)==10624
    assert answer_pipeline.PROVIDER_STAGE_SECONDS==65 and answer_pipeline.PROVIDER_DEADLINE_SECONDS==65
    result=run()
    assert [phase['request_shape']['effort'] for phase in result.trace['phases']]==['medium']
    assert len(transport.requests)==len(limits.receipts)==1
