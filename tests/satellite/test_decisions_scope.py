"""Offline contract checks, NOT satellite accuracy or field validation.

The two hardcoded 2x2 PNGs below are synthetic colours with one grey mask pixel.
They have no real location, acquisition or tree labels. Provider responses are
scripted. These tests verify evidence boundaries, not whether a model sees trees.

Contract checked against https://developers.openai.com/api/docs/guides/decisions
and https://developers.openai.com/api/reference/resources/decisions/methods/create
on 2026-10-29. No provider request leaves httpx.MockTransport.
"""
import base64
import hashlib
import io
import json

import httpx
from PIL import Image
import pytest

from satellite.domain import DomainError
from satellite.providers import DecisionsClassifier, QUESTIONS
from satellite.summary import canopy_presence, summarize_comparison


SYNTHETIC_BEFORE = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGNoaGjgidBg5InQYGBgAAAZhQKaoYhIPgAAAABJRU5ErkJggg==')
SYNTHETIC_AFTER = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGNsaGhgerCFienBFgYGBgAm+gSwjZMaVgAAAABJRU5ErkJggg==')
TARGET = {'id': 'area-synthetic-contract-only', 'area_m2': 900,
          'crs': 'EPSG:32643', 'geometry_crs': 'EPSG:4326',
          'bounds': [373000, 1712000, 373030, 1712030],
          'grid_resolution_m': 10, 'native_swir_scl_resolution_m': 20,
          'granularity': 'area_canopy'}
INTERVAL = {'before': '2025-10-10T05:00:00Z', 'after': '2025-10-20T05:00:00Z'}


def scripted_response(**updates):
    answers = {name: {'name': name, 'type': 'choice', 'choice': 'uncertain'} for name in QUESTIONS}
    for name, fields in updates.items():
        answers[name].update(fields)
    return {'model': 'gpt-6-luna', 'answers': list(answers.values()),
            'usage': {'input_tokens': 123, 'output_tokens': 0}}


def classify(monkeypatch, body, evidence=None):
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-never-live')
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, content=json.dumps(body), headers={'Content-Type': 'application/json'})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = DecisionsClassifier(client).classify(SYNTHETIC_BEFORE, SYNTHETIC_AFTER, evidence or {})
    assert len(requests) == 1
    return result, requests[0]


def measured(count=0, coverage=1):
    return {'state': 'observable' if coverage >= .8 else 'insufficient_clear_coverage',
            'common_usable_fraction': coverage,
            'candidates': {'features': [{'properties': {'area_m2': 900}} for _ in range(count)]}}


def model_choices(before='uncertain', after='uncertain', change='uncertain'):
    return {'state': 'complete', 'scope': {'target_id': TARGET['id']}, 'answers': {
        'before_canopy': {'choice': before}, 'after_canopy': {'choice': after},
        'canopy_change': {'choice': change}}}


def test_selected_footprint_and_exact_synthetic_inputs_are_bound_to_proposal(monkeypatch):
    evidence = {'target': TARGET, 'common_usable_fraction': .9}
    result, request = classify(monkeypatch, scripted_response(), evidence)
    body = json.loads(request.content)
    assert str(request.url) == 'https://api.openai.com/v1/decisions'
    assert body['model'] == 'gpt-6-luna'
    assert set(q['name'] for q in body['questions']) == set(QUESTIONS)
    content = body['input'][0]['content']
    assert body['input'][0]['role'] == 'user'
    images = [part for part in content if part['type'] == 'input_image']
    for part, fixture in zip(images, (SYNTHETIC_BEFORE, SYNTHETIC_AFTER), strict=True):
        assert part['detail'] == 'original'
        assert base64.b64decode(part['image_url'].split(',', 1)[1]) == fixture
        image = Image.open(io.BytesIO(fixture))
        assert image.size == (2, 2) and image.getpixel((0, 0)) == (128, 128, 128)
    payload = next(part['data'] for part in content if part['type'] == 'input_json')
    assert payload['target'] == TARGET and 'assessment_scope' not in evidence
    scope = result['scope']
    assert payload['assessment_scope'] == scope
    assert scope['target_id'] == TARGET['id'] and scope['area_m2'] == 900
    assert scope['grid_resolution_m'] == 10 and scope['native_swir_scl_resolution_m'] == 20
    assert scope['common_usable_fraction'] == .9 and scope['individual_tree_identity'] is False
    assert scope['before_png_sha256'] == hashlib.sha256(SYNTHETIC_BEFORE).hexdigest()
    assert scope['after_png_sha256'] == hashlib.sha256(SYNTHETIC_AFTER).hexdigest()
    assert 'synthetic-never-live' not in json.dumps(result)


def test_missing_target_is_explicit_and_cannot_invent_a_patch_identifier(monkeypatch):
    result, _ = classify(monkeypatch, scripted_response())
    assert result['scope']['target_id'] is None
    assert result['scope']['area_m2'] is None
    assert result['scope']['individual_tree_identity'] is False


def test_provider_distribution_is_retained_without_an_invented_accuracy_cutoff(monkeypatch):
    distribution = [{'value': 'yes', 'probability': .34}, {'value': 'no', 'probability': .33},
                    {'value': 'uncertain', 'probability': .33}]
    result, _ = classify(monkeypatch, scripted_response(before_canopy={
        'choice': 'yes', 'confidence': .01, 'probabilities': distribution}))
    answer = result['answers']['before_canopy']
    assert answer == {'choice': 'yes', 'confidence': .01, 'probabilities': distribution, 'probabilities_complete': True}
    assert result['calibration'] == 'not_calibrated' and result['confidence_threshold'] is None
    assert 'not verified facts' in result['validation']
    assert 'not validated accuracy' in result['validation']


def test_partial_scores_remain_partial_and_missing_scores_are_not_fabricated(monkeypatch):
    result, _ = classify(monkeypatch, scripted_response(before_canopy={
        'probabilities': [{'value': 'uncertain', 'probability': .7}]}))
    assert result['answers']['before_canopy']['probabilities_complete'] is False
    assert result['answers']['before_canopy']['probabilities'] == [{'value': 'uncertain', 'probability': .7}]
    assert result['answers']['after_canopy'] == {'choice': 'uncertain'}


@pytest.mark.parametrize('fields', [
    {'confidence': True}, {'confidence': float('nan')}, {'confidence': 1.1}, {'confidence': 10**400},
    {'probabilities': None}, {'probabilities': [{'value': 'yes', 'probability': -.1}]},
    {'probabilities': [{'value': 'yes', 'probability': float('inf')}]},
    {'probabilities': [{'value': 'yes', 'probability': 10**400}]},
    {'probabilities': [{'value': True, 'probability': .4}]},
    {'probabilities': [{'value': 'invented', 'probability': .4}]},
    {'probabilities': [{'value': 'yes', 'probability': .4}, {'value': 'yes', 'probability': .6}]},
    {'probabilities': [{'value': 'yes', 'probability': .8}, {'value': 'no', 'probability': .8}]},
    {'probabilities': [{'value': value, 'probability': .1} for value in ('yes', 'no', 'uncertain')]},
])
def test_malformed_optional_scores_fail_closed(monkeypatch, fields):
    with pytest.raises(DomainError) as error:
        classify(monkeypatch, scripted_response(before_canopy=fields))
    assert error.value.code == 'invalid_classification'


def test_refusal_and_uncertainty_never_become_canopy_absence(monkeypatch):
    result, _ = classify(monkeypatch, scripted_response(
        before_canopy={'type': 'refusal'}, after_canopy={'choice': 'uncertain', 'confidence': .99}))
    assert result['answers']['before_canopy'] == {'choice': 'uncertain', 'reason': 'provider_refused'}
    presence = canopy_presence(measured(), result)
    assert presence['before'] == presence['after'] == 'uncertain'
    assert presence['state'] == 'inconclusive'


@pytest.mark.parametrize('before,after,change,count,expected', [
    ('yes', 'no', 'possible_loss', 0, 'review_required'),
    ('yes', 'yes', 'possible_loss', 0, 'review_required'),
    ('yes', 'yes', 'no_visible_loss', 1, 'review_required'),
    ('no', 'no', 'possible_loss', 0, 'conflicting_evidence'),
    ('yes', 'no', 'no_visible_loss', 1, 'conflicting_evidence'),
    ('uncertain', 'uncertain', 'uncertain', 0, 'no_candidate_detected'),
])
def test_numeric_threshold_results_are_not_canopy_truth(before, after, change, count, expected):
    assessment = model_choices(before, after, change)
    summary = summarize_comparison('canopy_loss', measured(count), assessment, INTERVAL)
    assert summary['state'] == expected
    assert summary['method'] == 'checked-evidence-v2'
    presence = canopy_presence(measured(count), assessment)
    assert presence['target_id'] == TARGET['id']
    assert presence['assessment_status'] == 'unvalidated_model_proposal'
    if (before, after) == ('yes', 'yes'):
        assert 'partial loss' in presence['interpretation']


def test_insufficient_visibility_overrides_even_confident_scripted_choices(monkeypatch):
    classification, _ = classify(monkeypatch, scripted_response(
        before_canopy={'choice': 'yes', 'confidence': 1}, after_canopy={'choice': 'no', 'confidence': 1}))
    presence = canopy_presence(measured(coverage=.2), classification)
    assert presence['before'] == presence['after'] == 'uncertain'
    assert presence['assessment_status'] == 'unavailable'
    summary = summarize_comparison('canopy_loss', measured(coverage=.2), classification, INTERVAL)
    assert summary['state'] == 'inconclusive'
