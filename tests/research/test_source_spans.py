"""Lossless representation/ownership controls; no model or corpus access."""
from copy import deepcopy
import json

import pytest

from backend.source_spans import (annotate_payload,verify_annotated_payload,resolve_selector,fragments,registry_hash,
                                 verify_wire_binding,encoded,ANCHOR_PROTOCOL)
from backend.reconstruction import prepare_reconstruction,normalize_reconstruction,reconstruction_schema
from backend.chat import ChatRequest,prepare_answer
from tests.research.test_reconstruction import claim,response
from tests.research.span_fixtures import select_response


def payload(text='Visible source text.'):
    return {'question':'What does the source establish?',
        'sources':{'source-1':{'legal_currency':'unverified','source_date_metadata':None},
                   'source-2':{'legal_currency':'unverified'}},
        'evidence':[{'id':'a','source':'source-1','text':text,'warning':''},
                    {'id':'b','source':'source-1','text':'Another passage.'},
                    {'id':'c','source':'source-2','text':'Separate source.'}]}


@pytest.mark.parametrize('text',['',' \n\t','界'*1301,'😀'*601,'A. '*450,
    '  Begin.\n\n'+'Bounded condition. '*80+'\nEnd.\t','X'+' '*1300+'Y','x'*601])
def test_every_character_roundtrips_with_bounded_exact_offsets(text):
    original=payload(text);before=deepcopy(original)
    actual,registry=annotate_payload(original)
    restored,checked=verify_annotated_payload(actual,original)
    assert restored==original==before and checked==registry
    again,again_registry=annotate_payload(original)
    assert again==actual and registry_hash(again_registry)==registry_hash(registry)
    spans=[span for span in registry.values() if span['owner_kind']=='evidence' and span['owner_id']=='a' and span['field']=='text']
    assert all(0<len(span['text'])<=600 and span['text'].strip() for span in spans)
    for span in spans:assert text[span['start']:span['end']]==span['text']
    if not text.strip():assert actual['evidence'][0]['text']==text and not spans
    else:assert ''.join(x['text'] for x in actual['evidence'][0]['text'])==text


def test_nested_nonstring_and_empty_metadata_are_preserved_without_support():
    original=payload();source=original['sources']['source-1']
    source.update(source_date_metadata={'reviewed_locator_and_dates':'Visible date: 2024.',
        'date_caution':None,'other':{'arbitrary':['do not change',{'span_id':'not-an-anchor','text':'metadata'}]}},
        guide_verification={'limitations':[],'empty':''},extra=[None,False,{},[]])
    actual,registry=annotate_payload(original)
    assert verify_annotated_payload(actual,original)[0]==original
    assert actual['sources']['source-1']['guide_verification']==source['guide_verification']
    assert all(span['field']!='guide_verification.limitations' for span in registry.values())
    assert 'not-an-anchor' not in registry
    assert actual['sources']['source-1']['source_date_metadata']['other']==source['source_date_metadata']['other']


def test_source_metadata_reuse_requires_exact_source_identity_even_for_identical_text():
    original=payload();_,registry=annotate_payload(original)
    span=next(key for key,value in registry.items() if value['owner_kind']=='source' and value['owner_id']=='source-1')
    for citation in ('a','b'):
        assert resolve_selector({'citation_id':citation,'span_id':span},registry,original)['quote']=='unverified'
    with pytest.raises(ValueError,match='belong'):resolve_selector({'citation_id':'c','span_id':span},registry,original)
    with pytest.raises(ValueError,match='belong'):resolve_selector({'citation_id':'a','span_id':span},registry,original,primary=True)
    text_span=next(key for key,value in registry.items() if value['owner_kind']=='evidence' and value['owner_id']=='a')
    with pytest.raises(ValueError,match='belong'):resolve_selector({'citation_id':'b','span_id':text_span},registry,original)


@pytest.mark.parametrize('selector',[{}, {'citation_id':'a','span_id':'missing'},
    {'citation_id':'missing','span_id':'s1'}, {'citation_id':'a','span_id':['s1']},
    {'citation_id':'a','span_id':'s1','quote':'injected'}, {'citation_id':'a','field':'text','quote':'Visible source text.'}])
def test_unknown_or_free_quote_selector_is_rejected(selector):
    original=payload();_,registry=annotate_payload(original)
    with pytest.raises(ValueError):resolve_selector(selector,registry,original)


def test_publication_label_is_whole_and_never_truncated():
    original=payload();original['sources']['source-1']['source_publication']='P'*600
    actual,registry=annotate_payload(original)
    labels=[s for s in registry.values() if s['field']=='source_publication']
    assert len(labels)==1 and labels[0]['text']=='P'*600
    assert verify_annotated_payload(actual,original)[0]==original
    original['sources']['source-1']['source_publication']+='P';before=deepcopy(original)
    with pytest.raises(ValueError,match='Publication label'):annotate_payload(original)
    assert original==before


@pytest.mark.parametrize('mutate',[
    lambda p:p['evidence'][0]['text'][0].update(text='Changed text.'),
    lambda p:p['evidence'][0]['text'][0].update(span_id='s999'),
    lambda p:p['evidence'].pop(),
    lambda p:p['sources']['source-1'].update(legal_currency=[]),
    lambda p:p.update(question='Changed question?'),
    lambda p:p['evidence'][0].update(source='source-2'),
])
def test_actual_wire_mutation_cannot_borrow_original_registry(mutate):
    original=payload();actual,_=annotate_payload(original);mutate(actual)
    with pytest.raises(ValueError):verify_annotated_payload(actual,original)


def test_oversize_full_selector_schema_is_refused_without_pruning_ids():
    request=ChatRequest(question='What does the source say?')
    original=prepare_answer(request,[{'id':'a','text':'Visible source text.'}],provider='anthropic')
    registry={'s'+str(i):{'field':'text'} for i in range(1000)}
    before=deepcopy(registry)
    with pytest.raises(ValueError,match='schema exceeds'):reconstruction_schema(original.schema,'standard',registry)
    assert registry==before


def test_registry_mutation_is_rejected_even_when_selected_text_would_match():
    request=ChatRequest(question='What do gates do?')
    original=prepare_answer(request,[{'id':'a','text':'Gates regulate tidal water.'}],provider='anthropic')
    prepared=prepare_reconstruction(request,original,{'status':'insufficient_evidence','paragraphs':[]})
    native=response(claim(),prepared=prepared)
    first=next(iter(prepared.span_registry));prepared.span_registry[first]['start']+=1
    with pytest.raises(ValueError):normalize_reconstruction(native,prepared)


def test_split_conditions_stay_visible_and_can_be_supported_in_one_claim():
    text=('Context sentence. '*25)+'Permitted only with Board consent. '+('Other context. '*25)+'Work must stop during nesting season.'
    request=ChatRequest(question='What conditions apply?');original=prepare_answer(request,[{'id':'a','text':text}],provider='anthropic')
    prepared=prepare_reconstruction(request,original,{'status':'insufficient_evidence','paragraphs':[]})
    visible=json.loads(prepared.messages[-1]['content']);parts=visible['evidence'][0]['text']
    assert ''.join(p['text'] for p in parts)==text
    unit=claim('Board consent is required and work must stop during nesting season.',quote='Permitted only with Board consent.',
        extras=[{'citation_id':'a','field':'text','quote':'Work must stop during nesting season.'}])
    answer,offsets=normalize_reconstruction(response(unit,prepared=prepared),prepared)
    assert answer['paragraphs'][0]['text']==unit['text'] and len(offsets[0]['span_ids'])==2


def test_date_omission_is_still_a_semantic_negative_even_with_valid_span():
    text='The report published in 2024 records that the 2017 survey measured 25 units at Site V.'
    request=ChatRequest(question='What quantity was reported?')
    original=prepare_answer(request,[{'id':'a','text':text}],provider='anthropic')
    draft={'status':'answered','paragraphs':[{'text':'The 2024 report records 25 units in the 2017 survey.','citations':['a']}]}
    prepared=prepare_reconstruction(request,original,draft)
    assert 'Preserve source-visible date attribution' in prepared.messages[0]['content']
    good=claim('The report published in 2024 records 25 units measured at Site V in 2017.',quote=text)
    assert normalize_reconstruction(response(good,prepared=prepared),prepared)[0]['status']=='answered'
    wrong=claim('The source reports 25 units at Site V.',quote=text)
    assert normalize_reconstruction(response(wrong,prepared=prepared),prepared)[0]['paragraphs'][0]['text']==wrong['text']
    # Authored negative: visible material chronology omitted. This mechanical
    # acceptance must never be counted as a source-reviewed semantic pass.


def wire_fixture():
    original=payload('Visible source text.\n😀 चाँद e\u0301')
    annotated,registry=annotate_payload(original)
    draft={'messages':[{'role':'user','content':'Prior context 😀'},
                       {'role':'user','content':encoded(original).decode()}]}
    wrapper={**annotated,'anchor_protocol':ANCHOR_PROTOCOL,'request_scope':{'answer_style':'standard','document_id':None,'generation':None},
             'draft_answer':{'status':'insufficient_evidence','paragraphs':[]}}
    correction={'messages':[draft['messages'][0],{'role':'user','content':encoded(wrapper).decode()}]}
    return draft,correction,registry


def test_actual_wire_byte_basis_allows_outer_escaping_but_preserves_exact_inner_payload():
    draft,correction,registry=wire_fixture()
    # HTTP JSON may encode the same inner string differently. The original byte
    # basis is its decoded user content string, not the outer JSON quoting.
    proof=verify_wire_binding(json.dumps(correction,ensure_ascii=True),json.dumps(draft,ensure_ascii=True),registry_hash(registry))
    assert proof['byte_equality'] and proof['value_equality'] and proof['actual_wire_verified']
    assert proof['original_draft_payload_utf8_sha256']==proof['reconstructed_payload_utf8_sha256']
    assert proof['original_payload_utf8_bytes']==len(draft['messages'][-1]['content'].encode())


@pytest.mark.parametrize('mutation',['inner_escape','inner_order','history','registry','span_order'])
def test_semantic_equality_is_not_original_wire_byte_identity(mutation):
    draft,correction,registry=wire_fixture();expected=registry_hash(registry)
    if mutation=='inner_escape':
        draft['messages'][-1]['content']=json.dumps(json.loads(draft['messages'][-1]['content']),ensure_ascii=True,separators=(',',':'))
    elif mutation=='inner_order':
        value=json.loads(draft['messages'][-1]['content'])
        draft['messages'][-1]['content']=encoded({key:value[key] for key in reversed(value)}).decode()
    elif mutation=='history':correction['messages'][0]={'role':'user','content':'Different context'}
    elif mutation=='registry':expected='0'*64
    else:
        value=json.loads(correction['messages'][-1]['content'])
        value['sources']={key:value['sources'][key] for key in reversed(value['sources'])}
        correction['messages'][-1]['content']=encoded(value).decode()
    with pytest.raises(ValueError,match='actual-wire'):
        verify_wire_binding(encoded(correction).decode(),encoded(draft).decode(),expected)
