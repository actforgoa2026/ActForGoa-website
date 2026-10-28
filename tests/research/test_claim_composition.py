"""Prompt/version identity and owned mock I/O; no model accuracy claim."""
import asyncio
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from backend import answer_pipeline, reconstruction
from backend.async_anthropic import AsyncAnthropicClient
from backend.chat import AnswerCache, ChatRequest, Message, prepare_answer
from backend.evidence_plan_instructions import INSTRUCTIONS
from backend.providers import chat_config
from backend.source_spans import encoded, verify_annotated_payload
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.span_fixtures import empty_plan, select_response
from tests.research.test_answer_pipeline import setup, Limits, Transport, model_response
from tests.research.test_anthropic_acceptance import setup as legacy_setup
from tests.research.test_two_pass_acceptance import setup as acceptance_setup

DOCS = Path(__file__).parents[2] / 'docs'


def pins():
    return json.loads((DOCS / 'research-claim-composition-parity.json').read_text())


@pytest.mark.parametrize('style', ['standard', 'brief'])
def test_only_approved_final_workflow_paragraph_changes_from_v10(style):
    current = pins()
    old = json.loads((DOCS / 'research-evidence-plan-parity.json').read_text())
    final = INSTRUCTIONS['reconstruction'][style]
    parts = final.split('\n')
    assert parts[1] == current['replacement']
    assert len(parts[1].encode()) == 865
    restored = parts[:]
    restored[1] = current['previous_paragraph']
    raw = '\n'.join(restored).encode()
    previous = old['prompts']['final-' + style]
    assert len(raw) == previous['bytes']
    assert hashlib.sha256(raw).hexdigest() == previous['sha256']
    assert len(final.encode()) - len(raw) == 316
    plan = INSTRUCTIONS['draft'][style].encode()
    assert hashlib.sha256(plan).hexdigest() == old['prompts']['plan-' + style]['sha256']


def test_v10_cache_identity_cannot_supply_v11_answer(setup, monkeypatch):
    config, _, original, *_ = setup
    current = AnswerCache.key(config, original)
    identity = reconstruction.reconstruction_cache_identity(original, 'two_pass_v11')
    previous = deepcopy(identity)
    previous['spec'].update(version='two_pass_v10', capture_version=9)
    paragraphs = previous['correction_instructions'].split('\n')
    paragraphs[1] = pins()['previous_paragraph']
    previous['correction_instructions'] = '\n'.join(paragraphs)
    with monkeypatch.context() as m:
        m.setattr(reconstruction, 'reconstruction_cache_identity', lambda *_: deepcopy(previous))
        stale = AnswerCache.key(replace(config, pipeline='two_pass_v10'), original)
    cache = AnswerCache()
    cache.put(stale, {'fixture': 'unaccepted old answer'})
    assert stale != current and cache.get(current) is None
    with pytest.raises(ValueError):
        AnswerCache.key(replace(config, pipeline='two_pass_v10'), original)


def test_detached_spec_mutation_cannot_restore_v10_identity(setup, monkeypatch):
    config, _, original, *_ = setup
    before = AnswerCache.key(config, original)
    exported = reconstruction.pipeline_spec()
    exported.update(version='two_pass_v10', capture_version=9)
    monkeypatch.setitem(reconstruction.PIPELINE_SPEC, 'version', 'two_pass_v10')
    monkeypatch.setitem(reconstruction.PIPELINE_SPEC, 'capture_version', 9)
    assert reconstruction.pipeline_spec()['version'] == 'two_pass_v11'
    assert reconstruction.pipeline_spec()['capture_version'] == 10
    assert before == AnswerCache.key(config, original)


@pytest.mark.parametrize('change', [
    lambda plan: plan.update(pipeline='two_pass_v10'),
    lambda plan: plan['pipeline_spec'].update(version='two_pass_v10'),
    lambda plan: plan['pipeline_spec'].update(capture_version=9),
])
def test_stale_v10_acceptance_plan_fails_before_sensitive_access(acceptance_setup, monkeypatch, change):
    plan, config, *_ = acceptance_setup
    change(plan)
    def no_access(*_):
        pytest.fail('Stale identity must fail before packets, native library, keys or ledger access')
    for name in ('verify_packets', 'inspect_ledger', 'dotenv_values'):
        monkeypatch.setattr(acceptance, name, no_access)
    with pytest.raises(ValueError):
        acceptance.preflight(plan, 'test', config)


def test_readiness_and_initial_capture_bind_v11_and_capture10(acceptance_setup):
    plan, config, *_ = acceptance_setup
    context = acceptance.preflight(plan, 'test', config)
    for value in (acceptance.readiness_report(config, context, 'test'),
                  answer_pipeline.initial_pipeline_trace('synthetic-parent', context['day'])):
        assert value['capture_version'] == 10
        assert value['pipeline_spec'] == reconstruction.pipeline_spec()
        assert value['pipeline_spec']['version'] == 'two_pass_v11'


def test_prepared_final_cannot_be_mutated_back_to_old_prompt(setup):
    config, request, original, transport, limits, *_ = setup
    prepared = reconstruction.prepare_reconstruction(request, original, empty_plan())
    paragraphs = prepared.messages[0]['content'].split('\n')
    paragraphs[1] = pins()['previous_paragraph']
    prepared.messages[0]['content'] = '\n'.join(paragraphs)
    with pytest.raises(ValueError, match='identity changed'):
        reconstruction.reconstruction_message_request(config, prepared)
    assert not limits.receipts and not transport.requests


@pytest.mark.parametrize('style', ['standard', 'brief'])
def test_actual_httpx_bytes_use_approved_prompts_and_unchanged_sources_history(style, monkeypatch):
    for key, value in {'RESEARCH_CHAT_PROVIDER': 'anthropic', 'ANTHROPIC_CHAT_MODEL': 'claude-haiku-5-5',
                       'ANTHROPIC_CHAT_EFFORT': 'medium', 'ANTHROPIC_ANSWER_PIPELINE': 'two_pass_v11'}.items():
        monkeypatch.setenv(key, value)
    source = {'id': 'fictional-register', 'text': 'Permit holders must retain the inspection certificate.',
              'title': 'Fictional register', 'source_date_metadata': [{'field': 'datePublished', 'value': '2024'}]}
    request = ChatRequest(question='What must the fictional permit holder retain?', answer_style=style,
                          history=[Message(role='user', content='Which rule covers the permit?'),
                                   Message(role='assistant', content='What requirement do you want to check?')])
    original = prepare_answer(request, [source], provider='anthropic')
    baseline = json.loads(original.messages[-1]['content'])
    async def handler(actual, n):
        payload = json.loads(json.loads(actual.content)['messages'][-1]['content'])
        unit = {'primary_support': {'citation_id': source['id'], 'field': 'text', 'quote': source['text']},
                'supports': [{'citation_id': source['id'], 'field': 'source_publication',
                              'quote': 'Source publication year: 2024 (source metadata).'}],
                'text': 'The fictional register, published in 2024, requires permit holders to retain the inspection certificate.'}
        if n == 2:
            unit['plan_refs'] = [0]
        paragraph = unit if n == 1 else {'claims': [unit]}
        native = {'status': 'answered', **({'paragraph': paragraph} if style == 'brief' else {'paragraphs': [paragraph]})}
        return model_response(select_response(native, payload))
    transport = Transport(handler)
    limits = Limits()
    result = asyncio.run(answer_pipeline.run_answer_pipeline(request, original, chat_config(), limits=limits,
                        client_factory=lambda: AsyncAnthropicClient('fixture-only', transport=transport)))
    assert len(transport.requests) == len(limits.receipts) == 2 and transport.closed
    for phase, actual, trace in zip(('draft', 'reconstruction'), transport.requests, result.trace['phases']):
        body = json.loads(actual.content)
        assert body['system'] == INSTRUCTIONS[phase][style]
        if phase == 'reconstruction':
            assert hashlib.sha256(body['system'].encode()).hexdigest() == pins()['prompts']['final-' + style]['sha256']
        assert body['messages'][:-1] == original.messages[1:-1]
        wrapper = json.loads(body['messages'][-1]['content'])
        restored, _ = verify_annotated_payload({key: wrapper[key] for key in ('question', 'sources', 'evidence')}, baseline)
        assert encoded(restored) == encoded(baseline)
        assert trace['source_equality']['actual_wire_verified'] and trace['source_equality']['byte_equality']
        assert body['max_tokens'] == 12000
        assert body['output_config']['effort'] == ('low' if phase == 'draft' else 'medium')
    assert result.trace['capture_version'] == 10
    assert result.trace['pipeline_spec']['version'] == 'two_pass_v11'
    assert 'plan_refs' not in json.dumps(result.answer) and 'points' not in result.answer
