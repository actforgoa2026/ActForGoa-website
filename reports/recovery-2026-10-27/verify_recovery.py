"""Offline, read-only verification of a reconstructed research corpus.

Run from the repository root with the research Python environment. This script
does not create an app, initialize usage accounting, or construct a provider.
Only the explicitly selected report and fixture-copy destinations are written.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import numpy as np
import zvec

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend.library import Library

OLD_SQLITE_SHA = 'c6d80208581f3776d2cfaa2cfe3ff08e026bd055be1c2a574461934fa52d870f'
OLD_GENERATION = '20261026T131818-law-23a2e6a6'


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', required=True, type=Path)
    parser.add_argument('--input-state', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--cases-output', required=True, type=Path)
    args = parser.parse_args()
    root = args.data_root.resolve()
    state = json.loads(args.input_state.read_text())
    current = json.loads((root/'.research-index/CURRENT.json').read_text())['generation']
    inputs = [{'path': path, 'sha256': expected, 'unchanged': digest(path) == expected}
              for path, expected in state['input_sha256'].items()]
    assert all(item['unchanged'] for item in inputs), 'A read-only input changed'
    assert not list(root.rglob('answer-usage.sqlite*')), 'Usage database must not be in recovery data'
    assert not list(root.rglob('.research-usage')), 'Usage directory must not be in recovery data'
    assert not list(root.rglob('.env*')), 'Environment files must not be in recovery data'
    originals = {}
    generations = []
    for directory in sorted((root/'.research-index/generations').iterdir()):
        database = directory/'library.sqlite'
        with sqlite3.connect(f'file:{database}?mode=ro', uri=True) as db:
            db.row_factory = sqlite3.Row
            assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            docs = [json.loads(row[0]) for row in db.execute('SELECT metadata FROM documents')]
            page_count = db.execute('SELECT count(*) FROM pages').fetchone()[0]
            chunk_count = db.execute('SELECT count(*) FROM chunks').fetchone()[0]
            for doc in docs:
                relative = doc['raw_path']
                path = (root/relative).resolve()
                assert path.is_relative_to(root/'corpus/raw') and not (root/relative).is_symlink()
                if relative not in originals:
                    originals[relative] = digest(path)
                assert originals[relative] == doc['sha256'], relative
            verified_slices = 0
            previous_page = None
            page_text = None
            for row in db.execute('SELECT * FROM chunks ORDER BY doc_id,page,start'):
                key = (row['doc_id'], row['page'])
                if key != previous_page:
                    page = db.execute('SELECT text FROM pages WHERE doc_id=? AND page=?', key).fetchone()
                    assert page is not None, row['id']
                    page_text = page['text']
                    previous_page = key
                assert row['text'] == page_text[row['start']:row['end']], row['id']
                verified_slices += 1
            assert verified_slices == chunk_count, 'Missing chunk page'
            orphan_docs = db.execute('SELECT count(*) FROM pages p LEFT JOIN documents d ON d.id=p.doc_id WHERE d.id IS NULL').fetchone()[0]
            assert orphan_docs == 0
            chunk_text_hashes = {row['id']: hashlib.sha256(row['text'].encode()).digest()
                                 for row in db.execute('SELECT id,text FROM chunks')}
            fts_count = 0
            for row in db.execute('SELECT id,text FROM passages'):
                assert chunk_text_hashes.pop(row['id']) == hashlib.sha256(row['text'].encode()).digest()
                fts_count += 1
            assert not chunk_text_hashes
            assert fts_count == chunk_count
            generations.append({'generation': directory.name, 'sqlite_sha256': digest(database),
                                'documents': len(docs), 'pages': page_count, 'chunks': chunk_count,
                                'integrity_check': 'ok', 'verified_exact_slices': verified_slices,
                                'fts_rows': fts_count, 'all_originals_verified': True})
    lib = Library(root)
    reconciliation = json.loads((root/'legal-source-reconciliation.json').read_text())
    previous_generation = reconciliation['previous_generation']
    with lib.connect(previous_generation) as db:
        inherited_ids = {row[0] for row in db.execute('SELECT id FROM chunks')}
    previous_vectors = zvec.open(str(lib.generation_dir(previous_generation)/'zvec'),
                                 option=zvec.CollectionOption(read_only=True))
    vector_count = lib.vectors.stats.doc_count
    active = next(g for g in generations if g['generation'] == current)
    assert vector_count == active['chunks']
    with lib.connect() as db:
        vector_rows = list(db.execute('SELECT id,doc_id FROM chunks'))
    assert inherited_ids <= {row['id'] for row in vector_rows}
    vectors_verified = 0
    inherited_verified = 0
    for start in range(0, len(vector_rows), 256):
        batch = vector_rows[start:start+256]
        found = lib.vectors.fetch([row['id'] for row in batch])
        assert set(found) == {row['id'] for row in batch}
        inherited_batch = [row['id'] for row in batch if row['id'] in inherited_ids]
        inherited = previous_vectors.fetch(inherited_batch) if inherited_batch else {}
        for row in batch:
            document = found[row['id']]
            assert document.fields['document'] == row['doc_id']
            vector = np.asarray(document.vectors['embedding'])
            assert vector.shape == (384,) and np.isfinite(vector).all()
            assert abs(np.linalg.norm(vector)-1) < .001
            if row['id'] in inherited_ids:
                assert np.array_equal(vector, inherited[row['id']].vectors['embedding'])
                assert document.fields == inherited[row['id']].fields
                inherited_verified += 1
            vectors_verified += 1
    # The quantized encoder is sensitive to batch composition. Reproduce the
    # refresh script's actual 24-passage insertion batches, rather than demanding
    # byte equality with embeddings generated one passage at a time.
    with lib.connect() as db:
        appended = [dict(row) for row in db.execute('SELECT id,text FROM chunks ORDER BY rowid')
                    if row['id'] not in inherited_ids]
    appended_verified = 0
    for start in range(0, len(appended), 24):
        batch = appended[start:start+24]
        fresh = lib.encoder.encode([row['text'] for row in batch])
        stored = lib.vectors.fetch([row['id'] for row in batch])
        for row, vector in zip(batch, fresh):
            assert np.array_equal(vector, stored[row['id']].vectors['embedding']), row['id']
            appended_verified += 1
    baseline_root = Path(state['base_root'])
    baseline_checks = []
    for source in sorted((baseline_root/'.research-index/generations').iterdir()):
        copied = root/'.research-index/generations'/source.name
        files = [p for p in source.rglob('*') if p.is_file()]
        assert {str(p.relative_to(source)) for p in files} == {str(p.relative_to(copied)) for p in copied.rglob('*') if p.is_file()}
        assert all(digest(p) == digest(copied/p.relative_to(source)) for p in files)
        baseline_checks.append({'generation': source.name, 'files': len(files), 'all_files_byte_identical': True})
    reviewed_sources = []
    for item in reconciliation['outcomes']:
        doc = lib.document(item['document_id'], private=True)
        assert doc['sha256'] == item['sha256']
        assert doc.get('guide_verification'), item['citation']
        with lib.connect() as db:
            count = db.execute('SELECT count(*) FROM chunks WHERE doc_id=?', (doc['id'],)).fetchone()[0]
        assert count == item['searchable_passages']
        reviewed_sources.append({'citation': item['citation'], 'document_id': doc['id'],
                                 'sha256': doc['sha256'], 'searchable_passages': count})
    spec_path = ROOT/'tests/research/retrieval-evidence-cases.json'
    spec = json.loads(spec_path.read_text())
    reviewed_passages = []
    ids = sorted({identifier for case in spec['cases'] for group in case['required_evidence'] for identifier in group['any_of']})
    for identifier in ids:
        with lib.connect() as db:
            row = db.execute('SELECT * FROM chunks WHERE id=?', (identifier,)).fetchone()
        assert row is not None, identifier
        pages = lib.pages(row['doc_id'], current, row['page'], 1)
        assert pages[0]['text'][row['start']:row['end']] == row['text']
        reviewed_passages.append({'id': identifier, 'document_id': row['doc_id'], 'page': row['page'],
                                 'start': row['start'], 'end': row['end'],
                                 'text_sha256': hashlib.sha256(row['text'].encode()).hexdigest()})
    old_id = next(item['previous_document_id'] for item in reconciliation['outcomes'] if item['citation'] == 'V16')
    lib.document(old_id, reconciliation['previous_generation'])
    spec['generation'] = current
    # Questions, reviewed passage IDs and pass conditions remain unchanged.
    args.cases_output.parent.mkdir(parents=True, exist_ok=True)
    args.cases_output.write_text(json.dumps(spec, indent=2)+'\n')
    report = {'generation': current, 'source_git_head': state['source_git_head'],
              'historical_generation': OLD_GENERATION,
              'historical_sqlite_sha256': OLD_SQLITE_SHA,
              'sqlite_exactly_matches_historical_hash': active['sqlite_sha256'] == OLD_SQLITE_SHA,
              'limits': 'Historical SQLite hash matches are byte-identity evidence for that file only. The old complete package and vector-index hashes are unavailable. This is a new generation, not a recovered historical package. No answer acceptance, current-law or production-accounting claim.',
              'inputs': inputs, 'generations': generations, 'baseline_file_identity': baseline_checks,
              'originals': [{'path': p, 'sha256': h} for p, h in sorted(originals.items())],
              'current_vector_documents': vector_count, 'vector_ids_fields_and_values_verified': vectors_verified,
              'inherited_vectors_exactly_match_baseline': inherited_verified,
              'appended_vectors_exactly_match_replayed_ingestion_batches': appended_verified,
              'embedding_verification_method': 'Compare every inherited vector with the preserved baseline and replay all appended vectors in their original 24-passage insertion batches. Single-item re-encoding differs slightly with this quantized encoder and is not a byte-identity test.',
              'reviewed_sources': reviewed_sources,
              'reviewed_passages': reviewed_passages, 'old_v16_document_still_accessible': old_id,
              'fixture_source_sha256': digest(spec_path), 'fixture_copy_sha256': digest(args.cases_output),
              'fixture_copy_only_change': 'generation', 'provider_calls': 0,
              'usage_database_created_or_modified': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'generation': current, 'generations_checked': len(generations),
                      'unchanged_inputs': len(inputs), 'originals_verified': len(originals),
                      'current_exact_slices': active['verified_exact_slices'],
                      'vector_count': vector_count, 'reviewed_passages': len(reviewed_passages),
                      'historical_sqlite_byte_identical': report['sqlite_exactly_matches_historical_hash']}))


if __name__ == '__main__':
    main()
