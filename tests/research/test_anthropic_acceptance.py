"""Acceptance tooling on synthetic packets, sources and ledgers only."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from dataclasses import replace

import httpx
import pytest

from backend.anthropic_provider import AnthropicClient, message_request, API_VERSION
from backend.chat import ChatRequest, prepare_answer
from backend.providers import chat_config
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.test_anthropic_provider import anthropic_message, native_payload


@pytest.fixture
def setup(tmp_path,monkeypatch):
    class Today(datetime):
        @classmethod
        def now(cls,tz):return cls(2026,10,27,12,tzinfo=timezone.utc)
    import backend.hosting as hosting
    monkeypatch.setattr(acceptance,'datetime',Today);monkeypatch.setattr(hosting,'datetime',Today)
    monkeypatch.setattr(acceptance,'source_identity',lambda:'reviewed-head')
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','anthropic');monkeypatch.delenv('ANTHROPIC_CHAT_MODEL',raising=False)
    monkeypatch.delenv('ANTHROPIC_CHAT_EFFORT',raising=False)
    data=tmp_path/'disposable';data.mkdir();(data/'.research-index').mkdir()
    (data/'.research-index/CURRENT.json').write_text(json.dumps({'generation':'fixture-generation'}))
    (data/'.acceptance-disposable.json').write_text(json.dumps({'disposable_for_acceptance':True,'generation':'fixture-generation'}))
    ledger=tmp_path/'usage';ledger.mkdir()
    with sqlite3.connect(ledger/'answer-usage.sqlite') as db:
        db.execute('CREATE TABLE usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
        db.executemany('INSERT INTO usage VALUES (?,?)',[('2026-10-26',182),('2026-10-27',1)])
        db.execute('CREATE TABLE spend(month TEXT PRIMARY KEY,reserved_microusd INTEGER NOT NULL)')
        db.execute('INSERT INTO spend VALUES (?,?)',('2026-10',638065))
    packet=tmp_path/'cases.json';packet.write_text(json.dumps([
        {'id':'fixture-1','question':'How do gates regulate tidal water?'},
        {'id':'fixture-2','question':'What structures regulate tidal water?'}]))
    stage={'approval_reference':None,'expected_ledger':acceptance.inspect_ledger(ledger/'answer-usage.sqlite'),
        'max_attempts':2,'packets':[{'path':str(packet),'sha256':acceptance.sha(packet),'count':2,'partition':'regression'}]}
    plan={'source_commit':'reviewed-head','date_utc':'2026-10-27','generation':'fixture-generation','max_output_tokens':9000,
          'data_root':str(data),'usage_root':str(ledger),'stages':{'test':stage}}
    original=tmp_path/'original.txt';original.write_text('Gates regulate tidal water.')
    evidence={'id':'passage-1','document_id':'document-1','generation':'fixture-generation','page':1,
        'start':0,'end':len(original.read_text()),'text':original.read_text(),'title':'Public fixture',
        'url':'https://example.org/source','reader_url':'/documents/document-1?generation=fixture-generation&page=1&passage=passage-1'}
    class Library:
        generation='fixture-generation'
        def search(self,*args):return [evidence]
        def pages(self,*args,**kwargs):return [{'text':original.read_text()}]
        def document(self,*args):return {'page_count':1}
        def original(self,*args):return original,{'sha256':acceptance.sha(original)}
    return plan,replace(chat_config(),max_output_tokens=9000),Library(),tmp_path


def test_check_does_not_parse_independent_questions_or_initialize_ledger(setup,monkeypatch):
    plan,config,_,_=setup
    monkeypatch.setattr(acceptance,'load_cases',lambda _:pytest.fail('No questions may be parsed during check'))
    packet=plan['stages']['test']['packets'][0];packet['partition']='independent_heldout'
    assert acceptance.preflight(plan,'test',config)['count']==2
    with pytest.raises(ValueError,match='authorization'):acceptance.preflight(plan,'test',config,execute=True)
    path=Path(plan['usage_root'])/'answer-usage.sqlite';path.unlink()
    with pytest.raises(ValueError,match='baseline'):acceptance.preflight(plan,'test',config)
    assert not path.exists()


@pytest.mark.parametrize('tokens', [None, True, 9000.0, '12000', 0, 12001])
def test_plan_output_bound_requires_explicit_reviewed_integer_before_packet_reads(setup, monkeypatch, tokens):
    plan, config, _, _ = setup
    plan['max_output_tokens'] = tokens
    monkeypatch.setattr(acceptance, 'verify_packets', lambda _: pytest.fail('No artifact reads for invalid output bound'))
    with pytest.raises(ValueError, match='explicitly select'):
        acceptance.preflight(plan, 'test', config)


def test_missing_output_bound_has_no_historical_default(setup):
    plan, config, _, _ = setup
    plan.pop('max_output_tokens')
    with pytest.raises(ValueError, match='explicitly select'):
        acceptance.preflight(plan, 'test', config)


@pytest.mark.parametrize('planned, configured', [(9000, 12000), (12000, 9000)])
def test_preflight_rejects_any_plan_config_output_mismatch(setup, planned, configured):
    plan, config, _, _ = setup
    plan['max_output_tokens'] = planned
    with pytest.raises(ValueError, match='must match'):
        acceptance.preflight(plan, 'test', replace(config, max_output_tokens=configured))


def test_sonnet_cannot_inherit_haiku_output_increase(setup):
    plan, config, _, _ = setup
    plan.update(model='claude-sonnet-5-5', max_output_tokens=12000)
    with pytest.raises(ValueError, match='explicitly select'):
        acceptance.preflight(plan, 'test', replace(config, model=plan['model'], max_output_tokens=12000))


def test_check_cli_uses_actual_runtime_bound_without_rewriting_plan(setup, monkeypatch, capsys):
    plan, _, _, tmp = setup
    plan['max_output_tokens'] = 12000
    path = tmp / 'plan.json'
    original = json.dumps(plan).encode()
    path.write_bytes(original)
    monkeypatch.setattr(acceptance.sys, 'argv', ['evaluate', '--plan', str(path), '--stage', 'test'])
    acceptance.main()
    checked = json.loads(capsys.readouterr().out)
    assert checked['max_output_tokens'] == 12000
    assert checked['max_reservation_microusd'] == 18848
    assert checked['provider_calls'] == 0 and checked['heldout_questions_parsed'] is False
    assert path.read_bytes() == original


def test_main_refuses_historical_bound_before_key_library_client_or_dispatch(setup, monkeypatch):
    import builtins
    plan, _, _, tmp = setup
    plan['stages']['test']['approval_reference'] = 'synthetic-reviewed-plan'
    assert plan['max_output_tokens'] == 9000 and chat_config().max_output_tokens == 12000
    path = tmp / 'historical-plan.json'
    original = json.dumps(plan).encode()
    path.write_bytes(original)
    monkeypatch.setattr(acceptance.sys, 'argv', ['evaluate', '--plan', str(path), '--stage', 'test',
        '--execute', '--output', str(tmp / 'must-not-exist.json'), '--key-env-file', str(tmp / 'no-key')])
    for name in ('dotenv_values', 'AnthropicClient', 'run_cases', 'verify_packets'):
        monkeypatch.setattr(acceptance, name, lambda *a, **k: pytest.fail('Mismatched plan must stop before access or dispatch'))
    original_import = builtins.__import__
    def guarded_import(name, *args, **kwargs):
        if name == 'backend.library':pytest.fail('No native library access for mismatched plan')
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', guarded_import)
    with pytest.raises(ValueError, match='max_output_tokens must match'):
        acceptance.main()
    assert path.read_bytes() == original and not (tmp / 'must-not-exist.json').exists()


def test_low_plan_requires_explicit_matching_runtime_and_preserves_medium_default(setup):
    plan, _, _, _ = setup
    plan.update(effort='low', max_output_tokens=12000)
    medium = chat_config()
    assert medium.effort == 'medium' and acceptance.planned_effort(plan) == 'low'
    with pytest.raises(ValueError, match='effort must match'):
        acceptance.preflight(plan, 'test', medium)
    low = replace(medium, effort='low')
    assert acceptance.preflight(plan, 'test', low)['worst_reservation_microusd'] == 18848
    plan.pop('effort')
    with pytest.raises(ValueError, match='effort must match'):
        acceptance.preflight(plan, 'test', low)


def test_main_cannot_override_medium_runtime_with_low_plan(setup, monkeypatch):
    import builtins
    plan, _, _, tmp = setup
    plan.update(effort='low', max_output_tokens=12000)
    plan['stages']['test']['approval_reference'] = 'synthetic-review'
    path = tmp / 'low-plan.json';original = json.dumps(plan).encode();path.write_bytes(original)
    monkeypatch.setattr(acceptance.sys, 'argv', ['evaluate', '--plan', str(path), '--stage', 'test',
        '--execute', '--output', str(tmp / 'must-not-exist.json'), '--key-env-file', str(tmp / 'no-key')])
    for name in ('dotenv_values', 'AnthropicClient', 'run_cases', 'verify_packets'):
        monkeypatch.setattr(acceptance, name, lambda *a, **k: pytest.fail('Mismatched effort must stop before access or dispatch'))
    original_import = builtins.__import__
    def guarded_import(name, *args, **kwargs):
        if name == 'backend.library':pytest.fail('No native library access for mismatched effort')
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', guarded_import)
    with pytest.raises(ValueError, match='effort must match'):
        acceptance.main()
    assert chat_config().effort == 'medium' and path.read_bytes() == original
    assert not (tmp / 'must-not-exist.json').exists()


def test_low_check_cli_requires_explicit_environment_and_plan(setup, monkeypatch, capsys):
    plan, _, _, tmp = setup
    plan.update(effort='low', max_output_tokens=12000)
    path = tmp / 'explicit-low-plan.json';original = json.dumps(plan).encode();path.write_bytes(original)
    monkeypatch.setenv('ANTHROPIC_CHAT_EFFORT', 'low')
    monkeypatch.setattr(acceptance.sys, 'argv', ['evaluate', '--plan', str(path), '--stage', 'test'])
    acceptance.main()
    result = json.loads(capsys.readouterr().out)
    assert result['effort'] == 'low' and result['max_output_tokens'] == 12000
    assert result['provider_calls'] == 0 and result['max_reservation_microusd'] == 18848
    assert path.read_bytes() == original


@pytest.mark.parametrize('mutation,match',[
    ('head','identity'),('day','UTC-day'),('generation','disposable'),('hash','freeze'),('cap','bounded'),('baseline','baseline')])
def test_preflight_rejects_changed_inputs(setup,mutation,match):
    plan,config,_,_=setup;stage=plan['stages']['test']
    if mutation=='head':plan['source_commit']='unreviewed'
    if mutation=='day':plan['date_utc']='2026-10-28'
    if mutation=='generation':plan['generation']='other'
    if mutation=='hash':stage['packets'][0]['sha256']='0'*64
    if mutation=='cap':stage['max_attempts']=100
    if mutation=='baseline':stage['expected_ledger']['days']['2026-10-26']=0
    with pytest.raises(ValueError,match=match):acceptance.preflight(plan,'test',config)


@pytest.mark.parametrize('table,value,match',[('usage',99,'daily'),('spend',4999999,'monthly')])
def test_remaining_allowance_cannot_be_bypassed(setup,table,value,match):
    plan,config,_,_=setup;ledger=Path(plan['usage_root'])/'answer-usage.sqlite'
    with sqlite3.connect(ledger) as db:
        if table=='usage':db.execute('UPDATE usage SET attempts=? WHERE day=?',(value,'2026-10-27'))
        else:db.execute('UPDATE spend SET reserved_microusd=?',(value,))
    plan['stages']['test']['expected_ledger']=acceptance.inspect_ledger(ledger)
    with pytest.raises(ValueError,match=match):acceptance.preflight(plan,'test',config)


def test_comparison_model_requires_explicit_matching_plan(setup):
    plan,config,_,_=setup
    sonnet=replace(config,model='claude-sonnet-5-5')
    assert acceptance.planned_model(plan)=='claude-haiku-5-5'
    with pytest.raises(ValueError,match='match'):acceptance.preflight(plan,'test',sonnet)
    plan['model']=sonnet.model
    with pytest.raises(ValueError,match='match'):acceptance.preflight(plan,'test',config)
    context=acceptance.preflight(plan,'test',sonnet)
    assert context['worst_reservation_microusd']==316960
    for invalid in ('claude-unreviewed', 'openai/gpt-5.6-luna', None, []):
        plan['model']=invalid
        with pytest.raises(ValueError,match='reviewed'):acceptance.preflight(plan,'test',sonnet)


def test_high_effort_requires_explicit_matching_plan_without_cost_change(setup):
    plan,config,_,_=setup;plan['model']='claude-sonnet-5-5'
    medium=replace(config,model=plan['model']);high=replace(medium,effort='high')
    assert acceptance.planned_effort(plan)=='medium'
    before=acceptance.preflight(plan,'test',medium)
    with pytest.raises(ValueError,match='effort'):acceptance.preflight(plan,'test',high)
    plan['effort']='high'
    with pytest.raises(ValueError,match='effort'):acceptance.preflight(plan,'test',medium)
    after=acceptance.preflight(plan,'test',high)
    assert before['worst_reservation_microusd']==after['worst_reservation_microusd']==316960
    for invalid in ('low','xhigh',None,[]):
        plan['effort']=invalid
        with pytest.raises(ValueError,match='effort'):acceptance.preflight(plan,'test',high)


def test_sonnet_full_suite_cannot_bypass_existing_monthly_allowance(setup):
    plan,config,_,_=setup;plan['model']='claude-sonnet-5-5'
    stage=plan['stages']['test'];stage['max_attempts']=71;stage['packets'][0]['count']=71
    with pytest.raises(ValueError,match='monthly'):
        acceptance.preflight(plan,'test',replace(config,model=plan['model']))


def execute_fixture(setup,response):
    plan,config,library,tmp=setup
    context=acceptance.preflight(plan,'test',config)
    capture=acceptance.UsageCapture(httpx.MockTransport(lambda _:response))
    output=tmp/'result.json'
    with AnthropicClient('fixture-only',transport=capture) as client:
        report=acceptance.run_cases(library,client,capture,config,acceptance.load_cases(context['stage']),context,output)
    assert 'fixture-only' not in output.read_text() and 'private diagnostic' not in output.read_text()
    return report,output


def response(payload=None,**kwargs):
    message=anthropic_message(native_payload(payload) if payload is not None else None,**kwargs)
    message['usage']={'input_tokens':1500,'output_tokens':150,'cache_creation_input_tokens':0,'cache_read_input_tokens':0}
    return httpx.Response(200,json=message)


def test_success_records_complete_sources_and_pending_claim_review(setup):
    report,output=execute_fixture(setup,response())
    assert report['complete'] and report['attempts']==2
    assert report['after']['days']=={'2026-10-26':182,'2026-10-27':3}
    assert report['after']['months']['2026-10']==638065+report['reserved_microusd']
    assert report['entailment_acceptance']=='pending_human_review' and report['originals_checked']
    assert all(e['accounting_matches'] and e['usage_within_reservation'] for e in report['cases'])
    assert all(e['request_shape']['thinking']=='adaptive' and e['request_shape']['effort']=='medium'
               and e['request_shape']['max_tokens']==9000 for e in report['cases'])
    assert all(e['human_review']['status']=='pending' and e['human_review']['claims'][0]['entailment'] is None for e in report['cases'])
    for entry in report['cases']:
        assert entry['chat_request'] == {'question': entry['question'], 'history': [],
            'answer_style': 'standard', 'document_id': None, 'generation': None}
        assert entry['chat_request_supplied_fields'] == ['question']
        assert entry['retained_history'] == []
        captured = entry['outgoing_request']
        raw = captured['body_utf8'].encode('utf-8')
        assert captured['capture_status'] == 'captured_request'
        assert captured['body_sha256'] == hashlib.sha256(raw).hexdigest()
        assert captured['body_bytes'] == len(raw)
        body = json.loads(raw)
        prompt = [{'role': 'system', 'content': body['system']}, *body['messages']]
        assert hashlib.sha256(json.dumps(prompt, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest() == entry['prompt_sha256']
        assert json.loads(body['messages'][-1]['content'])['evidence'][0]['id'] == entry['prepared_evidence'][0]['id']
        assert body['output_config']['format']['schema']['properties']['status']
    setup[0]['stages']['test']['expected_ledger']=report['after']
    with pytest.raises(FileExistsError):execute_fixture(setup,response())


def test_sonnet_run_preserves_actual_identity_and_historical_accounting(setup):
    plan,config,library,tmp=setup;plan['model']='claude-sonnet-5-5'
    selected=replace(config,model=plan['model'])
    report,_=execute_fixture((plan,selected,library,tmp),response(model=selected.model))
    assert report['model']==selected.model and report['complete'] and report['attempts']==2
    assert report['after']['days']=={'2026-10-26':182,'2026-10-27':3}
    assert report['after']['months']['2026-10']==638065+report['reserved_microusd']
    for entry in report['cases']:
        assert entry['request_shape']['model']==entry['response_model']==selected.model
        assert entry['response_model_matches'] and entry['accounting_matches'] and entry['usage_within_reservation']


def test_high_effort_report_and_wire_identity_are_explicit(setup):
    plan,config,library,tmp=setup;plan.update(model='claude-sonnet-5-5',effort='high')
    selected=replace(config,model=plan['model'],effort=plan['effort'])
    report,_=execute_fixture((plan,selected,library,tmp),response(model=selected.model))
    assert report['complete'] and report['effort']=='high' and report['model']==selected.model
    assert all(c['request_shape']['effort']=='high' and c['request_shape']['thinking']=='adaptive'
               and c['request_shape']['max_tokens']==9000 and c['accounting_matches'] for c in report['cases'])


def test_new_capacity_is_explicit_in_report_wire_and_reservation(setup):
    plan, config, library, tmp = setup
    plan['max_output_tokens'] = 12000
    report, _ = execute_fixture((plan, replace(config, max_output_tokens=12000), library, tmp), response())
    assert report['complete'] and report['max_output_tokens'] == 12000
    assert all(entry['reserved_output_tokens'] == entry['request_shape']['max_tokens'] == 12000
               and entry['accounting_matches'] for entry in report['cases'])


def test_low_effort_survives_full_wire_capture_and_report(setup):
    plan, config, library, tmp = setup
    plan.update(effort='low', max_output_tokens=12000)
    report, _ = execute_fixture((plan, replace(config, effort='low', max_output_tokens=12000), library, tmp), response())
    assert report['complete'] and report['effort'] == 'low'
    for case in report['cases']:
        assert case['request_shape']['effort'] == 'low' and case['request_shape']['thinking'] == 'adaptive'
        body = json.loads(case['outgoing_request']['body_utf8'])
        assert body['output_config']['effort'] == 'low' and body['max_tokens'] == 12000
        assert case['accounting_matches'] and case['usage_within_reservation']


@pytest.mark.parametrize('model,effort', [('claude-sonnet-5-5', 'low'), ('claude-haiku-5-5', 'high')])
def test_wire_capture_refuses_unreviewed_model_effort_pair(setup, model, effort):
    _, config, library, _ = setup
    prepared = prepare_answer(ChatRequest(question='Where are gates?'), library.search('fixture'), provider='anthropic')
    wire = message_request(config, prepared)
    wire['model'] = model;wire['output_config']['effort'] = effort
    request = httpx.Request('POST', 'https://api.anthropic.com/v1/messages', json=wire)
    assert acceptance.outgoing_request_capture(request) == ({'capture_status': 'unexpected_request_shape'}, None)


def test_mismatched_reviewed_model_is_recorded_and_stops_without_retry(setup):
    plan,config,library,tmp=setup;plan['model']='claude-sonnet-5-5'
    report,_=execute_fixture((plan,replace(config,model=plan['model']),library,tmp),response())
    entry=report['cases'][0]
    assert not report['complete'] and report['attempts']==1
    assert entry['request_shape']['model']==plan['model']
    assert entry['response_model']=='claude-haiku-5-5' and not entry['response_model_matches']
    assert entry['accounting_matches'] and entry['reserved']


@pytest.mark.parametrize('reply',[httpx.Response(429,json={'error':'private diagnostic'}),
    response(stop='max_tokens'),response({'status':'answered','paragraphs':[{'text':'Unsupported.','citations':['unknown']}]}),
    response({'status':'insufficient_evidence','paragraphs':[]})])
def test_failures_and_unexpected_abstention_stop_without_retry_or_refund(setup,reply):
    report,_=execute_fixture(setup,reply)
    assert not report['complete'] and report['attempts']==1 and len(report['cases'])==1
    assert report['after']['days']['2026-10-27']==2
    assert report['reserved_microusd']>0 and report['cases'][0]['accounting_matches']


def test_missing_source_reviewed_passage_prevents_paid_dispatch(setup):
    plan,config,library,tmp=setup
    context=acceptance.preflight(plan,'test',config);cases=acceptance.load_cases(context['stage'])
    cases[0]['required_evidence']=[{'name':'Required provision','any_of':['absent']}]
    capture=acceptance.UsageCapture(httpx.MockTransport(lambda _:pytest.fail('No paid call for missing reviewed evidence')))
    with AnthropicClient('fixture-only',transport=capture) as client:
        report=acceptance.run_cases(library,client,capture,config,cases,context,tmp/'missing.json')
    assert report['attempts']==0 and report['after']==report['before'] and not report['complete']
    assert report['cases'][0]['outgoing_request'] == {'capture_status': 'not_dispatched'}


def test_reported_usage_over_reservation_stops_stage(setup):
    message=anthropic_message();message['usage']={'input_tokens':200000,'output_tokens':1,'cache_creation_input_tokens':0,'cache_read_input_tokens':0}
    report,_=execute_fixture(setup,httpx.Response(200,json=message))
    assert report['attempts']==1 and not report['complete'] and not report['cases'][0]['usage_within_reservation']


def test_template_preserves_original55_without_opening_heldout():
    template=json.loads((acceptance.ROOT/'tests/research/anthropic-acceptance-plan.template.json').read_text())
    known=[]
    for name in ('critical','remaining_regressions'):
        stage=template['stages'][name];acceptance.verify_packets(stage);known+=acceptance.load_cases(stage)
    assert len(known)==55 and len({c['id'] for c in known})==55
    assert sum(c['partition']=='abstention' for c in known)==4
    heldout=template['stages']['independent_heldout']
    assert heldout['max_attempts']==12 and heldout['packets'][0]['count']==12
    assert template['source_commit'] is None and all(s['approval_reference'] is None for s in template['stages'].values())


def test_source_review_packet_generation_must_match_final_data(setup):
    plan,_,_,_=setup;stage=plan['stages']['test'];packet=stage['packets'][0]
    path=Path(packet['path']);rows=json.loads(path.read_text())
    path.write_text(json.dumps({'generation':'other-generation','cases':rows}))
    with pytest.raises(ValueError,match='packet generation'):
        acceptance.load_cases(stage,'fixture-generation')


@pytest.mark.parametrize('paragraphs,code',[
    ([{'text':'word '*120+'end.','citations':['passage-1']}], 'brief_length'),
    ([{'text':'Gates regulate tides.','citations':['passage-1']}]*2, 'native_evidence_contract'),
    ([{'text':'Gates regulate tides.','citations':['unknown']}], 'native_evidence_contract'),
    ([{'text':'Incomplete sentence','citations':['passage-1']}], 'paragraph_incomplete'),
])
def test_failed_final_answer_diagnostics_preserve_cause_without_accepting_or_retrying(setup,paragraphs,code):
    plan,_,_,_=setup;packet=plan['stages']['test']['packets'][0];path=Path(packet['path'])
    rows=json.loads(path.read_text())
    for row in rows:row['answer_style']='brief'
    path.write_text(json.dumps(rows));packet['sha256']=acceptance.sha(path)
    payload={'status':'answered','paragraph':paragraphs[0]} if len(paragraphs)==1 else {'status':'answered','paragraphs':paragraphs}
    report,output=execute_fixture(setup,response(payload))
    entry=report['cases'][0]
    assert entry['failure_code']==code and not entry['mechanical_passed']
    assert entry['final_output_diagnostic']['answer']==native_payload(payload)
    assert entry['final_output_diagnostic']['paragraph_count']==len(paragraphs)
    assert entry['final_output_diagnostic']['word_counts']==[len(p['text'].split()) for p in paragraphs]
    assert report['attempts']==1 and not report['complete'] and 'answer' not in entry
    assert report['after']['days']['2026-10-27']==2 and entry['accounting_matches']
    assert 'private diagnostic' not in output.read_text() and 'signature' not in output.read_text()


@pytest.mark.parametrize('text,status',[
    ('private diagnostic not JSON','invalid_json'),
    (json.dumps({'status':'answered','paragraphs':[],'private diagnostic':'fixture-only'}),'unexpected_shape'),
    ('x'*65537,'oversize_text'),
])
def test_diagnostic_capture_never_persists_malformed_text_or_unexpected_fields(text,status):
    captured=acceptance.final_json_capture({'content':[
        {'type':'thinking','thinking':'private diagnostic'},
        {'type':'redacted_thinking','data':'private diagnostic'},
        {'type':'text','text':text}]})
    assert captured=={'capture_status':status}
    assert acceptance.failure_code(ValueError('private diagnostic fixture-only'))=='unclassified_local_failure'
    assert acceptance.failure_code(httpx.ReadTimeout('private diagnostic fixture-only'))=='non_validation_failure'


@pytest.mark.parametrize('model', ['claude-haiku-5-5', 'claude-sonnet-5-5'])
@pytest.mark.parametrize('style', ['brief', 'standard'])
def test_outgoing_capture_preserves_exact_bytes_object_and_visible_context(setup, model, style):
    _, config, library, _ = setup
    request = ChatRequest(question='Where is the café?', answer_style=style,
                          history=[{'role': 'user', 'content': 'Keep the source year.'}])
    prepared = prepare_answer(request, library.search('fixture'), provider='anthropic')
    wire = message_request(replace(config, model=model), prepared)
    # Noncanonical whitespace and UTF-8 prove the capture hashes transport bytes,
    # not a freshly serialized approximation of the payload.
    raw = json.dumps(wire, ensure_ascii=False, indent=2).encode('utf-8')
    outgoing = httpx.Request('POST', 'https://api.anthropic.com/v1/messages', content=raw,
        headers={'Authorization': 'Bearer fixture-only', 'anthropic-version': API_VERSION,
                 'anthropic-workspace-id': 'private-workspace'})
    calls = []
    def inner(actual):
        assert actual is outgoing and actual.content == raw
        assert actual.headers == outgoing.headers
        calls.append(actual)
        return response(model=model)
    capture = acceptance.UsageCapture(httpx.MockTransport(inner))
    capture.entry = {'reserved': True, 'provider_attempts': 0}
    capture.handle_request(outgoing)
    saved = capture.entry['outgoing_request']
    assert saved == {'capture_status': 'captured_request', 'body_utf8': raw.decode('utf-8'),
                     'body_sha256': hashlib.sha256(raw).hexdigest(), 'body_bytes': len(raw)}
    body = json.loads(saved['body_utf8'])
    assert body == wire and body['messages'] == prepared.messages[1:]
    assert body['system'] == prepared.messages[0]['content']
    assert len(calls) == capture.entry['provider_attempts'] == 1
    serialized = json.dumps(capture.entry)
    assert all(secret not in serialized for secret in ('fixture-only', 'private-workspace', 'private diagnostic'))


@pytest.mark.parametrize('mutation,status', [
    ('unexpected-field', 'unexpected_request_shape'),
    ('thinking-content', 'unexpected_request_shape'),
    ('message-block', 'unexpected_request_shape'),
    ('credential-echo', 'credential_like_content'),
    ('escaped-credential', 'credential_like_content'),
    ('other-key', 'credential_like_content'),
    ('credential-field', 'credential_like_content'),
    ('invalid-json', 'invalid_json_body'),
    ('duplicate-field', 'invalid_json_body'),
    ('invalid-utf8', 'invalid_json_body'),
    ('oversize', 'oversize_body'),
])
def test_unsafe_outgoing_capture_records_unavailability_without_body_or_dispatch(setup, mutation, status):
    _, config, library, _ = setup
    prepared = prepare_answer(ChatRequest(question='Where are gates?'), library.search('fixture'), provider='anthropic')
    wire = message_request(config, prepared)
    if mutation == 'unexpected-field': wire['api_key'] = 'private diagnostic'
    elif mutation == 'thinking-content': wire['thinking']['text'] = 'private diagnostic'
    elif mutation == 'message-block': wire['messages'][0]['content'] = [{'type': 'thinking', 'thinking': 'private diagnostic'}]
    elif mutation in ('credential-echo', 'escaped-credential'): wire['system'] = 'fixture-only'
    elif mutation == 'other-key': wire['system'] = 'sk-ant-private-diagnostic'
    elif mutation == 'credential-field': wire['messages'][0]['content'] = '{"api_key":"private diagnostic"}'
    raw = json.dumps(wire).encode()
    if mutation == 'escaped-credential': raw = raw.replace(b'fixture-only', b'fixture-\\u006fnly')
    elif mutation == 'duplicate-field': raw = b'{"system":"private diagnostic",' + raw[1:]
    elif mutation == 'invalid-json': raw = b'private diagnostic'
    elif mutation == 'invalid-utf8': raw = b'\xff'
    elif mutation == 'oversize': raw = b'x' * 131073
    outgoing = httpx.Request('POST', 'https://api.anthropic.com/v1/messages', content=raw,
                            headers={'Authorization': 'Bearer fixture-only', 'anthropic-version': API_VERSION})
    capture = acceptance.UsageCapture(httpx.MockTransport(lambda _: pytest.fail('Unsafe body must not dispatch')))
    capture.entry = {'reserved': True, 'provider_attempts': 0}
    with pytest.raises(ValueError, match='captured safely'):
        capture.handle_request(outgoing)
    assert capture.entry['outgoing_request'] == {'capture_status': status}
    assert capture.entry['provider_attempts'] == 0
    assert 'private diagnostic' not in json.dumps(capture.entry)


def test_streaming_request_body_is_explicitly_unavailable():
    outgoing = httpx.Request('POST', 'https://api.anthropic.com/v1/messages', content=iter([b'{}']))
    assert acceptance.outgoing_request_capture(outgoing) == ({'capture_status': 'body_unavailable'}, None)


def test_capture_distinguishes_original_request_history_from_retained_history(setup):
    plan, config, library, tmp = setup
    context = acceptance.preflight(plan, 'test', config)
    case = acceptance.load_cases(context['stage'])[0]
    case.update(history=[{'role': 'user' if i % 2 == 0 else 'assistant', 'content': 'Context ' * 500}
                         for i in range(8)], answer_style='standard',
                document_id='a' * 24 + '-' + 'b' * 12, generation='fixture-generation')
    capture = acceptance.UsageCapture(httpx.MockTransport(lambda _: response()))
    with AnthropicClient('fixture-only', transport=capture) as client:
        report = acceptance.run_cases(library, client, capture, config, [case], context, tmp / 'history.json')
    entry = report['cases'][0]
    assert report['complete'] and entry['chat_request'] == {k: case[k] for k in
        ('question', 'history', 'answer_style', 'document_id', 'generation')}
    assert entry['chat_request_supplied_fields'] == sorted(entry['chat_request'])
    wire = json.loads(entry['outgoing_request']['body_utf8'])
    assert entry['retained_history'] == wire['messages'][:-1]
    assert len(entry['retained_history']) < len(case['history'])
    assert entry['retained_history'] == case['history'][-len(entry['retained_history']):]
