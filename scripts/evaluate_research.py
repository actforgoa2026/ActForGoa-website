"""Live local-corpus checks: retrieval relevance, evidence identity and original integrity."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.library import Library

CASES=[
 ('How do khazans manage saline water with sluice gates?', ['khazan','khazans']),
 ('How do laterite plateaus supply groundwater and springs?', ['laterit','spring']),
 ('What is Goa State Water Policy 2021?', ['water policy']),
 ('What does the climate action plan say about rainfall and flooding?', ['climate','rainfall']),
 ('What are Goa monsoon rainfall trends?', ['rainfall','monsoon']),
 ('What is the Mhadei Mandovi river basin?', ['mandovi','mhadei','mahadayi']),
 ('What are the habitats of Cnemaspis goaensis?', ['cnemaspis']),
 ('What is the bird diversity of Goa?', ['bird','avifauna']),
 ('What are threats to sacred groves in Goa?', ['sacred']),
 ('Where do olive ridley turtles nest in Goa?', ['turtle','ridley']),
 ('What causes forest fires in Goa?', ['fire']),
 ('What are the impacts of mining on groundwater?', ['mining','groundwater']),
 ('How is water quality monitored by GSPCB?', ['water quality','monitoring']),
 ('What does Goa agriculture policy say about farming?', ['agriculture','agricultural']),
 ('What is the pre-monsoon groundwater level in Goa in 2025?', ['groundwater','ground water']),
 ('What is Goa forest cover in the India State of Forest Report?', ['forest cover','forest report']),
]

def evaluate():
    lib=Library();checks=[];failures=[]
    for query,expected in CASES:
        hits=lib.search(query,8)
        relevant=any(any(word in (h['title']+' '+h['text']).lower() for word in expected) for h in hits[:5])
        integrity=True
        for hit in hits:
            pages=lib.pages(hit['document_id'],hit['generation'],hit['page'],1)
            integrity &= bool(pages and pages[0]['text'][hit['start']:hit['end']]==hit['text'])
        item={'query':query,'expected_term_in_top5':relevant,'passage_integrity':integrity,'results':[{'title':h['title'],'source':h['url'],'page':h['page'],'matches':h['matches']} for h in hits[:5]]}
        checks.append(item)
        if not relevant or not integrity:failures.append(query)
    originals=[]
    with lib.connect() as db:
        documents=[json.loads(r['metadata']) for r in db.execute('SELECT metadata FROM documents')]
    for doc in documents:
        path,meta=lib.original(doc['id']);valid=hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256']
        if not valid:failures.append('Original checksum: '+doc['id'])
        originals.append(valid)
    report={'generation':lib.generation,'checks':checks,'queries_passed':sum(c['expected_term_in_top5'] and c['passage_integrity'] for c in checks),
            'queries_total':len(checks),'original_checksums_passed':sum(originals),'originals_total':len(originals),'failures':failures,
            'limits':'Top-five term coverage is a retrieval smoke check, not a factual-answer or entailment benchmark. Live OpenAI generation is a separate check.'}
    Path('reports').mkdir(exist_ok=True);Path('reports/research-evaluation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({key:value for key,value in report.items() if key!='checks'},indent=2))
    return 1 if failures else 0
if __name__=='__main__':sys.exit(evaluate())
