"""Build source-linked JSON and SQLite catalogues from archived public responses."""
from __future__ import annotations
import csv,hashlib,html,json,re,sqlite3
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit,urljoin
from bs4 import BeautifulSoup
from pypdf import PdfReader
from crawl import ROOT,BASE,CACHE,body,canonical,save

TOPICS = {
 'Waste & recycling':r'waste|recycl|plastic|compost|garbage|clean.?up|swachh',
 'Nature & wildlife':r'wildlife|snake|biodiversity|forest|tree|animal|sanctuar|mollem|conservation',
 'Water & environment':r'water|pollution|river|lake|wetland|climate|environment|flood',
 'Community & rights':r'rights|legal|women|child|education|communit|panchayat|gram sabha|voter|citizen',
 'Food & farming':r'agricultur|farm|food|organic|seed|permacultur|nutrition',
 'Culture & heritage':r'cultur|heritage|museum|art\b|music|history|tradition',
 'Planning & mobility':r'planning|development|mobility|road|transport|infrastructure|cycling|urban',
 'Health & wellbeing':r'health|mental|well.?being|hospital|counsel|disabil|covid'
}
EXCLUDE = re.compile(r'^(external-link|notifications|members|password-|register|profile|activity|connection-test|donor-dashboard|donation-history|donation-failed|donation-confirmation|blog-setting|my-account|checkout|cart|shop|page-with-|default-template|left-sidebar|favorite-posts|template-single|job-form|dashboard|listing|front$|sample-page|jobs-listing|job-dashboard|post-a-job|page-markup|page-image|level-|page-[ab]$|front-page|frontpage|clearing-floats|about$|lorem-ipsum|search$|pbd-record|process$)')

def clean(value):
    if isinstance(value,dict):value=value.get('rendered','')
    return re.sub(r'\s+',' ',BeautifulSoup(str(value or ''),'lxml').get_text(' ',strip=True)).strip()

def soup_of(value):
    s=BeautifulSoup(value or '','lxml')
    for e in s.select('script,style,noscript,form,input,button,nav,footer,iframe,.social_icons_block,.tags_media,.comments_posted'):
        e.decompose()
    # WordPress shortcode syntax is presentation debris, not editorial prose.
    for t in list(s.find_all(string=True)):
        new=re.sub(r'\[/?[a-zA-Z_][^\]]*\]','',str(t))
        if new!=str(t):t.replace_with(new)
    return s

def blocks(s):
    result=[]
    for el in s.find_all(['h1','h2','h3','h4','p','li']):
        if el.find_parent(['p','li']):continue
        text=clean(el.get_text(' ',strip=True))
        if text:result.append({'type':'heading' if el.name.startswith('h') else 'list' if el.name=='li' else 'paragraph','text':text})
    if not result:
        text=clean(s.get_text(' ',strip=True))
        if text:result=[{'type':'paragraph','text':text}]
    return result

def tag_topics(text):
    return [k for k,v in TOPICS.items() if re.search(v,text,re.I)] or ['Community & rights']

def phone(raw):
    display=clean(raw)
    # Keep the source label; do not concatenate lists or invent abbreviated numbers.
    first=re.split(r'[,;/]|\s+or\s+',display)[0]
    digits=re.sub(r'\D','',first)
    if digits.startswith('910') and len(digits)==13:digits='91'+digits[3:]
    if len(digits)==10:digits='91'+digits
    elif len(digits)==11 and digits.startswith('0'):digits='91'+digits[1:]
    valid=len(digits)==12 and digits.startswith('91')
    return {'display':display,'href':'tel:+'+digits if valid else None,'verification':'source-listed-unverified'}

def make_record(id,title,kind,url,content,date='',updated='',image='',source_api=''):
    s=soup_of(content)
    text=clean(s.get_text(' ',strip=True))
    title=clean(title)
    if not title:return None
    extracted=blocks(s)
    links=[]
    for a in s.select('a[href]'):
        u=urljoin(url,a['href'])
        if urlsplit(u).scheme in ('https','http','mailto','tel'):
            links.append({'label':clean(a.get_text(' ',strip=True)) or urlsplit(u).hostname or u,'url':u})
    docs=[l for l in links if re.search(r'\.(pdf|docx?|xlsx?|pptx?)($|\?)',l['url'],re.I)]
    emails=sorted(set(re.findall(r'(?<![\w.-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text)))
    emails=[e for e in emails if not e.endswith(('example.com','domain.com'))]
    phones=[]
    for a in s.select('a[href^="tel:"]'):phones.append(phone(a['href'][4:]))
    for match in re.finditer(r'(?<!\d)(?:\+91[ .-]?)?[6-9]\d{4}[ -]?\d{5}(?!\d)',text):
        p=phone(match.group())
        if p not in phones:phones.append(p)
    sentences=re.split(r'(?<=[.!?])\s+',text)
    summary=' '.join(sentences[:2])[:250]
    if len(summary)==250:summary=summary.rsplit(' ',1)[0]+'…'
    source=CACHE.get(canonical(url),{})
    return {'id':id,'title':title,'kind':kind,'source':url,'sourceApi':source_api,
      'sourceStatus':source.get('status'), 'publishedAt':date,'updatedAt':updated,
      'retrievedAt':source.get('fetched_at','2026-10-22'),'summary':summary or 'Read the original resource from ActForGoa.',
      'text':text,'blocks':extracted,'topics':tag_topics(title+' '+text),'imageSource':image,'image':'',
      'phones':phones,'emails':emails,'locations':[],'documents':docs,'links':links,
      'verification':'source-listed-unverified','editorialStatus':'imported'}

def main():
    wp=json.loads((ROOT/'data/wordpress.json').read_text())
    media={x['id']:x for x in wp.get('wp/v2/media',[])}
    records=[]; excluded=[]; known=set()
    orgs=json.loads((ROOT/'data/connections.json').read_text()) if (ROOT/'data/connections.json').exists() else wp.get('cn-api/v1/entry',[])
    for row in orgs:
        url=BASE+'/directory/'
        api=BASE+'/wp-json/cn-api/v1/entry/'+str(row['id'])+'?_fields=id,slug,fn,org,tel,email,adr,bio,excerpt'
        record=make_record('org-'+str(row['id']),row['fn'],'organisation',url,row.get('bio',{}).get('rendered',''),source_api=api)
        record['phones']=[phone(v.get('number',{})) for v in row.get('tel',[]) if clean(v.get('number'))]
        record['emails']=[clean(v.get('address')) for v in row.get('email',[]) if clean(v.get('address'))]
        record['locations']=[', '.join(filter(None,[clean(v.get(k)) for k in ['street_address','locality','region','postal_code']])) for v in row.get('adr',[]) if v.get('visibility','public')=='public']
        record['locality']=next((clean(v.get('locality')) for v in row.get('adr',[]) if clean(v.get('locality'))),'Goa')
        records.append(record)
    for endpoint,kind in [('wp/v2/posts','story'),('wp/v2/portfolio','story'),('wp/v2/pages','page')]:
        for row in wp.get(endpoint,[]):
            url=canonical(row['link']); known.add(url.rstrip('/'))
            if kind=='page' and EXCLUDE.search(row['slug']):
                excluded.append({'source':url,'title':clean(row['title']),'reason':'account, transactional, test, or template page retained in archive'});continue
            content=row.get('content',{}).get('rendered','')
            if not content:
                response=CACHE.get(url) or CACHE.get(url.rstrip('/'))
                if not response or response.get('status')!=200:continue
                page=soup_of(body(response))
                content=str(page.select_one('section#blog') or page.select_one('main') or '')
            image=media.get(row.get('featured_media'),{}).get('source_url','')
            r=make_record('wp-'+str(row['id']),row['title'],kind,url,content,row.get('date',''),row.get('modified',''),image)
            if r and (len(r['text'])>30 or r['links']):records.append(r)
    for url,response in CACHE.items():
        p=urlsplit(url)
        if not p.path.startswith('/resource/') or p.path=='/resource/' or '/page/' in p.path or p.query:continue
        if response.get('status')!=200 or 'text/html' not in response.get('content_type',''):continue
        if url.rstrip('/') in known:continue
        page=BeautifulSoup(body(response),'lxml')
        title=clean(page.select_one('h1').get_text()) if page.select_one('h1') else clean(page.title.get_text()).removesuffix(' - ActforGoa')
        content=page.select_one('.blog-post .content-container') or page.select_one('.content-container')
        if not content:continue
        date_el=page.select_one('.banner-content-wrap')
        date_match=re.search(r'(\d{1,2} [A-Za-z]+ \d{4})',date_el.get_text(' ') if date_el else '')
        image_el=content.select_one('img')
        image=image_el.get('src','') if image_el else ''
        r=make_record('resource-'+hashlib.sha256(url.encode()).hexdigest()[:10],title,'resource',url,str(content),date_match.group(1) if date_match else '',image=image)
        if r:records.append(r);known.add(url.rstrip('/'))
    # Attach document text for search; preserve the source article independently.
    # Named volunteer contacts are separate records so a person can search a name or locality.
    snake=next((r for r in records if r['id']=='resource-590480849c'),None)
    if snake:
        for i,b in enumerate(snake['blocks']):
            line=b['text']
            if not re.search(r'\b\d{7,10}\b',line):continue
            label=re.split(r'\d{7,10}',line)[0].strip(' –-/')
            name=label.split(',')[0].split(' – ')[0]
            contact=make_record('contact-snake-'+str(i),name,'contact',snake['source'],line,snake['publishedAt'])
            contact['summary']=line
            contact['text']='Snake rescue volunteer contact listed by ActForGoa. '+line
            contact['topics']=['Nature & wildlife']
            contact['parentId']=snake['id']
            contact['phones']=[phone(n) for n in re.findall(r'\b\d{7,10}\b',line)]
            contact['locality']=label[len(name):].strip(' ,–-') or 'Goa'
            records.append(contact)
    documents=[]
    for r in records:
        doc_text=[]
        for doc in r['documents']:
            response=CACHE.get(canonical(doc['url']))
            doc.update(status=response.get('status') if response else None)
            if response and response.get('status')==200 and response.get('path') and doc['url'].lower().split('?')[0].endswith('.pdf'):
                try:
                    reader=PdfReader(ROOT/response['path'])
                    text='\n'.join(page.extract_text() or '' for page in reader.pages)
                    doc.update(pages=len(reader.pages),textCharacters=len(text),archivePath=response['path'])
                    target=ROOT/'data/document-text'/f'{response["sha256"][:20]}.txt'
                    target.parent.mkdir(exist_ok=True);target.write_text(text)
                    doc['textPath']=str(target.relative_to(ROOT));doc_text.append(text[:25000])
                except Exception as e:doc['extractionError']=str(e)[:200]
            documents.append({'recordId':r['id'],**doc})
        if doc_text:r['documentText']='\n'.join(doc_text)
    records=list({r['id']:r for r in records}.values())
    # Reuse the reviewed, local image mapping without coupling extraction to image tooling.
    image_map=json.loads((ROOT/'data/image-map.json').read_text()) if (ROOT/'data/image-map.json').exists() else {}
    for r in records:r['image']=image_map.get(r['id'],{}).get('path','')
    records.sort(key=lambda r:(r['kind'],r['title'].lower()))
    save('catalog.json',records);save('documents.json',documents);save('migration-exclusions.json',excluded)
    public=ROOT/'public/data';public.mkdir(parents=True,exist_ok=True)
    (public/'catalog.json').write_text(json.dumps(records,ensure_ascii=False,separators=(',',':')))
    conn=sqlite3.connect(ROOT/'data/catalog.sqlite')
    conn.executescript('DROP TABLE IF EXISTS records;DROP TABLE IF EXISTS contacts;DROP TABLE IF EXISTS documents;DROP TABLE IF EXISTS record_topics;DROP TABLE IF EXISTS search;CREATE TABLE records(id TEXT PRIMARY KEY,kind TEXT,title TEXT,summary TEXT,body TEXT,source_url TEXT,source_api TEXT,published_at TEXT,updated_at TEXT,retrieved_at TEXT,verification TEXT);CREATE TABLE contacts(record_id TEXT,kind TEXT,value TEXT,action_url TEXT,verification TEXT);CREATE TABLE documents(record_id TEXT,url TEXT,title TEXT,status INTEGER,archive_path TEXT,text_path TEXT);CREATE TABLE record_topics(record_id TEXT,topic TEXT);CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,title,body,topics);')
    for r in records:
        conn.execute('INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?)',(r['id'],r['kind'],r['title'],r['summary'],r['text'],r['source'],r['sourceApi'],r['publishedAt'],r['updatedAt'],r['retrievedAt'],r['verification']))
        for p in r['phones']:conn.execute('INSERT INTO contacts VALUES (?,?,?,?,?)',(r['id'],'phone',p['display'],p['href'],p['verification']))
        for e in r['emails']:conn.execute('INSERT INTO contacts VALUES (?,?,?,?,?)',(r['id'],'email',e,'mailto:'+e,r['verification']))
        for t in r['topics']:conn.execute('INSERT INTO record_topics VALUES (?,?)',(r['id'],t))
        conn.execute('INSERT INTO search VALUES (?,?,?,?)',(r['id'],r['title'],r['text']+' '+r.get('documentText',''),' '.join(r['topics'])))
    for d in documents:conn.execute('INSERT INTO documents VALUES (?,?,?,?,?,?)',(d['recordId'],d['url'],d['label'],d.get('status'),d.get('archivePath'),d.get('textPath')))
    conn.commit();conn.close()
    summary={'records':len(records),'byKind':dict(Counter(r['kind'] for r in records)),'phoneEntries':sum(len(r['phones']) for r in records),'emailEntries':sum(len(r['emails']) for r in records),'documents':len(documents),'migrationExclusions':len(excluded),'retrievedAt':'2026-10-22'}
    save('catalog-summary.json',summary)
    (public/'summary.json').write_text(json.dumps(summary))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
