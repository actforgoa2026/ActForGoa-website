"""Produce an honest coverage report, source inventory, form map, and compact archives."""
import csv,gzip,json,re,sqlite3,tarfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from crawl import ROOT,CACHE,body,canonical,save

pages=[];forms=[];fragment_issues=[];extra_edges=[]
for url,r in CACHE.items():
 if 'text/html' not in r.get('content_type','') or not r.get('path'):continue
 s=BeautifulSoup(body(r),'lxml')
 pages.append({'url':url,'status':r.get('status'),'title':s.title.get_text(' ',strip=True) if s.title else '', 'path':r['path'],'bytes':r.get('bytes',0),'sha256':r.get('sha256',''),'softError':bool(re.search('There has been a critical error on this website',body(r)))})
 for f in s.select('form'):
  forms.append({'source':url,'action':f.get('action',''),'method':f.get('method','get'),'fields':[{'name':e.get('name',''),'type':e.get('type',e.name),'required':e.has_attr('required')} for e in f.select('input,select,textarea') if e.get('type')!='hidden']})
 ids={e.get('id') for e in s.select('[id]')}|{e.get('name') for e in s.select('a[name]')}
 for a in s.select('a[href^="#"]'):
  raw=a['href'];extra_edges.append({'source':url,'target':url,'fragment':raw[1:],'raw':raw,'relation':'fragment','text':a.get_text(' ',strip=True)[:200]})
  if len(raw)>1 and raw[1:] not in ids:fragment_issues.append({'source':url,'fragment':raw[1:],'label':a.get_text(' ',strip=True)[:150],'classification':'missing-static-anchor-may-be-script-controlled'})
save('page-inventory.json',pages);save('forms.json',forms);save('fragment-audit.json',fragment_issues)
save('fetch-manifest.json',list(CACHE.values()))
with (ROOT/'reports/page-inventory.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(pages[0]));w.writeheader();w.writerows(pages)
for name in ['links.json','library-links.json','fetch-manifest.json']:
 p=ROOT/'data'/name
 if p.exists():
  with gzip.open(str(p)+'.gz','wb',compresslevel=9) as out:out.write(p.read_bytes())
with gzip.open(ROOT/'data/fragment-links.json.gz','wt') as f:json.dump(extra_edges,f)
summary=json.loads((ROOT/'data/catalog-summary.json').read_text())
audit=json.loads((ROOT/'data/link-audit-summary.json').read_text())
docs=json.loads((ROOT/'data/documents.json').read_text())
counts=Counter(str(r.get('status')) for r in CACHE.values())
total_bytes=sum(r.get('bytes',0) for r in CACHE.values())
coverage={'fetchedURLs':len(CACHE),'httpStatuses':dict(counts),'archivedBytes':total_bytes,'htmlResponses':len(pages),'usableHtmlResponses':sum(p['status']==200 and not p['softError'] for p in pages),'forms':len(forms),'staticFragmentIssues':len(fragment_issues),'documentsWithExtractedText':sum(bool(d.get('textPath')) for d in docs),'catalogue':summary,'linkAudit':audit}
save('coverage.json',coverage)
lines=['# Archive coverage and findings','', 'Snapshot: 22 October 2026. Public, read-only crawl of https://actforgoa.org/.','',
 f'- {len(CACHE):,} distinct fetched URLs; {total_bytes/1024**3:.2f} GiB of response bodies.',
 f'- {len(pages):,} HTML responses, including failures and legacy attachment pages.',
 f'- {summary["records"]:,} searchable records: '+', '.join(f'{v} {k}' for k,v in summary['byKind'].items())+'.',
 f'- {summary["documents"]} linked document references; {coverage["documentsWithExtractedText"]} with extracted PDF text.',
 f'- {sum(audit.values()):,} unique linked destinations audited. See LINK-AUDIT.md and link-audit.csv.',
 '', '## Important findings','',
 '- The pages API fails when it renders legacy page content. A metadata-only field selection recovered 152 public page records; HTML supplies their content.',
 '- The Connections directory API fails in its default rendering path. Selecting public contact fields and paginating with offset recovered 104 entries. Its page parameter repeats the first page; offset 100 yielded the final 4 entries.',
 '- The public media API reports 2,207 records in its total header but actually returns 1,288 unique records across all 23 pages. This discrepancy remains unresolved; no private or authenticated endpoint was accessed. Linked responsive images, CSS and document traversal expand asset coverage independently.',
 '- The library has 24 archive pages and 237 recovered resources.',
 '- The snake rescue list is dated 22 October 2018. Its 49 named contact rows are indexed separately; current availability is not verified. Seven-digit local numbers are preserved as text, without inventing an area code.',
 '- Original relative footer links such as community and greenviksitgoa resolve beneath individual article URLs, creating thousands of questionable destinations. These are retained in the graph; many return access restrictions, which are not labelled confirmed dead.',
 '- The site contains old theme examples, shop/account pages, exposed shortcode text, a placeholder email address, and old staging links. 56 template/account pages are explicitly excluded from the rebuilt public search but remain archived.',
 '- Some HTTP 200 responses contain WordPress critical errors. These are classified as soft errors separately from genuine successes.',
 '', '## Boundaries and incomplete coverage','',
 'This is a deep public snapshot, not a claim to have recovered the private WordPress database. Robots exclusions, calendar loops, authenticated endpoints, login flows, form submissions, donation actions, query traps, syndication duplicates, and response bodies above 80 MiB were excluded. Third-party sites were link-checked, not recursively crawled. Linked documents were archived where accessible. JavaScript-only private community content, social-platform posts behind restrictions, and unlinked files are outside coverage.',
 '', 'PDF text extraction is best-effort; scanned pages have not been OCRed. Semantic indexing includes at most the first 3,200 words of each record/document aggregate; full extracted text remains in the local data folder and SQLite FTS index. Titles and wording are source material and can contain historical or inaccurate claims.',
 '', 'Missing static anchors are candidates for review, not automatically broken links: some are controlled by the original JavaScript. See data/fragment-audit.json.',
 '', '## Files','',
 '- `archive/raw/`, `archive/assets/`: exact bodies, locally retained, named by URL hash.',
 '- `archive/manifests/fetches.jsonl`: append-only fetch evidence with timestamps, status, redirects, checksums, and paths.',
 '- `archive/site-responses.tar.gz`: portable copy of raw HTML/API/sitemap responses and fetch manifest.',
 '- `data/fetch-manifest.json.gz`: latest metadata per URL.',
 '- `data/links.json.gz`, `data/library-links.json.gz`, `data/fragment-links.json.gz`: link graph including raw references and referring pages.',
 '- `data/catalog.sqlite`, `data/catalog.json`: normalized catalogue and contact/topic/document tables.',
 '- `data/document-text/`: extracted PDFs; `data/forms.json`: original form field inventory. Forms were not submitted.',
 '- `reports/page-inventory.csv`, `reports/link-audit.csv`: reviewable inventories.',
 '', '## Reproduction','',
 'Create the Python environment, install requirements, run `npm run crawl`, then run `scripts/recover_directory.py`, `scripts/crawl_library.py`, `npm run extract`, `npm run audit:links`, `scripts/inventory.py`, and `npm run index:semantic`. Fetches resume from the manifest. Cached successes are reused; use a new archive directory for a fresh-date crawl.',
]
(ROOT/'reports/CRAWL-REPORT.md').write_text('\n'.join(lines))
print(json.dumps(coverage,indent=2))
