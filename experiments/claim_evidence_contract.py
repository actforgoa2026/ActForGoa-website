"""Offline proposal, deliberately disconnected from every production entry point.

Only standard-library code and supplied dictionaries/JSON files are used. There is
no provider, environment, ledger, Library, SQLite, Zvec or network dependency.
Mechanical validity is never a semantic verdict or release approval.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path
import re

MAX_CLAIM_WORDS = 35  # Superseded short-claim experiment, not an atomicity proof.
PUBLICATION_FIELDS = frozenset({
    'prism.publicationDate', 'citation_online_date',
    'citation_publication_date', 'datePublished',
})
CAPTURES = {
    'sonnet-context-diagnostic2-f954ddf-once.json':
        '39f9a2b4c1276e27c35a08d7c41bc03caa0e58f684cf9d17258269abd0f5fadb',
    'sonnet-high-diagnostic2-2faa6b0-once.json':
        'bb9be999db8253428db92ec0a46f8f3e597fe21a000347b86b3a3ceb7e00f4e9',
}


def normalized(text):
    return ' '.join(text.split())


def locate_excerpt(passage, quote):
    """Find one unique exact span, permitting whitespace differences only.

    Return source-text character offsets; reject ambiguity, case changes,
    punctuation changes, ellipsis insertion, and arbitrary paraphrase.
    """
    if not isinstance(quote, str) or not 1 <= len(quote) <= 600 or not quote.strip():
        return None
    tokens = list(re.finditer(r'\S+', passage))
    body = ' '.join(t.group() for t in tokens)
    wanted = normalized(quote)
    starts = [m.start() for m in re.finditer('(?=' + re.escape(wanted) + ')', body)]
    if len(starts) != 1:
        return None
    # Map normalized string characters back to the unmodified passage.
    positions = []
    for index, token in enumerate(tokens):
        if index:
            positions.append(tokens[index - 1].end())
        positions.extend(range(token.start(), token.end()))
    start = starts[0]
    end = start + len(wanted)
    return {'start': positions[start], 'end': positions[end - 1] + 1}


def publication_year(source):
    """Derive only a source metadata year, never a measurement/legal date.

    Catalogue titles, URLs, retrieval dates and generic dc.date are intentionally
    ignored. Malformed or conflicting recognized fields produce an explicit
    unknown/conflict instead of an invented preferred year.
    """
    rows = source.get('source_date_metadata')
    origins, years, malformed = [], set(), False
    if isinstance(rows, list):
        for row in rows:
            if (not isinstance(row, dict) or not isinstance(row.get('field'), str)
                    or row['field'] not in PUBLICATION_FIELDS):
                continue
            value = row.get('value')
            origins.append({'field': row['field'], 'value': value})
            if not isinstance(value, str) or not re.fullmatch(r'(?:\d{4}|\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2})', value):
                malformed = True
                continue
            try:
                parsed = date.fromisoformat(value.replace('/', '-') if len(value) > 4 else value + '-01-01')
            except ValueError:
                malformed = True
                continue
            years.add(parsed.year)
    if malformed or len(years) > 1:
        state, year, label = 'conflict', None, 'Source publication year unresolved'
    elif years:
        year = next(iter(years))
        state, label = 'metadata', f'Source publication year: {year} (source metadata)'
    else:
        state, year, label = 'unknown', None, 'Source publication year not established'
    return {'state': state, 'year': year, 'label': label, 'basis': origins}


def audit_unit(text, supports, evidence, *, excerpt_only=False):
    """Evaluate a candidate short claim against its own explicit supports.

    In excerpt-only mode reject transformations, including valid paraphrases.
    Even an exact copy may be irrelevant or misleading out of context. No path
    here returns semantic_pass, approved, supported, or permission to publish.
    """
    issues, resolved = [], []
    if not isinstance(text, str) or not text.strip():
        issues.append('empty_claim')
    elif len(text.split()) > MAX_CLAIM_WORDS:
        issues.append('claim_word_limit')
    if not isinstance(supports, list) or not 1 <= len(supports) <= 10:
        issues.append('support_count')
        supports = []
    for support in supports:
        if not isinstance(support, dict) or set(support) != {'citation_id', 'quote'}:
            issues.append('support_shape')
            continue
        identifier = support['citation_id']
        if not isinstance(identifier, str) or identifier not in evidence:
            issues.append('unknown_citation')
            continue
        source = evidence[identifier]
        span = locate_excerpt(source['text'], support['quote'])
        if span is None:
            issues.append('unresolved_excerpt')
            continue
        resolved.append({'citation_id': identifier, 'span': span,
                         'quote': source['text'][span['start']:span['end']],
                         'publication': publication_year(source)})
    resolved_ids = {item['citation_id'] for item in resolved}
    for identifier in resolved_ids:
        if any(context not in resolved_ids for context in evidence[identifier].get('context_ids', [])):
            issues.append('missing_own_context')
    if excerpt_only and (not resolved or not isinstance(text, str)
                         or normalized(text) != normalized(resolved[0]['quote'])):
        issues.append('non_extractive_transformation')
    return {'mechanical': 'reject' if issues else 'valid',
            'issues': sorted(set(issues)), 'resolved': resolved,
            'semantic': 'not_assessed', 'release': 'hold'}


def audit_selection(payload, evidence):
    """Smaller candidate: the model selects IDs, the server supplies whole text.

    Full transitive required context accompanies each selected passage. Text is
    neither normalized nor truncated. Mechanical identity does not establish
    relevance, context completeness across chunks, or semantic correctness.
    """
    result = {'mechanical': 'reject', 'issues': [], 'units': [],
              'semantic': 'not_assessed', 'release': 'hold'}
    if not isinstance(payload, dict) or set(payload) != {'status', 'passage_ids'}:
        result['issues'] = ['selection_shape']
        return result
    status, selected = payload['status'], payload['passage_ids']
    if (status not in ('selected', 'insufficient_evidence') or not isinstance(selected, list)
            or any(not isinstance(identifier, str) for identifier in selected)):
        result['issues'] = ['selection_shape']
        return result
    if bool(selected) != (status == 'selected'):
        result['issues'] = ['selection_status_mismatch']
        return result
    if len(selected) != len(set(selected)) or any(identifier not in evidence for identifier in selected):
        result['issues'] = ['duplicate_or_unknown_selection']
        return result

    def context_closure(identifier, trail):
        if identifier in trail:
            raise ValueError('context_cycle')
        if identifier not in evidence:
            raise ValueError('unknown_context')
        item = evidence[identifier]
        if not isinstance(item.get('text'), str) or not item['text'].strip():
            raise ValueError('missing_source_text')
        if (not isinstance(item.get('document_id'), str) or not item['document_id']
                or not isinstance(item.get('generation'), str) or not item['generation']
                or type(item.get('page')) is not int or item['page'] < 1):
            raise ValueError('invalid_source_provenance')
        dependencies = item.get('context_ids', [])
        if not isinstance(dependencies, list) or any(not isinstance(dep, str) for dep in dependencies):
            raise ValueError('invalid_context_ids')
        ordered = []
        for dependency in dependencies:
            if dependency not in evidence:
                raise ValueError('unknown_context')
            if any(evidence[dependency].get(field) != item[field]
                   for field in ('document_id', 'generation', 'page')):
                raise ValueError('context_provenance_mismatch')
            for context in [*context_closure(dependency, trail | {identifier}), dependency]:
                if context not in ordered:
                    ordered.append(context)
        return ordered

    def present(identifier):
        source = evidence[identifier]
        return {'passage_id': identifier, 'text': source['text'],
                # Preserve supplied scope context separately from verbatim text
                # and catalogue titles; never infer or rewrite the heading.
                'source_section': {'label': 'Source section / scope metadata',
                                   'page_heading': deepcopy(source.get('page_heading'))},
                'provenance': {field: deepcopy(source[field]) for field in (
                    'document_id', 'generation', 'page', 'label', 'start', 'end',
                    'reader_url', 'url', 'title', 'retrieved_at', 'source_date_metadata') if field in source},
                'publication': publication_year(source),
                'limitations': {field: deepcopy(source[field]) for field in (
                    'warning', 'legal_currency', 'guide_verification') if field in source}}

    try:
        for identifier in selected:
            context_ids = context_closure(identifier, set())
            result['units'].append({'passage': present(identifier),
                                    'required_context': [present(context) for context in context_ids]})
    except ValueError as error:
        result['issues'] = [str(error)]
        result['units'] = []  # No partial acceptance or quiet salvage.
        return result
    result['mechanical'] = 'valid'
    return result


def reviewer_counterexamples():
    """Preserve LAW's two falsifications of arbitrary substring copying."""
    common = {'document_id': 'synthetic-document', 'generation': 'synthetic-generation', 'page': 1}
    eligibility = {'eligibility': {**common, 'text': 'The applicant is ineligible for support.'}}
    quote = 'eligible for support'
    prefix = audit_unit(quote, [{'citation_id': 'eligibility', 'quote': quote}],
                        eligibility, excerpt_only=True)
    table = {'row': {**common, 'text': 'Bird A   Region A', 'context_ids': ['header']},
             'header': {**common, 'text': 'Species   Endemic to'}}
    partial_header = audit_unit('Bird A   Region A', [
        {'citation_id': 'row', 'quote': 'Bird A   Region A'},
        {'citation_id': 'header', 'quote': 'Species'},
    ], table, excerpt_only=True)
    if prefix['mechanical'] != 'valid' or partial_header['mechanical'] != 'valid':
        raise ValueError('Reviewer falsification no longer reproduced')
    return [
        {'review_label': 'word_prefix_removed', 'synthetic': True, 'excerpt_only': prefix,
         'selection_only': audit_selection({'status': 'selected', 'passage_ids': ['eligibility']}, eligibility)},
        {'review_label': 'header_meaning_omitted', 'synthetic': True, 'excerpt_only': partial_header,
         'selection_only': audit_selection({'status': 'selected', 'passage_ids': ['row']}, table)},
    ]


def read_capture(path, expected_hash):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError('Captured report hash mismatch')
    return json.loads(raw)


def replay(directory):
    """Replay immutable historical output; never regenerate or salvage it."""
    packets, counterexamples = [], []
    for name, sha in CAPTURES.items():
        report = read_capture(directory / name, sha)
        cases = []
        for case in report['cases']:
            evidence = {e['id']: e for e in case['prepared_evidence']}
            payload = case['final_output_diagnostic']['answer']
            units = payload.get('paragraphs', [payload.get('paragraph')])
            output = []
            for number, unit in enumerate(units, 1):
                supports = [unit['primary_support'], *unit['supports']]
                # Warnings and legal/date metadata become app-owned fields in
                # this proposal. They are not factual text support here.
                text_supports = [{k: s[k] for k in ('citation_id', 'quote')}
                                 for s in supports if s['field'] == 'text']
                baseline = audit_unit(unit['text'], text_supports, evidence)
                extractive = audit_unit(unit['text'], text_supports, evidence, excerpt_only=True)
                output.append({'unit': number, 'word_count': len(unit['text'].split()),
                               'candidate': baseline, 'excerpt_only': extractive})
                if name == 'sonnet-high-diagnostic2-2faa6b0-once.json' and case['id'] == 'scope-01' and number == 3:
                    # Historical, independently reviewed failures. Slice actual
                    # output, do not manufacture a corrected answer or rerun it.
                    text = unit['text']
                    begin = text.index('In sum,')
                    examples = [
                        ('quantifier_scope_reversal', 0, text.index('.') + 1),
                        ('misplaced_india_range_citation', begin, text.index('.', begin) + 1),
                    ]
                    for label, left, right in examples:
                        claim = text[left:right]
                        paired = audit_unit(claim, text_supports, evidence)
                        copied = audit_unit(claim, text_supports, evidence, excerpt_only=True)
                        if paired['mechanical'] != 'valid' or 'non_extractive_transformation' not in copied['issues']:
                            raise ValueError('Counterexample no longer reproduces its declared mechanical outcome')
                        counterexamples.append({'historical_review_label': label,
                            'capture': name, 'case': case['id'], 'unit': number,
                            'claim_offsets_in_original_unit': [left, right], 'claim': claim,
                            'short_pairing_catches_failure': False,
                            'copy_only_rejects_transformation': True,
                            'candidate': paired, 'excerpt_only': copied})
            cases.append({'id': case['id'],
                          'historical_mechanical_passed': case['mechanical_passed'],
                          'units': output,
                          'selection_assembly_fixture': {
                              'selection_origin': 'deduplicated_historical_primary_support_ids_not_new_model_output',
                              'result': audit_selection({'status': 'selected', 'passage_ids': list(dict.fromkeys(
                                  unit['primary_support']['citation_id'] for unit in units))}, evidence)}})
        packets.append({'capture': name, 'sha256': sha, 'cases': cases})
    return {'proposal_only': True, 'provider_calls': 0,
            'semantic_acceptance': 'not_assessed', 'release': 'hold',
            'counterexamples': counterexamples, 'reviewer_counterexamples': reviewer_counterexamples(),
            'packets': packets}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captured-report-directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.captured_report_directory)
    # Never overwrite prior evidence or append to an existing packet.
    with args.output.open('x', encoding='utf-8') as output:
        args.output.chmod(0o600)
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print(json.dumps({'output': str(args.output), 'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'provider_calls': 0, 'semantic_acceptance': 'not_assessed', 'release': 'hold'}))


if __name__ == '__main__':
    main()
