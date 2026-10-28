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
from tests.research.span_fixtures import select_response, previous_workflow_prompt


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
    assert len(transport.requests) == 2
    for request in transport.requests:
        assert request.extensions['timeout'] == {'connect': 10, 'read': 45, 'write': 10, 'pool': 10}
    assert reconstruction.PIPELINE_SPEC['provider_stage_seconds'] == 45
    assert reconstruction.PIPELINE_SPEC['provider_deadline_seconds'] == 65


@pytest.mark.parametrize('style,expected_hashes', [
    ('standard', ['8e4c112832315f2ce847e85ec9a9d0df5ca56baf678fbad8aa2f740844c3d13d',
                  'e9dc4096cae996a46aea8278a6c639ee2a5e72769230d636b30c65bbd99c4966']),
    ('brief', ['7cf3aa8096fd9d49ea17d2e35ff87b48f9dbdb0adee6618ed1d129582b6c6927',
               '20ea11fcdb89ed7215e9d65be78ba3f8624366cf8111916e75b1f36513353131']),
])
def test_actual_requests_preserve_brief_bytes_and_only_approved_standard_shape_delta(setup, monkeypatch, style, expected_hashes):
    # Independently captured from fb60d77110c2e3ca55695088935451fbf0663d57
    # with this source-neutral fixture and real HTTPX serialization/fake I/O.
    config, _, _, transport, limits, _, _, factory = setup
    request = ChatRequest(question='What do gates do?', answer_style=style,
                          history=[Message(role='user', content='Gates and rain in Goa.')])
    original = prepare_answer(request, [{'id': 'a', 'text':
        'Gates regulate tidal water. Design must follow Appendix C.'}], provider='anthropic')
    async def handler(actual, n):
        payload = json.loads(json.loads(actual.content)['messages'][-1]['content'])
        paragraph = claim() if n == 1 else {'claims': [claim()]}
        native = {'status': 'answered', **({'paragraph': paragraph} if style == 'brief'
                                          else {'paragraphs': [paragraph]})}
        return model_response(select_response(native, payload))
    transport.handler = handler
    result = asyncio.run(pipeline.run_answer_pipeline(request, original, config,
                         limits=limits, client_factory=factory))
    assert result.trace['status'] == 'completed' and len(transport.requests) == 2
    # Undo only v7's reviewed draft-effort field before the historical shape
    # comparison below. Reconstruction remains exact for this same draft.
    bodies = [json.loads(r.content) for r in transport.requests]
    assert [b['output_config']['effort'] for b in bodies] == ['low', 'medium']
    # v8 changes only the two reviewed workflow sections and their priority.
    for body, phase in zip(bodies, ('draft', 'reconstruction')):
        body['system'] = previous_workflow_prompt(phase, style)
    bodies[0]['output_config']['effort'] = 'medium'
    if style == 'brief':
        assert [hashlib.sha256(httpx.Request('POST', str(r.url), json=b).content).hexdigest()
                for r, b in zip(transport.requests, bodies)] == expected_hashes
    else:
        # Reverse only the two reviewed shape changes, then require the exact
        # independently captured v4 bytes; all other sent content must agree.
        old_style = ('Return only status and paragraphs. For answered, provide one to four paragraph '
                     'objects with at most350 words total. For insufficient_evidence, paragraphs is an '
                     'empty array.')
        selected = span_draft.prepare_span_draft(request, original)
        for index, (actual, phase) in enumerate(zip(transport.requests, ('draft', 'reconstruction'))):
            body = bodies[index]
            assert body['system'].endswith(STYLE_RULES['standard'])
            before = deepcopy(body)
            before['system'] = body['system'].removesuffix(STYLE_RULES['standard']) + old_style
            with monkeypatch.context() as m:
                m.setattr(span_draft, 'standard_slot_schema', lambda schema, style: schema)
                before['output_config']['format']['schema'] = span_draft.span_schema(
                    original.schema, style, selected.span_registry, phase=phase)
            assert len(body['system'].encode()) - len(before['system'].encode()) == 181
            assert len(reconstruction.encoded(body['output_config']['format']['schema'])) - len(
                reconstruction.encoded(before['output_config']['format']['schema'])) == 341
            prior_bytes = httpx.Request('POST', str(actual.url), json=before).content
            assert hashlib.sha256(prior_bytes).hexdigest() == expected_hashes[index]


def test_stage_can_finish_after_thirty_only_within_shared_remaining_budget(setup, clock, monkeypatch):
    _, _, _, transport, _, _, run, _ = setup
    good = transport.handler
    delays = observe_timeout_delays(monkeypatch)
    async def handler(request, n):
        clock.now += 35 if n == 1 else 10
        return await good(request, n)
    transport.handler = handler
    result = run()
    assert result.trace['status'] == 'completed'
    assert [p['phase_seconds'] for p in result.trace['phases']] == [35, 10]
    assert delays == [45, 30]  # Not a fresh 45 for the correction.
    assert result.trace['elapsed_seconds'] == 45


def test_correction_can_use_more_than_thirty_if_draft_left_enough_time(setup, clock, monkeypatch):
    _, _, _, transport, _, _, run, _ = setup
    good = transport.handler
    delays = observe_timeout_delays(monkeypatch)
    async def handler(request, n):
        clock.now += 5 if n == 1 else 35
        return await good(request, n)
    transport.handler = handler
    result = run()
    assert result.trace['status'] == 'completed' and delays == [45, 45]
    assert [p['phase_seconds'] for p in result.trace['phases']] == [5, 35]


@pytest.mark.parametrize('phase', [1, 2])
@pytest.mark.parametrize('boundary', ['before_hook', 'after_observer'])
def test_phase_only_expiry_blocks_known_unsent_dispatch_at_each_hook_boundary(setup, clock, phase, boundary):
    config, request, prepared, transport, limits, _, _, _ = setup
    class DelayedClient(AsyncAnthropicClient):
        async def send(self, body, **kwargs):
            if boundary == 'before_hook' and len(limits.receipts) == phase:
                clock.now += 46
            return await super().send(body, **kwargs)
    def observer(trace):
        selected = trace['phases'][phase - 1]
        if boundary == 'after_observer' and selected['state'] == 'dispatched':
            clock.now += 46
    def factory():
        return DelayedClient('fixture-only', transport=transport)
    with pytest.raises(pipeline.PipelineFailure, match='provider_stage_timeout') as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, prepared, config, limits=limits,
                    client_factory=factory, observer=observer))
    trace = caught.value.trace
    selected = trace['phases'][phase - 1]
    assert clock.now == 146 < 165  # Phase expired while the shared allowance remains.
    assert len(limits.receipts) == phase and len(transport.requests) == phase - 1
    assert selected['reservation_receipt']['reserved'] and selected['provider_attempts'] == 0
    assert selected['dispatch_status'] == 'blocked_before_transport' and transport.closed
    assert 'final_answer' not in trace
    if phase == 1:
        assert 'reservation_receipt' not in trace['phases'][1]


def test_shared_expiry_after_first_stage_prevents_second_reservation_and_send(setup, clock):
    config, request, prepared, transport, limits, _, _, factory = setup
    def observer(trace):
        if trace['phases'][0]['state'] == 'completed':
            clock.now = 165
    with pytest.raises(pipeline.PipelineFailure, match='provider_deadline') as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, prepared, config, limits=limits,
                    client_factory=factory, observer=observer))
    assert len(limits.receipts) == len(transport.requests) == 1 and transport.closed
    assert 'final_answer' not in caught.value.trace
    assert 'reservation_receipt' not in caught.value.trace['phases'][1]


def test_remaining_shared_budget_actually_cancels_correction_io(setup, monkeypatch):
    _, _, _, transport, limits, _, run, _ = setup
    good = transport.handler
    monkeypatch.setattr(pipeline, 'PROVIDER_STAGE_SECONDS', .45)
    monkeypatch.setattr(pipeline, 'PROVIDER_DEADLINE_SECONDS', .65)
    delays = observe_timeout_delays(monkeypatch)
    async def handler(request, n):
        await asyncio.sleep(.12 if n == 1 else 10)
        return await good(request, n)
    transport.handler = handler
    started = time.monotonic()
    with pytest.raises(pipeline.PipelineFailure, match='provider_deadline') as caught:
        run(request_started_at=started - .30)
    assert len(delays) == 2 and 0 < delays[1] < delays[0] < .45
    assert time.monotonic() - started < .65
    assert len(transport.requests) == len(limits.receipts) == 2
    assert transport.cancelled and transport.closed and 'final_answer' not in caught.value.trace


@pytest.mark.parametrize('phase', [1, 2])
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
