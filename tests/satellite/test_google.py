"""Provider/authentication contracts, not environmental accuracy claims."""
from datetime import datetime, timezone
import json
import httpx
import pytest
from fastapi.testclient import TestClient
from satellite.app import create_app
from satellite.domain import Area, CatalogRequest, DomainError
from satellite.earth_engine import EarthEngine, COLLECTION
from satellite.google_maps import GoogleMaps
from satellite.service import SatelliteService

AREA = {'bbox': [73.845, 15.49, 73.85, 15.495]}


def test_earth_engine_namespaced_scene_and_date_validation():
    request = CatalogRequest(area=AREA, start_date='2025-10-20', end_date='2025-10-25')
    row = {'properties': {'scene_id':'20251020T052749_20251020T054119_T43PCT',
        'system:time_start':datetime(2025,10,20,5,44,40,5000,tzinfo=timezone.utc).timestamp()*1000,
        'CLOUDY_PIXEL_PERCENTAGE':36}, 'geometry':{'type':'Polygon','coordinates':[]}}
    scene = EarthEngine.scene(row, request)
    assert scene['id'].startswith('ee-') and scene['collection'] == COLLECTION
    assert scene['acquired_at'].endswith('.005000+00:00')
    grid = request.area.grid()
    assert SatelliteService._observation_key(scene['id'], grid) != SatelliteService._observation_key(scene['id'][3:], grid)
    row['properties']['system:time_start'] = 0
    with pytest.raises(ValueError):
        EarthEngine.scene(row, request)
    row['properties']['scene_id'] = '../../private-asset'
    with pytest.raises(ValueError):
        EarthEngine.scene(row, request)


def test_missing_earth_engine_credential_does_not_fallback(monkeypatch):
    monkeypatch.delenv('EARTH_ENGINE_CREDENTIALS_JSON', raising=False)
    with pytest.raises(DomainError, match='not connected'):
        EarthEngine(httpx.Client())._ee()


def test_google_context_partial_failure_and_secret_redaction(monkeypatch):
    monkeypatch.setenv('GOOGLE_MAPS_API_KEY','private-test-key')
    calls=[]
    def handler(request):
        calls.append(request)
        assert request.headers['x-goog-api-key'] == 'private-test-key'
        assert 'private-test-key' not in str(request.url)
        if request.url.host == 'weather.googleapis.com':
            return httpx.Response(403, json={'error':'private-test-key'})
        assert json.loads(request.content)['location'] == {'latitude':15.4925,'longitude':73.8475}
        return httpx.Response(200,json={'dateTime':'2026-10-29T12:00:00Z','indexes':[{'code':'uaqi','aqi':70}]})
    result=GoogleMaps(httpx.Client(transport=httpx.MockTransport(handler))).current(Area(**AREA))
    assert result['weather'] is None and result['unavailable'] == ['Weather']
    assert result['air_quality']['indexes'][0]['aqi'] == 70
    assert 'private-test-key' not in json.dumps(result) and len(calls) == 2


def test_google_environment_authenticated_and_bounded(monkeypatch,tmp_path):
    monkeypatch.setenv('SATELLITE_SERVICE_TOKEN','t'*40)
    monkeypatch.setenv('GOOGLE_MAPS_API_KEY','test-key')
    service=SatelliteService(tmp_path/'test.sqlite',httpx.Client(transport=httpx.MockTransport(lambda _:httpx.Response(200,json={}))))
    headers={'Authorization':'Bearer '+'t'*40,'X-Actor-ID':'google-test'}
    with TestClient(create_app(service)) as client:
        assert client.post('/environment',json={'area':AREA}).status_code == 401
        assert client.post('/environment',headers=headers,json={'area':{'bbox':[0,0,1,1]}}).status_code == 422
        for _ in range(50):
            assert client.post('/environment',headers=headers,json={'area':AREA}).status_code == 200
        assert client.post('/environment',headers=headers,json={'area':AREA}).status_code == 429


def test_preview_requires_authentication_and_bounded_dates(monkeypatch, tmp_path):
    monkeypatch.setenv('SATELLITE_SERVICE_TOKEN', 't'*40)
    service = SatelliteService(tmp_path/'preview.sqlite', httpx.Client())
    service.imagery_provider = 'earth-engine'
    calls=[]
    class PreviewProvider:
        def preview(self, request, on_generate):
            on_generate()
            calls.append(request)
            return {'provider':'earth-engine','scope':'navigation only'}
    service.cdse = PreviewProvider()
    headers={'Authorization':'Bearer '+'t'*40,'X-Actor-ID':'preview-test'}
    query={'start_date':'2026-01-01','end_date':'2026-01-31'}
    with TestClient(create_app(service)) as client:
        assert client.post('/preview',json=query).status_code == 401
        for dates in [('2026-02-01','2026-01-01'),('2025-01-01','2026-01-01'),('2016-01-01','2016-01-02'),('2099-01-01','2099-01-02')]:
            assert client.post('/preview',headers=headers,json=dict(zip(query,dates))).status_code == 422
        assert not calls
        assert client.post('/preview',headers=headers,json=query).status_code == 200
        assert len(calls) == 1


def test_preview_cache_keeps_navigation_separate_and_does_not_charge_again(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import MagicMock
    from satellite.domain import PreviewRequest
    provider=EarthEngine(httpx.Client())
    ee=MagicMock();images=ee.ImageCollection.return_value
    images.filterBounds.return_value=images;images.filterDate.return_value=images
    images.sort.return_value=images;images.limit.return_value=images
    ee.Dictionary.return_value.getInfo.return_value={'count':2,'first':1767225600000,'last':1768089600000}
    images.map.return_value.median.return_value.clip.return_value.getMapId.return_value={'tile_fetcher':SimpleNamespace(url_format='https://earthengine.googleapis.com/maps/test/tiles/{z}/{x}/{y}')}
    monkeypatch.setattr(provider,'_ee',lambda:ee)
    charged=[]
    query=PreviewRequest(start_date='2026-01-01',end_date='2026-01-31')
    first=provider.preview(query,lambda:charged.append(True));second=provider.preview(query,lambda:charged.append(True))
    assert first['method']=='cloud-masked median' and 'not an exact acquisition' in first['scope']
    assert not first['cache_hit'] and second['cache_hit'] and len(charged)==1
    assert first['tile_url']==second['tile_url']
    ee.ImageCollection.assert_called_once_with(COLLECTION)
    images.filterDate.assert_called_once_with('2026-01-01','2026-02-01')
