"""Reproduce the rejected selection experiment without a provider or app.

The profiler captures existing candidates for this diagnostic script only.
Runtime code and corpus contents are never changed. Do not import this into the
service. Exit 1 means at least one previously passing check regressed.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
import time
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend.chat import ChatRequest, prepare_answer
from backend.library import Library
from scripts.evaluate_research import CASES
from rejected_selector import revise


def duplicates(hits):
    seen = []
    for hit in hits:
        words = re.findall(r'\w+', hit['text'].lower())
        shingles = set(zip(words, words[1:]))
        if shingles and any(len(shingles & old)/max(len(shingles | old), 1) > .9 for old in seen):
            return True
        seen.append(shingles)
    return False


def score(lib, case, hits, fee_id):
    prepared = prepare_answer(ChatRequest(question=case['question'], answer_style='brief'), hits)
    ids = [hit['id'] for hit in prepared.evidence]
    if 'terms' in case:
        passed = any(any(word in (hit['title']+' '+hit['text']).lower() for word in case['terms']) for hit in hits[:5])
    else:
        positions = [ids.index(i) for i in case['required_any_of'] if i in ids]
        passed = bool(positions)
        if case.get('fee_must_not_outrank_support') and fee_id in ids:
            passed = passed and min(positions) < ids.index(fee_id)
    integrity = True
    links = True
    for hit in hits:
        page = lib.pages(hit['document_id'], hit['generation'], hit['page'], 1)[0]
        integrity &= page['text'][hit['start']:hit['end']] == hit['text']
        qs = parse_qs(urlsplit(hit['reader_url']).query)
        links &= (qs.get('passage') == [hit['id']] and qs.get('page') == [str(hit['page'])]
                  and qs.get('generation') == [hit['generation']])
    return {'passed': bool(passed and integrity and links), 'passage_integrity': integrity,
            'reader_locators_match': links, 'near_duplicate_results': duplicates(hits),
            'input_token_bound': prepared.input_token_bound,
            'results': [{'id': h['id'], 'document_id': h['document_id'], 'title': h['title'],
                         'page': h['page'], 'in_prompt': h['id'] in ids} for h in hits]}


def timing(values):
    return {'median_seconds': statistics.median(values),
            'p95_seconds': sorted(values)[max(0, int(len(values)*.95+.999)-1)],
            'samples': len(values)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.data_root.resolve()
    if any((parent/'snapshot-files.json').exists() for parent in (source, *source.parents)):
        parser.error('This diagnostic opens Zvec. Use a disposable copy, never a preservation snapshot.')
    held_path = Path(__file__).with_name('held-out-cases.json')
    held = json.loads(held_path.read_text())
    original = json.loads((ROOT/'reports/recovery-2026-10-27/retrieval-evidence-cases.json').read_text())
    lib = Library(args.data_root)
    assert lib.generation == held['generation'] == original['generation']
    assert not (args.data_root/'.research-usage').exists()
    fee_id = held['cases'][0]['required_any_of'][0]
    cases = [{**case, 'group': 'development', 'required_any_of': case['required_evidence'][0]['any_of']}
             for case in original['cases']]
    cases += [{**case, 'group': 'held_out'} for case in held['cases']]
    cases += [{'id': f'smoke-{i}', 'question': q, 'terms': terms, 'group': 'smoke'}
              for i, (q, terms) in enumerate(CASES)]
    results = []
    baseline_times, prototype_times, selection_times = [], [], []
    lib.search(cases[0]['question'], 10)  # Warm the encoder/index before timing.
    for case in cases:
        limit = 8 if 'terms' in case else 10
        for _ in range(3):
            start = time.perf_counter()
            lib.search(case['question'], limit)
            baseline_times.append(time.perf_counter()-start)
        captured = {}

        def capture(frame, event, _):
            if event == 'return' and frame.f_code is Library.search.__code__:
                values = frame.f_locals
                captured.update(concepts=sorted(values['query_concepts']),
                                candidates=[{**dict(row), 'meta': meta,
                                             'score': values['relevance'](identifier),
                                             'channels': values['channels'][identifier]}
                                            for identifier, (row, meta) in values['candidates'].items()])

        start = time.perf_counter()
        sys.setprofile(capture)
        try:
            baseline = lib.search(case['question'], limit)
        finally:
            sys.setprofile(None)
        record = {'case': case, 'baseline': baseline, **captured}
        selection_start = time.perf_counter()
        candidate, changes = revise(record)
        selection_times.append(time.perf_counter()-selection_start)
        prototype_times.append(time.perf_counter()-start)
        base_score, candidate_score = score(lib, case, baseline, fee_id), score(lib, case, candidate, fee_id)
        same_slots = [h['document_id'] for h in baseline] == [h['document_id'] for h in candidate]
        assert same_slots and max(Counter(h['document_id'] for h in candidate).values(), default=0) <= 2
        results.append({'id': case['id'], 'group': case['group'], 'question': case['question'],
                        'baseline': base_score, 'candidate': candidate_score, 'changes': changes,
                        'same_document_slots': same_slots})
    counts = {group: {'total': sum(r['group'] == group for r in results),
                      **{mode: sum(r['group'] == group and r[mode]['passed'] for r in results)
                         for mode in ['baseline', 'candidate']}}
              for group in ['development', 'held_out', 'smoke']}
    regressions = [r['id'] for r in results if r['baseline']['passed'] and not r['candidate']['passed']]
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'generation': lib.generation,
              'runtime_library_sha256': hashlib.sha256((ROOT/'backend/library.py').read_bytes()).hexdigest(),
              'heldout_fixture_sha256': hashlib.sha256(held_path.read_bytes()).hexdigest(),
              'summary': counts, 'regressions': regressions, 'candidate_adopted': False,
              'timings': {'normal_baseline': timing(baseline_times),
                          'instrumented_prototype_including_selection': timing(prototype_times),
                          'selection_only': timing(selection_times)},
              'results': results, 'provider_calls': 0,
              'limits': 'Offline diagnostic only. Prototype timing includes profiler capture and is not production latency. Held-out cases were frozen before experimentation and were not used to retune the rejected selector. Search slots, caps, citation slices and real prompt limits are retained. No source changes, app initialization, usage ledger, provider client, deployment or live-answer acceptance.'}
    assert not (args.data_root/'.research-usage').exists()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({key: report[key] for key in ['summary', 'regressions', 'timings']}))
    return 1 if regressions else 0


if __name__ == '__main__':
    sys.exit(main())
