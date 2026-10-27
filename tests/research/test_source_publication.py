"""Publication provenance checks, independent of retrieval, providers and native stores."""
from copy import deepcopy
from dataclasses import replace
import json

import pytest

from backend.anthropic_provider import message_request, normalize_native_answer
from backend.chat import ChatRequest, Message, evidence_payload, prepare_answer
from backend.providers import chat_config
from backend.source_publication import publication_context


@pytest.mark.parametrize('values,year', [
    (['2025'], 2025), (['2025-05-04', '2025/05/04'], 2025),
    (['2024-02-29'], 2024), (['2025-01-01', '2025-12-31'], 2025),
    (['2024', '2025'], None), (['2025', 'not stated'], None),
    (['2025-02-29'], None), (['2025-04-31'], None), (['0000'], None),
    ([' 2025'], None), (['2025-05/04'], None), (['2025-05-04T00:00:00Z'], None),
    ([2025], None), ([True], None), ([None], None),
])
def test_only_consistent_explicit_publication_years_resolve(values, year):
    metadata = [{'field': 'prism.publicationDate', 'value': value} for value in values]
    context = publication_context(metadata)
    assert context['year'] == year
    assert ('unresolved' in context['label']) == (year is None)


@pytest.mark.parametrize('metadata', [
    None, {}, [], {'reviewed_locator_and_dates': 'Saved in 2025.'},
    [{'field': 'dc.date', 'value': '2025'}],
    [{'field': 'retrieved_at', 'value': '2025-05-04'}],
    [{'field': [], 'value': '2025'}, {'field': {}, 'value': '2025'}],
])
def test_generic_dates_and_unknown_provenance_do_not_become_publication_years(metadata):
    assert publication_context(metadata) is None


def dated_evidence():
    return [{
        'id': 'survey', 'text': 'In 2019, twelve of the surveyed ponds held water in June.',
        'document_id': 'doc-a', 'generation': 'saved-a', 'title': 'Survey uploaded 2026',
        'retrieved_at': '2026-10-28',
        'source_date_metadata': [
            {'field': 'dc.date', 'value': '2026-10-28'},
            {'field': 'prism.publicationDate', 'value': '2025-05-04'},
            {'field': 'citation_online_date', 'value': '2025/05/04'},
        ],
    }]


def dated_unit():
    return {
        'text': 'A source published in 2025 reports that twelve surveyed ponds held water in June 2019.',
        'primary_support': {'citation_id': 'survey', 'field': 'text',
                            'quote': dated_evidence()[0]['text']},
        'supports': [{'citation_id': 'survey', 'field': 'source_publication',
                      'quote': 'Source publication year: 2025 (source metadata).'}],
    }


def native_answer(unit, style='standard'):
    return {'status': 'answered', **({'paragraph': unit} if style == 'brief' else {'paragraphs': [unit]})}


def test_publication_annotation_is_native_only_and_does_not_rewrite_source_records():
    evidence = dated_evidence()
    original = deepcopy(evidence)
    native = evidence_payload(evidence, provider='anthropic')
    source = next(iter(native['sources'].values()))
    assert source['source_publication'] == 'Source publication year: 2025 (source metadata).'
    assert source['source_date_metadata'] == original[0]['source_date_metadata']
    assert native['evidence'][0]['text'] == original[0]['text']
    for provider in (None, 'openrouter', 'openai', 'qwen'):
        assert 'source_publication' not in next(iter(evidence_payload(evidence, provider=provider)['sources'].values()))
    assert evidence == original


@pytest.mark.parametrize('style', ['brief', 'standard'])
@pytest.mark.parametrize('model', ['claude-haiku-5-5', 'claude-sonnet-5-5'])
def test_dated_paraphrase_preserves_observation_year_and_maps_losslessly(style, model, monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER', 'anthropic')
    monkeypatch.setenv('ANTHROPIC_CHAT_MODEL', model)
    monkeypatch.setenv('ANTHROPIC_CHAT_EFFORT', 'medium')
    evidence = dated_evidence()
    prepared = prepare_answer(ChatRequest(question='What did the pond survey report?', answer_style=style),
                              evidence, provider='anthropic')
    unit = dated_unit()
    result = json.loads(normalize_native_answer(json.dumps(native_answer(unit, style)), prepared))
    assert result['paragraphs'] == [{'text': unit['text'], 'citations': ['survey']}]
    assert prepared.evidence == evidence
    wire = message_request(chat_config(), prepared)
    assert wire['model'] == model and wire['max_tokens'] == 9000
    assert wire['thinking'] == {'type': 'adaptive'}
    assert wire['output_config']['effort'] == 'medium'
    assert len(json.dumps(wire['output_config']['format']['schema'], separators=(',', ':')).encode()) <= 4096


@pytest.mark.parametrize('change', ['missing-support', 'missing-year', 'wrong-year', 'substring-year',
                                   'partial-label', 'different-source', 'other-paragraph'])
def test_local_year_acknowledgement_cannot_be_omitted_or_borrowed(change):
    evidence = dated_evidence() + [{'id': 'other', 'text': 'Ponds are seasonal.',
                                   'source_date_metadata': [{'field': 'datePublished', 'value': '2024'}]}]
    prepared = prepare_answer(ChatRequest(question='What was observed in 2025?',
        history=[Message(role='assistant', content='A previous answer mentioned 2025.')]), evidence, provider='anthropic')
    unit = dated_unit()
    payload = native_answer(unit)
    if change == 'missing-support': unit['supports'] = []
    elif change == 'missing-year': unit['text'] = 'The survey found twelve ponds holding water in June 2019.'
    elif change == 'wrong-year': unit['text'] = unit['text'].replace('2025', '2024')
    elif change == 'substring-year': unit['text'] = unit['text'].replace('2025', '120250')
    elif change == 'partial-label': unit['supports'][0]['quote'] = '2025'
    elif change == 'different-source': unit['supports'][0]['citation_id'] = 'other'
    elif change == 'other-paragraph':
        payload['paragraphs'].append(deepcopy(unit))
        payload['paragraphs'][1]['text'] = 'Twelve surveyed ponds held water in June 2019.'
    with pytest.raises(ValueError, match='evidence contract'):
        normalize_native_answer(json.dumps(payload), prepared)


def test_inconsistent_derived_label_fails_before_dispatch(monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER', 'anthropic')
    prepared = prepare_answer(ChatRequest(question='What did the survey report?'), dated_evidence(), provider='anthropic')
    payload = json.loads(prepared.messages[-1]['content'])
    next(iter(payload['sources'].values()))['source_publication'] = 'Source publication year: 2024 (source metadata).'
    altered = replace(prepared, messages=[*prepared.messages[:-1], {
        'role': 'user', 'content': json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}])
    with pytest.raises(ValueError, match='publication differs'):
        message_request(chat_config(), altered)


def test_date_acknowledgement_does_not_certify_meaning():
    # An exact quote plus the right year can still accompany a wrong assertion.
    # Preserve this blind spot explicitly; live semantic review is mandatory.
    prepared = prepare_answer(ChatRequest(question='What did the survey report?'), dated_evidence(), provider='anthropic')
    unit = dated_unit()
    unit['text'] = 'A source published in 2025 proves all ponds everywhere hold water all year.'
    result = json.loads(normalize_native_answer(json.dumps(native_answer(unit)), prepared))
    assert result['paragraphs'][0]['text'] == unit['text']


@pytest.mark.parametrize('distinct_source', [False, True])
def test_each_source_has_its_own_local_label_while_same_source_passages_share_one(distinct_source):
    evidence = dated_evidence()
    second = deepcopy(evidence[0])
    second.update(id='second', text='A separate observation concerns flowering plants.')
    if distinct_source:second['document_id'] = 'different-document'
    evidence.append(second)
    prepared = prepare_answer(ChatRequest(question='What does the published survey describe?'), evidence, provider='anthropic')
    payload = json.loads(prepared.messages[-1]['content'])
    assert len(payload['sources']) == (2 if distinct_source else 1)
    unit = dated_unit()
    unit['text'] += ' The 2025 material also describes an observation of flowering plants.'
    unit['supports'].append({'citation_id': 'second', 'field': 'text', 'quote': second['text']})
    if distinct_source:
        # Identical year/label does not make two distinct source records equal.
        with pytest.raises(ValueError, match='evidence contract'):
            normalize_native_answer(json.dumps(native_answer(unit)), prepared)
        unit['supports'].append({'citation_id': 'second', 'field': 'source_publication',
                                'quote': unit['supports'][0]['quote']})
    result = json.loads(normalize_native_answer(json.dumps(native_answer(unit)), prepared))
    assert result['paragraphs'] == [{'text': unit['text'], 'citations': ['survey', 'second']}]


def test_shared_source_acknowledgement_cannot_be_borrowed_from_another_paragraph():
    evidence = dated_evidence()
    second = deepcopy(evidence[0])
    second.update(id='second', text='A separate observation concerns flowering plants.')
    evidence.append(second)
    prepared = prepare_answer(ChatRequest(question='What does the published survey describe?'), evidence, provider='anthropic')
    another = {'text': 'The source published in 2025 describes an observation of flowering plants.',
               'primary_support': {'citation_id': 'second', 'field': 'text', 'quote': second['text']},
               'supports': []}
    answer = {'status': 'answered', 'paragraphs': [dated_unit(), another]}
    with pytest.raises(ValueError, match='evidence contract'):
        normalize_native_answer(json.dumps(answer), prepared)


def test_shared_source_label_does_not_replace_required_context_text():
    evidence = dated_evidence()
    context = deepcopy(evidence[0])
    context.update(id='header', text='Survey columns: year and seasonal pond count.')
    evidence[0]['supporting_context'] = [context]
    prepared = prepare_answer(ChatRequest(question='What did the survey observe?'), evidence, provider='anthropic')
    unit = dated_unit()
    with pytest.raises(ValueError, match='evidence contract'):
        normalize_native_answer(json.dumps(native_answer(unit)), prepared)
    unit['supports'].append({'citation_id': 'header', 'field': 'text', 'quote': context['text']})
    result = json.loads(normalize_native_answer(json.dumps(native_answer(unit)), prepared))
    assert result['paragraphs'][0]['citations'] == ['survey', 'header']
