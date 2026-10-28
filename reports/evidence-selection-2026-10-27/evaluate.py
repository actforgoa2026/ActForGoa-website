"""One paired assessment, without a provider, app or genuine usage ledger."""
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
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scripts.evaluate_research_copy import is_preserved


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def assess(library, case, hits):
    from backend.chat import ChatRequest, prepare_answer, MAX_PROMPT_BYTES, FRAMING_TOKEN_ALLOWANCE
    prepared = prepare_answer(ChatRequest(question=case['question'], answer_style='brief'), hits) if hits else None
    ids = [h['id'] for h in prepared.evidence] if prepared else []
    if 'terms' in case:
        support = any(any(t in (h['title']+' '+h['text']).lower() for t in case['terms']) for h in hits[:5])
    else:
        support = all(set(group['any_of']).intersection(ids) for group in case['required_evidence'])
    if case.get('fee_must_not_outrank_support'):
        fee = case['fee_id']
        wanted = case['required_evidence'][0]['any_of']
        positions = [ids.index(i) for i in wanted if i in ids]
        support = support and bool(positions) and (fee not in ids or min(positions) < ids.index(fee))
    integrity, locators, seen, duplicates = True, True, [], False
    for hit in hits:
        page = library.pages(hit['document_id'], hit['generation'], hit['page'], 1)[0]
        integrity &= page['text'][hit['start']:hit['end']] == hit['text']
        qs = parse_qs(urlsplit(hit['reader_url']).query)
        locators &= (qs.get('generation') == [hit['generation']] and qs.get('page') == [str(hit['page'])]
                     and qs.get('passage') == [hit['id']]
                     and urlsplit(hit['reader_url']).path == '/documents/'+hit['document_id'])
        tokens = re.findall(r'\w+', hit['text'].lower())
        shingles = set(zip(tokens, tokens[1:]))
        duplicates |= bool(shingles) and any(len(shingles & s)/max(len(shingles | s), 1) > .9 for s in seen)
        seen.append(shingles)
    size = len(json.dumps(prepared.messages, ensure_ascii=False, separators=(',', ':')).encode()) if prepared else 0
    budget = bool(prepared) and size <= MAX_PROMPT_BYTES and prepared.input_token_bound == size+FRAMING_TOKEN_ALLOWANCE
    cap = max(Counter(h['document_id'] for h in hits).values(), default=0) <= 2
    schema_ok = bool(prepared) and prepared.schema['properties']['paragraphs']['items']['properties']['citations']['items']['enum'] == ids
    safeguards = integrity and locators and not duplicates and budget and cap and schema_ok
    return {'passed': bool(support and safeguards), 'support_in_prompt': bool(support),
            'passage_integrity': integrity, 'reader_locators_match': locators, 'near_duplicates': duplicates,
            'two_passage_cap': cap, 'prompt_budget_passed': budget, 'schema_ids_match': schema_ok,
            'prompt_bytes': size, 'input_token_bound': prepared.input_token_bound if prepared else 0,
            'safeguards_passed': safeguards,
            'results': [{'id': h['id'], 'document_id': h['document_id'], 'title': h['title'],
                         'page': h['page'], 'in_prompt': h['id'] in ids} for h in hits]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if is_preserved(args.data_root) or is_preserved(args.output):
        parser.error('Use the disposable-copy wrapper')
    if args.output.exists():
        parser.error('Keep the first assessment; choose a new task before another candidate')
    from backend.library import Library
    from scripts.evaluate_research import CASES
    import pymupdf
    from candidate import revise

    freeze = json.loads((HERE/'freeze.json').read_text())
    plan = json.loads((HERE/'assessment-plan.json').read_text())
    assert sha(HERE/'frozen-cases.json') == freeze['sha256'] == plan['frozen_sha256']
    assert sha(HERE/'candidate.py') == plan['candidate_sha256']
    assert sha(ROOT/'backend/library.py') == plan['baseline_library_sha256']
    original = json.loads((ROOT/'reports/recovery-2026-10-27/retrieval-evidence-cases.json').read_text())
    prior = json.loads((ROOT/'reports/rti-offline-2026-10-27/held-out-cases.json').read_text())
    frozen = json.loads((HERE/'frozen-cases.json').read_text())
    cases = [{**c, 'group': 'known_original'} for c in original['cases']]
    fee_id = prior['cases'][0]['required_any_of'][0]
    cases += [{**c, 'group': 'known_prior', 'fee_id': fee_id,
               'required_evidence': [{'name': 'Previously reviewed support', 'any_of': c['required_any_of']}]}
              for c in prior['cases']]
    cases += [{**c, 'group': 'frozen'} for c in frozen['cases']]
    cases += [{'id': f'smoke-{i}', 'question': q, 'terms': terms, 'group': 'smoke'} for i, (q, terms) in enumerate(CASES)]
    library = Library(args.data_root)
    assert library.generation == original['generation'] == prior['generation'] == frozen['generation']
    expected = {pid for c in cases for g in c.get('required_evidence', []) for pid in g['any_of']}
    readers = {}
    with library.connect() as db:
        for pid in sorted(expected):
            row = db.execute('SELECT * FROM chunks WHERE id=?', (pid,)).fetchone()
            assert row is not None
            page = library.pages(row['doc_id'], start=row['page'], limit=1)[0]
            assert page['text'][row['start']:row['end']] == row['text']
            if row['doc_id'] not in readers:
                path, meta = library.original(row['doc_id'])
                assert sha(path) == meta['sha256']
                pages = library.pages(row['doc_id'], start=1, limit=meta['page_count'])
                assert len(pages) == meta['page_count'] and pages[-1]['page'] == meta['page_count']
                with pymupdf.open(path) as pdf:
                    assert len(pdf) == meta['page_count']
                    pdf[-1].get_pixmap(matrix=pymupdf.Matrix(.25, .25))
                readers[row['doc_id']] = {'title': meta['title'], 'pages': len(pages),
                    'original_sha256': meta['sha256'], 'full_text_and_final_original_page': True}
        for case in frozen['cases']:
            for locator in case['source_review']:
                row = db.execute('SELECT * FROM chunks WHERE id=?', (locator['passage_id'],)).fetchone()
                assert row['doc_id'] == locator['document_id'] and row['page'] == locator['page']
                assert row['start'] == locator['start'] and row['end'] == locator['end']
                assert row['text'] == locator['reviewed_text']
                assert hashlib.sha256(row['text'].encode()).hexdigest() == locator['text_sha256']
                assert readers[row['doc_id']]['original_sha256'] == locator['original_sha256']
    results = []
    for case in cases:
        captured = {}

        def capture(frame, event, _):
            if event == 'return' and frame.f_code is Library.search.__code__:
                v = frame.f_locals
                captured.update(terms=v['terms'], generation=v['generation'], candidates=[
                    {**dict(row), 'meta': meta, 'rrf': v['scores'][identifier],
                     'baseline_score': v['relevance'](identifier), 'channels': v['channels'][identifier]}
                    for identifier, (row, meta) in v['candidates'].items()])

        limit = 8 if case['group'] == 'smoke' else 10
        start = time.perf_counter()
        sys.setprofile(capture)
        try:
            baseline = library.search(case['question'], limit)
        finally:
            sys.setprofile(None)
        baseline_seconds = time.perf_counter()-start
        start = time.perf_counter()
        candidate, ranking = revise(captured, limit)
        candidate_seconds = time.perf_counter()-start
        base_result = assess(library, case, baseline)
        candidate_result = assess(library, case, candidate)
        expected_ids = {i for g in case.get('required_evidence', []) for i in g['any_of']}
        details = []
        ordered = sorted(captured['candidates'], key=lambda r: ranking['scores'].get(r['id'], 0), reverse=True)
        for rank, row in enumerate(ordered, 1):
            if row['id'] in expected_ids or row['id'] in {h['id'] for h in candidate}:
                details.append({'id': row['id'], 'document_id': row['doc_id'], 'page': row['page'],
                    'expected': row['id'] in expected_ids, 'candidate_rank_before_caps': rank,
                    'baseline_score': row['baseline_score'], 'rrf': row['rrf'],
                    'candidate_score': ranking['scores'][row['id']], 'lexical': ranking['lexical'][row['id']]})
        results.append({'id': case['id'], 'group': case['group'], 'question': case['question'],
                        'baseline': base_result, 'candidate': candidate_result, 'ranking_diagnosis': details,
                        'instrumented_baseline_seconds': baseline_seconds,
                        'candidate_selection_seconds': candidate_seconds})
    groups = ['known_original', 'known_prior', 'frozen', 'smoke']
    summary = {g: {'total': sum(r['group'] == g for r in results),
                  **{m: sum(r['group'] == g and r[m]['passed'] for r in results) for m in ['baseline', 'candidate']}}
               for g in groups}
    regressions = [r['id'] for r in results if r['baseline']['passed'] and not r['candidate']['passed']]
    candidate_failures = [r['id'] for r in results if not r['candidate']['passed']]
    safeguards = all(r[m]['safeguards_passed'] for r in results for m in ['baseline', 'candidate'])
    accepted = (summary['known_original']['candidate'] == 9 and not regressions and safeguards
                and summary['smoke']['candidate'] == len(CASES))
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'generation': library.generation,
              'candidate_sha256': plan['candidate_sha256'], 'frozen_fixture_sha256': freeze['sha256'],
              'baseline_library_sha256': plan['baseline_library_sha256'], 'candidate_assessments': 1,
              'summary': summary, 'regressions': regressions, 'candidate_failures': candidate_failures,
              'all_safeguards_passed': safeguards, 'repair_gate_passed': accepted, 'runtime_adopted': False,
              'full_document_checks': readers, 'provider_calls': 0, 'genuine_usage_operations': 0,
              'results': results,
              'limits': 'One predetermined candidate. Original and prior held-out cases are now known evidence. New frozen cases were never tuned on. Source recall and exact citation integrity are not answer entailment or legal currency; no production latency or live readiness claim.'}
    assert not (args.data_root/'.research-usage').exists()
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['summary', 'regressions', 'candidate_failures', 'all_safeguards_passed', 'repair_gate_passed']}))
    return 0 if accepted else 1


if __name__ == '__main__':
    sys.exit(main())
