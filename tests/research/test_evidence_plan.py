"""Offline source-neutral plan/recovery/retention controls, never model accuracy."""
import asyncio
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from backend import answer_pipeline, span_draft
from backend.chat import ChatRequest, prepare_answer, AnswerCache
from backend.evidence_plan import (validate_plan_shape, validate_evidence_plan, validate_plan_refs,
                                  plan_answer_schema, PLAN_PROTOCOL, FINAL_INTERNAL_PROTOCOL)
from backend.paragraph_slots import strict_answer_json
from backend.span_instructions import span_answer_instructions
from backend.span_draft import prepare_span_draft, normalize_span_draft
from backend.reconstruction import prepare_reconstruction, normalize_reconstruction, pipeline_spec
from tests.research.span_fixtures import empty_plan, select_response
from tests.research.test_answer_pipeline import setup, model_response
from tests.research.test_reconstruction import claim, response


def prepared_plan(evidence=None):
    evidence=evidence or [{'id':'fixture-sheds','text':'Permitted sheds must retain a drainage plan.'}]
    request=ChatRequest(question='What is supported about the sheds?')
    original=prepare_answer(request,evidence,provider='anthropic')
    prepared=prepare_span_draft(request,original)
    span=next(k for k,v in prepared.span_registry.items() if v['field']=='text')
    plan={'status':'planned','points':[{'need':'Shed conditions','coverage':'partial','gaps':['subject']}],
          'units':[{'point':0,'kind':'normative','primary_support':{'citation_id':evidence[0]['id'],'span_id':span},'linked_supports':[]}]}
    return request,original,prepared,plan


@pytest.mark.parametrize('phase',['draft','reconstruction'])
@pytest.mark.parametrize('style',['standard','brief'])
def test_exact_reviewed_prompt_and_wire_schema_bytes(phase,style):
    fixture=json.loads((Path(__file__).parents[2]/'docs/research-evidence-plan-parity.json').read_text())
    key=('plan' if phase=='draft' else 'final')+'-'+style
    raw=span_answer_instructions(phase,style).encode();pin=fixture['prompts'][key]
    if phase=='reconstruction':
        current=json.loads((Path(__file__).parents[2]/'docs/research-claim-composition-parity.json').read_text())
        pin=current['prompts'][key]
    assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256']
    schema=plan_answer_schema(fixture['citation_ids'],fixture['registry'],phase=phase,style=style)
    assert schema==fixture['wire_schemas']['plan-wire' if phase=='draft' else 'final-'+style+'-wire']


def test_partial_condition_is_retained_despite_unknown_broader_subject():
    request,original,prepared,plan=prepared_plan()
    assert normalize_span_draft(json.dumps(plan),prepared)==plan
    assert plan['points'][0]['coverage']=='partial' and plan['points'][0]['gaps']==['subject']
    final=prepare_reconstruction(request,original,plan)
    unit=claim('For a permitted shed, its drainage plan must be retained.',quote=original.evidence[0]['text'],citation=original.evidence[0]['id'])
    unit['plan_refs']=[0]
    answer,_=normalize_reconstruction(response(unit,prepared=final),final)
    assert answer['status']=='answered'


@pytest.mark.parametrize('value',[True,False,0.0,'0',-1,1,None])
def test_point_ref_is_strict_integer_within_actual_point_count(value):
    *_,plan=prepared_plan();plan['units'][0]['point']=value
    with pytest.raises(ValueError):validate_plan_shape(plan)


@pytest.mark.parametrize('refs',[[True],[False],[0.0],['0'],[-1],[1],[0,0],None])
def test_final_refs_are_strict_bounded_and_unique(refs):
    *_,plan=prepared_plan();unit=plan['units'][0]
    c={'plan_refs':refs,'primary_support':unit['primary_support'],'supports':[],'text':'Fixture.'}
    with pytest.raises(ValueError):validate_plan_refs(c,plan)


def test_reordered_duplicate_link_rejected_but_same_span_under_distinct_roles_counts():
    *_,plan=prepared_plan();u=plan['units'][0];s=u['primary_support']
    u['linked_supports']=[{'role':'duty','support':deepcopy(s)}]
    assert validate_plan_shape(plan)==plan
    u['linked_supports'].append({'support':{'span_id':s['span_id'],'citation_id':s['citation_id']},'role':'duty'})
    with pytest.raises(ValueError):validate_plan_shape(plan)
    u['linked_supports'][1]['role']='condition'
    assert validate_plan_shape(plan)==plan


@pytest.mark.parametrize('label,valid',[('क'*32,True),('क'*33,False),('x'*96,True),('x'*97,False),('x\n',False),('x\x85',False),('   ',False)])
def test_need_limit_counts_utf8_bytes_without_repair(label,valid):
    *_,plan=prepared_plan();plan['points'][0]['need']=label;before=deepcopy(plan)
    if valid:assert validate_plan_shape(plan)==plan
    else:
        with pytest.raises(ValueError):validate_plan_shape(plan)
    assert plan==before


def test_exact_subset_is_claim_local_and_does_not_repair_missing_support():
    *_,plan=prepared_plan();s=plan['units'][0]['primary_support']
    extra={'citation_id':'b','span_id':'s2'}
    plan['units'][0]['linked_supports']=[{'role':'condition','support':extra}]
    claim={'plan_refs':[0],'primary_support':s,'supports':[],'text':'Fixture.'};before=deepcopy(claim);records=[]
    with pytest.raises(ValueError):validate_plan_refs(claim,plan,observer=records.append)
    assert claim==before and records[-1]['missing_selectors']==[['b','s2']]
    claim['supports']=[extra]
    assert not validate_plan_refs(claim,plan)['missing_selectors']


def test_empty_plan_has_no_valid_ref_but_direct_recovery_remains_valid():
    c={'plan_refs':[],'primary_support':{'citation_id':'a','span_id':'s1'},'supports':[],'text':'Fixture.'}
    assert validate_plan_refs(c,empty_plan())['plan_refs']==[]
    c['plan_refs']=[0]
    with pytest.raises(ValueError):validate_plan_refs(c,empty_plan())


def test_plan_identity_mutation_cannot_change_second_request():
    request,original,_,plan=prepared_plan();prepared=prepare_reconstruction(request,original,plan)
    prepared.compact_plan['points'][0]['need']='Changed'
    with pytest.raises(ValueError):normalize_reconstruction(response(claim(),prepared=prepared),prepared)


def test_final_schema_overflow_fails_before_first_reservation_or_client(setup,monkeypatch):
    _,_,_,transport,limits,_,run,_=setup;original=span_draft.span_schema
    def schema(*args,**kwargs):
        if kwargs['phase']=='reconstruction':raise ValueError('Final schema exceeds bound')
        return original(*args,**kwargs)
    monkeypatch.setattr(span_draft,'span_schema',schema)
    with pytest.raises(answer_pipeline.PipelineFailure):run()
    assert not limits.receipts and not transport.requests and not transport.closed


def test_empty_first_plan_recovers_full_evidence_and_only_publishes_final(setup):
    _,_,_,transport,limits,observed,run,_=setup;good=transport.handler
    async def handle(req,n):
        if n==1:return model_response(empty_plan())
        return await good(req,n)
    transport.handler=handle;result=run()
    assert len(limits.receipts)==2 and result.answer['status']=='answered'
    assert result.trace['phases'][0]['validated_plan']==empty_plan()
    assert result.trace['phases'][1]['plan_sha256']==result.trace['phases'][0]['validated_plan_sha256']
    assert 'plan_refs' not in json.dumps(result.answer) and 'points' not in result.answer
    assert all('final_answer' not in x for x in observed if x['status']!='completed')


def test_correct_selectors_do_not_prove_modal_fidelity():
    request,original,_,plan=prepared_plan();prepared=prepare_reconstruction(request,original,plan)
    wrong=claim('Permitted sheds may retain a drainage plan.',quote=original.evidence[0]['text'],citation=original.evidence[0]['id']);wrong['plan_refs']=[0]
    answer,_=normalize_reconstruction(response(wrong,prepared=prepared),prepared)
    assert answer['paragraphs'][0]['text']==wrong['text']
    # Explicit semantic-negative fixture: must became may. Mechanical acceptance
    # is not counted as a correct answer or a live model acceptance result.


@pytest.mark.parametrize('missing',['paragraph_protocol','answer_style','final_internal_protocol','plan_protocol'])
@pytest.mark.parametrize('value',[{'status':'insufficient_evidence','points':[],'units':[]},
                                 {'status':'insufficient_evidence','paragraphs':[]},{}])
def test_capture_new_protocol_requires_complete_trusted_context(missing,value):
    from backend.answer_trace import final_json_capture
    context={'phase':'draft','anchor_protocol':'lossless_source_spans_v2',
             'paragraph_protocol':'four_nullable_slots_v1','answer_style':'standard',
             'plan_protocol':PLAN_PROTOCOL,'final_internal_protocol':FINAL_INTERNAL_PROTOCOL}
    context.pop(missing)
    result=final_json_capture(model_response(value).json(),**context)
    assert result=={'capture_status':'unexpected_plan_protocol'}


def test_plan_count_ceilings_count_occurrences_not_unique_supports():
    *_,plan=prepared_plan();u=plan['units'][0]
    u['linked_supports']=[{'role':r,'support':deepcopy(u['primary_support'])} for r in ('condition','duty','scope')]
    plan['units']=[deepcopy(u) for _ in range(12)]
    assert validate_plan_shape(plan)==plan  # 12 units, 48 occurrences, one distinct selector.
    extra=deepcopy(plan);extra['units'][0]['linked_supports'].append({'role':'date','support':deepcopy(u['primary_support'])})
    with pytest.raises(ValueError):validate_plan_shape(extra)
    extra=deepcopy(plan);extra['units'].append(deepcopy(u))
    with pytest.raises(ValueError):validate_plan_shape(extra)
    ten=deepcopy(plan);ten['units']=[deepcopy(u)]
    ten['units'][0]['linked_supports']=[{'role':r,'support':deepcopy(u['primary_support'])} for r in
        ('condition','exception','duty','scope','quantity','date','context','publication','extraction')]
    assert validate_plan_shape(ten)==ten
    ten['units'][0]['linked_supports'].append({'role':'other','support':deepcopy(u['primary_support'])})
    with pytest.raises(ValueError):validate_plan_shape(ten)


def test_compact_8192_byte_boundary_is_separate_from_source_provenance():
    from backend.source_spans import encoded
    *_,plan=prepared_plan();selector=plan['units'][0]['primary_support']
    selector['citation_id']=''
    selector['citation_id']='x'*(8192-len(encoded(plan)))
    assert len(encoded(plan))==8192 and validate_plan_shape(plan)==plan
    # This deliberately invented long ID is only a structural byte control;
    # actual source ownership would reject it. It is never an accepted answer.
    selector['citation_id']+='x'
    with pytest.raises(ValueError):validate_plan_shape(plan)


def test_submitted_ref_order_is_preserved_without_sorting():
    *_,plan=prepared_plan();plan['units'].append(deepcopy(plan['units'][0]))
    c={'plan_refs':[1,0],'primary_support':plan['units'][0]['primary_support'],'supports':[],'text':'Fixture.'}
    assert validate_plan_refs(c,plan)['plan_refs']==[1,0]


def test_second_wire_cannot_replace_the_bound_plan_after_preparation(setup):
    from backend.async_anthropic import AsyncAnthropicClient
    config,request,prepared,transport,limits,*_=setup
    class MutatingClient(AsyncAnthropicClient):
        async def send(self,body,**kwargs):
            changed=deepcopy(body);payload=json.loads(changed['messages'][-1]['content'])
            if 'evidence_plan' in payload:
                payload['evidence_plan']['points'][0]['need']='Changed after binding'
                changed['messages'][-1]['content']=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
            return await super().send(changed,**kwargs)
    def factory():return MutatingClient('fixture-only',transport=transport)
    with pytest.raises(answer_pipeline.PipelineFailure,match='request_capture_mismatch'):
        asyncio.run(answer_pipeline.run_answer_pipeline(request,prepared,config,limits=limits,client_factory=factory))
    assert len(limits.receipts)==2 and len(transport.requests)==1 and transport.closed
