from dataclasses import replace
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from types import SimpleNamespace

import httpx
import pytest
from shapely.geometry import box, mapping
from shapely.ops import transform
from shapely.errors import ShapelyError

from satellite.amche import AmcheContext, SOURCES, _CACHE, _CACHE_LOCK
from satellite.domain import Area, TO_UTM


AREA = Area(bbox=[73.82, 15.48, 73.83, 15.49])


def feature(geometry=None, **properties):
    return {'type': 'Feature', 'geometry': geometry or mapping(box(73.822, 15.482, 73.824, 15.484)),
            'properties': {'id': 'record-1', 'name': 'Reference pond', 'village': 'Test village', **properties}}


def fixture(features=None, **extra):
    raw = json.dumps({'type': 'FeatureCollection', 'features': features if features is not None else [feature()], **extra}).encode()
    source = replace(SOURCES[0], sha256=hashlib.sha256(raw).hexdigest())
    return raw, source


@pytest.fixture(autouse=True)
def clear_cache():
    with _CACHE_LOCK:
        _CACHE.clear()
    yield
    with _CACHE_LOCK:
        _CACHE.clear()


def client_for(raw, handler=None, **kwargs):
    return httpx.Client(transport=httpx.MockTransport(handler or (lambda request: httpx.Response(200, content=raw))), **kwargs)


def test_context_uses_true_polygon_intersection_and_metric_area():
    # The notch contains the selection; its exterior bbox overlaps the selection,
    # but the actual polygon does not. A bbox-only join would report a false hit.
    ring = [[73.819,15.479],[73.831,15.479],[73.831,15.491],[73.829,15.491],
            [73.829,15.481],[73.821,15.481],[73.821,15.491],[73.819,15.491],[73.819,15.479]]
    selection = Area(bbox=[73.823,15.483,73.827,15.487])
    raw, source = fixture([feature({'type':'Polygon','coordinates':[ring]})])
    with client_for(raw) as client:
        result = AmcheContext(client, sources=[source]).search(selection)
    assert result['state'] == 'no_matches'
    assert result['layers'][0]['union_overlap_m2'] == 0
    with _CACHE_LOCK:
        _CACHE.clear()
    geometry = box(73.822,15.482,73.824,15.484)
    raw, source = fixture([feature(mapping(geometry))])
    with client_for(raw) as client:
        layer = AmcheContext(client, sources=[source]).search(AREA.grid())['layers'][0]
    expected = transform(TO_UTM, geometry).area
    assert layer['union_overlap_m2'] == pytest.approx(expected, abs=.01)
    assert layer['matches'][0]['intersection_area_m2'] == pytest.approx(expected, abs=.01)
    assert 0 < layer['query_fraction'] < 1
    assert layer['reference_date'] == 'Water Body Atlas 2025'
    assert layer['effective_date'] is None


def test_queries_and_credentials_never_forwarded_and_snapshot_cache_is_shared():
    raw, source = fixture()
    requests = []
    def handle(request):
        requests.append(request)
        assert str(request.url) == source.url
        assert request.method == 'GET' and request.content == b''
        assert set(request.headers) == {'host', 'accept', 'user-agent'}
        return httpx.Response(200, content=raw)
    with client_for(raw, handle, headers={'Authorization':'Bearer private', 'Cookie':'private=1', 'X-Actor-ID':'private'}, auth=('private','private'), params={'secret':'private'}) as client:
        contexts = [AmcheContext(client, sources=[source]) for _ in range(4)]
        with ThreadPoolExecutor(max_workers=4) as executor:
            values = list(executor.map(lambda context: context.search(AREA), contexts))
    assert len(requests) == 1
    assert all(value['state'] == 'available' for value in values)
    assert len({value['layers'][0]['fetched_at'] for value in values}) == 1


def test_duplicate_source_ids_keep_unique_citations_but_not_double_overlap_area():
    raw, source = fixture([feature(), feature(name='Second source entry')])
    with client_for(raw) as client:
        layer = AmcheContext(client, sources=[source]).search(AREA)['layers'][0]
    assert layer['matched_records'] == 2
    assert layer['duplicate_source_id_count'] == 1
    assert len({match['id'] for match in layer['matches']}) == 2
    assert {match['source_record_id'] for match in layer['matches']} == {'record-1'}
    assert layer['union_overlap_m2'] == layer['matches'][0]['intersection_area_m2']


def test_boundary_points_are_locations_without_forest_extent():
    raw, source = fixture([feature({'type':'Point','coordinates':[73.82,15.48]}, match_accuracy='unmatched')])
    source = replace(source, id='private-forests')
    with client_for(raw) as client:
        layer = AmcheContext(client, sources=[source]).search(AREA)['layers'][0]
    assert layer['point_match_count'] == 1
    assert layer['polygon_match_count'] == 0
    assert layer['union_overlap_m2'] == 0
    assert layer['matches'][0]['relation'] == 'location_only'
    assert layer['matches'][0]['intersection_area_m2'] is None
    assert layer['matches'][0]['query_fraction'] is None


def test_invalid_geometries_quarantined_properties_bounded_and_owners_excluded():
    crossed = {'type':'Polygon','coordinates':[[[73.821,15.481],[73.825,15.485],[73.825,15.481],[73.821,15.485],[73.821,15.481]]]}
    raw, source = fixture([feature(crossed), feature(name='x'*500, owners='private names', html='<script>', url='javascript:alert(1)')])
    with client_for(raw) as client:
        result = AmcheContext(client, sources=[source]).search(AREA)
    layer = result['layers'][0]
    assert result['state'] == 'partial'
    assert layer['excluded_record_count'] == 1 and layer['valid_record_count'] == 1
    assert len(layer['matches'][0]['label']) <= 480
    assert 'private names' not in json.dumps(result)
    assert '<script>' not in json.dumps(result) and 'javascript:' not in json.dumps(result)


@pytest.mark.parametrize('change', ['crs','hash','outside','feature-limit'])
def test_invalid_source_is_unavailable_not_zero_matches(change):
    raw, source = fixture()
    if change == 'crs':
        raw, source = fixture(crs={'type':'name','properties':{'name':'EPSG:32643'}})
    elif change == 'outside':
        raw, source = fixture([feature({'type':'Point','coordinates':[0,0]})])
    elif change == 'feature-limit':
        raw, source = fixture([feature()] * 5001)
    else:
        source = replace(source, sha256='0'*64)
    with client_for(raw) as client:
        result = AmcheContext(client, sources=[source]).search(AREA)
    assert result['state'] == 'unavailable'
    assert result['layers'][0]['match_state'] == 'unknown'
    assert 'union_overlap_m2' not in result['layers'][0]


def test_outage_and_redirect_are_cached_without_following_or_inferring_absence():
    raw, source = fixture()
    calls = []
    def handle(request):
        calls.append(str(request.url))
        return httpx.Response(302, headers={'location':'https://untrusted.example/private'})
    with client_for(raw, handle) as client:
        context = AmcheContext(client, sources=[source])
        assert context.search(AREA)['state'] == 'unavailable'
        assert context.search(AREA)['state'] == 'unavailable'
    assert calls == [source.url]


def test_streaming_limit_and_truncated_match_output():
    raw, source = fixture([feature(id=index) for index in range(25)])
    with client_for(raw) as client:
        layer = AmcheContext(client, sources=[source]).search(AREA)['layers'][0]
    assert layer['matched_records'] == 25 and len(layer['matches']) == 20 and layer['truncated']
    with _CACHE_LOCK:
        _CACHE.clear()
    source = replace(source, maximum=10)
    with client_for(raw, lambda request:httpx.Response(200, stream=httpx.ByteStream(raw))) as client:
        assert AmcheContext(client, sources=[source]).search(AREA)['state'] == 'unavailable'


def test_empty_registry_is_distinct_from_unavailable():
    with client_for(b'') as client:
        result = AmcheContext(client, sources=[]).search(AREA)
    assert result['state'] == 'not_configured' and result['layers'] == []


def test_topology_operation_failure_is_unavailable_not_an_empty_finding(monkeypatch):
    import satellite.amche as amche
    def failure(_values):
        raise ShapelyError('internal topology detail')
    monkeypatch.setattr(amche, 'unary_union', failure)
    raw, source = fixture()
    with client_for(raw) as client:
        result = AmcheContext(client, sources=[source]).search(AREA)
    assert result['state'] == 'unavailable'
    assert 'internal topology detail' not in json.dumps(result)
    assert 'does not establish' in result['message']


def test_slow_stream_has_total_deadline_and_is_closed(monkeypatch):
    import satellite.amche as amche
    clock = [0.0]
    monkeypatch.setattr(amche, 'time', SimpleNamespace(monotonic=lambda:clock[0]))
    raw, source = fixture()
    closed = []
    class SlowStream(httpx.SyncByteStream):
        def __iter__(self):
            yield raw[:10]
            clock[0] = 13.0
            yield raw[10:]
        def close(self):
            closed.append(True)
    with client_for(raw, lambda request:httpx.Response(200,stream=SlowStream())) as client:
        assert AmcheContext(client,sources=[source]).search(AREA)['state'] == 'unavailable'
    assert closed


def test_busy_fetch_lock_is_bounded_and_does_not_block_healthy_cache():
    raw, source = fixture()
    entered, release = threading.Event(), threading.Event()
    def hold():
        with _CACHE_LOCK:
            entered.set()
            release.wait(timeout=5)
    with client_for(raw) as client:
        context = AmcheContext(client,sources=[source])
        cached = context._snapshot(source)
        thread = threading.Thread(target=hold)
        thread.start(); assert entered.wait(timeout=1)
        try:
            start = time.monotonic()
            assert context._snapshot(source) is cached
            assert time.monotonic()-start < .5
            start = time.monotonic()
            assert context._snapshot(replace(source,id='uncached')) is None
            assert time.monotonic()-start < 3
        finally:
            release.set(); thread.join(timeout=1)
    assert not any(key[0]=='uncached' for key in _CACHE)
