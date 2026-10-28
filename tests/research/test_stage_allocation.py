"""Versioned shared deadlines using synthetic clocks and owned fake transports."""
import asyncio
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
import hashlib
import json
import time

import pytest
import httpx

from backend import answer_pipeline as pipeline, reconstruction
from backend.async_anthropic import AsyncAnthropicClient
from backend import span_draft
from backend.span_instructions import STYLE_RULES
from backend.chat import AnswerCache, ChatRequest, Message, prepare_answer
from tests.research.test_answer_pipeline import setup, model_response
from tests.research.test_reconstruction import claim
from tests.research.span_fixtures import select_response, previous_workflow_prompt, historical_span_schema


@pytest.fixture
def clock(monkeypatch):
    clock = SimpleNamespace(now=100.0)
    # Keep the event loop's real monotonic clock independent of the fixture.
    monkeypatch.setattr(pipeline, 'time', SimpleNamespace(monotonic=lambda: clock.now))
    return clock


def observe_timeout_delays(monkeypatch):
    original = asyncio.timeout
    delays = []
    def timeout(delay):
        delays.append(delay)
        return original(delay)
    monkeypatch.setattr(pipeline.asyncio, 'timeout', timeout)
    return delays


def test_actual_transport_read_timeout_matches_stage_with_other_limits_unchanged(setup):
    _, _, _, transport, _, _, run, _ = setup
    run()
    assert len(transport.requests) == 1
    for request in transport.requests:
        assert request.extensions['timeout'] == {'connect': 10, 'read': 65, 'write': 10, 'pool': 10}
    assert reconstruction.PIPELINE_SPEC['provider_stage_seconds'] == 65
    assert reconstruction.PIPELINE_SPEC['provider_deadline_seconds'] == 65


@pytest.mark.parametrize('style,expected_hashes', [
    ('standard', ['8e4c112832315f2ce847e85ec9a9d0df5ca56baf678fbad8aa2f740844c3d13d',
                  'e9dc4096cae996a46aea8278a6c639ee2a5e72769230d636b30c65bbd99c4966']),
    ('brief', ['7cf3aa8096fd9d49ea17d2e35ff87b48f9dbdb0adee6618ed1d129582b6c6927',
               '20ea11fcdb89ed7215e9d65be78ba3f8624366cf8111916e75b1f36513353131']),
])
def test_actual_source_history_and_historical_wire_lineage_remain_pinned(setup, monkeypatch, style, expected_hashes):
    # Independently captured from fb60d77110c2e3ca55695088935451fbf0663d57
    # with this source-neutral fixture and real HTTPX serialization/fake I/O.
    config, _, _, transport, limits, _, _, factory = setup
    request = ChatRequest(question='What do gates do?', answer_style=style,
                          history=[Message(role='user', content='Gates and rain in Goa.')])
    original = prepare_answer(request, [{'id': 'a', 'text':
        'Gates regulate tidal water. Design must follow Appendix C.'}], provider='anthropic')
    async def handler(actual, n):
        payload = json.loads(json.loads(actual.content)['messages'][-1]['content'])
        paragraph = {'claims': [claim()]}
        native = {'status': 'answered', **({'paragraph': paragraph} if style == 'brief'
                                          else {'paragraphs': [paragraph]})}
        return model_response(select_response(native, payload))
    transport.handler = handler
    result = asyncio.run(pipeline.run_answer_pipeline(request, original, config,
                         limits=limits, client_factory=factory))
    assert result.trace['status'] == 'completed' and len(transport.requests) == 1
    # V10 intentionally replaces both wire schemas and the first output.
    # Reconstruct only this authored historical fixture to audit old hashes;
    # this is not production repair or transfer of model-output acceptance.
    bodies = [json.loads(r.content) for r in transport.requests]
    assert [b['output_config']['effort'] for b in bodies] == ['high']
    selected = span_draft.prepare_span_draft(request, original)
    for body, phase in zip(bodies, ('reconstruction',)):
        payload=json.loads(body['messages'][-1]['content'])
        assert payload.pop('plan_protocol')=='bounded_source_plan_v1'
        base={k:payload[k] for k in ('question','sources','evidence','request_scope')}
        if phase=='reconstruction':
            assert payload['evidence_plan']==result.trace['local_adapter']['value']
            base['draft_answer']={'status':'answered','paragraphs':[{'text':'Gates regulate tidal water.','citations':['a']}]}
        base['anchor_protocol']=payload['anchor_protocol']
        body['messages'][-1]['content']=reconstruction.encoded(base).decode()
        body['system']=previous_workflow_prompt(phase,style)
        body['output_config']['format']['schema']=historical_span_schema(original.schema,style,selected.span_registry,phase=phase)
        # Undo the v12 final-high experiment for this historical wire audit.
        body['output_config']['effort'] = 'medium'
    if style == 'brief':
        assert [hashlib.sha256(httpx.Request('POST', str(r.url), json=b).content).hexdigest()
                for r, b in zip(transport.requests, bodies)] == expected_hashes[1:]
    else:
        # Reverse only the two reviewed shape changes, then require the exact
        # independently captured v4 bytes; all other sent content must agree.
        old_style = ('Return only status and paragraphs. For answered, provide one to four paragraph '
                     'objects with at most350 words total. For insufficient_evidence, paragraphs is an '
                     'empty array.')
        selected = span_draft.prepare_span_draft(request, original)
        for index, (actual, phase) in enumerate(zip(transport.requests, ('reconstruction',))):
            body = bodies[index]
            assert body['system'].endswith(STYLE_RULES['standard'])
            before = deepcopy(body)
            before['system'] = body['system'].removesuffix(STYLE_RULES['standard']) + old_style
            before['output_config']['format']['schema'] = historical_span_schema(
                original.schema, style, selected.span_registry, phase=phase, slots=False)
            assert len(body['system'].encode()) - len(before['system'].encode()) == 181
            assert len(reconstruction.encoded(body['output_config']['format']['schema'])) - len(
                reconstruction.encoded(before['output_config']['format']['schema'])) == 341
            prior_bytes = httpx.Request('POST', str(actual.url), json=before).content
            assert hashlib.sha256(prior_bytes).hexdigest() == expected_hashes[index + 1]


def test_single_request_can_finish_after_forty_five_within_original_deadline(setup, clock, monkeypatch):
    _, _, _, transport, _, _, run, _ = setup
    good = transport.handler
    delays = observe_timeout_delays(monkeypatch)
    async def handler(request, n):
        clock.now += 50
        return await good(request, n)
    transport.handler = handler
    result = run()
    assert result.trace['status'] == 'completed'
    assert [p['phase_seconds'] for p in result.trace['phases']] == [50]
    assert delays == [65]  # One request, no separate 45-second cutoff.
    assert result.trace['elapsed_seconds'] == 50


def test_retrieval_time_is_subtracted_before_single_request(setup, clock, monkeypatch):
    _, _, _, transport, _, _, run, _ = setup
    good = transport.handler
    delays = observe_timeout_delays(monkeypatch)
    async def handler(request, n):
        clock.now += 44
        return await good(request, n)
    transport.handler = handler
    result = run(request_started_at=clock.now - 20)
    assert result.trace['status'] == 'completed' and delays == [45]
    assert [p['phase_seconds'] for p in result.trace['phases']] == [44]
    assert result.trace['elapsed_seconds'] == 64


@pytest.mark.parametrize('phase', [1])
@pytest.mark.parametrize('boundary', ['before_hook', 'after_observer'])
def test_overall_expiry_blocks_known_unsent_dispatch_at_each_hook_boundary(setup, clock, phase, boundary):
    config, request, prepared, transport, limits, _, _, _ = setup
    class DelayedClient(AsyncAnthropicClient):
        async def send(self, body, **kwargs):
            if boundary == 'before_hook' and len(limits.receipts) == phase:
                clock.now += 66
            return await super().send(body, **kwargs)
    def observer(trace):
        selected = trace['phases'][phase - 1]
        if boundary == 'after_observer' and selected['state'] == 'dispatched':
            clock.now += 66
    def factory():
        return DelayedClient('fixture-only', transport=transport)
    with pytest.raises(pipeline.PipelineFailure, match='provider_deadline') as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, prepared, config, limits=limits,
                    client_factory=factory, observer=observer))
    trace = caught.value.trace
    selected = trace['phases'][phase - 1]
    assert clock.now == 166 > 165  # Original overall deadline expired.
    assert len(limits.receipts) == phase and len(transport.requests) == phase - 1
    assert selected['reservation_receipt']['reserved'] and selected['provider_attempts'] == 0
    assert selected['dispatch_status'] == 'blocked_before_transport' and transport.closed
    assert 'final_answer' not in trace


def test_expiry_after_final_observation_prevents_publication(setup, clock):
    config, request, prepared, transport, limits, _, _, factory = setup
    def observer(trace):
        if trace['phases'][0]['state'] == 'completed':
            clock.now = 165
    with pytest.raises(pipeline.PipelineFailure, match='provider_deadline') as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, prepared, config, limits=limits,
                    client_factory=factory, observer=observer))
    assert len(limits.receipts) == len(transport.requests) == 1 and transport.closed
    assert 'final_answer' not in caught.value.trace
    assert len(caught.value.trace['phases']) == 1


def test_remaining_overall_budget_actually_cancels_single_request(setup, monkeypatch):
    _, _, _, transport, limits, _, run, _ = setup
    good = transport.handler
    monkeypatch.setattr(pipeline, 'PROVIDER_STAGE_SECONDS', .45)
    monkeypatch.setattr(pipeline, 'PROVIDER_DEADLINE_SECONDS', .65)
    delays = observe_timeout_delays(monkeypatch)
    async def handler(request, n):
        await asyncio.sleep(10)
        return await good(request, n)
    transport.handler = handler
    started = time.monotonic()
    with pytest.raises(pipeline.PipelineFailure, match='provider_deadline') as caught:
        run(request_started_at=started - .30)
    assert len(delays) == 1 and 0 < delays[0] < .45
    assert time.monotonic() - started < .65
    assert len(transport.requests) == len(limits.receipts) == 1
    assert transport.cancelled and transport.closed and 'final_answer' not in caught.value.trace


@pytest.mark.parametrize('phase', [1])
def test_shared_expiry_rejects_late_return_even_if_transport_suppresses_cancellation(setup, monkeypatch, phase):
    _, _, _, transport, limits, _, run, _ = setup
    good = transport.handler
    monkeypatch.setattr(pipeline, 'PROVIDER_STAGE_SECONDS', .45)
    monkeypatch.setattr(pipeline, 'PROVIDER_DEADLINE_SECONDS', .10)
    async def handler(request, n):
        if n == phase:
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                pass
        return await good(request, n)
    transport.handler = handler
    with pytest.raises(pipeline.PipelineFailure, match='provider_deadline') as caught:
        run()
    assert len(transport.requests) == len(limits.receipts) == phase and transport.closed
    assert 'final_answer' not in caught.value.trace


def test_v5_cache_cannot_reuse_v4_medium_with_thirty_second_spec(setup, monkeypatch):
    config, _, original, *_ = setup
    cache = AnswerCache()
    with monkeypatch.context() as m:
        m.setattr(reconstruction, 'PIPELINE_VERSION', 'two_pass_v4')
        m.setattr(reconstruction, 'PIPELINE_SPEC', {**deepcopy(reconstruction.PIPELINE_SPEC),
                  'version': 'two_pass_v4', 'provider_stage_seconds': 30})
        previous = AnswerCache.key(replace(config, pipeline='two_pass_v4'), original)
    current = AnswerCache.key(config, original)
    cache.put(previous, {'fixture': 'old result'})
    assert current != previous and cache.get(current) is None
    with pytest.raises(ValueError):
        AnswerCache.key(replace(config, pipeline='two_pass_v4'), original)
