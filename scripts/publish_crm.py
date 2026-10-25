"""Build the browser CRM snapshot from the versioned research release."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/releases/2026-10-23'
records = []
for filename, collection in [('community_directory.csv', 'community'), ('government_directory.csv', 'government')]:
    with (SOURCE / filename).open(encoding='utf-8-sig', newline='') as stream:
        records.extend(dict(row, collection=collection) for row in csv.DictReader(stream))
with (SOURCE / 'opportunities.csv').open(encoding='utf-8-sig', newline='') as stream:
    opportunities = list(csv.DictReader(stream))
ids = {r['record_id'] for r in records}
assert len(ids) == len(records) == 3267
assert all(i in ids for r in opportunities for i in r['related_record_ids'].split(' | ') if i)
output = ROOT / 'public/data/crm.json'
output.write_text(json.dumps({'version': 'directory-2026-10-23', 'records': records, 'opportunities': opportunities}, ensure_ascii=False, separators=(',', ':')))
print(f'Published {len(records)} CRM records and {len(opportunities)} linked participation routes')
