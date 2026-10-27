"""Paired offline evaluation; entry through run_copy.py only."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import types
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scripts.evaluate_research_copy import is_preserved

def protected(path):
    return is_preserved(path) or Path(path).resolve().is_relative_to(Path.home()/'Documents/ActForGoa Recovery')
BASE='9d705d946cbdc55ad0d9bda4cfb9f243f76b177c'


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def baseline_module(name,path):
    source=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT,text=True)
    mod=types.ModuleType('backend.review_baseline_'+name)
    mod.__file__=str(ROOT/path);sys.modules[mod.__name__]=mod
    exec(compile(source,mod.__file__,'exec'),mod.__dict__)
    return mod


def supports(case,hits):
    if 'terms' in case:
        return any(any(t in (h['title']+' '+h['text']).lower() for t in case['terms']) for h in hits[:5])
    ids=[h['id'] for h in hits]
    ok=all(set(g['any_of'])&set(ids) for g in case['required_evidence'])
    if ok and case.get('fee_must_not_outrank_support') and case['fee_id'] in ids:
        ok=min(ids.index(i) for i in case['required_evidence'][0]['any_of'] if i in ids)<ids.index(case['fee_id'])
    return bool(ok)


def score(library,chat,case,hits):
    request=chat.ChatRequest(question=case['question'],answer_style='brief')
    prepared=chat.prepare_answer(request,hits) if hits else None
    selected=prepared.evidence if prepared else []
    ids=[h['id'] for h in selected]
    slices=True;links=True;duplicate=False;seen=[]
    for h in hits:
        page=library.pages(h['document_id'],h['generation'],h['page'],1)[0]
        slices &= page['text'][h['start']:h['end']]==h['text']
        url=urlsplit(h['reader_url']);qs=parse_qs(url.query)
        links &= (url.path=='/documents/'+h['document_id'] and qs.get('generation')==[h['generation']] and qs.get('page')==[str(h['page'])] and qs.get('passage')==[h['id']])
        words=re.findall(r'\w+',h['text'].lower());shingles=set(zip(words,words[1:]))
        duplicate |= bool(shingles) and any(len(shingles&s)/max(len(shingles|s),1)>.9 for s in seen)
        seen.append(shingles)
    size=len(json.dumps(prepared.messages,ensure_ascii=False,separators=(',',':')).encode()) if prepared else 0
    bounds=bool(prepared) and size<=24000 and prepared.input_token_bound==size+chat.FRAMING_TOKEN_ALLOWANCE
    schema=bool(prepared) and prepared.schema['properties']['paragraphs']['items']['properties']['citations']['items']['enum']==ids
    cap=max(Counter(h['document_id'] for h in hits).values(),default=0)<=2
    safety=slices and links and not duplicate and bounds and schema and cap
    return {'passed':supports(case,selected) and safety,'retrieved_support':supports(case,hits),
            'prompt_support':supports(case,selected),'safeguards_passed':safety,
            'passage_integrity':slices,'reader_locators_match':links,'near_duplicates':duplicate,
            'two_passage_cap':cap,'prompt_budget_passed':bounds,'schema_ids_match':schema,
            'prompt_bytes':size,'input_token_bound':prepared.input_token_bound if prepared else 0,
            'results':[{'id':h['id'],'document_id':h['document_id'],'title':h['title'],
                        'page':h['page'],'in_prompt':h['id'] in ids} for h in hits]}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--development-only',action='store_true');a=p.parse_args(argv)
    if protected(a.data_root) or protected(a.output):p.error('Use the disposable-copy wrapper')
    if a.output.exists():p.error('Keep previous evidence; use a fresh output path')
    # No native imports until path preservation checks pass.
    from backend.library import Library
    from backend import chat
    from scripts.evaluate_research import CASES
    old_library=baseline_module('library','backend/library.py');old_chat=baseline_module('chat','backend/chat.py')
    original=json.loads((ROOT/'reports/recovery-2026-10-27/retrieval-evidence-cases.json').read_text())
    prior=json.loads((ROOT/'reports/rti-offline-2026-10-27/held-out-cases.json').read_text())
    former=json.loads((ROOT/'reports/evidence-selection-2026-10-27/frozen-cases.json').read_text())
    cases=[{**c,'group':'original'} for c in original['cases']]
    cases += [{**c,'group':'prior','fee_id':prior['cases'][0]['required_any_of'][0],
               'required_evidence':[{'any_of':c['required_any_of']}]} for c in prior['cases']]
    cases += [{**c,'group':'previous_frozen'} for c in former['cases']]
    cases += [{'id':f'smoke-{i}','question':q,'terms':t,'group':'smoke'} for i,(q,t) in enumerate(CASES)]
    if not a.development_only:
        plan=json.loads((HERE/'candidate-freeze.json').read_text())
        for path,digest in plan['code_sha256'].items():assert sha(ROOT/path)==digest,path
        assert sha(HERE/'assessment-cases.json')==plan['assessment_sha256']
        assessment=json.loads((HERE/'assessment-cases.json').read_text())
        cases += [{**c,'group':'assessment'} for c in assessment['cases']]
    library=Library(a.data_root);assert library.generation==original['generation']==prior['generation']==former['generation']
    expected={i for c in cases for g in c.get('required_evidence',[]) for i in g['any_of']}
    originals={}
    with library.connect() as db:
        for pid in expected:
            row=db.execute('SELECT * FROM chunks WHERE id=?',(pid,)).fetchone();assert row is not None,pid
            page=library.pages(row['doc_id'],start=row['page'],limit=1)[0]
            assert page['text'][row['start']:row['end']]==row['text']
            if row['doc_id'] not in originals:
                path,meta=library.original(row['doc_id']);assert sha(path)==meta['sha256']
                pages=library.pages(row['doc_id'],start=1,limit=meta['page_count'])
                assert len(pages)==meta['page_count']
                originals[row['doc_id']]={'original_sha256':meta['sha256'],'title':meta['title'],'pages':len(pages),'full_saved_text_checked':True}
        for case in cases:
            for review in case.get('source_review',[]):
                row=db.execute('SELECT * FROM chunks WHERE id=?',(review['passage_id'],)).fetchone()
                assert all(row[k]==review[k] for k in ['page','start','end'])
                assert row['doc_id']==review['document_id'] and row['text']==review['reviewed_text']
                assert hashlib.sha256(row['text'].encode()).hexdigest()==review['text_sha256']
                assert originals[row['doc_id']]['original_sha256']==review['original_sha256']
    results=[]
    for case in cases:
        limit=8 if case['group']=='smoke' else 10
        start=time.perf_counter();before=old_library.Library.search(library,case['question'],limit);base_seconds=time.perf_counter()-start
        start=time.perf_counter();after=library.search(case['question'],limit);new_seconds=time.perf_counter()-start
        row={'id':case['id'],'group':case['group'],'question':case['question'],
             'baseline':score(library,old_chat,case,before),
             'compaction_only':score(library,chat,case,before),
             'selection_only':score(library,old_chat,case,after),
             'candidate':score(library,chat,case,after),
             'baseline_seconds':base_seconds,'candidate_seconds':new_seconds}
        results.append(row)
    groups=list(dict.fromkeys(r['group'] for r in results));modes=['baseline','compaction_only','selection_only','candidate']
    summary={g:{'total':sum(r['group']==g for r in results),**{m:sum(r['group']==g and r[m]['passed'] for r in results) for m in modes}} for g in groups}
    regressions=[r['id'] for r in results if r['baseline']['passed'] and not r['candidate']['passed']]
    failures=[r['id'] for r in results if not r['candidate']['passed']]
    safety=all(r[m]['safeguards_passed'] for r in results for m in modes)
    gate=not regressions and safety and summary['original']['candidate']==9 and summary['smoke']['candidate']==16
    report={'created_at':datetime.now(timezone.utc).isoformat(),'candidate_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'baseline_commit':BASE,'generation':library.generation,'assessment_run':not a.development_only,
            'summary':summary,'regressions':regressions,'candidate_failures':failures,
            'all_safeguards_passed':safety,'repair_gate_passed':gate,'full_document_checks':originals,
            'results':results,'provider_calls':0,'genuine_usage_operations':0,
            'limits':'Known 9+15+20 cases were iterated on. Frozen 12 are used once only after candidate freeze. Exact evidence recall is not answer entailment or legal currency. Runtime and metadata contract changes still require live provider acceptance. Source originals and indexes are copied before native access.'}
    assert not (a.data_root/'.research-usage').exists()
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['summary','regressions','candidate_failures','all_safeguards_passed','repair_gate_passed']}))
    return 0 if gate else 1

if __name__=='__main__':sys.exit(main())
