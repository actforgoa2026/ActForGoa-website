"""Lossless correction-only source spans; selectors never supply new quotations."""
from copy import deepcopy
import hashlib
import json
import re

from .anthropic_provider import SUPPORT_FIELDS, MAX_QUOTE_CHARS

ANCHOR_PROTOCOL = 'lossless_source_spans_v1'
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
            fragment={'text':text}
            if text.strip():
                identifier='s'+str(len(registry)+1)
                fragment={'span_id':identifier,'text':text}
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
    if actual!=expected:raise ValueError('Source span wire identity differs')
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
            text=fragment['text'];end=position+len(text)
            if 'span_id' in fragment:
                rebuilt_registry[fragment['span_id']]={'owner_kind':kind,'owner_id':owner,'field':field,
                    'start':position,'end':end,'text':text}
            position=end
        target[target_key]=''.join(part['text'] for part in parts)
    if reconstructed!=original or rebuilt_registry!=registry:
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


def verify_wire_binding(correction_body_utf8, draft_body_utf8, expected_registry_sha256):
    """Prove identity from captured HTTP bodies, including inner-payload bytes.

    The byte basis is the UTF8 content of the draft's final user message, after
    decoding the outer HTTP JSON string once. prepare_answer serializes it as
    compact ensure_ascii=False JSON in insertion order. Outer HTTP escaping is
    independent; inner payload escaping/order must reconstruct byte-for-byte.
    """
    try:
        draft=json.loads(draft_body_utf8);correction=json.loads(correction_body_utf8)
        original_bytes=draft['messages'][-1]['content'].encode('utf-8')
        original=json.loads(original_bytes)
        wrapper=json.loads(correction['messages'][-1]['content'])
        if (set(wrapper)!={'question','sources','evidence','request_scope','draft_answer','anchor_protocol'}
                or wrapper['anchor_protocol']!=ANCHOR_PROTOCOL
                or correction['messages'][:-1]!=draft['messages'][:-1]):raise ValueError()
        restored,registry=verify_annotated_payload({k:wrapper[k] for k in ('question','sources','evidence')},original)
        reconstructed_bytes=encoded(restored)
        if reconstructed_bytes!=original_bytes or registry_hash(registry)!=expected_registry_sha256:raise ValueError()
        digest=lambda value:hashlib.sha256(value).hexdigest()
        return {'actual_wire_verified':True,'value_equality':True,'byte_equality':True,
            'serialization_contract':PAYLOAD_SERIALIZATION,'original_payload_utf8_bytes':len(original_bytes),
            'original_draft_payload_utf8_sha256':digest(original_bytes),
            'reconstructed_payload_utf8_sha256':digest(reconstructed_bytes),
            'actual_request_body_sha256':digest(correction_body_utf8.encode('utf-8')),
            'captured_draft_request_body_sha256':digest(draft_body_utf8.encode('utf-8')),
            'retained_history_equal':True,'span_registry_sha256':registry_hash(registry)}
    except (ValueError,KeyError,TypeError,IndexError,AttributeError):
        raise ValueError('Source span actual-wire binding differs') from None
