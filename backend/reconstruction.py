"""Pure evidence-preserving reconstruction contract; no I/O or provider calls."""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json

from pydantic import ValidationError

from .anthropic_provider import (MAX_SUPPORTS, normalize_native_answer, validated_unit_supports,
    _represented_fields, _represented_contexts, _represented_publications)
from .chat import (ChatRequest, PreparedAnswer, Paragraph, GroundedAnswer, citation_text,
                   validate_answer, FRAMING_TOKEN_ALLOWANCE)
from .source_spans import (ANCHOR_PROTOCOL, annotate_payload, verify_annotated_payload,
                          resolve_selector, registry_hash, original_baseline)
from .span_draft import PIPELINE_VERSION, span_schema
from .span_instructions import ANSWER_WORKFLOW, span_answer_instructions
from .paragraph_slots import PARAGRAPH_PROTOCOL, strict_answer_json, decode_envelope, source_slot
from .phase_effort import phase_effort, phase_policy_metadata, validate_pipeline_config

CORRECTION_PROMPT_BYTES = 36000
COMPACT_DRAFT_BYTES = 8192
PROVIDER_DEADLINE_SECONDS = 65
PROVIDER_STAGE_SECONDS = 45
def pipeline_spec():
    """Detached export; neither callers nor nested maps can change policy."""
    return {'version': PIPELINE_VERSION, 'correction_prompt_bytes': CORRECTION_PROMPT_BYTES,
            'compact_draft_bytes': COMPACT_DRAFT_BYTES, 'provider_deadline_seconds': PROVIDER_DEADLINE_SECONDS,
            'provider_stage_seconds': PROVIDER_STAGE_SECONDS, 'capture_version': 8,
            'answer_workflow': ANSWER_WORKFLOW,
            'paragraph_protocol': PARAGRAPH_PROTOCOL, 'anchor_protocol': ANCHOR_PROTOCOL,
            **phase_policy_metadata()}


# Compatibility export for readers; execution always obtains a fresh spec.
PIPELINE_SPEC = pipeline_spec()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def reconstruction_schema(schema, style, registry):
    return span_schema(schema,style,registry,phase='reconstruction')


def reconstruction_instructions(base, style):
    if not base:raise ValueError('Missing original selection instructions')
    return span_answer_instructions('reconstruction',style)


@dataclass
class ReconstructionPrepared:
    original: PreparedAnswer
    request: dict
    compact_draft: dict
    messages: list[dict]
    schema: dict
    input_token_bound: int
    binding_sha256: str
    span_registry: dict
    span_registry_sha256: str
    source_payload_sha256: str
    annotated_payload_sha256: str

    @property
    def answer_style(self):
        return self.original.answer_style


def prepare_reconstruction(request, original, draft):
    if not isinstance(request, ChatRequest) or request.answer_style != original.answer_style:
        raise ValueError('Reconstruction request identity differs')
    # Do not forward full public citation records, raw model reasoning or notices.
    try:
        compact = {k: deepcopy(draft[k]) for k in ('status', 'paragraphs')}
        validated = GroundedAnswer.model_validate(compact, strict=True)
        validate_answer(validated, original.evidence, original.answer_style)
    except (ValueError, ValidationError, KeyError, TypeError):
        raise ValueError('Reconstruction draft did not match the public contract') from None
    if len(encoded(compact)) > COMPACT_DRAFT_BYTES:
        raise ValueError('Reconstruction draft exceeds its byte bound')
    if not original.base_instructions:
        raise ValueError('Missing native answer instructions')
    payload = json.loads(original.messages[-1]['content'])
    if payload.get('question') != request.question:
        raise ValueError('Reconstruction question differs from draft evidence')
    if set(payload) != {'question', 'sources', 'evidence'}:
        raise ValueError('Unexpected original evidence payload')
    scope = {'answer_style': request.answer_style, 'document_id': request.document_id,
             'generation': request.generation}
    if encoded(original.request_scope) != encoded(scope):
        raise ValueError('Reconstruction scope differs from prepared request')
    annotated,registry=annotate_payload(payload)
    restored,actual_registry=verify_annotated_payload(annotated,payload)
    if restored!=payload or actual_registry!=registry:raise ValueError('Source span preparation differs')
    correction_payload = {**annotated, 'request_scope': scope, 'draft_answer': compact,
                          'anchor_protocol':ANCHOR_PROTOCOL}
    history = deepcopy(original.messages[1:-1])
    messages = [{'role': 'system', 'content': reconstruction_instructions(original.base_instructions, original.answer_style)},
                *history, {'role': 'user', 'content': encoded(correction_payload).decode()}]
    size = len(encoded(messages))
    if size > CORRECTION_PROMPT_BYTES:
        raise ValueError('Reconstruction input exceeds its byte bound')
    schema = reconstruction_schema(original.schema, original.answer_style,registry)
    binding = digest({'version': PIPELINE_VERSION, 'request': request.model_dump(),
                      'draft_messages': original.messages, 'draft_evidence': original.evidence,
                      'correction_messages': messages, 'schema': schema,'span_registry':registry})
    return ReconstructionPrepared(original, request.model_dump(), compact, messages, schema,
                                  size + FRAMING_TOKEN_ALLOWANCE, binding,registry,registry_hash(registry),
                                  digest(payload),digest(annotated))


def validate_prepared_identity(prepared):
    expected = prepare_reconstruction(ChatRequest(**prepared.request), prepared.original, prepared.compact_draft)
    for key in ('messages','schema','binding_sha256','input_token_bound','span_registry',
                'span_registry_sha256','source_payload_sha256','annotated_payload_sha256'):
        if encoded(getattr(prepared,key))!=encoded(getattr(expected,key)):
            raise ValueError('Reconstruction prepared input identity changed')


def reconstruction_message_request(config, prepared):
    validate_pipeline_config(config)
    validate_prepared_identity(prepared)
    _represented_contexts(prepared.original)
    _represented_publications(prepared.original)
    config.maximum_cost_microusd(prepared.input_token_bound)
    return {'model': config.model, 'max_tokens': config.max_output_tokens,
            'system': prepared.messages[0]['content'], 'messages': prepared.messages[1:],
            'stream': False, 'service_tier': 'standard_only', 'thinking': {'type': 'adaptive'},
            'output_config': {'effort': phase_effort('reconstruction'),
                'format': {'type': 'json_schema', 'schema': prepared.schema}}}


def reconstruction_cache_identity(original, version):
    if version != PIPELINE_VERSION:
        raise ValueError('Unknown reconstruction pipeline version')
    annotated,registry=annotate_payload(json.loads(original.messages[-1]['content']))
    return {'spec': pipeline_spec(), 'request_scope': deepcopy(original.request_scope),
            'correction_instructions': reconstruction_instructions(original.base_instructions, original.answer_style),
            'draft_schema': span_schema(original.schema,original.answer_style,registry,phase='draft'),
            'draft_instructions':span_answer_instructions('draft',original.answer_style),
            'prepared_original':original_baseline(original.messages[-1]['content'],original.messages[1:-1],original.request_scope),
            'correction_schema': reconstruction_schema(original.schema, original.answer_style,registry),
            'span_registry_sha256':registry_hash(registry),
            'annotated_payload_sha256':digest(annotated),
            'correction_prompt_limit': CORRECTION_PROMPT_BYTES, 'draft_byte_limit': COMPACT_DRAFT_BYTES}


def normalize_reconstruction(content, prepared, *, resolved_observer=None):
    """Validate claim-local anchors, then apply unchanged paragraph/public guards.

    Joining is lossless. Neither a quote match nor a claim object establishes
    semantic correctness; independent review is still required.
    """
    original = prepared.original
    resolution={'anchor_protocol':ANCHOR_PROTOCOL,'kind':'deterministic_source_span_lookup','complete':False,'claims':[]}
    def observe_resolution():
        if resolved_observer is not None:resolved_observer(deepcopy(resolution))
    try:
        validate_prepared_identity(prepared)
        original_payload=json.loads(original.messages[-1]['content'])
        correction_payload=json.loads(prepared.messages[-1]['content'])
        restored,registry=verify_annotated_payload(
            {k:correction_payload[k] for k in ('question','sources','evidence')},original_payload)
        if (correction_payload.get('anchor_protocol')!=ANCHOR_PROTOCOL or registry!=prepared.span_registry
                or registry_hash(registry)!=prepared.span_registry_sha256
                or digest(restored)!=prepared.source_payload_sha256):raise ValueError()
        payload,mapping = decode_envelope(strict_answer_json(content),protocol=PARAGRAPH_PROTOCOL,
                                          style=original.answer_style,phase='reconstruction')
        if mapping is not None:resolution['slot_mapping']=mapping
        key = 'paragraph' if original.answer_style == 'brief' else 'paragraphs'
        if not isinstance(payload, dict) or set(payload) != {'status', key}:
            raise ValueError()
        if payload['status'] == 'insufficient_evidence':
            if payload[key] != (None if key == 'paragraph' else []):
                raise ValueError()
            normalized = normalize_native_answer(json.dumps(payload,ensure_ascii=False), original)
            resolution['complete']=True;observe_resolution()
            return validate_answer(GroundedAnswer.model_validate_json(normalized, strict=True),
                                   original.evidence, original.answer_style), []
        if payload['status'] != 'answered':
            raise ValueError()
        paragraphs = [payload[key]] if key == 'paragraph' else payload[key]
        if not isinstance(paragraphs, list) or not 1 <= len(paragraphs) <= (1 if key == 'paragraph' else 4):
            raise ValueError()
        fields, contexts, publications = (_represented_fields(original), _represented_contexts(original),
                                           _represented_publications(original))
        assembled, offsets = [], []
        for pi, paragraph in enumerate(paragraphs):
            if (not isinstance(paragraph, dict) or set(paragraph) != {'claims'}
                    or not isinstance(paragraph['claims'], list) or not paragraph['claims']):
                raise ValueError()
            texts, supports, seen = [], [], set()
            offset = 0
            for ci, selected_unit in enumerate(paragraph['claims']):
                resolved_record={'paragraph_index':pi,'slot_name':source_slot(original.answer_style,pi),'claim_index':ci,'status':'pending','resolved_supports':[]}
                resolution['claims'].append(resolved_record)
                if (not isinstance(selected_unit,dict) or set(selected_unit)!={'text','primary_support','supports'}
                        or not isinstance(selected_unit['supports'],list)
                        or len(selected_unit['supports'])>=MAX_SUPPORTS):raise ValueError()
                for si,selector in enumerate([selected_unit['primary_support'],*selected_unit['supports']]):
                    support=resolve_selector(selector,registry,restored,primary=si==0)
                    resolved_record['resolved_supports'].append(support)
                resolved_record['status']='resolved';observe_resolution()
                unit={'text':selected_unit['text'],'primary_support':resolved_record['resolved_supports'][0],
                      'supports':resolved_record['resolved_supports'][1:]}
                citations, _ = validated_unit_supports(unit, fields, contexts, publications)
                claim = Paragraph.model_validate({'text': unit['text'], 'citations': citations}, strict=True)
                if citation_text(claim.text, fields) != claim.text:
                    raise ValueError()
                offsets.append({'paragraph_index': pi, 'slot_name':source_slot(original.answer_style,pi), 'claim_index': ci, 'start': offset,
                                'end': offset + len(claim.text), 'text_sha256': hashlib.sha256(claim.text.encode()).hexdigest(),
                                'citation_ids': citations,
                                'span_ids':list(dict.fromkeys(s['span_id'] for s in [selected_unit['primary_support'],*selected_unit['supports']]))})
                texts.append(claim.text)
                offset += len(claim.text) + 1
                for support in [unit['primary_support'], *unit['supports']]:
                    identity = (support['citation_id'], support['field'], support['quote'])
                    if identity not in seen:
                        seen.add(identity)
                        supports.append(deepcopy(support))
            if len(supports) > MAX_SUPPORTS:
                raise ValueError()
            assembled.append({'text': ' '.join(texts), 'primary_support': supports[0], 'supports': supports[1:]})
        native = {'status': 'answered', key: assembled[0] if key == 'paragraph' else assembled}
        normalized = normalize_native_answer(json.dumps(native, ensure_ascii=False), original)
        answer = validate_answer(GroundedAnswer.model_validate_json(normalized, strict=True),
                                 original.evidence, original.answer_style)
        for mapping in offsets:
            text = answer['paragraphs'][mapping['paragraph_index']]['text'][mapping['start']:mapping['end']]
            if hashlib.sha256(text.encode()).hexdigest() != mapping['text_sha256']:
                raise ValueError()
        resolution['complete']=True;observe_resolution()
        return answer, offsets
    except (ValueError, ValidationError, KeyError, TypeError, IndexError):
        resolution.update(complete=False,failure_code='reconstruction_contract_failure')
        if resolution['claims'] and resolution['claims'][-1]['status']=='pending':
            resolution['claims'][-1]['status']='failed'
        observe_resolution()
        raise ValueError('Reconstruction did not match the evidence contract') from None
