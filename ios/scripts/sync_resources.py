#!/usr/bin/env python3
"""Bundle the canonical web files without maintaining a second catalogue or model."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'ios/ActForGoa/Content'

def sync():
    records = json.loads((ROOT / 'public/data/catalog.json').read_text())
    index = json.loads((ROOT / 'public/data/vector-index.json').read_text())
    ids = {r['id'] for r in records}
    assert len(ids) == len(records), 'Duplicate record IDs'
    assert set(index['ids']) <= ids, 'Search index contains unknown records'
    assert index['records'] == len(records), 'Rebuild the web semantic index before shipping'
    assert (ROOT / 'public/data/vectors.bin').stat().st_size == len(index['ids']) * index['dimensions'] * 4
    manifest = {}
    sources = [p for directory in ['data', 'models', 'assets'] for p in (ROOT / 'public' / directory).rglob('*') if p.is_file()]
    sources.extend([ROOT / 'shared/search-config.json', ROOT / 'shared/onnxruntime-LICENSE'])
    expected = set()
    for src in sources:
        rel = src.relative_to(ROOT / 'public') if src.is_relative_to(ROOT / 'public') else Path(src.name)
        dest = DEST / rel
        expected.add(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        manifest[str(rel)] = digest
        if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest() != digest:
            shutil.copy2(src, dest)
    # Only delete stale generated files within this script's owned destination.
    for path in DEST.rglob('*'):
        if path.is_file() and path not in expected and path.name != 'manifest.json':
            path.unlink()
    (DEST / 'manifest.json').write_text(json.dumps({'records': len(records), 'files': manifest}, indent=2) + '\n')
    print(f'Bundled {len(records)} records and {len(sources)} canonical web assets.')

if __name__ == '__main__':
    sync()
