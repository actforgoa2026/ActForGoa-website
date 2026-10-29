"""Saved metadata retrieval: spatial/temporal correctness, no invented evidence."""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from satellite.app import create_app
from satellite.domain import Area, EvidenceRequest, HistoryRequest
from satellite.service import SatelliteService
from test_service import AREA, CATALOG, COMPARISON, HEADERS, TIMES, credentials


PARTIAL = {'bbox': [73.825, 15.48, 73.835, 15.49]}
OTHER = {'bbox': [73.9, 15.48, 73.91, 15.49]}
QUERY = {'area': AREA, 'start_date': '2025-10-01', 'end_date': '2025-10-28'}


def saved(service, *, area=AREA, actual=None, actor='editor-one', state='observable', question='Canopy near Ribandar',
          before=TIMES[0], after=TIMES[1], intent='canopy_loss', status='complete', created=None):
    request = {**COMPARISON, 'area': area, 'intent': intent, 'question': question}
    result = {
        'area': {'geometry': Area(**(actual or area)).grid()['wgs84_geometry']},
        'observation_interval': {'before': before, 'after': after},
        'summary': {'state': 'no_candidate_detected' if state == 'observable' else 'inconclusive',
                    'headline': 'No numeric candidates' if state == 'observable' else 'Insufficient clear imagery',
                    'statements': [{'text': 'Seasonal wetland visibility needs review.', 'sources': ['coverage']}]},
        'evidence': {'state': state, 'common_usable_fraction': 1 if state == 'observable' else .4,
                     'metrics': {'ndvi': {'before_median': .7, 'after_median': .68, 'median_paired_change': -.02, 'paired_pixels': 100}},
                     'candidates': {'type': 'FeatureCollection', 'features': []}, 'water_change': None},
        'classification': {'state': 'complete', 'provider': 'openai-decisions', 'model': 'fixture-not-a-live-call',
                           'answers': {'before_canopy': {'choice': 'yes'}, 'after_canopy': {'choice': 'uncertain'},
                                       'invented': {'choice': 'illegal'}, 'canopy_change': {'choice': 'illegal'}}},
        'canopy_presence': {'before': 'yes', 'after': 'uncertain', 'state': 'inconclusive'},
        'before': {'catalog_scene_id': 'before-fixture', 'acquired_at': [before], 'image': 'PRIVATE-IMAGE-MUST-NOT-ENTER-METADATA'},
        'after': {'catalog_scene_id': 'after-fixture', 'acquired_at': [after], 'image': 'PRIVATE-IMAGE-MUST-NOT-ENTER-METADATA'},
    }
    job = service.store.start(actor, request)
    service.store.finish(job, result, failed=status == 'failed')
    if status == 'running':
        service.store.db.execute("UPDATE jobs SET status='running' WHERE id=?", (job,))
    if created:
        service.store.db.execute('UPDATE jobs SET created=? WHERE id=?', (created, job))
    service.store.db.commit()
    return job


@pytest.fixture
def service(tmp_path):
    instance = SatelliteService(tmp_path/'jobs.sqlite', httpx.Client(transport=httpx.MockTransport(lambda request: pytest.fail('Saved evidence must not call a provider'))))
    yield instance
    instance.close()


def test_saved_query_is_actor_private_metadata_only_and_never_calls_provider(service, credentials):
    first = saved(service)
    saved(service, actor='someone-else')
    # Avoid TestClient lifespan closing this fixture's service twice.
    client = TestClient(create_app(service))
    assert client.post('/evidence', json=QUERY).status_code == 401
    assert client.post('/evidence', headers={'Authorization': HEADERS['Authorization']}, json=QUERY).status_code == 403
    response = client.post('/evidence', headers=HEADERS, json=QUERY)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['state'] == 'available'
    assert [card['id'] for card in data['cards']] == [first]
    assert 'PRIVATE-IMAGE' not in response.text
    assert service.store.db.execute('SELECT count(*) FROM quota').fetchone()[0] == 0
    assert data['cards'][0]['citation']['route'].endswith(first)
    assert data['cards'][0]['classification']['answers'] == {'before_canopy': {'choice': 'yes'}, 'after_canopy': {'choice': 'uncertain'}}
    assert data['cards'][0]['provenance']['before']['acquired_at'] == [TIMES[0]]


def test_spatial_filter_excludes_remote_unknown_and_stale_footprints(service):
    same = saved(service)
    partial = saved(service, area=PARTIAL)
    saved(service, area=OTHER)
    saved(service, area=AREA, actual=OTHER)
    unknown = service.store.start('editor-one')
    service.store.finish(unknown, {'observation_interval': {'before': TIMES[0], 'after': TIMES[1]}})
    result = service.evidence(EvidenceRequest(**QUERY), 'editor-one')
    assert {card['id'] for card in result['cards']} == {same, partial}
    assert result['cards'][0]['spatial']['relation'] == 'same_area'
    assert result['cards'][0]['spatial']['query_fraction'] == 1
    overlap = result['cards'][1]
    assert overlap['spatial']['relation'] == 'partial_overlap'
    assert .49 < overlap['spatial']['query_fraction'] < .51
    assert overlap['measurements']['metrics']['ndvi']['before_median'] == .7
    assert 'not recalculated' in overlap['measurements']['scope_note']
    assert any(gap['code'] == 'partial_area' for gap in result['gaps'])
    assert 'total_loss' not in result and 'total_area' not in result


def test_history_area_scope_uses_same_rules_and_paginates_after_spatial_filter(service):
    first, second = saved(service), saved(service, area=PARTIAL)
    saved(service, area=OTHER)
    saved(service, area=AREA, actual=OTHER)
    query = HistoryRequest(area=AREA, limit=1)
    page = service.store.history('editor-one', query)
    assert page['next_offset'] == 1
    next_page = service.store.history('editor-one', query.model_copy(update={'offset':1}))
    assert {page['items'][0]['id'], next_page['items'][0]['id']} == {first, second}
    assert next_page['next_offset'] is None
    assert 'spatial' in page['items'][0]
    # Findings search includes the saved statement text, not just the headline.
    assert len(service.store.history('editor-one', HistoryRequest(area=AREA, query='wetland'))['items']) == 2


def test_time_topic_status_and_retention_are_enforced_before_returning_evidence(service):
    within = saved(service, before='2025-10-15T05:00:00Z', after='2025-10-16T05:00:00Z')
    overlap = saved(service)
    saved(service, before='2025-09-01T05:00:00Z', after='2025-09-10T05:00:00Z')
    saved(service, intent='surface_water')
    saved(service, status='failed')
    saved(service, status='running')
    saved(service, created=(datetime.now(timezone.utc)-timedelta(days=31)).isoformat())
    query = EvidenceRequest(area=AREA, start_date='2025-10-14', end_date='2025-10-17', intent='canopy_loss')
    result = service.evidence(query, 'editor-one')
    assert [card['id'] for card in result['cards']] == [within, overlap]
    assert result['cards'][0]['temporal']['relation'] == 'within_window'
    assert result['cards'][1]['temporal']['relation'] == 'overlaps_window'
    assert any(gap['code'] == 'partial_period' for gap in result['gaps'])


def test_empty_unknown_and_inconclusive_are_never_rendered_as_no_change(service):
    empty = service.evidence(EvidenceRequest(**QUERY), 'editor-one')
    assert empty['state'] == 'no_matches'
    assert 'does not establish that nothing changed' in empty['headline']
    saved(service, state='insufficient_clear_coverage')
    cloudy = service.evidence(EvidenceRequest(**QUERY), 'editor-one')
    assert cloudy['state'] == 'available'
    assert cloudy['cards'][0]['canopy_presence']['after'] == 'uncertain'
    assert any(gap['code'] == 'insufficient_clear_coverage' for gap in cloudy['gaps'])


def test_meaningful_question_words_rank_only_after_location_and_time(service):
    irrelevant = saved(service, question='The area and observations')
    relevant = saved(service, question='Ribandar canopy question')
    partial = saved(service, area=PARTIAL, question='Ribandar canopy question')
    result = service.evidence(EvidenceRequest(**QUERY, question='What happened to Ribandar canopy in this area?'), 'editor-one')
    assert [card['id'] for card in result['cards']] == [relevant, irrelevant, partial]
    assert 'deterministic' in result['ranking']


def test_scan_and_card_bounds_report_truncation(service):
    template_id = saved(service)
    row = service.store.db.execute('SELECT actor,status,created,result,request FROM jobs WHERE id=?', (template_id,)).fetchone()
    with service.store.db:
        for number in range(301):
            service.store.db.execute('INSERT INTO jobs(id,actor,status,created,result,request) VALUES(?,?,?,?,?,?)', (f'fixture-{number:04}', *row))
    result = service.evidence(EvidenceRequest(**QUERY, limit=3), 'editor-one')
    assert result['scanned_count'] == 300
    assert result['scan_truncated'] and result['results_truncated']
    assert result['matched_count'] == 300 and len(result['cards']) == 3
    assert any(gap['code'] == 'scan_truncated' for gap in result['gaps'])
    assert service.store.history('editor-one', HistoryRequest(area=AREA))['scan_truncated'] is True


def test_validation_allows_saved_years_but_rejects_future_and_overflow_dates(service, credentials):
    client = TestClient(create_app(service))
    assert client.post('/evidence', headers=HEADERS, json={**QUERY, 'start_date':'2018-01-01'}).status_code == 200
    for change in [{'end_date':'9999-12-31'}, {'start_date':'2025-10-29'}, {'limit':9}, {'area':{'bbox':[0,0,.01,.01]}}]:
        assert client.post('/evidence', headers=HEADERS, json={**QUERY, **change}).status_code == 422
    assert client.post('/history', headers=HEADERS, json={'end_date':'9999-12-31'}).status_code == 422


def test_optional_context_is_explicit_separate_and_has_no_satellite_or_model_effect(service, monkeypatch):
    from satellite.amche import AmcheContext
    calls = []
    monkeypatch.setattr(AmcheContext, 'search', lambda self, grid: calls.append('amche') or {'state':'no_matches','message':'Reference data only'})
    monkeypatch.setattr(service.context, 'search', lambda question, intent: calls.append(('ecology', intent)) or {'state':'available','sources':[],'message':'Background only'})
    plain = service.evidence(EvidenceRequest(**QUERY), 'editor-one')
    assert not calls and 'amche_context' not in plain
    enriched = service.evidence(EvidenceRequest(**QUERY, include_context=True), 'editor-one')
    assert calls == ['amche', ('ecology', None)]
    assert enriched['state'] == 'no_matches'
    assert enriched['amche_context']['state'] == 'no_matches'
    assert enriched['library_context']['state'] == 'available'
    assert service.store.db.execute('SELECT count(*) FROM quota').fetchone()[0] == 0


def test_optional_context_exceptions_do_not_discard_saved_evidence(service, monkeypatch):
    from satellite.amche import AmcheContext
    job = saved(service)
    def fail(*args):
        raise RuntimeError('private upstream error details must not be exposed')
    monkeypatch.setattr(AmcheContext, 'search', fail)
    monkeypatch.setattr(service.context, 'search', fail)
    result = service.evidence(EvidenceRequest(**QUERY, include_context=True), 'editor-one')
    assert result['cards'][0]['id'] == job
    assert result['amche_context']['state'] == result['library_context']['state'] == 'unavailable'
    assert 'private upstream' not in json.dumps(result)


def test_saved_model_scores_are_validated_without_turning_them_into_accuracy(service):
    job = saved(service)
    result = json.loads(service.store.db.execute('SELECT result FROM jobs WHERE id=?', (job,)).fetchone()[0])
    result['classification']['answers']['before_canopy'] = {'choice':'yes','confidence':.8,
        'probabilities':[{'value':'yes','probability':.8},{'value':'no','probability':.1},{'value':'uncertain','probability':.1}]}
    result['classification']['answers']['after_canopy'] = {'choice':'uncertain','confidence':True,'probabilities':'broken'}
    service.store.finish(job, result)
    classification = service.evidence(EvidenceRequest(**QUERY), 'editor-one')['cards'][0]['classification']
    assert classification['answers']['before_canopy']['confidence'] == .8
    assert classification['answers']['before_canopy']['probabilities_complete'] is True
    assert classification['answers']['after_canopy'] == {'choice':'uncertain','score_validation':'invalid_saved_scores_omitted'}
    assert classification['calibration'] == 'not_calibrated'
    assert classification['confidence_threshold'] is None


def test_truncated_empty_scan_does_not_claim_entire_history_has_no_matches(service):
    from satellite.evidence_query import build_evidence
    result = build_evidence(EvidenceRequest(**QUERY), [], scan_truncated=True)
    assert result['state'] == 'no_matches'
    assert 'Older records were not checked' in result['headline']
    assert 'No retained saved comparisons match' not in result['headline']


def test_malformed_result_geometry_does_not_fall_back_to_request_area(service):
    job = saved(service)
    result = json.loads(service.store.db.execute('SELECT result FROM jobs WHERE id=?', (job,)).fetchone()[0])
    result['area'] = {'geometry':{'type':'Point','coordinates':[73.825,15.485]}}
    service.store.finish(job, result)
    assert service.evidence(EvidenceRequest(**QUERY), 'editor-one')['cards'] == []
    assert service.store.history('editor-one', HistoryRequest(area=AREA))['items'] == []
