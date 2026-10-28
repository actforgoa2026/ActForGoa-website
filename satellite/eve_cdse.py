"""EVE-derived Sentinel-2 retrieval, hardened for hosted monitoring.

Modified from EVE helper.py at a49119dedcb7e929b69b7d78912dd52665c871fc.
See vendor/NOTICE.md and EVE-LICENSE. No exposed filesystem paths or evalscripts.
"""
from datetime import datetime, timedelta, timezone
import io
import json
import os
import tarfile
import threading
import time
import httpx
from .domain import CatalogRequest, DomainError

TOKEN_URL = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
CATALOG_URL = 'https://sh.dataspace.copernicus.eu/catalog/v1/search'
PROCESS_URL = 'https://sh.dataspace.copernicus.eu/process/v1'
EVALSCRIPT = '''//VERSION=3
function setup() {
  return {input:[{bands:["B04","B03","B02","B08","B11","B12","SCL","dataMask"]}],
          output:{id:"spectral",bands:8,sampleType:"FLOAT32"},mosaicking:"TILE"};
}
function evaluatePixel(samples) {
  if (!samples.length) return [0,0,0,0,0,0,0,0];
  let s=samples[0];
  return [s.B04,s.B03,s.B02,s.B08,s.B11,s.B12,s.SCL,s.dataMask];
}
function updateOutputMetadata(scenes,inputMetadata,outputMetadata) {
  outputMetadata.userData={tiles:scenes.tiles};
}
'''


class CDSE:
    def __init__(self, client: httpx.Client):
        self.http = client
        self._token = ''
        self._expiry = 0
        self._lock = threading.Lock()

    def token(self):
        with self._lock:
            if self._token and time.monotonic() < self._expiry:
                return self._token
            client_id, secret = os.getenv('CDSE_CLIENT_ID'), os.getenv('CDSE_CLIENT_SECRET')
            if not client_id or not secret:
                raise DomainError('imagery_unavailable', 'Copernicus credentials are not configured yet.', 503)
            r = self.http.post(TOKEN_URL, data={'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': secret})
            if r.status_code != 200:
                raise DomainError('imagery_authentication', 'Copernicus authentication failed. Check the server OAuth client and expiry.', 502)
            try:
                d = r.json()
                if not isinstance(d['access_token'], str) or not 60 <= float(d['expires_in']) <= 86400:
                    raise ValueError()
                self._token = d['access_token']
                self._expiry = time.monotonic() + float(d['expires_in']) - 30
                return self._token
            except (KeyError, TypeError, ValueError):
                raise DomainError('imagery_authentication', 'Copernicus returned an invalid token response.', 502) from None

    def post(self, url, payload, limit=16_000_000):
        # No redirect following: provider tokens cannot be sent to caller-selected hosts.
        headers = {'Authorization': 'Bearer ' + self.token()}
        # Multiple output responses alone do not select the bundle: without this
        # Accept header Process can return only the TIFF, omitting provenance.
        if url == PROCESS_URL:
            headers['Accept'] = 'application/tar'
        with self.http.stream('POST', url, headers=headers, json=payload) as r:
            if r.status_code != 200:
                if r.status_code == 401:
                    self._expiry = 0
                raise DomainError('imagery_provider_error', f'Copernicus could not complete the request (HTTP {r.status_code}).', 502)
            chunks, size = [], 0
            for chunk in r.iter_bytes():
                size += len(chunk)
                if size > limit:
                    raise DomainError('imagery_too_large', 'The imagery response exceeds the allowed size. Select a smaller area.', 502)
                chunks.append(chunk)
            return b''.join(chunks)

    def catalog(self, request: CatalogRequest):
        data = {'intersects': request.area.grid()['wgs84_geometry'],
                'datetime': f'{request.start_date}T00:00:00Z/{request.end_date}T23:59:59Z',
                'collections': ['sentinel-2-l2a'], 'limit': 100}
        scenes, seen = [], set()
        truncated = False
        # Explicit bounded pagination. A partial catalog is never described as complete.
        for _ in range(3):
            page = json.loads(self.post(CATALOG_URL, data, 4_000_000))
            for f in page.get('features', []):
                p = f['properties']
                acquisition = datetime.fromisoformat(p['datetime'].replace('Z', '+00:00'))
                if acquisition.tzinfo is None or not request.start_date <= acquisition.date() <= request.end_date:
                    raise DomainError('invalid_provenance', 'The catalog returned an acquisition outside the requested range.', 502)
                if f['id'] in seen:
                    continue
                seen.add(f['id'])
                scenes.append({'id': f['id'], 'acquired_at': p['datetime'],
                               'scene_cloud_percent': p.get('eo:cloud_cover'), 'geometry': f['geometry'],
                               'collection': 'sentinel-2-l2a'})
            next_page = page.get('context', {}).get('next')
            if next_page is None:
                break
            data['next'] = next_page
        else:
            truncated = True
        ordered=sorted(scenes, key=lambda s: (s['acquired_at'], s['id']))
        return {'state': 'available' if scenes else 'no_imagery', 'scenes': ordered,
                'searched_at':datetime.now(timezone.utc).isoformat(),
                'latest_acquired_at':ordered[-1]['acquired_at'] if ordered else None,
                'search_start':request.start_date.isoformat(),'search_end':request.end_date.isoformat(),
                'truncated': truncated, 'cloud_note': 'Catalog cloud percentage describes the whole scene, not your selected area.'}

    def observation(self, scene, grid):
        acquired = datetime.fromisoformat(scene['acquired_at'].replace('Z', '+00:00'))
        # No least-cloudy multi-day mosaic. Only the selected acquisition instant.
        start, end = acquired-timedelta(seconds=1), acquired+timedelta(seconds=1)
        body = {'input': {'bounds': {'geometry': grid['geometry'], 'bbox': grid['bounds'],
                                     'properties': {'crs': 'http://www.opengis.net/def/crs/EPSG/0/32643'}},
                          'data': [{'type': 'sentinel-2-l2a', 'dataFilter': {'timeRange': {'from': start.isoformat(), 'to': end.isoformat()},
                                      'mosaickingOrder': 'mostRecent'}, 'processing': {'harmonizeValues': True, 'upsampling': 'NEAREST', 'downsampling': 'NEAREST'}}]},
                'output': {'width': grid['width'], 'height': grid['height'], 'responses': [
                    {'identifier': 'spectral', 'format': {'type': 'image/tiff'}},
                    {'identifier': 'userdata', 'format': {'type': 'application/json'}}]}, 'evalscript': EVALSCRIPT}
        data = self.post(PROCESS_URL, body)
        try:
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                allowed = {m.name: m for m in archive.getmembers() if m.isfile() and m.name in {'spectral.tif', 'userdata.json'}}
                if set(allowed) != {'spectral.tif', 'userdata.json'} or any(m.size > 16_000_000 for m in allowed.values()):
                    raise ValueError()
                spectral = archive.extractfile(allowed['spectral.tif']).read()
                metadata = json.load(archive.extractfile(allowed['userdata.json']))
            tiles = metadata['tiles']
            if not tiles or len(tiles) > 8:
                raise ValueError()
            for tile in tiles:
                t = datetime.fromisoformat(tile['date'].replace('Z', '+00:00'))
                if t.tzinfo is None or not start <= t <= end or not (tile.get('dataPath') or tile.get('shId')):
                    raise ValueError()
            provenance = {'catalog_scene_id': scene['id'], 'catalog_acquired_at': scene['acquired_at'],
                          'acquired_at': sorted({t['date'] for t in tiles}),
                          'process_tiles': [{k: t[k] for k in ('date', 'shId', 'dataPath') if k in t} for t in tiles],
                          'collection': 'sentinel-2-l2a', 'preset': 'true_color', 'display_resolution_m': 10,
                          'swir_and_scene_classification_native_resolution_m': 20,
                          'retrieved_at': datetime.now(timezone.utc).isoformat()}
            return spectral, provenance
        except (tarfile.TarError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            raise DomainError('invalid_provenance', 'The image acquisition could not be verified against the selected observation. Comparison stopped.', 502) from None
