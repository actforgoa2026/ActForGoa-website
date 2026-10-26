"""Server-only model configuration and conservative, versioned inference prices."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
import os
import re
from urllib.parse import urlsplit
from openai import OpenAI

# USD per million tokens, standard uncached Singapore/International prices.
# Keep prompts below 32K tokens; changing models requires reviewing these rates.
# Verified 2026-10-26: https://openrouter.ai/qwen/qwen3.7-flash
# and https://www.alibabacloud.com/help/en/model-studio/model-pricing
# OpenRouter requests enforce these ceilings; credit-purchase fees are separate.
PRICES = {
    ('openrouter', 'qwen/qwen3.7-flash'): ('0.030', '0.130'),
    ('openrouter', 'qwen/qwen3.8-flash'): ('0.15', '0.47'),
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

    def maximum_cost_microusd(self, input_token_bound):
        input_rate, output_rate = map(Decimal, PRICES[(self.provider, self.model)])
        # USD/million tokens multiplied by token count is micro-USD. Round up.
        return int((input_token_bound * input_rate + self.max_output_tokens * output_rate)
                   .to_integral_value(rounding=ROUND_CEILING))

    def client(self):
        key = os.getenv(self.key_name)
        # No SDK retries: each budget reservation covers exactly one provider attempt.
        return OpenAI(api_key=key, base_url=self.base_url, timeout=60, max_retries=0) if key else None


def chat_config():
    provider = os.getenv('RESEARCH_CHAT_PROVIDER', 'openrouter')
    if provider == 'openrouter':
        config = ChatConfig(provider, os.getenv('OPENROUTER_CHAT_MODEL', 'qwen/qwen3.7-flash'),
                            'OpenRouter and Alibaba Cloud (Qwen)', 'OPENROUTER_API_KEY',
                            'https://openrouter.ai/api/v1')
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
    elif provider == 'openai':
        config = ChatConfig(provider, os.getenv('OPENAI_CHAT_MODEL', 'gpt-5.6-luna'),
                            'OpenAI', 'OPENAI_API_KEY', 'https://api.openai.com/v1')
    else:
        raise ValueError('RESEARCH_CHAT_PROVIDER must be openrouter, qwen or openai')
    if (provider, config.model) not in PRICES:
        raise ValueError('This model needs a reviewed budget rate before it can be enabled')
    return config
