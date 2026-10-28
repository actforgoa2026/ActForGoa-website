"""Add verified legal originals to a cloned immutable research generation.

No network calls and no changes to the source corpus or previous generation.
The evidence register supplies reviewed scope/limitations, not consolidated law.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import zvec
from bs4 import BeautifulSoup
from backend.embeddings import Encoder
from backend.domains import document_domains
from backend.extraction import VERSION, extract_source, safe_path, text_quality_warning

REGISTER = Path('corpus/research/verification-2026-10-23/evidence-manifest.json')
# These classifications describe the reviewed originals in the register, rather
# than guessing legal authority from a URL, upload date or document filename.
KINDS = {
    'V01': 'official_procedure', 'V02': 'official_procedure', 'V03': 'primary_legislation',
    'V04': 'commencement_notification', 'V05': 'gazette_with_amendment',
    'V06': 'amendment_notification', 'V07': 'rules_notification', 'V08': 'official_press_statement',
    'V09': 'rules_notification', 'V10': 'scheme_notification', 'V11': 'legislative_statement',
    'V12': 'official_press_statement', 'V13': 'clinical_guidance', 'V14': 'official_handbook',
    'V15': 'official_press_statement', 'V16': 'official_procedure', 'V17': 'official_circular',
    'V18': 'final_wetland_notifications', 'V19': 'rules_notification',
    'V20': 'historical_primary_legislation', 'V21': 'administrative_order_in_gazette',
    'V22': 'official_map', 'V23': 'primary_legislation_with_commencement',
    'V24': 'official_forms_index', 'V25': 'official_citizen_charter', 'V26': 'legislative_answer',
}

def sha(path):
    with path.open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()

def copy_file(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if sha(source) != sha(destination): raise ValueError('Destination checksum conflict')
        return
    if sys.platform == 'darwin': subprocess.run(['cp', '-c', str(source), str(destination)], check=True)
    else: shutil.copy2(source, destination)

def clone_directory(source, destination):
    if destination.exists(): raise ValueError('Refusing to replace an existing generation')
    for path in source.rglob('*'):
        if path.is_symlink(): raise ValueError('Source generation contains a symlink')
        relative = path.relative_to(source)
        if path.is_dir(): (destination / relative).mkdir(parents=True, exist_ok=True)
        else: copy_file(path, destination / relative)

def reviewed_metadata(metadata, evidence):
    return {**metadata, 'title': evidence['title'], 'domains':list(dict.fromkeys([*document_domains(metadata),'legal'])),
        'document_kind_hint': KINDS[evidence['citation']],
        'classification_method': 'Manual classification of the official original in the guide verification register',
        'legal_currency': f"{KINDS[evidence['citation']]}; reviewed passages, not verified consolidated current law. {evidence['limitations']}",
        'source_date_metadata': {
            'original_metadata': metadata.get('source_date_metadata'),
            'review_date': evidence['review_date_local'],
            'review_timezone': evidence['review_timezone'],
            'reviewed_locator_and_dates': evidence['location'],
            'date_caution': 'Review, retrieval and upload dates are not commencement or publication dates.'},
        'guide_verification': {key: evidence[key] for key in ('citation','location','limitations','review_date_local','review_timezone')},
    }

def verified_pages(root, metadata, entry):
    if entry['citation'] in ('V08', 'V15'):
        # PIB wraps its article in an ASP.NET form. The generic extractor drops
        # forms, so independently reproduce the reviewed native article text.
        soup = BeautifulSoup(safe_path(root, metadata['raw_path']).read_bytes(), 'lxml')
        article = soup.select_one('.innner-page-main-about-us-content-right-part')
        if article is None: raise ValueError('Verified PIB article is missing')
        text = article.get_text('\n', strip=True)
        if hashlib.sha256(text.encode()).hexdigest() != entry['text_sha256']:
            raise ValueError('Verified PIB extraction checksum differs')
        pages = [{'page':1, 'label':'Official release text', 'text':text,
            'origin':'pib_article_native_text', 'warning':'Official press statement; not primary legislation or proof of local service availability.'}]
        extraction_hash = hashlib.sha256(json.dumps(pages, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        return metadata['sha256'][:24]+'-'+extraction_hash[:12], pages
    return extract_source(root, metadata, improve=True, ocr_budget=[0])

def refresh(base_root, source_root, output_root):
    base_root, source_root, output_root = map(lambda p: Path(p).resolve(), (base_root, source_root, output_root))
    if output_root in (base_root, source_root) or output_root.exists():
        raise ValueError('Use a new, isolated output directory')
    evidence = json.loads((source_root / REGISTER).read_text())
    if {e['citation'] for e in evidence} != set(KINDS): raise ValueError('Unexpected verification register')
    generation = json.loads((base_root / '.research-index/CURRENT.json').read_text())['generation']
    old = base_root / '.research-index/generations' / generation
    old_manifest = json.loads((old / 'manifest.json').read_text())
    old_database_hash = sha(old / 'library.sqlite')
    encoder = Encoder()
    if encoder.fingerprint != old_manifest['encoder_sha256'] or old_manifest['extraction_version'] != VERSION:
        raise ValueError('Embedding/extraction version differs; a reviewed migration is required')
    new_generation = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-law-' + uuid.uuid4().hex[:8]
    index = output_root / '.research-index'
    clone_directory(old, index / 'generations' / generation)
    new = index / 'generations' / new_generation
    clone_directory(old, new)
    db = sqlite3.connect(new / 'library.sqlite')
    records = [json.loads(row[0]) for row in db.execute('SELECT metadata FROM documents')]
    by_hash = {record['sha256']: record for record in records}
    for record in records:
        source = safe_path(base_root, record['raw_path'])
        if sha(source) != record['sha256']: raise ValueError('Baseline original checksum mismatch')
        copy_file(source, output_root / record['raw_path'])
    vectors = zvec.open(str(new / 'zvec'))
    pending = []
    outcomes = []

    def flush():
        if not pending: return
        embedded = encoder.encode([row['text'] for row in pending])
        result = vectors.insert([zvec.Doc(id=row['id'], fields={'document': row['doc_id']},
            vectors={'embedding': vector.tolist()}) for row, vector in zip(pending, embedded)])
        if result and any(not status.ok() for status in result): raise RuntimeError('Vector insertion failed')
        pending.clear()

    for entry in evidence:
        metadata = json.loads((source_root / f"corpus/metadata/{entry['id']}.json").read_text())
        if metadata['sha256'] != entry['sha256'] or sha(safe_path(source_root, entry['raw_path'])) != entry['sha256']:
            raise ValueError('Verified original checksum mismatch')
        present = by_hash.get(entry['sha256'])
        refresh_ocr = bool(present and metadata.get('ocr_pages_path') and
            not db.execute('SELECT count(*) FROM chunks WHERE doc_id=?', (present['id'],)).fetchone()[0])
        if present and not refresh_ocr:
            updated = reviewed_metadata(present, entry)
            aliases = updated.setdefault('aliases', [])
            if entry['url'] not in {a['url'] for a in aliases}:
                aliases.append({'url': entry['url'], 'title': entry['title']})
            db.execute('UPDATE documents SET metadata=? WHERE id=?', (json.dumps(updated), present['id']))
            db.execute('UPDATE passages SET title=? WHERE id IN (SELECT id FROM chunks WHERE doc_id=?)', (entry['title'], present['id']))
            doc_id = present['id']
            outcome = 'existing_original_provenance_enriched'
        else:
            metadata = reviewed_metadata(metadata, entry)
            for key in ('raw_path','pages_path','text_path','ocr_pages_path'):
                if metadata.get(key): copy_file(safe_path(source_root, metadata[key]), output_root / metadata[key])
            if metadata.get('ocr_pages_path') and entry.get('ocr_sha256'):
                if sha(safe_path(output_root, metadata['ocr_pages_path'])) != entry['ocr_sha256']:
                    raise ValueError('Verified OCR checksum differs')
            doc_id, pages = verified_pages(output_root, metadata, entry)
            updated = {**metadata, 'id': doc_id, 'source_id': metadata['id'], 'extraction_version': VERSION,
                'page_count': len(pages), 'page_labels': 'physical_pdf_pages' if metadata.get('format') == 'pdf' else 'document_sections',
                'quality': {'low_text_pages': sum(len(p['text'].strip()) < 60 for p in pages),
                            'ocr_pages': sum(p['origin'].startswith('ocr') for p in pages)},
                'aliases': [{'url': entry['url'], 'title': entry['title']}], 'ecology_source': False}
            if refresh_ocr:
                # The old generation and its exact empty extraction remain
                # readable. This generation uses the newly available OCR.
                db.execute('DELETE FROM pages WHERE doc_id=?', (present['id'],))
                db.execute('DELETE FROM documents WHERE id=?', (present['id'],))
            db.execute('INSERT INTO documents VALUES (?,?)', (doc_id, json.dumps(updated)))
            for page in pages:
                warning = text_quality_warning(page['text'])
                if warning: page['warning'] = warning
                db.execute('INSERT INTO pages VALUES (?,?,?,?,?,?)', (doc_id,page['page'],page['label'],page['text'],page['origin'],page['warning']))
                if warning: continue
                for left, right, text in encoder.chunks(page['text']):
                    chunk_id = hashlib.sha256(f'{doc_id}:{page["page"]}:{left}:{right}'.encode()).hexdigest()[:32]
                    db.execute('INSERT INTO chunks VALUES (?,?,?,?,?,?,?)', (chunk_id,doc_id,page['page'],left,right,text,page['origin']))
                    db.execute('INSERT INTO passages VALUES (?,?,?)', (chunk_id,entry['title'],text))
                    pending.append({'id':chunk_id,'doc_id':doc_id,'text':text})
                    if len(pending) >= 24: flush()
            by_hash[entry['sha256']] = updated
            outcome = 'existing_original_ocr_refreshed' if refresh_ocr else 'added_verified_original'
        outcomes.append({'citation':entry['citation'],'title':entry['title'],'url':entry['url'],'sha256':entry['sha256'],
            'document_id':doc_id,'outcome':outcome,'searchable_passages':db.execute('SELECT count(*) FROM chunks WHERE doc_id=?',(doc_id,)).fetchone()[0],
            'previous_document_id':present['id'] if refresh_ocr else None, 'limitations':entry['limitations']})
        db.commit()
        print(entry['citation'], outcome, flush=True)
    flush(); vectors.optimize(); vectors.flush(); del vectors
    stats = Counter(old_manifest['stats'])
    for table, key in [('documents','documents'),('pages','pages'),('chunks','chunks')]:
        stats[key] = db.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
    stats['low_text_pages'] = db.execute('SELECT count(*) FROM pages WHERE length(trim(text))<60').fetchone()[0]
    stats['ocr_pages'] = db.execute("SELECT count(*) FROM pages WHERE origin LIKE 'ocr%'").fetchone()[0]
    stats['corrupt_pages_excluded_from_search'] = db.execute("SELECT count(*) FROM pages WHERE warning LIKE 'Corrupted character extraction%'").fetchone()[0]
    if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise ValueError('SQLite integrity failure')
    db.commit(); db.close()
    if sha(old / 'library.sqlite') != old_database_hash: raise ValueError('Baseline was changed')
    manifest = {**old_manifest, 'generation':new_generation,'created_at':datetime.now(timezone.utc).isoformat(),
        'stats':dict(stats),'previous_generation':generation,'verification_register':str(REGISTER),
        'verification_register_sha256':sha(source_root/REGISTER),'legal_source_refresh':{'added':sum(o['outcome']=='added_verified_original' for o in outcomes),'reconciled':len(outcomes)}}
    (new / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    report = {'generation':new_generation,'previous_generation':generation,'stats':dict(stats),'outcomes':outcomes,
        'old_database_sha256':old_database_hash,'previous_generation_unchanged':True,
        'scope':'All 26 reviewed originals reconciled by bytes; limited passage verification is not a legal currency guarantee.'}
    (output_root / 'legal-source-reconciliation.json').write_text(json.dumps(report, indent=2)+'\n')
    # Publish only after originals, vectors, metadata and the report are complete.
    temporary = index / 'CURRENT.tmp'
    temporary.write_text(json.dumps({'generation':new_generation})+'\n')
    temporary.replace(index / 'CURRENT.json')
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-root', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    result = refresh(args.base_root, args.source_root, args.output_root)
    print(json.dumps({k:v for k,v in result.items() if k!='outcomes'}, indent=2))
