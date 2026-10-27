"""Acceptance tooling on synthetic packets, sources and ledgers only."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

import httpx
import pytest

from backend.anthropic_provider import AnthropicClient
from backend.providers import chat_config
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.test_anthropic_provider import anthropic_message


@pytest.fixture
def setup(tmp_path,monkeypatch):
    class Today(datetime):
        @classmethod
        def now(cls,tz):return cls(2026,10,27,12,tzinfo=timezone.utc)
    import backend.hosting as hosting
    monkeypatch.setattr(acceptance,'datetime',Today);monkeypatch.setattr(hosting,'datetime',Today)
    monkeypatch.setattr(acceptance,'source_identity',lambda:'reviewed-head')
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER','anthropic');monkeypatch.delenv('ANTHROPIC_CHAT_MODEL',raising=False)
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
    plan={'source_commit':'reviewed-head','date_utc':'2026-10-27','generation':'fixture-generation',
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
    return plan,chat_config(),Library(),tmp_path


def test_check_does_not_parse_independent_questions_or_initialize_ledger(setup,monkeypatch):
    plan,config,_,_=setup
    monkeypatch.setattr(acceptance,'load_cases',lambda _:pytest.fail('No questions may be parsed during check'))
    packet=plan['stages']['test']['packets'][0];packet['partition']='independent_heldout'
    assert acceptance.preflight(plan,'test',config)['count']==2
    with pytest.raises(ValueError,match='authorization'):acceptance.preflight(plan,'test',config,execute=True)
    path=Path(plan['usage_root'])/'answer-usage.sqlite';path.unlink()
    with pytest.raises(ValueError,match='baseline'):acceptance.preflight(plan,'test',config)
    assert not path.exists()


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
    message=anthropic_message(payload,**kwargs)
    message['usage']={'input_tokens':1500,'output_tokens':150,'cache_creation_input_tokens':0,'cache_read_input_tokens':0}
    return httpx.Response(200,json=message)


def test_success_records_complete_sources_and_pending_claim_review(setup):
    report,output=execute_fixture(setup,response())
    assert report['complete'] and report['attempts']==2
    assert report['after']['days']=={'2026-10-26':182,'2026-10-27':3}
    assert report['after']['months']['2026-10']==638065+report['reserved_microusd']
    assert report['entailment_acceptance']=='pending_human_review' and report['originals_checked']
    assert all(e['accounting_matches'] and e['usage_within_reservation'] for e in report['cases'])
    assert all(e['human_review']['status']=='pending' and e['human_review']['claims'][0]['entailment'] is None for e in report['cases'])
    setup[0]['stages']['test']['expected_ledger']=report['after']
    with pytest.raises(FileExistsError):execute_fixture(setup,response())


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
    ([{'text':'Gates regulate tides.','citations':['passage-1']}]*2, 'paragraph_bound'),
    ([{'text':'Gates regulate tides.','citations':['unknown']}], 'citation_identity'),
    ([{'text':'Incomplete sentence','citations':['passage-1']}], 'paragraph_incomplete'),
])
def test_failed_final_answer_diagnostics_preserve_cause_without_accepting_or_retrying(setup,paragraphs,code):
    plan,_,_,_=setup;packet=plan['stages']['test']['packets'][0];path=Path(packet['path'])
    rows=json.loads(path.read_text())
    for row in rows:row['answer_style']='brief'
    path.write_text(json.dumps(rows));packet['sha256']=acceptance.sha(path)
    payload={'status':'answered','paragraphs':paragraphs}
    report,output=execute_fixture(setup,response(payload))
    entry=report['cases'][0]
    assert entry['failure_code']==code and not entry['mechanical_passed']
    assert entry['final_output_diagnostic']['answer']==payload
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
