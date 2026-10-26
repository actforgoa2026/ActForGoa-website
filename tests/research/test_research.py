import hashlib
import json
from pathlib import Path
import zipfile
import subprocess
import sys
import tarfile
import httpx
from fastapi.testclient import TestClient
from openai import OpenAI
import pymupdf
import pytest
from backend.app import create_app
from backend.chat import GroundedAnswer, Paragraph, validate_answer
from backend.extraction import extract_docx, extract_source, safe_path
from backend.library import Library
from scripts.build_research_index import build

@pytest.fixture(scope='module')
def collection(tmp_path_factory):
    root=tmp_path_factory.mktemp('research')
    for folder in ['raw','metadata','pages','text']:(root/'corpus'/folder).mkdir(parents=True)
    sources=[('water','Khazan water management','The khazan fields manage saline tidal water through sluice gates and protective bunds. Freshwater comes from monsoon rainfall.'),
             ('wildlife','Goa endemic gecko study','Cnemaspis goaensis is a gecko described from Goa. This taxonomy study discusses lizards and rocky habitats.'),
             ('plateau','Laterite aquifer study','Laterite plateaus absorb seasonal rainfall. Groundwater emerges as springs along the contact between permeable laterite and underlying rock.')]
    for sid,title,text in sources:
        pdf=pymupdf.open()
        for page_text in [text,'Final page of '+title+'. The complete document includes this last page.']:
            page=pdf.new_page();page.insert_text((40,60),page_text,fontsize=10)
        raw=pdf.tobytes();pdf.close();checksum=hashlib.sha256(raw).hexdigest();relative=f'corpus/raw/{checksum}.pdf';(root/relative).write_bytes(raw)
        meta={'id':sid,'url':f'https://example.org/{sid}.pdf','title':title,'status':'downloaded','sha256':checksum,'raw_path':relative,'format':'pdf','publisher_class':'research','retrieved_at':'2026-10-22T00:00:00Z'}
        (root/'corpus/metadata'/f'{sid}.json').write_text(json.dumps(meta))
    (root/'corpus/ecology-seeds.json').write_text(json.dumps([{'url':f'https://example.org/{sid}.pdf'} for sid,_,_ in sources]))
    manifest=build(root,ocr_pages=0)
    return root,manifest

def test_real_hybrid_search_and_complete_document(collection):
    root,manifest=collection;lib=Library(root)
    found=lib.search('khazan sluice gates salt water')
    assert found and found[0]['title']=='Khazan water management'
    assert set(found[0]['matches'])=={'keyword','semantic'}
    assert found[0]['publisher_class']=='research'
    assert {'legal_currency','source_date_metadata','topics'}<=found[0].keys()
    pages=lib.pages(found[0]['document_id'])
    assert len(pages)==2 and 'Final page' in pages[-1]['text']
    assert found[0]['text']==pages[0]['text'][found[0]['start']:found[0]['end']]
    assert found[0]['page_context']==pages[0]['text'][:1400]
    assert lib.search('springs rainfall laterite')[0]['title']=='Laterite aquifer study'
    assert len(lib.search('gecko',doc_id=found[0]['document_id']))<=4
    assert manifest['stats']['documents']==3

@pytest.mark.parametrize('staged',[True,False])
def test_release_package_reopens_zvec_and_keeps_only_indexed_originals(collection,tmp_path,staged):
    root,_=collection
    (root/'corpus/raw/unindexed.txt').write_text('Not part of the published collection')
    (root/'.env.local').write_text('UNRELATED_LOCAL_SETTING=fixture-only\n')
    script=Path(__file__).resolve().parents[2]/'scripts/package_research.py'
    command=[sys.executable,str(script),'--data-root',str(root),'--output',str(tmp_path/'package')]
    if staged:command.append('--stage-data')
    report=json.loads(subprocess.check_output(command,text=True))
    if staged:published=Path(report['directory'])
    else:
        with tarfile.open(report['archive']) as archive:archive.extractall(tmp_path/'unpacked',filter='data')
        published=tmp_path/'unpacked/research'
    library=Library(published)
    hit=library.search('khazan saline sluice gates')[0]
    assert hit['title']=='Khazan water management'
    original,meta=library.original(hit['document_id'])
    assert hashlib.sha256(original.read_bytes()).hexdigest()==meta['sha256']
    assert not (published/'corpus/raw/unindexed.txt').exists()
    assert not (published/'.env.local').exists()

def test_document_endpoints_and_original_checksum(collection):
    root,_=collection
    with TestClient(create_app(root)) as client:
        result=client.get('/api/search',params={'q':'khazan saline'}).json()['results'][0]
        doc=client.get('/api/documents/'+result['document_id']).json()
        raw=client.get(doc['original_url']);assert raw.status_code==200
        assert hashlib.sha256(raw.content).hexdigest()==doc['sha256']
        assert raw.headers['content-type']=='application/pdf'
        assert raw.headers['content-disposition'].startswith('attachment')
        image=client.get('/api/documents/'+doc['id']+'/pages/2/image')
        assert image.status_code==200 and image.content.startswith(b'\x89PNG')
        assert client.get('/api/documents/'+doc['id']+'/pages/999/image').status_code==404
        assert 'Final page' in client.get(doc['text_url']).text
        assert client.get('/api/documents/'+doc['id']+'/pages',params={'start':2}).json()['pages'][0]['page']==2
        assert client.get('/api/documents/'+doc['id'],params={'generation':'../../secret'}).status_code==404
        assert client.get('/api/documents/does-not-exist').status_code==404
        assert client.get('/api/search',params={'q':'x','limit':1000}).status_code==422
        assert client.post('/api/chat',json={'question':'khazan?'},headers={'origin':'https://evil.example'}).status_code==403
        assert client.get('/api/status',headers={'host':'evil.example'}).status_code==400

def test_missing_credential_keeps_search_working(collection,monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','openrouter')
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    with TestClient(create_app(collection[0])) as client:
        assert client.get('/api/status').json()['chat_ready'] is False
        assert client.post('/api/chat',json={'question':'How do sluice gates work?'}).status_code==503
        assert client.get('/api/search',params={'q':'sluice'}).json()['results']

def test_responses_sdk_citation_contract(collection,monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','openai')
    monkeypatch.setenv('OPENAI_CHAT_MODEL','gpt-5-mini')
    captured=[]
    def provider(request):
        body=json.loads(request.content);captured.append(body)
        payload=json.loads(body['input'][-1]['content']);evidence=payload['evidence'][0]
        output={'status':'answered','paragraphs':[{'text':evidence['text'],'citations':[evidence['id']]}]}
        return httpx.Response(200,json={'id':'resp_test','object':'response','created_at':1,'status':'completed','model':'gpt-5-mini','output':[{'type':'message','id':'msg_test','role':'assistant','status':'completed','content':[{'type':'output_text','text':json.dumps(output),'annotations':[]}]}]})
    model=OpenAI(api_key='test-fixture-only',http_client=httpx.Client(transport=httpx.MockTransport(provider)))
    with TestClient(create_app(collection[0],client=model)) as client:
        response=client.post('/api/chat',json={'question':'How do khazan sluice gates manage saline water?'})
        assert response.status_code==200,response.text
        answer=response.json();assert answer['status']=='answered'
        assert captured[0]['store'] is False
        assert captured[0]['text']['format']['type']=='json_schema'
        for cite in answer['citations']:
            meta=client.get('/api/documents/'+cite['document_id'],params={'generation':cite['generation']});assert meta.status_code==200
            pages=client.get('/api/documents/'+cite['document_id']+'/pages',params={'start':cite['page'],'generation':cite['generation']}).json()['pages']
            assert cite['text'] in pages[0]['text']
            assert client.get(meta.json()['original_url']).status_code==200
    model.close()

def test_fabricated_and_missing_citations_are_rejected():
    evidence=[{'id':'known'}]
    for citations in [[],['invented']]:
        with pytest.raises(ValueError):validate_answer(GroundedAnswer(status='answered',paragraphs=[Paragraph(text='A claim',citations=citations)]),evidence)
    assert validate_answer(GroundedAnswer(status='insufficient_evidence',paragraphs=[]),evidence)['citations']==[]

def test_no_page_text_is_lost_to_embedding_limit(collection):
    lib=Library(collection[0]);text='Rain falls on the plateau. '*600+' FINAL SENTENCE.'
    chunks=list(lib.encoder.chunks(text))
    assert chunks[0][0]==0 and chunks[-1][1]==len(text)
    assert 'FINAL SENTENCE.' in chunks[-1][2]
    assert all(a[1]>=b[0] for a,b in zip(chunks,chunks[1:]))

def test_exact_semantic_match_is_retained_not_filtered_as_low_score(collection):
    import zvec
    lib=Library(collection[0]);hit=lib.search('khazan sluice')[0]
    vector=lib.encoder.encode([hit['text']])[0].tolist()
    nearest=lib.vectors.query(queries=zvec.Query('embedding',vector=vector),topk=1)[0]
    assert nearest.score<0.01
    exact=lib.search(hit['text'])[0]
    assert exact['id']==nearest.id and 'semantic' in exact['matches']
    assert lib.search('zqxvtrnjkwq')==[]

def test_docx_tables_headers_and_notes(tmp_path):
    file=tmp_path/'document.docx';ns='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    with zipfile.ZipFile(file,'w') as archive:
        for name,text in [('document','River table cell'),('header1','Header evidence'),('footnotes','Footnote evidence')]:
            archive.writestr('word/'+name+'.xml',f'<w:document xmlns:w="{ns}"><w:body><w:tbl><w:tr><w:tc><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>')
    pages=extract_docx(file);assert len(pages)==3
    assert 'River table cell' in pages[0]['text']
    assert {'Header evidence','Footnote evidence'} <= {p['text'] for p in pages}
    with pytest.raises(ValueError):safe_path(tmp_path,'../../etc/passwd')

def test_generation_keeps_old_citations_resolvable(collection):
    root,manifest=collection;old=Library(root).search('khazan water')[0]
    second=build(root,ocr_pages=0)
    assert second['generation']!=manifest['generation']
    new=Library(root)
    assert new.document(old['document_id'],old['generation'])['id']==old['document_id']
    assert new.search('khazan water')[0]['id']==old['id']

def test_updated_original_does_not_break_saved_version(collection):
    root,_=collection;old=Library(root).search('khazan water')[0]
    meta_path=root/'corpus/metadata/water.json';meta=json.loads(meta_path.read_text())
    with pymupdf.open(root/meta['raw_path']) as pdf:
        page=pdf.new_page();page.insert_text((40,60),'New edition of the khazan water study. Added observation.',fontsize=10)
        raw=pdf.tobytes()
    checksum=hashlib.sha256(raw).hexdigest();meta.update(sha256=checksum,raw_path=f'corpus/raw/{checksum}.pdf')
    (root/meta['raw_path']).write_bytes(raw);meta_path.write_text(json.dumps(meta))
    build(root,ocr_pages=0);lib=Library(root)
    assert lib.document(old['document_id'],old['generation'])['page_count']==2
    updated=lib.search('khazan water')[0]
    assert updated['document_id']!=old['document_id']
    assert lib.document(updated['document_id'])['page_count']==3
    assert lib.search('khazan',doc_id=old['document_id'],generation=old['generation'])[0]['document_id']==old['document_id']

def test_html_prefaced_pdf_is_recovered_as_pdf(tmp_path):
    (tmp_path/'corpus/raw').mkdir(parents=True)
    with pymupdf.open() as pdf:
        page=pdf.new_page();page.insert_text((40,60),'Dust mitigation guidance: cover construction material.')
        raw=b'<html><head></head></html>\r\n'+pdf.tobytes()
    checksum=hashlib.sha256(raw).hexdigest();path='corpus/raw/wrapped.pdf';(tmp_path/path).write_bytes(raw)
    meta={'format':'html','raw_path':path,'sha256':checksum}
    _,pages=extract_source(tmp_path,meta)
    assert meta['format']=='pdf' and len(pages)==1
    assert 'Dust mitigation' in pages[0]['text']

def test_main_content_excludes_government_footer_navigation(tmp_path):
    (tmp_path/'corpus/raw').mkdir(parents=True)
    raw=b'<html><body><nav>State water policy rivers rainfall</nav><div class="node"><div class="content"><p>This document explains external links and their ownership, without water measurements or policy provisions.</p></div></div><div>State Water Department Footer</div></body></html>'
    (tmp_path/'corpus/raw/page.html').write_bytes(raw)
    _,pages=extract_source(tmp_path,{'format':'html','raw_path':'corpus/raw/page.html','sha256':hashlib.sha256(raw).hexdigest()})
    assert 'external links' in pages[0]['text'] and 'Footer' not in pages[0]['text'] and 'rainfall' not in pages[0]['text']

def test_corrupted_text_is_flagged_for_search_exclusion():
    from backend.extraction import text_quality_warning
    assert text_quality_warning('abc\ufffd\ufffd\ufffd\x01')
    assert not text_quality_warning('Goa’s rivers include the Mandovi.\nRainfall: 2,900 mm.')


def test_openrouter_chat_citations_documents_followup_and_cache(collection,monkeypatch):
    from tests.research.test_chat_controls import completion
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','openrouter')
    captured=[]
    def provider(request):
        body=json.loads(request.content);captured.append(body)
        evidence=json.loads(body['messages'][-1]['content'])['evidence'][0]
        return httpx.Response(200,json=completion(json.dumps({'status':'answered','paragraphs':[
            {'text':evidence['text'],'citations':[evidence['id']]}]})))
    with OpenAI(api_key='fixture-only',base_url='https://openrouter.ai/api/v1',max_retries=0,
                http_client=httpx.Client(transport=httpx.MockTransport(provider))) as model:
        with TestClient(create_app(collection[0],client=model)) as client:
            question='How do khazan gates regulate saline water?'
            first=client.post('/api/chat',json={'question':question})
            assert first.status_code==200,first.text
            answer=first.json()
            assert client.post('/api/chat',json={'question':question}).json()==answer and len(captured)==1
            for cite in answer['citations']:
                doc=client.get('/api/documents/'+cite['document_id'],params={'generation':cite['generation']}).json()
                assert hashlib.sha256(client.get(doc['original_url']).content).hexdigest()==doc['sha256']
                text=client.get(doc['text_url']);assert text.status_code==200 and 'Final page' in text.text
                pages=client.get('/api/documents/'+cite['document_id']+'/pages',params={'start':cite['page'],'generation':cite['generation']}).json()['pages']
                assert cite['text'] in pages[0]['text']
            followup={'question':'And during the monsoon?','history':[
                {'role':'user','content':question},{'role':'assistant','content':answer['paragraphs'][0]['text']}]}
            assert client.post('/api/chat',json=followup).status_code==200
            assert client.post('/api/chat',json=followup).status_code==200
            assert len(captured)==3
            assert captured[-1]['messages'][1:3]==followup['history']
            cite=answer['citations'][0]
            scoped=client.post('/api/chat',json={'question':question,'document_id':cite['document_id'],'generation':cite['generation']})
            assert scoped.status_code==200
            assert all(c['document_id']==cite['document_id'] for c in scoped.json()['citations'])


@pytest.mark.parametrize('failure',['401','402','429','timeout','bad-citation'])
def test_provider_failure_is_safe_not_retried_or_cached_and_reservation_persists(collection,monkeypatch,failure):
    import sqlite3
    from tests.research.test_chat_controls import completion
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','openrouter')
    count=[0]
    def provider(request):
        count[0]+=1
        if failure=='timeout':raise httpx.ReadTimeout('private diagnostic',request=request)
        if failure=='bad-citation':
            return httpx.Response(200,json=completion(json.dumps({'status':'answered','paragraphs':[
                {'text':'Unsupported','citations':['invented']}]})))
        return httpx.Response(int(failure),json={'error':{'message':'private diagnostic','type':'failure'}})
    with sqlite3.connect(collection[0]/'.research-usage/answer-usage.sqlite') as db:
        before=db.execute('SELECT SUM(reserved_microusd) FROM spend').fetchone()[0]
    with OpenAI(api_key='fixture-only',max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(provider))) as model:
        with TestClient(create_app(collection[0],client=model)) as client:
            for _ in range(2):
                response=client.post('/api/chat',json={'question':'What controls khazan tidal water?'})
                assert response.status_code==502
                assert 'private diagnostic' not in response.text and 'fixture-only' not in response.text
            assert count[0]==2
            assert client.get('/api/search',params={'q':'khazan'}).status_code==200
    with sqlite3.connect(collection[0]/'.research-usage/answer-usage.sqlite') as db:
        assert db.execute('SELECT SUM(reserved_microusd) FROM spend').fetchone()[0]>before


def test_exhausted_budget_does_not_call_provider(collection,monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','openrouter')
    monkeypatch.setenv('RESEARCH_MONTHLY_ANSWER_BUDGET_USD','0')
    def provider(_):raise AssertionError('A depleted budget must prevent dispatch')
    with OpenAI(api_key='fixture-only',http_client=httpx.Client(transport=httpx.MockTransport(provider))) as model:
        with TestClient(create_app(collection[0],client=model)) as client:
            assert client.post('/api/chat',json={'question':'How do khazan sluice gates work?'}).status_code==429
            assert client.get('/api/search',params={'q':'khazan'}).json()['results']


def test_service_only_package_does_not_require_or_replace_corpus(tmp_path):
    output=tmp_path/'release';service=output/'service';service.mkdir(parents=True)
    (service/'stale-secret.env').write_text('fixture that must not survive regeneration')
    data=output/'data';data.mkdir();(data/'keep.txt').write_text('existing volume package')
    script=Path(__file__).resolve().parents[2]/'scripts/package_research.py'
    report=json.loads(subprocess.check_output([sys.executable,str(script),'--service-only',
        '--data-root',str(tmp_path/'not-present'),'--output',str(output)],text=True))
    assert (Path(report['service'])/'backend/providers.py').exists()
    assert not (service/'stale-secret.env').exists()
    assert (data/'keep.txt').read_text()=='existing volume package'
