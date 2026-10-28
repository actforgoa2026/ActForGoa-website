"""Trusted phase dispatch: no protocol inference from returned object keys."""
import json

from .evidence_plan import PLAN_PROTOCOL, FINAL_INTERNAL_PROTOCOL, validate_plan_shape
from .paragraph_slots import (PARAGRAPH_PROTOCOL, AnswerEnvelopeError, decode_envelope,
                              SLOT_NAMES)


def check_plan_context(*, plan_protocol, final_internal_protocol, paragraph_protocol, style, phase):
    if (plan_protocol!=PLAN_PROTOCOL or final_internal_protocol!=FINAL_INTERNAL_PROTOCOL
            or paragraph_protocol!=PARAGRAPH_PROTOCOL or style not in ('standard','brief')
            or phase not in ('draft','reconstruction')):
        raise AnswerEnvelopeError('unexpected_plan_protocol')


def decode_plan_response(value, *, plan_protocol, final_internal_protocol, paragraph_protocol, style, phase):
    check_plan_context(plan_protocol=plan_protocol,final_internal_protocol=final_internal_protocol,
                       paragraph_protocol=paragraph_protocol,style=style,phase=phase)
    if phase=='draft':return validate_plan_shape(value),None
    normalized,mapping=decode_envelope(value,protocol=paragraph_protocol,style=style,phase=phase)
    paragraphs=normalized['paragraphs'] if style=='standard' else ([] if normalized['paragraph'] is None else [normalized['paragraph']])
    for paragraph in paragraphs:
        if (type(paragraph) is not dict or set(paragraph)!={'claims'}
                or type(paragraph['claims']) is not list or not paragraph['claims']):
            raise AnswerEnvelopeError('invalid_planned_claims')
        for claim in paragraph['claims']:
            if (type(claim) is not dict or set(claim)!={'plan_refs','primary_support','supports','text'}
                    or type(claim['plan_refs']) is not list or len(claim['plan_refs'])>12
                    or any(type(i) is not int or not 0<=i<12 for i in claim['plan_refs'])
                    or len(set(claim['plan_refs']))!=len(claim['plan_refs'])):
                raise AnswerEnvelopeError('invalid_planned_claims')
    return normalized,mapping


def check_plan_request(body, *, plan_protocol, final_internal_protocol, paragraph_protocol, style, phase):
    check_plan_context(plan_protocol=plan_protocol,final_internal_protocol=final_internal_protocol,
                       paragraph_protocol=paragraph_protocol,style=style,phase=phase)
    try:
        schema=body['output_config']['format']['schema']
        request=json.loads(body['messages'][-1]['content'])
        keys={'question','sources','evidence','request_scope','anchor_protocol','plan_protocol'}
        if phase=='reconstruction':keys.add('evidence_plan')
        if (set(request)!=keys or request['plan_protocol']!=plan_protocol
                or request['request_scope']['answer_style']!=style):raise ValueError()
        if phase=='draft':
            expected={'status','points','units'}
            if set(schema['definitions']['unit']['properties'])!={'point','kind','primary_support','linked_supports'}:raise ValueError()
        else:
            expected={'status',*SLOT_NAMES} if style=='standard' else {'status','paragraph'}
            paragraph=schema['definitions']['paragraph']
            if (set(paragraph['properties'])!={'claims'}
                    or set(paragraph['properties']['claims']['items']['properties'])!={'plan_refs','primary_support','supports','text'}):raise ValueError()
            validate_plan_shape(request['evidence_plan'])
        if set(schema['properties'])!=expected or set(schema['required'])!=expected:raise ValueError()
    except (ValueError,TypeError,KeyError,IndexError):
        raise AnswerEnvelopeError('request_plan_protocol_mismatch') from None
