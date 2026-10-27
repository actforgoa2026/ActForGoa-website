"""Capture known regressions and source text; never evaluates a new candidate."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.evaluate_research_copy import is_preserved

p = argparse.ArgumentParser()
p.add_argument('--data-root', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
if is_preserved(a.data_root) or is_preserved(a.output):
    p.error('Use the disposable-copy wrapper')
from backend.library import Library

library = Library(a.data_root)
original = json.loads((ROOT/'reports/recovery-2026-10-27/retrieval-evidence-cases.json').read_text())
prior = json.loads((ROOT/'reports/rti-offline-2026-10-27/held-out-cases.json').read_text())
cases = [{**case, 'required_any_of': case['required_evidence'][0]['any_of']} for case in original['cases']] + prior['cases']
results = []
for case in cases:
    captured = {}

    def capture(frame, event, _):
        if event == 'return' and frame.f_code is Library.search.__code__:
            v = frame.f_locals
            captured.update(terms=v['terms'], concepts=sorted(v['query_concepts']), candidates=[
                {**dict(row), 'meta': meta, 'score': v['relevance'](identifier), 'rrf': v['scores'][identifier],
                 'channels': v['channels'][identifier]}
                for identifier, (row, meta) in v['candidates'].items()])

    sys.setprofile(capture)
    try:
        hits = library.search(case['question'], 10)
    finally:
        sys.setprofile(None)
    results.append({'case': case, 'hits': hits, **captured})
with library.connect() as db:
    expected = {i for c in cases for i in c['required_any_of']}
    doc_ids = {db.execute('SELECT doc_id FROM chunks WHERE id=?', (i,)).fetchone()[0] for i in expected}
    documents = []
    for doc_id in sorted(doc_ids):
        meta = library.document(doc_id, private=True)
        rows = [dict(r) for r in db.execute('SELECT * FROM chunks WHERE doc_id=? ORDER BY page,start', (doc_id,))]
        documents.append({'metadata': meta, 'chunks': rows})
a.output.write_text(json.dumps({'known_cases': results, 'source_documents': documents}, indent=2)+'\n')
print(json.dumps({'known_cases': len(results), 'source_documents': len(documents)}))
