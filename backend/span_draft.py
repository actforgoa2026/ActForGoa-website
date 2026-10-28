"""Wire-only span draft transformation after the unchanged evidence selection."""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json

from .anthropic_provider import (MAX_SCHEMA_BYTES, MAX_SUPPORTS, native_answer_schema,
    native_answer_instructions, normalize_native_answer, _represented_contexts,
    _represented_publications)
from .chat import (ChatRequest, PreparedAnswer, GroundedAnswer, validate_answer,
                   MAX_PROMPT_BYTES, FRAMING_TOKEN_ALLOWANCE)
from .source_spans import (ANCHOR_PROTOCOL, annotate_payload, verify_annotated_payload,
                          original_baseline, registry_hash, resolve_selector, encoded)
from .span_instructions import span_answer_instructions

PIPELINE_VERSION = 'two_pass_v5'


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def span_schema(schema, style, registry, *, phase):
    result=native_answer_schema(schema,style)
    key='paragraph' if style=='brief' else 'paragraphs'
    paragraph=(result['properties'][key]['anyOf'][0] if style=='brief'
               else result['properties'][key]['items'])
    unit=deepcopy(paragraph)
    unit['properties']={key:unit['properties'][key] for key in ('primary_support','supports','text')}
    for primary,support in ((True,unit['properties']['primary_support']),
                            (False,unit['properties']['supports']['items'])):
        ids=[key for key,span in registry.items() if not primary or span['field']=='text']
        if not ids:raise ValueError('No selectable source text')
        support['properties']={'citation_id':support['properties']['citation_id'],
                               'span_id':{'type':'string','enum':ids}}
        support['required']=['citation_id','span_id']
    unit['required']=['primary_support','supports','text']
    paragraph.clear()
    if phase=='draft':paragraph.update(unit)
    elif phase=='reconstruction':
        paragraph.update(type='object',additionalProperties=False,
                         properties={'claims':{'type':'array','items':unit}},required=['claims'])
    else:raise ValueError('Unknown span phase')
    if len(encoded(result))>MAX_SCHEMA_BYTES:raise ValueError('Span schema exceeds its reserved allowance')
    return result


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
    wrapper={**annotated,'request_scope':scope,'anchor_protocol':ANCHOR_PROTOCOL}
    messages=[{'role':'system','content':span_answer_instructions('draft',original.answer_style)},
              *deepcopy(history),{'role':'user','content':encoded(wrapper).decode()}]
    size=len(encoded(messages))
    if size>MAX_PROMPT_BYTES:raise ValueError('Span draft exceeds its byte bound')
    schema=span_schema(original.schema,original.answer_style,registry,phase='draft')
    binding=digest({'version':PIPELINE_VERSION,'request':request.model_dump(),'baseline':baseline,
                    'original_messages':original.messages,'original_evidence':original.evidence,
                    'messages':messages,'schema':schema,'registry':registry})
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
    if (config.pipeline,config.provider,config.model,config.effort,config.max_output_tokens)!=(
            PIPELINE_VERSION,'anthropic','claude-haiku-5-5','medium',12000):
        raise ValueError('Span draft requires the reviewed configuration')
    validate_span_draft_identity(prepared)
    _represented_contexts(prepared.original);_represented_publications(prepared.original)
    config.maximum_cost_microusd(prepared.input_token_bound)
    return {'model':config.model,'max_tokens':config.max_output_tokens,
            'system':prepared.messages[0]['content'],'messages':prepared.messages[1:],
            'stream':False,'service_tier':'standard_only','thinking':{'type':'adaptive'},
            'output_config':{'effort':config.effort,'format':{'type':'json_schema','schema':prepared.schema}}}


def normalize_span_draft(content,prepared,*,resolved_observer=None):
    resolution={'anchor_protocol':ANCHOR_PROTOCOL,'phase':'draft',
                'kind':'deterministic_source_span_lookup','complete':False,'paragraphs':[]}
    def observe():
        if resolved_observer is not None:resolved_observer(deepcopy(resolution))
    validate_span_draft_identity(prepared)
    try:
        result=json.loads(content)
        key='paragraph' if prepared.answer_style=='brief' else 'paragraphs'
        if not isinstance(result,dict) or set(result)!={'status',key}:raise ValueError()
        if result['status']=='insufficient_evidence':
            if result[key]!=(None if key=='paragraph' else []):raise ValueError()
            units=[]
        elif result['status']=='answered':
            units=[result[key]] if key=='paragraph' else result[key]
            if not isinstance(units,list) or not 1<=len(units)<=(1 if key=='paragraph' else 4):raise ValueError()
        else:raise ValueError()
        payload=json.loads(prepared.baseline['payload_utf8'])
        native=[]
        for index,unit in enumerate(units):
            record={'paragraph_index':index,'status':'pending','resolved_supports':[]}
            resolution['paragraphs'].append(record);observe()
            if (not isinstance(unit,dict) or set(unit)!={'text','primary_support','supports'}
                    or not isinstance(unit['supports'],list) or not 0<=len(unit['supports'])<MAX_SUPPORTS):raise ValueError()
            supports=[]
            for support_index,selector in enumerate([unit['primary_support'],*unit['supports']]):
                supports.append(resolve_selector(selector,prepared.span_registry,payload,primary=support_index==0))
                record['resolved_supports']=deepcopy(supports);observe()
            native.append({'text':unit['text'],'primary_support':supports[0],'supports':supports[1:]})
            record['status']='resolved';observe()
        converted={'status':result['status'],key:(native[0] if native else None) if key=='paragraph' else native}
        normalized=normalize_native_answer(json.dumps(converted,ensure_ascii=False),prepared.original)
        answer=validate_answer(GroundedAnswer.model_validate_json(normalized,strict=True),
                               prepared.original.evidence,prepared.answer_style)
    except (ValueError,TypeError,KeyError,IndexError):
        if resolution['paragraphs']:resolution['paragraphs'][-1]['status']='failed'
        observe()
        raise ValueError('Draft source selectors did not match the evidence contract') from None
    resolution['complete']=True;observe()
    return answer
