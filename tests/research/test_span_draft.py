"""Both-stage source selection and private baseline safety; fake provider only."""
import asyncio
from copy import deepcopy
import json
import hashlib
from pathlib import Path

import pytest

from backend import answer_pipeline, span_draft
from backend.async_anthropic import AsyncAnthropicClient
from backend.chat import ChatRequest, prepare_answer
from backend.span_draft import prepare_span_draft, normalize_span_draft
from backend.source_spans import annotate_payload, verify_annotated_payload, encoded
from tests.research.span_fixtures import select_response
from tests.research.test_reconstruction import claim
from tests.research.test_answer_pipeline import setup, Limits, Transport, model_response


@pytest.mark.parametrize('style',['standard','brief'])
def test_draft_selectors_preserve_original_selection_and_resolve_only_server_text(style):
    request=ChatRequest(question='What do gates do?',answer_style=style)
    original=prepare_answer(request,[{'id':'a','text':'Gates regulate tidal water.'}],provider='anthropic')
    before=deepcopy(original);prepared=prepare_span_draft(request,original)
    payload=json.loads(prepared.messages[-1]['content'])
    assert original==before
    assert verify_annotated_payload({k:payload[k] for k in ('question','sources','evidence')},json.loads(before.messages[-1]['content']))[0]==json.loads(prepared.baseline['payload_utf8'])
    native={'status':'answered',**({'paragraph':claim()} if style=='brief' else {'paragraphs':[claim()]})}
    selected=select_response(native,payload);observed=[]
    answer=normalize_span_draft(json.dumps(selected),prepared,resolved_observer=observed.append)
    assert answer['paragraphs']==[{'text':'Gates regulate tidal water.','citations':['a']}]
    assert observed[-1]['complete'] and observed[-1]['paragraphs'][0]['resolved_supports'][0]['quote']==original.evidence[0]['text']
    # The old copied-quote format, including a plausible case change, is not a
    # selector answer and is never repaired into an accepted draft.
    with pytest.raises(ValueError):normalize_span_draft(json.dumps(native),prepared)


@pytest.mark.parametrize('change',[
    lambda p:p.span_registry[next(iter(p.span_registry))].update(start=1),
    lambda p:p.baseline.update(payload_sha256='0'*64),
    lambda p:p.baseline['request_scope'].update(generation='changed'),
    lambda p:p.messages[-1].update(content=p.messages[-1]['content'].replace('Gates','gates')),
    lambda p:p.request.update(question='A different question?'),
    lambda p:p.schema.update(extra=True),
])
def test_prepared_draft_identity_rejects_registry_baseline_schema_or_request_mutation(change):
    request=ChatRequest(question='What do gates do?')
    original=prepare_answer(request,[{'id':'a','text':'Gates regulate tidal water.'}],provider='anthropic')
    prepared=prepare_span_draft(request,original)
    selected=select_response({'status':'answered','paragraphs':[claim()]},json.loads(prepared.messages[-1]['content']))
    change(prepared)
    with pytest.raises(ValueError):normalize_span_draft(json.dumps(selected),prepared)


def test_shorter_wire_prompt_does_not_reselect_extra_evidence_or_history():
    request=ChatRequest(question='What does the source establish?')
    evidence=[{'id':str(i),'text':('Visible conditions and source context. '*54)+str(i)} for i in range(12)]
    original=prepare_answer(request,evidence,provider='anthropic');before=deepcopy(original)
    assert len(original.evidence)<10
    prepared=prepare_span_draft(request,original)
    actual=json.loads(prepared.messages[-1]['content'])
    assert [e['id'] for e in actual['evidence']]==[e['id'] for e in before.evidence]
    assert original==before and prepared.messages[1:-1]==before.messages[1:-1]


def test_overflow_refuses_without_changing_selected_input(monkeypatch):
    request=ChatRequest(question='What do gates do?')
    original=prepare_answer(request,[{'id':'a','text':'Gates regulate tidal water.'}],provider='anthropic');before=deepcopy(original)
    monkeypatch.setattr(span_draft,'MAX_PROMPT_BYTES',10)
    with pytest.raises(ValueError,match='byte bound'):prepare_span_draft(request,original)
    assert original==before


@pytest.mark.parametrize('where',['source_split','question','encoded_question','history','scope_workspace','workspace_question','credential_field'])
def test_unsafe_original_is_withheld_before_any_reservation_observer_or_send(setup,where):
    config,_,_,transport,_,_,_,_=setup
    secret='fixture-only';workspace='private-workspace-fixture'
    request=ChatRequest(question='What do gates do?')
    evidence=[{'id':'a','text':'Gates regulate tidal water.'}]
    if where=='source_split':evidence[0]['text']='x'*597+secret+' visible source.'
    elif where=='question':request=ChatRequest(question='Explain '+secret+'.')
    elif where=='encoded_question':request=ChatRequest(question='Explain '+''.join('\\u%04x'%ord(c) for c in secret)+'.')
    elif where=='history':request=ChatRequest(question='What do gates do?',history=[{'role':'user','content':json.dumps({'value':secret})}])
    elif where=='scope_workspace':request=ChatRequest(question='What do gates do?',generation=workspace)
    elif where=='workspace_question':request=ChatRequest(question='Explain '+workspace+'.')
    else:evidence[0]['source_date_metadata']={'api_key':'authored-fake-value'}
    original=prepare_answer(request,evidence,provider='anthropic')
    if where=='source_split':
        annotated,_=annotate_payload(json.loads(original.messages[-1]['content']))
        assert secret not in encoded(annotated).decode()  # annotation alone cannot detect this echo
    limits=Limits();observed=[]
    def factory():return AsyncAnthropicClient(secret,workspace,transport=transport)
    with pytest.raises(answer_pipeline.PipelineFailure,match='unsafe_prepared_original') as caught:
        asyncio.run(answer_pipeline.run_answer_pipeline(request,original,config,limits=limits,client_factory=factory,observer=observed.append))
    assert not limits.receipts and not transport.requests and transport.closed
    assert 'prepared_original' not in caught.value.trace
    saved=json.dumps(observed)
    assert secret not in saved and workspace not in saved and 'authored-fake-value' not in saved


def test_draft_partial_resolution_keeps_raw_selector_failure_and_stops_correction(setup):
    _,_,_,transport,limits,_,run,_=setup;good=transport.handler
    async def broken(req,n):
        response=await good(req,n);payload=response.json();native=json.loads(payload['content'][-1]['text'])
        native['paragraph_1']['supports']=[{'citation_id':'a','span_id':'unknown'}]
        return model_response(native)
    transport.handler=broken
    with pytest.raises(answer_pipeline.PipelineFailure) as caught:run()
    phase=caught.value.trace['phases'][0]
    assert len(transport.requests)==len(limits.receipts)==1
    assert phase['final_output_diagnostic']['answer']['paragraph_1']['supports'][0]['span_id']=='unknown'
    resolution=phase['deterministic_support_resolution']
    assert not resolution['complete'] and len(resolution['paragraphs'][0]['resolved_supports'])==1
    assert resolution['paragraphs'][0]['status']=='failed'
    assert caught.value.trace['phases'][1]['provider_attempts']==0 and 'final_answer' not in caught.value.trace


def test_valid_selectors_do_not_prove_omitted_conditions_or_dates_semantically_correct():
    source='The 2023 rules permit work only with Board consent. Design must follow Appendix C.'
    request=ChatRequest(question='What conditions apply?')
    original=prepare_answer(request,[{'id':'a','text':source}],provider='anthropic')
    prepared=prepare_span_draft(request,original)
    wrong=claim('The rules permit work with Board consent.',quote=source)
    selected=select_response({'status':'answered','paragraphs':[wrong]},json.loads(prepared.messages[-1]['content']))
    answer=normalize_span_draft(json.dumps(selected),prepared)
    assert answer['paragraphs'][0]['text']==wrong['text']
    # Explicit semantic negative: date and mandatory design condition omitted.
    # Mechanical acceptance is not a reviewed factual or legal accuracy pass.


@pytest.mark.parametrize('change',['missing_support','missing_year','cross_source'])
def test_paragraph_draft_keeps_existing_publication_guards(change):
    from tests.research.test_source_publication import dated_evidence,dated_unit
    evidence=dated_evidence()+[{'id':'other','text':'An unrelated source.',
                              'source_date_metadata':[{'field':'datePublished','value':'2025'}]}]
    request=ChatRequest(question='What did the survey record?')
    prepared=prepare_span_draft(request,prepare_answer(request,evidence,provider='anthropic'))
    native=select_response({'status':'answered','paragraphs':[dated_unit()]},json.loads(prepared.messages[-1]['content']))
    assert normalize_span_draft(json.dumps(native),prepared)['status']=='answered'
    unit=native['paragraph_1']
    if change=='missing_support':unit['supports']=[]
    elif change=='missing_year':unit['text']=unit['text'].replace('2025','an unspecified year')
    else:unit['supports'][0]['citation_id']='other'
    with pytest.raises(ValueError):normalize_span_draft(json.dumps(native),prepared)


def test_paragraph_draft_cannot_omit_required_header_text_support():
    header={'id':'header','text':'Table: Species and regional occurrence.'}
    row={'id':'a','text':'Species A occurs in Region B.','supporting_context':[header]}
    request=ChatRequest(question='What is recorded?')
    prepared=prepare_span_draft(request,prepare_answer(request,[row],provider='anthropic'))
    payload=json.loads(prepared.messages[-1]['content'])
    unit=claim('Species A occurs in Region B.',quote=row['text'])
    selected=select_response({'status':'answered','paragraphs':[unit]},payload)
    with pytest.raises(ValueError):normalize_span_draft(json.dumps(selected),prepared)
    unit['supports']=[{'citation_id':'header','field':'text','quote':header['text']}]
    selected=select_response({'status':'answered','paragraphs':[unit]},payload)
    assert normalize_span_draft(json.dumps(selected),prepared)['status']=='answered'


def test_exact_independently_reviewed_wire_instruction_hashes_are_pinned():
    from backend.span_instructions import span_answer_instructions
    record=json.loads((Path(__file__).parents[2]/'docs/research-slot-instruction-parity.json').read_text())
    for phase,styles in record['rendered_instructions'].items():
        for style,pin in styles.items():
            actual=span_answer_instructions(phase,style).encode()
            assert len(actual)==pin['utf8_bytes']
            assert hashlib.sha256(actual).hexdigest()==pin['sha256']
