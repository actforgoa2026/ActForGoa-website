"""Synthetic provider contracts; these are NOT field/accuracy tests."""
from datetime import datetime, timezone
import io
import json
import tarfile
import time
import httpx
import numpy as np
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from satellite.app import create_app
from satellite.domain import Area, CatalogRequest, CompareRequest, DomainError, Interpretation, Query, change_interval, make_plan
from satellite.eve_cdse import CDSE, TOKEN_URL, CATALOG_URL, PROCESS_URL
from satellite.evidence import compare_pixels, read_observation, classification_image
from PIL import Image
from satellite.providers import AnthropicPlanner, AnthropicClassifier, DecisionsClassifier, ImageClassifier, QUESTIONS
from satellite.summary import canopy_presence, summarize_comparison
from satellite.service import SatelliteService
from satellite.store import Store

AREA = {'bbox':[73.82,15.48,73.83,15.49]}
CATALOG = {'area':AREA,'start_date':'2025-10-01','end_date':'2025-10-28'}
TIMES = ['2025-10-10T05:00:00Z','2025-10-20T05:00:00Z']
SCENES = [{'id':f'scene-{i}','acquired_at':t,'geometry':{'type':'Polygon','coordinates':[]},'scene_cloud_percent':0,'collection':'sentinel-2-l2a'} for i,t in enumerate(TIMES)]
COMPARISON = {**CATALOG,'before_id':'scene-0','after_id':'scene-1','intent':'canopy_loss',
              'window_start':'2025-10-18T00:00:00+05:30','window_end':'2025-10-28T00:00:00+05:30'}
HEADERS = {'Authorization':'Bearer '+'a'*40,'X-Actor-ID':'editor-one'}


def raster(grid, after=False, cloud=False, wrong_grid=False):
    bands = np.zeros((8,grid['height'],grid['width']),dtype='float32')
    bands[:3] = .08
    bands[3] = .6
    bands[4:6] = .12
    bands[6] = 9 if cloud else 4
    bands[7] = 1
    if after:
        bands[0,10:30,10:30] = .3
        bands[3,10:30,10:30] = .12
    with MemoryFile() as memory:
        with memory.open(driver='GTiff',count=8,dtype='float32',width=grid['width'],height=grid['height'],crs='EPSG:32643',
                         transform=from_origin(grid['bounds'][0]+(10 if wrong_grid else 0),grid['bounds'][3],10,10)) as dataset:
            dataset.write(bands)
        return memory.read()


def bundle(grid, after=False, date=None, cloud=False):
    payload=io.BytesIO()
    with tarfile.open(fileobj=payload,mode='w') as archive:
        for name,data in [('spectral.tif',raster(grid,after,cloud)),('userdata.json',json.dumps({'tiles':[{'date':date or TIMES[int(after)],'shId':'synthetic-tile'}]}).encode())]:
            member=tarfile.TarInfo(name);member.size=len(data);archive.addfile(member,io.BytesIO(data))
    return payload.getvalue()


def transport(calls, cloud=False, stale=False):
    grid=Area(**AREA).grid()
    def handler(request):
        calls.append(str(request.url))
        if str(request.url)==TOKEN_URL:
            return httpx.Response(200,json={'access_token':'test-only-provider-token','expires_in':3600})
        data=json.loads(request.content)
        if str(request.url)==CATALOG_URL:
            assert data['collections']==['sentinel-2-l2a']
            return httpx.Response(200,json={'features':[{'id':s['id'],'geometry':s['geometry'],'properties':{'datetime':s['acquired_at'],'eo:cloud_cover':0}} for s in SCENES]})
        if str(request.url)==PROCESS_URL:
            assert request.headers['Accept']=='application/tar'
            assert data['output']['responses'][0]['format']['type']=='image/tiff'
            assert data['input']['data'][0]['dataFilter']['mosaickingOrder']=='mostRecent'
            assert data['output']['width']==grid['width']
            assert 'save_path' not in data
            after='2025-10-20' in data['input']['data'][0]['dataFilter']['timeRange']['to']
            return httpx.Response(200,content=bundle(grid,after,date='2025-10-01T05:00:00Z' if stale else None,cloud=cloud))
        if str(request.url)=='https://api.openai.com/v1/decisions':
            assert data['model']=='gpt-6-luna'
            assert len([p for p in data['input'][0]['content'] if p['type']=='input_image'])==2
            return httpx.Response(200,json={'model':'gpt-6-luna','answers':[{'type':'choice','name':q['name'],'choice':'uncertain','confidence':.99} for q in data['questions']]})
        raise AssertionError('Unexpected network destination '+str(request.url))
    return httpx.MockTransport(handler)


@pytest.fixture
def credentials(monkeypatch):
    monkeypatch.delenv('SATELLITE_RESEARCH_ORIGIN',raising=False)
    for name in ['CDSE_CLIENT_ID','CDSE_CLIENT_SECRET','OPENAI_API_KEY']:
        monkeypatch.setenv(name,'synthetic-test-only')
    monkeypatch.setenv('SATELLITE_SERVICE_TOKEN','a'*40)
    monkeypatch.setenv('SATELLITE_MCP_TOKEN','m'*40)
    monkeypatch.setenv('SATELLITE_CLASSIFIER','openai-decisions')


@pytest.mark.parametrize('bbox',[[0,0,.01,.01],[74.5,15.5,74.51,15.51],[73.8,15.3,74.2,15.7],[73.9,15.5,73.8,15.4],[73.82,15.48,73.82001,15.48001],[float('nan'),15.4,74,15.5]])
def test_reject_invalid_or_outside_goa_areas(bbox):
    with pytest.raises(ValidationError): Area(bbox=bbox)


@pytest.mark.parametrize('start,end',[('2025-10-28','2025-10-01'),('2025-01-01','2025-12-31'),('2010-01-01','2010-01-02'),('2999-01-01','2999-01-02')])
def test_invalid_date_ranges(start,end):
    with pytest.raises(ValidationError): CatalogRequest(area=AREA,start_date=start,end_date=end)


def interpretation(**updates):
    return Interpretation(intent='canopy_loss',scope='selected_area',place_name='',time_mode='relative_days',days=10,start_date=None,end_date=None,individual_tree=False,**updates)


def test_relative_window_and_baseline_are_separate_in_ist():
    plan=make_plan(Query(question='Trees here in the last 10 days?',area=AREA),interpretation(),datetime(2026,10,28,10,0,tzinfo=timezone.utc))
    assert plan['window_start']=='2026-10-18T15:30:00+05:30'
    assert plan['window_end']=='2026-10-28T15:30:00+05:30'
    assert plan['catalog_start']=='2026-09-18'


@pytest.mark.parametrize('scope,state',[('named_place','area_required'),('goa','statewide_not_ready'),('unsupported','unsupported')])
def test_no_invented_place_or_silent_statewide_scan(scope,state):
    value=interpretation().model_copy(update={'scope':scope,'place_name':'Verlem'})
    assert make_plan(Query(question='Trees in Verlem?',area=AREA),value)['state']==state


def test_overlap_is_not_exact_event_date():
    result=change_interval(TIMES[0],TIMES[1],'2025-10-18T00:00:00Z','2025-10-28T00:00:00Z')
    assert result['relation']=='overlaps_window'
    assert result['exact_event_date'] is None


def test_spectral_candidate_and_cloud_abstention():
    grid=Area(**AREA).grid()
    before=read_observation(raster(grid),grid);after=read_observation(raster(grid,after=True),grid)
    result=compare_pixels(before,after,grid)
    assert result['state']=='observable'
    assert result['candidates']['features'][0]['properties']['area_m2']==40000
    assert result['candidates']['features'][0]['properties']['kind']=='possible_vegetation_loss'
    cloud=read_observation(raster(grid,cloud=True),grid)
    result=compare_pixels(before,cloud,grid)
    assert result['state']=='insufficient_clear_coverage'
    assert result['common_usable_fraction']==0
    assert result['candidates']['features']==[]


def test_misaligned_grid_stops_comparison():
    grid=Area(**AREA).grid()
    with pytest.raises(DomainError,match='grid'):read_observation(raster(grid,wrong_grid=True),grid)


def test_auth_catalog_provenance_classification_and_job_access(tmp_path,credentials):
    calls=[]
    service=SatelliteService(tmp_path/'jobs.sqlite',httpx.Client(transport=transport(calls)))
    with TestClient(create_app(service)) as client:
        assert client.get('/healthz').status_code==200
        assert client.get('/status').status_code==401
        assert client.post('/catalog',json=CATALOG).status_code==401
        assert calls==[]
        assert client.get('/status',headers={'Authorization':HEADERS['Authorization']}).status_code==403
        response=client.post('/compare',headers=HEADERS,json=COMPARISON)
        assert response.status_code==202
        job=response.json()['id']
        for _ in range(100):
            result=client.get('/jobs/'+job,headers=HEADERS).json()
            if result['status']!='running':break
            time.sleep(.01)
        assert result['status']=='complete',result
        data=result['result']
        assert data['before']['catalog_scene_id']=='scene-0'
        assert data['after']['acquired_at']==[TIMES[1]]
        assert data['observation_interval']['query_window_relation']=='overlaps_window'
        assert data['classification']['answers']['canopy_change']['choice']=='uncertain'
        assert all(answer['confidence']==.99 for answer in data['classification']['answers'].values())
        assert data['classification']['calibration']=='not_calibrated'
        assert data['classification']['confidence_threshold'] is None
        assert data['fire_detections']['state']=='not_queried'
        assert client.get('/jobs/'+job,headers={**HEADERS,'X-Actor-ID':'different-editor'}).status_code==404
        assert calls.count(TOKEN_URL)==1


def test_clouds_skip_paid_classification(tmp_path,credentials):
    calls=[];service=SatelliteService(tmp_path/'jobs.sqlite',httpx.Client(transport=transport(calls,cloud=True)))
    try:
        result=service.run_comparison(CompareRequest(**COMPARISON))
        assert result['classification']['state']=='skipped'
        assert not any('openai.com' in u for u in calls)
    finally:service.close()


def test_acquisition_mismatch_fails_closed(tmp_path,credentials):
    calls=[];service=SatelliteService(tmp_path/'jobs.sqlite',httpx.Client(transport=transport(calls,stale=True)))
    try:
        with pytest.raises(DomainError,match='acquisition'):service.run_comparison(CompareRequest(**COMPARISON))
        assert not any('openai.com' in u for u in calls)
    finally:service.close()


def test_unbundled_tiff_cannot_be_used_without_provenance(credentials):
    grid=Area(**AREA).grid()
    cdse=CDSE(httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,content=raster(grid)))))
    cdse.token=lambda:'test-only'
    with pytest.raises(DomainError) as error:cdse.observation(SCENES[0],grid)
    assert error.value.code=='invalid_provenance'


def test_missing_credentials_and_empty_catalog_are_distinct(monkeypatch):
    monkeypatch.delenv('CDSE_CLIENT_ID',raising=False)
    cdse=CDSE(httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'features':[]}))))
    with pytest.raises(DomainError) as error:cdse.catalog(CatalogRequest(**CATALOG))
    assert error.value.code=='imagery_unavailable'
    cdse.token=lambda:'test'
    assert cdse.catalog(CatalogRequest(**CATALOG))['state']=='no_imagery'


def test_catalog_pagination_marks_truncation():
    calls=[]
    def handler(request):
        body=json.loads(request.content);calls.append(body)
        return httpx.Response(200,json={'features':[],'context':{'next':len(calls)*100}})
    cdse=CDSE(httpx.Client(transport=httpx.MockTransport(handler)));cdse.token=lambda:'test'
    result=cdse.catalog(CatalogRequest(**CATALOG))
    assert len(calls)==3 and result['truncated'] is True
    assert calls[-1]['next']==200


def test_model_refusals_and_invalid_choices_are_not_findings(credentials):
    def handler(request):return httpx.Response(200,json={'model':'gpt-6-luna','answers':[{'type':'refusal','name':n} for n in QUESTIONS]})
    classifier=DecisionsClassifier(httpx.Client(transport=httpx.MockTransport(handler)))
    assert all(a['choice']=='uncertain' for a in classifier.classify(b'png',b'png',{})['answers'].values())
    classifier.http=httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'answers':[{'name':'canopy_change','type':'choice','choice':'definitely_illegal'}]})))
    with pytest.raises(DomainError):classifier.classify(b'png',b'png',{})


def test_planner_validates_model_output(monkeypatch):
    monkeypatch.setenv('ANTHROPIC_API_KEY','test-only')
    value=interpretation().model_dump(mode='json');value['sql']='DROP TABLE events'
    planner=AnthropicPlanner(httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'stop_reason':'tool_use','content':[{'type':'tool_use','name':'plan_observation','input':value}]}))))
    with pytest.raises(DomainError):planner.interpret(Query(question='Trees here?',area=AREA))


def test_reservations_survive_restart_and_jobs_do_not_reexecute(tmp_path):
    path=tmp_path/'jobs.sqlite';store=Store(path);store.reserve('plans',1);job=store.start('editor');store.close()
    store=Store(path)
    try:
        with pytest.raises(DomainError) as error:store.reserve('plans',1)
        assert error.value.status==429
        assert store.get(job,'editor')['status']=='failed'
    finally:store.close()


def test_mcp_auth_and_discovery(tmp_path,credentials):
    service=SatelliteService(tmp_path/'jobs.sqlite',httpx.Client(transport=httpx.MockTransport(lambda r:pytest.fail('No provider call during discovery'))))
    with TestClient(create_app(service),base_url='http://localhost') as client:
        payload={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test','version':'1'}}}
        headers={'Authorization':'Bearer '+'m'*40,'Accept':'application/json, text/event-stream'}
        assert client.post('/mcp',json=payload).status_code==401
        assert client.post('/mcp',headers=HEADERS,json=payload).status_code==401
        assert client.post('/mcp',headers=headers,json=payload).status_code==200
        assert client.post('/mcp',headers={**headers,'Host':'untrusted.example'},json=payload).status_code==421
        assert client.post('/mcp',headers={**headers,'Origin':'https://untrusted.example'},json=payload).status_code==403
        response=client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':2,'method':'tools/list'})
        assert response.status_code==200,response.text
        assert {t['name'] for t in response.json()['result']['tools']}=={'plan_goa_observation','list_goa_observations','compare_goa_observations','get_goa_comparison'}


def test_classifier_sees_only_common_clear_pixels():
    grid=Area(**AREA).grid()
    observation=read_observation(raster(grid),grid)
    common=observation['clear'].copy()
    common[10:20,10:20]=False
    image=np.array(Image.open(io.BytesIO(classification_image(observation,common))))
    assert np.all(image[~common]==128)
    original=np.array(Image.open(io.BytesIO(observation['png'])).convert('RGB'))
    assert np.array_equal(image[common],original[common])


def test_no_save_paths_and_body_limits(tmp_path,credentials):
    service=SatelliteService(tmp_path/'jobs.sqlite',httpx.Client(transport=httpx.MockTransport(lambda r:pytest.fail('No provider calls'))))
    with TestClient(create_app(service)) as client:
        assert client.post('/catalog',headers=HEADERS,json={**CATALOG,'save_path':'/tmp/x'}).status_code==422
        assert client.post('/plan',headers=HEADERS,content=b'x'*17000).status_code==413


def checked_evidence(count=0, coverage=1.0):
    return {'state':'observable' if coverage>=.8 else 'insufficient_clear_coverage',
            'common_usable_fraction':coverage, 'candidates_truncated':False,
            'candidates':{'type':'FeatureCollection','features':[{'properties':{'area_m2':900}} for _ in range(count)]}}


def assessed(before='uncertain', after='uncertain', change='uncertain'):
    return {'state':'complete','answers':{'before_canopy':{'choice':before},'after_canopy':{'choice':after},'canopy_change':{'choice':change}}}


@pytest.mark.parametrize('before,after,state',[
    ('yes','no','possible_disappearance'),('no','yes','possible_appearance'),
    ('yes','yes','visible_both'),('no','no','not_identified'),
    ('yes','uncertain','inconclusive'),('uncertain','no','inconclusive'),
    ('no','uncertain','inconclusive'),('uncertain','yes','inconclusive'),('uncertain','uncertain','inconclusive'),
])
def test_same_location_presence_decisions_do_not_invent_tree_identity(before,after,state):
    result=canopy_presence(checked_evidence(),assessed(before,after))
    assert result['state']==state
    assert result['before']==before and result['after']==after
    assert 'not an individual-tree' in result['scope']
    if before==after=='yes':assert 'partial loss' in result['interpretation']
    if (before,after)==('yes','no'):assert 'does not establish cutting' in result['interpretation']


def test_clouds_missing_classifier_and_invalid_answers_cannot_become_absence():
    for evidence,classification in [
        (checked_evidence(coverage=.3),assessed('yes','no')),
        (checked_evidence(),{**assessed('yes','no'),'state':'unavailable'}),
        (checked_evidence(),assessed('invalid','no')),
    ]:
        result=canopy_presence(evidence,classification)
        assert result['state']=='inconclusive'
        assert result['before']=='uncertain'


def test_presence_and_change_disagreement_is_explicit():
    result=canopy_presence(checked_evidence(1),assessed('yes','no','no_visible_loss'))
    assert result['state']=='conflicting_evidence'


@pytest.mark.parametrize('count,before,after,change,state',[
    (0,'yes','yes','no_visible_loss','no_candidate_detected'),
    (1,'yes','yes','no_visible_loss','review_required'),
    (0,'yes','no','possible_loss','review_required'),
    (1,'yes','no','possible_loss','review_required'),
    (1,'yes','no','no_visible_loss','conflicting_evidence'),
])
def test_interpretation_reconciles_numeric_and_image_decisions(count,before,after,change,state):
    result=summarize_comparison('canopy_loss',checked_evidence(count),assessed(before,after,change),{'before':TIMES[0],'after':TIMES[1],'query_window_relation':'overlaps_window'})
    assert result['state']==state
    text=' '.join(s['text'] for s in result['statements'])
    assert 'before that period' in text and 'exact event date' in text
    assert all(set(s['sources'])<={'before','after','spectral','coverage','assessment'} and s['sources'] for s in result['statements'])


def test_cloud_coverage_and_outside_dates_override_apparent_change():
    interval={'before':TIMES[0],'after':TIMES[1]}
    cloud=summarize_comparison('canopy_loss',checked_evidence(1,.2),assessed('yes','no','possible_loss'),interval)
    assert cloud['state']=='inconclusive'
    assert 'not enough clear imagery' in cloud['headline']
    outside=summarize_comparison('canopy_loss',checked_evidence(1),assessed('yes','no','possible_loss'),{**interval,'query_window_relation':'outside_window'})
    assert outside['state']=='outside_window'


def test_absence_of_visible_burn_does_not_mean_no_fire():
    classification={'state':'complete','answers':{'fire_evidence':{'choice':'no_visible_burn'}}}
    result=summarize_comparison('fire',checked_evidence(),classification,{'before':TIMES[0],'after':TIMES[1]})
    assert any('cannot establish that no fire occurred' in s['text'] for s in result['statements'])


def test_decisions_default_does_not_silently_switch_to_anthropic(monkeypatch):
    monkeypatch.delenv('SATELLITE_CLASSIFIER',raising=False)
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    monkeypatch.setenv('ANTHROPIC_API_KEY','test-only')
    assert ImageClassifier.selected_provider() is None
    monkeypatch.setenv('OPENAI_API_KEY','test-only')
    assert ImageClassifier.selected_provider()=='openai-decisions'
    monkeypatch.setenv('SATELLITE_CLASSIFIER','anthropic')
    assert ImageClassifier.selected_provider()=='anthropic'


def test_anthropic_assessment_uses_two_images_and_rejects_unbounded_findings(monkeypatch):
    monkeypatch.setenv('ANTHROPIC_API_KEY','test-only')
    choices={name:'uncertain' for name in QUESTIONS};choices.update(before_canopy='yes',after_canopy='no')
    def handler(request):
        body=json.loads(request.content)
        assert body['tool_choice']['name']=='assess_observations'
        assert len([p for p in body['messages'][0]['content'] if p['type']=='image'])==2
        return httpx.Response(200,json={'model':'test-model','stop_reason':'tool_use','content':[{'type':'tool_use','name':'assess_observations','input':choices}],
            'usage':{'input_tokens':100,'output_tokens':30,'untrusted':'discard'}})
    classifier=AnthropicClassifier(httpx.Client(transport=httpx.MockTransport(handler)))
    result=classifier.classify(b'before',b'after',{})
    assert result['answers']['before_canopy']['choice']=='yes'
    assert result['usage']=={'input_tokens':100,'output_tokens':30}
    choices['trees_cut']=37
    with pytest.raises(DomainError):classifier.classify(b'before',b'after',{})


def test_failed_decisions_call_retains_imagery_and_reserves_usage_once(tmp_path,credentials,monkeypatch):
    monkeypatch.setenv('ANTHROPIC_API_KEY','test-only')
    calls=[];base=transport(calls)
    def handler(request):
        if str(request.url)=='https://api.openai.com/v1/decisions':
            calls.append(str(request.url));return httpx.Response(503,json={'error':'unavailable'})
        return base.handle_request(request)
    service=SatelliteService(tmp_path/'jobs.sqlite',httpx.Client(transport=httpx.MockTransport(handler)))
    try:
        result=service.run_comparison(CompareRequest(**COMPARISON))
        assert result['classification']['state']=='unavailable'
        assert result['before']['image'].startswith('data:image/png')
        assert result['canopy_presence']['state']=='inconclusive'
        assert service.store.db.execute("SELECT used FROM quota WHERE operation='classifications'").fetchone()[0]==1
        assert calls.count('https://api.openai.com/v1/decisions')==1
        assert not any('anthropic.com' in url for url in calls)
    finally:service.close()
