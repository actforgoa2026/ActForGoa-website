"""Exact workflow identity and retained guards, never model accuracy tests."""
import asyncio
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from backend import answer_pipeline as pipeline, reconstruction
from backend.chat import AnswerCache, ChatRequest, prepare_answer
from backend.phase_effort import PIPELINE_VERSION
from backend.span_draft import prepare_span_draft, span_draft_message_request
from backend.span_instructions import ANSWER_WORKFLOW, span_answer_instructions
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.span_fixtures import previous_workflow_prompt, previous_source_completeness_prompt, select_response
from tests.research.test_answer_pipeline import setup, model_response
from tests.research.test_reconstruction import claim
from tests.research.test_anthropic_acceptance import setup as legacy_setup
from tests.research.test_two_pass_acceptance import setup as acceptance_setup


@pytest.mark.parametrize('phase', ['draft', 'reconstruction'])
@pytest.mark.parametrize('style', ['standard', 'brief'])
def test_reversing_only_reviewed_workflow_reproduces_prior_prompt_hash(phase, style):
    root = Path(__file__).parents[2] / 'docs'
    before = json.loads((root / 'research-slot-instruction-parity.json').read_text())
    after = json.loads((root / 'research-required-coverage-parity.json').read_text())
    old_pin, new_pin = (record['rendered_instructions'][phase][style] for record in (before, after))
    old = previous_workflow_prompt(phase, style).encode()
    new = previous_source_completeness_prompt(phase, style).encode()
    assert (len(old), hashlib.sha256(old).hexdigest()) == (old_pin['utf8_bytes'], old_pin['sha256'])
    assert (len(new), hashlib.sha256(new).hexdigest()) == (new_pin['utf8_bytes'], new_pin['sha256'])
    assert len(new) - len(old) == new_pin['delta_bytes']


@pytest.mark.parametrize('change', [
    lambda p: p.update(pipeline='two_pass_v7'),
    lambda p: p['pipeline_spec'].update(version='two_pass_v7'),
    lambda p: p['pipeline_spec'].update(capture_version=6),
    lambda p: p['pipeline_spec'].pop('answer_workflow'),
    lambda p: p['pipeline_spec'].update(answer_workflow='draft_expansion'),
    lambda p: p['pipeline_spec'].update(answer_workflow=None),
])
def test_stale_or_missing_workflow_plan_stops_before_packet_and_key_access(acceptance_setup, monkeypatch, change):
    plan, config, *_ = acceptance_setup;change(plan)
    def no_access(*_):pytest.fail('Workflow identity must fail before packet/key/ledger reads')
    for name in ('verify_packets', 'dotenv_values', 'inspect_ledger'):
        monkeypatch.setattr(acceptance, name, no_access)
    with pytest.raises(ValueError):acceptance.preflight(plan, 'test', config)


def test_detached_workflow_spec_cannot_downgrade_later_requests_or_cache(setup, monkeypatch):
    config, request, original, *_ = setup
    before_key = AnswerCache.key(config, original)
    before_body = span_draft_message_request(config, prepare_span_draft(request, original))
    exported = reconstruction.reconstruction_cache_identity(original, PIPELINE_VERSION)
    exported['spec']['answer_workflow'] = 'draft_expansion'
    monkeypatch.setitem(reconstruction.PIPELINE_SPEC, 'answer_workflow', 'draft_expansion')
    assert AnswerCache.key(config, original) == before_key
    assert span_draft_message_request(config, prepare_span_draft(request, original)) == before_body
    assert reconstruction.pipeline_spec()['answer_workflow'] == ANSWER_WORKFLOW


def test_prior_v7_mixed_effort_cache_cannot_supply_new_workflow(setup, monkeypatch):
    config, _, original, *_ = setup
    current = AnswerCache.key(config, original)
    historical = reconstruction.reconstruction_cache_identity(original, PIPELINE_VERSION)
    historical['spec'].update(version='two_pass_v7', capture_version=6)
    historical['spec'].pop('answer_workflow')
    historical['draft_instructions'] = previous_workflow_prompt('draft', original.answer_style)
    historical['correction_instructions'] = previous_workflow_prompt('reconstruction', original.answer_style)
    with monkeypatch.context() as m:
        m.setattr(reconstruction, 'reconstruction_cache_identity', lambda *_: deepcopy(historical))
        previous = AnswerCache.key(replace(config, pipeline='two_pass_v7'), original)
    cache = AnswerCache();cache.put(previous, {'fixture': 'unaccepted prior answer'})
    assert current != previous and cache.get(current) is None
    with pytest.raises(ValueError):AnswerCache.key(replace(config, pipeline='two_pass_v7'), original)


@pytest.mark.parametrize('style', ['standard', 'brief'])
def test_valid_label_with_omitted_year_still_blocks_final_after_both_calls(setup, style):
    config, _, _, transport, limits, _, _, factory = setup
    request = ChatRequest(question='What does the source say?', answer_style=style)
    source = {'id': 'a', 'text': 'Gates regulate tidal water.',
              'source_date_metadata': [{'field': 'datePublished', 'value': '2022-01-04'}]}
    original = prepare_answer(request, [source], provider='anthropic')
    publication = {'citation_id': 'a', 'field': 'source_publication',
                   'quote': 'Source publication year: 2022 (source metadata).'}
    async def handler(actual, n):
        body = json.loads(actual.content);payload = json.loads(body['messages'][-1]['content'])
        text = ('The source published in 2022 states that gates regulate tidal water.' if n == 1
                else 'Gates regulate tidal water.')
        unit = claim(text, extras=[publication])
        para = unit if n == 1 else {'claims': [unit]}
        native = {'status': 'answered', **({'paragraph': para} if style == 'brief' else {'paragraphs': [para]})}
        return model_response(select_response(native, payload))
    transport.handler = handler
    with pytest.raises(pipeline.PipelineFailure, match='local_validation_failure') as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, original, config, limits=limits, client_factory=factory))
    trace = caught.value.trace
    assert len(transport.requests) == len(limits.receipts) == 2 and transport.closed
    assert trace['phases'][0]['state'] == 'completed' and trace['phases'][1]['state'] == 'failed'
    assert 'final_answer' not in trace
    assert trace['pipeline_spec']['answer_workflow'] == ANSWER_WORKFLOW
    assert trace['phases'][1]['final_output_diagnostic']['capture_status'] == 'captured_unvalidated_json'
    assert all(p['reservation_receipt']['reserved'] for p in trace['phases'])


def test_new_workflow_is_unambiguous_in_readiness_and_initial_failure_capture(acceptance_setup):
    plan, config, *_ = acceptance_setup
    context = acceptance.preflight(plan, 'test', config)
    for value in (acceptance.readiness_report(config, context, 'test'),
                  pipeline.initial_pipeline_trace('synthetic-parent', context['day'])):
        assert value['capture_version'] == 11
        assert value['pipeline_spec']['version'] == 'two_pass_v12'
        assert value['pipeline_spec']['answer_workflow'] == 'evidence_plan_first_v1'
        assert value['phase_efforts'] == {'draft': 'low', 'reconstruction': 'high'}
