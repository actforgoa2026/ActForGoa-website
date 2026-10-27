"""Small native Messages adapter: one fixed-host request, no retries or tools."""
from copy import deepcopy
import json

import httpx

ENDPOINT = 'https://api.anthropic.com/v1/messages'
API_VERSION = '2026-10-21'
MAX_SCHEMA_BYTES = 4096
# In addition to prepare_answer's message bytes + 2,048 framing tokens:
# 4,096 bytes for the native schema + 4,096 tokens for format/system overhead.
INPUT_ALLOWANCE = MAX_SCHEMA_BYTES + 4096
PRICE_TIER_INPUT_LIMIT = 100_000


class AnthropicAPIError(Exception):
    """Keep provider payloads, credentials and request content out of errors."""
    def __init__(self, status_code=None):
        self.status_code = status_code
        super().__init__('Anthropic request failed')


def native_schema(schema):
    if not isinstance(schema, dict):
        raise ValueError('Missing structured answer schema')
    result = deepcopy(schema)

    def simplify(value):
        if isinstance(value, dict):
            # Unsupported by native JSON outputs. Original constraints remain in
            # the prompt and are enforced locally against the parsed answer.
            for key in ('minLength', 'maxLength', 'maxItems'):
                value.pop(key, None)
            for child in value.values():
                simplify(child)
        elif isinstance(value, list):
            for child in value:
                simplify(child)

    simplify(result)
    if len(json.dumps(result, ensure_ascii=False, separators=(',', ':')).encode()) > MAX_SCHEMA_BYTES:
        raise ValueError('The native answer schema exceeds its reserved allowance')
    return result


# These are fields actually represented in the request, never hidden library
# metadata. Provenance can qualify a claim but cannot replace passage support.
SUPPORT_FIELDS = ('text', 'warning', 'legal_currency',
                  'source_date_metadata.reviewed_locator_and_dates',
                  'source_date_metadata.date_caution', 'guide_verification.limitations')
MAX_SUPPORTS = 10
MAX_QUOTE_CHARS = 600


def native_answer_schema(schema, answer_style):
    # Keep the public schema independent of the native evidence contract.
    native_schema(schema)  # Reject an oversized caller schema before conversion.
    identifiers = schema['properties']['paragraphs']['items']['properties']['citations']['items']['enum']
    support = {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'citation_id': {'type': 'string', 'enum': identifiers},
            'field': {'type': 'string', 'enum': list(SUPPORT_FIELDS)},
            'quote': {'type': 'string'},
        }, 'required': ['citation_id', 'field', 'quote'],
    }
    primary = deepcopy(support)
    primary['properties']['field']['enum'] = ['text']
    paragraph = {
        'type': 'object', 'additionalProperties': False,
        'properties': {'text': {'type': 'string'}, 'primary_support': primary,
                       'supports': {'type': 'array', 'items': support}},
        'required': ['text', 'primary_support', 'supports'],
    }
    key = 'paragraph' if answer_style == 'brief' else 'paragraphs'
    value = {'anyOf': [paragraph, {'type': 'null'}]} if key == 'paragraph' else {'type': 'array', 'items': paragraph}
    return native_schema({
        'type': 'object', 'additionalProperties': False,
        'properties': {'status': schema['properties']['status'], key: value},
        'required': ['status', key],
    })


def native_answer_instructions(instructions, answer_style):
    # Native-only substitution: other providers retain their existing contracts.
    instructions = instructions.replace(
        'Put evidence IDs only in the citations array, never in paragraph text.',
        'Put evidence IDs only in primary_support.citation_id or supports.citation_id, never in paragraph text.')
    if answer_style == 'standard':
        instructions = instructions.replace(
            'If answering, address the actual question in at most four paragraphs and 350 words; omit unrelated background.',
            'If answering, address only the requested points in the fewest sufficient paragraphs, '
            'within four paragraphs and 350 words. For conceptual distinctions, explain the distinction '
            'directly without unrequested numerical examples. Omit unrelated procedures and background.')
    shape = ('Return only status and paragraph. For answered, paragraph is one object; '
             'for insufficient_evidence, paragraph is null. Never return a paragraphs array.'
             if answer_style == 'brief' else
             'Return only status and paragraphs. For answered, paragraphs contains one to four objects; '
             'for insufficient_evidence, paragraphs is an empty array.')
    return instructions + '\n' + shape + (
        ' Each object has text, primary_support and supports only. '
        'primary_support is one object with citation_id, field set to text, and quote. '
        'supports is an array of zero to nine additional objects with citation_id, field and quote. '
        'Use an exact selected passage ID. field is one of: ' + ', '.join(SUPPORT_FIELDS) + '. '
        'For each support, copy a contiguous quote of 1 to 600 characters from that passage field '
        'or its referenced source field. Whitespace may be normalized; spelling, case and punctuation must stay exact. '
        'Attach caveats and source limitations to the associated text-supported claim unit; never add a metadata-only conclusion. '
        'The other allowed fields support only explicit dates, '
        'source limitations and provenance qualifications, never substantive ecological claims. '
        'catalogue_scope_hint is a catalogue title for document identity, jurisdiction and version context only. '
        'It does not prove authorship, publication dates, advocacy or official status, or current law. '
        'Do not quote the hint, hidden metadata or other page text as support. '
        'Before returning, check every clause, opening statement and definition against its own paragraph supports. '
        'Retain entity, habitat, taxonomic, geographic and time qualifiers, including annual measurement periods. '
        'Do not infer authorship, advocacy or official status from a host or catalogue label, or add definitions absent from the evidence. '
        'Do not label extraction OCR unless the supplied warning explicitly says so. '
        'Rewrite or omit unsupported claims; do not borrow support from another paragraph. '
        'Quotes anchor evidence but do not establish entailment by themselves.'
    )


def _represented_fields(prepared):
    # Resolve against exactly the payload visible to the model. Hidden metadata
    # in prepared.evidence cannot legitimize a quote absent from the request.
    payload = json.loads(prepared.messages[-1]['content'])
    allowed = {e['id'] for e in prepared.evidence}
    fields = {}
    for passage in payload['evidence']:
        if passage['id'] not in allowed:
            continue
        source = payload['sources'][passage['source']]
        fields[passage['id']] = {}
        for name in SUPPORT_FIELDS:
            value = passage if name in ('text', 'warning') else source
            for part in name.split('.'):
                value = value.get(part) if isinstance(value, dict) else None
            if isinstance(value, str):
                fields[passage['id']][name] = value
    return fields


def _represented_contexts(prepared):
    """Use the visible dependency contract and reject local/wire disagreement."""
    payload = json.loads(prepared.messages[-1]['content'])
    expected = {item['id']: item.get('context_ids', []) for item in prepared.evidence}
    visible = {item['id']: item.get('context_ids', []) for item in payload['evidence']}
    if visible != expected or any(
        not isinstance(contexts, list)
        or any(not isinstance(context, str) or context not in visible or context == identifier
               for context in contexts)
        for identifier, contexts in visible.items()
    ):
        raise ValueError('Source context differs from the model-visible evidence contract')
    return visible


def normalize_native_answer(content, prepared):
    from .chat import Paragraph, citation_text
    from pydantic import ValidationError
    try:
        payload = json.loads(content)
        key = 'paragraph' if prepared.answer_style == 'brief' else 'paragraphs'
        if (not isinstance(payload, dict) or set(payload) != {'status', key}
                or payload['status'] not in ('answered', 'insufficient_evidence')):
            raise ValueError()
        units = [payload[key]] if key == 'paragraph' and payload[key] is not None else payload[key]
        if payload['status'] == 'insufficient_evidence':
            if payload[key] != (None if key == 'paragraph' else []):
                raise ValueError()
            units = []
        elif not isinstance(units, list) or not 1 <= len(units) <= (1 if key == 'paragraph' else 4):
            raise ValueError()
        fields = _represented_fields(prepared)
        contexts = _represented_contexts(prepared)
        paragraphs = []
        for unit in units:
            if (not isinstance(unit, dict) or set(unit) != {'text', 'primary_support', 'supports'}
                    or not isinstance(unit['primary_support'], dict) or unit['primary_support'].get('field') != 'text'
                    or not isinstance(unit['supports'], list) or not 0 <= len(unit['supports']) < MAX_SUPPORTS):
                raise ValueError()
            citations = []
            text_supports = set()
            for support in [unit['primary_support'], *unit['supports']]:
                if not isinstance(support, dict) or set(support) != {'citation_id', 'field', 'quote'}:
                    raise ValueError()
                identifier, field, quote = (support[k] for k in ('citation_id', 'field', 'quote'))
                if (not all(isinstance(v, str) for v in (identifier, field, quote))
                        or not 1 <= len(quote) <= MAX_QUOTE_CHARS or not quote.strip()
                        or field not in fields.get(identifier, {})
                        or ' '.join(quote.split()) not in ' '.join(fields[identifier][field].split())):
                    raise ValueError()
                if identifier not in citations:
                    citations.append(identifier)
                if field == 'text':
                    text_supports.add(identifier)
            if any(context not in text_supports for identifier in citations for context in contexts[identifier]):
                raise ValueError()
            paragraph = Paragraph.model_validate({'text': unit['text'], 'citations': citations}, strict=True)
            # Shared display cleanup must not silently rewrite a native claim.
            if citation_text(paragraph.text, fields) != paragraph.text:
                raise ValueError()
            paragraphs.append(paragraph.model_dump())
    except (ValueError, ValidationError, KeyError, TypeError):
        raise ValueError('The native answer did not match the evidence contract') from None
    return json.dumps({'status': payload['status'], 'paragraphs': paragraphs}, ensure_ascii=False)


def reviewed_effort(model, effort):
    allowed = {'claude-haiku-5-5': ('medium',), 'claude-sonnet-5-5': ('medium', 'high')}
    if not isinstance(effort, str) or effort not in allowed.get(model, ()):
        raise ValueError('This Anthropic model and effort combination needs a reviewed configuration')
    return effort


def message_request(config, prepared):
    # Recheck the same reviewed rate tier before dispatch, even for direct callers.
    from .chat import MAX_PROMPT_BYTES, FRAMING_TOKEN_ALLOWANCE
    config.maximum_cost_microusd(prepared.input_token_bound)
    schema = native_answer_schema(prepared.schema, prepared.answer_style)
    system = prepared.messages[0]['content']
    if not prepared.base_instructions:
        raise ValueError('Missing native answer instructions')
    expected = native_answer_instructions(prepared.base_instructions, prepared.answer_style)
    if system != expected:
        raise ValueError('Native answer context was not prepared before budgeting')
    messages = [{'role': 'system', 'content': system}, *prepared.messages[1:]]
    size = len(json.dumps(messages, ensure_ascii=False, separators=(',', ':')).encode())
    if size > MAX_PROMPT_BYTES or size + FRAMING_TOKEN_ALLOWANCE > prepared.input_token_bound:
        raise ValueError('The native prompt exceeds its reserved allowance')
    _represented_contexts(prepared)
    return {
        'model': config.model,
        'max_tokens': config.max_output_tokens,
        'system': system,
        'messages': prepared.messages[1:],
        'stream': False,
        'service_tier': 'standard_only',
        'thinking': {'type': 'adaptive'},
        'output_config': {
            'effort': reviewed_effort(config.model, config.effort),
            'format': {'type': 'json_schema', 'schema': schema},
        },
    }



class AnthropicClient:
    def __init__(self, api_key, workspace_id=None, *, transport=None):
        headers = {'Authorization': 'Bearer ' + api_key, 'anthropic-version': API_VERSION}
        if workspace_id:
            headers['anthropic-workspace-id'] = workspace_id
        self._http = httpx.Client(
            headers=headers, timeout=httpx.Timeout(60, connect=10, write=10, pool=10),
            follow_redirects=False, trust_env=False,
            transport=transport if transport is not None else httpx.HTTPTransport(retries=0),
        )

    def answer(self, config, prepared):
        body = message_request(config, prepared)
        try:
            response = self._http.post(ENDPOINT, json=body, follow_redirects=False)
        except httpx.HTTPError:
            raise AnthropicAPIError() from None
        if response.status_code != 200:
            raise AnthropicAPIError(response.status_code)
        try:
            message = response.json()
        except ValueError:
            raise ValueError('The answer service returned an invalid response') from None
        if (not isinstance(message, dict) or message.get('type') != 'message'
                or message.get('role') != 'assistant' or message.get('model') != config.model):
            raise ValueError('The answer service returned an unexpected response')
        if message.get('stop_reason') != 'end_turn' or message.get('stop_details'):
            raise ValueError('The answer was incomplete or declined')
        blocks = message.get('content')
        if not isinstance(blocks, list):
            raise ValueError('No structured answer was returned')
        texts = []
        for block in blocks:
            if not isinstance(block, dict):
                raise ValueError('The answer service returned invalid content')
            kind = block.get('type')
            if kind == 'text' and isinstance(block.get('text'), str):
                texts.append(block['text'])
            elif kind not in ('thinking', 'redacted_thinking'):
                raise ValueError('The answer service returned unsupported content')
        if not texts or not ''.join(texts).strip():
            raise ValueError('No structured answer was returned')
        content = ''.join(texts)
        return normalize_native_answer(content, prepared)

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
