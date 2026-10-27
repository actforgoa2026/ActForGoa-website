"""Synthetic unit inputs only. They do not confer authority on real sources."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import adapter as a
from ..profile import canonical, instant, loads, sha, value_hash


def span(text):
    return {'start': 0, 'end': len(text), 'text': text, 'text_sha256': sha(text.encode())}


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.text = 'Synthetic 🌱 evidence e\u0301.'
        self.block = {'id': 'block-one', 'text': self.text, 'source_date_metadata': None,
                      'origin': 'synthetic-test', 'extra_original_metadata': {'keep': []}}
        self.case = {'id': 'case-one', 'question': 'Synthetic question?',
                     'prepared_evidence': [self.block], 'request_shape': {'effort': 'medium'},
                     'answer': {'paragraphs': [{'text': self.text}]},
                     'final_output_diagnostic': {'answer': {'paragraphs': [{'text': self.text}]}},
                     'human_review': {'status': 'pending', 'claims': [{'original': True}],
                                      'material_omissions': [], 'reviewer': None},
                     'mechanical_passed': True, 'expected_behavior_passed': True,
                     'prompt_sha256': '0' * 64}
        self.capture = {'model': 'synthetic', 'cases': [self.case, deepcopy(self.case)]}
        self.review = {'reviewer': 'Synthetic assistant', 'reviewed_at': '2026-10-27T19:00:00Z',
                       'findings': [{'id': 'synthetic-finding', 'text': 'Attributed opinion'}]}
        self.capture_hash = self.write('capture.json', self.capture)
        self.review_hash = self.write('review.json', self.review)
        self.kinds = {self.capture_hash: 'capture', self.review_hash: 'review'}
        patcher = patch.object(a, 'ARTIFACT_KINDS', self.kinds)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.binding = {'key': 'case:one', 'capture_sha256': self.capture_hash,
                        'pointer': '/cases/0', 'case_id': 'case-one'}
        author = {'name': 'Synthetic annotator', 'role': 'assistant_analyst', 'at': '2026-10-28T00:30:00+05:30'}
        self.annotation = {'id': 'ann:one', 'case_key': 'case:one', 'author': author,
                           'source_review': {'artifact_sha256': self.review_hash, 'finding_pointer': '/findings/0',
                                             'finding_value_sha256': value_hash(self.review['findings'][0]),
                                             'author_pointer': '/reviewer', 'author_value': self.review['reviewer'],
                                             'time_pointer': '/reviewed_at', 'time_value': self.review['reviewed_at']},
                           'target': {'representation': 'raw_diagnostic', 'artifact_sha256': self.capture_hash,
                                      'pointer': '/cases/0/final_output_diagnostic/answer/paragraphs/0/text',
                                      'span': span(self.text)},
                           'evidence': [{'role': 'local_cited_evidence', 'block_pointer': '/cases/0/prepared_evidence/0',
                                         'block_id': 'block-one', 'block_value_sha256': value_hash(self.block),
                                         'selection': {'kind': 'text_span', 'pointer': '/text', 'span': span(self.text)}}],
                           'finding': 'unresolved', 'rationale': 'Synthetic linkage test, no semantic approval.'}
        self.coverage = {'id': 'cov:one', 'case_key': 'case:one', 'question_pointer': '/cases/0/question',
                         'question_span': span(self.case['question']), 'annotation_ids': ['ann:one'],
                         'state': 'reviewed_part', 'rationale': 'Only this synthetic part.'}
        self.input = {'version': a.VERSION,
                      'artifacts': [{'sha256': self.capture_hash, 'path': str(self.directory / 'capture.json')},
                                    {'sha256': self.review_hash, 'path': str(self.directory / 'review.json')}],
                      'sidecar': {'version': a.VERSION, 'cases': [self.binding], 'observations': [],
                                  'annotations': [self.annotation], 'coverage': [self.coverage]}}

    def write(self, name, value):
        raw = canonical(value)
        (self.directory / name).write_bytes(raw)
        return sha(raw)

    def check_error(self, code, path, exit_code=1):
        result, exit_actual = a.link(canonical(self.input))
        self.assertEqual(exit_code, exit_actual)
        self.assertEqual(a.rejected([a.error(code, path)]), result)

    def test_preserves_complete_objects_and_missing_root(self):
        result, code = a.link(canonical(self.input))
        self.assertEqual(0, code)
        self.assertEqual('linked_for_review', result['status'])
        selected = result['selected_cases'][0]
        fields = {x['name']: x['presence'] for x in selected['captured_fields']}
        for name, value in self.case.items():
            self.assertEqual({'state': 'captured', 'value': value, 'value_sha256': value_hash(value)}, fields[name])
        self.assertEqual({'state': 'not_captured'}, selected['capture_observations'][-1]['presence'])
        self.assertEqual({'state': 'not_captured'}, selected['block_context_observations'][0]['presence'])
        self.assertEqual(self.input['sidecar'], result['review_annotations'])
        for key, value in a.SENTINELS.items():
            self.assertEqual(value, result[key])

    def test_missing_null_empty_are_distinct(self):
        for pointer, expected in [('/effort', {'state': 'not_captured'}),
                                  ('/cases/0/prepared_evidence/0/source_date_metadata', {'state': 'captured', 'value': None, 'value_sha256': value_hash(None)}),
                                  ('/cases/0/human_review/material_omissions', {'state': 'captured', 'value': [], 'value_sha256': value_hash([])})]:
            self.input['sidecar']['observations'] = [{'id': 'obs:one', 'case_key': 'case:one', 'pointer': pointer, 'expected': expected}]
            self.assertEqual(0, a.link(canonical(self.input))[1])
            self.input['sidecar']['observations'][0]['expected'] = {'state': 'captured', 'value': '', 'value_sha256': value_hash('')}
            self.check_error('OBSERVATION_MISMATCH', ['sidecar', 'observations', 0, 'expected'])

    def test_unicode_spans_count_codepoints_without_normalizing(self):
        self.annotation['target']['span'] = {'start': 10, 'end': 11, 'text': '🌱', 'text_sha256': sha('🌱'.encode())}
        self.assertEqual(0, a.link(canonical(self.input))[1])
        self.annotation['target']['span']['end'] = 12
        self.check_error('TARGET_SPAN', ['sidecar', 'annotations', 0, 'target', 'span'])

    def test_representation_cannot_be_substituted_for_identical_text(self):
        self.annotation['target']['representation'] = 'normalized'
        self.check_error('TARGET_REPRESENTATION', ['sidecar', 'annotations', 0, 'target'])
        self.annotation['target']['pointer'] = '/cases/0/answer/paragraphs/0/text'
        self.assertEqual(0, a.link(canonical(self.input))[1])

    def test_wrong_case_precedes_bad_span(self):
        self.annotation['target']['pointer'] = '/cases/1/answer/paragraphs/99/text'
        self.annotation['target']['span']['text'] = 'stale'
        self.check_error('TARGET_CASE', ['sidecar', 'annotations', 0, 'target'])

    def test_source_binding_precedes_selection(self):
        self.annotation['evidence'][0]['block_value_sha256'] = '0' * 64
        self.annotation['evidence'][0]['selection']['span']['text'] = 'stale'
        self.check_error('SOURCE_BINDING', ['sidecar', 'annotations', 0, 'evidence', 0])

    def test_source_span_exactness(self):
        self.annotation['evidence'][0]['selection']['span']['text_sha256'] = '0' * 64
        self.check_error('SOURCE_SELECTION', ['sidecar', 'annotations', 0, 'evidence', 0, 'selection'])

    def test_review_identity_cannot_be_reconstructed(self):
        self.annotation['source_review']['author_value'] = 'Human reviewer'
        self.check_error('REVIEW_PROVENANCE', ['sidecar', 'annotations', 0, 'source_review'])

    def test_capture_is_not_a_review(self):
        self.annotation['source_review']['artifact_sha256'] = self.capture_hash
        self.check_error('REVIEW_PROVENANCE', ['sidecar', 'annotations', 0, 'source_review'])

    def test_unrelated_observation_does_not_open_accounting(self):
        self.input['sidecar']['observations'] = [{'id': 'obs:one', 'case_key': 'case:one',
                                                 'pointer': '/accounting', 'expected': {'state': 'not_captured'}}]
        self.check_error('OBSERVATION_POINTER', ['sidecar', 'observations', 0])

    def test_missing_parent_is_not_missing_member(self):
        self.input['sidecar']['observations'] = [{'id': 'obs:one', 'case_key': 'case:one',
                                                 'pointer': '/cases/0/answer/missing/child', 'expected': {'state': 'not_captured'}}]
        self.check_error('OBSERVATION_POINTER', ['sidecar', 'observations', 0])

    def test_duplicate_cases_cannot_alias(self):
        self.input['sidecar']['cases'].append({**self.binding, 'key': 'case:two'})
        self.check_error('DUPLICATE_ID', ['sidecar', 'cases', 1])

    def test_coverage_dangling_reference_and_no_partial_output(self):
        self.coverage['annotation_ids'].append('ann:absent')
        self.check_error('COVERAGE_LINK', ['sidecar', 'coverage', 0])

    def test_first_stage_stops_later_failures(self):
        self.input['artifacts'][0]['sha256'] = 'f' * 64
        self.coverage['annotation_ids'].append('ann:absent')
        self.check_error('UNKNOWN_ARTIFACT', ['artifacts', 0, 'sha256'])

    def test_duplicate_deliveries_reject_before_reads(self):
        self.input['artifacts'].append(deepcopy(self.input['artifacts'][0]))
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('must not read')):
            self.check_error('DUPLICATE_ID', ['artifacts', 2, 'sha256'])

    def test_unreadable_artifact_is_operational(self):
        (self.directory / 'capture.json').unlink()
        self.check_error('IO_FAILURE', ['artifacts', 0, 'path'], 2)

    def test_invalid_date_is_shape_failure(self):
        self.annotation['author']['at'] = '2026-02-30T00:00:00Z'
        self.check_error('INPUT_SHAPE', ['sidecar', 'annotations', 0, 'author', 'at'])

    def test_date_and_shape_errors_share_first_member_order(self):
        self.annotation['author']['at'] = '2026-02-30T00:00:00Z'
        self.annotation['target']['span']['start'] = True
        self.check_error('INPUT_SHAPE', ['sidecar', 'annotations', 0, 'author', 'at'])

    def test_illustration_requires_explicit_same_capture_and_case(self):
        illustration = {'format_version': 'afg-bridge-illustrations-v2',
                        'author': self.annotation['author'], 'status': 'unaccepted_assistant_illustration',
                        'prior_file_sha256': '0' * 64,
                        'cases': [{'case_id': 'case-one', 'capture_sha256': self.capture_hash,
                                   'capture_case_pointer': '/cases/0', 'question': self.case['question'],
                                   'claims': [{'id': 'I1', 'text': self.text}], 'limitations': []}]}
        digest = self.write('illustration.json', illustration)
        self.kinds[digest] = 'illustration'
        self.input['artifacts'].append({'sha256': digest, 'path': str(self.directory / 'illustration.json')})
        self.annotation['target'].update(representation='illustrative', artifact_sha256=digest,
                                         pointer='/cases/0/claims/0/text')
        self.assertEqual(0, a.link(canonical(self.input))[1])
        # A second selected case has equal prose, but cannot borrow this illustration.
        self.binding['pointer'] = '/cases/1'
        self.check_error('TARGET_CASE', ['sidecar', 'annotations', 0, 'target'])

    def test_unlinked_annotations_are_not_implicitly_covered(self):
        self.coverage.update(state='unresolved', annotation_ids=[])
        self.check_error('COVERAGE_LINK', ['sidecar', 'annotations', 0])

    def test_uncovered_selected_case_is_reported(self):
        self.input['sidecar']['cases'].append({**self.binding, 'key': 'case:two', 'pointer': '/cases/1'})
        self.check_error('COVERAGE_LINK', ['sidecar', 'cases', 1])

    def test_missing_review_reports_all_reference_locations(self):
        self.input['artifacts'].pop()
        self.check_error('MISSING_ARTIFACT', ['sidecar', 'annotations', 0, 'source_review', 'artifact_sha256'])

    def test_stale_delivery_is_rejected_before_case_access(self):
        self.input['artifacts'][0]['path'] = str(self.directory / 'review.json')
        self.check_error('ARTIFACT_HASH', ['artifacts', 0, 'sha256'])

    def test_artifact_strict_parse_failure(self):
        raw = b'{"a":1,"a":2}'
        digest = sha(raw)
        (self.directory / 'bad.json').write_bytes(raw)
        self.kinds[digest] = 'review'
        self.input['artifacts'].append({'sha256': digest, 'path': str(self.directory / 'bad.json')})
        self.check_error('ARTIFACT_PARSE', ['artifacts', 2, 'path'])

    def test_id_suffix_and_boolean_integer_rejected(self):
        self.annotation['id'] += '\n'
        self.check_error('INPUT_SHAPE', ['sidecar', 'annotations', 0, 'id'])
        self.annotation['id'] = 'ann:one'
        self.annotation['target']['span']['start'] = True
        self.check_error('INPUT_SHAPE', ['sidecar', 'annotations', 0, 'target', 'span', 'start'])

    def test_error_sort_and_dedup(self):
        errors = [a.error('TARGET_SPAN', ['sidecar', 'annotations', 2]),
                  a.error('TARGET_POINTER', ['sidecar', 'annotations', 0]),
                  a.error('TARGET_SPAN', ['sidecar', 'annotations', 2])]
        self.assertEqual([errors[1], errors[0]], a.rejected(errors)['errors'])


class ProfileTests(unittest.TestCase):
    def test_strict_json(self):
        for raw in [b'\xef\xbb\xbf{}', b'{"a":1,"\\u0061":2}', b'NaN', b'1e999', b'"\\ud800"', b'"\xff"']:
            with self.subTest(raw=raw):
                self.assertEqual(a.rejected([a.error('INPUT_SHAPE', [])]), a.link(raw)[0])

    def test_preserves_json_values(self):
        self.assertEqual({'empty': [], 'null': None, 'number': -2, 'bool': True}, loads(b'{"empty":[],"null":null,"number":-2,"bool":true}'))

    def test_pointer_escaping_and_array_lexing(self):
        self.assertEqual(9, a.resolve({'a/b': {'~': [9]}}, '/a~1b/~0/0'))
        for pointer in ['/a/01', '/a/-', '/a/+0', '/a/9', '/a~2']:
            with self.assertRaises(a.PointerError):
                a.resolve({'a': [9]}, pointer)

    def test_timestamp_requires_real_date_and_offset(self):
        for value in ['2026-10-28', '2026-02-30T00:00:00Z', '2026-10-28T00:00:00', '2026-10-28T24:00:00Z', '2026-10-28T00:00:00+00:60']:
            self.assertFalse(instant(value), value)
        self.assertTrue(instant('2026-10-28T00:30:00.123+05:30'))
