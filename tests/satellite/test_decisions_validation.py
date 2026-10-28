"""Offline checks for the bounded live validation command; never real API calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import httpx
import pytest
from satellite.domain import Area
from satellite.providers import QUESTIONS
from test_service import AREA, TIMES, raster

SCRIPT=Path(__file__).resolve().parents[2]/'scripts/validate-satellite-decisions.py'
spec=importlib.util.spec_from_file_location('satellite_decisions_validation',SCRIPT)
validation=importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


@pytest.fixture
def recorded(tmp_path,monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','synthetic-never-live')
    source=tmp_path/'recorded';source.mkdir()
    document={'state':'passed','request':{'area':AREA},'observations':[],'selected_scene_ids':['scene-0','scene-1']}
    grid=Area(**AREA).grid()
    for index,label in enumerate(('before','after')):
        data=raster(grid,after=bool(index))
        (source/(label+'.tif')).write_bytes(data)
        document['observations'].append({'label':label,'spectral_sha256':hashlib.sha256(data).hexdigest(),
            'provenance':{'catalog_scene_id':f'scene-{index}','catalog_acquired_at':TIMES[index],
                          'acquired_at':[TIMES[index]],'collection':'sentinel-2-l2a'}})
    (source/'validation.json').write_text(json.dumps(document))
    return source


def test_single_call_provenance_and_safe_report(recorded,tmp_path):
    calls=[]
    def handler(request):
        calls.append(request)
        body=json.loads(request.content)
        assert str(request.url)==validation.ENDPOINT
        assert len([part for part in body['input'][0]['content'] if part['type']=='input_image'])==2
        return httpx.Response(200,headers={'x-request-id':'req_fixture'},json={'model':'gpt-6-luna',
            'answers':[{'name':name,'type':'choice','choice':'uncertain'} for name in QUESTIONS],
            'usage':{'input_tokens':200,'output_tokens':30,'ignored':'never-retain'}})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        report=validation.run_validation(recorded,tmp_path/'result',client=client,ledger_path=tmp_path/'usage.sqlite')
    assert report['state']=='passed' and len(calls)==1
    assert report['requests_attempted']==1 and report['reservation']=='persisted_before_request'
    assert report['provider_response']=={'status':200,'request_id':'req_fixture'}
    assert report['provider_usage']=={'input_tokens':200,'output_tokens':30}
    assert report['inputs'][0]['acquired_at']=='2025-10-10T05:00:00+00:00'
    assert len(report['inputs'][0]['common_masked_png_sha256'])==64
    assert report['canopy_presence']['state']=='inconclusive'
    serialized=json.dumps(report)
    assert 'synthetic-never-live' not in serialized and 'image/png;base64' not in serialized
    with pytest.raises(FileExistsError):validation.run_validation(recorded,tmp_path/'result',ledger_path=tmp_path/'usage.sqlite')


def test_paid_failure_is_not_retried_and_reservation_survives(recorded,tmp_path):
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(503,headers={'x-request-id':'req_unavailable'},json={'error':{'message':'secret-like raw provider error must not be retained'}})
    ledger=tmp_path/'usage.sqlite'
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        first=validation.run_validation(recorded,tmp_path/'first',client=client,ledger_path=ledger)
        second=validation.run_validation(recorded,tmp_path/'second',client=client,ledger_path=ledger)
    assert first['state']=='failed' and first['requests_attempted']==1
    assert second['error']['code']=='daily_limit' and second['requests_attempted']==0
    assert len(calls)==1
    assert 'secret-like' not in json.dumps(first)
    with sqlite3.connect(ledger) as db:assert db.execute("SELECT used FROM quota WHERE operation='classifications'").fetchone()[0]==1


def test_changed_raster_fails_before_reservation_or_request(recorded,tmp_path):
    (recorded/'after.tif').write_bytes(b'altered')
    ledger=tmp_path/'usage.sqlite'
    with httpx.Client(transport=httpx.MockTransport(lambda request:pytest.fail('Changed evidence must not reach a provider'))) as client:
        report=validation.run_validation(recorded,tmp_path/'result',client=client,ledger_path=ledger)
    assert report['error']['code']=='recording_hash_mismatch'
    assert report['requests_attempted']==0 and report['reservation']=='not_made'
    assert not ledger.exists()


def test_invalid_answer_retains_usage_without_raw_response(recorded,tmp_path):
    with httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json={'model':'gpt-6-luna',
            'answers':[],'usage':{'input_tokens':123,'output_tokens':8},'private':'must-not-be-retained'}))) as client:
        report=validation.run_validation(recorded,tmp_path/'result',client=client,ledger_path=tmp_path/'usage.sqlite')
    assert report['state']=='failed' and report['error']['code']=='invalid_classification'
    assert report['provider_usage']=={'input_tokens':123,'output_tokens':8}
    assert 'must-not-be-retained' not in json.dumps(report)
