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


def native_brief_schema(schema):
    # Native outputs cannot enforce maxItems. A nullable object represents
    # exactly one paragraph, with no array to silently combine or truncate.
    return native_schema({
            'type': 'object', 'additionalProperties': False,
            'properties': {
                'status': schema['properties']['status'],
                'paragraph': {'anyOf': [schema['properties']['paragraphs']['items'], {'type': 'null'}]},
            },
            'required': ['status', 'paragraph'],
        })


def native_brief_instructions(instructions, schema):
    return instructions + (
            '\nReturn only status and paragraph. For answered, paragraph is one object with text and citations; '
            'for insufficient_evidence, paragraph is null. Never return a paragraphs array. '
            'Return JSON conforming to this inline schema: '
        ) + json.dumps(schema, ensure_ascii=False, separators=(',', ':'))


def message_request(config, prepared):
    # Recheck the same reviewed rate tier before dispatch, even for direct callers.
    from .chat import MAX_PROMPT_BYTES, FRAMING_TOKEN_ALLOWANCE
    config.maximum_cost_microusd(prepared.input_token_bound)
    schema = native_schema(prepared.schema)
    system = prepared.messages[0]['content']
    if prepared.answer_style == 'brief':
        if not prepared.base_instructions:
            raise ValueError('Missing native brief instructions')
        schema = native_brief_schema(prepared.schema)
        expected = native_brief_instructions(prepared.base_instructions, schema)
        if system != expected:
            raise ValueError('Native brief context was not prepared before budgeting')
    messages = [{'role': 'system', 'content': system}, *prepared.messages[1:]]
    size = len(json.dumps(messages, ensure_ascii=False, separators=(',', ':')).encode())
    if size > MAX_PROMPT_BYTES or size + FRAMING_TOKEN_ALLOWANCE > prepared.input_token_bound:
        raise ValueError('The native prompt exceeds its reserved allowance')
    return {
        'model': config.model,
        'max_tokens': config.max_output_tokens,
        'system': system,
        'messages': prepared.messages[1:],
        'stream': False,
        'service_tier': 'standard_only',
        'thinking': {'type': 'adaptive'},
        'output_config': {
            'effort': 'medium',
            'format': {'type': 'json_schema', 'schema': schema},
        },
    }


def normalize_brief_answer(content, prepared):
    # Delayed import avoids the chat -> providers -> adapter import cycle.
    from pydantic import ValidationError
    from .chat import Paragraph
    try:
        payload = json.loads(content)
        if (not isinstance(payload, dict) or set(payload) != {'status', 'paragraph'}
                or payload['status'] not in ('answered', 'insufficient_evidence')):
            raise ValueError()
        if payload['status'] == 'insufficient_evidence':
            if payload['paragraph'] is not None:raise ValueError()
            paragraphs = []
        else:
            paragraph = Paragraph.model_validate(payload['paragraph'], strict=True)
            allowed = prepared.schema['properties']['paragraphs']['items']['properties']['citations']['items']['enum']
            if any(c not in allowed for c in paragraph.citations):
                raise ValueError()
            paragraphs = [paragraph.model_dump()]
    except (ValueError, ValidationError):
        raise ValueError('The native brief answer did not match the required schema') from None
    return json.dumps({'status': payload['status'], 'paragraphs': paragraphs}, ensure_ascii=False)


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
        return normalize_brief_answer(content, prepared) if prepared.answer_style == 'brief' else content

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
