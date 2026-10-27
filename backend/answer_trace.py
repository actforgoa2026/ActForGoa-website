"""Safe exact-request and final-output capture shared by both execution modes."""
import hashlib
import json
import re

import httpx
from .anthropic_provider import reviewed_effort
from .providers import PRICES


def final_json_capture(payload, *, phase='draft'):
    """Keep only bounded final answer JSON, never thinking or response metadata.

    Invalid JSON and unexpected fields are represented by fixed categories.
    The output is diagnostic, not accepted or served answer content.
    """
    blocks = payload.get('content')
    if not isinstance(blocks, list):return {'capture_status': 'missing_text'}
    texts = [b['text'] for b in blocks if isinstance(b, dict) and b.get('type') == 'text' and isinstance(b.get('text'), str)]
    text = ''.join(texts)
    if not text:return {'capture_status': 'missing_text'}
    if len(text.encode()) > 65536:return {'capture_status': 'oversize_text'}
    try:answer=json.loads(text)
    except ValueError:return {'capture_status': 'invalid_json'}
    if not isinstance(answer,dict) or answer.get('status') not in ('answered','insufficient_evidence'):
        return {'capture_status':'unexpected_shape'}
    if set(answer) == {'status','paragraph'}:
        paragraphs=[] if answer['paragraph'] is None else [answer['paragraph']]
        representation='native_brief'
    elif set(answer) == {'status','paragraphs'} and isinstance(answer['paragraphs'],list) and len(answer['paragraphs'])<=16:
        paragraphs=answer['paragraphs'];representation='paragraph_array'
    else:return {'capture_status':'unexpected_shape'}
    captured_paragraphs = paragraphs
    if phase == 'reconstruction':
        if any(not isinstance(p, dict) or set(p) != {'claims'} or not isinstance(p['claims'], list)
               for p in paragraphs):
            return {'capture_status': 'unexpected_shape'}
        paragraphs = [unit for p in paragraphs for unit in p['claims']]
        representation = 'reconstruction_' + representation
    elif phase != 'draft':
        return {'capture_status': 'unexpected_phase'}
    for p in paragraphs:
        if (not isinstance(p,dict) or not isinstance(p.get('text'),str) or len(p['text']) > 12000):
            return {'capture_status':'unexpected_shape'}
        if set(p) == {'text','citations'}:
            if (not isinstance(p['citations'],list) or len(p['citations']) > 20
                    or any(not isinstance(c,str) or len(c)>160 for c in p['citations'])):
                return {'capture_status':'unexpected_shape'}
        elif set(p) in ({'text','supports'}, {'text','primary_support','supports'}):
            if not isinstance(p['supports'],list) or len(p['supports']) > 20:
                return {'capture_status':'unexpected_shape'}
            supports=p['supports']
            if 'primary_support' in p:supports=[p['primary_support'],*supports]
            for support in supports:
                if (not isinstance(support,dict) or set(support) != {'citation_id','field','quote'}
                        or any(not isinstance(support[k],str) or len(support[k]) > bound
                               for k,bound in [('citation_id',160),('field',160),('quote',1200)])):
                    return {'capture_status':'unexpected_shape'}
        else:return {'capture_status':'unexpected_shape'}
    word_counts = ([sum(len(u['text'].split()) for u in p['claims']) for p in captured_paragraphs]
                   if phase == 'reconstruction' else [len(p['text'].split()) for p in paragraphs])
    return {'capture_status':'captured_unvalidated_json','representation':representation,'answer':answer,
            'paragraph_count':len(captured_paragraphs),'word_counts':word_counts}


def outgoing_request_capture(request):
    """Capture exact safe request bytes, never headers or generated thinking.

    This is diagnostic instrumentation, not a request builder. Unknown shapes
    fail closed without storing their body or forwarding a modified request.
    """
    try:
        raw = request.content
    except httpx.RequestNotRead:
        return {'capture_status': 'body_unavailable'}, None
    if len(raw) > 131072:
        return {'capture_status': 'oversize_body'}, None
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:raise ValueError('Duplicate field')
            result[key] = value
        return result
    try:
        text = raw.decode('utf-8')
        body = json.loads(text, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, ValueError):
        return {'capture_status': 'invalid_json_body'}, None
    expected = {'model', 'max_tokens', 'system', 'messages', 'stream',
                'service_tier', 'thinking', 'output_config'}
    if not isinstance(body, dict) or set(body) != expected:
        return {'capture_status': 'unexpected_request_shape'}, None
    output = body['output_config']
    messages = body['messages']
    if (not isinstance(body['system'], str) or not isinstance(body['model'], str)
            or ('anthropic', body['model']) not in PRICES
            or type(body['max_tokens']) is not int or body['max_tokens'] <= 0
            or body['stream'] is not False or body['service_tier'] != 'standard_only'
            or body['thinking'] != {'type': 'adaptive'}
            or not isinstance(output, dict) or set(output) != {'effort', 'format'}
            or not isinstance(output['format'], dict) or set(output['format']) != {'type', 'schema'}
            or output['format']['type'] != 'json_schema' or not isinstance(output['format']['schema'], dict)
            or not isinstance(messages, list) or not messages
            or any(not isinstance(m, dict) or set(m) != {'role', 'content'}
                   or m['role'] not in ('user', 'assistant') or not isinstance(m['content'], str)
                   for m in messages)):
        return {'capture_status': 'unexpected_request_shape'}, None
    try:
        reviewed_effort(body['model'], output['effort'])
    except ValueError:
        return {'capture_status': 'unexpected_request_shape'}, None
    # Header values are used only to refuse accidental credential echoes. They
    # are never persisted. Also refuse common key prefixes and credential fields.
    secrets = [request.headers.get('x-api-key'),
               request.headers.get('authorization', '').removeprefix('Bearer ')]
    def strings(value):
        if isinstance(value, str):yield value
        elif isinstance(value, list):
            for item in value:yield from strings(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                yield key
                yield from strings(item)
    decoded = '\n'.join(strings(body))
    credential_field = re.compile(r'"(?:authorization|x-api-key|api[_-]?key|access[_-]?token)"\s*:', re.I)
    if (any(secret and secret in decoded for secret in secrets)
            or re.search(r'\bsk-(?:ant|or|proj)-[A-Za-z0-9_-]+', decoded)
            or credential_field.search(decoded)
            or credential_field.search(text.replace('\\"', '"'))):
        return {'capture_status': 'credential_like_content'}, None
    return {'capture_status': 'captured_request', 'body_utf8': text,
            'body_sha256': hashlib.sha256(raw).hexdigest(), 'body_bytes': len(raw)}, body

