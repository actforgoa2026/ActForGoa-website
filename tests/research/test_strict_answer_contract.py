"""Regressions for real citation identity and answer-length failures."""
from copy import deepcopy
import json
import pytest
from backend.chat import ChatRequest, normalize_answer, prepare_answer, provider_schema


EVIDENCE = [{'id': 'a44740d147d1894cd1304efd76dad111',
             'title': 'ZSI Goa bird report',
             'text': 'Nilgiri Wood Pigeon Columba elphinstonii Western Ghats'}]
REQUEST = ChatRequest(question='What geographic range does the source identify?')


def answer(text='The table identifies the Western Ghats as the endemic range.'):
    return {'coverage': 'full', 'paragraphs': [{'text': text, 'supports': [
        {'citation_id': EVIDENCE[0]['id'], 'quote': EVIDENCE[0]['text']}]}],
        'outside_context': None, 'limitation': None}


def test_wire_schema_restricts_support_to_selected_ids_and_has_no_duplicate_citation_list():
    payload, selected = prepare_answer(REQUEST, EVIDENCE)
    tool = payload['tools'][0]
    assert tool['strict'] is True
    assert tool['input_schema']['$defs']['Support']['properties']['citation_id']['enum'] == [EVIDENCE[0]['id']]
    assert 'citations' not in tool['input_schema']['$defs']['SupportedParagraph']['properties']
    assert list(tool['input_schema']['$defs']['SupportedParagraph']['properties']) == ['supports', 'text']
    assert selected == EVIDENCE


def test_links_are_derived_only_after_validating_exact_support():
    result = normalize_answer(answer(), REQUEST, EVIDENCE)
    assert result['paragraphs'][0]['citations'] == [EVIDENCE[0]['id']]
    assert result['citations'] == EVIDENCE
    for change in ['document_title', 'unknown_id', 'altered_quote', 'legacy_second_list']:
        raw = answer()
        if change == 'document_title': raw['paragraphs'][0]['supports'][0]['citation_id'] = EVIDENCE[0]['title']
        if change == 'unknown_id': raw['paragraphs'][0]['supports'][0]['citation_id'] = 'unknown'
        if change == 'altered_quote': raw['paragraphs'][0]['supports'][0]['quote'] = 'Endemic only to Goa'
        if change == 'legacy_second_list': raw['paragraphs'][0]['citations'] = [EVIDENCE[0]['title']]
        with pytest.raises(ValueError): normalize_answer(raw, REQUEST, EVIDENCE)


def test_word_boundaries_preserve_complete_text_and_reject_overflow_without_truncating():
    for separator in [' ', '\n', '\t', '\u00a0']:
        valid = separator.join(['Word'] * 60)
        assert normalize_answer(answer(valid), REQUEST, EVIDENCE)['paragraphs'][0]['text'] == valid
        with pytest.raises(ValueError): normalize_answer(answer(valid + ' extra'), REQUEST, EVIDENCE)
    raw = answer(' '.join(['Word'] * 60))
    raw['paragraphs'] *= 3
    assert len(normalize_answer(raw, REQUEST, EVIDENCE)['paragraphs']) == 3
    raw['paragraphs'].append(deepcopy(raw['paragraphs'][0]))
    with pytest.raises(ValueError): normalize_answer(raw, REQUEST, EVIDENCE)


def test_strict_schema_omits_unsupported_constraints_but_retains_server_checks():
    schema = json.dumps(provider_schema(EVIDENCE))
    for forbidden in ['minLength', 'maxLength', 'maxItems', 'pattern']:
        assert forbidden not in schema
    raw = answer(); raw['paragraphs'][0]['supports'] *= 7
    with pytest.raises(ValueError): normalize_answer(raw, REQUEST, EVIDENCE)


def test_prompt_budget_does_not_authorize_omitted_sources():
    evidence = EVIDENCE + [{'id': 'omitted', 'text': 'x' * 40000}]
    payload, selected = prepare_answer(REQUEST, evidence)
    assert selected == EVIDENCE
    assert payload['tools'][0]['input_schema']['$defs']['Support']['properties']['citation_id']['enum'] == [EVIDENCE[0]['id']]
