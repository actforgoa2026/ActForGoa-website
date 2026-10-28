"""Strict response decoding and lossless, bounded standard paragraph envelopes."""
from copy import deepcopy
import hashlib
import json
import math

PARAGRAPH_PROTOCOL = 'four_nullable_slots_v1'
SLOT_NAMES = tuple(f'paragraph_{i}' for i in range(1, 5))


class AnswerEnvelopeError(ValueError):
    """Fixed categories only: never include provider keys, values or raw text."""
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def value_hash(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def strict_answer_json(content):
    def unique(pairs):
        value = {}
        for key, child in pairs:
            if key in value:
                raise AnswerEnvelopeError('duplicate_json_key')
            value[key] = child
        return value
    def constant(_):
        raise AnswerEnvelopeError('invalid_json_constant')
    def bounded(value, depth=0):
        if depth > 32:
            raise AnswerEnvelopeError('answer_depth_exceeded')
        if isinstance(value, float) and not math.isfinite(value):
            raise AnswerEnvelopeError('invalid_json_constant')
        if isinstance(value, str):value.encode()
        if isinstance(value, dict):
            for key, child in value.items():
                key.encode()
                bounded(child, depth + 1)
        elif isinstance(value, list):
            for child in value:bounded(child, depth + 1)
    try:
        if not isinstance(content, str):raise AnswerEnvelopeError('invalid_json')
        if len(content.encode()) > 65536:raise AnswerEnvelopeError('oversize_text')
        value = json.loads(content, object_pairs_hook=unique, parse_constant=constant)
        bounded(value)
        return value
    except AnswerEnvelopeError:
        raise
    except (ValueError, TypeError, RecursionError, UnicodeError):
        raise AnswerEnvelopeError('invalid_json') from None


def check_context(*, protocol, style, phase):
    if protocol != PARAGRAPH_PROTOCOL or style not in ('standard', 'brief') or phase not in ('draft', 'reconstruction'):
        raise AnswerEnvelopeError('unexpected_answer_protocol')


def check_request_context(body, *, protocol, style, phase):
    """Match trusted execution context to the frozen outbound request shape."""
    check_context(protocol=protocol, style=style, phase=phase)
    try:
        schema = body['output_config']['format']['schema']
        keys = {'status', *SLOT_NAMES} if style == 'standard' else {'status', 'paragraph'}
        if set(schema['properties']) != keys or set(schema['required']) != keys:raise ValueError()
        paragraph = (schema['definitions']['paragraph'] if style == 'standard'
                     else schema['properties']['paragraph']['anyOf'][0])
        expected = {'primary_support', 'supports', 'text'} if phase == 'draft' else {'claims'}
        if set(paragraph['properties']) != expected:raise ValueError()
        request = json.loads(body['messages'][-1]['content'])
        if request['request_scope']['answer_style'] != style:raise ValueError()
    except (KeyError, IndexError, TypeError, ValueError):
        raise AnswerEnvelopeError('request_answer_protocol_mismatch') from None


def standard_slot_schema(schema, style):
    if style == 'brief':return deepcopy(schema)
    if style != 'standard':raise AnswerEnvelopeError('unexpected_answer_protocol')
    paragraph = deepcopy(schema['properties']['paragraphs']['items'])
    return {'type': 'object', 'additionalProperties': False,
            'properties': {'status': deepcopy(schema['properties']['status']),
                **{slot: {'anyOf': [{'$ref': '#/definitions/paragraph'}, {'type': 'null'}]}
                   for slot in SLOT_NAMES}},
            'required': ['status', *SLOT_NAMES], 'definitions': {'paragraph': paragraph}}


def decode_envelope(value, *, protocol, style, phase):
    """Convert only a valid envelope; all inner values remain exactly unchanged.

    The returned mapping establishes envelope identity, never answer validity.
    A malformed envelope yields neither a partial paragraph list nor a mapping.
    """
    check_context(protocol=protocol, style=style, phase=phase)
    keys = {'status', *SLOT_NAMES} if style == 'standard' else {'status', 'paragraph'}
    if not isinstance(value, dict) or set(value) != keys:
        raise AnswerEnvelopeError('unexpected_slot_shape' if style == 'standard' else 'unexpected_brief_shape')
    if value['status'] not in ('answered', 'insufficient_evidence'):
        raise AnswerEnvelopeError('unexpected_answer_status')
    if style == 'brief':
        if (value['status'] == 'answered' and type(value['paragraph']) is not dict
                or value['status'] == 'insufficient_evidence' and value['paragraph'] is not None):
            raise AnswerEnvelopeError('answer_status_content_mismatch')
        return deepcopy(value), None
    paragraphs, slots, null_seen = [], [], False
    for name in SLOT_NAMES:
        paragraph = value[name]
        if paragraph is None:
            null_seen = True
            continue
        if type(paragraph) is not dict:raise AnswerEnvelopeError('unexpected_slot_type')
        if null_seen:raise AnswerEnvelopeError('unexpected_slot_hole')
        slots.append({'slot_name': name, 'paragraph_index': len(paragraphs),
                      'value_sha256': value_hash(paragraph)})
        paragraphs.append(deepcopy(paragraph))
    if (value['status'] == 'answered' and not paragraphs
            or value['status'] == 'insufficient_evidence' and paragraphs):
        raise AnswerEnvelopeError('answer_status_content_mismatch')
    mapping = {'kind': 'deterministic_slot_mapping', 'protocol': protocol,
               'source_diagnostic_sha256': value_hash(value), 'complete': True, 'slots': slots}
    return {'status': value['status'], 'paragraphs': paragraphs}, mapping


def source_slot(style, index):
    return SLOT_NAMES[index] if style == 'standard' else 'paragraph'
