"""Add canonical authored guides to research metadata without claiming primary law.

This does not download official documents or replace an existing corpus. Existing
original bytes and generations remain intact. Rebuild the index separately.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.embeddings import ROOT

GUIDES = {
    'REPORTING_GUIDE_DRAFT.md': ('reporting', 'Report a civic or environmental problem', ['legal']),
    'BUILDING_GUIDE_DRAFT.md': ('building', 'Plan building or repair work', ['legal']),
    'FARMING_GUIDE_DRAFT.md': ('farming', 'Start or sustain farming', ['legal', 'ecology']),
    'ANIMAL_WELFARE_GUIDE_DRAFT.md': ('animal-welfare', 'Help animals and report cruelty', ['legal', 'ecology']),
    'ENVIRONMENTAL_PROTECTION_GUIDE_DRAFT.md': ('environmental-protection', 'Protect the environment', ['legal', 'ecology']),
}
LIMITATION = 'ActForGoa authored draft guide, not primary legislation or verified consolidated current law. Check the cited official source and the guide verification register before acting.'


def ingest(data_root=ROOT, guide_root=None):
    data_root = Path(data_root).resolve()
    guide_root = Path(guide_root or ROOT / 'corpus/guides').resolve()
    # Validate every input before writing anything; never quietly ingest an empty library.
    sources = [(filename, details, (guide_root / filename).read_bytes()) for filename, details in GUIDES.items()]
    for folder in ('raw', 'metadata'):
        (data_root / 'corpus' / folder).mkdir(parents=True, exist_ok=True)
    outcomes = []
    for filename, (slug, title, domains), raw in sources:
        raw.decode('utf-8')
        digest = hashlib.sha256(raw).hexdigest()
        url = f'https://actforgoa-field-guide.vercel.app/read/guide-{slug}'
        identifier = hashlib.sha256(url.encode()).hexdigest()[:24]
        relative = f'corpus/raw/{digest}.md'
        destination = data_root / relative
        if destination.exists() and destination.read_bytes() != raw:
            raise ValueError('Existing guide bytes conflict with their checksum')
        destination.write_bytes(raw)
        metadata = {'id': identifier, 'url': url, 'title': title, 'status': 'authored',
            'sha256': digest, 'raw_path': relative, 'text_path': relative, 'format': 'markdown',
            'publisher_class': 'actforgoa_authored_guide', 'domains': domains,
            'document_kind_hint': 'authored_draft_guide', 'legal_currency': LIMITATION,
            'source_date_metadata': {'date_caution': 'Draft guide snapshot. Snapshot date is not the publication or commencement date of its cited laws.'},
            'guide_verification': {'limitations': LIMITATION, 'source_file': filename},
            'snapshot_at': datetime.now(timezone.utc).isoformat(), 'rights_status': 'ActForGoa authored guide; cited sources retain their own rights.'}
        path = data_root / 'corpus/metadata' / f'{identifier}.json'
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(path)
        outcomes.append({'id': identifier, 'title': title, 'sha256': digest, 'domains': domains})
    return {'guides': outcomes, 'count': len(outcomes), 'scope': LIMITATION}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=ROOT)
    parser.add_argument('--guide-root', type=Path)
    args = parser.parse_args()
    print(json.dumps(ingest(args.data_root, args.guide_root), indent=2))
