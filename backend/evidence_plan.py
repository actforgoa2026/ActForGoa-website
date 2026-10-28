"""Bounded source-selection plan, never a prose answer or entailment validator."""
from copy import deepcopy
import hashlib
import json

from .source_spans import encoded, resolve_selector
from .anthropic_provider import (_represented_fields, _represented_contexts,
    _represented_publications, MAX_SCHEMA_BYTES, MAX_QUOTE_CHARS)
from .paragraph_slots import AnswerEnvelopeError

PLAN_PROTOCOL = 'bounded_source_plan_v1'
FINAL_INTERNAL_PROTOCOL = 'planned_claim_supports_v1'
COMPACT_PLAN_BYTES = 8192
ROLES = ('condition','exception','duty','scope','quantity','date','context','publication','extraction','other')
GAPS = ('support','subject','predicate','antecedent','procedure','reference','scope','date','quantity','currentness','source_access')


def _object(properties):
    return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}


def _ref(name):
    return {'$ref':'#/definitions/'+name}


def plan_answer_schema(citation_ids, registry, *, phase, style):
    """Exact reviewed wire grammar; cross-field/byte/provenance limits are local."""
    if phase not in ('draft','reconstruction') or style not in ('standard','brief'):
        raise ValueError('Unknown plan answer shape')
    text_ids=[key for key,span in registry.items() if span['field']=='text']
    if not citation_ids or not text_ids:raise ValueError('No selectable source text')
    defs={
        'citation':{'type':'string','enum':list(citation_ids)},
        'selector':_object({'citation_id':_ref('citation'),'span_id':{'type':'string','enum':list(registry)}}),
        'primary':_object({'citation_id':_ref('citation'),'span_id':{'type':'string','enum':text_ids}}),
    }
    if phase=='draft':
        point=_object({'need':{'type':'string','description':'1 to 96 UTF-8 bytes; no control characters.'},
            'coverage':{'type':'string','enum':['supported','partial','missing']},
            'gaps':{'type':'array','items':{'type':'string','enum':list(GAPS)},'description':'At most 4 distinct codes.'}})
        link=_object({'role':{'type':'string','enum':list(ROLES)},'support':_ref('selector')})
        unit=_object({'point':{'type':'integer','enum':list(range(8))},
            'kind':{'type':'string','enum':['descriptive','normative']},'primary_support':_ref('primary'),
            'linked_supports':{'type':'array','items':_ref('link'),'description':'At most 9 links; 48 total selector occurrences across plan.'}})
        result=_object({'status':{'type':'string','enum':['planned','insufficient_evidence']},
            'points':{'type':'array','items':_ref('point'),'description':'At most 8 points; planned requires at least one.'},
            'units':{'type':'array','items':_ref('unit'),'description':'At most 12 units. Compact entire plan at most8192 UTF-8 bytes.'}})
        result['definitions']={**defs,'point':point,'link':link,'unit':unit}
    else:
        claim=_object({'plan_refs':{'type':'array','items':{'type':'integer','enum':list(range(12))},
            'description':'Distinct valid unit indices; empty allowed for direct recovery.'},
            'primary_support':_ref('primary'),'supports':{'type':'array','items':_ref('selector')},'text':{'type':'string'}})
        paragraph=_object({'claims':{'type':'array','minItems':1,'items':claim}})
        props={'status':{'type':'string','enum':['answered','insufficient_evidence']}}
        names=[f'paragraph_{i}' for i in range(1,5)] if style=='standard' else ['paragraph']
        props.update({name:{'anyOf':[_ref('paragraph'),{'type':'null'}]} for name in names})
        result=_object(props);result['definitions']={**defs,'paragraph':paragraph}
    if len(encoded(result))>MAX_SCHEMA_BYTES:raise ValueError('Plan schema exceeds its reserved allowance')
    return result


def selector_identity(selector):
    if (type(selector) is not dict or set(selector)!={'citation_id','span_id'}
            or any(type(selector[k]) is not str or not selector[k] for k in ('citation_id','span_id'))):
        raise ValueError('Invalid plan selector')
    return selector['citation_id'],selector['span_id']


def unit_selectors(unit):
    return [unit['primary_support'],*[link['support'] for link in unit['linked_supports']]]


def validate_plan_shape(value):
    """Strict structural normal form only. No labels are treated as source facts."""
    try:
        if (type(value) is not dict or set(value)!={'status','points','units'}
                or value['status'] not in ('planned','insufficient_evidence')
                or type(value['points']) is not list or len(value['points'])>8
                or type(value['units']) is not list or len(value['units'])>12):raise ValueError()
        if (value['status']=='planned') != bool(value['units']):raise ValueError()
        used=[0]*len(value['points']);count=0
        for point in value['points']:
            if (type(point) is not dict or set(point)!={'need','coverage','gaps'}
                    or type(point['need']) is not str or not point['need'].strip()
                    or not 1<=len(point['need'].encode())<=96
                    or any(ord(c)<32 or 127<=ord(c)<=159 for c in point['need'])
                    or point['coverage'] not in ('supported','partial','missing')
                    or type(point['gaps']) is not list or len(point['gaps'])>4
                    or any(type(g) is not str or g not in GAPS for g in point['gaps'])
                    or len(set(point['gaps']))!=len(point['gaps'])):raise ValueError()
        for unit in value['units']:
            if (type(unit) is not dict or set(unit)!={'point','kind','primary_support','linked_supports'}
                    or type(unit['point']) is not int or not 0<=unit['point']<len(used)
                    or unit['kind'] not in ('descriptive','normative')
                    or type(unit['linked_supports']) is not list or len(unit['linked_supports'])>9):raise ValueError()
            used[unit['point']]+=1;selector_identity(unit['primary_support']);links=set()
            for link in unit['linked_supports']:
                if (type(link) is not dict or set(link)!={'role','support'}
                        or type(link['role']) is not str or link['role'] not in ROLES):raise ValueError()
                identity=(link['role'],*selector_identity(link['support']))
                if identity in links:raise ValueError()
                links.add(identity)
            count+=1+len(unit['linked_supports'])
        if count>48:raise ValueError()
        for point,n in zip(value['points'],used):
            if (point['coverage']=='supported' and (not n or point['gaps'])
                    or point['coverage']=='partial' and (not n or not point['gaps'])
                    or point['coverage']=='missing' and (n or not point['gaps'])):raise ValueError()
        if len(encoded(value))>COMPACT_PLAN_BYTES:raise ValueError()
    except (ValueError,TypeError,KeyError,UnicodeError):
        raise AnswerEnvelopeError('invalid_evidence_plan') from None
    return deepcopy(value)


def validate_evidence_plan(value, original, registry, *, observer=None):
    """Plan equivalents of source guards; deliberately no fabricated prose check."""
    plan=validate_plan_shape(value)
    payload=json.loads(original.messages[-1]['content'])
    fields=_represented_fields(original);contexts=_represented_contexts(original)
    publications=_represented_publications(original)
    records=[]
    try:
        for index,unit in enumerate(plan['units']):
            record={'unit_index':index,'point_index':unit['point'],'status':'pending','selectors':deepcopy(unit_selectors(unit)),
                    'linked_roles':[link['role'] for link in unit['linked_supports']],'resolved_supports':[]}
            records.append(record)
            cited=set();texts=set();published=set()
            for si,selector in enumerate(unit_selectors(unit)):
                support=resolve_selector(selector,registry,payload,primary=si==0)
                identifier,field,quote=(support[k] for k in ('citation_id','field','quote'))
                if (not 1<=len(quote)<=MAX_QUOTE_CHARS or not quote.strip()
                        or field not in fields.get(identifier,{})
                        or ' '.join(quote.split()) not in ' '.join(fields[identifier][field].split())):raise ValueError()
                cited.add(identifier)
                if field=='text':texts.add(identifier)
                if field=='source_publication':
                    if quote!=publications.get(identifier,{}).get('label'):raise ValueError()
                    published.add(publications[identifier]['source'])
                record['resolved_supports'].append(support)
            if any(c not in texts for identifier in cited for c in contexts[identifier]):raise ValueError()
            if any(publications[c]['source'] not in published for c in cited if c in publications):raise ValueError()
            record['status']='resolved'
        if observer:observer({'complete':True,'kind':'plan_source_provenance','units':records,'plan_sha256':hashlib.sha256(encoded(plan)).hexdigest()})
        return plan
    except (ValueError,TypeError,KeyError,IndexError):
        if records:records[-1]['status']='failed'
        if observer:observer({'complete':False,'kind':'plan_source_provenance','units':records})
        raise ValueError('Plan source provenance differs') from None


def validate_plan_refs(claim, plan, *, observer=None):
    """Exact selector retention only; never semantic entailment or output repair."""
    if type(claim) is not dict or set(claim)!={'plan_refs','primary_support','supports','text'}:raise ValueError('Invalid planned claim')
    refs=claim['plan_refs']
    if (type(refs) is not list or len(refs)>12
            or any(type(i) is not int or not 0<=i<len(plan['units']) for i in refs)
            or len(set(refs))!=len(refs)
            or type(claim['supports']) is not list or len(claim['supports'])>9):raise ValueError('Invalid plan references')
    present=[selector_identity(s) for s in [claim['primary_support'],*claim['supports']]]
    required=[]
    for i in refs:
        for s in unit_selectors(plan['units'][i]):
            pair=selector_identity(s)
            if pair not in required:required.append(pair)
    missing=[pair for pair in required if pair not in present]
    record={'plan_refs':deepcopy(refs),'plan_sha256':hashlib.sha256(encoded(plan)).hexdigest(),
            'required_selectors':[list(pair) for pair in required],
            'present_selectors':[list(pair) for pair in present],'missing_selectors':[list(pair) for pair in missing],
            'selector_retention_only':True}
    if observer:observer(deepcopy(record))
    if missing:raise ValueError('Referenced plan support missing')
    return record
