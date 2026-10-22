"""Recover public directory fields without the broken legacy rendering field."""
import json
from crawl import fetch,body,save,BASE
records=[]
page=1
seen=set()
while True:
    item=fetch(f'{BASE}/wp-json/cn-api/v1/entry?per_page=100&offset={(page-1)*100}&_fields=id,slug,fn,org,tel,email,adr,bio,excerpt,url,links,link,urls,categories,modified,date')
    if item.get('status') != 200: raise RuntimeError(item)
    rows=json.loads(body(item))
    fresh=[r for r in rows if r['id'] not in seen]
    records.extend(fresh)
    seen.update(r['id'] for r in fresh)
    print(page,len(rows),item.get('total'),item.get('pages'),flush=True)
    if len(rows)<100 or not fresh:break
    page+=1
save('connections.json',records)
print(json.dumps(records[:1],indent=2))
