"""One request-owned async transport; cancellation closes active provider I/O."""
import inspect
import re
import httpx

from .anthropic_provider import ENDPOINT, API_VERSION, AnthropicAPIError, native_content


class AsyncAnthropicClient:
    def __init__(self, api_key, workspace_id=None, *, transport=None):
        headers = {'Authorization': 'Bearer ' + api_key, 'anthropic-version': API_VERSION}
        if workspace_id:
            headers['anthropic-workspace-id'] = workspace_id
        self._request_observer = None
        self._http = httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(30, connect=10, write=10, pool=10),
            follow_redirects=False, trust_env=False,
            transport=transport if transport is not None else httpx.AsyncHTTPTransport(retries=0),
            event_hooks={'request': [self._observe_request]})

    async def _observe_request(self, request):
        if self._request_observer is None:
            raise ValueError('Missing stage dispatch observer')
        result = self._request_observer(request)
        if inspect.isawaitable(result):
            await result

    async def send(self, body, *, on_request, on_response):
        if self._request_observer is not None:
            raise ValueError('Concurrent use of an owned provider transport')
        self._request_observer = on_request
        try:
            try:
                response = await self._http.post(ENDPOINT, json=body, follow_redirects=False)
            except httpx.HTTPError:
                raise AnthropicAPIError() from None
            metadata = {'provider_http_status': response.status_code}
            if response.status_code != 200:
                on_response(metadata)
                raise AnthropicAPIError(response.status_code)
            try:
                payload = response.json()
            except ValueError:
                on_response(metadata)
                raise ValueError('The answer service returned an invalid response') from None
            if isinstance(payload, dict):
                metadata.update(response_model_matches=payload.get('model') == body['model'],
                                response_model=payload.get('model') if payload.get('model') == body['model'] else 'unexpected_model')
                stop = payload.get('stop_reason')
                metadata['stop_reason'] = stop if stop in ('end_turn','refusal','max_tokens','model_context_window_exceeded','tool_use','pause_turn') else 'unexpected'
                usage = payload.get('usage', {})
                if isinstance(usage, dict):
                    metadata['reported_usage'] = {k:usage[k] for k in ('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')
                                                   if type(usage.get(k)) is int and usage[k] >= 0}
                    details = usage.get('output_tokens_details', {})
                    if isinstance(details, dict) and type(details.get('thinking_tokens')) is int and details['thinking_tokens'] >= 0:
                        metadata['reported_usage']['thinking_tokens'] = details['thinking_tokens']
                # Inspect final text only; never emit response reasoning. A
                # credential echo in otherwise valid JSON must not enter a
                # diagnostic capture or a public answer.
                blocks=payload.get('content',[])
                final=''.join(b.get('text','') for b in blocks if isinstance(b,dict)
                              and b.get('type')=='text' and isinstance(b.get('text'),str)) if isinstance(blocks,list) else ''
                secret=self._http.headers.get('authorization','').removeprefix('Bearer ')
                if ((secret and secret in final)
                        or re.search(r'\bsk-(?:ant|or|proj)-[A-Za-z0-9_-]+',final)
                        or re.search(r'"(?:authorization|x-api-key|api[_-]?key|access[_-]?token)"\s*:',final,re.I)):
                    on_response(metadata)
                    raise ValueError('The answer service returned unsafe final content')
                # Phase is carried by the local callback, not sent to the model.
                on_response(metadata, payload)
            else:
                on_response(metadata)
            return native_content(payload, body['model'])
        finally:
            self._request_observer = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._http.aclose()
