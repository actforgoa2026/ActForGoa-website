"""Public, resumable site archive. Run from the repository root with .venv/bin/python.

No authentication, forms, donations, or other state-changing endpoints are used.
"""
from __future__ import annotations
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import mimetypes
import re
import threading
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://actforgoa.org'
ARCHIVE = ROOT / 'archive'
MANIFEST = ARCHIVE / 'manifests' / 'fetches.jsonl'
for name in ['raw', 'assets', 'manifests']:
    (ARCHIVE / name).mkdir(parents=True, exist_ok=True)
LOCK = threading.Lock()
LOCAL = threading.local()
CACHE = {}
if MANIFEST.exists():
    for line in MANIFEST.read_text().splitlines():
        try:
            item = json.loads(line)
            CACHE[item['url']] = item
        except (ValueError, KeyError):
            pass
EDGES, SKIPPED = [], {}
ASSETS = set()
ROBOTS = []
UA = 'ActForGoaArchive/1.0 (client-authorized public website migration; read-only)'

def canonical(url, base=BASE):
    url = urljoin(base, (url or '').strip()).replace('&amp;', '&')
    p = urlsplit(url)
    if p.scheme not in ('http', 'https'):
        return url
    host = (p.hostname or '').lower()
    if host in ('www.actforgoa.org', 'actforgoa.org'):
        host = 'actforgoa.org'
        scheme = 'https'
    else:
        scheme = p.scheme
    query = urlencode([(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True)
                       if not k.startswith('utm_') and k not in ('fbclid','gclid')])
    return urlunsplit((scheme,host,p.path or '/',query,''))

def internal(url):
    return urlsplit(url).hostname == 'actforgoa.org'

def forbidden(url):
    p = urlsplit(url)
    if p.scheme not in ('http','https'): return 'non-http'
    if re.search(r'/(wp-admin|wp-login|xmlrpc)(?:[/.?]|$)', p.path): return 'administrative'
    if re.search(r'(add-to-cart|remove_item|logout|give_action|replytocom|ai1ec_exporter_controller)=', p.query): return 'state-changing-or-duplicate-query'
    if '/action~' in p.path: return 'robots-calendar-trap'
    if internal(url):
        for rule in ROBOTS:
            if re.match(rule, p.path + ('?' + p.query if p.query else '')): return 'robots-disallowed'
    return None

def fetch(url, asset=False, retry=False):
    url = canonical(url)
    old = CACHE.get(url)
    if old and not retry and old.get('path') and (ROOT / old['path']).exists():
        return old
    rule = forbidden(url)
    if rule:
        SKIPPED[url] = rule
        return {'url':url,'status':None,'error':rule}
    if not hasattr(LOCAL,'session'):
        LOCAL.session = requests.Session()
        LOCAL.session.headers['User-Agent'] = UA
    item = {'url':url,'fetched_at':dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        time.sleep(.15)
        r = LOCAL.session.get(url, timeout=(12,45), stream=True)
        item.update(status=r.status_code,final_url=r.url,content_type=r.headers.get('Content-Type',''),
                    redirects=[{'status':h.status_code,'url':h.url} for h in r.history],
                    etag=r.headers.get('ETag'),last_modified=r.headers.get('Last-Modified'),
                    total=r.headers.get('X-WP-Total'),pages=r.headers.get('X-WP-TotalPages'))
        chunks, size = [], 0
        for chunk in r.iter_content(65536):
            size += len(chunk)
            if size > 80 * 1024 * 1024:
                item['error'] = 'over-80MiB-per-response-boundary'
                r.close()
                break
            chunks.append(chunk)
        if 'error' not in item:
            content = b''.join(chunks)
            mime = item['content_type'].split(';')[0]
            ext = Path(urlsplit(url).path).suffix
            if not re.match(r'^\.[a-zA-Z0-9]{1,7}$',ext): ext = ''
            if mime == 'text/html': ext = '.html'
            elif mime == 'application/json': ext = '.json'
            elif not ext: ext = mimetypes.guess_extension(mime) or '.bin'
            relative = Path('archive') / ('assets' if asset else 'raw') / (hashlib.sha256(url.encode()).hexdigest()[:24] + ext)
            (ROOT / relative).write_bytes(content)
            item.update(path=str(relative),bytes=len(content),sha256=hashlib.sha256(content).hexdigest())
        r.close()
    except requests.RequestException as e:
        item['error'] = str(e)[:500]
        item.setdefault('status',None)
    with LOCK:
        CACHE[url] = item
        with MANIFEST.open('a') as f: f.write(json.dumps(item,ensure_ascii=False)+'\n')
    return item

def body(item):
    return (ROOT / item['path']).read_text(errors='replace') if item.get('path') else ''

def links(html, url):
    soup = BeautifulSoup(html,'lxml')
    found = set()
    for tag, attr, relation in [('a','href','link'),('img','src','image'),('img','data-src','image'),('img','data-lazyload','image'),
                                ('script','src','script'),('link','href','head-link'),('iframe','src','embed'),
                                ('source','src','media'),('video','src','media'),('audio','src','media')]:
        for el in soup.find_all(tag):
            raw = el.get(attr)
            if not raw or raw.startswith(('data:','javascript:','#')): continue
            target = canonical(raw,url)
            EDGES.append({'source':url,'target':target,'raw':raw,'text':el.get_text(' ',strip=True)[:300],
                          'relation':relation,'fragment':urlsplit(raw).fragment})
            if relation == 'link': found.add(target)
            elif relation in ('image','script','media') or (tag == 'link' and 'stylesheet' in el.get('rel',[])):
                if internal(target): ASSETS.add(target)
    for el in soup.select('[srcset]'):
        for part in el['srcset'].split(','):
            target = canonical(part.strip().split(' ')[0],url)
            if internal(target): ASSETS.add(target)
    for match in re.finditer(r'url\([\s\x22\x27]*([^\)\x22\x27]+)', html):
        target=canonical(match.group(1).strip(),url)
        if internal(target) and '/wp-content/uploads/' in target: ASSETS.add(target)
    return found

def save(name, data):
    (ROOT / 'data' / name).write_text(json.dumps(data,ensure_ascii=False,indent=2))

def main():
    robots = body(fetch(BASE+'/robots.txt'))
    for line in robots.splitlines():
        if line.strip().lower().startswith('disallow:'):
            value=line.split(':',1)[1].strip()
            if value: ROBOTS.append('^'+re.escape(value).replace(r'\*','.*'))
    api = fetch(BASE+'/wp-json/')
    types_item = fetch(BASE+'/wp-json/wp/v2/types')
    types = json.loads(body(types_item))
    tax_item = fetch(BASE+'/wp-json/wp/v2/taxonomies')
    tax = json.loads(body(tax_item))
    queue = {BASE+'/'}
    wp = {}
    collections = {v['rest_namespace']+'/'+v['rest_base'] for v in types.values() if '(' not in v.get('rest_base','')}
    collections.update(v.get('rest_namespace','wp/v2')+'/'+v['rest_base'] for v in tax.values() if v.get('rest_base'))
    collections.update(['cn-api/v1/entry','cn-api/v1/category'])
    for endpoint in sorted(collections):
        records = []
        page = 1
        fields = ''
        while True:
            item=fetch(f'{BASE}/wp-json/{endpoint}?per_page=100&page={page}{fields}')
            if item.get('status') == 500 and endpoint == 'wp/v2/pages' and not fields:
                fields = '&_fields=id,slug,link,date,modified,title,parent,featured_media'
                item=fetch(f'{BASE}/wp-json/{endpoint}?per_page=100&page={page}{fields}')
            if item.get('status') == 500 and endpoint == 'cn-api/v1/entry' and not fields:
                fields = '&_fields=id,slug,fn,org,tel,email,adr,bio,excerpt,url,categories'
                item=fetch(f'{BASE}/wp-json/{endpoint}?per_page=100&page={page}{fields}')
            if item.get('status') != 200: break
            try: rows = json.loads(body(item))
            except ValueError: break
            if not isinstance(rows,list): break
            records.extend(rows)
            if page >= int(item.get('pages') or 1): break
            page += 1
        wp[endpoint] = records
        print(f'API {endpoint}: {len(records)}',flush=True)
        for row in records:
            if row.get('link'): queue.add(canonical(row['link']))
            html=row.get('content',{}).get('rendered','') if isinstance(row.get('content'),dict) else ''
            if html: queue.update(x for x in links(html,row.get('link',BASE)) if internal(x))
            if row.get('source_url'): ASSETS.add(canonical(row['source_url']))
        save('wordpress.json',wp)
    sitemap_queue = {BASE+'/sitemap.xml',BASE+'/wp-sitemap.xml'}
    sitemap_seen=set()
    while sitemap_queue:
        url=sitemap_queue.pop()
        if url in sitemap_seen: continue
        sitemap_seen.add(url)
        item=fetch(url)
        soup=BeautifulSoup(body(item),'xml')
        locs={canonical(x.get_text()) for x in soup.find_all('loc')}
        if soup.find('sitemapindex'): sitemap_queue.update(locs-sitemap_seen)
        else: queue.update(locs)
    seen=set()
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        while queue:
            batch=[]
            for url in sorted(queue):
                if url in seen: continue
                if not internal(url): continue
                rule=forbidden(url)
                if rule: SKIPPED[url]=rule; seen.add(url);continue
                p=urlsplit(url)
                if p.path.startswith('/wp-json/') or '/feed' in p.path:
                    SKIPPED[url]='api-separately-archived-or-syndication-duplicate';seen.add(url);continue
                if p.query and not all(k in ('page','paged','p','page_id','s') for k,v in parse_qsl(p.query)):
                    SKIPPED[url]='query-variant-boundary';seen.add(url);continue
                if re.search(r'\.(pdf|docx?|xlsx?|pptx?|zip|jpe?g|png|gif|webp|svg|mp[34]|woff2?|css|js)$',p.path,re.I):
                    ASSETS.add(url);seen.add(url);continue
                batch.append(url)
            queue=set()
            if not batch: break
            for item in pool.map(fetch,batch):
                seen.add(item['url'])
                if item.get('status')==200 and 'text/html' in item.get('content_type',''):
                    queue.update(links(body(item),item.get('final_url',item['url']))-seen)
            print(f'HTML frontier: visited={len(seen)} next={len(queue)} assets={len(ASSETS)}',flush=True)
            save('links.json',EDGES)
            save('crawl-exclusions.json',SKIPPED)
    # Public linked documents on other hosts are archived, not entire external websites.
    for edge in EDGES:
        if re.search(r'\.(pdf|docx?|xlsx?|pptx?)$',urlsplit(edge['target']).path,re.I): ASSETS.add(edge['target'])
    asset_seen=set()
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        while ASSETS-asset_seen:
            batch=sorted(ASSETS-asset_seen)
            for i,item in enumerate(pool.map(lambda u:fetch(u,asset=True),batch)):
                asset_seen.add(item['url'])
                if item.get('status')==200 and ('text/css' in item.get('content_type','') or urlsplit(item['url']).path.endswith('.css')):
                    for raw in re.findall(r'url\([\s\x22\x27]*([^\)\x22\x27]+)',body(item)):
                        target=canonical(raw.strip(),item['url'])
                        if internal(target): ASSETS.add(target)
                if (i+1)%100==0: print(f'Assets: {len(asset_seen)}/{len(ASSETS)}',flush=True)
    save('links.json',EDGES)
    save('crawl-exclusions.json',SKIPPED)
    save('fetch-manifest.json',list(CACHE.values()))
    print(json.dumps({'fetched':len(CACHE),'edges':len(EDGES),'assets':len(asset_seen),'excluded':len(SKIPPED)}),flush=True)

if __name__=='__main__': main()
