"""Stage one SAPCC extraction in a new generation; never activate or edit the base.

Retain every other document/page/chunk/FTS row, all old generations, original
bytes and the usage ledger. CURRENT.json is deliberately outside this script.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.embeddings import Encoder
from scripts.extract_sapcc import SOURCE_SHA256, VERSION
import zvec


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def unchanged_rows(db, doc_id):
    digest = hashlib.sha256()
    statements = [
        ('documents', 'SELECT * FROM documents WHERE id!=? ORDER BY id'),
        ('pages', 'SELECT * FROM pages WHERE doc_id!=? ORDER BY doc_id,page'),
        ('chunks', 'SELECT * FROM chunks WHERE doc_id!=? ORDER BY id'),
        ('passages', 'SELECT p.* FROM passages p JOIN chunks c ON c.id=p.id WHERE c.doc_id!=? ORDER BY p.id'),
    ]
    counts = {}
    for name, query in statements:
        count = 0
        for row in db.execute(query, (doc_id,)):
            digest.update(json.dumps([name, list(row)], ensure_ascii=False).encode())
            count += 1
        counts[name] = count
    return {'sha256': digest.hexdigest(), 'counts': counts}


def build(data_root, base_index, index_root, baseline, generation, pages_path):
    if not all(re.fullmatch(r'[A-Za-z0-9-]{1,80}', name) for name in (baseline, generation)) or baseline == generation:
        raise ValueError('Distinct, safe generation names are required')
    source = base_index / 'generations' / baseline
    target = index_root / 'generations' / generation
    if target.exists():
        raise ValueError('Target already exists; preserve it and choose a new generation')
    if any(path.is_symlink() for path in source.rglob('*')):
        raise ValueError('Base generation cannot contain symlinks')
    before_files = {str(path.relative_to(source)): sha(path) for path in source.rglob('*') if path.is_file()}
    pages = json.loads(pages_path.read_text())
    if [page['page'] for page in pages] != list(range(1, 112)):
        raise ValueError('Incomplete SAPCC page sequence')
    if any(page['origin'] != VERSION for page in pages):
        raise ValueError('Unexpected extraction version')
    extraction_hash = hashlib.sha256(json.dumps(pages, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    doc_id = SOURCE_SHA256[:24] + '-' + extraction_hash[:12]
    with sqlite3.connect(f'file:{source / "library.sqlite"}?mode=ro', uri=True) as base:
        matches = [(identifier, json.loads(meta)) for identifier, meta in base.execute('SELECT id,metadata FROM documents')
                   if json.loads(meta).get('sha256') == SOURCE_SHA256]
        if len(matches) != 1:
            raise ValueError('Expected exactly one existing SAPCC original')
        old_id, metadata = matches[0]
        original = (data_root / metadata['raw_path']).resolve()
        if not original.is_relative_to((data_root / 'corpus/raw').resolve()) or sha(original) != SOURCE_SHA256:
            raise ValueError('Source PDF identity does not match')
        preserved = unchanged_rows(base, old_id)
    shutil.copytree(source, target)
    encoder = Encoder()
    manifest = json.loads((source / 'manifest.json').read_text())
    if encoder.fingerprint != manifest['encoder_sha256']:
        raise ValueError('Embedding model must match the base generation')
    db = sqlite3.connect(target / 'library.sqlite')
    old_chunks = [row[0] for row in db.execute('SELECT id FROM chunks WHERE doc_id=?', (old_id,))]
    vectors = zvec.open(str(target / 'zvec'))
    statuses = vectors.delete(old_chunks)
    if any(not status.ok() for status in statuses):
        raise RuntimeError('Could not remove all old SAPCC vectors from the staged copy')
    db.executemany('DELETE FROM passages WHERE id=?', [(identifier,) for identifier in old_chunks])
    for table in ('chunks', 'pages'):
        db.execute(f'DELETE FROM {table} WHERE doc_id=?', (old_id,))
    db.execute('DELETE FROM documents WHERE id=?', (old_id,))
    metadata.update(id=doc_id, title='Goa State Action Plan for Climate Change (SAPCC), 2023–2033',
                    extraction_version=VERSION, page_count=111,
                    source_date_metadata={'publication_date': '2023-04-26', 'plan_period': '2023–2033'},
                    quality={'low_text_pages': sum(sum(c.isalnum() for c in p['text']) < 100 for p in pages),
                             'ocr_pages': 0, 'scanned_minutes_excluded': 12},
                    guide_verification={'limitations': 'Policy proposals from the 2023 plan, not current implementation evidence. Tables retain native cells; cross-page rows are not reconstructed. Scanned minutes on PDF pages 99–110 are excluded from answers.'})
    db.execute('INSERT INTO documents VALUES(?,?)', (doc_id, json.dumps(metadata, ensure_ascii=False)))
    pending = []
    inserted = 0

    def flush():
        if not pending:
            return
        embeddings = encoder.encode([text for _, text in pending])
        statuses = vectors.insert([zvec.Doc(id=identifier, fields={'document': doc_id}, vectors={'embedding': vector.tolist()})
                                  for (identifier, _), vector in zip(pending, embeddings)])
        if any(not status.ok() for status in statuses):
            raise RuntimeError('Staged SAPCC vector insertion failed')
        pending.clear()

    for page in pages:
        db.execute('INSERT INTO pages VALUES(?,?,?,?,?,?)',
                   (doc_id, page['page'], page['label'], page['text'], page['origin'], page['warning']))
        if 99 <= page['page'] <= 110 or sum(c.isalnum() for c in page['text']) < 100:
            continue
        for left, right, text in encoder.chunks(page['text']):
            identifier = hashlib.sha256(f'{doc_id}:{page["page"]}:{left}:{right}'.encode()).hexdigest()[:32]
            db.execute('INSERT INTO chunks VALUES(?,?,?,?,?,?,?)', (identifier, doc_id, page['page'], left, right, text, page['origin']))
            db.execute('INSERT INTO passages VALUES(?,?,?)', (identifier, metadata['title'], text))
            pending.append((identifier, text))
            inserted += 1
            if len(pending) >= 24:
                flush()
    flush()
    vectors.optimize()
    vectors.flush()
    del vectors
    db.commit()
    if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or unchanged_rows(db, doc_id) != preserved:
        raise RuntimeError('Unrelated source data changed in the staged generation')
    stats = dict(manifest['stats'])
    for table, key in [('documents', 'documents'), ('pages', 'pages'), ('chunks', 'chunks')]:
        stats[key] = db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    stats['low_text_pages'] = db.execute('SELECT COUNT(*) FROM pages WHERE length(trim(text))<60').fetchone()[0]
    db.close()
    after_files = {str(path.relative_to(source)): sha(path) for path in source.rglob('*') if path.is_file()}
    if before_files != after_files:
        raise RuntimeError('Base generation changed during staging')
    report = {'baseline': baseline, 'generation': generation, 'old_document_id': old_id, 'document_id': doc_id,
              'source_sha256': SOURCE_SHA256, 'extraction_sha256': extraction_hash, 'extraction_version': VERSION,
              'old_chunks': len(old_chunks), 'new_chunks': inserted, 'preserved_rows': preserved,
              'base_files_unchanged': True, 'base_files': before_files, 'current_changed': False}
    manifest.update(generation=generation, created_at=datetime.now(timezone.utc).isoformat(), stats=stats,
                    sapcc_refresh=report)
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (target / 'sapcc-refresh.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('data-root', 'base-index', 'index-root', 'pages'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--generation', required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.data_root, args.base_index, args.index_root, args.baseline, args.generation, args.pages), indent=2))
