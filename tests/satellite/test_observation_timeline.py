"""Synthetic contracts for explicit map-image loading; no live provider calls."""
import base64
from datetime import datetime, timezone, timedelta
import io
import json
import threading
import time

import httpx
import numpy as np
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from pyproj import Transformer
from rasterio.transform import from_bounds

from satellite.app import create_app
from satellite.domain import Area, CompareRequest, DomainError, HistoryRequest, ObservationRequest
from satellite.evidence import map_layer, public_observation, read_observation
from satellite.service import SatelliteService
from satellite.store import Store
from test_service import AREA, CATALOG, COMPARISON, HEADERS, TIMES, PROCESS_URL, raster, transport, credentials


REQUEST = {**CATALOG, 'scene_id': 'scene-0'}


def wait_job(client, response, headers=HEADERS):
    assert response.status_code == 202, response.text
    job = response.json()['id']
    for _ in range(200):
        value = client.get('/jobs/' + job, headers=headers).json()
        if value['status'] != 'running':
            return value
        time.sleep(.01)
    pytest.fail('Synthetic observation did not complete')


def test_observation_has_actual_dates_georeferenced_image_and_no_decisions(tmp_path, credentials):
    calls = []
    service = SatelliteService(tmp_path/'jobs.sqlite', httpx.Client(transport=transport(calls)))
    with TestClient(create_app(service)) as client:
        assert client.post('/observation', json=REQUEST).status_code == 401
        assert client.post('/observation', headers={'Authorization': HEADERS['Authorization']}, json=REQUEST).status_code == 403
        assert not calls
        job = wait_job(client, client.post('/observation', headers=HEADERS, json=REQUEST))
        assert job['status'] == 'complete', job
        result = job['result']
        assert result['kind'] == 'observation'
        observation = result['observation']
        assert observation['catalog_scene_id'] == REQUEST['scene_id']
        assert observation['acquired_at'] == [TIMES[0]]
        assert observation['quality']['usable_fraction'] == 1
        assert observation['map_layer']['crs'] == 'EPSG:3857'
        assert observation['map_layer']['bbox_crs'] == 'EPSG:4326'
        assert 'image' not in observation['map_layer']
        assert observation['map_layer']['bbox'][0] < 73.82 < observation['map_layer']['bbox'][2]
        assert calls.count(PROCESS_URL) == 1
        assert not any('openai.com' in url or 'anthropic.com' in url or '/search?' in url for url in calls)
        assert 'classification' not in result
        assert client.post('/history', headers=HEADERS, json={}).json()['items'] == []
        assert client.get('/jobs/' + job['id'], headers={**HEADERS, 'X-Actor-ID': 'someone-else'}).status_code == 404


def test_cached_timeline_reloads_survive_restart_without_provider_or_quota(tmp_path, credentials):
    path = tmp_path/'jobs.sqlite'
    calls = []
    service = SatelliteService(path, httpx.Client(transport=transport(calls)))
    with TestClient(create_app(service)) as client:
        first = wait_job(client, client.post('/observation', headers=HEADERS, json=REQUEST))['result']
        count = len(calls)
        for _ in range(3):
            response = client.post('/observation', headers=HEADERS, json=REQUEST)
            assert response.status_code == 200
            assert response.json()['result']['cache_hit'] is True
            assert response.json()['result']['observation'] == first['observation']
        assert len(calls) == count
        assert service.store.db.execute('SELECT count(*) FROM jobs').fetchone()[0] == 1
        assert service.store.db.execute("SELECT used FROM quota WHERE operation='observations'").fetchone()[0] == 1
    service = SatelliteService(path, httpx.Client(transport=httpx.MockTransport(lambda request: pytest.fail('Cache hit must not contact a provider'))))
    with TestClient(create_app(service)) as client:
        assert client.post('/observation', headers=HEADERS, json=REQUEST).status_code == 200
        invalid_range = {**REQUEST, 'start_date': '2025-10-15'}
        assert client.post('/observation', headers=HEADERS, json=invalid_range).status_code == 400
        assert service._cached_observation('scene-0', Area(**AREA).grid(), 'different-actor') is None


def test_loaded_observations_reused_by_compare_but_not_other_actor(tmp_path, credentials):
    calls = []
    service = SatelliteService(tmp_path/'jobs.sqlite', httpx.Client(transport=transport(calls)))
    with TestClient(create_app(service)) as client:
        wait_job(client, client.post('/observation', headers=HEADERS, json=REQUEST))
        wait_job(client, client.post('/observation', headers=HEADERS, json={**REQUEST, 'scene_id': 'scene-1'}))
        assert calls.count(PROCESS_URL) == 2
        comparison = wait_job(client, client.post('/compare', headers=HEADERS, json=COMPARISON))
        assert comparison['status'] == 'complete', comparison
        assert comparison['result']['before']['map_layer']['bbox'] == comparison['result']['after']['map_layer']['bbox']
        assert calls.count(PROCESS_URL) == 2
        assert len(client.post('/history', headers=HEADERS, json={}).json()['items']) == 1
        other = wait_job(client, client.post('/observation', headers={**HEADERS, 'X-Actor-ID': 'someone-else'}, json=REQUEST),
                         {**HEADERS, 'X-Actor-ID': 'someone-else'})
        assert other['status'] == 'complete'
        assert calls.count(PROCESS_URL) == 3


def test_area_mask_and_scene_are_part_of_cache_identity(tmp_path, credentials):
    service = SatelliteService(tmp_path/'jobs.sqlite', httpx.Client(transport=httpx.MockTransport(lambda request: pytest.fail('No provider call expected'))))
    try:
        a = Area(**AREA).grid()
        b = Area(bbox=[73.820001, 15.480001, 73.83, 15.49]).grid()
        c = Area(bbox=[73.83, 15.48, 73.84, 15.49]).grid()
        assert a['bounds'] == b['bounds'], 'Fixture must exercise different masks on an identical snapped grid'
        keys = {service._observation_key(scene, grid) for scene, grid in [('scene-0', a), ('scene-0', b), ('scene-0', c), ('scene-1', a)]}
        assert len(keys) == 4
        service.store.cache_observation('editor-one', service._observation_key('scene-0', a), raster(a), {'catalog_scene_id': 'scene-0'})
        assert service._cached_observation('scene-0', b, 'editor-one') is None
        assert service._cached_observation('scene-0', c, 'editor-one') is None
    finally:
        service.close()


def test_unlisted_or_mismatched_scene_never_becomes_displayed_image(tmp_path, credentials):
    calls = []
    service = SatelliteService(tmp_path/'jobs.sqlite', httpx.Client(transport=transport(calls, stale=True)))
    with TestClient(create_app(service)) as client:
        missing = wait_job(client, client.post('/observation', headers=HEADERS, json={**REQUEST, 'scene_id': 'invented'}))
        assert missing['status'] == 'failed'
        assert missing['result']['code'] == 'scene_unavailable'
        assert calls.count(PROCESS_URL) == 0
        mismatched = wait_job(client, client.post('/observation', headers=HEADERS, json=REQUEST))
        assert mismatched['status'] == 'failed'
        assert mismatched['result']['code'] == 'invalid_provenance'
        assert service.store.db.execute('SELECT count(*) FROM observations').fetchone()[0] == 0
        assert not any('openai.com' in url for url in calls)


def test_observation_retrievals_share_capacity_and_persistent_daily_limit(tmp_path, credentials):
    calls = []
    path = tmp_path/'jobs.sqlite'
    service = SatelliteService(path, httpx.Client(transport=transport(calls)))
    with TestClient(create_app(service)) as client:
        service.capacity.acquire()
        assert client.post('/observation', headers=HEADERS, json=REQUEST).status_code == 429
        service.capacity.release()
        for _ in range(20):
            service.store.reserve('observations', 20)
        assert client.post('/observation', headers=HEADERS, json=REQUEST).status_code == 429
        assert not calls
        # Failure releases the one-worker capacity.
        assert service.capacity.acquire(blocking=False)
        service.capacity.release()
    service = SatelliteService(path, httpx.Client(transport=transport(calls)))
    with TestClient(create_app(service)) as client:
        assert client.post('/observation', headers=HEADERS, json=REQUEST).status_code == 429
        assert not calls


def test_cached_decode_and_projection_share_capacity(tmp_path, credentials, monkeypatch):
    calls = []
    service = SatelliteService(tmp_path/'jobs.sqlite', httpx.Client(transport=transport(calls)))
    with TestClient(create_app(service)) as client:
        wait_job(client, client.post('/observation', headers=HEADERS, json=REQUEST))
        entered, release = threading.Event(), threading.Event()
        cached = service._cached_observation
        def held_decode(*args):
            entered.set()
            assert release.wait(5)
            return cached(*args)
        monkeypatch.setattr(service, '_cached_observation', held_decode)
        completed, failed = [], []
        def retrieve():
            try:
                completed.append(service.observation(ObservationRequest(**REQUEST), 'editor-one'))
            except Exception as error:
                failed.append(error)
        worker = threading.Thread(target=retrieve)
        worker.start()
        try:
            assert entered.wait(5)
            with pytest.raises(DomainError) as error:
                service.observation(ObservationRequest(**REQUEST), 'editor-one')
            assert error.value.code == 'busy'
            with pytest.raises(DomainError):
                service.compare(CompareRequest(**COMPARISON), 'editor-one')
        finally:
            release.set()
            worker.join(timeout=5)
        assert not failed and completed[0]['result']['cache_hit']
        assert service.capacity.acquire(blocking=False)
        service.capacity.release()
        assert calls.count(PROCESS_URL) == 1


def test_web_mercator_overlay_matches_projected_pixel_and_transparency():
    grid = Area(**AREA).grid()
    observation = read_observation(raster(grid), grid)
    # Mark a single native pixel with a distinctive color. The projected marker
    # must land at that point's actual Web Mercator map coordinate, not merely
    # at the same relative location in a stretched longitude/latitude rectangle.
    native = np.zeros((grid['height'], grid['width'], 4), dtype='uint8')
    row, col = 25, 30
    native[row, col] = [255, 0, 0, 255]
    payload = io.BytesIO()
    Image.fromarray(native).save(payload, format='PNG')
    observation['png'] = payload.getvalue()
    layer = map_layer(observation)
    image = np.array(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',', 1)[1]))))
    assert image.shape == (layer['height'], layer['width'], 4)
    assert np.count_nonzero(image[:, :, 3]) in (1, 2)
    x, y = observation['transform'] * (col + .5, row + .5)
    marker_x, marker_y = Transformer.from_crs(32643, 3857, always_xy=True).transform(x, y)
    w, s, e, n = layer['bbox']
    west, south = Transformer.from_crs(4326, 3857, always_xy=True).transform(w, s)
    east, north = Transformer.from_crs(4326, 3857, always_xy=True).transform(e, n)
    transform = from_bounds(west, south, east, north, layer['width'], layer['height'])
    target_col, target_row = ~transform * (marker_x, marker_y)
    assert image[int(target_row), int(target_col)].tolist() == [255, 0, 0, 255]
    assert np.array_equal(observation['bands'], read_observation(raster(grid), grid)['bands'])


def test_large_high_detail_pair_fits_proxy_with_one_display_png_per_observation():
    grid = Area(bbox=[74, 15.2, 74.046, 15.245]).grid()
    assert grid['area_m2'] > 24_000_000
    observation = read_observation(raster(grid), grid)
    rgba = np.random.default_rng(42).integers(0, 256, (grid['height'], grid['width'], 4), dtype='uint8')
    rgba[:, :, 3] = 255
    payload = io.BytesIO()
    Image.fromarray(rgba).save(payload, format='PNG')
    observation['png'] = payload.getvalue()
    public = public_observation(observation, {'catalog_scene_id': 'synthetic-large-scene', 'acquired_at': [TIMES[0]]})
    assert 'image' not in public['map_layer']
    assert public['image'] == map_layer(observation)['image']
    # Leave substantial room under 4 MiB for candidates and result metadata;
    # opaque random RGB is deliberately harder to compress than typical tiles.
    size = len(json.dumps({'before': public, 'after': public}).encode())
    assert size < 3 * 1024 * 1024


def test_cache_retention_actor_scope_count_and_byte_bounds(tmp_path):
    path = tmp_path/'jobs.sqlite'
    store = Store(path)
    try:
        for number in range(61):
            store.cache_observation('actor', str(number), b'x', {})
        assert store.db.execute('SELECT count(*) FROM observations').fetchone()[0] == 60
        assert store.observation('other-actor', '60') is None
        for number in range(9):
            store.cache_observation('actor', 'large-' + str(number), b'x' * 16_000_000, {})
        assert store.db.execute('SELECT sum(length(spectral)) FROM observations').fetchone()[0] <= 128 * 1024 * 1024
        with pytest.raises(DomainError):
            store.cache_observation('actor', 'too-large', b'x' * 16_000_001, {})
        store.db.execute('UPDATE observations SET created=?', ((datetime.now(timezone.utc) - timedelta(days=31)).isoformat(),))
        store.db.commit()
        assert store.observation('actor', 'large-8') is None
    finally:
        store.close()
    store = Store(path)
    try:
        assert store.db.execute('SELECT count(*) FROM observations').fetchone()[0] == 0
    finally:
        store.close()


def test_observation_jobs_expire_without_erasing_saved_comparisons(tmp_path):
    store = Store(tmp_path/'jobs.sqlite')
    try:
        observation = store.start('actor', {**REQUEST, 'kind': 'observation'})
        comparison = store.start('actor', COMPARISON)
        store.db.execute('UPDATE jobs SET created=?', ((datetime.now(timezone.utc)-timedelta(days=2)).isoformat(),))
        store.db.commit()
        store.start('actor', COMPARISON)
        with pytest.raises(DomainError):
            store.get(observation, 'actor')
        assert store.get(comparison, 'actor')['request']['intent'] == 'canopy_loss'
        assert len(store.history('actor', HistoryRequest())['items']) == 2
    finally:
        store.close()
