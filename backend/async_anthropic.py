"""One request-owned async transport; cancellation closes active provider I/O."""
import inspect
import json
import httpx

from .anthropic_provider import ENDPOINT, API_VERSION, AnthropicAPIError, native_content
from .reconstruction import PROVIDER_STAGE_SECONDS
from .paragraph_slots import (strict_answer_json, decode_envelope, check_request_context,
                              AnswerEnvelopeError)


class AsyncAnthropicClient:
    def __init__(self, api_key, workspace_id=None, *, transport=None):
        headers = {'Authorization': 'Bearer ' + api_key, 'anthropic-version': API_VERSION}
        if workspace_id:
            headers['anthropic-workspace-id'] = workspace_id
        self._request_observer = None
        self._http = httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(PROVIDER_STAGE_SECONDS, connect=10, write=10, pool=10),
            follow_redirects=False, trust_env=False,
            transport=transport if transport is not None else httpx.AsyncHTTPTransport(retries=0),
            event_hooks={'request': [self._observe_request]})

    async def _observe_request(self, request):
        if self._request_observer is None:
            raise ValueError('Missing stage dispatch observer')
        result = self._request_observer(request)
        if inspect.isawaitable(result):
            await result

    def capture_prepared_original(self, original_body, baseline):
        """Local synthetic safety checks, never dispatch or invoke request hooks.

        Scan original unfragmented text with this client's real credentials and
        also scan the exact baseline including history/scope. Only approved
        decoded baseline data is returned; headers never leave the transport.
        """
        from .answer_trace import outgoing_request_capture
        from copy import deepcopy
        original_request=self._http.build_request('POST',ENDPOINT,json=original_body)
        capture,decoded=outgoing_request_capture(original_request)
        if decoded is None:
            return {'capture_status':'withheld_unsafe_prepared_original'},None
        synthetic=deepcopy(original_body)
        synthetic['messages']=[{'role':'user','content':json.dumps(baseline,ensure_ascii=False,separators=(',',':'))}]
        baseline_request=self._http.build_request('POST',ENDPOINT,json=synthetic)
        baseline_capture,baseline_body=outgoing_request_capture(baseline_request)
        if baseline_body is None:
            return {'capture_status':'withheld_unsafe_prepared_original'},None
        return {'capture_status':'safe_prepared_original',
                'check':'provider_owned_synthetic_request_no_dispatch',
                'synthetic_original_body_sha256':capture['body_sha256'],
                'synthetic_baseline_body_sha256':baseline_capture['body_sha256']},json.loads(baseline_body['messages'][-1]['content'])

    async def send(self, body, *, on_request, on_response, paragraph_protocol,
                   answer_style, phase):
        if self._request_observer is not None:
            raise ValueError('Concurrent use of an owned provider transport')
        check_request_context(body, protocol=paragraph_protocol, style=answer_style, phase=phase)
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
                from .answer_trace import credential_like_content
                secrets=[self._http.headers.get('authorization','').removeprefix('Bearer '),
                         self._http.headers.get('x-api-key'),self._http.headers.get('anthropic-workspace-id')]
                try:
                    decoded = strict_answer_json(final)
                    decode_envelope(decoded, protocol=paragraph_protocol, style=answer_style, phase=phase)
                    decoded_final = json.dumps(decoded, ensure_ascii=False)
                except AnswerEnvelopeError as error:
                    # The final text must never reach a payload-bearing
                    # callback after ambiguity, syntax or envelope failure.
                    metadata['response_validation_failure'] = error.code
                    on_response(metadata)
                    raise ValueError('The answer service returned invalid final JSON') from None
                if credential_like_content(decoded_final,secrets):
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
