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


def message_request(config, prepared):
    # Recheck the same reviewed rate tier before dispatch, even for direct callers.
    config.maximum_cost_microusd(prepared.input_token_bound)
    size = len(json.dumps(prepared.messages, ensure_ascii=False, separators=(',', ':')).encode())
    if size > prepared.input_token_bound:
        raise ValueError('The native prompt exceeds its reserved allowance')
    return {
        'model': config.model,
        'max_tokens': config.max_output_tokens,
        'system': prepared.messages[0]['content'],
        'messages': prepared.messages[1:],
        'stream': False,
        'service_tier': 'standard_only',
        'thinking': {'type': 'adaptive'},
        'output_config': {
            'effort': 'medium',
            'format': {'type': 'json_schema', 'schema': native_schema(prepared.schema)},
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
        return ''.join(texts)

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
