"""Paid, real-corpus chat checks. Mechanical citation checks require human claim review."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlsplit
import httpx

ROOT=Path(__file__).resolve().parents[1]

def run(origin, output, cases):
    report={'origin':origin,'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
            'verification':'Live provider; citation identity and file integrity only. Human entailment review required.',
            'cases':[]}
    checked_originals={}
    def save():
        output.parent.mkdir(parents=True,exist_ok=True)
        temporary=output.with_suffix('.tmp');temporary.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');temporary.replace(output)
    def local_path(path):
        url=urlsplit(path)
        if url.scheme or url.netloc or not path.startswith('/api/documents/'):
            raise ValueError('Unexpected document endpoint')
        return path
    with httpx.Client(base_url=origin,timeout=150,follow_redirects=False) as client:
        status=client.get('/api/status');status.raise_for_status();report['service']=status.json()
        if not report['service'].get('chat_ready'):raise SystemExit('Live chat is not configured; no model requests sent.')
        for index,case in enumerate(cases):
            started=time.monotonic();entry={**case,'human_review':'pending'}
            try:
                response=client.post('/api/chat',json={k:case[k] for k in ('question','history') if k in case})
                entry['http_status']=response.status_code
                if response.status_code!=200:
                    entry['passed']=False;entry['error']='Chat request did not return an answer.'
                else:
                    answer=response.json();entry['answer']=answer
                    citations={c['id']:c for c in answer['citations']}
                    if answer['status']=='answered':
                        assert answer['paragraphs'] and citations,'Answered without cited paragraphs'
                        assert all(p['text'].strip() and p['citations'] and set(p['citations'])<=citations.keys() for p in answer['paragraphs'])
                    else:
                        assert answer['status']=='insufficient_evidence' and not answer['paragraphs'] and not citations
                    for cite in citations.values():
                        params={'generation':cite['generation']}
                        base='/api/documents/'+cite['document_id']
                        document=client.get(base,params=params);document.raise_for_status();doc=document.json()
                        pages=client.get(base+'/pages',params={**params,'start':cite['page'],'limit':1});pages.raise_for_status()
                        assert cite['text'] in pages.json()['pages'][0]['text'],'Passage mismatch'
                        reader=urlsplit(cite['reader_url']);assert not reader.scheme and not reader.netloc and reader.path=='/documents/'+cite['document_id']
                        version=(cite['document_id'],cite['generation'])
                        if version not in checked_originals:
                            text=client.get(local_path(doc['text_url']));text.raise_for_status();assert text.text.strip()
                            digest=hashlib.sha256()
                            with client.stream('GET',local_path(doc['original_url'])) as original:
                                original.raise_for_status()
                                for block in original.iter_bytes():digest.update(block)
                            assert digest.hexdigest()==doc['sha256'],'Original checksum mismatch'
                            checked_originals[version]=True
                    entry['passed']=True
                    entry['abstention_matches_expectation']=(answer['status']=='insufficient_evidence') if case.get('expect_abstention') else None
            except (httpx.HTTPError,AssertionError,ValueError,KeyError) as error:
                entry.update(passed=False,error=type(error).__name__)
            entry['seconds']=round(time.monotonic()-started,2);report['cases'].append(entry)
            report['summary']={'completed':len(report['cases']),'mechanical_passes':sum(c['passed'] for c in report['cases']),
                               'originals_verified':len(checked_originals),'human_review':'pending'}
            save();print(f"{index+1}/{len(cases)} {case['id']}: {'pass' if entry['passed'] else 'FAIL'} ({entry['seconds']}s)",flush=True)
            if entry.get('http_status') in (401,402,429,502,503):break
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin',default='http://127.0.0.1:8091')
    parser.add_argument('--output',type=Path,default=ROOT/'reports/research-live-chat.json')
    parser.add_argument('--limit',type=int,default=50)
    args=parser.parse_args()
    origin=args.origin.rstrip('/');url=urlsplit(origin)
    if url.username or url.password or url.query or url.fragment or url.path or url.scheme not in ('http','https'):
        parser.error('Use a plain research service origin without credentials or a path')
    if url.scheme=='http' and url.hostname not in ('127.0.0.1','localhost'):
        parser.error('Remote live evaluation requires HTTPS')
    if not 1<=args.limit<=50:parser.error('--limit must be between 1 and 50')
    cases=json.loads((ROOT/'tests/research/goa-chat-cases.json').read_text())[:args.limit]
    result=run(origin,args.output,cases)
    raise SystemExit(0 if len(result['cases'])==len(cases) and all(c['passed'] for c in result['cases']) else 1)
