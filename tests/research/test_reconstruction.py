"""Source-neutral offline reconstruction tests; no provider or native library."""
from copy import deepcopy
from dataclasses import replace
import json

import pytest

from backend.chat import ChatRequest, Message, prepare_answer
from backend.providers import chat_config
from backend.reconstruction import (prepare_reconstruction, reconstruction_message_request,
    normalize_reconstruction, encoded, CORRECTION_PROMPT_BYTES)
from backend.source_spans import verify_annotated_payload
from tests.research.span_fixtures import select_response,payload_from_prepared,slot_response


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER', 'anthropic')
    monkeypatch.setenv('ANTHROPIC_CHAT_MODEL', 'claude-haiku-5-5')
    monkeypatch.setenv('ANTHROPIC_CHAT_EFFORT', 'medium')
    monkeypatch.setenv('ANTHROPIC_ANSWER_PIPELINE','two_pass_v11')
    evidence = [{'id': 'a', 'text': 'Gates regulate tidal water. Design must follow Appendix C.',
                 'document_id': 'doc-a', 'generation': 'fixture'}]
    request = ChatRequest(question='What do the gates do?', history=[Message(role='user',content='Tell me about gates.')])
    original = prepare_answer(request, evidence, provider='anthropic')
    draft = {'status':'insufficient_evidence','points':[],'units':[]}
    return chat_config(), request, original, draft


def claim(text='Gates regulate tidal water.', citation='a', quote='Gates regulate tidal water.', extras=()):
    return {'primary_support': {'citation_id':citation,'field':'text','quote':quote},
            'supports':list(extras),'text':text}


def response(*units, style='standard', prepared=None):
    paragraph = {'claims': list(units)}
    native={'status':'answered', **({'paragraph':paragraph} if style=='brief' else {'paragraphs':[paragraph]})}
    if prepared is not None:native=select_response(native,payload_from_prepared(prepared))
    return json.dumps(native)


@pytest.mark.parametrize('style',['standard','brief'])
def test_exact_complete_input_and_deterministic_claim_assembly(setup,style):
    config,request,original,draft=setup
    request=request.model_copy(update={'answer_style':style})
    original=prepare_answer(request,original.evidence,provider='anthropic')
    before=deepcopy(original)
    prepared=prepare_reconstruction(request,original,draft)
    wire=reconstruction_message_request(config,prepared)
    source=json.loads(original.messages[-1]['content']);actual=json.loads(wire['messages'][-1]['content'])
    assert verify_annotated_payload({k:actual[k] for k in ('question','sources','evidence')},source)[0]==source
    assert wire['messages'][:-1]==original.messages[1:-1]
    assert actual['evidence_plan']==draft
    assert actual['request_scope']=={'answer_style':style,'document_id':None,'generation':None}
    assert original==before and 'not forwarded' not in str(wire)
    assert len(encoded(prepared.messages))+2048==prepared.input_token_bound
    assert len(encoded(prepared.schema))<4096
    assert wire['output_config']['effort']=='medium' and wire['max_tokens']==12000
    assert 'direct the reader to the original table' not in wire['system']
    units=[claim(),claim('Design must follow Appendix C.',quote='Design must follow Appendix C.')]
    answer,offsets=normalize_reconstruction(response(*units,style=style,prepared=prepared),prepared)
    assert answer['paragraphs']==[{'text':'Gates regulate tidal water. Design must follow Appendix C.','citations':['a']}]
    for m,u in zip(offsets,units):
        assert answer['paragraphs'][0]['text'][m['start']:m['end']]==u['text']
        assert m['citation_ids']==['a']


def test_insufficient_draft_is_reconstructed_and_final_abstention_is_empty(setup):
    _,request,original,_=setup
    prepared=prepare_reconstruction(request,original,{'status':'insufficient_evidence','points':[],'units':[]})
    assert normalize_reconstruction(response(claim(),prepared=prepared),prepared)[0]['status']=='answered'
    answer,mapping=normalize_reconstruction(json.dumps(slot_response({'status':'insufficient_evidence','paragraphs':[]})),prepared)
    assert answer['paragraphs']==[] and mapping==[]


@pytest.mark.parametrize('mutation',[
    lambda p:p.messages[-1].update(content=p.messages[-1]['content'].replace('tidal water','fresh water')),
    lambda p:p.schema['properties'].update(unexpected={'type':'string'}),
    lambda p:setattr(p,'input_token_bound',p.input_token_bound-1),
    lambda p:p.request.update(question='A different question?'),
    lambda p:p.original.evidence[0].update(text='Changed source.'),
])
def test_mutated_prepared_input_cannot_dispatch(setup,mutation):
    config,request,original,draft=setup
    prepared=prepare_reconstruction(request,original,draft);mutation(prepared)
    with pytest.raises(ValueError):reconstruction_message_request(config,prepared)


def test_multibyte_compact_draft_overflow_is_not_truncated(setup):
    _,request,original,draft=setup
    draft.update(status='insufficient_evidence',points=[{'need':'界'*33,'coverage':'missing','gaps':['support']}],units=[])
    before=deepcopy(draft)
    with pytest.raises(ValueError,match='invalid_evidence_plan'):prepare_reconstruction(request,original,draft)
    assert draft==before


def test_full_message_overflow_preserves_all_input_before_refusal(setup):
    _,request,original,draft=setup
    original.messages.insert(1,{'role':'user','content':'界'*12000})
    before=deepcopy(original)
    with pytest.raises(ValueError,match='input exceeds'):prepare_reconstruction(request,original,draft)
    assert original==before


@pytest.mark.parametrize('unit',[
    {'text':'No free bridge.','claims':[claim()]},
    {'claims':[]},
    {'claims':[claim(quote='Not in the source.')]},
    {'claims':[claim(citation='missing')]},
    {'claims':[dict(claim(),score=1)]},
])
def test_free_prose_or_unsupported_anchor_shapes_rejected(setup,unit):
    _,request,original,draft=setup;prepared=prepare_reconstruction(request,original,draft)
    with pytest.raises(ValueError,match='evidence contract'):
        normalize_reconstruction(json.dumps({'status':'answered','paragraphs':[unit]}),prepared)


def test_claim_local_context_cannot_be_borrowed_from_sibling(setup):
    _,request,_,draft=setup
    context={'id':'ctx-header','text':'Table: Endemic to Region R.','document_id':'doc-a','generation':'fixture','page':1}
    row={'id':'a','text':'Species P occurs here.','document_id':'doc-a','generation':'fixture','page':1,'supporting_context':[context]}
    original=prepare_answer(request,[row],provider='anthropic')
    draft={'status':'insufficient_evidence','points':[],'units':[]}
    prepared=prepare_reconstruction(request,original,draft)
    row_claim=claim('Species P occurs here.',quote='Species P occurs here.')
    header_claim=claim('The header labels regional endemism.',citation='ctx-header',quote=context['text'])
    with pytest.raises(ValueError):normalize_reconstruction(response(row_claim,header_claim,prepared=prepared),prepared)
    row_claim['supports']=[header_claim['primary_support']]
    assert normalize_reconstruction(response(row_claim,header_claim,prepared=prepared),prepared)[0]['status']=='answered'


def test_publication_acknowledgement_is_shared_within_paragraph_only(setup):
    _,request,_,draft=setup
    e={'id':'a','text':'Gates regulate tidal water. Design must follow Appendix C.',
       'source_date_metadata':[{'field':'prism.publicationDate','value':'2022-01-04'}]}
    original=prepare_answer(request,[e],provider='anthropic');prepared=prepare_reconstruction(request,original,draft)
    publication={'citation_id':'a','field':'source_publication','quote':'Source publication year: 2022 (source metadata).'}
    first=claim('The source published in 2022 states that gates regulate tidal water.',extras=[publication])
    second=claim('Design must follow Appendix C.',quote='Design must follow Appendix C.')
    assert normalize_reconstruction(response(first,second,prepared=prepared),prepared)[0]['status']=='answered'
    native={'status':'answered','paragraphs':[{'claims':[first]},{'claims':[second]}]}
    with pytest.raises(ValueError):normalize_reconstruction(json.dumps(select_response(native,payload_from_prepared(prepared))),prepared)


def test_deduplicated_paragraph_support_limit_does_not_add_claim_count_cap(setup):
    _,request,original,draft=setup;prepared=prepare_reconstruction(request,original,draft)
    assert normalize_reconstruction(response(*[claim() for _ in range(15)],prepared=prepared),prepared)[0]['status']=='answered'
    # Distinct exact quotes still retain the existing ten-support paragraph cap.
    text=''.join((f'Fact {i}. ').ljust(600,'x') for i in range(11));original.evidence[0]['text']=text
    original=prepare_answer(request,original.evidence,provider='anthropic');prepared=prepare_reconstruction(request,original,draft)
    with pytest.raises(ValueError):normalize_reconstruction(response(*[claim(f'Fact {i}.',quote=f'Fact {i}.') for i in range(11)],prepared=prepared),prepared)


def test_quote_valid_wrong_claim_is_not_mistaken_for_semantic_acceptance(setup):
    _,request,original,draft=setup;prepared=prepare_reconstruction(request,original,draft)
    wrong='Gates regulate all water everywhere and need no design conditions.'
    # This must remain an explicit semantic negative even though the local
    # mechanics accept its genuine quote. No automatic accuracy score exists.
    answer,_=normalize_reconstruction(response(claim(wrong),prepared=prepared),prepared)
    assert answer['paragraphs'][0]['text']==wrong
