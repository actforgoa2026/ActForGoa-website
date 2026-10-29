"""Bounded, deterministic retrieval of saved evidence; this is not AI inference.

Cards preserve the original comparison footprint and actual acquisition interval.
Partial intersections never turn whole-comparison metrics into local measurements.
"""
from datetime import datetime, time, timedelta
import math
import re

from shapely.geometry import shape
from shapely.ops import transform
from shapely.errors import ShapelyError

from .domain import Area, IST, TO_UTM
from .providers import QUESTIONS, choice_evidence

STOPWORDS = set('a an and are as at be been between by can did do does for from had has have here how i in is it its me of on or our please show since than that the their there these they this those through to was we were what when where which who why will with you your'.split())


def _polygon(raw):
    if not isinstance(raw, dict) or raw.get('type') not in {'Polygon', 'MultiPolygon'}:
        return None
    try:
        polygon = shape(raw)
        if polygon.is_empty or not polygon.is_valid or not all(math.isfinite(v) for v in polygon.bounds):
            return None
        west, south, east, north = polygon.bounds
        if not (73.5 <= west < east <= 74.6 and 14.7 <= south < north <= 16):
            return None
        return transform(TO_UTM, polygon)
    except (ValueError, TypeError, KeyError, ShapelyError):
        return None


def comparison_geometry(request, result_area):
    """A malformed/stale result footprint must not fall back to another ROI."""
    requested = None
    if isinstance(request, dict) and request.get('area') is not None:
        try:
            requested = shape(Area.model_validate(request['area']).grid()['geometry'])
        except (ValueError, TypeError, ShapelyError):
            return None
    actual = None
    if result_area is not None:
        if not isinstance(result_area, dict) or (actual := _polygon(result_area.get('geometry'))) is None:
            return None
    if actual is not None and requested is not None:
        if actual.symmetric_difference(requested).area > max(1, requested.area * 1e-6):
            return None
    return actual if actual is not None else requested


def spatial_match(query_geometry, request, result_area):
    polygon = comparison_geometry(request, result_area)
    if polygon is None:
        return None
    intersection = polygon.intersection(query_geometry).area
    if intersection <= 0:
        return None
    same = polygon.symmetric_difference(query_geometry).area <= max(1, query_geometry.area * 1e-6)
    return {'relation': 'same_area' if same else 'partial_overlap',
            'query_fraction': round(min(1, intersection/query_geometry.area), 6),
            'comparison_fraction': round(min(1, intersection/polygon.area), 6),
            'intersection_area_m2': round(intersection, 2)}


def _temporal(interval, query):
    try:
        before, after = (datetime.fromisoformat(interval[key].replace('Z', '+00:00')) for key in ('before', 'after'))
        if before.tzinfo is None or after.tzinfo is None or before >= after:
            return None
    except (ValueError, TypeError, KeyError, AttributeError):
        return None
    start = datetime.combine(query.start_date, time.min, IST)
    end = datetime.combine(query.end_date + timedelta(days=1), time.min, IST)
    if before >= end or after < start:
        return None
    seconds = max(0, (min(after, end)-max(before, start)).total_seconds())
    fraction = seconds / (after-before).total_seconds()
    return {'relation': 'within_window' if start <= before < after < end else 'overlaps_window',
            'before': interval['before'], 'after': interval['after'], 'interval_fraction': round(fraction, 6)}


def _tokens(text):
    return {word for word in re.findall(r'[^\W_]+', text.lower()) if len(word) > 2 and word not in STOPWORDS}


def _finite(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None


def build_evidence(query, rows, scan_truncated=False):
    selected = shape(query.area.grid()['geometry'])
    tokens = _tokens(query.question)
    matches = []
    for row in rows:
        spatial = spatial_match(selected, row.get('request'), row.get('area'))
        temporal = _temporal(row.get('observation_interval'), query)
        if spatial is None or temporal is None:
            continue
        request = row.get('request') if isinstance(row.get('request'), dict) else {}
        summary = row.get('summary') if isinstance(row.get('summary'), dict) else None
        statements = (summary or {}).get('statements', [])
        if not isinstance(statements, list):
            statements = []
        text = ' '.join(value for value in [request.get('question', ''), (summary or {}).get('headline', ''),
                         *[value.get('text', '') for value in statements if isinstance(value, dict)]] if isinstance(value, str))
        lexical = len(tokens & _tokens(text))
        raw_answers = row.get('classification.answers') or {}
        if not isinstance(raw_answers, dict): raw_answers = {}
        answers = {}
        for name, value in raw_answers.items():
            if name not in QUESTIONS or not isinstance(value, dict) or value.get('choice') not in QUESTIONS[name][1]:
                continue
            try:
                answers[name] = choice_evidence(value, QUESTIONS[name][1])
            except (ValueError, TypeError, KeyError, AttributeError):
                # Older records can lack valid optional score fields. Retain
                # the checked choice, never invent or silently repair scores.
                answers[name] = {'choice':value['choice'], 'score_validation':'invalid_saved_scores_omitted'}
            if value.get('reason') == 'provider_refused':
                answers[name]['reason'] = 'provider_refused'
        raw_metrics = row.get('evidence.metrics') or {}
        if not isinstance(raw_metrics, dict): raw_metrics = {}
        metrics = {name: {key: _finite(value.get(key)) for key in ('before_median', 'after_median', 'median_paired_change', 'paired_pixels')}
                   for name, value in raw_metrics.items() if name in {'ndvi', 'ndwi', 'nbr'} and isinstance(value, dict)}
        card = {'id': row['id'], 'created_at': row['created_at'], 'intent': request.get('intent'),
                'question': request.get('question', ''), 'spatial': spatial, 'temporal': temporal,
                'clarity': {'state': row.get('evidence.state') or 'unknown',
                            'common_usable_fraction': _finite(row.get('evidence.common_usable_fraction'))},
                'classification': {'state': row.get('classification.state') or 'unknown',
                                   'provider': row.get('classification.provider'), 'model': row.get('classification.model'),
                                   'answers': answers, 'scope':row.get('classification.scope'),
                                   'calibration':'not_calibrated','confidence_threshold':None},
                'provenance': {which:{'catalog_scene_id':row.get(which+'.catalog_scene_id'),
                                     'acquired_at':row.get(which+'.acquired_at')} for which in ('before','after')},
                'canopy_presence': row.get('canopy_presence'), 'summary': summary,
                'measurements': {'metrics': metrics, 'vegetation_candidate_count': row.get('vegetation_candidate_count'),
                    'candidates_truncated': bool(row.get('evidence.candidates_truncated')),
                    'water_change': row.get('evidence.water_change'),
                    'scope_note': 'Measurements describe the original comparison footprint and common usable pixels. They are not recalculated for the selected overlap and must not be summed across comparisons.'},
                'citation': {'job_id': row['id'], 'route': '/api/admin/satellite/jobs/' + row['id'],
                             'label': 'Saved comparison ' + row['id'][:8]}}
        rank = (spatial['relation'] == 'same_area', spatial['query_fraction'], spatial['comparison_fraction'],
                temporal['relation'] == 'within_window', temporal['interval_fraction'], lexical, row['created_at'], row['id'])
        matches.append((rank, card))
    matches.sort(key=lambda item: item[0], reverse=True)
    cards = [card for _, card in matches[:query.limit]]
    gaps = [{'code': 'saved_scope', 'message': 'This search covers only your retained completed comparisons. It is not a fresh satellite search or continuous monitoring.'},
            {'code': 'coverage_unknown', 'message': 'No continuous coverage or last-clear/first-missing event date is established. Missing records and unobserved periods do not mean no change.'}]
    if not matches:
        headline = ('No matches were found among the newest 300 eligible saved comparisons. Older records were not checked.' if scan_truncated else
                    'No retained saved comparisons match this area, period and topic. This does not establish that nothing changed.')
        gaps.append({'code': 'no_saved_evidence', 'message': 'Select acquisitions and run a comparison to collect evidence for this area.'})
    else:
        headline = ('At least ' if scan_truncated else '')+f'{len(matches)} saved comparison'+('s match' if len(matches) != 1 else ' matches')+' this area and period. Review each footprint, acquisition date and visibility before drawing a conclusion.'
    if any(card['spatial']['relation'] == 'partial_overlap' for card in cards):
        gaps.append({'code': 'partial_area', 'message': 'Some comparisons only overlap this selection. Their measurements and conclusions apply to the original footprint, not specifically to the overlap.'})
    if any(card['temporal']['relation'] != 'within_window' for card in cards):
        gaps.append({'code': 'partial_period', 'message': 'Some observation intervals extend outside your period. A possible change could have happened outside the requested dates.'})
    if cards and all(card['clarity']['state'] != 'observable' for card in cards):
        gaps.append({'code': 'insufficient_clear_coverage', 'message': 'None of the returned comparisons establishes sufficient common clear coverage. These records cannot establish absence of change.'})
    if scan_truncated:
        gaps.append({'code': 'scan_truncated', 'message': 'Only the newest 300 eligible records were scanned. Narrow the period or topic; the result may omit other matches.'})
    return {'state': 'available' if cards else 'no_matches', 'query': query.model_dump(mode='json'),
            'headline': headline, 'cards': cards, 'gaps': gaps, 'scanned_count': len(rows), 'matched_count': len(matches),
            'scan_truncated': scan_truncated, 'results_truncated': len(matches) > query.limit,
            'retention_days': 30, 'method': 'saved-evidence-v1',
            'ranking': 'Spatial relationship, temporal overlap, shared question/finding words, then recency; deterministic retrieval, not an AI answer.'}
