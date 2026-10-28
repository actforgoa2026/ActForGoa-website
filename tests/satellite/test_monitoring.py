"""Private investigation history, bounded context retrieval and water evidence."""
from datetime import datetime, timezone, timedelta
import json
import sqlite3
import httpx
import pytest
from fastapi.testclient import TestClient
from satellite.app import create_app
from satellite.context import EcologyContext
from satellite.domain import Area, CompareRequest, HistoryRequest
from satellite.evidence import read_observation, compare_pixels
from satellite.service import SatelliteService
from satellite.store import Store
from satellite.summary import summarize_comparison
from test_service import AREA, COMPARISON, TIMES, HEADERS, raster, transport, credentials


SOURCE={'id':'passage-1','title':'Goa river observations','text':'Seasonal water levels and tides affect estuarine extent.',
    'url':'https://research.example/river.pdf','reader_url':'/documents/river?passage=passage-1&generation=fixture',
    'generation':'fixture','domains':['ecology'],'label':'Page 4','retrieved_at':'2026-10-20','warning':'Historical context'}


def test_history_is_private_small_and_filters_actual_dates(tmp_path,credentials):
    service=SatelliteService(tmp_path/'jobs.sqlite',httpx.Client(transport=httpx.MockTransport(lambda r:pytest.fail('History must not call a provider'))))
    with TestClient(create_app(service)) as client:
        store=service.store
        for actor in ['editor-one','other-editor']:
            for n in range(3):
                job=store.start(actor,{**COMPARISON,'question':f'Ribandar trees {n}%'})
                store.finish(job,{'summary':{'headline':'Possible canopy loss'},'before':{'image':'large-png-must-not-be-listed'},
                    'observation_interval':{'before':TIMES[0],'after':TIMES[1]},'evidence':{'common_usable_fraction':.9}})
        assert client.post('/history',json={}).status_code==401
        data=client.post('/history',headers=HEADERS,json={'query':'Ribandar','intent':'canopy_loss','start_date':'2025-10-15','end_date':'2025-10-16','limit':2}).json()
        assert len(data['items'])==2 and data['next_offset']==2
        assert 'large-png' not in json.dumps(data)
        assert data['items'][0]['evidence.common_usable_fraction']==.9
        second=client.post('/history',headers=HEADERS,json={'offset':2,'limit':2}).json()
        assert len(second['items'])==1 and second['next_offset'] is None
        assert not set(i['id'] for i in data['items']) & set(i['id'] for i in second['items'])
        assert len(client.post('/history',headers=HEADERS,json={'query':'0%'}).json()['items'])==1
        assert len(client.post('/history',headers=HEADERS,json={'query':'possible canopy'}).json()['items'])==3
        assert not client.post('/history',headers=HEADERS,json={'intent':'waste'}).json()['items']
        assert not client.post('/history',headers=HEADERS,json={'start_date':'2026-10-01'}).json()['items']
        assert client.post('/history',headers=HEADERS,json={'start_date':'2026-10-02','end_date':'2026-10-01'}).status_code==422
        other=client.post('/history',headers={**HEADERS,'X-Actor-ID':'other-editor'},json={}).json()
        assert not set(i['id'] for i in data['items']) & set(i['id'] for i in other['items'])


def test_history_migrates_legacy_jobs_and_retains_no_expired_results(tmp_path):
    path=tmp_path/'jobs.sqlite';db=sqlite3.connect(path)
    db.execute('CREATE TABLE jobs(id TEXT PRIMARY KEY,actor TEXT NOT NULL,status TEXT NOT NULL,created TEXT NOT NULL,result TEXT)')
    db.execute('INSERT INTO jobs VALUES(?,?,?,?,?)',('old','actor','complete',datetime.now(timezone.utc).isoformat(),'{}'))
    db.commit();db.close()
    store=Store(path)
    try:
        assert store.get('old','actor')['request'] is None
        assert store.history('actor',HistoryRequest())['items'][0]['id']=='old'
        store.db.execute('UPDATE jobs SET created=?',((datetime.now(timezone.utc)-timedelta(days=31)).isoformat(),))
        assert store.history('actor',HistoryRequest())['items']==[]
    finally:store.close()


def test_context_preserves_bounded_passages_and_citations(monkeypatch):
    monkeypatch.setenv('SATELLITE_RESEARCH_ORIGIN','https://research.fixture.test')
    def handler(request):
        assert request.url.path=='/api/search' and request.url.params['domain']=='ecology'
        assert 'x-api-key' not in request.headers and 'authorization' not in request.headers
        return httpx.Response(200,json={'domain':'ecology','results':[SOURCE,{**SOURCE,'id':'long','text':'x'*2500}]})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result=EcologyContext(client).search('What changed in this river?','surface_water')
    assert result['state']=='available'
    assert result['sources'][0]['text']==SOURCE['text']
    assert result['sources'][0]['reader_url']==SOURCE['reader_url']
    assert len(result['sources'][1]['text'])==1800 and result['sources'][1]['excerpt_truncated']
    assert 'do not establish the cause' in result['message']


@pytest.mark.parametrize('mode',['legacy','redirect','oversize','failure','unsafe_source','wrong_domain','invalid_json'])
def test_unusable_research_never_becomes_ecology_evidence(mode,monkeypatch):
    monkeypatch.setenv('SATELLITE_RESEARCH_ORIGIN','https://research.fixture.test')
    calls=[]
    def handler(request):
        calls.append(request)
        if mode=='legacy':return httpx.Response(200,json={'results':[SOURCE]})
        if mode=='redirect':return httpx.Response(302,headers={'Location':'https://elsewhere.test'})
        if mode=='oversize':return httpx.Response(200,content=b'x'*512001)
        if mode=='failure':return httpx.Response(503)
        if mode=='invalid_json':return httpx.Response(200,content=b'[]')
        return httpx.Response(200,json={'domain':'ecology','results':[{**SOURCE,**({'url':'javascript:alert(1)'} if mode=='unsafe_source' else {'domains':['legal']})}]})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:result=EcologyContext(client).search('water','surface_water')
    assert result['state'] in {'unavailable','no_matches'} and result['sources']==[]
    assert len(calls)==1


@pytest.mark.parametrize('origin',['http://public.test','https://user:secret@public.test','https://public.test/path','https://public.test?q=x'])
def test_context_rejects_unbounded_origins(origin,monkeypatch):
    monkeypatch.setenv('SATELLITE_RESEARCH_ORIGIN',origin)
    with httpx.Client(transport=httpx.MockTransport(lambda r:pytest.fail('Invalid origin was contacted'))) as client:
        assert EcologyContext(client).search('water','surface_water')['state']=='unavailable'


def test_failed_context_retains_comparison_and_newer_scene_metadata(tmp_path,credentials,monkeypatch):
    monkeypatch.setenv('SATELLITE_RESEARCH_ORIGIN','https://research.fixture.test')
    base=transport([])
    def handler(request):
        if request.url.host=='research.fixture.test':return httpx.Response(503)
        return base.handle_request(request)
    service=SatelliteService(tmp_path/'jobs.sqlite',httpx.Client(transport=httpx.MockTransport(handler)))
    original=service.cdse.catalog
    service.cdse.catalog=lambda req: {**(catalog:=original(req)),'scenes':catalog['scenes']+[{'id':'newer','acquired_at':'2025-10-25T05:00:00Z'}]}
    try:
        result=service.run_comparison(CompareRequest(**COMPARISON))
        assert result['library_context']['state']=='unavailable'
        assert result['before']['image'].startswith('data:image/png')
        assert result['freshness']['newer_acquisitions_in_search']==1
        assert result['freshness']['latest_acquired_at_in_search']=='2025-10-25T05:00:00Z'
        assert result['planning_context']['legal_status']=='not_established'
    finally:service.close()


def test_water_gains_losses_exclude_unusable_pixels_and_have_mapped_candidates():
    grid=Area(**AREA).grid()
    before=read_observation(raster(grid),grid);after=read_observation(raster(grid),grid)
    before['bands'][6,10:20,10:20]=6  # 100 pixels lose water label
    after['bands'][6,30:40,30:40]=6  # 100 pixels gain water label
    after['bands'][6,50:60,50:60]=6;after['clear'][50:60,50:60]=False
    evidence=compare_pixels(before,after,grid);water=evidence['water_change']
    assert all(water[key]==10000 for key in ['before_area_m2','after_area_m2','gained_area_m2','lost_area_m2'])
    assert len(evidence['water_candidates']['features'])==2
    assert 'Native 20 m' in water['method']
    summary=summarize_comparison('surface_water',evidence,{'state':'unavailable','answers':{}},{'before':TIMES[0],'after':TIMES[1]})
    assert summary['state']=='review_required'
    assert any('Tides, seasonality' in statement['text'] for statement in summary['statements'])
    after['clear'][:]=False
    assert compare_pixels(before,after,grid)['water_change'] is None


@pytest.mark.parametrize('intent,choice,caveat',[('waste','possible_large_accumulation','Ordinary litter'),('land_change','possible_construction','does not establish whether construction is lawful')])
def test_waste_and_construction_keep_inference_limits(intent,choice,caveat):
    key='waste_evidence' if intent=='waste' else 'land_change'
    evidence={'state':'observable','common_usable_fraction':1,'candidates':{'features':[]}}
    result=summarize_comparison(intent,evidence,{'state':'complete','answers':{key:{'choice':choice}}},{'before':TIMES[0],'after':TIMES[1]})
    assert any(caveat in statement['text'] for statement in result['statements'])
