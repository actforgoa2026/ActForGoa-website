"""Wire-only source plan after the unchanged evidence selection."""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json

from .anthropic_provider import (native_answer_instructions, _represented_contexts,
                                 _represented_publications)
from .chat import (ChatRequest, PreparedAnswer,
                   MAX_PROMPT_BYTES, FRAMING_TOKEN_ALLOWANCE)
from .source_spans import (ANCHOR_PROTOCOL, annotate_payload, verify_annotated_payload,
                          original_baseline, registry_hash, encoded)
from .span_instructions import span_answer_instructions
from .paragraph_slots import PARAGRAPH_PROTOCOL, strict_answer_json
from .phase_effort import PIPELINE_VERSION, phase_effort, validate_pipeline_config
from .evidence_plan import PLAN_PROTOCOL, FINAL_INTERNAL_PROTOCOL, validate_evidence_plan
from .plan_protocol import decode_plan_response


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def span_schema(schema, style, registry, *, phase):
    # IDs are from the unchanged native preparation, never selected by the plan.
    from .evidence_plan import plan_answer_schema
    ids=schema['properties']['paragraphs']['items']['properties']['citations']['items']['enum']
    return plan_answer_schema(ids,registry,phase=phase,style=style)


@dataclass
class SpanDraftPrepared:
    original: PreparedAnswer
    request: dict
    baseline: dict
    messages: list[dict]
    schema: dict
    input_token_bound: int
    binding_sha256: str
    span_registry: dict
    span_registry_sha256: str
    annotated_payload_sha256: str

    @property
    def answer_style(self):return self.original.answer_style


def prepare_span_draft(request, original):
    if not isinstance(request,ChatRequest) or request.answer_style!=original.answer_style:
        raise ValueError('Span draft request identity differs')
    scope={key:getattr(request,key) for key in ('answer_style','document_id','generation')}
    if encoded(scope)!=encoded(original.request_scope):raise ValueError('Span draft scope differs')
    if (not original.base_instructions or original.messages[0]!=
            {'role':'system','content':native_answer_instructions(original.base_instructions,original.answer_style)}):
        raise ValueError('Legacy selection instructions differ')
    history=original.messages[1:-1]
    request_history=[item.model_dump() for item in request.history]
    if history and encoded(history)!=encoded(request_history[-len(history):]):
        raise ValueError('Retained history differs from request')
    baseline=original_baseline(original.messages[-1]['content'],history,scope)
    payload=json.loads(baseline['payload_utf8'])
    if payload['question']!=request.question:raise ValueError('Span draft question differs')
    annotated,registry=annotate_payload(payload)
    verify_annotated_payload(annotated,payload)
    wrapper={**annotated,'request_scope':scope,'anchor_protocol':ANCHOR_PROTOCOL,'plan_protocol':PLAN_PROTOCOL}
    messages=[{'role':'system','content':span_answer_instructions('draft',original.answer_style)},
              *deepcopy(history),{'role':'user','content':encoded(wrapper).decode()}]
    size=len(encoded(messages))
    if size>MAX_PROMPT_BYTES:raise ValueError('Span draft exceeds its byte bound')
    schema=span_schema(original.schema,original.answer_style,registry,phase='draft')
    final_schema=span_schema(original.schema,original.answer_style,registry,phase='reconstruction')
    binding=digest({'version':PIPELINE_VERSION,'request':request.model_dump(),'baseline':baseline,
                    'original_messages':original.messages,'original_evidence':original.evidence,
                    'messages':messages,'schema':schema,'registry':registry,
                    'plan_protocol':PLAN_PROTOCOL,'final_internal_protocol':FINAL_INTERNAL_PROTOCOL,
                    'final_schema':final_schema,'final_instructions':span_answer_instructions('reconstruction',original.answer_style)})
    return SpanDraftPrepared(original,request.model_dump(),baseline,messages,schema,
                             size+FRAMING_TOKEN_ALLOWANCE,binding,registry,
                             registry_hash(registry),digest(annotated))


def validate_span_draft_identity(prepared):
    expected=prepare_span_draft(ChatRequest(**prepared.request),prepared.original)
    for key in ('baseline','messages','schema','input_token_bound','binding_sha256',
                'span_registry','span_registry_sha256','annotated_payload_sha256'):
        if encoded(getattr(prepared,key))!=encoded(getattr(expected,key)):
            raise ValueError('Span draft prepared identity differs')


def span_draft_message_request(config,prepared):
    validate_pipeline_config(config)
    validate_span_draft_identity(prepared)
    _represented_contexts(prepared.original);_represented_publications(prepared.original)
    config.maximum_cost_microusd(prepared.input_token_bound)
    return {'model':config.model,'max_tokens':config.max_output_tokens,
            'system':prepared.messages[0]['content'],'messages':prepared.messages[1:],
            'stream':False,'service_tier':'standard_only','thinking':{'type':'adaptive'},
            'output_config':{'effort':phase_effort('draft'),'format':{'type':'json_schema','schema':prepared.schema}}}


def normalize_span_draft(content,prepared,*,resolved_observer=None):
    """The first phase returns a validated plan, never a public answer."""
    validate_span_draft_identity(prepared)
    plan,_=decode_plan_response(strict_answer_json(content),plan_protocol=PLAN_PROTOCOL,
        final_internal_protocol=FINAL_INTERNAL_PROTOCOL,paragraph_protocol=PARAGRAPH_PROTOCOL,
        style=prepared.answer_style,phase='draft')
    return validate_evidence_plan(plan,prepared.original,prepared.span_registry,observer=resolved_observer)
