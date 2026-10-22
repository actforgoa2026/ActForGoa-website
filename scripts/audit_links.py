"""Audit link destinations with repeat checks; do not equate 403s with dead links."""
import concurrent.futures as cf,csv,datetime as dt,json,re,time
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlsplit
import requests
from bs4 import BeautifulSoup
from crawl import ROOT,CACHE,body,canonical,forbidden,UA,save

REPORT=ROOT/'reports/link-checks.jsonl'
old={}
if REPORT.exists():
 for line in REPORT.read_text().splitlines():
  try:r=json.loads(line);old[r['url']]=r
  except ValueError:pass

def classify(status,error=''):
 if error:return 'unreachable'
 if status in (404,410):return 'broken'
 if status in (401,403,429):return 'restricted-or-rate-limited'
 if status and status>=500:return 'server-error'
 if status and 200<=status<400:return 'ok'
 return 'review'

def check(url):
 if url in old:return old[url]
 item={'url':url,'checkedAt':dt.datetime.now(dt.timezone.utc).isoformat()}
 if urlsplit(url).scheme not in ('http','https'):
  return {**item,'classification':'non-http','status':None}
 if forbidden(url):return {**item,'classification':'excluded','reason':forbidden(url),'status':None}
 cached=CACHE.get(url)
 if cached and cached.get('status')==200:
  item.update(status=200,finalUrl=cached.get('final_url',url),classification='ok',method='archived-GET')
  if 'text/html' in cached.get('content_type','') and re.search(r'There has been a critical error on this website|internal_server_error',body(cached)):
   item['classification']='soft-error'
  return item
 attempts=[]
 for attempt in range(2):
  try:
   with requests.get(url,headers={'User-Agent':UA},timeout=(8,18),stream=True) as r:
    attempts.append({'status':r.status_code,'finalUrl':r.url})
    status=r.status_code;item.update(status=status,finalUrl=r.url,classification=classify(status),method='GET')
    if status not in (404,410) and status<500:break
  except requests.RequestException as e:
   attempts.append({'error':str(e)[:250]});item.update(status=None,classification='unreachable',error=str(e)[:250])
  time.sleep(.25)
 item['attempts']=attempts
 return item

def main():
 edges=[]
 for f in ['links.json','library-links.json']:
  if (ROOT/'data'/f).exists():edges+=json.loads((ROOT/'data'/f).read_text())
 # Independently extract every archived HTML page: catches initial frontier and failed partial pages.
 for url,item in CACHE.items():
  if 'text/html' not in item.get('content_type','') or not item.get('path') or '/wp-json/' in url:continue
  soup=BeautifulSoup(body(item),'lxml')
  for a in soup.select('a[href]'):
   raw=a['href']
   if not raw or raw.startswith(('javascript:','#')):continue
   edges.append({'source':url,'target':canonical(raw,url),'text':a.get_text(' ',strip=True)[:200],'relation':'link','fragment':urlsplit(raw).fragment})
 refs=defaultdict(set)
 for e in edges:
  if e.get('relation')=='link':refs[e['target']].add(e['source'])
 for r in json.loads((ROOT/'data/catalog.json').read_text()):
  for d in r['documents']+r['links']:refs[canonical(d.get('url',''))].add(r['source'])
 results=[]
 print('Unique destinations',len(refs),flush=True)
 with cf.ThreadPoolExecutor(max_workers=8) as pool:
  for i,result in enumerate(pool.map(check,sorted(refs))):
   result['referrers']=sorted(refs[result['url']]);result['referrerCount']=len(result['referrers'])
   results.append(result)
   with REPORT.open('a') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n')
   if (i+1)%100==0:print('Checked',i+1,dict(Counter(r['classification'] for r in results)),flush=True)
 save('link-audit.json',results)
 summary=dict(Counter(r['classification'] for r in results));save('link-audit-summary.json',summary)
 fields=['classification','status','url','finalUrl','referrerCount','referrers']
 with (ROOT/'reports/link-audit.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader()
  for r in results:writer.writerow({**r,'referrers':' | '.join(r['referrers'])})
 issues=[r for r in results if r['classification'] in ('broken','server-error','soft-error','unreachable')]
 lines=['# Link audit','',f'Checked {len(results)} unique linked destinations on 22 October 2026.','',json.dumps(summary,indent=2),'','HTTP 404/410 is confirmed broken after repeat GETs. Server errors and soft errors are listed separately. Access restrictions and rate limits are not called broken. A successful response is not proof that a contact or service is current.','', '## Priority repairs','']
 for r in sorted(issues,key=lambda x:-x['referrerCount'])[:50]:lines.append(f'- **{r["classification"]} ({r.get("status")})** {r["url"]} · {r["referrerCount"]} referring pages')
 lines+=['','Full source-to-target evidence is in link-audit.csv and data/link-audit.json. Raw HTTP evidence is in the local archive. Placeholder addresses such as contact@example.com and old staging-domain links require editorial repair even if their HTTP destination resolves.']
 (ROOT/'reports/LINK-AUDIT.md').write_text('\n'.join(lines))
 print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
