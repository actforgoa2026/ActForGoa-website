"""Versioned public map records intersected with a private selected area.

Only the two fixed public source URLs below are fetched. The selected geometry,
question, account identity and provider credentials never leave this service.
Amche software licensing is separate from the publishers' dataset terms.
"""
from collections import Counter
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import threading
import time

import httpx
from shapely.errors import ShapelyError
from shapely.geometry import shape
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree

from .domain import TO_UTM


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    sha256: str
    maximum: int
    source_url: str
    source_label: str
    reference_date: str
    note: str


SOURCES = (
    Source('water-bodies', 'Water-body reference records',
           'https://gist.githubusercontent.com/planemad/e5ccc47bf2a1aa458a86d6839476f539/raw/6922fcc2d5ffd4d58b0fb069b9f57334f13cd953/goa-water-bodies.geojson',
           '55c34660d6ea7c820194072b83d54370b0037acfd4d687d95bc7a0551aac25fa', 12_000_000,
           'https://goawrd.gov.in/', 'Goa Water Resources Department, via Amche Atlas',
           'Water Body Atlas 2025',
           'Mapped reference records, not current water extent. Complete coverage and effective dates have not been established.'),
    Source('private-forests', 'Private-forest reference records',
           'https://gist.githubusercontent.com/planemad/54b84c11fc0325889f1127e49b5740db/raw/1f99740ddb55a1528d76a5364aa9a95c1fe800da/goa_private_forest_plots-jun-2026.geojson',
           '2212306378794a01daacc57bbc809788c1f35286d797ca1af85ed2d42b97355a', 3_000_000,
           'https://docs.google.com/spreadsheets/d/1OHrd9c61IQ2rE_pKqPrtMgT5AY5Wepru/edit?gid=378361244',
           'Goa private forest records, collected by the Amche community', 'June 2026 collection',
           'An incomplete collection with partial survey matches and unmatched location points. These records establish neither current canopy nor legal status.'),
)

_CACHE = {}
_CACHE_LOCK = threading.RLock()
_SUCCESS_TTL = 24 * 60 * 60
_FAILURE_TTL = 5 * 60
_FIELDS = ('name', 'village', 'taluka', 'survey', 'subdivision', 'subdiv', 'wb_id',
           'match_accuracy', 'match_notes', 'partial_plot_match')


def _text(value, maximum=160):
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return ''
    if isinstance(value, float) and not math.isfinite(value):
        return ''
    return ''.join(character for character in str(value) if character.isprintable())[:maximum].strip()


def _geometry(value, counter):
    if not isinstance(value, dict):
        raise ValueError('geometry')

    def position(point):
        counter[0] += 1
        if counter[0] > 500_000:
            raise OverflowError('vertex limit')
        if not isinstance(point, list) or not 2 <= len(point) <= 3:
            raise ValueError('position')
        if any(isinstance(number, bool) or not isinstance(number, (float, int)) or not math.isfinite(number) for number in point):
            raise ValueError('position')
        if not (73.5 <= point[0] <= 74.6 and 14.7 <= point[1] <= 16):
            raise ValueError('Goa bounds')
        return point[:2]

    def polygon(rings):
        if not isinstance(rings, list) or not rings:
            raise ValueError('polygon')
        output = []
        for ring in rings:
            if not isinstance(ring, list) or len(ring) < 4:
                raise ValueError('ring')
            points = [position(point) for point in ring]
            if points[0] != points[-1]:
                raise ValueError('open ring')
            output.append(points)
        return output

    kind, coordinates = value.get('type'), value.get('coordinates')
    if kind == 'Point':
        coordinates = position(coordinates)
    elif kind == 'Polygon':
        coordinates = polygon(coordinates)
    elif kind == 'MultiPolygon' and isinstance(coordinates, list) and coordinates:
        coordinates = [polygon(item) for item in coordinates]
    else:
        raise ValueError('geometry type')
    geometry = shape({'type': kind, 'coordinates': coordinates})
    if geometry.is_empty or not geometry.is_valid:
        raise ValueError('invalid geometry')
    projected = transform(TO_UTM, geometry)
    if projected.is_empty or not projected.is_valid or not all(math.isfinite(number) for number in projected.bounds):
        raise ValueError('invalid projected geometry')
    return projected


def _parse(raw, source):
    if hashlib.sha256(raw).hexdigest() != source.sha256:
        raise ValueError('source changed')
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get('type') != 'FeatureCollection':
        raise ValueError('collection')
    features = data.get('features')
    if not isinstance(features, list) or not features or len(features) > 5000:
        raise ValueError('feature limit')
    crs = data.get('crs')
    if crs is not None and (not isinstance(crs, dict) or crs.get('type') != 'name' or
            not isinstance(crs.get('properties'), dict) or crs['properties'].get('name') not in
            {'urn:ogc:def:crs:OGC:1.3:CRS84', 'EPSG:4326'}):
        raise ValueError('coordinate system')
    rows, excluded, counter, identifiers = [], 0, [0], Counter()
    for index, feature in enumerate(features):
        try:
            if not isinstance(feature, dict) or feature.get('type') != 'Feature':
                raise ValueError('feature')
            geometry = _geometry(feature.get('geometry'), counter)
            properties = feature.get('properties') or {}
            if not isinstance(properties, dict):
                raise ValueError('properties')
            safe = {key: _text(properties.get(key)) for key in _FIELDS}
            raw_id = _text(properties.get('id'), 100)
            if raw_id:
                identifiers[raw_id] += 1
            rows.append({'id': f'{source.id}:{source.sha256[:16]}:{index}',
                         'source_record_id': raw_id, 'properties': safe,
                         'geometry': geometry})
        except (ValueError, TypeError, KeyError, ShapelyError):
            # Do not silently repair a survey boundary. Quarantine it and retain
            # the excluded count so a zero-match answer cannot imply completeness.
            excluded += 1
    if not rows:
        raise ValueError('no valid records')
    return {'rows': rows, 'tree': STRtree([row['geometry'] for row in rows]),
            'record_count': len(features), 'valid_record_count': len(rows),
            'excluded_record_count': excluded,
            'duplicate_source_id_count': sum(count - 1 for count in identifiers.values() if count > 1),
            'fetched_at': datetime.now(timezone.utc).isoformat()}


class AmcheContext:
    def __init__(self, client, *, sources=None):
        self.http = client
        self.sources = SOURCES if sources is None else tuple(sources)

    def _snapshot(self, source):
        key = (source.id, source.url, source.sha256)
        cached = _CACHE.get(key)
        if cached and cached[0] > time.monotonic():
            return cached[1]
        # One shared fetch per pinned snapshot, including across service objects.
        # Healthy immutable cache entries remain usable while another source is
        # loading. Busy fetches return unknown promptly, without poisoning cache.
        if not _CACHE_LOCK.acquire(timeout=2):
            return None
        try:
            cached = _CACHE.get(key)
            if cached and cached[0] > time.monotonic():
                return cached[1]
            snapshot = None
            try:
                # A supplied client's default cookies/authorization must not be
                # forwarded to public sources. Construct independently of its
                # default query params too: only the exact fixed URL is fetched.
                request = httpx.Request('GET', source.url,
                    headers={'Accept': 'application/geo+json, application/json',
                             'User-Agent': 'ActForGoa-satellite-context/1'},
                    extensions={'timeout': httpx.Timeout(connect=5, read=8, write=5, pool=5).as_dict()})
                deadline = time.monotonic() + 12
                with closing(self.http.send(request, auth=None, stream=True, follow_redirects=False)) as response:
                    if response.status_code != 200:
                        raise ValueError('source unavailable')
                    if int(response.headers.get('content-length', '0')) > source.maximum:
                        raise ValueError('source too large')
                    chunks, size = [], 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > source.maximum or time.monotonic() > deadline:
                            raise ValueError('source too large')
                        chunks.append(chunk)
                snapshot = _parse(b''.join(chunks), source)
            except (httpx.HTTPError, ValueError, TypeError, KeyError, OverflowError, ShapelyError):
                # Provider response bodies and arbitrary error text never reach
                # the saved context result. Imagery remains usable on failure.
                snapshot = None
            _CACHE[key] = (time.monotonic() + (_SUCCESS_TTL if snapshot else _FAILURE_TTL), snapshot)
            return snapshot
        finally:
            _CACHE_LOCK.release()

    def search(self, area):
        try:
            return self._search(area)
        except ShapelyError:
            # Reference joins are optional background. A topology failure must
            # neither erase saved imagery evidence nor become a zero-hit claim.
            return {'state': 'unavailable',
                    'message': 'The reference geometry could not be checked. This does not establish whether mapped records overlap the selection.',
                    'checked_at': datetime.now(timezone.utc).isoformat(),
                    'coverage': 'not_established', 'matched_records': 0, 'layers': []}

    def _search(self, area):
        grid = area.grid() if hasattr(area, 'grid') else area
        query = transform(TO_UTM, shape(grid['wgs84_geometry']))
        if query.is_empty or not query.is_valid or not 0 < query.area <= 25_000_001:
            raise ValueError('Use a validated Goa selection of at most 25 square kilometres.')
        layers = []
        for source in self.sources:
            metadata = {'id': source.id, 'title': source.title, 'source_url': source.source_url,
                        'source_label': source.source_label, 'dataset_url': source.url,
                        'snapshot_sha256': source.sha256, 'reference_date': source.reference_date,
                        'effective_date': None, 'coverage': 'not_established', 'note': source.note}
            snapshot = self._snapshot(source)
            if snapshot is None:
                layers.append({**metadata, 'state': 'unavailable', 'match_state': 'unknown',
                               'fetched_at': None, 'matches': [], 'truncated': False})
                continue
            matches, overlaps = [], []
            polygon_count = point_count = boundary_count = 0
            for index in snapshot['tree'].query(query, predicate='intersects'):
                row = snapshot['rows'][int(index)]
                geometry, properties = row['geometry'], row['properties']
                if geometry.geom_type == 'Point':
                    relation, overlap_area, fraction = 'location_only', None, None
                    point_count += 1
                else:
                    intersection = geometry.intersection(query)
                    overlap_area = intersection.area
                    fraction = min(1, overlap_area / query.area)
                    if overlap_area > 0:
                        relation = 'area_overlap'
                        polygon_count += 1
                        overlaps.append(intersection)
                    else:
                        relation = 'boundary_touch'
                        boundary_count += 1
                name = properties['name']
                title = name if name and name not in {'--', 'N/A'} else properties['wb_id']
                if not title:
                    title = 'Survey ' + properties['survey'] if properties['survey'] else 'Mapped reference record'
                label = ' · '.join(filter(None, [title, properties['village'], properties['taluka']]))
                matches.append({'id': row['id'], 'source_record_id': row['source_record_id'],
                    'label': label[:480], 'village': properties['village'], 'taluka': properties['taluka'],
                    'survey': properties['survey'], 'subdivision': properties['subdivision'] or properties['subdiv'],
                    'geometry_type': geometry.geom_type, 'relation': relation,
                    'intersection_area_m2': round(overlap_area, 2) if overlap_area is not None else None,
                    'query_fraction': round(fraction, 6) if fraction is not None else None,
                    'match_accuracy': properties['match_accuracy'], 'partial_plot_match': properties['partial_plot_match']})
            # Union protects aggregate area from overlapping/duplicated records.
            union_area = unary_union(overlaps).area if overlaps else 0
            matches.sort(key=lambda match: (-(match['intersection_area_m2'] or 0), match['id']))
            layers.append({**metadata, 'state': 'available',
                'match_state': 'matches' if matches else 'no_matches',
                **{key: snapshot[key] for key in ('fetched_at', 'record_count', 'valid_record_count',
                    'excluded_record_count', 'duplicate_source_id_count')},
                'polygon_match_count': polygon_count, 'point_match_count': point_count,
                'boundary_touch_count': boundary_count, 'matched_records': len(matches),
                'union_overlap_m2': round(union_area, 2), 'query_fraction': round(min(1, union_area / query.area), 6),
                'matches': matches[:20], 'truncated': len(matches) > 20})
        available = [layer for layer in layers if layer['state'] == 'available']
        matched = sum(layer['matched_records'] for layer in available)
        if not layers:
            state = 'not_configured'
        elif not available:
            state = 'unavailable'
        elif len(available) != len(layers) or any(layer['excluded_record_count'] for layer in available):
            state = 'partial'
        else:
            state = 'available' if matched else 'no_matches'
        messages = {
            'not_configured': 'No map context sources are configured.',
            'unavailable': 'Map context sources could not be checked. This does not imply an absence of mapped records.',
            'no_matches': 'No valid records in these reference snapshots intersect the selection. Coverage is not complete or established.',
            'partial': 'Some map context is unavailable or has invalid geometry. The usable records below are background context.',
            'available': 'These mapped reference records intersect the selection. They are background context, not evidence of a recent change.',
        }
        return {'state': state, 'message': messages[state], 'checked_at': datetime.now(timezone.utc).isoformat(),
                'coverage': 'not_established', 'matched_records': matched, 'layers': layers,
                'temporal_note': 'Reference editions and retrieval dates do not establish when a record became effective or whether it applied during the selected imagery period.',
                'count_note': 'Counts describe source records, not a verified total of forests, water bodies or legal parcels. Point records have no mapped extent.'}

    context = search
