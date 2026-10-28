"""Real Zvec domain retrieval and fixture-only Anthropic/provider checks."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import httpx
import pytest
from fastapi.testclient import TestClient
from backend.anthropic_answers import AnthropicAnswers, AnthropicAPIError, maximum_cost
from backend.app import create_app
from backend.chat import ChatRequest, normalize_answer, prepare_answer
from backend.library import Library
from scripts.build_research_index import build
from scripts.ingest_legal_guides import ingest, GUIDES


@pytest.fixture(scope='module')
def section_library(tmp_path_factory):
    root=tmp_path_factory.mktemp('sections')
    guides=root/'guides';guides.mkdir()
    for filename, (slug, title, domains) in GUIDES.items():
        (guides/filename).write_text(f'# {title}\n\nThis authored draft explains {slug}. A permission enquiry should identify the responsible office. Check the official current procedure before acting.\n')
    ingest(root, guides)
    # A real ecological document alongside the authored legal guides.
    text='Mangrove forests protect tidal habitat. These wetland trees are adapted to saline water.'
    digest=hashlib.sha256(text.encode()).hexdigest();raw=f'corpus/raw/{digest}.txt';(root/raw).write_text(text)
    (root/'corpus/metadata/mangrove.json').write_text(json.dumps({'id':'mangrove','title':'Mangrove ecology','url':'https://example.org/mangrove','raw_path':raw,'text_path':raw,'format':'text','status':'downloaded','sha256':digest,'domains':['ecology']}))
    build(root,ocr_pages=0)
    return root


def test_domain_filters_apply_to_both_hybrid_channels_before_ranking(section_library):
    lib=Library(section_library)
    assert lib.domain_counts()=={'legal':5,'ecology':4}
    legal=lib.search('permission responsible office',domain='legal')
    assert legal and all('legal' in result['domains'] for result in legal)
    assert any(set(result['matches'])=={'keyword','semantic'} for result in legal)
    ecological=lib.search('mangrove tidal habitat',domain='ecology')
    assert ecological[0]['title']=='Mangrove ecology'
    assert lib.search('mangrove tidal habitat',doc_id=ecological[0]['document_id'],domain='legal')==[]
    assert 'draft' in legal[0]['legal_currency']
    assert 'not primary legislation' in lib.document(legal[0]['document_id'])['legal_currency']


def test_section_api_echoes_scope_and_unsupported_domains_fail(section_library,monkeypatch):
    monkeypatch.delenv('ANTHROPIC_API_KEY',raising=False)
    with TestClient(create_app(section_library)) as client:
        status=client.get('/api/status').json()
        assert status['provider']=='anthropic' and status['domain_counts']['legal']==5
        assert not status['chat_ready']
        response=client.get('/api/search',params={'q':'permission office','domain':'legal'})
        assert response.status_code==200 and response.json()['domain']=='legal'
        assert all('legal' in item['domains'] for item in response.json()['results'])
        assert client.get('/api/search',params={'q':'permission','domain':'invented'}).status_code==422
        assert client.post('/api/chat',json={'question':'permission','domain':'invented'}).status_code==422


def example():
    evidence=[{'id':'source-1','text':'A permit may be required. Ask the responsible authority to confirm the current procedure.', 'legal_currency':'Historical draft; not consolidated current law.'}]
    raw={'coverage':'partial','paragraph_1':{'text':'The draft says a permit may be required; confirm the current procedure with the responsible authority.', 'supports':['source-1']},'paragraph_2':None,'paragraph_3':None,'paragraph_4':None,'paragraph_5':None,
         'outside_context':'You can prepare a short description of your planned work before asking for guidance.', 'limitation':'The library does not establish which permit applies to your site.'}
    return evidence,raw


def test_library_and_outside_answers_have_distinct_provenance():
    evidence,raw=example();request=ChatRequest(question='What permission applies?',domain='legal')
    result=normalize_answer(raw,request,evidence)
    assert result['paragraphs'][0]['citations']==['source-1']
    assert result['outside_context']['provenance']=='model_knowledge'
    assert 'not checked' in result['outside_context']['notice']
    assert result['domain']=='legal' and result['coverage']=='partial'
    assert 'outside_context' not in result['paragraphs'][0]


@pytest.mark.parametrize('corruption',['unknown_citation','fabricated_quote','full_with_outside','no_evidence_with_claim','outside_disabled','invented_link'])
def test_answer_contract_rejects_provenance_mixing(corruption):
    evidence,raw=example();request=ChatRequest(question='What permission applies?',domain='legal')
    if corruption=='unknown_citation':raw['paragraph_1']['supports'][0]='fabricated'
    if corruption=='fabricated_quote':raw['paragraph_1']['supports'][0]={'citation_id':'source-1','quote':'The permit is always required.'}
    if corruption=='full_with_outside':raw['coverage']='full'
    if corruption=='no_evidence_with_claim':raw['coverage']='none'
    if corruption=='outside_disabled':request.include_outside_context=False
    if corruption=='invented_link':raw['outside_context']='See https://invented.example/source.'
    with pytest.raises(ValueError):normalize_answer(raw,request,evidence)


def test_step_by_step_explanation_has_room_without_losing_citations():
    # A synthetic source and its four supported steps, not model-quality evidence.
    steps = [
        "1. Start by writing down what you want to do and where you plan to do it. Include a simple description of the site and the work you are considering. This helps the office understand your enquiry before deciding which procedure may apply to your situation.",
        "2. Contact the responsible office with that description and ask it to confirm the current procedure. Ask which documents it needs from you and whether any permission is required before you begin. Keep the response with your notes so you can refer to the information later.",
        "3. Gather the documents the office asks for and check that the details match your enquiry. If something is unclear, ask the office to explain it before submitting the application. A missing document or an unclear description may need to be corrected during the enquiry process.",
        "4. Keep a copy of your submitted documents and the acknowledgement you receive. Use the reference on that acknowledgement when following up with the office. An acknowledgement records receipt of your enquiry or application; it does not by itself confirm that permission for the work has been granted.",
    ]
    assert 180 < sum(len(step.split()) for step in steps) < 300
    evidence = [{'id': f'step-{i}', 'text': step} for i, step in enumerate(steps)]
    raw = {'coverage': 'full', **{f'paragraph_{i+1}': {'text': source['text'], 'supports': [source['id']]} for i,source in enumerate(evidence)}, 'paragraph_5': None}
    request = ChatRequest(question='Can you explain those steps in a little more detail?')
    result = normalize_answer(raw, request, evidence)
    assert [paragraph['text'] for paragraph in result['paragraphs']] == steps
    assert [citation['id'] for citation in result['citations']] == [source['id'] for source in evidence]
    assert result['outside_context'] is None
    invalid = deepcopy(raw)
    invalid['paragraph_4']['supports'][0] = 'fabricated'
    with pytest.raises(ValueError, match='supporting source'):
        normalize_answer(invalid, request, evidence)
    # Even fully quoted answers retain a finite size bound; they are not truncated.
    oversized = deepcopy(raw)
    oversized['paragraph_5'] = {'text': ' '.join(steps[:3]), 'supports': ['extra']}
    with pytest.raises(ValueError, match='too long'):
        normalize_answer(oversized, request, evidence + [{'id': 'extra', 'text': ' '.join(steps[:3])}])


def test_no_library_match_is_labeled_and_never_has_fake_citations():
    raw={'coverage':'none','paragraph_1':None,'paragraph_2':None,'paragraph_3':None,'paragraph_4':None,'paragraph_5':None,'outside_context':'Start by describing the location and the activity you want help with.', 'limitation':'No matching information was found in our library.'}
    result=normalize_answer(raw,ChatRequest(question='An uncovered topic?',domain='legal'),[])
    assert result['status']=='insufficient_evidence' and result['citations']==[]
    assert result['outside_context']['text'] and result['library_notice']


def test_provider_failures_are_not_retried_or_credential_leaked():
    calls=[]
    def fail(request):
        calls.append(request)
        return httpx.Response(429,json={'error':'sensitive upstream payload'})
    client=AnthropicAnswers('fixture-secret',httpx.Client(transport=httpx.MockTransport(fail)))
    with pytest.raises(AnthropicAPIError) as error:client.answer('claude-haiku-5-5',{})
    assert len(calls)==1 and error.value.status_code==429
    assert 'sensitive' not in str(error.value) and 'fixture-secret' not in str(error.value)
    client.close()


@pytest.mark.parametrize('reason,content',[
    ('max_tokens',[{'type':'tool_use','name':'answer_library_question','input':{}}]),
    ('refusal',[{'type':'text','text':'Declined'}]),
    ('end_turn',[{'type':'text','text':'Unstructured answer'}]),
    ('tool_use',[]),
    ('tool_use',[{'type':'tool_use','name':'unexpected','input':{}}]),
    ('tool_use',[{'type':'tool_use','name':'answer_library_question','input':{}}]*2),
])
def test_successful_transport_does_not_bypass_answer_contract(reason,content):
    calls=[]
    def provider(request):
        calls.append(request)
        return httpx.Response(200,json={'stop_reason':reason,'content':content})
    client=AnthropicAnswers('fixture',httpx.Client(transport=httpx.MockTransport(provider)))
    try:
        with pytest.raises(ValueError):client.answer('claude-haiku-5-5',{})
        assert len(calls)==1
    finally:client.close()


def test_failed_provider_attempt_stays_reserved_and_daily_budget_survives_restart(section_library,monkeypatch):
    calls=[]
    class FailedProvider:
        def answer(self,*args):
            calls.append(args)
            raise AnthropicAPIError(429)
    monkeypatch.setenv('RESEARCH_DAILY_ANSWER_LIMIT','1')
    # The module fixture has no chat usage yet; only synthetic ledger data is used.
    for expected in [502,429]:
        with TestClient(create_app(section_library,client=FailedProvider())) as client:
            response=client.post('/api/chat',json={'question':'What permission should I check?', 'domain':'legal'})
            assert response.status_code==expected
    assert len(calls)==1
    with sqlite3.connect(section_library/'.research-usage/answer-usage.sqlite') as db:
        assert db.execute('SELECT sum(attempts) FROM usage').fetchone()[0]==1
        assert db.execute('SELECT sum(reserved_microusd) FROM spend').fetchone()[0]>0


def test_preparation_does_not_truncate_source_qualifications():
    evidence,raw=example()
    evidence.append({'id':'too-long','text':'x'*40000+' but this is not mandatory.'})
    payload,selected=prepare_answer(ChatRequest(question='What permission applies?'),evidence)
    assert [entry['id'] for entry in selected]==['source-1']
    assert json.loads(payload['messages'][0]['content'])['evidence'][0]['text']==evidence[0]['text']
    assert maximum_cost('claude-haiku-5-5',payload)>0


@pytest.mark.parametrize('initial',['missing','empty','wrong_schema'])
def test_missing_preserved_usage_ledger_keeps_chat_disabled_but_search_works(section_library,tmp_path,monkeypatch,initial):
    monkeypatch.setenv('ANTHROPIC_API_KEY','fixture-not-a-real-key')
    monkeypatch.setenv('RESEARCH_CHAT_ENABLED','1')
    monkeypatch.setenv('RESEARCH_REQUIRE_EXISTING_USAGE','1')
    path=tmp_path/'.research-usage/answer-usage.sqlite'
    if initial!='missing':
        path.parent.mkdir()
        if initial=='empty':path.touch()
        else:
            with sqlite3.connect(path) as db:db.execute('CREATE TABLE unrelated(value TEXT)')
    before=path.read_bytes() if path.exists() else None
    with TestClient(create_app(tmp_path,index_root=section_library/'.research-index')) as client:
        status=client.get('/api/status').json()
        assert status['search_ready'] and not status['chat_ready']
        assert status['chat_unavailable_reason']==('usage_ledger_missing' if initial=='missing' else 'usage_ledger_unavailable')
        assert client.post('/api/chat',json={'question':'What permission?','domain':'legal'}).status_code==503
    assert (path.read_bytes() if path.exists() else None)==before
    if initial=='missing':assert not path.parent.exists()


def test_no_evidence_with_outside_disabled_never_calls_provider(section_library,tmp_path):
    class NoProviderCall:
        def answer(self,*args):raise AssertionError('No outside context was requested')
    with TestClient(create_app(tmp_path,index_root=section_library/'.research-index',client=NoProviderCall())) as client:
        response=client.post('/api/chat',json={'question':'zqxvtrnjkwq','domain':'legal','include_outside_context':False})
        assert response.status_code==200
        assert response.json()['coverage']=='none' and response.json()['outside_context'] is None
    assert not (tmp_path/'.research-usage').exists()


def test_authored_guide_source_urls_all_resolve_to_canonical_guide_records(tmp_path):
    from urllib.parse import urlsplit
    source_root=Path(__file__).resolve().parents[2]
    canonical={item['id'] for item in json.loads((source_root/'src/content/guides.json').read_text())}
    ingest(tmp_path,source_root/'corpus/guides')
    for metadata in (tmp_path/'corpus/metadata').glob('*.json'):
        source=json.loads(metadata.read_text())
        assert urlsplit(source['url']).path.removeprefix('/read/') in canonical
    assert GUIDES['ENVIRONMENTAL_PROTECTION_GUIDE_DRAFT.md'][0]=='environmental-protection'


@pytest.mark.parametrize('damage',['removed','empty','wrong_schema'])
def test_running_service_detects_lost_required_ledger_and_keeps_search_available(section_library,tmp_path,monkeypatch,damage):
    from backend.hosting import PublicLimits
    monkeypatch.setenv('RESEARCH_REQUIRE_EXISTING_USAGE','1')
    ledger_root=tmp_path/'.research-usage'
    assert PublicLimits(ledger_root).reserve_answer(10)
    path=ledger_root/'answer-usage.sqlite'
    class NoProviderCall:
        def answer(self,*args):raise AssertionError('Unavailable accounting must not dispatch')
    with TestClient(create_app(tmp_path,index_root=section_library/'.research-index',client=NoProviderCall())) as client:
        assert client.get('/api/status').json()['chat_ready']
        path.unlink()
        if damage=='empty':path.touch()
        if damage=='wrong_schema':
            with sqlite3.connect(path) as db:db.execute('CREATE TABLE unrelated(value TEXT)')
        before=path.read_bytes() if path.exists() else None
        status=client.get('/api/status').json()
        assert status['search_ready'] and not status['chat_ready']
        assert status['chat_unavailable_reason']==('usage_ledger_missing' if damage=='removed' else 'usage_ledger_unavailable')
        assert client.post('/api/chat',json={'question':'What permission?','domain':'legal'}).status_code==503
        assert client.get('/api/search',params={'q':'permission','domain':'legal'}).json()['results']
        assert (path.read_bytes() if path.exists() else None)==before


def test_ledger_loss_between_readiness_and_reservation_fails_closed(section_library,tmp_path,monkeypatch):
    from backend.hosting import PublicLimits
    monkeypatch.setenv('RESEARCH_REQUIRE_EXISTING_USAGE','1')
    ledger_root=tmp_path/'.research-usage';assert PublicLimits(ledger_root).reserve_answer(10)
    path=ledger_root/'answer-usage.sqlite'
    original=PublicLimits.reserve_stage
    def disappears(self,*args,**kwargs):
        path.unlink()
        return original(self,*args,**kwargs)
    monkeypatch.setattr(PublicLimits,'reserve_stage',disappears)
    class NoProviderCall:
        def answer(self,*args):raise AssertionError('A missing ledger must never dispatch')
    with TestClient(create_app(tmp_path,index_root=section_library/'.research-index',client=NoProviderCall())) as client:
        assert client.get('/api/status').json()['chat_ready']
        response=client.post('/api/chat',json={'question':'What permission?','domain':'legal'})
        assert response.status_code==503 and not path.exists()
        assert not client.get('/api/status').json()['chat_ready']
