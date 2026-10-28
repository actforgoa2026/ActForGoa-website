"""Offline paired retrieval/context review on an explicitly disposable index."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.evaluate_research_copy import is_preserved


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_baseline(name,path,commit,rewrite=None):
    source=subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT,text=True)
    if rewrite:
        source=source.replace(*rewrite)
    module=types.ModuleType('backend.source_context_baseline_'+name)
    module.__file__=str(ROOT/path)
    sys.modules[module.__name__]=module
    exec(compile(source,module.__file__,'exec'),module.__dict__)
    return module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--baseline',default='3f18ffa064b1729a5a65bcd3b350509a9c351193')
    parser.add_argument('--captured-answers',type=Path)
    args=parser.parse_args()
    data=args.data_root.resolve()
    for path in (data,args.output.resolve()):
        if is_preserved(path) or path.is_relative_to(Path.home()/'Documents/ActForGoa Recovery'):
            parser.error('Use an approved disposable copy; never open preservation sources natively')
    if args.output.exists():
        parser.error('Preserve previous evidence; choose a new output path')
    marker=json.loads((data/'.acceptance-disposable.json').read_text())
    if marker.get('disposable_for_acceptance') is not True:
        parser.error('An explicitly marked acceptance copy is required')
    for key in list(os.environ):
        if key.startswith(('RESEARCH_','ANTHROPIC_','OPENAI_','OPENROUTER_','DASHSCOPE_','QWEN_')):
            del os.environ[key]
    # Native imports happen only after preservation and marker checks.
    from backend.library import Library
    from backend import chat
    from backend.anthropic_provider import message_request, native_answer_schema
    from backend.providers import ChatConfig
    from scripts.evaluate_research import CASES
    evaluation_path=ROOT/'reports/passage-selection-2026-10-27/evaluate.py'
    spec=importlib.util.spec_from_file_location('source_context_scoring',evaluation_path)
    scoring=importlib.util.module_from_spec(spec);spec.loader.exec_module(scoring)
    old_library=load_baseline('library','backend/library.py',args.baseline)
    old_adapter=load_baseline('adapter','backend/anthropic_provider.py',args.baseline)
    old_chat=load_baseline('chat','backend/chat.py',args.baseline,
                         ('from .anthropic_provider import','from .source_context_baseline_adapter import'))
    packets=[('original','reports/recovery-2026-10-27/retrieval-evidence-cases.json'),
             ('prior','reports/rti-offline-2026-10-27/held-out-cases.json'),
             ('previous_frozen','reports/evidence-selection-2026-10-27/frozen-cases.json'),
             ('consumed_assessment','reports/passage-selection-2026-10-27/assessment-cases.json')]
    cases=[]
    for group,path in packets:
        payload=json.loads((ROOT/path).read_text())
        assert payload['generation']==marker['generation']
        for case in payload['cases']:
            row={**case,'group':group}
            if group=='prior':
                row['required_evidence']=[{'any_of':case['required_any_of']}]
                row['fee_id']=payload['cases'][0]['required_any_of'][0]
            cases.append(row)
    cases += [dict(id=f'smoke-{i}',question=q,terms=terms,group='smoke') for i,(q,terms) in enumerate(CASES)]
    assert len(cases)==72
    library=Library(data)
    assert library.generation==marker['generation']
    config=ChatConfig('anthropic','claude-sonnet-5-5','Anthropic','ANTHROPIC_API_KEY',
                      'https://api.anthropic.com/v1',max_output_tokens=9000,route='anthropic',structured=True)

    def check_prepared(prepared):
        wire=message_request(config,prepared)
        messages=[{'role':'system','content':wire['system']},*wire['messages']]
        size=len(json.dumps(messages,ensure_ascii=False,separators=(',',':')).encode())
        schema=wire['output_config']['format']['schema']
        unit=schema['properties']['paragraph']['anyOf'][0] if prepared.answer_style=='brief' else schema['properties']['paragraphs']['items']
        ids=[item['id'] for item in prepared.evidence]
        checks={'actual_native_budget':size<=24000 and size+2048==prepared.input_token_bound,
                'schema_budget':len(json.dumps(schema,ensure_ascii=False,separators=(',',':')).encode())<=4096,
                'schema_matches':schema==native_answer_schema(prepared.schema,prepared.answer_style),
                'selected_ids_match_wire':unit['properties']['primary_support']['properties']['citation_id']['enum']==unit['properties']['supports']['items']['properties']['citation_id']['enum']==ids,
                'context_dependencies_retained':all(context in ids for item in prepared.evidence for context in item.get('context_ids',[])),
                'exact_index_and_page_spans':True,'reader_locators':True,
                'unchanged_max_cost':config.maximum_cost_microusd(prepared.input_token_bound)<=158480}
        with library.connect() as db:
            for item in prepared.evidence:
                row=db.execute('SELECT c.*,p.text AS page_text FROM chunks c JOIN pages p ON p.doc_id=c.doc_id AND p.page=c.page WHERE c.id=?',(item['id'],)).fetchone()
                checks['exact_index_and_page_spans'] &= bool(row) and all(row[key]==item[key] for key in ('page','start','end','text')) and row['doc_id']==item['document_id'] and row['page_text'][item['start']:item['end']]==item['text']
                url=urlsplit(item['reader_url']);query=parse_qs(url.query)
                checks['reader_locators'] &= url.path=='/documents/'+item['document_id'] and query=={'generation':[item['generation']],'page':[str(item['page'])],'passage':[item['id']]}
        return {'checks':checks,'passed':all(checks.values()),'actual_native_prompt_bytes':size,
                'schema_bytes':len(json.dumps(schema,ensure_ascii=False,separators=(',',':')).encode()),
                'selected_ids':ids,'context_dependencies':{item['id']:item['context_ids'] for item in prepared.evidence if item.get('context_ids')}}

    results=[]
    for case in cases:
        limit=8 if case['group']=='smoke' else 10
        before=old_library.Library.search(library,case['question'],limit)
        after=library.search(case['question'],limit)
        row={'id':case['id'],'group':case['group'],
             'retrieval_unchanged':[{k:v for k,v in h.items() if k!='supporting_context'} for h in after]==before,
             'styles':{}}
        for style in ('brief','standard'):
            def wrapped(module):
                return types.SimpleNamespace(ChatRequest=lambda **kwargs:module.ChatRequest(**{**kwargs,'answer_style':style}),
                    FRAMING_TOKEN_ALLOWANCE=module.FRAMING_TOKEN_ALLOWANCE,
                    prepare_answer=lambda request,hits:module.prepare_answer(request,hits,provider='anthropic'))
            baseline=scoring.score(library,wrapped(old_chat),case,before)
            candidate=scoring.score(library,wrapped(chat),case,after)
            prepared=chat.prepare_answer(chat.ChatRequest(question=case['question'],answer_style=style),after,provider='anthropic')
            wire=check_prepared(prepared)
            candidate['passed'] &= wire['passed']
            row['styles'][style]={'baseline':baseline,'candidate':candidate,'wire':wire}
        results.append(row)
    diagnostics=[]
    if args.captured_answers:
        captured=json.loads(args.captured_answers.read_text())
        for case in captured['cases']:
            hits=library.search(case['question'],10)
            prepared=chat.prepare_answer(chat.ChatRequest(question=case['question']),hits,provider='anthropic')
            diagnostics.append({'id':case['id'],'question':case['question'],**check_prepared(prepared),
                                'prepared_evidence':prepared.evidence})
    groups=list(dict.fromkeys(case['group'] for case in cases))
    summary={style:{group:{'total':sum(r['group']==group for r in results),
                'before':sum(r['group']==group and r['styles'][style]['baseline']['passed'] for r in results),
                'after':sum(r['group']==group and r['styles'][style]['candidate']['passed'] for r in results)} for group in groups} for style in ('brief','standard')}
    regressions={style:[r['id'] for r in results if r['styles'][style]['baseline']['passed'] and not r['styles'][style]['candidate']['passed']] for style in ('brief','standard')}
    safety=all(r['retrieval_unchanged'] and all(s['wire']['passed'] and s['candidate']['safeguards_passed'] for s in r['styles'].values()) for r in results)
    report={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'baseline':args.baseline,'generation':library.generation,'provider_calls':0,'genuine_usage_operations':0,
            'source_sha256':{path:sha(ROOT/path) for path in ('backend/library.py','backend/source_context.py','backend/chat.py','backend/anthropic_provider.py')},
            'packet_sha256':{path:sha(ROOT/path) for _,path in packets},'summary':summary,'regressions':regressions,
            'all_safeguards_passed':safety,'known_failures':{style:[r['id'] for r in results if not r['styles'][style]['candidate']['passed']] for style in ('brief','standard')},
            'results':results,'diagnostics':diagnostics,
            'limits':'Consumed regression evidence only. Context supplies exact indexed source excerpts; it does not establish claim entailment, current law, complete table reconstruction or cross-page headings. No provider client or genuine usage ledger was opened.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as handle:json.dump(report,handle,indent=2)
    print(json.dumps({key:report[key] for key in ('summary','regressions','all_safeguards_passed','known_failures')}))
    return 0 if safety and not any(regressions.values()) and all(d['passed'] for d in diagnostics) else 1


if __name__=='__main__':
    raise SystemExit(main())
