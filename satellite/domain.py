"""Validated queries, fixed map grids and conservative temporal claims."""
from datetime import date, datetime, timedelta, timezone
from enum import Enum
import json
import math
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pyproj import Transformer
from shapely.geometry import box, mapping, shape
from shapely.ops import transform

IST = ZoneInfo('Asia/Kolkata')
TO_UTM = Transformer.from_crs(4326, 32643, always_xy=True).transform
TO_WGS = Transformer.from_crs(32643, 4326, always_xy=True).transform
GOA = shape(json.loads((Path(__file__).parent / 'data/goa.geojson').read_text())['geometry'])


class DomainError(Exception):
    def __init__(self, code: str, message: str, status=400):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Intent(str, Enum):
    canopy_loss = 'canopy_loss'
    fire = 'fire'
    surface_water = 'surface_water'
    land_change = 'land_change'
    waste = 'waste'


class Area(StrictModel):
    bbox: tuple[float, float, float, float]

    @model_validator(mode='after')
    def valid(self):
        w, s, e, n = self.bbox
        if not all(math.isfinite(v) for v in self.bbox) or not (-180 <= w < e <= 180 and -90 <= s < n <= 90):
            raise ValueError('Use west, south, east, north coordinates in longitude/latitude order.')
        # Check before projection or intersection to bound work, including far-away input.
        if e - w > .06 or n - s > .06:
            raise ValueError('Select an area up to 5 km across for on-demand comparison.')
        clipped = box(*self.bbox).intersection(GOA)
        if clipped.is_empty or transform(TO_UTM, clipped).area < 900:
            raise ValueError('Select at least 900 square metres within Goa.')
        if transform(TO_UTM, box(*self.bbox)).area > 25_000_000:
            raise ValueError('Select at most 25 square kilometres.')
        return self

    def grid(self):
        polygon = box(*self.bbox).intersection(GOA)
        projected = transform(TO_UTM, polygon)
        x1, y1, x2, y2 = projected.bounds
        bounds = [math.floor(x1 / 10) * 10, math.floor(y1 / 10) * 10,
                  math.ceil(x2 / 10) * 10, math.ceil(y2 / 10) * 10]
        width, height = round((bounds[2]-bounds[0])/10), round((bounds[3]-bounds[1])/10)
        if max(width, height) > 700:
            raise DomainError('area_too_large', 'Select a more compact area.')
        return {'bounds': bounds, 'width': width, 'height': height, 'crs': 'EPSG:32643',
                'resolution_m': 10, 'geometry': mapping(projected), 'area_m2': projected.area,
                'wgs84_geometry': mapping(polygon), 'clipped_to_goa': not GOA.covers(box(*self.bbox))}


class AreaRequest(StrictModel):
    area: Area


class Query(StrictModel):
    question: str = Field(min_length=3, max_length=1000)
    area: Area | None = None


class Interpretation(StrictModel):
    intent: Intent
    scope: Literal['selected_area', 'named_place', 'goa', 'unsupported']
    place_name: str = Field(max_length=120)
    time_mode: Literal['relative_days', 'absolute_dates', 'unspecified']
    days: int = Field(ge=1, le=365)
    start_date: date | None
    end_date: date | None
    individual_tree: bool


class CatalogRequest(StrictModel):
    area: Area
    start_date: date
    end_date: date

    @model_validator(mode='after')
    def valid_dates(self):
        if not 0 <= (self.end_date-self.start_date).days <= 120:
            raise ValueError('Choose an ordered date range of up to 120 days.')
        if self.start_date < date(2017, 3, 28) or self.end_date > datetime.now(IST).date():
            raise ValueError('Choose available historical dates from 28 March 2017 onwards.')
        return self


class CompareRequest(CatalogRequest):
    before_id: str = Field(min_length=1, max_length=180, pattern=r'^[A-Za-z0-9_.-]+$')
    after_id: str = Field(min_length=1, max_length=180, pattern=r'^[A-Za-z0-9_.-]+$')
    intent: Intent
    question: str = Field(default='', max_length=1000)
    window_start: datetime | None = None
    window_end: datetime | None = None

    @model_validator(mode='after')
    def valid_window(self):
        if (self.window_start is None) != (self.window_end is None):
            raise ValueError('Provide both query window bounds.')
        if self.window_start is not None:
            if self.window_start.tzinfo is None or self.window_end.tzinfo is None or self.window_start >= self.window_end:
                raise ValueError('Provide ordered query dates with timezones.')
        return self


class ObservationRequest(CatalogRequest):
    scene_id: str = Field(min_length=1, max_length=180, pattern=r'^[A-Za-z0-9_.-]+$')


class HistoryRequest(StrictModel):
    area: Area | None = None
    query: str = Field(default='', max_length=300)
    intent: Intent | None = None
    start_date: date | None = None
    end_date: date | None = None
    offset: int = Field(default=0, ge=0, le=1000)
    limit: int = Field(default=20, ge=1, le=25)

    @model_validator(mode='after')
    def ordered(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError('Use an ordered observation period.')
        for value in (self.start_date, self.end_date):
            if value and not date(2017, 3, 28) <= value <= datetime.now(IST).date():
                raise ValueError('Choose available historical dates from 28 March 2017 through today.')
        return self


class EvidenceRequest(StrictModel):
    area: Area
    start_date: date
    end_date: date
    intent: Intent | None = None
    question: str = Field(default='', max_length=1000)
    limit: int = Field(default=8, ge=1, le=8)
    include_context: bool = False

    @model_validator(mode='after')
    def ordered(self):
        # Evidence search reads retained metadata, not an unbounded CDSE catalog.
        # It can cover distant acquisition dates without making provider calls.
        if not date(2017, 3, 28) <= self.start_date <= self.end_date <= datetime.now(IST).date():
            raise ValueError('Choose an ordered historical period from 28 March 2017 through today.')
        return self


def make_plan(query: Query, interpreted: Interpretation, now: datetime | None = None):
    now = (now or datetime.now(timezone.utc)).astimezone(IST)
    warnings = ['Sentinel-2 supports canopy patches, not a reliable count of individual trees.',
                'Image dates bound when a change became observable; they do not establish its cause.']
    if interpreted.scope == 'unsupported':
        return {'state': 'unsupported', 'message': 'Ask about canopy, fire evidence, visible water, waste sites or development within Goa.'}
    if interpreted.scope == 'goa':
        return {'state': 'statewide_not_ready', 'message': 'Goa-wide change indexing is not available yet. Select an area for an on-demand investigation.', 'warnings': warnings}
    if interpreted.scope == 'named_place' or query.area is None:
        return {'state': 'area_required', 'place_name': interpreted.place_name,
                'message': 'Locate this place on the map and select the area. Place names are not converted into guessed coordinates.'}
    if interpreted.time_mode == 'unspecified':
        return {'state': 'dates_required', 'message': 'Include a date range or a period such as “the last 10 days”.'}
    if interpreted.time_mode == 'relative_days':
        start, end = now - timedelta(days=interpreted.days), now
    else:
        if not interpreted.start_date or not interpreted.end_date:
            raise DomainError('invalid_plan', 'The query provider did not resolve the dates. Please specify them.')
        start = datetime.combine(interpreted.start_date, datetime.min.time(), IST)
        end = min(datetime.combine(interpreted.end_date + timedelta(days=1), datetime.min.time(), IST), now)
    if start >= end or end > now or (end-start).days > 90 or start.date() < date(2017, 3, 28):
        raise DomainError('invalid_dates', 'Use a past observation window of up to 90 days.')
    baseline_start = max(date(2017, 3, 28), (start - timedelta(days=30)).date())
    if interpreted.individual_tree:
        warnings.insert(0, 'This question concerns individual trees. The available resolution may be insufficient; canopy change is the supported observation.')
    return {'state': 'ready', 'intent': interpreted.intent.value, 'timezone': 'Asia/Kolkata',
            'window_start': start.isoformat(), 'window_end': end.isoformat(),
            'catalog_start': baseline_start.isoformat(), 'catalog_end': end.date().isoformat(),
            'area': query.area.model_dump(), 'warnings': warnings,
            'message': 'Find observations, then choose a before and after image. The baseline search includes 30 preceding days.'}


def change_interval(before: str, after: str, window_start: str, window_end: str):
    a, b, start, end = [datetime.fromisoformat(v.replace('Z', '+00:00')) for v in (before, after, window_start, window_end)]
    if any(v.tzinfo is None for v in (a, b, start, end)) or not a < b or not start < end:
        raise ValueError('Use ordered, timezone-aware observations and query bounds.')
    overlaps = a < end and b > start
    return {'last_observed_before': before, 'first_observed_after': after,
            'relation': 'within_window' if start <= a < b <= end else 'overlaps_window' if overlaps else 'outside_window',
            'exact_event_date': None, 'cause': 'not_established'}
