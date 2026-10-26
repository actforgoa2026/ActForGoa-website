"""Read-only, resumable public-source corpus; independent of the website migration.

Run with .venv/bin/python scripts/ingest_goa_corpus.py --help.
Original response bytes, extraction, discovery evidence, and fetch failures stay separate.
"""
from __future__ import annotations
import argparse, concurrent.futures as cf, csv, datetime as dt, hashlib, io, json, logging
import mimetypes, re, sqlite3, threading, time, unicodedata, zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode, unquote
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / 'corpus'
for sub in ['raw', 'text', 'pages', 'metadata', 'logs', 'research']:
    (C / sub).mkdir(parents=True, exist_ok=True)
UA = 'ActForGoaResearch/1.0 (public environmental and civic reference archive; read-only)'
TOPICS = {
 'building_planning_land': r'\b(building|construction|planning|development permission|land use|land revenue|mundkar|comunidade|communidade|tenan|conversion|zoning|zone change|gldbcr|regional plan|panchayat|municipal|heritage|accessibility|rpwd)\w*',
 'agriculture_food': r'\b(agricultur|farm|crop|seed|fertili|insecticide|pesticide|horticultur|organic|nurser|khazan|irrigation|soil|food|livestock|oil palm|coconut|cashew)\w*',
 'animals_wildlife': r'\b(animal|veterinar|cruelty|dog|cattle|wildlife|wild life|sanctuar|rescue|snake|tiger|cow slaughter|bird)\w*',
 'coasts_wetlands_water': r'\b(coast|crz|czmp|wetland|mangrove|river|water|groundwater|ground water|khazan|fishing|fisher|aquaculture|sand mining|flood)\w*',
 'forests_trees_biodiversity': r'\b(forest|tree|biodivers|biological divers|afforestation|conservation|mollem|eco.sensitive|western ghat)\w*',
 'pollution_waste_climate': r'\b(pollution|environment|waste|plastic|noise|sewage|effluent|hazardous|eia|climate|air quality|mining|mineral|sustainab|compost)\w*',
 'reporting_rights_governance': r'\b(complaint|grievance|rti|right to information|legal aid|legal service|tribunal|public hearing|public interest|citizen|gram sabha|forest rights|time.bound|human rights)\w*',
}
DOC = re.compile(r'\.(pdf|docx?|rtf|txt|odt)(?:$|\?)', re.I)
SKIP = re.compile(r'(wp-admin|wp-login|xmlrpc|logout|add-to-cart|replytocom|action~|/feed/|/tag/|/author/|/cart/|/donat|recruitment|vacanc|tender|quotation|requisition|corrigendum.*tender|advertisement.*post|syllabus|salary|seniority|recruit|photogallery|photo-gallery|/gallery/|privacy-policy|terms-and-conditions)', re.I)
HUB = re.compile(r'acts?|rules?|regulation|amendment|notification|gazette|judgment|judgement|legal|publication|resource|guide|charter|rti|complaint|grievance|policy|scheme|manual|permission|download|report|wetland|crz|coast|forest|agricultur|animal|waste|water|biodivers|panchayat|tenancy|land.use|land-revenue|mundkar|community|my-mollem', re.I)
LOCK = threading.Lock()
LOCAL = threading.local()
HOST_LOCKS, ROBOTS = {}, {}
logging.getLogger('pypdf').setLevel(logging.ERROR)

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def dump(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def append(path, value):
    with LOCK:
        with path.open('a') as f: f.write(json.dumps(value, ensure_ascii=False)+'\n')
def canonical(url, base=''):
    p = urlsplit(urljoin(base, url.strip()).replace('&amp;', '&'))
    host=(p.hostname or '').lower()
    if not host or p.scheme not in ['http','https']: return ''
    netloc=host + ((':'+str(p.port)) if p.port and p.port not in [80,443] else '')
    query=urlencode([(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if not k.startswith('utm_') and k not in ['fbclid','gclid']])
    return urlunsplit((p.scheme,netloc,p.path or '/',query,''))
def topic_tags(text): return [k for k,v in TOPICS.items() if re.search(v,text,re.I)]
def official(url):
    h=urlsplit(url).hostname or ''
    return h.endswith(('.gov.in','.nic.in')) or h in ['goa.gov.in','goaspcb.gov.in','goawrd.gov.in','goaprintingpress.gov.in']
def publisher_class(url):
    h=urlsplit(url).hostname or ''
    if official(url): return 'government_or_court'
    if h.endswith('actforgoa.org'): return 'act_for_goa'
    if h.endswith('fao.org'): return 'intergovernmental_repository'
    if h.endswith(('goafoundation.org','elaw.in','elaw.org','goenchoektopp.com','indiatogether.org','indiawaterportal.org','prsindia.org','ielrc.org')): return 'civil_society_or_commentary'
    if 'icar' in h or h.endswith('ccari.res.in'): return 'public_research_institution'
    if h.endswith(('mongabay.com','indiatimes.com','thehindu.com','heraldgoa.in','navhindtimes.in','thegoan.net')): return 'journalism'
    return 'other_public_source'
def session():
    if not hasattr(LOCAL,'session'):
        LOCAL.session=requests.Session(); LOCAL.session.headers['User-Agent']=UA
    return LOCAL.session
def polite_get(url, **kwargs):
    host=urlsplit(url).netloc
    with LOCK: gate=HOST_LOCKS.setdefault(host,threading.Lock())
    with gate:
        time.sleep(.5)
        return session().get(url,timeout=(10,35),**kwargs)
def robots_allowed(url):
    p=urlsplit(url); origin=f'{p.scheme}://{p.netloc}'
    with LOCK: gate=HOST_LOCKS.setdefault('robots:'+origin,threading.Lock())
    with gate:
        if origin not in ROBOTS:
            record={'origin':origin,'retrieved_at':now()}; rp=None
            try:
                r=polite_get(origin+'/robots.txt'); record.update(http_status=r.status_code)
                if r.status_code==200 and not r.text.lstrip().startswith('<'):
                    rp=RobotFileParser();rp.parse(r.text.splitlines())
                    record['body']=r.text
                else: record['note']='No parseable robots policy obtained; public read-only bounded fetching.'
            except requests.RequestException as e: record['error']=str(e)[:400]
            ROBOTS[origin]=rp
            append(C/'logs'/'robots.jsonl',record)
    return not ROBOTS[origin] or ROBOTS[origin].can_fetch(UA,url)

def extract(item, content):
    sid=item['id']; mime=item.get('content_type','').split(';')[0]
    pages=[]; meta={}; actual='binary'; title=item.get('title_hint','')
    if content.lstrip().startswith(b'%PDF-'):
        actual='pdf'; reader=PdfReader(io.BytesIO(content),strict=False)
        if reader.is_encrypted:
            if not reader.decrypt(''): raise ValueError('encrypted PDF; no password attempted')
        for i,p in enumerate(reader.pages):
            try: t=p.extract_text() or ''; error=None
            except Exception as e: t='';error=str(e)[:300]
            pages.append({'page':i+1,'text':t,'characters':len(t),'extraction_error':error,'needs_ocr_review':len(t.strip())<60})
        meta['pdf_metadata']={str(k):str(v) for k,v in (reader.metadata or {}).items()}
        meta['page_count']=len(pages)
        text='\n\n'.join(f'=== PDF page {p["page"]} ===\n{p["text"]}' for p in pages)
        meta['extraction_method']='pypdf native text; no OCR; PDF page numbers are physical file pages'
        meta['pages_needing_ocr_review']=[p['page'] for p in pages if p['needs_ocr_review']]
        n=sum(p['characters'] for p in pages)
        meta['extraction_status']='needs_ocr' if n<100 else ('partial_text_check_scans' if meta['pages_needing_ocr_review'] else 'native_text_extracted')
    elif 'html' in mime or b'<html' in content[:2000].lower() or b'<!doctype html' in content[:1000].lower():
        actual='html'; soup=BeautifulSoup(content,'lxml')
        if soup.title: meta['html_title']=soup.title.get_text(' ',strip=True)
        if not title or title.lower() in ['view','download','click here','pdf','act','rules']: title=meta.get('html_title',title)
        meta['source_date_metadata']=[{'field':x.get('property') or x.get('name'),'value':x.get('content')} for x in soup.select('meta[content]') if re.search('published|modified|date',x.get('property','')+' '+x.get('name',''),re.I)]
        meta['source_time_elements']=[{'datetime':x.get('datetime'),'text':x.get_text(' ',strip=True)} for x in soup.find_all('time')][:20]
        for el in soup(['script','style','noscript','nav','header','footer','form','svg']):el.decompose()
        articles=soup.select('article')
        main=soup.select_one('main') or soup.select_one('.entry-content') or (articles[0] if len(articles)==1 else None) or soup.body or soup
        text=main.get_text('\n',strip=True)
        meta['extraction_method']='BeautifulSoup DOM text; scripts, navigation, header, footer and forms excluded; original HTML preserved'
        meta['extraction_status']='text_extracted' if len(text)>100 else 'minimal_or_script_dependent'
        if re.search(r'^(access denied|forbidden|just a moment|attention required)',meta.get('html_title',''),re.I): meta['extraction_status']='blocked_html'
    elif content[:2]==b'PK' and urlsplit(item['url']).path.lower().endswith('.docx'):
        actual='docx'
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            s=BeautifulSoup(z.read('word/document.xml'),'xml')
            text='\n'.join(p.get_text() for p in s.find_all('w:p'))
        meta.update(extraction_method='DOCX main document XML; headers, footers, comments not extracted',extraction_status='text_extracted')
    elif mime.startswith('text/') or urlsplit(item['url']).path.lower().endswith('.txt'):
        actual='text';text=content.decode('utf-8',errors='replace');meta.update(extraction_method='UTF-8 decode',extraction_status='text_extracted')
    else:
        text='';meta.update(extraction_method='none',extraction_status='unsupported_format')
    meta.update(format=actual,title=title or unquote(Path(urlsplit(item['url']).path).name),text_characters=len(text))
    if text:
        path=C/'text'/f'{sid}.txt';path.write_text(text);meta['text_path']=str(path.relative_to(ROOT))
        meta['text_sha256']=hashlib.sha256(text.encode()).hexdigest()
    if pages:
        path=C/'pages'/f'{sid}.json';dump(path,pages);meta['pages_path']=str(path.relative_to(ROOT))
    tag_text=meta['title']+' '+item.get('discovery_context','')+' '+text[:20000]
    meta['topics']=sorted(set(item.get('topics',[])+topic_tags(tag_text)))
    # Discovery titles are clues, not a determination of legal effect.
    hint=(meta['title']+' '+item.get('title_hint','')).lower()
    if 'draft' in hint: kind='draft_document'
    elif 'judgment' in hint or 'judgement' in hint or ' vs ' in hint: kind='judgment_or_order'
    elif 'amend' in hint or 'corrigendum' in hint: kind='amendment_or_corrigendum'
    elif re.search(r'\b(act|rules|regulations|notification|code)\b',hint): kind='legislation_or_notification'
    elif re.search(r'charter|procedure|guide|manual|scheme|rti|complaint|grievance',hint): kind='guidance_or_service'
    else: kind='article_report_or_index'
    meta['document_kind_hint']=kind
    meta['classification_method']='publisher domain plus discovery/title keyword triage; not legal validation'
    meta['legal_currency']='not_consolidated_or_legally_verified'
    meta['applicability']='Goa relevance selected for research; territorial scope, commencement, amendments, stays and repeal require review'
    meta['language_status']='not_manually_verified; preserve original language'
    return meta

def fetch(seed, retry=False):
    u=canonical(seed['url']);sid=hashlib.sha256(u.encode()).hexdigest()[:24];mp=C/'metadata'/f'{sid}.json'
    if mp.exists() and not retry:
        old=json.loads(mp.read_text())
        if old.get('raw_path') and (ROOT/old['raw_path']).exists(): return old
        if old.get('error'): return old
    item={**seed,'url':u,'id':sid,'retrieved_at':now(),'publisher_class':seed.get('publisher_class') or publisher_class(u),'fetch_method':'requests HTTPS/HTTP GET, TLS verification enabled','status':'failed'}
    try:
        if not robots_allowed(u): raise ValueError('robots_disallowed')
        r=polite_get(u,stream=True)
        item.update(http_status=r.status_code,final_url=r.url,content_type=r.headers.get('Content-Type',''),etag=r.headers.get('ETag'),last_modified=r.headers.get('Last-Modified'),redirects=[{'url':x.url,'status':x.status_code} for x in r.history])
        b=bytearray()
        for chunk in r.iter_content(65536):
            b.extend(chunk)
            if len(b)>80*1024*1024: r.close();raise ValueError('response_exceeds_80_MiB')
        r.close();content=bytes(b);sha=hashlib.sha256(content).hexdigest()
        ext='.pdf' if content.lstrip().startswith(b'%PDF-') else ('.html' if 'html' in item['content_type'] else Path(urlsplit(r.url).path).suffix.lower())
        if not re.fullmatch(r'\.[a-z0-9]{1,6}',ext or ''): ext='.bin'
        path=C/'raw'/f'{sha}{ext}'
        if not path.exists():path.write_bytes(content)
        item.update(raw_path=str(path.relative_to(ROOT)),sha256=sha,bytes=len(content))
        if r.status_code!=200: item['error']=f'HTTP {r.status_code}; response archived, excluded from usable sources'
        else:
            item.update(extract(item,content));item['status']='downloaded'
            if item['extraction_status']=='blocked_html': item['status']='failed';item['error']='HTTP 200 challenge/error page'
    except Exception as e: item['error']=f'{type(e).__name__}: {e}'[:600]
    dump(mp,item);append(C/'logs'/'fetches.jsonl',item)
    return item

def discover(item):
    if item.get('format')!='html' or item.get('status')!='downloaded':return []
    soup=BeautifulSoup((ROOT/item['raw_path']).read_bytes(),'lxml');found=[]
    for a in soup.select('a[href], iframe[src], embed[src], object[data]'):
        raw=a.get('href') or a.get('src') or a.get('data') or ''
        if raw.startswith(('#','javascript:','mailto:','tel:')):continue
        u=canonical(raw,item.get('final_url',item['url']))
        if not u: continue
        label=a.get_text(' ',strip=True)
        parent=a.find_parent(class_='document_holder') or a.find_parent('tr') or a.find_parent('li') or a.parent
        context=parent.get_text(' ',strip=True)[:900] if parent else label
        edge={'source_id':item['id'],'source_url':item['url'],'url':u,'label':label,'context':context}
        append(C/'logs'/'links.jsonl',edge)
        if SKIP.search(u+' '+label):continue
        if re.search(r'\.(jpe?g|png|gif|svg|webp|zip|mp[34]|css|js|xlsx?|pptx?)(?:$|\?)',u,re.I):continue
        if any(k in dict(parse_qsl(urlsplit(u).query)) for k in ['s','share','replytocom']):continue
        isdoc=bool(DOC.search(u));tags=topic_tags(label+' '+unquote(u)+' '+context)
        same=(urlsplit(u).hostname or '').removeprefix('www.')==(urlsplit(item['url']).hostname or '').removeprefix('www.')
        if not (isdoc or same or official(u)): continue
        if not tags and not HUB.search(label+' '+unquote(u)):continue
        if not isdoc and not HUB.search(label+' '+unquote(u)):continue
        title=label
        named=parent.select_one('.doc_name') if parent else None
        if named:title=named.get_text(' ',strip=True)
        if label.lower() in ['view','download','click here','pdf','read more','']:title=context[:260] or unquote(Path(urlsplit(u).path).name)
        if named:title=named.get_text(' ',strip=True)
        dates=re.findall(r'Date\s*:\s*(\d{2}/\d{2}/\d{4})',context)
        found.append({'url':u,'title_hint':title,'discovered_from':item['url'],'discovery_context':context,'source_listing_dates':dates,'source_listing_date_note':'Portal listing date, not independently verified publication or commencement date','topics':tags,'depth':item.get('depth',0)+1})
    return found

def snapshot_actforgoa():
    p=ROOT/'data'/'wordpress.json'
    if not p.exists():return []
    raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();out=C/'research'/f'actforgoa-wordpress-{sha[:12]}.json'
    out.write_bytes(raw);wp=json.loads(raw);seeds=[];records=[]
    for collection,rows in wp.items():
        if collection.endswith(('/posts','/portfolio','/pages')):
            for r in rows:
                title=BeautifulSoup(r.get('title',{}).get('rendered',''),'lxml').get_text(' ',strip=True)
                content=r.get('content',{}).get('rendered','');text=BeautifulSoup(content,'lxml').get_text('\n',strip=True)
                rec={'collection':collection,'id':r.get('id'),'url':r.get('link'),'title':title,'source_date':r.get('date'),'source_modified':r.get('modified'),'text':text,'topics':topic_tags(title+' '+text),'snapshot_path':str(out.relative_to(ROOT))}
                records.append(rec)
                if r.get('link') and not re.search(r'connection-test|template|sidebar|shortcodes|elements|privacy-policy|log_file',r['link'],re.I):seeds.append({'url':r['link'],'title_hint':title,'topics':rec['topics'],'discovered_from':'existing public WordPress archive snapshot','depth':1})
                s=BeautifulSoup(content,'lxml')
                for a in s.select('a[href]'):
                    u=canonical(a['href'],r.get('link',''))
                    if u and DOC.search(u):seeds.append({'url':u,'title_hint':a.get_text(' ',strip=True),'discovered_from':r.get('link'),'depth':1})
        elif collection.endswith('/media'):
            for r in rows:
                u=r.get('source_url','')
                if DOC.search(u) and 'log_file' not in u:seeds.append({'url':u,'title_hint':BeautifulSoup(r.get('title',{}).get('rendered',''),'lxml').get_text(' ',strip=True),'discovered_from':r.get('link'),'depth':1})
    dump(C/'research'/'actforgoa-baseline.json',records)
    return seeds

def build_index():
    rows=[json.loads(p.read_text()) for p in sorted((C/'metadata').glob('*.json'))]
    with (C/'catalog.jsonl').open('w') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    fields=['id','title','url','final_url','publisher_class','document_kind_hint','topics','status','http_status','format','page_count','extraction_status','text_characters','legal_currency','retrieved_at','raw_path','text_path','pages_path','sha256','discovered_from','error']
    with (C/'catalog.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for r in rows:w.writerow({k:('; '.join(r.get(k,[])) if isinstance(r.get(k),list) else r.get(k)) for k in fields})
    db=sqlite3.connect(C/'search.sqlite');db.executescript('DROP TABLE IF EXISTS sources; DROP TABLE IF EXISTS passages; CREATE TABLE sources(id TEXT PRIMARY KEY, title TEXT, url TEXT, publisher_class TEXT, kind TEXT, topics TEXT, raw_path TEXT, text_path TEXT, legal_currency TEXT); CREATE VIRTUAL TABLE passages USING fts5(source_id UNINDEXED, page UNINDEXED, passage UNINDEXED, title, text, text_origin UNINDEXED, tokenize="unicode61");')
    chunks=0
    for r in rows:
        if r['status']!='downloaded' or not r.get('text_path') or r.get('inclusion_status','included').startswith('excluded'):continue
        db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?)',(r['id'],r.get('title'),r['url'],r['publisher_class'],r.get('document_kind_hint'),','.join(r.get('topics',[])),r.get('raw_path'),r['text_path'],r.get('legal_currency')))
        ps=json.loads((ROOT/r['pages_path']).read_text()) if r.get('pages_path') else [{'page':None,'text':(ROOT/r['text_path']).read_text()}]
        ocr={p['page']:p for p in json.loads((ROOT/r['ocr_pages_path']).read_text())} if r.get('ocr_pages_path') else {}
        for p in ps:
            t=p['text'];origin='native_extraction'
            if len(t.strip())<60 and p['page'] in ocr and len(ocr[p['page']]['text'])>len(t):t=ocr[p['page']]['text'];origin='ocr_eng_unverified'
            for n,start in enumerate(range(0,len(t),5000)):
                chunk=t[start:start+5000]
                if chunk.strip():db.execute('INSERT INTO passages VALUES(?,?,?,?,?,?)',(r['id'],p['page'],n+1,r.get('title'),chunk,origin));chunks+=1
    db.commit();db.close()
    good=[r for r in rows if r['status']=='downloaded'];pdfs=[r for r in good if r.get('format')=='pdf']
    counts={'generated_at':now(),'attempted_sources':len(rows),'downloaded_sources':len(good),'failed_sources':len(rows)-len(good),'unique_downloaded_content_hashes':len({r['sha256'] for r in good}),'formats':dict(Counter(r.get('format') for r in good)),'publishers':dict(Counter(r['publisher_class'] for r in good)),'topics':dict(Counter(t for r in good for t in r.get('topics',[]))),'pdf_pages':sum(r.get('page_count',0) for r in pdfs),'pdfs_needing_ocr':sum(r.get('extraction_status')=='needs_ocr' for r in pdfs),'pdfs_with_any_low_text_pages':sum(bool(r.get('pages_needing_ocr_review')) for r in pdfs),'search_passages':chunks,'downloaded_bytes_by_source':sum(r.get('bytes',0) for r in good),'extraction_status':dict(Counter(r.get('extraction_status') for r in good))}
    counts['included_sources']=sum(not r.get('inclusion_status','included').startswith('excluded') for r in good)
    counts['excluded_downloaded_sources']=sum(r.get('inclusion_status','included').startswith('excluded') for r in good)
    counts['included_pdf_sources']=sum(not r.get('inclusion_status','included').startswith('excluded') for r in pdfs)
    included=[r for r in good if not r.get('inclusion_status','included').startswith('excluded')]
    unique_pdf={r['sha256']:r for r in included if r.get('format')=='pdf'}
    counts.update(unique_included_pdf_files=len(unique_pdf),unique_included_pdf_pages=sum(r.get('page_count',0) for r in unique_pdf.values()),ocr_documents=sum(bool(r.get('ocr_pages_path')) for r in rows),ocr_pages_with_text=sum(r.get('ocr_pages_completed',0) for r in rows),included_publisher_counts=dict(Counter(r['publisher_class'] for r in included)))
    dump(C/'stats.json',counts);dump(C/'research'/'failures.json',[r for r in rows if r['status']!='downloaded']);print(json.dumps(counts,indent=2),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',default='corpus/seeds.json');ap.add_argument('--depth',type=int,default=2);ap.add_argument('--limit',type=int,default=500);ap.add_argument('--workers',type=int,default=6);ap.add_argument('--actforgoa',action='store_true');ap.add_argument('--index-only',action='store_true');ap.add_argument('--retry',action='store_true');ap.add_argument('--skip-index',action='store_true');ap.add_argument('--child-documents-only',action='store_true');a=ap.parse_args()
    if a.index_only:build_index();return
    queue=json.loads((ROOT/a.seeds).read_text())
    if a.actforgoa:queue+=snapshot_actforgoa()
    visited=set();pending={};done=0
    while queue and done<a.limit:
        batch=[]
        for s in queue:
            u=canonical(s['url'])
            if not u or u in visited:continue
            if done+len(batch)>=a.limit:pending[u]=s;continue
            visited.add(u);s['url']=u;batch.append(s)
        queue=[]
        if not batch:break
        with cf.ThreadPoolExecutor(max_workers=a.workers) as pool:
            futures={pool.submit(fetch,s,a.retry):s for s in batch}
            for f in cf.as_completed(futures):
                r=f.result();done+=1
                print(f'{done}: {r["status"]} {r.get("format", "")} {r["url"]} {r.get("error", "")}',flush=True)
                scope_depth=futures[f].get('depth',0)
                if scope_depth<a.depth:
                    new=discover({**r,'depth':scope_depth})
                    queue+=[s for s in new if DOC.search(s['url'])] if a.child_documents_only else new
    for s in queue:
        if s['url'] not in visited:pending[s['url']]=s
    dump(C/'research'/('pending-'+Path(a.seeds).stem+'.json'),list(pending.values()))
    if not a.skip_index:build_index()

if __name__=='__main__':main()
