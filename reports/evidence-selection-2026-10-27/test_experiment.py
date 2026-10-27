"""Synthetic safety checks for the report-only experiment, with no native index."""
from collections import Counter
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fielded_candidate', HERE/'candidate.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


@pytest.mark.parametrize('entry', ['evaluate.py', 'capture_sources.py'])
@pytest.mark.parametrize('argument', ['--data-root', '--output'])
def test_native_entry_rejects_preservation_via_symlink(tmp_path, entry, argument):
    protected = tmp_path/'protected'
    protected.mkdir()
    (protected/'seal.json').write_text('{}')
    alias = tmp_path/'alias'
    alias.symlink_to(protected, target_is_directory=True)
    args = {'--data-root': str(tmp_path/'absent-data'), '--output': str(tmp_path/'result.json')}
    args[argument] = str(alias/'child')
    result = subprocess.run([sys.executable, str(HERE/entry),
                             *[value for pair in args.items() for value in pair]], capture_output=True, text=True)
    assert result.returncode == 2
    assert 'disposable-copy wrapper' in result.stderr
    assert not (protected/'child').exists()


def row(identifier, document, text):
    return {'id': identifier, 'doc_id': document, 'text': text, 'rrf': .02,
            'meta': {'title': 'Archive guide', 'url': 'https://example.org/'+document},
            'page': 1, 'label': '1', 'start': 0, 'end': len(text), 'origin': 'text',
            'warning': None, 'page_context': '', 'channels': ['keyword']}


def test_complete_words_do_not_join_notify_and_notifications():
    record = {'generation': 'synthetic', 'terms': ['notify'], 'candidates': [
        row('one', 'a', 'Old notifications were superseded.'),
        row('two', 'b', 'Notify the archive clerk about damage.')]}
    hits, scores = candidate.revise(record, 10)
    assert hits[0]['id'] == 'two'
    assert scores['lexical']['one'] == 0


def test_document_cap_and_cross_document_duplicate_filter():
    first = 'Water flows through sluice gates to regulate saline entry.'
    record = {'generation': 'synthetic', 'terms': ['water'], 'candidates': [
        row('one', 'a', first), row('duplicate', 'b', first),
        row('two', 'a', 'Fresh water can recharge shallow wells during rainfall.'),
        row('three', 'a', 'Drinking water distribution requires regular maintenance.'),
        row('four', 'c', 'Surface water pools host seasonal aquatic plants.')]}
    hits, _ = candidate.revise(record, 10)
    assert max(Counter(h['document_id'] for h in hits).values()) <= 2
    assert len({'one', 'duplicate'} & {h['id'] for h in hits}) == 1
    assert all(h['text'][h['start']:h['end']] == h['text'] for h in hits)
