"""Authored fake-provider selectors, not a production quote-repair operation."""
from copy import deepcopy
import json


def select_claim(unit,payload):
    def selector(support):
        citation=support['citation_id']
        passage=next((p for p in payload['evidence'] if p['id']==citation),{})
        field=support['field']
        value=passage if field in ('text','warning') else payload['sources'].get(passage.get('source'),{})
        for key in field.split('.'):
            value=value.get(key) if isinstance(value,dict) else None
        quote=' '.join(support['quote'].split())
        candidates=value if isinstance(value,list) else []
        span=next((x[0] for x in candidates if isinstance(x,list) and len(x)==2 and isinstance(x[0],str)
                   and quote in ' '.join(x[1].split())),'unknown-span')
        return {'citation_id':citation,'span_id':span}
    result=deepcopy(unit)
    result['primary_support']=selector(unit['primary_support'])
    result['supports']=[selector(s) for s in unit['supports']]
    return result


def select_response(native,payload):
    result=deepcopy(native)
    paragraphs=([result['paragraph']] if result.get('paragraph') is not None else []) if 'paragraph' in result else result['paragraphs']
    for paragraph in paragraphs:
        if 'claims' in paragraph:
            paragraph['claims']=[{**select_claim(unit,payload),'plan_refs':deepcopy(unit.get('plan_refs',[]))} for unit in paragraph['claims']]
        else:
            selected=select_claim(paragraph,payload)
            paragraph.clear();paragraph.update(selected)
    if payload.get('plan_protocol')=='bounded_source_plan_v1' and 'evidence_plan' not in payload:
        # Authored mock provider fixture for the explicitly selected first phase.
        if result['status']=='insufficient_evidence':return empty_plan()
        return {'status':'planned','points':[{'need':'Requested source proposition '+str(i+1),'coverage':'supported','gaps':[]} for i in range(len(paragraphs))],
                'units':[{'point':i,'kind':'descriptive','primary_support':p['primary_support'],
                          'linked_supports':[{'role':'other','support':v} for v in p['supports']]} for i,p in enumerate(paragraphs)]}
    return slot_response(result)


def slot_response(result):
    """Author a new protocol fixture, never repair a provider response."""
    if 'paragraphs' not in result:return deepcopy(result)
    paragraphs=result['paragraphs']
    assert len(paragraphs)<=4
    return {'status':result['status'],**{f'paragraph_{i+1}':deepcopy(paragraphs[i]) if i<len(paragraphs) else None for i in range(4)}}


def payload_from_prepared(prepared):
    return json.loads(prepared.messages[-1]['content'])


def previous_workflow_prompt(phase, style):
    """Reverse only the reviewed workflow edits for historical byte checks."""
    import json
    from pathlib import Path
    from backend.span_instructions import RULES, PHASE_RULES, STYLE_RULES
    record = json.loads((Path(__file__).parents[2] / 'docs/research-required-coverage-parity.json').read_text())
    rules = {**previous_source_completeness_rules(), 'workflow': record['previous_workflow']}
    phase_rule = PHASE_RULES[phase]
    if phase == 'reconstruction':
        assert phase_rule.startswith(record['new_reconstruction_prefix'])
        phase_rule = record['previous_reconstruction_prefix'] + phase_rule.removeprefix(record['new_reconstruction_prefix'])
    return '\n'.join([rules['boundary'], phase_rule,
                      *[value for key, value in rules.items() if key != 'boundary'], STYLE_RULES[style]])


def previous_source_completeness_rules():
    """Restore v8 rules for historical byte checks; never used at runtime."""
    from pathlib import Path
    from backend.span_instructions import RULES
    record = json.loads((Path(__file__).parents[2] / 'docs/research-source-completeness-parity.json').read_text())
    rules = dict(RULES)
    for edit in record['edits']:
        key = edit['target'].split('.')[-1]
        assert rules[key] == edit['after']
        rules[key] = edit['before']
    return rules


def previous_source_completeness_prompt(phase, style):
    from backend.span_instructions import PHASE_RULES, STYLE_RULES
    rules = previous_source_completeness_rules()
    return '\n'.join([rules['boundary'], rules['workflow'], PHASE_RULES[phase],
                      *[v for k, v in rules.items() if k not in ('boundary', 'workflow')],
                      STYLE_RULES[style]])


def empty_plan():
    return {'status':'insufficient_evidence','points':[],'units':[]}


def historical_span_schema(schema, style, registry, *, phase, slots=True):
    """Frozen v9 grammar for historical byte audits, never production fallback."""
    from backend.anthropic_provider import native_answer_schema
    from backend.paragraph_slots import standard_slot_schema
    result=native_answer_schema(schema,style)
    key='paragraph' if style=='brief' else 'paragraphs'
    paragraph=result['properties'][key]['anyOf'][0] if style=='brief' else result['properties'][key]['items']
    unit=deepcopy(paragraph)
    unit['properties']={k:unit['properties'][k] for k in ('primary_support','supports','text')}
    for primary,support in ((True,unit['properties']['primary_support']),(False,unit['properties']['supports']['items'])):
        ids=[k for k,v in registry.items() if not primary or v['field']=='text']
        support['properties']={'citation_id':support['properties']['citation_id'],'span_id':{'type':'string','enum':ids}}
        support['required']=['citation_id','span_id']
    unit['required']=['primary_support','supports','text'];paragraph.clear()
    if phase=='draft':paragraph.update(unit)
    else:paragraph.update(type='object',additionalProperties=False,properties={'claims':{'type':'array','items':unit}},required=['claims'])
    return standard_slot_schema(result,style) if slots else result
