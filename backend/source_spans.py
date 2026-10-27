"""Lossless source spans in both stages; selectors never supply quotations."""
from copy import deepcopy
import hashlib
import json
import re

from .anthropic_provider import SUPPORT_FIELDS, MAX_QUOTE_CHARS

ANCHOR_PROTOCOL = 'lossless_source_spans_v2'
PAYLOAD_SERIALIZATION = 'utf8-json-ensure_ascii_false-compact-preserve_key_order'


def encoded(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()


def registry_hash(registry):
    return hashlib.sha256(encoded(registry)).hexdigest()


def _location(record, field):
    parts=field.split('.');parent=record
    for key in parts[:-1]:
        parent=parent.get(key) if isinstance(parent,dict) else None
    return (parent,parts[-1]) if isinstance(parent,dict) else (None,None)


def _fields(payload):
    if (not isinstance(payload,dict) or set(payload)!={'question','sources','evidence'}
            or not isinstance(payload['sources'],dict) or not isinstance(payload['evidence'],list)):
        raise ValueError('Invalid source span payload')
    for identifier,record in payload['sources'].items():
        if not isinstance(record,dict):raise ValueError('Invalid source span record')
        for field in SUPPORT_FIELDS:
            if field not in ('text','warning'):
                yield 'source',identifier,record,field
    seen=set()
    for record in payload['evidence']:
        if (not isinstance(record,dict) or not isinstance(record.get('id'),str) or record['id'] in seen
                or record.get('source') not in payload['sources']):raise ValueError('Invalid source span passage')
        seen.add(record['id'])
        for field in ('text','warning'):
            yield 'evidence',record['id'],record,field


def fragments(text):
    """Greedy bounded partition, preferring complete sentences then whitespace.

    Offsets are Python Unicode code points. Every character belongs to exactly
    one piece, including leading/trailing whitespace and incomplete sentences.
    """
    start=0
    while start<len(text):
        end=min(start+MAX_QUOTE_CHARS,len(text))
        if end<len(text):
            window=text[start:end]
            candidates=[m.end() for m in re.finditer(r'[.!?][\"\)\]\u201d\u2019]*\s+',window) if m.end()>=MAX_QUOTE_CHARS//2]
            if not candidates:
                candidates=[m.end() for m in re.finditer(r'\s+',window) if m.end()>=MAX_QUOTE_CHARS//2]
            if candidates:end=start+candidates[-1]
        yield start,end,text[start:end]
        start=end


def annotate_payload(original):
    result=deepcopy(original);registry={}
    for kind,owner,record,field in _fields(result):
        parent,key=_location(record,field)
        value=parent.get(key) if parent is not None else None
        # Empty/whitespace-only strings and non-string nested metadata stay
        # exactly as supplied. They grant no new support or inferred text.
        if not isinstance(value,str) or not value.strip():continue
        if field=='source_publication':
            if len(value)>MAX_QUOTE_CHARS:raise ValueError('Publication label exceeds source span bound')
            pieces=[(0,len(value),value)]
        else:pieces=fragments(value)
        annotated=[]
        for start,end,text in pieces:
            fragment=[None,text]
            if text.strip():
                identifier='s'+str(len(registry)+1)
                fragment=[identifier,text]
                registry[identifier]={'owner_kind':kind,'owner_id':owner,'field':field,
                                      'start':start,'end':end,'text':text}
            annotated.append(fragment)
        parent[key]=annotated
    return result,registry


def verify_annotated_payload(actual, original):
    """Bind actual wire content to the canonical registry and lossless original.

    Original types identify eligible string fields; a pre-existing metadata
    array must never be interpreted as an invented string or support catalogue.
    """
    expected,registry=annotate_payload(original)
    # Python equality equates True/1 and 1/1.0. The JSON contract must preserve
    # their types and the documented key order, as well as semantic values.
    if actual!=expected or encoded(actual)!=encoded(expected):raise ValueError('Source span wire identity differs')
    reconstructed=deepcopy(actual)
    original_fields=list(_fields(original));actual_fields=list(_fields(reconstructed))
    if len(original_fields)!=len(actual_fields):raise ValueError('Source span field identity differs')
    rebuilt_registry={}
    for before,after in zip(original_fields,actual_fields):
        kind,owner,record,field=before
        other_kind,other_owner,other_record,other_field=after
        if (kind,owner,field)!=(other_kind,other_owner,other_field):raise ValueError('Source span ownership differs')
        parent,key=_location(record,field);value=parent.get(key) if parent is not None else None
        if not isinstance(value,str) or not value.strip():continue
        target,target_key=_location(other_record,field);parts=target[target_key]
        position=0
        for fragment in parts:
            identifier,text=fragment;end=position+len(text)
            if identifier is not None:
                rebuilt_registry[identifier]={'owner_kind':kind,'owner_id':owner,'field':field,
                    'start':position,'end':end,'text':text}
            position=end
        target[target_key]=''.join(part[1] for part in parts)
    if (reconstructed!=original or encoded(reconstructed)!=encoded(original)
            or rebuilt_registry!=registry or encoded(rebuilt_registry)!=encoded(registry)):
        raise ValueError('Source spans do not reconstruct original evidence')
    return reconstructed,rebuilt_registry


def resolve_selector(selector, registry, original_payload, *, primary=False):
    if not isinstance(selector,dict) or set(selector)!={'citation_id','span_id'}:
        raise ValueError('Invalid source span selector')
    citation,identifier=selector['citation_id'],selector['span_id']
    if not isinstance(citation,str) or not isinstance(identifier,str) or identifier not in registry:
        raise ValueError('Unknown source span selector')
    passages={item['id']:item for item in original_payload['evidence']}
    if citation not in passages:raise ValueError('Unknown source span citation')
    span=registry[identifier]
    owner=citation if span['owner_kind']=='evidence' else passages[citation]['source']
    if span['owner_id']!=owner or (primary and span['field']!='text'):
        raise ValueError('Source span does not belong to selected citation')
    return {'citation_id':citation,'field':span['field'],'quote':span['text']}


def original_baseline(payload_utf8, history, scope):
    """Freeze the original preparation, not a claim that these bytes were sent.

    Private owned data until the transport's local credential/shape check passes.
    """
    payload=json.loads(payload_utf8)
    if encoded(payload)!=payload_utf8.encode('utf-8'):
        raise ValueError('Original payload serialization differs')
    if (not isinstance(payload,dict) or not isinstance(payload.get('question'),str)
            or not isinstance(scope,dict) or set(scope)!={'answer_style','document_id','generation'}
            or scope['answer_style'] not in ('standard','brief')
            or any(scope[key] is not None and not isinstance(scope[key],str) for key in ('document_id','generation'))
            or not isinstance(history,list) or any(not isinstance(item,dict) or set(item)!={'role','content'}
                or item['role'] not in ('user','assistant') or not isinstance(item['content'],str) for item in history)):
        raise ValueError('Original history or scope differs')
    # Also validate the exact original payload shape and represented ownership.
    list(_fields(payload))
    data={'kind':'prepared_original_payload','serialization_contract':PAYLOAD_SERIALIZATION,
          'payload_utf8':payload_utf8,'payload_sha256':hashlib.sha256(payload_utf8.encode()).hexdigest(),
          'retained_history':deepcopy(history),'request_scope':deepcopy(scope)}
    return {**data,'binding_sha256':hashlib.sha256(encoded(data)).hexdigest()}


def verify_wire_binding(actual_body_utf8, baseline, expected_registry_sha256, *, phase, draft_body_utf8=None):
    """Reconstruct each actual captured wire body to the same prepared baseline.

    The original UTF8 byte basis is explicitly pre-annotation preparation. Both
    actual sends use annotations. This proof never substitutes for the separate
    transport-owned credential check required before baseline capture.
    """
    try:
        expected_baseline=original_baseline(baseline['payload_utf8'],baseline['retained_history'],baseline['request_scope'])
        if encoded(baseline)!=encoded(expected_baseline):raise ValueError()
        actual=json.loads(actual_body_utf8)
        original_bytes=baseline['payload_utf8'].encode('utf-8')
        original=json.loads(original_bytes)
        wrapper=json.loads(actual['messages'][-1]['content'])
        keys={'question','sources','evidence','request_scope','anchor_protocol'}
        if phase=='reconstruction':keys.add('draft_answer')
        elif phase!='draft':raise ValueError()
        if (set(wrapper)!=keys
                or wrapper['anchor_protocol']!=ANCHOR_PROTOCOL
                or encoded(wrapper['request_scope'])!=encoded(baseline['request_scope'])
                or encoded(actual['messages'][:-1])!=encoded(baseline['retained_history'])):raise ValueError()
        restored,registry=verify_annotated_payload({k:wrapper[k] for k in ('question','sources','evidence')},original)
        reconstructed_bytes=encoded(restored)
        if reconstructed_bytes!=original_bytes or registry_hash(registry)!=expected_registry_sha256:raise ValueError()
        digest=lambda value:hashlib.sha256(value).hexdigest()
        proof={'actual_wire_verified':True,'value_equality':True,'byte_equality':True,
            'baseline_kind':'prepared_original_payload','phase':phase,
            'serialization_contract':PAYLOAD_SERIALIZATION,'original_payload_utf8_bytes':len(original_bytes),
            'prepared_original_payload_utf8_sha256':digest(original_bytes),
            'reconstructed_payload_utf8_sha256':digest(reconstructed_bytes),
            'actual_request_body_sha256':digest(actual_body_utf8.encode('utf-8')),
            'retained_history_equal':True,'request_scope_equal':True,'span_registry_sha256':registry_hash(registry)}
        if phase=='reconstruction':
            if not isinstance(draft_body_utf8,str):raise ValueError()
            draft_proof=verify_wire_binding(draft_body_utf8,baseline,expected_registry_sha256,phase='draft')
            proof['captured_draft_request_body_sha256']=draft_proof['actual_request_body_sha256']
            proof['both_actual_wires_match_baseline']=True
        return proof
    except (ValueError,KeyError,TypeError,IndexError,AttributeError):
        raise ValueError('Source span actual-wire binding differs') from None
