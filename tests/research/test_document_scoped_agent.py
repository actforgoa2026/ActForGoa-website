"""Document-only tools and incomplete-scan citations, without provider calls."""
import json
import sqlite3

import pytest

from backend.agent_corpus import AgentCorpus
from backend.research_agent import ResearchTools, validate_answer


@pytest.fixture
def corpus(tmp_path):
    (tmp_path / 'manifest.json').write_text('{}')
    with sqlite3.connect(tmp_path / 'library.sqlite') as db:
        db.executescript('''
            CREATE TABLE documents(id TEXT, metadata TEXT);
            CREATE TABLE pages(doc_id TEXT, page INTEGER, label TEXT, text TEXT, origin TEXT, warning TEXT);
            CREATE TABLE chunks(id TEXT, doc_id TEXT, page INTEGER, start INTEGER, end INTEGER, text TEXT);
        ''')
        for identifier in ('plan', 'unrelated'):
            db.execute('INSERT INTO documents VALUES(?,?)', (identifier, json.dumps({
                'id': identifier, 'title': identifier, 'domains': ['ecology'], 'page_count': 2,
            })))
        db.executemany('INSERT INTO pages VALUES(?,?,?,?,?,?)', [
            ('plan', 1, 'PDF page 1', 'A proposed solar measure.', 'native', ''),
            ('plan', 2, 'PDF page 2', 'Partly extracted committee footer.', 'native',
             'Scanned committee minutes: native text is incomplete; these pages are not answer evidence. Read the original page image.'),
        ])
    return AgentCorpus(tmp_path, 'retained-edition', tmp_path, tmp_path / 'unused-search.sqlite')


def answer(evidence):
    return {'paragraphs': [{'text': 'A proposed measure.', 'supports': [evidence['id']]}],
            'clarification': None, 'limitation': None, 'followups': []}


def test_scoped_agent_cannot_leave_the_selected_source(corpus):
    tools = ResearchTools(corpus, 'ecology', 'plan')
    assert [d['id'] for d in tools.catalogue({'query': 'solar'})['documents']] == ['plan']
    assert tools.catalogue({'offset': 1})['documents'] == []
    with pytest.raises(ValueError, match='scoped to one document'):
        tools.read({'document_id': 'unrelated'})
    for method in (tools.crm_search, tools.crm_read):
        with pytest.raises(ValueError, match='only the selected document'):
            method({})
    assert len(ResearchTools(corpus).catalogue({})['documents']) == 2


def test_incomplete_scan_remains_readable_but_cannot_support_an_answer(corpus):
    tools = ResearchTools(corpus, 'ecology', 'plan')
    page = tools.read({'document_id': 'plan', 'page': 2})['pages'][0]
    assert page['text'] == 'Partly extracted committee footer.'
    assert page['answer_excluded']
    with pytest.raises(ValueError, match='preserved answer exclusion'):
        validate_answer(answer(page), tools, 'ecology')


def test_supported_answer_retains_exact_passage_and_edition(corpus):
    tools = ResearchTools(corpus, 'ecology', 'plan')
    page = tools.read({'document_id': 'plan', 'page': 1})['pages'][0]
    assert not page['answer_excluded']
    citation = validate_answer(answer(page), tools, 'ecology')['citations'][0]
    assert citation['text'] == 'A proposed solar measure.'
    assert citation['generation'] == 'retained-edition'
    assert 'generation=retained-edition' in citation['reader_url']
    assert 'passage=' in citation['reader_url']


def test_scoped_discovery_requires_a_read_before_exposing_citation_ids(corpus, monkeypatch):
    evidence = corpus.evidence('plan', 1)
    monkeypatch.setattr(corpus, 'search', lambda *args: {'results': [evidence]})
    tools = ResearchTools(corpus, 'ecology', 'plan')
    discovery = tools.search({'query': 'solar'})['results'][0]
    assert discovery['document_id'] == 'plan' and discovery['page'] == 1
    assert 'id' not in discovery and 'reader_url' not in discovery
    with pytest.raises(ValueError, match='source read'):
        validate_answer(answer(evidence), tools, 'ecology')
    read = tools.read({'document_id': 'plan', 'page': 1})['pages'][0]
    assert validate_answer(answer(read), tools, 'ecology')['citations']
    assert ResearchTools(corpus).search({'query': 'solar'})['results'][0]['id'] == evidence['id']


def test_native_spread_carries_original_headers_into_read_and_citations(corpus):
    corpus.documents['plan']['extraction_version'] = 'goa-sapcc-native-spreads-v1'
    header = 'Intervention\tStatus\tAgency\tBarriers and gaps\tBudget\tTime frame'
    row = 'Rural rooftop solar\tproposed\tGEDA\tun-electrified houses identified\tRs. 1 crore\t2 years'
    # A longer spread must remain complete even if the SDK asks for a short
    # excerpt, with exact adjacent headers inside the existing total tool cap.
    text = row + '\n' + 'Original source context. ' * 80
    with sqlite3.connect(corpus.index / 'library.sqlite') as db:
        db.execute('UPDATE pages SET text=? WHERE doc_id=? AND page=1', (header, 'plan'))
        db.execute('UPDATE pages SET text=?,warning=? WHERE doc_id=? AND page=2', (text, '', 'plan'))
    tools = ResearchTools(corpus, 'ecology', 'plan')
    pages = tools.read({'document_id': 'plan', 'page': 2, 'max_chars': 1000})['pages']
    assert pages[0]['text'] == text
    assert pages[1]['text'] == header
    assert sum(len(p['text']) for p in pages) <= 24000
    tools.read({'document_id': 'plan', 'page': 1})
    result = validate_answer(answer(pages[0]), tools, 'ecology')
    assert [c['page'] for c in result['citations']] == [2, 1]
    assert result['paragraphs'][0]['citations'] == [pages[0]['id'], pages[1]['id']]
