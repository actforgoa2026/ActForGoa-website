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
