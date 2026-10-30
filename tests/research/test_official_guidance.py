"""Keep reviewed preparedness sources distinct from proposals and live alerts."""
import pytest

from backend.official_guidance import flood_guidance, guidance_allowed, SAPCC_SHA256
from backend.research_agent import ResearchTools, validate_answer, agent_options


class Corpus:
    def document(self, identifier):
        return {'sha256': SAPCC_SHA256 if identifier == 'sapcc' else 'unrelated'}


def raw(supports):
    return {'paragraphs': [{'text': 'Prepare safely.', 'supports': supports}],
            'clarification': None, 'limitation': None, 'followups': []}


def test_allowlisted_guidance_extends_sapcc_and_general_research_only():
    corpus = Corpus()
    assert guidance_allowed(corpus, None) and guidance_allowed(corpus, 'sapcc')
    assert not guidance_allowed(corpus, 'other')
    for identifier in (None, 'sapcc'):
        readers = ResearchTools(corpus, document_id=identifier)
        result = readers.official_guidance({'topic': 'floods'})
        assert len(result['sources']) == 2
        assert result['checked_on'] == '2026-10-30'
        with pytest.raises(ValueError): readers.official_guidance({'topic': 'https://untrusted.example'})
    with pytest.raises(ValueError, match='outside'):
        ResearchTools(corpus, document_id='other').official_guidance({'topic': 'floods'})


def test_read_required_and_exact_reviewed_summary_resolved():
    readers = ResearchTools(Corpus(), document_id='sapcc')
    source = flood_guidance()['sources'][0]
    with pytest.raises(ValueError, match='source read'):
        validate_answer(raw([source['id']]), readers, 'ecology')
    readers.official_guidance({'topic': 'floods'})
    result = validate_answer(raw([source['id']]), readers, 'ecology')
    assert result['paragraphs'][0]['source_kind'] == 'official_guidance'
    assert result['citations'][0] == source
    assert source['published_on'] is None
    assert 'not a live flood warning' in source['warning']
    assert source['origin'] == 'official_guidance_summary'


def test_mixed_policy_and_preparedness_supports_are_rejected():
    readers = ResearchTools(Corpus(), document_id='sapcc')
    source = readers.official_guidance({'topic': 'floods'})['sources'][0]
    readers.evidence['plan-page'] = {'id': 'plan-page', 'text': 'A proposed measure.'}
    readers.citable_ids.add('plan-page')
    with pytest.raises(ValueError, match='separate paragraphs'):
        validate_answer(raw(['plan-page', source['id']]), readers, 'ecology')
    answer = raw(['plan-page'])
    answer['paragraphs'] += raw([source['id']])['paragraphs']
    result = validate_answer(answer, readers, 'ecology')
    assert [p['source_kind'] for p in result['paragraphs']] == ['library', 'official_guidance']


def test_sdk_exposes_guidance_without_broadening_other_document_tools(tmp_path):
    for identifier, allowed in [('sapcc', True), ('other', False)]:
        readers = ResearchTools(Corpus(), document_id=identifier)
        options = agent_options(readers, 'Test', 'http://127.0.0.1:1', 'test', 0, state=tmp_path)
        assert ('mcp__research__read_official_guidance' in options.allowed_tools) == allowed
        assert options.tools == []


def test_guidance_exposes_one_citation_id_without_a_competing_digest():
    readers = ResearchTools(Corpus())
    source = readers.official_guidance({'topic': 'floods'})['sources'][0]
    assert 'sha256' not in source
    original = readers.evidence[source['id']]
    assert len(original['sha256']) == 64
    assert validate_answer(raw([source['id']]), readers, 'all')['citations'][0] == original
    expanded = source['id'].rsplit(':', 1)[0] + ':' + original['sha256']
    with pytest.raises(ValueError, match='source read'):
        validate_answer(raw([expanded]), readers, 'all')
