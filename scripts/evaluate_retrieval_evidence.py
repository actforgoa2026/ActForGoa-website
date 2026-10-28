"""Offline retrieval gates. Never constructs a provider client or generates an answer."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.chat import ChatRequest, prepare_answer
from backend.library import Library
from scripts.evaluate_research import CASES
from scripts.evaluate_research_copy import is_preserved


def passage_integrity(library, hits):
    for hit in hits:
        pages=library.pages(hit['document_id'],hit['generation'],hit['page'],1)
        if not pages or pages[0]['text'][hit['start']:hit['end']]!=hit['text']:
            return False
    return True


def evaluate_case(library, case):
    request=ChatRequest(**{key:case[key] for key in ('question','answer_style','history','document_id','generation') if key in case})
    previous=next((m.content for m in reversed(request.history) if m.role=='user'),'')
    query=request.question+(' '+previous[:500] if len(request.question.split())<8 else '')
    start=time.monotonic()
    hits=library.search(query,10,request.document_id,request.generation)
    prepared=prepare_answer(request,hits).evidence if hits else []
    elapsed=time.monotonic()-start
    retrieved_ids={hit['id'] for hit in hits};prepared_ids={hit['id'] for hit in prepared}
    groups=[{'name':group['name'],'any_of':group['any_of'],
             'retrieved':bool(retrieved_ids.intersection(group['any_of'])),
             'in_model_prompt':bool(prepared_ids.intersection(group['any_of']))}
            for group in case['required_evidence']]
    integrity=passage_integrity(library,hits)
    return {'id':case['id'],'question':request.question,'seconds':round(elapsed,4),
            'passed':bool(groups) and integrity and all(g['in_model_prompt'] for g in groups),
            'passage_integrity':integrity,'required_evidence':groups,
            'results':[{'id':h['id'],'title':h['title'],'page':h['page'],'in_model_prompt':h['id'] in prepared_ids} for h in hits]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',type=Path,required=True)
    parser.add_argument('--cases',type=Path,default=ROOT/'tests/research/retrieval-evidence-cases.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if is_preserved(args.data_root) or is_preserved(args.output):
        parser.error('Do not open or write inside preservation snapshots or sealed packages. Use scripts/evaluate_research_copy.py and write reports outside the preserved directory.')
    spec=json.loads(args.cases.read_text());library=Library(args.data_root)
    if library.generation!=spec['generation']:
        parser.error('Evidence cases belong to a different corpus generation; review the source locators before updating them.')
    # Catch stale/typoed expectations rather than treating them as ranking failures.
    with library.connect() as db:
        for case in spec['cases']:
            for group in case['required_evidence']:
                if not group['any_of']:parser.error('Evidence groups must contain at least one reviewed passage ID.')
                for identifier in group['any_of']:
                    if not db.execute('SELECT 1 FROM chunks WHERE id=?',(identifier,)).fetchone():
                        parser.error('Reviewed passage is missing from this corpus: '+identifier)
    results=[evaluate_case(library,case) for case in spec['cases']]
    smoke=[]
    for query,terms in CASES:
        hits=library.search(query,8)
        relevant=any(any(term in (h['title']+' '+h['text']).lower() for term in terms) for h in hits[:5])
        smoke.append({'query':query,'expected_term_in_top5':relevant,'passage_integrity':passage_integrity(library,hits)})
    passed=sum(r['passed'] for r in results);smoke_passed=sum(r['expected_term_in_top5'] and r['passage_integrity'] for r in smoke)
    report={'generation':library.generation,'provider_calls':0,'cases':results,'smoke':smoke,
            'summary':{'evidence_cases_passed':passed,'evidence_cases_total':len(results),'smoke_passed':smoke_passed,'smoke_total':len(smoke)},
            'limits':'Checks recall of reviewed evidence and exact passage slices, including prompt budgeting. A failure may indicate another valid supporting passage needs review. Passing does not establish answer entailment, current law or live acceptance. Original checksums are not repeated.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['summary']))
    return 0 if passed==len(results) and smoke_passed==len(smoke) else 1


if __name__=='__main__':sys.exit(main())
