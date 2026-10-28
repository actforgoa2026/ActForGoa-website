import hashlib
import json
from pathlib import Path
import pymupdf
import pytest
from backend.library import Library
from scripts.build_research_index import build
import scripts.refresh_verified_legal_sources as refresh


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


@pytest.fixture
def roots(tmp_path, monkeypatch):
    base, source = tmp_path/'base', tmp_path/'source'
    metadata = []
    for name, text in [('water','Khazan sluice gates control tidal water entering agricultural fields.'), ('sop','')]:
        pdf = pymupdf.open(); page = pdf.new_page()
        if text: page.insert_text((40,60), text)
        raw = pdf.tobytes(); pdf.close()
        digest = hashlib.sha256(raw).hexdigest()
        path = f'corpus/raw/{digest}.pdf'
        (base/path).parent.mkdir(parents=True,exist_ok=True); (base/path).write_bytes(raw)
        item = {'id':name,'url':f'https://example.org/{name}.pdf','title':name,'format':'pdf','status':'downloaded','sha256':digest,'raw_path':path}
        write_json(base/f'corpus/metadata/{name}.json',item); metadata.append(item)
    write_json(base/'corpus/ecology-seeds.json',[{'url':m['url']} for m in metadata])
    manifest = build(base,ocr_pages=0)
    sop = metadata[1].copy()
    sop['ocr_pages_path'] = 'corpus/ocr/sop.json'
    (source/sop['raw_path']).parent.mkdir(parents=True,exist_ok=True)
    (source/sop['raw_path']).write_bytes((base/sop['raw_path']).read_bytes())
    write_json(source/sop['ocr_pages_path'],[{'page':1,'text':'Official institutional animal handling guidance requires authorised personnel and shelter arrangements.'}])
    write_json(source/'corpus/metadata/sop.json',sop)
    article = 'Official statement about electronic reporting and the statutory signature requirement.'
    html = f'<html><body><form><div class="innner-page-main-about-us-content-right-part">{article}</div></form></body></html>'.encode()
    digest = hashlib.sha256(html).hexdigest(); path=f'corpus/raw/{digest}.html'
    (source/path).write_bytes(html)
    pib = {'id':'pib','url':'https://example.org/release','title':'release','format':'html','status':'downloaded','sha256':digest,'raw_path':path}
    write_json(source/'corpus/metadata/pib.json',pib)
    entries=[]
    for citation,item in [('V16',sop),('V15',pib)]:
        entries.append({**item,'citation':citation,'review_date_local':'2026-10-23','review_timezone':'Asia/Kolkata','location':'Test source locator','limitations':'Fixture; not real law.',
            'text_sha256':hashlib.sha256(article.encode()).hexdigest(),
            'ocr_sha256':refresh.sha(source/sop['ocr_pages_path']) if citation=='V16' else None})
    write_json(source/refresh.REGISTER,entries)
    monkeypatch.setattr(refresh,'KINDS',{'V16':'official_procedure','V15':'official_press_statement'})
    return base, source, manifest['generation']


def test_refresh_recovers_form_wrapped_articles_and_ocr_without_breaking_old_citations(roots,tmp_path):
    base,source,old_generation=roots
    old=Library(base)
    water=old.search('khazan water gates')[0]
    original_hash=refresh.sha(base/f'.research-index/generations/{old_generation}/library.sqlite')
    output=tmp_path/'refreshed'
    report=refresh.refresh(base,source,output)
    new=Library(output)
    assert new.generation!=old_generation
    assert report['stats']['documents']==3
    assert all(o['searchable_passages']>0 for o in report['outcomes'])
    assert new.search('electronic reporting signature')[0]['title']=='release'
    ocr=next(o for o in report['outcomes'] if o['citation']=='V16')
    assert ocr['outcome']=='existing_original_ocr_refreshed'
    assert new.pages(ocr['document_id'])[0]['origin'].startswith('ocr')
    assert new.pages(ocr['previous_document_id'],old_generation)[0]['text']==''
    assert new.pages(water['document_id'],old_generation)[0]['text']==old.pages(water['document_id'])[0]['text']
    assert new.original(water['document_id'],old_generation)[0].is_file()
    assert refresh.sha(base/f'.research-index/generations/{old_generation}/library.sqlite')==original_hash
    with pytest.raises(ValueError,match='isolated'):
        refresh.refresh(base,source,output)


def test_bad_verified_bytes_do_not_publish_a_generation(roots,tmp_path):
    base,source,old_generation=roots
    entries=json.loads((source/refresh.REGISTER).read_text())
    entries[0]['sha256']='0'*64
    write_json(source/refresh.REGISTER,entries)
    output=tmp_path/'rejected'
    with pytest.raises(ValueError,match='checksum'):
        refresh.refresh(base,source,output)
    assert not (output/'.research-index/CURRENT.json').exists()
    assert json.loads((base/'.research-index/CURRENT.json').read_text())['generation']==old_generation
