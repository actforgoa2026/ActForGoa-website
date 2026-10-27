"""Versioned extraction. Original bytes and native text are never overwritten."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile
from lxml import etree
import pymupdf
from bs4 import BeautifulSoup

VERSION = 'layout-ocr-docx-v2'

def text_quality_warning(text):
    if not text:return ''
    bad=sum(c=='\ufffd' or (ord(c)<32 and c not in '\n\r\t') for c in text)
    return 'Corrupted character extraction; excluded from search. Inspect the original file.' if bad/len(text)>.02 else ''

def digest(value):
    return hashlib.sha256(value).hexdigest()

def safe_path(root, relative):
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve() / 'corpus'):
        raise ValueError('File outside corpus')
    return path

def extract_docx(path):
    """Preserve body/table order and include headers, footers, footnotes and endnotes."""
    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    parts = []
    with zipfile.ZipFile(path) as archive:
        names = ['word/document.xml'] + sorted(n for n in archive.namelist() if
            n.startswith(('word/header', 'word/footer', 'word/footnotes', 'word/endnotes')) and n.endswith('.xml'))
        for name in names:
            tree = etree.fromstring(archive.read(name), parser=etree.XMLParser(resolve_entities=False, no_network=True))
            paragraphs = [''.join(p.xpath('.//w:t/text()', namespaces=namespace)) for p in tree.xpath('//w:p', namespaces=namespace)]
            parts.append({'page':len(parts)+1, 'label':Path(name).stem, 'text':'\n'.join(paragraphs),
                          'origin':'docx_xml', 'warning':'Sections, not physical Word page numbers. Table cells follow document order.'})
    return parts

def extract_source(root, metadata, improve=False, ocr_budget=None):
    raw = safe_path(root, metadata['raw_path'])
    # Existing corpus metadata is not sufficient proof of the file's identity.
    raw_bytes = raw.read_bytes()
    raw_hash = digest(raw_bytes)
    if raw_hash != metadata['sha256']:
        raise ValueError('Original checksum mismatch')
    # Some historical servers wrapped PDF bytes in a short HTML preface.
    if metadata.get('format')!='pdf' and 0<=raw_bytes.find(b'%PDF-')<1024:
        metadata['format']='pdf'
        metadata['format_detection']='PDF signature within first 1024 bytes; parsed as PDF'
        improve=True
    cache = Path(root) / 'corpus' / 'extracted' / f'{raw_hash}-{VERSION}.json'
    if improve and cache.exists():
        pages = json.loads(cache.read_text())
        extraction_hash = digest(json.dumps(pages, sort_keys=True, ensure_ascii=False).encode())
        return raw_hash[:24]+'-'+extraction_hash[:12], pages
    ocr = {}
    if metadata.get('ocr_pages_path'):
        ocr = {p['page']:p for p in json.loads(safe_path(root, metadata['ocr_pages_path']).read_text())}
    if metadata.get('format') == 'html':
        soup=BeautifulSoup(raw_bytes,'lxml')
        for element in soup.select('script,style,noscript,nav,header,footer,form,svg,[role=navigation],.site-header,.site-footer,.breadcrumb,.breadcrumbs'):
            element.decompose()
        main=None
        for selector in ['.node .content','.field-name-body','.field--name-body','.entry-content','article','main','[role=main]','#content']:
            found=soup.select(selector)
            if len(found)==1 and len(found[0].get_text(strip=True))>60:
                main=found[0];break
        if main is None:
            content=soup.select('.content')
            main=content[0] if len(content)==1 else soup.body or soup
        pages=[{'page':1,'label':'Document text','text':main.get_text('\n',strip=True),'origin':'html_main_content',
                'warning':'Webpage extraction may contain only an abstract or index; it is not proof of full article access.'}]
    elif metadata.get('format') == 'docx':
        pages = extract_docx(raw)
    elif metadata.get('format') == 'pdf' and improve:
        pages = []
        with pymupdf.open(stream=raw_bytes,filetype='pdf') as document:
            if document.needs_pass:
                raise ValueError('Password protected PDF')
            for number, page in enumerate(document, 1):
                text = page.get_text('text', sort=True)
                origin = 'pymupdf_reading_order'
                warning = ''
                if len(text.strip()) < 60 and number in ocr:
                    text = ocr[number]['text']; origin = 'ocr_eng_unverified'
                if len(text.strip()) < 60 and ocr_budget and ocr_budget[0] > 0:
                    ocr_budget[0] -= 1
                    try:
                        with tempfile.TemporaryDirectory(prefix='actforgoa-ocr-') as tmp:
                            image = Path(tmp) / 'page.png'
                            page.get_pixmap(dpi=150, colorspace=pymupdf.csGRAY).save(image)
                            result = subprocess.run(['tesseract',str(image),'stdout','-l','eng','--psm','3'],
                                capture_output=True,text=True,check=True,timeout=60,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
                            if len(result.stdout.strip()) > len(text.strip()):
                                text=result.stdout;origin='ocr_eng_unverified'
                    except (OSError, subprocess.SubprocessError):
                        warning='OCR failed; inspect the original page.'
                if len(text.strip()) < 60:
                    warning = warning or 'Little extractable text; this may be a scan, map, image or blank page.'
                if origin == 'ocr_eng_unverified':
                    warning = 'Machine OCR in English, not manually verified. Check the original for numbers and names.'
                pages.append({'page':number,'label':f'PDF page {number}','text':text,'origin':origin,'warning':warning})
    elif metadata.get('pages_path'):
        pages = json.loads(safe_path(root, metadata['pages_path']).read_text())
        for page in pages:
            page['origin']='native_extraction';page['label']=f"PDF page {page['page']}"
            if len(page['text'].strip()) < 60 and page['page'] in ocr:
                page['text']=ocr[page['page']]['text'];page['origin']='ocr_eng_unverified'
            page['warning'] = ('Machine OCR in English, not manually verified.' if page['origin'].startswith('ocr') else
                'Little extractable text; inspect the original.' if len(page['text'].strip())<60 else '')
    else:
        text = safe_path(root, metadata['text_path']).read_text() if metadata.get('text_path') else ''
        pages = [{'page':1,'label':'Document text','text':text,'origin':'html_text' if metadata.get('format')=='html' else 'native_extraction',
                  'warning':'Webpage extraction may contain only an abstract or index; it is not proof of full article access.' if metadata.get('format')=='html' else ''}]
    extraction_hash = digest(json.dumps(pages, sort_keys=True, ensure_ascii=False).encode())
    if improve:
        cache.parent.mkdir(parents=True, exist_ok=True)
        temporary = cache.with_suffix('.tmp')
        temporary.write_text(json.dumps(pages, ensure_ascii=False))
        temporary.replace(cache)
    return raw_hash[:24]+'-'+extraction_hash[:12], pages
