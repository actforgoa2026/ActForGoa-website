"""Read-only end-to-end checks of a running research API; never calls a paid provider."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.error
from urllib.parse import urlencode

CASES = [
    ('How do khazans manage fresh and salt water?', ['khazan']),
    ('How do laterite plateaus supply groundwater and springs?', ['laterit', 'spring']),
    ('What is Goa State Water Policy 2021?', ['water policy']),
    ('What does the climate action plan say about rainfall and flooding?', ['climate', 'rainfall']),
    ('What is the Mhadei Mandovi river basin?', ['mandovi', 'mhadei', 'mahadayi']),
    ('What are the habitats of Cnemaspis goaensis?', ['cnemaspis']),
]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('origin')
    parser.add_argument('--frontend',action='store_true',help='Verify same-origin API rewrites; healthz belongs only to the backend origin.')
    parser.add_argument('--output',type=Path,default=Path('reports/research-release/http-verification.json'))
    args=parser.parse_args();origin=args.origin.rstrip('/')
    def get(path):
        with urllib.request.urlopen(origin+path,timeout=120) as response:
            return response.read(),{key.lower():value for key,value in response.headers.items()}
    def data(path):return json.loads(get(path)[0])
    status=data('/api/status');assert status['search_ready']
    assert status['search_mode']=='zvec+fts5+rrf'
    if not args.frontend:assert data('/healthz')['ready']
    checks=[];sample=None
    for query,terms in CASES:
        hits=data('/api/search?'+urlencode({'q':query,'limit':5}))['results']
        assert hits and any(any(t in (h['title']+' '+h['text']).lower() for t in terms) for h in hits)
        for hit in hits:
            suffix='?'+urlencode({'generation':hit['generation']})
            base='/api/documents/'+hit['document_id']
            page=data(base+'/pages'+suffix+'&start='+str(hit['page'])+'&limit=1')['pages'][0]
            assert page['text'][hit['start']:hit['end']]==hit['text']
            assert data(base+'/passages/'+hit['id']+suffix)['text']==hit['text']
        checks.append({'question':query,'passages_verified':len(hits),'titles':[h['title'] for h in hits]})
        if 'Water Policy' in query:sample=next(h for h in hits if 'Water Policy' in h['title'])
    assert sample
    base='/api/documents/'+sample['document_id'];suffix='?'+urlencode({'generation':sample['generation']})
    doc=data(base+suffix)
    original,headers=get(doc['original_url'])
    assert hashlib.sha256(original).hexdigest()==doc['sha256']
    assert original.startswith(b'%PDF') and 'attachment' in headers.get('content-disposition','')
    fulltext,_=get(doc['text_url'])
    assert fulltext.count(b'=== PDF page ')==doc['page_count']
    page_image,_=get(base+'/pages/'+str(sample['page'])+'/image'+suffix)
    assert page_image.startswith(b'\x89PNG\r\n\x1a\n')
    chat='configured; not invoked by this read-only test'
    if not status['chat_ready']:
        request=urllib.request.Request(origin+'/api/chat',data=json.dumps({'question':CASES[0][0]}).encode(),headers={'Content-Type':'application/json'})
        try:urllib.request.urlopen(request,timeout=30);raise AssertionError('Unconfigured chat must return 503')
        except urllib.error.HTTPError as error:
            assert error.code==503
            chat=json.loads(error.read())['detail']
    report={'origin':origin,'generation':status['generation'],'status':status,'queries':checks,
        'original_verified':{'id':doc['id'],'sha256':doc['sha256'],'bytes':len(original),'pages':doc['page_count']},
        'full_text_pages_verified':doc['page_count'],'original_page_png_verified':True,'chat':chat,
        'limits':'Retrieval and citation identity checks, not a live generated-answer or factual-entailment evaluation.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'origin':origin,'generation':status['generation'],'queries_passed':len(checks),'documents':status['stats'].get('documents'),'chat_ready':status['chat_ready'],'original_bytes':len(original),'full_text_pages':doc['page_count']},indent=2))

if __name__=='__main__':main()
