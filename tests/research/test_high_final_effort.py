"""Scoped final-high capture with fictional sources and mock I/O only."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import httpx
import pytest

from backend import answer_pipeline, reconstruction
from backend.answer_trace import outgoing_request_capture
from backend.anthropic_provider import message_request, reviewed_effort
from backend.chat import AnswerCache
from backend.evidence_plan_instructions import INSTRUCTIONS
from backend.phase_effort import PIPELINE_VERSION, EFFORT_POLICY
from backend.span_draft import prepare_span_draft, span_draft_message_request
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.span_fixtures import empty_plan
from tests.research.test_answer_pipeline import setup
from tests.research.test_anthropic_acceptance import setup as legacy_setup
from tests.research.test_two_pass_acceptance import setup as acceptance_setup


def context(phase):
    return dict(pipeline_version=PIPELINE_VERSION, effort_policy=EFFORT_POLICY,
                base_config_effort='medium', phase=phase)


def body_for(setup, phase):
    config, request, original, *_ = setup
    if phase == 'draft':
        return span_draft_message_request(config, prepare_span_draft(request, original))
    prepared = reconstruction.prepare_reconstruction(request, original, empty_plan())
    return reconstruction.reconstruction_message_request(config, prepared)


def capture(body, **kwargs):
    request = httpx.Request('POST', 'https://api.anthropic.com/v1/messages',
                           headers={'x-api-key': 'fixture-only'}, json=body)
    return outgoing_request_capture(request, **kwargs)


@pytest.mark.parametrize('phase,effort', [('draft', 'low'), ('reconstruction', 'high')])
def test_exact_trusted_phase_context_captures_unmodified_body(setup, phase, effort):
    body = body_for(setup, phase)
    record, decoded = capture(body, phase_context=context(phase))
    assert record['capture_status'] == 'captured_request'
    assert decoded == body and decoded['output_config']['effort'] == effort
    raw = record['body_utf8'].encode()
    assert record['body_sha256'] == hashlib.sha256(raw).hexdigest()
    assert record['body_bytes'] == len(raw)


@pytest.mark.parametrize('bad', [
    {}, [], 'reconstruction',
    {'phase': 'reconstruction'},
    {**context('reconstruction'), 'extra': True},
    {**context('reconstruction'), 'pipeline_version': 'two_pass_v11'},
    {**context('reconstruction'), 'effort_policy': 'low_draft_medium_reconstruction_v1'},
    {**context('reconstruction'), 'base_config_effort': 'high'},
    {**context('reconstruction'), 'base_config_effort': None},
    context('draft'), context('unknown'),
])
def test_high_capture_requires_complete_matching_trusted_context(setup, bad):
    assert capture(body_for(setup, 'reconstruction'), phase_context=bad) == (
        {'capture_status': 'unexpected_request_shape'}, None)


@pytest.mark.parametrize('field,value', [
    ('effort', 'medium'), ('effort', 'low'), ('effort', 'xhigh'), ('effort', 'max'),
    ('effort', None), ('model', 'claude-sonnet-5-5'), ('max_tokens', 11999),
    ('max_tokens', 12000.0),
])
def test_valid_context_cannot_authorize_wrong_final_body(setup, field, value):
    body = body_for(setup, 'reconstruction')
    (body['output_config'] if field == 'effort' else body)[field] = value
    assert capture(body, phase_context=context('reconstruction')) == (
        {'capture_status': 'unexpected_request_shape'}, None)


def test_high_cannot_escape_into_unscoped_capture_or_native_builder(setup):
    config, _, original, *_ = setup
    high = body_for(setup, 'reconstruction')
    for kwargs in ({}, {'phase_context': None}):
        assert capture(high, **kwargs) == ({'capture_status': 'unexpected_request_shape'}, None)
    with pytest.raises(ValueError): reviewed_effort(config.model, 'high')
    with pytest.raises(ValueError): message_request(replace(config, effort='high'), original)
    assert message_request(config, original)['output_config']['effort'] == 'medium'


@pytest.mark.parametrize('model,effort', [
    ('claude-haiku-5-5', 'low'), ('claude-haiku-5-5', 'medium'),
    ('claude-sonnet-5-5', 'medium'), ('claude-sonnet-5-5', 'high'),
])
def test_legacy_unscoped_capture_and_single_pass_review_remain_valid(setup, model, effort):
    body = body_for(setup, 'draft')
    body['model'] = model
    body['output_config']['effort'] = effort
    assert reviewed_effort(model, effort) == effort
    assert capture(body)[0]['capture_status'] == 'captured_request'


@pytest.mark.parametrize('secret', ['fixture-only', 'sk-ant-fictional-credential',
                                    '{"api_key":"fictional-credential"}'])
def test_valid_high_context_still_withholds_credential_echoes(setup, secret):
    body = body_for(setup, 'reconstruction')
    body['messages'][-1]['content'] += secret
    assert capture(body, phase_context=context('reconstruction')) == (
        {'capture_status': 'credential_like_content'}, None)


def test_actual_owned_hook_passes_fresh_complete_local_context(setup, monkeypatch):
    _, _, _, transport, limits, _, run, _ = setup
    seen = []
    def inspect(actual, *, phase_context=None):
        assert phase_context == context('draft' if not seen else 'reconstruction')
        seen.append(phase_context)
        return outgoing_request_capture(actual, phase_context=phase_context)
    monkeypatch.setattr(answer_pipeline, 'outgoing_request_capture', inspect)
    result = run()
    assert len(seen) == len(transport.requests) == len(limits.receipts) == 2
    assert seen[0] is not seen[1]
    assert result.trace['status'] == 'completed'


@pytest.mark.parametrize('phase', ['draft', 'reconstruction'])
def test_capture_rejection_retains_reservation_and_never_sends_target(setup, monkeypatch, phase):
    _, _, _, transport, limits, _, run, _ = setup
    def forged(actual, *, phase_context=None):
        if phase_context['phase'] == phase:
            phase_context = {**phase_context, 'pipeline_version': 'two_pass_v11'}
        return outgoing_request_capture(actual, phase_context=phase_context)
    monkeypatch.setattr(answer_pipeline, 'outgoing_request_capture', forged)
    with pytest.raises(answer_pipeline.PipelineFailure, match='request_capture_mismatch') as caught:
        run()
    count = 1 if phase == 'draft' else 2
    stopped = caught.value.trace['phases'][count - 1]
    assert len(limits.receipts) == count and len(transport.requests) == count - 1
    assert stopped['reservation_receipt']['reserved'] and stopped['provider_attempts'] == 0
    assert stopped['outgoing_request'] == {'capture_status': 'unexpected_request_shape'}
    assert 'final_answer' not in caught.value.trace and transport.closed


@pytest.mark.parametrize('change', [
    lambda p: p.update(pipeline='two_pass_v11'),
    lambda p: p['pipeline_spec'].update(version='two_pass_v11'),
    lambda p: p['pipeline_spec'].update(capture_version=10),
    lambda p: p.update(effort_policy='low_draft_medium_reconstruction_v1'),
    lambda p: p['pipeline_spec'].update(effort_policy='low_draft_medium_reconstruction_v1'),
    lambda p: p.update(base_config_effort='high'),
    lambda p: p['pipeline_spec'].update(base_config_effort='high'),
    lambda p: p.update(phase_efforts={'draft': 'low', 'reconstruction': 'medium'}),
    lambda p: p['pipeline_spec'].update(phase_efforts={'draft': 'low', 'reconstruction': 'medium'}),
])
def test_stale_v11_or_mixed_plan_rejected_before_sensitive_access(acceptance_setup, monkeypatch, change):
    plan, config, *_ = acceptance_setup
    change(plan)
    def no_access(*_): pytest.fail('Invalid identity must fail before packet/key/ledger access')
    for name in ('verify_packets', 'inspect_ledger', 'dotenv_values'):
        monkeypatch.setattr(acceptance, name, no_access)
    with pytest.raises(ValueError): acceptance.preflight(plan, 'test', config)


def test_v11_cache_does_not_supply_v12_answer_with_identical_prompts(setup, monkeypatch):
    config, _, original, *_ = setup
    current = AnswerCache.key(config, original)
    old = deepcopy(reconstruction.reconstruction_cache_identity(original, PIPELINE_VERSION))
    old['spec'].update(version='two_pass_v11', capture_version=10,
                       effort_policy='low_draft_medium_reconstruction_v1',
                       phase_efforts={'draft': 'low', 'reconstruction': 'medium'})
    with monkeypatch.context() as m:
        m.setattr(reconstruction, 'reconstruction_cache_identity', lambda *_: deepcopy(old))
        stale = AnswerCache.key(replace(config, pipeline='two_pass_v11'), original)
    cache = AnswerCache()
    cache.put(stale, {'fixture': 'prior unaccepted result'})
    assert current != stale and cache.get(current) is None
    with pytest.raises(ValueError): AnswerCache.key(replace(config, pipeline='two_pass_v11'), original)


@pytest.mark.parametrize('phase,prefix', [('draft', 'plan'), ('reconstruction', 'final')])
@pytest.mark.parametrize('style', ['standard', 'brief'])
def test_all_four_v11_prompts_remain_byte_identical(phase, prefix, style):
    pins = json.loads((Path(__file__).parents[2] / 'docs/research-high-final-effort.json').read_text())
    raw = INSTRUCTIONS[phase][style].encode()
    assert {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()} == pins['prompts'][prefix + '-' + style]
