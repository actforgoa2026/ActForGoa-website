from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
import threading
import time
import httpx
from .domain import CatalogRequest, CompareRequest, ObservationRequest, EvidenceRequest, DomainError, Query, make_plan, change_interval
from .eve_cdse import CDSE
from .earth_engine import EarthEngine
from .evidence import read_observation, compare_pixels, public_observation, classification_image
from .providers import AnthropicPlanner, ImageClassifier
from .summary import summarize_comparison, canopy_presence
from .context import EcologyContext
from .store import Store
from .evidence_query import build_evidence


class SatelliteService:
    def __init__(self, path, client=None):
        self.http = client or httpx.Client(timeout=45, follow_redirects=False)
        self.store = Store(path)
        self.imagery_provider = os.getenv('SATELLITE_IMAGERY_PROVIDER', 'cdse')
        if self.imagery_provider not in {'cdse', 'earth-engine'}:
            raise ValueError('Unknown SATELLITE_IMAGERY_PROVIDER')
        self.cdse = EarthEngine(self.http) if self.imagery_provider == 'earth-engine' else CDSE(self.http)
        self.planner = AnthropicPlanner(self.http)
        self.classifier = ImageClassifier(self.http)
        self.context = EcologyContext(self.http)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.capacity = threading.BoundedSemaphore(1)
        self._catalog_lock = threading.Lock()
        self._catalogs = {}

    def plan(self, query: Query):
        self.store.reserve('plans', 30)
        return make_plan(query, self.planner.interpret(query))

    def catalog(self, request: CatalogRequest):
        # The browser searches immediately before loading an observation. Reuse
        # that verified, short-lived catalog instead of repeating the provider
        # request in the worker. Only public scene metadata is shared; imagery
        # and jobs retain their existing actor-scoped storage.
        key = (self.imagery_provider, request.area.bbox, request.start_date, request.end_date)
        with self._catalog_lock:
            now = time.monotonic()
            self._catalogs = {k: v for k, v in self._catalogs.items() if v[0] > now}
            cached = self._catalogs.get(key)
            if cached:
                return {**deepcopy(cached[1]), 'cache_hit': True}
            self.store.reserve('catalog', 100)
            result = self.cdse.catalog(request)
            if len(self._catalogs) >= 32:
                self._catalogs.pop(next(iter(self._catalogs)))
            self._catalogs[key] = (time.monotonic() + 120, deepcopy(result))
            return {**result, 'cache_hit': False}

    def evidence(self, request: EvidenceRequest, actor: str):
        rows, truncated = self.store.evidence_rows(actor, request)
        result = build_evidence(request, rows, truncated)
        if request.include_context:
            from .amche import AmcheContext
            try:
                result['amche_context'] = AmcheContext(self.http).search(request.area.grid())
            except Exception:
                # Optional reference sources must never erase saved evidence.
                result['amche_context'] = {'state':'unavailable','layers':[],'matched_records':0,
                    'coverage':'not_established','checked_at':datetime.now(timezone.utc).isoformat(),
                    'message':'Map context could not be checked. Saved satellite evidence is retained; no absence of mapped records is inferred.'}
            try:
                result['library_context'] = self.context.search(request.question, request.intent.value if request.intent else None)
            except Exception:
                result['library_context'] = {'state':'unavailable','sources':[],
                    'message':'Ecology background could not be checked. Saved satellite evidence is retained.'}
        return result

    @staticmethod
    def _observation_key(scene_id, grid):
        # Include the clipped geometry as well as the snapped grid: adjacent
        # selections can share raster dimensions but have different ROI masks.
        value = {'version': 1, 'scene_id': scene_id, 'crs': grid['crs'],
                 'bounds': grid['bounds'], 'width': grid['width'], 'height': grid['height'],
                 'geometry': grid['geometry']}
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

    def _cached_observation(self, scene_id, grid, actor):
        if actor is None:
            return None
        cached = self.store.observation(actor, self._observation_key(scene_id, grid))
        if cached is None:
            return None
        spectral, provenance, created = cached
        if provenance.get('catalog_scene_id') != scene_id:
            raise DomainError('invalid_provenance', 'The saved observation does not match the selected scene.', 502)
        return read_observation(spectral, grid), provenance, created

    def _load_observation(self, scene, grid, actor=None):
        cached = self._cached_observation(scene['id'], grid, actor)
        if cached and cached[1].get('catalog_acquired_at') == scene['acquired_at']:
            return cached[0], cached[1]
        spectral, provenance = self.cdse.observation(scene, grid)
        observation = read_observation(spectral, grid)
        if actor is not None:
            self.store.cache_observation(actor, self._observation_key(scene['id'], grid), spectral, provenance)
        return observation, provenance

    @staticmethod
    def _observation_result(observation, provenance, grid, cached=False):
        return {'kind': 'observation', 'observation': public_observation(observation, provenance),
                'area': {'geometry': grid['wgs84_geometry'], 'area_m2': round(grid['area_m2']),
                         'clipped_to_goa': grid['clipped_to_goa']},
                'cache_hit': cached, 'generated_at': datetime.now(timezone.utc).isoformat(),
                'note': 'A dated observation, not a change finding. Browsing imagery does not run image decisions.'}

    def observation(self, request: ObservationRequest, actor: str):
        if not self.capacity.acquire(blocking=False):
            raise DomainError('busy', 'Another imagery request is running. Please try again shortly.', 429)
        handed_off = False
        try:
            # Decoding/reprojecting a cached TIFF uses substantial memory too.
            # Keep it under the same one-request bound as provider retrieval.
            grid = request.area.grid()
            cached = self._cached_observation(request.scene_id, grid, actor)
            if cached:
                acquired = datetime.fromisoformat(cached[1]['catalog_acquired_at'].replace('Z', '+00:00'))
                if not request.start_date <= acquired.date() <= request.end_date:
                    raise DomainError('scene_unavailable', 'The selected observation is outside this date range.')
                # Cache hits return directly: no provider call, reservation or
                # duplicate stored image job is created by moving back in time.
                return {'status': 'complete', 'result': self._observation_result(cached[0], cached[1], grid, True)}
            self.store.reserve('observations', 20)
            job = self.store.start(actor, {**request.model_dump(mode='json'), 'kind': 'observation'})
            self.executor.submit(self._run_observation, job, request, actor)
            handed_off = True
            return {'id': job, 'status': 'running'}
        finally:
            if not handed_off:
                self.capacity.release()

    def _run_observation(self, job, request, actor):
        try:
            catalog = self.catalog(CatalogRequest.model_validate(request.model_dump(include={'area', 'start_date', 'end_date'})))
            scene = next((value for value in catalog['scenes'] if value['id'] == request.scene_id), None)
            if scene is None:
                raise DomainError('scene_unavailable', 'This observation is unavailable in the current catalog. Search again.')
            grid = request.area.grid()
            observation, provenance = self._load_observation(scene, grid, actor)
            self.store.finish(job, self._observation_result(observation, provenance, grid))
        except DomainError as error:
            self.store.finish(job, {'error': error.message, 'code': error.code}, failed=True)
        except Exception:
            self.store.finish(job, {'error': 'The observation could not be retrieved. No image was inferred.', 'code': 'observation_failed'}, failed=True)
        finally:
            self.capacity.release()

    def compare(self, request: CompareRequest, actor: str):
        if not self.capacity.acquire(blocking=False):
            raise DomainError('busy', 'Another comparison is running. Please try again shortly.', 429)
        try:
            self.store.reserve('comparisons', 10)
            job = self.store.start(actor,request.model_dump(mode='json'))
            self.executor.submit(self._run, job, request, actor)
            return {'id': job, 'status': 'running'}
        except Exception:
            self.capacity.release()
            raise

    def _run(self, job, request, actor):
        try:
            self.store.finish(job, self.run_comparison(request, actor))
        except DomainError as error:
            self.store.finish(job, {'error':error.message,'code':error.code}, failed=True)
        except Exception:
            # Provider bodies and credentials must never enter saved errors or logs.
            self.store.finish(job, {'error':'The comparison failed safely. No finding was inferred.','code':'comparison_failed'}, failed=True)
        finally:
            self.capacity.release()

    def run_comparison(self, request, actor=None):
        catalog_request = CatalogRequest.model_validate(request.model_dump(include={'area','start_date','end_date'}))
        catalog = self.catalog(catalog_request)
        scenes = {s['id']:s for s in catalog['scenes']}
        if request.before_id not in scenes or request.after_id not in scenes:
            raise DomainError('scene_unavailable', 'One selected scene is unavailable in the current catalog. Search again.')
        a,b = scenes[request.before_id],scenes[request.after_id]
        if datetime.fromisoformat(a['acquired_at']) >= datetime.fromisoformat(b['acquired_at']):
            raise DomainError('invalid_order', 'Choose two different observations in chronological order.')
        grid = request.area.grid()
        before, before_source = self._load_observation(a, grid, actor)
        after, after_source = self._load_observation(b, grid, actor)
        evidence = compare_pixels(before, after, grid)
        identity = {'geometry':grid['wgs84_geometry'],'crs':grid['crs'],'bounds':grid['bounds'],'resolution_m':10}
        target = {'id':'area-'+hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24],
                  'geometry':grid['wgs84_geometry'],'bounds':grid['bounds'],'crs':grid['crs'],'geometry_crs':'EPSG:4326',
                  'area_m2':round(grid['area_m2']),'grid_resolution_m':10,'native_swir_scl_resolution_m':20,
                  'granularity':'area_canopy','common_usable_fraction':evidence['common_usable_fraction']}
        classification = {'state':'skipped','answers':{},'message':'Insufficient common clear coverage for reliable image classification.'}
        if evidence['state'] == 'observable':
            try:
                if self.classifier.selected_provider():
                    self.store.reserve('classifications', 10)
                common = before['clear'] & after['clear']
                classification = self.classifier.classify(classification_image(before, common), classification_image(after, common), {
                    'before':before_source, 'after':after_source, 'spectral_metrics':evidence['metrics'],
                    'target':target,
                    'common_usable_fraction':evidence['common_usable_fraction'], 'area_m2':grid['area_m2'],
                    'intent':request.intent.value,'water_change':evidence['water_change'],
                    'numeric_vegetation_loss_candidates':len(evidence['candidates']['features'])})
            except (DomainError, httpx.HTTPError):
                classification = {'state':'unavailable','answers':{},'message':'Image classification was unavailable. The measured imagery evidence is retained.'}
        interval = {'before':a['acquired_at'],'after':b['acquired_at'],'exact_event_date':None,'cause':'not_established'}
        if request.window_start:
            interval['query_window_relation'] = change_interval(a['acquired_at'], b['acquired_at'], request.window_start.isoformat(), request.window_end.isoformat())['relation']
        latest=max(catalog['scenes'],key=lambda scene:datetime.fromisoformat(scene['acquired_at']))['acquired_at']
        freshness={'catalog_searched_at':catalog.get('searched_at'),'latest_acquired_at_in_search':latest,
            'selected_after_acquired_at':b['acquired_at'],
            'newer_acquisitions_in_search':sum(datetime.fromisoformat(scene['acquired_at'])>datetime.fromisoformat(b['acquired_at']) for scene in catalog['scenes']),
            'search_start':request.start_date.isoformat(),'search_end':request.end_date.isoformat(),'catalog_truncated':catalog['truncated'],
            'note':'Acquisition availability is not clear-sky coverage. Newer scenes have not necessarily been checked for local visibility.'}
        # No exact event time or cause is generated from image differences.
        return {'intent':request.intent.value,'target':target,'evidence':evidence,'classification':classification,
                'summary':summarize_comparison(request.intent.value,evidence,classification,interval),
                'canopy_presence':canopy_presence(evidence,classification),
                'freshness':freshness,'library_context':self.context.search(request.question,request.intent.value),
                'planning_context':{'state':'not_checked','legal_status':'not_established',
                    'message':'No parcel permissions or planning records have been joined. Visible construction does not establish whether a building is lawful.'},
                'before':public_observation(before,before_source),'after':public_observation(after,after_source),
                'area':{'geometry':grid['wgs84_geometry'],'area_m2':round(grid['area_m2']),'clipped_to_goa':grid['clipped_to_goa']},
                'observation_interval': interval,
                'fire_detections': {'state':'not_queried','message':'FIRMS has not been queried. No conclusion about absence of fire is supported.'},
                'limitations':['Possible vegetation loss is not a count of trees and does not establish cutting.',
                               'Seasonal vegetation, plantations, crop harvest, water level and alignment effects require review.',
                               'These are the selected observations, not necessarily the last clear presence and first clear absence.',
                               'Findings are exploratory and have not passed Goa field validation.'],
                'generated_at':datetime.now(timezone.utc).isoformat()}

    def close(self):
        self.executor.shutdown(wait=True)
        self.http.close()
        self.store.close()
