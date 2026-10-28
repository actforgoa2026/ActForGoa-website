from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import threading
import httpx
from .domain import CatalogRequest, CompareRequest, DomainError, Query, make_plan, change_interval
from .eve_cdse import CDSE
from .evidence import read_observation, compare_pixels, public_observation, classification_image
from .providers import AnthropicPlanner, DecisionsClassifier
from .store import Store


class SatelliteService:
    def __init__(self, path, client=None):
        self.http = client or httpx.Client(timeout=45, follow_redirects=False)
        self.store = Store(path)
        self.cdse = CDSE(self.http)
        self.planner = AnthropicPlanner(self.http)
        self.classifier = DecisionsClassifier(self.http)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.capacity = threading.BoundedSemaphore(1)

    def plan(self, query: Query):
        self.store.reserve('plans', 30)
        return make_plan(query, self.planner.interpret(query))

    def catalog(self, request: CatalogRequest):
        self.store.reserve('catalog', 100)
        return self.cdse.catalog(request)

    def compare(self, request: CompareRequest, actor: str):
        if not self.capacity.acquire(blocking=False):
            raise DomainError('busy', 'Another comparison is running. Please try again shortly.', 429)
        try:
            self.store.reserve('comparisons', 10)
            job = self.store.start(actor)
            self.executor.submit(self._run, job, request)
            return {'id': job, 'status': 'running'}
        except Exception:
            self.capacity.release()
            raise

    def _run(self, job, request):
        try:
            self.store.finish(job, self.run_comparison(request))
        except DomainError as error:
            self.store.finish(job, {'error':error.message,'code':error.code}, failed=True)
        except Exception:
            # Provider bodies and credentials must never enter saved errors or logs.
            self.store.finish(job, {'error':'The comparison failed safely. No finding was inferred.','code':'comparison_failed'}, failed=True)
        finally:
            self.capacity.release()

    def run_comparison(self, request):
        catalog_request = CatalogRequest.model_validate(request.model_dump(include={'area','start_date','end_date'}))
        catalog = self.catalog(catalog_request)
        scenes = {s['id']:s for s in catalog['scenes']}
        if request.before_id not in scenes or request.after_id not in scenes:
            raise DomainError('scene_unavailable', 'One selected scene is unavailable in the current catalog. Search again.')
        a,b = scenes[request.before_id],scenes[request.after_id]
        if datetime.fromisoformat(a['acquired_at']) >= datetime.fromisoformat(b['acquired_at']):
            raise DomainError('invalid_order', 'Choose two different observations in chronological order.')
        grid = request.area.grid()
        before_data, before_source = self.cdse.observation(a, grid)
        after_data, after_source = self.cdse.observation(b, grid)
        before, after = read_observation(before_data, grid), read_observation(after_data, grid)
        evidence = compare_pixels(before, after, grid)
        classification = {'state':'skipped','answers':{},'message':'Insufficient common clear coverage for reliable image classification.'}
        if evidence['state'] == 'observable':
            try:
                common = before['clear'] & after['clear']
                classification = self.classifier.classify(classification_image(before, common), classification_image(after, common), {
                    'before':before_source, 'after':after_source, 'spectral_metrics':evidence['metrics'],
                    'common_usable_fraction':evidence['common_usable_fraction'], 'area_m2':grid['area_m2']})
            except (DomainError, httpx.HTTPError):
                classification = {'state':'unavailable','answers':{},'message':'Image classification was unavailable. The measured imagery evidence is retained.'}
        interval = {'before':a['acquired_at'],'after':b['acquired_at'],'exact_event_date':None,'cause':'not_established'}
        if request.window_start:
            interval['query_window_relation'] = change_interval(a['acquired_at'], b['acquired_at'], request.window_start.isoformat(), request.window_end.isoformat())['relation']
        # No exact event time or cause is generated from image differences.
        return {'intent':request.intent.value,'evidence':evidence,'classification':classification,
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
