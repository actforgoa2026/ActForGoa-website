"""Owned fake I/O exercises strict decoding before capture and both normalizers."""
import asyncio
from copy import deepcopy
import json

import pytest

from backend import answer_pipeline as pipeline, answer_trace
from backend.answer_trace import final_json_capture
from backend.async_anthropic import AsyncAnthropicClient
from backend.phase_effort import PIPELINE_VERSION, EFFORT_POLICY
from backend.chat import ChatRequest, prepare_answer
from backend.paragraph_slots import (PARAGRAPH_PROTOCOL, SLOT_NAMES, AnswerEnvelopeError,
    strict_answer_json, decode_envelope, encoded, value_hash)
from backend.source_spans import ANCHOR_PROTOCOL
from backend.span_draft import prepare_span_draft, normalize_span_draft
from backend.span_draft import span_draft_message_request
from backend.reconstruction import prepare_reconstruction, normalize_reconstruction, reconstruction_message_request
from tests.research.test_answer_pipeline import setup, model_response
from tests.research.test_anthropic_provider import anthropic_message
from tests.research.test_reconstruction import claim
from tests.research.span_fixtures import select_response, slot_response


def output_payload(raw):
    return anthropic_message(content=[{'type': 'text', 'text': raw}])


def capture(raw, style, phase):
    return final_json_capture(output_payload(raw), answer_style=style, phase=phase,
                              anchor_protocol=ANCHOR_PROTOCOL, paragraph_protocol=PARAGRAPH_PROTOCOL)


@pytest.mark.parametrize('style', ['standard', 'brief'])
@pytest.mark.parametrize('phase', ['draft', 'reconstruction'])
@pytest.mark.parametrize('codepoint', [0xd800, 0xdc00])
def test_direct_capture_rejects_unpaired_surrogate_before_utf8_length_check(style, phase, codepoint):
    # This is an invalid raw Python string at the defensive capture boundary,
    # distinct from a JSON-escaped surrogate tested through owned transport.
    assert capture('{"invalid":"' + chr(codepoint) + '"}', style, phase) == {'capture_status': 'invalid_json'}


def authored(payload, phase, style, text='Gates regulate tidal water.'):
    unit = claim(text)
    paragraph = unit if phase == 'draft' else {'claims': [unit]}
    return select_response({'status': 'answered', **({'paragraph': paragraph} if style == 'brief'
                           else {'paragraphs': [paragraph]})}, payload)


@pytest.mark.parametrize('phase', ['draft', 'reconstruction'])
@pytest.mark.parametrize('status', ['answered', 'insufficient_evidence'])
@pytest.mark.parametrize('mask', range(16))
def test_every_slot_mask_and_status_has_no_partial_mapping(mask, status, phase):
    unit = {'text': 'Goa’s जल gates.', 'primary_support': {'citation_id': 'a', 'span_id': 's1'}, 'supports': []}
    paragraph = unit if phase == 'draft' else {'claims': [unit]}
    value = {'status': status, **{name: deepcopy(paragraph) if mask & (1 << i) else None
                                for i, name in enumerate(SLOT_NAMES)}}
    valid = mask in (1, 3, 7, 15) if status == 'answered' else mask == 0
    raw = encoded(value).decode()
    if not valid:
        with pytest.raises(AnswerEnvelopeError):
            decode_envelope(value, protocol=PARAGRAPH_PROTOCOL, style='standard', phase=phase)
        diagnostic = capture(raw, 'standard', phase)
        assert set(diagnostic) == {'capture_status'}
        return
    converted, mapping = decode_envelope(value, protocol=PARAGRAPH_PROTOCOL, style='standard', phase=phase)
    diagnostic = capture(raw, 'standard', phase)
    assert diagnostic['answer'] == value and diagnostic['derived_slot_mapping'] == mapping
    assert mapping['source_diagnostic_sha256'] == diagnostic['source_diagnostic_sha256'] == value_hash(value)
    for entry, actual in zip(mapping['slots'], converted['paragraphs']):
        assert encoded(actual) == encoded(value[entry['slot_name']])
        assert entry['value_sha256'] == value_hash(actual)
    assert len(converted['paragraphs']) == mask.bit_count()


@pytest.mark.parametrize('phase', ['draft', 'reconstruction'])
def test_member_order_cannot_change_named_slot_order(phase):
    values = [{'text': text} for text in ('First जल.', 'Second Goa’s.')]
    value = {'paragraph_4': None, 'paragraph_2': values[1], 'status': 'answered',
             'paragraph_3': None, 'paragraph_1': values[0]}
    converted, mapping = decode_envelope(value, protocol=PARAGRAPH_PROTOCOL, style='standard', phase=phase)
    assert encoded(converted['paragraphs']) == encoded(values)
    assert [s['slot_name'] for s in mapping['slots']] == ['paragraph_1', 'paragraph_2']


@pytest.mark.parametrize('mutation', ['missing', 'extra', 'fifth', 'array', 'wrong_type', 'unknown_status'])
@pytest.mark.parametrize('phase', ['draft', 'reconstruction'])
def test_invalid_envelope_capture_contains_no_answer_or_mapping(mutation, phase):
    value = slot_response({'status': 'answered', 'paragraphs': [{'text': 'Fixture.'}]})
    if mutation == 'missing':value.pop('paragraph_4')
    if mutation == 'extra':value['extra'] = 'private synthetic value'
    if mutation == 'fifth':value['paragraph_5'] = {'text': 'Fifth.'}
    if mutation == 'array':value = {'status': 'answered', 'paragraphs': [{'text': 'Fixture.'}] * 6}
    if mutation == 'wrong_type':value['paragraph_1'] = []
    if mutation == 'unknown_status':value['status'] = 'maybe'
    diagnostic = capture(json.dumps(value), 'standard', phase)
    assert set(diagnostic) == {'capture_status'}
    assert 'private synthetic value' not in json.dumps(diagnostic)


def invalid_json(raw, mutation, style):
    # The owned first phase now has plan labels/units, not prose slots.
    if '"points":' in raw:
        if mutation in ('slot','text','escaped_text','claims','surrogate','escaped_secret'):
            if mutation=='slot':return raw.replace('"units":','"units":[],"units":',1)
            if mutation=='text':return raw.replace('"need":','"need":"sk-ant-sensitive-fixture","need":',1)
            if mutation=='escaped_text':return raw.replace('"need":','"\\u006eeed":"fixture-only","need":',1)
            if mutation=='claims':return raw.replace('"linked_supports":','"linked_supports":[],"linked_supports":',1)
            if mutation=='surrogate':return raw.replace('"need":','"bad":"\\ud800","need":',1)
            secret=''.join('\\u%04x'%ord(c) for c in 'fixture-only')
            return raw.replace('"need":','"need":"'+secret+'","need":',1)
        if mutation in ('hole','missing_slot','fifth_slot','status_content','wrong_slot','unknown_status'):
            value=json.loads(raw)
            if mutation=='hole':value['units']=[]
            if mutation=='missing_slot':value.pop('units')
            if mutation=='fifth_slot':value['extra_unit']={}
            if mutation=='status_content':value['status']='insufficient_evidence'
            if mutation=='wrong_slot':value['units']={}
            if mutation=='unknown_status':value['status']='maybe'
            return json.dumps(value)
    if mutation == 'status':return raw.replace('"status":', '"status":"hidden-workspace","status":', 1)
    if mutation == 'slot':
        key = 'paragraph_1' if style == 'standard' else 'paragraph'
        return raw.replace('"' + key + '":', '"' + key + '":"fixture-only","' + key + '":', 1)
    if mutation == 'text':return raw.replace('"text":', '"text":"sk-ant-sensitive-fixture","text":', 1)
    if mutation == 'escaped_text':return raw.replace('"text":', '"\\u0074ext":"fixture-only","text":', 1)
    if mutation == 'claims':return raw.replace('"supports":', '"claims":[],"claims":[],"supports":', 1)
    if mutation == 'selector':return raw.replace('"span_id":', '"span_id":"hidden-workspace","span_id":', 1)
    if mutation == 'nan':return raw[:-1] + ',"invalid":NaN}'
    if mutation == 'infinity':return raw[:-1] + ',"invalid":Infinity}'
    if mutation == 'negative_infinity':return raw[:-1] + ',"invalid":-Infinity}'
    if mutation == 'overflow_float':return raw[:-1] + ',"invalid":1e999}'
    if mutation == 'malformed':return raw[:-1]
    if mutation == 'surrogate':return raw.replace('"text":', '"bad":"\\ud800","text":', 1)
    if mutation == 'depth':return '{\"a\":'*34+'0'+'}'*34
    if mutation == 'escaped_secret':
        secret=''.join('\\u%04x'%ord(c) for c in 'fixture-only')
        return raw.replace('\"text\":', '\"text\":\"'+secret+'\",\"text\":', 1)
    if mutation in ('hole','missing_slot','fifth_slot','status_content','wrong_slot','unknown_status'):
        value=json.loads(raw);key='paragraph_1' if style=='standard' else 'paragraph'
        if mutation=='hole':
            if style=='standard':value['paragraph_2']=value[key]
            value[key]=None
        if mutation=='missing_slot':value.pop('paragraph_4' if style=='standard' else 'paragraph')
        if mutation=='fifth_slot':value['paragraph_5']={}
        if mutation=='status_content':value['status']='insufficient_evidence'
        if mutation=='wrong_slot':value[key]=[]
        if mutation=='unknown_status':value['status']='maybe'
        return json.dumps(value)
    if mutation == 'legacy_array':return '{"status":"answered","paragraphs":[]}'
    raise AssertionError(mutation)


@pytest.mark.parametrize('style', ['standard', 'brief'])
@pytest.mark.parametrize('target', [1])
@pytest.mark.parametrize('mutation', ['status', 'slot', 'text', 'escaped_text', 'claims', 'selector',
                                    'nan', 'infinity', 'negative_infinity', 'overflow_float', 'malformed', 'legacy_array',
                                    'depth','surrogate','escaped_secret','hole','missing_slot','fifth_slot',
                                    'status_content','wrong_slot','unknown_status'])
def test_invalid_final_json_stops_before_payload_callback_for_every_style_and_stage(setup, monkeypatch, style, target, mutation):
    config, _, _, transport, limits, _, _, _ = setup
    request = ChatRequest(question='What do gates do?', answer_style=style)
    original = prepare_answer(request, [{'id': 'a', 'text': 'Gates regulate tidal water.'}], provider='anthropic')
    observed, callbacks = [], []
    invalid_returned = False
    original_scan = answer_trace.credential_like_content
    def scan(value, secrets=()):
        if invalid_returned:pytest.fail('Invalid final JSON reached decoded credential scanning')
        return original_scan(value, secrets)
    monkeypatch.setattr(answer_trace, 'credential_like_content', scan)
    async def handler(actual, n):
        payload = json.loads(json.loads(actual.content)['messages'][-1]['content'])
        raw = encoded(authored(payload, 'reconstruction', style)).decode()
        nonlocal invalid_returned
        if n == target:
            raw = invalid_json(raw, mutation, style)
            invalid_returned = True
        return model_response(None, content=[{'type': 'text', 'text': raw}])
    transport.handler = handler
    class ObservedClient(AsyncAnthropicClient):
        async def send(self, body, *, on_response, **kwargs):
            def response(metadata, payload=None):
                callbacks.append({'metadata': deepcopy(metadata), 'payload_present': payload is not None})
                on_response(metadata, payload)
            return await super().send(body, on_response=response, **kwargs)
    def factory():return ObservedClient('fixture-only', 'hidden-workspace', transport=transport)
    with pytest.raises(pipeline.PipelineFailure) as caught:
        asyncio.run(pipeline.run_answer_pipeline(request, original, config, limits=limits,
                     client_factory=factory, observer=observed.append))
    assert len(transport.requests) == len(limits.receipts) == target and transport.closed
    assert callbacks[-1]['payload_present'] is False
    assert callbacks[-1]['metadata']['provider_http_status'] == 200
    assert callbacks[-1]['metadata']['reported_usage']['output_tokens'] == 250
    assert 'response_validation_failure' in callbacks[-1]['metadata']
    phase = caught.value.trace['phases'][target - 1]
    assert 'final_output_diagnostic' not in phase and 'deterministic_support_resolution' not in phase
    assert 'final_answer' not in caught.value.trace
    saved = json.dumps([observed, callbacks, caught.value.trace])
    assert all(secret not in saved for secret in ('fixture-only', 'hidden-workspace', 'sk-ant-sensitive-fixture'))


@pytest.mark.parametrize('style', ['standard', 'brief'])
@pytest.mark.parametrize('phase', ['draft', 'reconstruction'])
def test_capture_and_normalizer_defensively_reject_duplicates(setup, style, phase):
    _, _, _, _, _, _, _, _ = setup
    request = ChatRequest(question='What do gates do?', answer_style=style)
    original = prepare_answer(request, [{'id': 'a', 'text': 'Gates regulate tidal water.'}], provider='anthropic')
    prepared = (prepare_span_draft(request, original) if phase == 'draft' else
                prepare_reconstruction(request, original, {'status':'insufficient_evidence','points':[],'units':[]}))
    payload = json.loads(prepared.messages[-1]['content'])
    raw = invalid_json(encoded(authored(payload, phase, style)).decode(), 'escaped_text', style)
    diagnostic = capture(raw, style, phase)
    assert diagnostic == {'capture_status': 'duplicate_json_key'}
    observed = []
    normalizer = normalize_span_draft if phase == 'draft' else normalize_reconstruction
    with pytest.raises(ValueError):normalizer(raw, prepared, resolved_observer=observed.append)
    if phase=='draft':assert observed==[]
    else:
        assert 'slot_mapping' not in observed[-1]
        assert not observed[-1]['complete']


@pytest.mark.parametrize('style', ['standard', 'brief'])
def test_valid_unicode_answer_keeps_exact_text_and_original_slot_traces(setup, style):
    config, _, _, transport, limits, _, _, factory = setup
    text = 'Goa’s जल gates regulate tidal water.'
    request = ChatRequest(question='What do gates do?', answer_style=style)
    original = prepare_answer(request, [{'id': 'a', 'text': text}], provider='anthropic')
    async def handler(actual, n):
        payload = json.loads(json.loads(actual.content)['messages'][-1]['content'])
        unit = claim(text, quote=text)
        paragraph = {'claims': [unit]}
        return model_response(select_response({'status': 'answered', **({'paragraph': paragraph}
            if style == 'brief' else {'paragraphs': [paragraph]})}, payload))
    transport.handler = handler
    result = asyncio.run(pipeline.run_answer_pipeline(request, original, config, limits=limits, client_factory=factory))
    assert result.answer['paragraphs'] == [{'text': text, 'citations': ['a']}]
    expected_slot = 'paragraph_1' if style == 'standard' else 'paragraph'
    for phase in result.trace['phases']:
        diagnostic = phase['final_output_diagnostic']
        resolution = phase['deterministic_support_resolution']
        records = resolution['claims']
        assert records[0]['slot_name'] == expected_slot
        if style == 'standard':
            assert diagnostic['derived_slot_mapping'] == resolution['slot_mapping']
            assert diagnostic['answer']['paragraph_1'] is not None
        else:
            assert 'slot_mapping' not in resolution and 'derived_slot_mapping' not in diagnostic
            assert 'native_brief' in diagnostic['representation']
            assert set(diagnostic['answer']) == {'status', 'paragraph'}
    offset = result.trace['assembly_offsets'][0]
    assert offset['slot_name'] == expected_slot
    assert result.answer['paragraphs'][0]['text'][offset['start']:offset['end']] == text


@pytest.mark.parametrize('style', ['standard', 'brief'])
def test_valid_insufficient_evidence_keeps_style_specific_shape_through_sole_final_phase(setup, style):
    config, _, _, transport, limits, _, _, factory = setup
    request = ChatRequest(question='What do gates do?', answer_style=style)
    original = prepare_answer(request, [{'id': 'a', 'text': 'Gates regulate tidal water.'}], provider='anthropic')
    value = ({'status': 'insufficient_evidence', 'paragraph': None} if style == 'brief' else
             slot_response({'status': 'insufficient_evidence', 'paragraphs': []}))
    async def handler(req,n):return model_response(value)
    transport.handler = handler
    result = asyncio.run(pipeline.run_answer_pipeline(request, original, config, limits=limits, client_factory=factory))
    assert result.answer['status'] == 'insufficient_evidence' and result.answer['paragraphs'] == []
    assert len(transport.requests) == len(limits.receipts) == 1
    for phase in result.trace['phases']:
        assert phase['final_output_diagnostic']['answer'] == value
        if style == 'brief':assert 'derived_slot_mapping' not in phase['final_output_diagnostic']


@pytest.mark.parametrize('change', [{'paragraph_protocol': None}, {'paragraph_protocol': 'legacy'},
                                  {'answer_style': 'brief'}, {'phase': 'draft'}])
def test_transport_refuses_untrusted_or_inconsistent_context_before_io(setup, change):
    config, request, original, transport, _, _, _, factory = setup
    body = reconstruction_message_request(config, prepare_reconstruction(request, original, {'status':'insufficient_evidence','points':[],'units':[]}))
    context = {'paragraph_protocol': PARAGRAPH_PROTOCOL, 'answer_style': 'standard', 'phase': 'reconstruction',
               'pipeline_version': PIPELINE_VERSION, 'effort_policy': EFFORT_POLICY,
               'base_config_effort': 'medium','plan_protocol':'bounded_source_plan_v1',
               'final_internal_protocol':'planned_claim_supports_v1', **change}
    def no_callback(*_):pytest.fail('Invalid context must not reach a request or response callback')
    async def scenario():
        async with factory() as client:
            with pytest.raises(AnswerEnvelopeError):
                await client.send(body, on_request=no_callback, on_response=no_callback, **context)
    asyncio.run(scenario())
    assert not transport.requests and transport.closed
