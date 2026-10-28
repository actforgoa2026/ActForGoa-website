"""Phase policy through actual owned fake I/O and disposable acceptance state."""
import asyncio
from copy import deepcopy
from dataclasses import replace
import json
import sys

import pytest

from backend import answer_pipeline as pipeline, reconstruction
from backend.async_anthropic import AsyncAnthropicClient
from backend.chat import AnswerCache
from backend.phase_effort import (PIPELINE_VERSION, EFFORT_POLICY, PhasePolicyError,
    phase_effort, phase_policy_metadata)
from backend.paragraph_slots import PARAGRAPH_PROTOCOL
from backend.span_draft import prepare_span_draft, span_draft_message_request
from backend.reconstruction import prepare_reconstruction, reconstruction_message_request
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.test_answer_pipeline import setup
from tests.research.test_anthropic_acceptance import setup as legacy_setup
from tests.research.test_two_pass_acceptance import setup as acceptance_setup, run as run_acceptance


def test_exported_maps_cache_identity_and_observer_cannot_mutate_policy(setup, monkeypatch):
    config, request, original, transport, limits, _, _, factory = setup
    before = AnswerCache.key(config, original)
    exports = [phase_policy_metadata(), reconstruction.pipeline_spec(),
               reconstruction.reconstruction_cache_identity(original, PIPELINE_VERSION)['spec']]
    for value in exports:
        value['phase_efforts'].update(draft='high', reconstruction='low', extra='medium')
        value['effort_policy'] = 'untrusted'
    monkeypatch.setitem(reconstruction.PIPELINE_SPEC['phase_efforts'], 'draft', 'high')
    monkeypatch.setitem(reconstruction.PIPELINE_SPEC, 'effort_policy', 'untrusted')
    def observer(value):
        value['phase_efforts']['draft'] = 'high'
        value['pipeline_spec']['phase_efforts']['reconstruction'] = 'low'
        for phase in value['phases']:
            phase['effort_policy'] = 'untrusted'
            phase['expected_phase_effort'] = 'high'
            phase['phase'] = 'draft'
    result = asyncio.run(pipeline.run_answer_pipeline(request, original, config,
        limits=limits, client_factory=factory, observer=observer))
    assert before == AnswerCache.key(config, original)
    assert [json.loads(r.content)['output_config']['effort'] for r in transport.requests] == ['high']
    assert [p['expected_phase_effort'] for p in result.trace['phases']] == ['high']
    assert result.trace['pipeline_spec'] == reconstruction.pipeline_spec()
    assert phase_policy_metadata()['phase_efforts'] == {'reconstruction': 'high'}
    assert config.effort == 'medium'


@pytest.mark.parametrize('phase,wrong', [('reconstruction', 'low'), ('reconstruction', 'medium'), ('reconstruction', 'xhigh'), ('reconstruction', 'max')])
@pytest.mark.parametrize('in_place', [False, True])
def test_wrong_phase_effort_is_reserved_but_never_sent(setup, phase, wrong, in_place):
    config, request, original, transport, limits, _, _, _ = setup
    target = 1
    class MutatingClient(AsyncAnthropicClient):
        async def send(self, body, **kwargs):
            selected = body if in_place else deepcopy(body)
            if kwargs['phase'] == phase:
                selected['output_config']['effort'] = wrong
            return await super().send(selected, **kwargs)
    with pytest.raises(pipeline.PipelineFailure, match='local_validation_failure') as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, original, config, limits=limits,
            client_factory=lambda: MutatingClient('fixture-only', transport=transport)))
    trace = caught.value.trace
    stopped = trace['phases'][target - 1]
    assert len(limits.receipts) == target and len(transport.requests) == target - 1
    assert stopped['provider_attempts'] == 0 and stopped['reservation_receipt']['reserved']
    assert stopped['dispatch_status'] == 'blocked_before_transport' and transport.closed
    assert 'final_answer' not in trace and 'request_shape' not in stopped
    assert stopped['expected_phase_effort'] == phase_effort(phase)


@pytest.mark.parametrize('phase', ['reconstruction'])
@pytest.mark.parametrize('change', [
    {'pipeline_version': 'two_pass_v11'}, {'pipeline_version': 'two_pass_v10'}, {'pipeline_version': 'two_pass_v6'}, {'pipeline_version': None},
    {'effort_policy': 'low_draft_medium_reconstruction_v1'}, {'effort_policy': None}, {'effort_policy': 'uniform_medium'},
    {'base_config_effort': 'high'}, {'base_config_effort': None}, {'base_config_effort': 'low'},
])
def test_transport_rejects_missing_or_wrong_policy_context_before_callbacks(setup, phase, change):
    config, request, original, transport, _, _, _, factory = setup
    body = (span_draft_message_request(config, prepare_span_draft(request, original)) if phase == 'draft'
            else reconstruction_message_request(config, prepare_reconstruction(request, original,
                 {'status':'insufficient_evidence','points':[],'units':[]})))
    context = {'paragraph_protocol': PARAGRAPH_PROTOCOL, 'answer_style': 'standard', 'phase': phase,
               'pipeline_version': PIPELINE_VERSION, 'effort_policy': EFFORT_POLICY,
               'base_config_effort': 'medium', 'plan_protocol':'bounded_source_plan_v1',
               'final_internal_protocol':'planned_claim_supports_v1', **change}
    def no_callback(*_):pytest.fail('Invalid policy must not reach any request/response callback')
    async def scenario():
        async with factory() as client:
            with pytest.raises(PhasePolicyError, match='^Invalid answer phase policy$'):
                await client.send(body, on_request=no_callback, on_response=no_callback, **context)
    asyncio.run(scenario())
    assert not transport.requests and transport.closed


@pytest.mark.parametrize('phase', ['reconstruction'])
@pytest.mark.parametrize('field,value', [('model', 'claude-sonnet-5-5'), ('model', None),
    ('max_tokens', 9000), ('max_tokens', 12001), ('max_tokens', 12000.0), ('max_tokens', None)])
def test_direct_owned_transport_enforces_fixed_model_and_output_bound(setup, phase, field, value):
    config, request, original, transport, _, _, _, factory = setup
    body = (span_draft_message_request(config, prepare_span_draft(request, original)) if phase == 'draft'
            else reconstruction_message_request(config, prepare_reconstruction(request, original,
                 {'status':'insufficient_evidence','points':[],'units':[]})))
    if value is None:body.pop(field)
    else:body[field] = value
    def no_callback(*_):pytest.fail('Invalid fixed configuration must fail before callbacks or I/O')
    async def scenario():
        async with factory() as client:
            with pytest.raises(PhasePolicyError):
                await client.send(body, on_request=no_callback, on_response=no_callback,
                    paragraph_protocol=PARAGRAPH_PROTOCOL, answer_style='standard', phase=phase,
                    pipeline_version=PIPELINE_VERSION, effort_policy=EFFORT_POLICY, base_config_effort='medium',
                    plan_protocol='bounded_source_plan_v1',final_internal_protocol='planned_claim_supports_v1')
    asyncio.run(scenario())
    assert not transport.requests and transport.closed


@pytest.mark.parametrize('phase', ['reconstruction'])
@pytest.mark.parametrize('field,value', [('model', 'claude-sonnet-5-5'), ('max_tokens', 9000)])
def test_changed_fixed_configuration_retains_target_reservation_without_send(setup, phase, field, value):
    config, request, original, transport, limits, _, _, _ = setup
    class WrongConfiguration(AsyncAnthropicClient):
        async def send(self, body, **kwargs):
            if kwargs['phase'] == phase:body[field] = value
            return await super().send(body, **kwargs)
    with pytest.raises(pipeline.PipelineFailure) as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, original, config, limits=limits,
            client_factory=lambda: WrongConfiguration('fixture-only', transport=transport)))
    target = 1
    stopped = caught.value.trace['phases'][target - 1]
    assert len(limits.receipts) == target and len(transport.requests) == target - 1
    assert stopped['dispatch_status'] == 'blocked_before_transport' and stopped['provider_attempts'] == 0
    assert stopped['reservation_receipt']['reserved'] and 'final_answer' not in caught.value.trace


@pytest.mark.parametrize('phase', ['reconstruction'])
def test_relabelled_phase_with_matching_effort_still_fails_its_schema(setup, phase):
    config, request, original, transport, limits, _, _, _ = setup
    class Relabelled(AsyncAnthropicClient):
        async def send(self, body, **kwargs):
            if kwargs['phase'] == phase:
                kwargs['phase'] = 'reconstruction' if phase == 'draft' else 'draft'
                body['output_config']['effort'] = 'high'  # Forged draft still cannot use final schema/policy.
            return await super().send(body, **kwargs)
    with pytest.raises(pipeline.PipelineFailure) as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, original, config, limits=limits,
            client_factory=lambda: Relabelled('fixture-only', transport=transport)))
    target = 1
    assert len(limits.receipts) == target and len(transport.requests) == target - 1
    assert caught.value.trace['phases'][target - 1]['dispatch_status'] == 'blocked_before_transport'
    assert 'final_answer' not in caught.value.trace


@pytest.mark.parametrize('location', ['top', 'spec'])
@pytest.mark.parametrize('field,value', [
    ('base_config_effort', None), ('base_config_effort', 'low'),
    ('effort_policy', None), ('effort_policy', 'uniform_medium'),
    ('phase_efforts', None), ('phase_efforts', {}),
    ('phase_efforts', {'draft': 'low'}),
    ('phase_efforts', {'draft': 'low', 'reconstruction': 'medium'}),
    ('phase_efforts', {'draft': 'low', 'reconstruction': 'high', 'extra': 'low'}),
    ('phase_efforts', {'draft': 'medium', 'reconstruction': 'low'}),
    ('phase_efforts', {'draft': 'medium', 'reconstruction': 'medium'}),
    ('phase_efforts', {'draft': 'low', 'reconstruction': 'low'}),
    ('effort', 'medium'),
])
def test_new_plan_policy_is_exact_before_packet_or_ledger_access(acceptance_setup, monkeypatch, location, field, value):
    plan, config, *_ = acceptance_setup
    target = plan if location == 'top' else plan['pipeline_spec']
    if value is None:target.pop(field)
    else:target[field] = value
    def no_access(*_):pytest.fail('Policy must fail before packet/native/key/ledger work')
    monkeypatch.setattr(acceptance, 'verify_packets', no_access)
    monkeypatch.setattr(acceptance, 'inspect_ledger', no_access)
    monkeypatch.setattr(acceptance, 'dotenv_values', no_access)
    with pytest.raises(ValueError):acceptance.preflight(plan, 'test', config)


def assert_policy(value):
    assert 'effort' not in value
    assert all(value[k] == v for k, v in phase_policy_metadata().items())
    assert value['capture_version'] == 12 and value['pipeline_spec'] == reconstruction.pipeline_spec()


def test_actual_readiness_cli_and_complete_capture_describe_base_and_phases(acceptance_setup, monkeypatch, capsys):
    plan, config, _, tmp, _, transports, _ = acceptance_setup
    plan_file = tmp / 'plan.json';plan_file.write_text(json.dumps(plan))
    monkeypatch.setattr(sys, 'argv', ['acceptance', '--plan', str(plan_file), '--stage', 'test'])
    monkeypatch.setattr(acceptance, 'chat_config', lambda: config)
    acceptance.main()
    readiness = json.loads(capsys.readouterr().out)
    assert_policy(readiness)
    assert readiness['provider_calls'] == 0 and readiness['max_attempts'] == 2 and not transports
    report = run_acceptance(acceptance_setup)
    assert_policy(report)
    for case in report['cases']:
        assert_policy(case['pipeline_trace'])
        for phase in case['pipeline_trace']['phases']:
            expected = phase_effort(phase['phase'])
            assert phase['effort_policy'] == EFFORT_POLICY
            assert phase['expected_phase_effort'] == phase['request_shape']['effort'] == expected


def test_failure_before_dispatch_still_captures_expected_policy(acceptance_setup):
    plan, config, library, tmp, factory, transports, _ = acceptance_setup
    context = acceptance.preflight(plan, 'test', config)
    cases = acceptance.load_cases(context['stage'])
    cases[0]['required_evidence'] = [{'any_of': ['missing']}]
    report = acceptance.run_cases(library, factory, None, config, cases, context, tmp / 'missing.json')
    assert_policy(report)
    trace = report['cases'][0]['pipeline_trace'];assert_policy(trace)
    assert [p['expected_phase_effort'] for p in trace['phases']] == ['high']
    assert all('request_shape' not in p for p in trace['phases'])
    assert report['attempts'] == 0 and report['before'] == report['after'] and not transports


def test_single_pass_metadata_and_legacy_effort_default_are_unchanged(legacy_setup):
    plan, config, *_ = legacy_setup
    assert config.pipeline == 'single_pass'
    assert acceptance.configuration_capture(config) == {'effort': config.effort}
    plan.pop('effort', None)
    assert acceptance.planned_effort(plan) == 'medium'


def test_new_cache_cannot_reuse_v6_uniform_medium(setup, monkeypatch):
    config, _, original, *_ = setup
    current = AnswerCache.key(config, original)
    new_identity = reconstruction.reconstruction_cache_identity(original, PIPELINE_VERSION)
    old_identity = deepcopy(new_identity)
    old_identity['spec'].update(version='two_pass_v6', capture_version=5)
    for key in phase_policy_metadata():old_identity['spec'].pop(key)
    with monkeypatch.context() as m:
        m.setattr(reconstruction, 'reconstruction_cache_identity', lambda *_: deepcopy(old_identity))
        previous = AnswerCache.key(replace(config, pipeline='two_pass_v6'), original)
    cache = AnswerCache();cache.put(previous, {'fixture': 'old answer'})
    assert current != previous and cache.get(current) is None
    with pytest.raises(ValueError):AnswerCache.key(replace(config, pipeline='two_pass_v6'), original)
