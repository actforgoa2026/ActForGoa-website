"""Short-lived public metadata reuse, without sharing private observations."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import threading
import time
import httpx
import pytest
from satellite.domain import CatalogRequest, DomainError
from satellite.service import SatelliteService
from test_service import CATALOG, SCENES


def test_catalog_reuse_preserves_freshness_and_exact_area(tmp_path, monkeypatch):
    service = SatelliteService(tmp_path/'jobs.sqlite', httpx.Client())
    calls = []
    now = [100]
    monkeypatch.setattr('satellite.service.time.monotonic', lambda: now[0])
    def fetch(request):
        calls.append(request)
        return {'scenes': deepcopy(SCENES), 'searched_at': 'original-time', 'truncated': False}
    monkeypatch.setattr(service.cdse, 'catalog', fetch)
    try:
        query = CatalogRequest(**CATALOG)
        first = service.catalog(query)
        first['scenes'].clear()
        again = service.catalog(query)
        assert len(calls) == 1 and again['cache_hit']
        assert again['scenes'] == SCENES and again['searched_at'] == 'original-time'
        assert service.store.db.execute("SELECT used FROM quota WHERE operation='catalog'").fetchone()[0] == 1
        changed = CatalogRequest(**{**CATALOG, 'area': {'bbox': [73.820001,15.48,73.83,15.49]}})
        assert not service.catalog(changed)['cache_hit']
        now[0] = 221
        assert not service.catalog(query)['cache_hit']
        assert len(calls) == 3
    finally:
        service.close()


def test_concurrent_catalog_requests_share_success_but_not_failure(tmp_path, monkeypatch):
    service = SatelliteService(tmp_path/'jobs.sqlite', httpx.Client())
    entered, release = threading.Event(), threading.Event()
    calls = []
    def fetch(request):
        calls.append(request);entered.set();assert release.wait(3)
        return {'scenes': deepcopy(SCENES), 'searched_at': 'original-time'}
    monkeypatch.setattr(service.cdse, 'catalog', fetch)
    query = CatalogRequest(**CATALOG)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(service.catalog, query)
            assert entered.wait(3)
            second = pool.submit(service.catalog, query)
            release.set()
            assert not first.result()['cache_hit'] and second.result()['cache_hit']
        assert len(calls) == 1
        other = CatalogRequest(**{**CATALOG, 'end_date':'2025-10-27'})
        def fail(_):
            raise DomainError('unavailable', 'Try again')
        monkeypatch.setattr(service.cdse, 'catalog', fail)
        with pytest.raises(DomainError):service.catalog(other)
        monkeypatch.setattr(service.cdse, 'catalog', fetch)
        assert not service.catalog(other)['cache_hit']
    finally:
        service.close()
