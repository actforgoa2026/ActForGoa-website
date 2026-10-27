"""Server-only model configuration and conservative, versioned inference prices."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
import os
import re
from urllib.parse import urlsplit
from openai import OpenAI
from .anthropic_provider import AnthropicClient, INPUT_ALLOWANCE, PRICE_TIER_INPUT_LIMIT, reviewed_effort

# USD per million tokens, standard uncached rates (Singapore for direct Qwen).
# Anthropic includes an extra native-schema allowance and a 100K tier guard;
# other providers keep their existing prompt bounds. Review rates before changes.
# Verified 2026-10-26: https://openrouter.ai/qwen/qwen3.7-flash
# https://openrouter.ai/openai/gpt-5-nano/pricing
# and https://www.alibabacloud.com/help/en/model-studio/model-pricing
# OpenRouter requests enforce these ceilings; credit-purchase fees are separate.
PRICES = {
    # https://platform.claude.com/docs/en/models/haiku-5-5/overview (2026-10-27)
    ('anthropic', 'claude-haiku-5-5'): ('0.10', '0.50'),
    # Explicit opt-in comparison; the Anthropic default remains Haiku.
    # https://platform.claude.com/docs/en/models/sonnet-5-5/overview (2026-10-27)
    ('anthropic', 'claude-sonnet-5-5'): ('2.00', '10.00'),
    ('openrouter', 'qwen/qwen3.7-flash'): ('0.030', '0.130'),
    ('openrouter', 'qwen/qwen3.8-flash'): ('0.15', '0.47'),
    ('openrouter', 'openai/gpt-5-nano'): ('0.05', '0.40'),
    ('openrouter', 'openai/gpt-5.6-luna'): ('0.20', '1.20'),
    ('qwen', 'qwen3.7-flash-2026-07-15'): ('0.030', '0.130'),
    ('qwen', 'qwen3.8-flash'): ('0.15', '0.47'),
    ('openai', 'gpt-5-mini'): ('0.25', '2.00'),
    ('openai', 'gpt-5.6-luna'): ('0.20', '1.20'),
}


@dataclass(frozen=True)
class ChatConfig:
    provider: str
    model: str
    label: str
    key_name: str
    base_url: str
    max_output_tokens: int = 1800
    route: str = 'alibaba'
    structured: bool = False
    effort: str = 'medium'
    pipeline: str = 'single_pass'

    def maximum_cost_microusd(self, input_token_bound):
        if not isinstance(input_token_bound, int) or input_token_bound < 0:
            raise ValueError('Invalid input token bound')
        if self.provider == 'anthropic':
            input_token_bound += INPUT_ALLOWANCE
            if input_token_bound > PRICE_TIER_INPUT_LIMIT:
                raise ValueError('Anthropic input exceeds the reviewed price tier')
        input_rate, output_rate = map(Decimal, PRICES[(self.provider, self.model)])
        # USD/million tokens multiplied by token count is micro-USD. Round up.
        return int((input_token_bound * input_rate + self.max_output_tokens * output_rate)
                   .to_integral_value(rounding=ROUND_CEILING))

    def client(self):
        key = os.getenv(self.key_name)
        if self.provider == 'anthropic':
            return AnthropicClient(key, os.getenv('ANTHROPIC_WORKSPACE_ID')) if key else None
        # No SDK retries: each budget reservation covers exactly one provider attempt.
        return OpenAI(api_key=key, base_url=self.base_url, timeout=60, max_retries=0) if key else None

    def async_client(self):
        from .async_anthropic import AsyncAnthropicClient
        if self.provider != 'anthropic' or self.pipeline != 'two_pass_v3':
            raise ValueError('Async reconstruction requires an explicit reviewed pipeline')
        key = os.getenv(self.key_name)
        if not key:
            raise ValueError('Answers are not configured')
        return AsyncAnthropicClient(key, os.getenv('ANTHROPIC_WORKSPACE_ID'))


def chat_config():
    provider = os.getenv('RESEARCH_CHAT_PROVIDER', 'openrouter')
    if provider == 'openrouter':
        model=os.getenv('OPENROUTER_CHAT_MODEL', 'openai/gpt-5.6-luna')
        is_openai=model.startswith('openai/')
        config = ChatConfig(provider, model,
                            'OpenRouter and OpenAI' if is_openai else 'OpenRouter and Alibaba Cloud (Qwen)', 'OPENROUTER_API_KEY',
                            'https://openrouter.ai/api/v1',max_output_tokens=3500 if is_openai else 1800,route='openai' if is_openai else 'alibaba',
                            structured=is_openai or model=='qwen/qwen3.8-flash')
    elif provider == 'qwen':
        model = os.getenv('QWEN_CHAT_MODEL', 'qwen3.7-flash-2026-07-15')
        endpoint = os.getenv('QWEN_BASE_URL', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1').rstrip('/')
        url = urlsplit(endpoint)
        # Keep credentials on Alibaba's Singapore endpoints and the quoted price region.
        if (url.scheme != 'https' or url.username or url.password or url.port or url.query or url.fragment
                or url.path != '/compatible-mode/v1'
                or not (url.hostname == 'dashscope-intl.aliyuncs.com'
                        or re.fullmatch(r'[a-z0-9-]+\.ap-southeast-1\.maas\.aliyuncs\.com', url.hostname or ''))):
            raise ValueError('QWEN_BASE_URL must be an Alibaba Singapore OpenAI-compatible endpoint')
        config = ChatConfig(provider, model, 'Alibaba Cloud (Qwen)', 'DASHSCOPE_API_KEY', endpoint)
    elif provider == 'anthropic':
        model = os.getenv('ANTHROPIC_CHAT_MODEL', 'claude-haiku-5-5')
        effort = reviewed_effort(model, os.getenv('ANTHROPIC_CHAT_EFFORT', 'medium'))
        config = ChatConfig(provider, model,
                            'Anthropic', 'ANTHROPIC_API_KEY', 'https://api.anthropic.com/v1',
                            max_output_tokens=12000 if model == 'claude-haiku-5-5' else 9000,
                            route='anthropic', structured=True, effort=effort,
                            pipeline=os.getenv('ANTHROPIC_ANSWER_PIPELINE', 'single_pass'))
    elif provider == 'openai':
        config = ChatConfig(provider, os.getenv('OPENAI_CHAT_MODEL', 'gpt-5.6-luna'),
                            'OpenAI', 'OPENAI_API_KEY', 'https://api.openai.com/v1')
    else:
        raise ValueError('RESEARCH_CHAT_PROVIDER must be openrouter, qwen, anthropic or openai')
    if (provider, config.model) not in PRICES:
        raise ValueError('This model needs a reviewed budget rate before it can be enabled')
    if config.pipeline not in ('single_pass', 'two_pass_v3'):
        raise ValueError('This answer pipeline needs a reviewed configuration')
    if config.pipeline == 'two_pass_v3' and (provider, config.model, config.effort, config.max_output_tokens) != (
            'anthropic', 'claude-haiku-5-5', 'low', 12000):
        raise ValueError('Two-pass answers require explicit Haiku low with 12000 output tokens')
    return config
