"""Explicitly gated, one-pass Anthropic acceptance; --check never dispatches."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import httpx
from dotenv import dotenv_values
from backend.anthropic_provider import AnthropicClient, API_VERSION, INPUT_ALLOWANCE
from backend.chat import ChatRequest, prepare_answer, answer_question, MAX_PROMPT_BYTES, FRAMING_TOKEN_ALLOWANCE
from backend.hosting import PublicLimits
from backend.providers import PRICES, chat_config
from backend.usage_reconciliation import inspect_ledger


# Only messages owned by our validators may become diagnostics. Never persist
# arbitrary exception text, provider error bodies or Pydantic input echoes.
FAILURE_CODES = {
    'The answer did not match the required schema': 'answer_schema',
    'The native brief answer did not match the required schema': 'native_brief_schema',
    'The native answer did not match the evidence contract': 'native_evidence_contract',
    'Answer exceeds its paragraph bound': 'paragraph_bound',
    'Brief answer exceeds its length bound': 'brief_length',
    'Answer contains missing or unknown citations': 'citation_identity',
    'Answer paragraph appears incomplete': 'paragraph_incomplete',
    'Insufficient evidence must not contain unsupported paragraphs': 'abstention_content',
    'Answer has no cited paragraphs': 'empty_answer',
    'No structured answer was returned': 'missing_answer',
    'The answer was incomplete or declined': 'incomplete_or_declined',
    'Reviewed required evidence is missing before dispatch': 'missing_required_evidence',
    'Budget refused dispatch': 'budget_refused',
}


def failure_code(error):
    return FAILURE_CODES.get(str(error), 'unclassified_local_failure') if type(error) is ValueError else 'non_validation_failure'


def final_json_capture(payload):
    """Keep only bounded final answer JSON, never thinking or response metadata.

    Invalid JSON and unexpected fields are represented by fixed categories.
    The output is diagnostic, not accepted or served answer content.
    """
    blocks = payload.get('content')
    if not isinstance(blocks, list):return {'capture_status': 'missing_text'}
    texts = [b['text'] for b in blocks if isinstance(b, dict) and b.get('type') == 'text' and isinstance(b.get('text'), str)]
    text = ''.join(texts)
    if not text:return {'capture_status': 'missing_text'}
    if len(text.encode()) > 65536:return {'capture_status': 'oversize_text'}
    try:answer=json.loads(text)
    except ValueError:return {'capture_status': 'invalid_json'}
    if not isinstance(answer,dict) or answer.get('status') not in ('answered','insufficient_evidence'):
        return {'capture_status':'unexpected_shape'}
    if set(answer) == {'status','paragraph'}:
        paragraphs=[] if answer['paragraph'] is None else [answer['paragraph']]
        representation='native_brief'
    elif set(answer) == {'status','paragraphs'} and isinstance(answer['paragraphs'],list) and len(answer['paragraphs'])<=16:
        paragraphs=answer['paragraphs'];representation='paragraph_array'
    else:return {'capture_status':'unexpected_shape'}
    for p in paragraphs:
        if (not isinstance(p,dict) or not isinstance(p.get('text'),str) or len(p['text']) > 12000):
            return {'capture_status':'unexpected_shape'}
        if set(p) == {'text','citations'}:
            if (not isinstance(p['citations'],list) or len(p['citations']) > 20
                    or any(not isinstance(c,str) or len(c)>160 for c in p['citations'])):
                return {'capture_status':'unexpected_shape'}
        elif set(p) in ({'text','supports'}, {'text','primary_support','supports'}):
            if not isinstance(p['supports'],list) or len(p['supports']) > 20:
                return {'capture_status':'unexpected_shape'}
            supports=p['supports']
            if 'primary_support' in p:supports=[p['primary_support'],*supports]
            for support in supports:
                if (not isinstance(support,dict) or set(support) != {'citation_id','field','quote'}
                        or any(not isinstance(support[k],str) or len(support[k]) > bound
                               for k,bound in [('citation_id',160),('field',160),('quote',1200)])):
                    return {'capture_status':'unexpected_shape'}
        else:return {'capture_status':'unexpected_shape'}
    return {'capture_status':'captured_unvalidated_json','representation':representation,'answer':answer,
            'paragraph_count':len(paragraphs),'word_counts':[len(p['text'].split()) for p in paragraphs]}


def sha(path):
    with Path(path).open('rb') as file:return hashlib.file_digest(file, 'sha256').hexdigest()


def source_identity():
    head = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
    if dirty:raise ValueError('Tracked source must be clean')
    return head


def packet_path(packet):
    path = Path(packet['path'])
    return path if path.is_absolute() else ROOT/path


def verify_packets(stage):
    # Hash bytes only. Do not parse independent held-out questions during planning.
    for packet in stage['packets']:
        if packet['partition'] not in ('regression', 'abstention', 'independent_heldout'):
            raise ValueError('Each packet needs an explicit evaluation partition')
        if sha(packet_path(packet)) != packet['sha256']:
            raise ValueError('Question packet changed after freeze')


def load_cases(stage, expected_generation=None):
    cases = []
    for packet in stage['packets']:
        payload = json.loads(packet_path(packet).read_text())
        if isinstance(payload,dict) and expected_generation is not None and payload.get('generation') != expected_generation:
            raise ValueError('Source-reviewed packet generation changed')
        rows = payload['cases'] if isinstance(payload, dict) else payload
        include, exclude = packet.get('include_ids'), set(packet.get('exclude_ids', []))
        chosen = [r for r in rows if (include is None or r['id'] in include) and r['id'] not in exclude]
        if len(chosen) != packet['count']:raise ValueError('Frozen packet count changed')
        cases.extend(dict(row, partition=packet['partition']) for row in chosen)
    if len({c['id'] for c in cases}) != len(cases):raise ValueError('Duplicate case IDs')
    requests = [json.dumps({k: c[k] for k in ('question','history','answer_style') if k in c}, sort_keys=True) for c in cases]
    if len(set(requests)) != len(requests):raise ValueError('Duplicate requests require separate explicit review')
    for case in cases:
        ChatRequest(**{k: case[k] for k in ('question','history','answer_style','document_id','generation') if k in case})
        if case['partition'] == 'abstention' and case.get('expect_abstention') is not True:
            raise ValueError('Abstention cases must state the expected abstention')
    return cases


def planned_model(plan):
    # Historical plans implied Haiku. Any comparison model must be explicit,
    # reviewed in the shared price allowlist, and pinned in the frozen plan.
    model = plan.get('model', 'claude-haiku-5-5')
    if not isinstance(model, str) or ('anthropic', model) not in PRICES:
        raise ValueError('Only a reviewed Anthropic plan model is allowed')
    return model


def preflight(plan, stage_name, config, *, execute=False):
    if plan.get('source_commit') != source_identity():raise ValueError('Final integrated source identity is not approved')
    day = datetime.now(timezone.utc).date().isoformat()
    if plan.get('date_utc') != day:raise ValueError('This plan requires a new UTC-day approval')
    if config.provider != 'anthropic' or config.model != planned_model(plan):
        raise ValueError('Configured model must match the reviewed Anthropic plan model')
    stage = plan['stages'][stage_name]
    if execute and not stage.get('approval_reference'):raise ValueError('Coordinator execution authorization is required')
    count = sum(p['count'] for p in stage['packets'])
    if not 1 <= count <= stage['max_attempts'] <= 99:raise ValueError('Stage exceeds its bounded attempt plan')
    verify_packets(stage)
    root = Path(plan['data_root']).resolve()
    if any('sealed' in p.lower() or 'restoration-candidate' in p.lower() for p in root.parts):
        raise ValueError('Never open a preservation source through the live evaluator')
    marker = json.loads((root/'.acceptance-disposable.json').read_text())
    if marker != {'disposable_for_acceptance': True, 'generation': plan['generation']}:
        raise ValueError('Use the approved disposable data copy')
    if json.loads((root/'.research-index/CURRENT.json').read_text())['generation'] != plan['generation']:
        raise ValueError('Data generation changed')
    ledger = Path(plan['usage_root']).resolve()/'answer-usage.sqlite'
    before = inspect_ledger(ledger)
    if not before['exists'] or before != stage['expected_ledger']:
        raise ValueError('Existing canonical ledger does not match the approved baseline')
    worst = config.maximum_cost_microusd(MAX_PROMPT_BYTES + FRAMING_TOKEN_ALLOWANCE)
    if before['days'].get(day, 0)+count > 100:raise ValueError('Not enough daily attempts for this stage')
    if before['months'].get(day[:7], 0)+worst*count > 5_000_000:
        raise ValueError('Not enough monthly allowance for this bounded stage')
    return {'stage': stage, 'count': count, 'before': before, 'ledger': ledger,
            'worst_reservation_microusd': worst*count, 'day': day}


class UsageCapture(httpx.BaseTransport):
    """Capture only numeric usage and protocol facts, never raw thinking/headers."""
    def __init__(self, inner):self.inner=inner;self.entry=None

    def handle_request(self, request):
        entry = self.entry
        if entry is None or not entry.get('reserved') or entry['provider_attempts']:
            raise ValueError('An unreserved or duplicate provider dispatch was blocked')
        if str(request.url) != 'https://api.anthropic.com/v1/messages':raise ValueError('Unexpected provider host')
        entry['provider_attempts'] += 1
        body = json.loads(request.content)
        entry['request_shape'] = {'model': body['model'], 'version': request.headers['anthropic-version'],
            'max_tokens': body['max_tokens'], 'service_tier': body['service_tier'],
            'effort': body['output_config']['effort'], 'thinking': body['thinking']['type'],
            'format': body['output_config']['format']['type']}
        response = self.inner.handle_request(request)
        response.read()
        entry['provider_http_status'] = response.status_code
        if response.status_code == 200:
            try:payload=response.json()
            except ValueError:payload={}
            if isinstance(payload, dict):
                entry['final_output_diagnostic'] = final_json_capture(payload)
                entry['response_model_matches'] = payload.get('model') == body['model']
                response_model = payload.get('model')
                entry['response_model'] = (response_model if isinstance(response_model, str)
                    and ('anthropic', response_model) in PRICES else 'unexpected_model')
                stop = payload.get('stop_reason')
                entry['stop_reason'] = stop if stop in ('end_turn','refusal','max_tokens','model_context_window_exceeded','tool_use','pause_turn') else 'unexpected'
                usage=payload.get('usage',{})
                if isinstance(usage,dict):
                    entry['reported_usage'] = {k:usage[k] for k in ('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')
                                              if type(usage.get(k)) is int and usage[k]>=0}
                    details=usage.get('output_tokens_details',{})
                    if isinstance(details,dict) and type(details.get('thinking_tokens')) is int:
                        entry['reported_usage']['thinking_tokens']=details['thinking_tokens']
        return response

    def close(self):self.inner.close()


def usage_within_reservation(entry):
    usage=entry.get('reported_usage',{})
    fields=('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')
    if not all(type(usage.get(k)) is int and usage[k]>=0 for k in fields):return False
    return (sum(usage[k] for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens')) <= entry['reserved_input_tokens']
            and usage['output_tokens'] <= entry['reserved_output_tokens'] and usage['cache_creation_input_tokens']==0)


def accounting_matches(before, after, day, attempts, reservation):
    expected=json.loads(json.dumps(before))
    if attempts:
        expected['days'][day]=expected['days'].get(day,0)+attempts
        expected['months'][day[:7]]=expected['months'].get(day[:7],0)+reservation
    return after == expected


def verify_citations(library, answer, checked):
    for citation in answer['citations']:
        doc_id,generation=citation['document_id'],citation['generation']
        page=library.pages(doc_id,generation,start=citation['page'],limit=1)[0]
        if page['text'][citation['start']:citation['end']] != citation['text']:
            raise ValueError('Cited text differs from its exact page slice')
        link=urlsplit(citation['reader_url'])
        params=parse_qs(link.query)
        if (link.scheme or link.netloc or link.path != '/documents/'+doc_id
                or params.get('generation') != [generation]
                or params.get('page') != [str(citation['page'])]
                or params.get('passage') != [citation['id']]):
            raise ValueError('Unexpected reader link')
        identity=doc_id+':'+generation
        if identity not in checked:
            document=library.document(doc_id,generation)
            original,meta=library.original(doc_id,generation)
            if sha(original) != meta['sha256']:raise ValueError('Original checksum mismatch')
            pages=[]
            for start in range(1,document['page_count']+1,50):
                pages.extend(library.pages(doc_id,generation,start=start,limit=50))
            if len(pages) != document['page_count']:raise ValueError('Full document pages are incomplete')
            checked[identity]={'sha256':meta['sha256'],'page_count':len(pages),'full_text_sha256':
                hashlib.sha256('\n\n'.join(p['text'] for p in pages).encode()).hexdigest()}


def save(report, output):
    fd, temporary=tempfile.mkstemp(prefix='.acceptance-',dir=output.parent)
    try:
        with os.fdopen(fd,'w') as file:json.dump(report,file,indent=2,ensure_ascii=False);file.write('\n')
        os.replace(temporary,output)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)


def run_cases(library, client, capture, config, cases, context, output):
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    # A report cannot be resumed or overwritten into an implicit paid retry.
    with output.open('x'):pass
    output.chmod(0o600)
    report={'source_commit':source_identity(),'harness_sha256':sha(__file__),'generation':library.generation,
        'api_version':API_VERSION,'model':config.model,'before':context['before'],'cases':[],
        'originals_checked':{},'entailment_acceptance':'pending_human_review','complete':False}
    limits=PublicLimits(context['ledger'].parent,chats_per_day=100,monthly_usd='5')
    save(report,output)
    for case in cases:
        before=inspect_ledger(context['ledger'])
        expected_previous=report['cases'][-1]['ledger_after'] if report['cases'] else context['before']
        if before != expected_previous or datetime.now(timezone.utc).date().isoformat()!=context['day']:
            report['stop_reason']='Ledger or UTC day changed';break
        entry={'id':case['id'],'partition':case['partition'],'question':case['question'],
               'review_focus':case.get('review_focus'),'expected_abstention':case.get('expect_abstention',False),
               'required_evidence':case.get('required_evidence',[]),'source_review':case.get('source_review',[]),
               'provider_attempts':0,'reserved':False,'reservation_microusd':0,'ledger_before':before,
               'human_review':{'status':'pending','claims':[],'material_omissions':[],'reviewer':None}}
        report['cases'].append(entry);capture.entry=entry;save(report,output)
        fatal=False
        try:
            request=ChatRequest(**{k:case[k] for k in ('question','history','answer_style','document_id','generation') if k in case})
            # Match /api/chat follow-up retrieval. This harness does not replace
            # final HTTP/frontend acceptance or use the application's answer cache.
            previous=next((m.content for m in reversed(request.history) if m.role=='user'),'')
            query=request.question+(' '+previous[:500] if len(request.question.split())<8 else '')
            evidence=library.search(query,10,request.document_id,request.generation)
            entry['retrieved_ids']=[e['id'] for e in evidence]
            if not evidence:
                entry['answer']={'status':'insufficient_evidence','paragraphs':[],'citations':[]}
                entry['no_evidence_before_dispatch']=True
            else:
                prepared=prepare_answer(request,evidence,provider=config.provider)
                entry['prepared_evidence']=prepared.evidence
                selected={e['id'] for e in prepared.evidence}
                entry['required_evidence_retained']=all(set(item['any_of']) & selected for item in entry['required_evidence'])
                if not entry['required_evidence_retained']:
                    raise ValueError('Reviewed required evidence is missing before dispatch')
                entry['prompt_sha256']=hashlib.sha256(json.dumps(prepared.messages,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
                entry['reserved_input_tokens']=prepared.input_token_bound+INPUT_ALLOWANCE
                entry['reserved_output_tokens']=config.max_output_tokens
                cost=config.maximum_cost_microusd(prepared.input_token_bound)
                if not limits.reserve_answer(cost):raise ValueError('Budget refused dispatch')
                entry.update(reserved=True,reservation_microusd=cost);save(report,output)
                entry['answer']=answer_question(client,config,prepared)
            verify_citations(library,entry['answer'],report['originals_checked'])
            entry['mechanical_passed']=True
            entry['expected_behavior_passed']=(entry['answer']['status']=='insufficient_evidence') if entry['expected_abstention'] else entry['answer']['status']=='answered'
            entry['human_review']['claims']=[{'paragraph_index':i,'paragraph':p['text'],'citation_ids':p['citations'],
                'atomic_claims':[],'entailment':None,'scope':None,'chronology':None,'currentness':None,'extraction_limits':None}
                for i,p in enumerate(entry['answer']['paragraphs'])]
        except BaseException as error:
            entry.update(mechanical_passed=False,error_type=type(error).__name__,error_status=getattr(error,'status_code',None),
                         failure_code=failure_code(error))
            # No error body, raw output, key, raw thinking, or implicit retry.
            fatal=True
        finally:
            entry['ledger_after']=inspect_ledger(context['ledger'])
            entry['accounting_matches']=accounting_matches(before,entry['ledger_after'],context['day'],int(entry['reserved']),entry['reservation_microusd'])
            if entry['provider_attempts']:
                entry['usage_within_reservation']=usage_within_reservation(entry)
                if not entry['usage_within_reservation']:fatal=True
            if not entry['accounting_matches'] or not entry.get('expected_behavior_passed',False):fatal=True
            save(report,output)
        print(json.dumps({'case_id':case['id'],'partition':case['partition'],'attempts':entry['provider_attempts'],
                          'mechanical_passed':entry.get('mechanical_passed',False),'stopped':fatal}),flush=True)
        if fatal:
            report['stop_reason']='Case failed; coordinator review required before any further paid run';break
    report['after']=inspect_ledger(context['ledger'])
    report['complete']=len(report['cases'])==len(cases) and not report.get('stop_reason')
    report['attempts']=sum(e['provider_attempts'] for e in report['cases'])
    report['reserved_microusd']=sum(e['reservation_microusd'] for e in report['cases'])
    save(report,output)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--stage',required=True)
    parser.add_argument('--execute',action='store_true',help='Paid calls; requires separate coordinator authorization')
    parser.add_argument('--output',type=Path);parser.add_argument('--key-env-file',type=Path)
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text())
    os.environ['RESEARCH_CHAT_PROVIDER']='anthropic';os.environ['ANTHROPIC_CHAT_MODEL']=planned_model(plan)
    config=chat_config();context=preflight(plan,args.stage,config,execute=args.execute)
    if not args.execute:
        print(json.dumps({'ready_for_separate_authorization':True,'stage':args.stage,'model':config.model,'max_attempts':context['count'],
            'max_reservation_microusd':context['worst_reservation_microusd'],'provider_calls':0,
            'heldout_questions_parsed':False}));return
    if not args.output or args.output.exists():raise ValueError('A new output path is required')
    cases=load_cases(context['stage'],plan['generation'])
    values=dotenv_values(args.key_env_file) if args.key_env_file else os.environ
    key=values.get('ANTHROPIC_API_KEY')
    if not key:raise ValueError('No Anthropic key configured')
    # Delayed until approved execution; never open any preserved index to plan.
    from backend.library import Library
    library=Library(Path(plan['data_root']))
    capture=UsageCapture(httpx.HTTPTransport(retries=0))
    with AnthropicClient(key,values.get('ANTHROPIC_WORKSPACE_ID'),transport=capture) as client:
        report=run_cases(library,client,capture,config,cases,context,args.output)
    if not report['complete']:raise SystemExit(1)


if __name__=='__main__':main()
