"""Bounded native Anthropic Messages calls, with no automatic retries."""
from decimal import Decimal, ROUND_CEILING
import json
import os
import httpx

ENDPOINT = 'https://api.anthropic.com/v1/messages'
# Preserves the model and reviewed standard price from the prior integration.
MODEL_PRICES = {'claude-haiku-5-5': ('0.10', '0.50'), 'claude-sonnet-5-5': ('2.00', '10.00')}
DEFAULT_MODEL = 'claude-haiku-5-5'
MAX_OUTPUT_TOKENS = 4096
MAX_PROMPT_BYTES = 28000


class AnthropicAPIError(Exception):
    def __init__(self, status_code=None):
        self.status_code = status_code
        super().__init__('The answer provider could not complete this request.')


def configured_model():
    model = os.getenv('ANTHROPIC_CHAT_MODEL', DEFAULT_MODEL)
    if model not in MODEL_PRICES:
        raise ValueError('This model requires a reviewed budget rate before activation.')
    return model


def maximum_cost(model, payload):
    # UTF-8 bytes conservatively bound text tokens; include framing/tool overhead.
    size = len(json.dumps(payload, ensure_ascii=False).encode())
    if size > MAX_PROMPT_BYTES:
        raise ValueError('The answer prompt exceeds its bounded input allowance.')
    input_rate, output_rate = map(Decimal, MODEL_PRICES[model])
    return int(((size + 8192) * input_rate + MAX_OUTPUT_TOKENS * output_rate).to_integral_value(rounding=ROUND_CEILING))


def maximum_request_cost(model):
    input_rate, output_rate = map(Decimal, MODEL_PRICES[model])
    return int(((MAX_PROMPT_BYTES + 8192) * input_rate + MAX_OUTPUT_TOKENS * output_rate).to_integral_value(rounding=ROUND_CEILING))


class AnthropicAnswers:
    def __init__(self, key, http_client=None):
        self.key = key
        self.http = http_client or httpx.Client(timeout=60, follow_redirects=False)

    def close(self):
        self.http.close()

    def answer(self, model, payload):
        try:
            response = self.http.post(ENDPOINT, headers={
                'x-api-key': self.key, 'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            }, json={'model': model, 'max_tokens': MAX_OUTPUT_TOKENS, **payload})
            if response.status_code != 200:
                raise AnthropicAPIError(response.status_code)
            body = response.json()
            if not isinstance(body, dict) or body.get('stop_reason') != 'tool_use':
                raise ValueError('Incomplete structured answer')
            if not isinstance(body.get('content'), list):
                raise ValueError('Invalid answer content')
            calls = [item for item in body['content'] if isinstance(item, dict) and item.get('type') == 'tool_use']
            if len(calls) != 1 or calls[0].get('name') != 'answer_library_question':
                raise ValueError('Missing structured answer')
            if not isinstance(calls[0].get('input'), dict):
                raise ValueError('Invalid structured answer')
            return calls[0]['input']
        except (httpx.HTTPError, json.JSONDecodeError) as error:
            raise AnthropicAPIError() from None
