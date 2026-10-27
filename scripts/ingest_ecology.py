"""Ingest the reviewed ecology seed list and report successes and gaps separately."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.ingest_goa_corpus import ROOT, fetch, now

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--retry-failed',action='store_true');args=parser.parse_args()
    seeds=json.loads((ROOT/'corpus/ecology-seeds.json').read_text());report=[]
    for seed in seeds:
        result=fetch(seed)
        # Retry transient transport failures, never evade robots, certificate errors or access restrictions.
        if args.retry_failed and result['status']=='failed' and any(x in result.get('error','') for x in ['Timeout','IncompleteRead','ConnectionError']):
            result=fetch(seed,retry=True)
        report.append({key:result.get(key) for key in ['url','title','title_hint','status','format','page_count','extraction_status','retrieved_at','error','sha256']})
        print(f'{len(report)}/{len(seeds)} {result["status"]}: {result["url"]}',flush=True)
    output={'generated_at':now(),'counts':dict(Counter(r['status'] for r in report)),'sources':report}
    (ROOT/'corpus/ecology-ingestion-report.json').write_text(json.dumps(output,indent=2))
    print(json.dumps(output['counts']),flush=True)
