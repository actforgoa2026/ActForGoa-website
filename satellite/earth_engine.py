"""Read-only, exact-acquisition Sentinel-2 retrieval through Earth Engine.

Analysis uses exact acquisitions. A separate cloud-masked median supplies navigation
only. No exports or asset writes; credentials remain on the API service.
"""
from datetime import datetime, timedelta, timezone
import json
import os
import re
import threading
import time
from urllib.parse import urlparse
from .domain import DomainError

COLLECTION = 'COPERNICUS/S2_SR_HARMONIZED'
PREFIX = 'ee-'
SCOPE = 'https://www.googleapis.com/auth/earthengine.readonly'
BANDS = ['B4', 'B3', 'B2', 'B8', 'B11', 'B12', 'SCL']


class EarthEngine:
    def __init__(self, client):
        self.http = client
        self._initialized = False
        self._lock = threading.Lock()
        self._preview_lock = threading.Lock()
        self._previews = {}

    @staticmethod
    def configured():
        return bool(os.getenv('EARTH_ENGINE_PROJECT') and os.getenv('EARTH_ENGINE_CREDENTIALS_JSON'))

    def _ee(self):
        import ee
        from google.oauth2.credentials import Credentials
        with self._lock:
            if not self._initialized:
                if not self.configured():
                    raise DomainError('imagery_unavailable', 'Earth Engine is not connected yet.', 503)
                try:
                    info = json.loads(os.environ['EARTH_ENGINE_CREDENTIALS_JSON'])
                    info.setdefault('client_id', ee.oauth.CLIENT_ID)
                    info.setdefault('client_secret', ee.oauth.CLIENT_SECRET)
                    info['token_uri'] = ee.oauth.TOKEN_URI
                    credentials = Credentials.from_authorized_user_info(info, scopes=[SCOPE])
                    ee.Initialize(credentials=credentials, project=os.environ['EARTH_ENGINE_PROJECT'])
                    ee.data.setDeadline(45000)
                    self._initialized = True
                except Exception:
                    raise DomainError('imagery_authentication', 'Earth Engine could not authenticate. Reconnect its read-only credential on the server.', 502) from None
        return ee

    def preview(self, request, on_generate=None):
        """A dated navigation composite. Never used as an analysis observation."""
        from .domain import GOA
        from shapely.geometry import mapping
        key = (request.start_date.isoformat(), request.end_date.isoformat())
        with self._preview_lock:
            cached = self._previews.get(key)
            if cached and cached[0] > time.monotonic():
                return {**cached[1], 'cache_hit': True}
            if on_generate:
                on_generate()
            ee = self._ee()
            try:
                roi = ee.Geometry(mapping(GOA))
                images = (ee.ImageCollection(COLLECTION).filterBounds(roi)
                          .filterDate(key[0], (request.end_date + timedelta(days=1)).isoformat())
                          .sort('system:time_start', False).limit(160))
                metadata = ee.Dictionary({'count': images.size(),
                    'first': images.aggregate_min('system:time_start'),
                    'last': images.aggregate_max('system:time_start')}).getInfo()
                if not metadata['count']:
                    raise DomainError('no_imagery', 'Earth Engine has no Sentinel-2 imagery in this period. Choose another date range.', 404)
                def clear_pixels(image):
                    image = ee.Image(image)
                    scl = image.select('SCL')
                    return image.select(['B4', 'B3', 'B2']).updateMask(scl.gte(4).And(scl.lte(6)))
                composite = images.map(clear_pixels).median().clip(roi)
                descriptor = composite.getMapId({'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.25})
                tile_url = descriptor['tile_fetcher'].url_format
                parsed = urlparse(tile_url)
                if parsed.scheme != 'https' or parsed.hostname != 'earthengine.googleapis.com' or parsed.username or parsed.password:
                    raise ValueError('Unexpected tile destination')
                result = {'provider': 'earth-engine', 'collection': COLLECTION,
                    'tile_url': tile_url, 'start_date': key[0], 'end_date': key[1],
                    'first_acquired_at': datetime.fromtimestamp(metadata['first']/1000, timezone.utc).isoformat(),
                    'last_acquired_at': datetime.fromtimestamp(metadata['last']/1000, timezone.utc).isoformat(),
                    'scene_count': metadata['count'], 'method': 'cloud-masked median',
                    'scope': 'Goa navigation overview; not an exact acquisition or change measurement.',
                    'cache_hit': False}
                self._previews = {k:v for k,v in self._previews.items() if v[0] > time.monotonic()}
                if len(self._previews) >= 8:
                    self._previews.pop(next(iter(self._previews)))
                self._previews[key] = (time.monotonic()+2700, result)
                return result
            except DomainError:
                raise
            except Exception:
                raise DomainError('imagery_provider_error', 'The Earth Engine overview could not load. Retry or choose another period.', 502) from None

    @staticmethod
    def scene(feature, request):
        props = feature['properties']
        scene_id = props['scene_id']
        if not re.fullmatch(r'[0-9]{8}T[0-9]{6}_[0-9]{8}T[0-9]{6}_T[A-Z0-9]{5}', scene_id):
            raise ValueError('Unexpected scene identifier')
        acquired = datetime.fromtimestamp(props['system:time_start'] / 1000, timezone.utc)
        if not request.start_date <= acquired.date() <= request.end_date:
            raise ValueError('Acquisition outside request')
        return {'id': PREFIX + scene_id, 'acquired_at': acquired.isoformat(),
                'scene_cloud_percent': props.get('CLOUDY_PIXEL_PERCENTAGE'),
                'geometry': feature['geometry'], 'collection': COLLECTION, 'provider': 'earth-engine'}

    def catalog(self, request):
        ee = self._ee()
        try:
            roi = ee.Geometry(request.area.grid()['wgs84_geometry'])
            images = (ee.ImageCollection(COLLECTION).filterBounds(roi)
                      .filterDate(request.start_date.isoformat(), (request.end_date + timedelta(days=1)).isoformat())
                      .sort('system:time_start').limit(301))
            # Keep metadata bounded; no image pixels or broad asset listings here.
            rows = ee.FeatureCollection(images.toList(301).map(lambda item: ee.Feature(
                ee.Image(item).geometry(), ee.Image(item).toDictionary(
                    ['system:time_start', 'CLOUDY_PIXEL_PERCENTAGE']).set('scene_id', ee.Image(item).get('system:index'))))).getInfo()['features']
            scenes = sorted([self.scene(row, request) for row in rows[:300]], key=lambda s: (s['acquired_at'], s['id']))
        except Exception:
            raise DomainError('imagery_provider_error', 'Earth Engine could not list verified acquisitions. Try again shortly.', 502) from None
        return {'state': 'available' if scenes else 'no_imagery', 'scenes': scenes,
                'provider': 'earth-engine', 'collection': COLLECTION,
                'searched_at': datetime.now(timezone.utc).isoformat(),
                'latest_acquired_at': scenes[-1]['acquired_at'] if scenes else None,
                'search_start': request.start_date.isoformat(), 'search_end': request.end_date.isoformat(),
                'truncated': len(rows) > 300,
                'cloud_note': 'Catalog cloud percentage describes the whole scene, not your selected area.'}

    def observation(self, scene, grid):
        ee = self._ee()
        if not scene['id'].startswith(PREFIX) or scene.get('collection') != COLLECTION:
            raise DomainError('invalid_provenance', 'Choose an Earth Engine acquisition from the current search.', 502)
        asset = COLLECTION + '/' + scene['id'][len(PREFIX):]
        try:
            source = ee.Image(asset)
            timestamp = source.get('system:time_start').getInfo()
            acquired = datetime.fromtimestamp(timestamp / 1000, timezone.utc).isoformat()
            if acquired != scene['acquired_at']:
                raise ValueError('Acquisition changed')
            selected = source.select(BANDS)
            # Reflectance scale 0.0001. SCL stays categorical; default nearest
            # neighbour resampling preserves its native 20 m classifications.
            valid = selected.mask().reduce(ee.Reducer.min()).rename('dataMask')
            image = (source.select(BANDS[:6]).multiply(0.0001)
                     .addBands(source.select('SCL')).addBands(valid)
                     .clip(ee.Geometry(grid['wgs84_geometry'])).unmask(0, False).toFloat())
            url = image.getDownloadURL({'format': 'GEO_TIFF', 'filePerBand': False,
                'crs': grid['crs'], 'crs_transform': [10, 0, grid['bounds'][0], 0, -10, grid['bounds'][3]],
                'dimensions': [grid['width'], grid['height']]})
            parsed = urlparse(url)
            if parsed.scheme != 'https' or parsed.hostname != 'earthengine.googleapis.com' or parsed.username or parsed.password:
                raise ValueError('Unexpected download destination')
        except Exception:
            raise DomainError('imagery_provider_error', 'Earth Engine could not prepare this exact acquisition. No substitute image was used.', 502) from None
        chunks, size = [], 0
        with self.http.stream('GET', url) as response:
            if response.status_code != 200:
                raise DomainError('imagery_provider_error', 'Earth Engine could not retrieve the selected pixels.', 502)
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > 16_000_000:
                    raise DomainError('imagery_too_large', 'Select a smaller area for this observation.', 502)
                chunks.append(chunk)
        return b''.join(chunks), {'provider': 'earth-engine', 'catalog_scene_id': scene['id'],
            'catalog_acquired_at': acquired, 'acquired_at': [acquired], 'earth_engine_asset': asset,
            'collection': COLLECTION, 'preset': 'true_color', 'display_resolution_m': 10,
            'swir_and_scene_classification_native_resolution_m': 20,
            'retrieved_at': datetime.now(timezone.utc).isoformat()}
