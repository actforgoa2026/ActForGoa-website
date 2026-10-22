"""Prioritize all 24 publicly linked library archive pages, then their records."""
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit
from crawl import BASE, fetch, body, links, save, EDGES
pages={BASE+'/resource/'}
seen=set()
records=set()
with ThreadPoolExecutor(max_workers=3) as pool:
    while pages-seen:
        batch=sorted(pages-seen)
        for item in pool.map(fetch,batch):
            seen.add(item['url'])
            for url in links(body(item),item['url']):
                if url.startswith(BASE+'/resource/page/'):pages.add(url)
                elif url.startswith(BASE+'/resource/') and url!=BASE+'/resource/':records.add(url)
    print('Archive pages',len(seen),'resources',len(records),flush=True)
    for i,item in enumerate(pool.map(fetch,sorted(records))):
        links(body(item),item['url'])
        if i%30==0:print('Resources',i,flush=True)
save('library-links.json',EDGES)
