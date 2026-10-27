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
        span=next((x['span_id'] for x in candidates if isinstance(x,dict) and 'span_id' in x
                   and quote in ' '.join(x['text'].split())),'unknown-span')
        return {'citation_id':citation,'span_id':span}
    result=deepcopy(unit)
    result['primary_support']=selector(unit['primary_support'])
    result['supports']=[selector(s) for s in unit['supports']]
    return result


def select_response(native,payload):
    result=deepcopy(native)
    paragraphs=([result['paragraph']] if result.get('paragraph') is not None else []) if 'paragraph' in result else result['paragraphs']
    for paragraph in paragraphs:
        paragraph['claims']=[select_claim(unit,payload) for unit in paragraph['claims']]
    return result


def payload_from_prepared(prepared):
    return json.loads(prepared.messages[-1]['content'])
