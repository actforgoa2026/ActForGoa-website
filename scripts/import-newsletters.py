"""Import the five issues linked by ActForGoa's original newsletter archive.
No tracking pixels, scripts, mailing-list forms or subscriber tokens are retained.
Run from the repository root. Requires only Python's standard library.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from hashlib import sha256
import json, re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public' / 'assets' / 'newsletters'
PUBLIC.mkdir(parents=True,exist_ok=True)
ISSUES = [
 ('2025-year-end', 'Year-end newsletter 2024–2025', '2025', 'A four-page illustrated review of Act for Goa’s work in 2024 and 2025.', 'https://actforgoa.org/wp-content/uploads/2026/03/2024-2025-Act-for-Goa-Year-End-Newsletter.pdf'),
 ('2022-december', 'Taking action for Goa', 'December 2022', 'Community recognition, the Goa Climate Series and projects supporting the environment.', 'https://mailchi.mp/eb66242be2b6/k7ncfe5st3'),
 ('2022-august', 'A guide to the panchayat elections', 'August 2022', 'The original voter information issue published ahead of Goa’s 2022 village panchayat elections.', 'https://mailchi.mp/4f827fac9f80/panchayat-elections-are-this-wednesday-heres-what-you-need-to-know-16519023'),
 ('2022-july', 'Stay informed, take action', 'July 2022', 'World Environment Day clean-ups and other community initiatives around Goa.', 'https://mailchi.mp/17f3965c491d/act-for-goa-stay-informed-take-action-16513439'),
 ('2022-april', 'Act for Goa’s first newsletter', 'April 2022', 'An introduction to the shared platform and its early activities.', 'https://mailchi.mp/56c61bdf0566/actforgoas-first-newsletter-16099003'),
]
class Node:
 def __init__(self, tag='', attrs=None):self.tag=tag;self.attrs=dict(attrs or []);self.children=[]
class Tree(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root]
 def handle_starttag(self,tag,attrs):
  node=Node(tag,attrs);self.stack[-1].children.append(node)
  if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(node)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==tag:self.stack=self.stack[:i];break
 def handle_data(self,data):self.stack[-1].children.append(data)
def find(node,predicate):
 if isinstance(node,str):return None
 if predicate(node):return node
 for child in node.children:
  found=find(child,predicate)
  if found:return found
 return None
def clean_url(url):
 p=urlsplit(url)
 if p.scheme not in {'https','http','mailto'}:return ''
 return urlunsplit((p.scheme,p.netloc,p.path,urlencode([(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith(('utm_','mc_'))]),p.fragment))
def fetch(url):
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as response:
  if response.status!=200:raise RuntimeError(f'{url}: {response.status}')
  return response.read(),response.headers.get_content_type()
def convert(node,issue,images):
 if isinstance(node,str):return node
 if node.tag in {'script','style','form','input','button'}:return ''
 if node.tag=='img':
  src=node.attrs.get('src','');alt=node.attrs.get('alt','')
  try:width=float(node.attrs.get('width',0))
  except ValueError:width=0
  if width<180 or 'mailchimp' in alt.lower() or 'rewards' in src:return ''
  image_id=sha256(src.encode()).hexdigest()[:16]
  data,kind=fetch(src)
  ext={'image/png':'.png','image/jpeg':'.jpg','image/webp':'.webp','image/gif':'.gif'}.get(kind)
  if not ext:return ''
  filename=issue+'-'+image_id+ext;(PUBLIC/filename).write_bytes(data)
  images.append({'path':'/assets/newsletters/'+filename,'source':src,'sha256':sha256(data).hexdigest(),'copyright':'Original ActForGoa newsletter image; retained with its source.'})
  return '\n\n!['+(alt or 'Illustration from the original newsletter')+'](/assets/newsletters/'+filename+')\n\n'
 text=''.join(convert(c,issue,images) for c in node.children)
 if node.tag=='a':
  href=clean_url(node.attrs.get('href',''))
  if any(x in href for x in ['unsubscribe','update-profile','preferences','list-manage.com']):return ''
  return '['+text.strip()+']('+href+')' if href and text.strip() else text
 if node.tag=='br':return '\n'
 if node.tag in {'h1','h2','h3','h4'}:return '\n\n## '+text.strip()+'\n\n'
 if node.tag in {'p','div','tr'}:return '\n\n'+text.strip()+'\n\n'
 if node.tag=='li':return '\n- '+text.strip()+'\n'
 if node.tag=='strong':return '**'+text.strip()+'**' if text.strip() else ''
 return text

def main():
 records=[];manifest=[]
 cache=ROOT/'.reports/dev/newsletters'
 for issue,title,date,summary,url in ISSUES:
  suffix='.pdf' if url.endswith('.pdf') else '.html'
  cached=cache/(issue+suffix)
  raw=cached.read_bytes() if cached.exists() else fetch(url)[0]
  record={'id':issue,'title':title,'date':date,'year':date[-4:],'summary':summary,'source':url,'checkedOn':'2026-10-29'}
  if suffix=='.pdf':
   (PUBLIC/(issue+suffix)).write_bytes(raw);record['pdf']='/assets/newsletters/'+issue+suffix
   transcription=ROOT/'src/content/newsletter-text'/(issue+'.md')
   if transcription.exists():record['markdown']=transcription.read_text()
  else:
   tree=Tree();tree.feed(raw.decode());body=find(tree.root,lambda n:n.attrs.get('id')=='root')
   if not body:raise RuntimeError('Missing campaign body: '+issue)
   images=[];markdown=convert(body,issue,images)
   markdown=re.sub(r'\n[ \t]+','\n',markdown);markdown=re.sub(r'\n{3,}','\n\n',markdown).strip()
   markdown=markdown.split('Want to change how you receive these emails?')[0].strip()
   markdown=markdown.replace('<<First Name>>','reader').replace('**NEWSLETTER**','')
   markdown=re.sub(r'^## ([A-Z][A-Z &]+)$',lambda m:'## '+m[1].capitalize(),markdown,flags=re.M)
   markdown=re.sub(r'^\s*(?:\*\*December 2022\*\*|## 25th July 2022)\s*$', '', markdown, flags=re.M)
   markdown=markdown.replace('Aggregating information for citizens to contribute to Goa’s sustainable development','')
   markdown=re.sub(r'\n{3,}','\n\n',markdown).strip()
   record['markdown']=markdown
   manifest.extend(images)
  records.append(record)
  manifest.append({'path':'/assets/newsletters/'+issue+suffix if suffix=='.pdf' else 'src/content/newsletters.json#'+issue,'source':url,'sha256':sha256(raw).hexdigest(),'retrievedOn':'2026-10-29','status':200})
 (ROOT/'src/content/newsletters.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 previous_manifest=PUBLIC/'provenance.json'
 if previous_manifest.exists():
  previous=json.loads(previous_manifest.read_text())
  manifest.extend(asset for asset in previous.get('assets',[]) if asset.get('page') and (ROOT/'public'/asset['path'].lstrip('/')).exists())
 (PUBLIC/'provenance.json').write_text(json.dumps({'archiveSource':'https://actforgoa.org/newsletters/','retrievedOn':'2026-10-29','note':'Public ActForGoa archive. Original historical wording and article links retained; mailing-list controls and tracking pixels omitted. Images kept from the original newsletter; copyright remains with original creators.','assets':manifest,'transcription':{'path':'src/content/newsletter-text/2025-year-end.md','method':'Transcribed from all four rendered source PDF pages and checked visually. Heading case and reading order normalized; historical wording and spellings retained. Illustrations remain in the original-layout disclosure.','checkedOn':'2026-10-29'}},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'issues':len(records),'assets':len(manifest),'markdownCharacters':sum(len(x.get('markdown','')) for x in records)}))
if __name__=='__main__':main()
