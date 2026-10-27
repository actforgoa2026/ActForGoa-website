"""Prompt size savings must never remove a source qualification or change text."""
from copy import deepcopy
import json

import pytest

from backend.chat import (ChatRequest, GroundedAnswer, MAX_PROMPT_BYTES,
                          FRAMING_TOKEN_ALLOWANCE, evidence_payload,
                          prepare_answer, validate_answer)


def passage(identifier, **changes):
    return dict(id=identifier, document_id='doc-a', generation='generation-a',
                title='Saved national assessment', url='https://example.org/source.pdf',
                retrieved_at='2026-01-01', publisher_class='government_or_court',
                legal_currency='Not verified current consolidated law.',
                source_date_metadata=[{'field': 'publication_date', 'value': '2011'}],
                guide_verification={'status': 'source_verified', 'remaining': ['Confirm applicability locally.']},
                topics=['water'], document_kind_hint='report', page=7,
                label='Physical page 7', start=10, end=48,
                text='The district has a recorded supply.\n',
                page_heading='7.2 ANOTHER STATE', warning='OCR may be incomplete.',
                **changes)


def test_shared_provenance_round_trips_with_exact_local_context():
    first=passage('a'); second={**first,'id':'b','page':8,'start':23,'end':57,
                               'text':'पाणी  stays\nexact.','page_heading':'8.1 GOA',
                               'warning':'Different page warning.'}
    hits=[first,second]; before=deepcopy(hits)
    payload=evidence_payload(hits)
    assert len(payload['sources'])==1
    for sent, original in zip(payload['evidence'],hits):
        joined={**payload['sources'][sent['source']],**{k:v for k,v in sent.items() if k!='source'}}
        assert joined==original
    assert hits==before


@pytest.mark.parametrize('field,value',[
    ('document_id','other-document'), ('generation','older-generation'),
    ('url','https://example.org/amendment.pdf'), ('legal_currency','Draft only.'),
    ('guide_verification',{'remaining':['Later court orders unverified.']}),
    ('source_date_metadata',[{'field':'publication_date','value':'2025'}]),
])
def test_different_source_identity_or_caveats_are_never_merged(field,value):
    first=passage('a');second={**first,'id':'b',field:value}
    payload=evidence_payload([first,second])
    assert len(payload['sources'])==2
    assert payload['evidence'][0]['source']!=payload['evidence'][1]['source']


def test_compaction_keeps_more_complete_evidence_with_same_byte_cap():
    common=passage('a')
    common['legal_currency']='Not verified current law; confirm local applicability. '*45
    hits=[{**common,'id':f'passage-{i}','page':i+1,'text':'Exact saved prose. '*35} for i in range(10)]
    prepared=prepare_answer(ChatRequest(question='What does the saved source support?',answer_style='brief'),hits)
    size=len(json.dumps(prepared.messages,ensure_ascii=False,separators=(',',':')).encode())
    assert size<=MAX_PROMPT_BYTES==24000
    assert prepared.input_token_bound==size+FRAMING_TOKEN_ALLOWANCE
    assert prepared.evidence==hits
    payload=json.loads(prepared.messages[-1]['content'])
    assert len(payload['sources'])==1
    assert [e['text'] for e in payload['evidence']]==[e['text'] for e in hits]
    assert payload['sources']['source-1']['legal_currency']==common['legal_currency']
    assert prepared.schema['properties']['paragraphs']['items']['properties']['citations']['items']['enum']==[h['id'] for h in hits]
    # Repeating the same metadata in the former layout exceeds this cap.
    old_fields=('id','title','label','text','page_heading','url','warning','retrieved_at',
                'publisher_class','legal_currency','source_date_metadata','topics',
                'document_kind_hint','guide_verification')
    repeated={'question':'What does the saved source support?',
              'evidence':[{k:h[k] for k in old_fields} for h in hits]}
    old_messages=[prepared.messages[0],{'role':'user','content':json.dumps(repeated,separators=(',',':'))}]
    assert len(json.dumps(old_messages,separators=(',',':')).encode())>MAX_PROMPT_BYTES


def test_source_references_are_not_accepted_as_citations_or_private_paths():
    hits=[{**passage('a'),'raw_path':'private/data.pdf','page_context':'Uncited prose.'}]
    prepared=prepare_answer(ChatRequest(question='What is supported?'),hits)
    encoded=json.dumps(prepared.messages)
    assert 'private/data.pdf' not in encoded and 'Uncited prose.' not in encoded
    bad=GroundedAnswer.model_validate({'status':'answered','paragraphs':[{'text':'Claim.','citations':['source-1']}]})
    with pytest.raises(ValueError,match='unknown citations'):validate_answer(bad,hits)
