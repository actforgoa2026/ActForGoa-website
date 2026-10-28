"""Synthetic development probes, never the historical acceptance set."""
import unittest
from claim_review_candidate import FACETS, Span, check, review


class ClaimReviewTests(unittest.TestCase):
    def pack(self, texts):
        # Synthetic spans deliberately keep originals as independent passages.
        return {'passages': {str(i): text for i, text in enumerate(texts)},
                'spans': [Span(str(i), str(i), 0, len(text), ('0',) if i else ())
                          for i, text in enumerate(texts)]}

    def claim(self, text, ids):
        return {'text': text, 'supports': ids, 'facets': {f: list(ids) for f in FACETS}}

    def test_explicit_context_is_required_without_expansion(self):
        pack = self.pack(['Bachbhatt lake is in Salcete.', 'The lake requires protection.'])
        claim = self.claim('Bachbhatt lake requires protection.', ['1'])
        with self.assertRaisesRegex(ValueError, 'incomplete explicit'):
            check(pack, [claim])
        self.assertEqual(claim['supports'], ['1'])
        self.assertEqual(check(pack, [self.claim(claim['text'], ['0', '1'])])['semantic'], 'not_assessed')

    def test_complete_evidence_does_not_prove_paraphrase(self):
        probes = [
            (['Design must comply with the conditions.', 'Details are in Annexure A.'],
             'Design details are unavailable.', 'modality'),
            (['Survey of avian diversity, 2019.', '104 species were recorded; 16 were endemic. The denominator is unclear.'],
             '16 of 104 birds in Goa are endemic today.', 'population'),
            (['Fee type | Copies | Application', 'Charge | 10 | 0'],
             'The application fee is 10.', 'measure'),
            (['Only eligible residents may apply.', 'Approval is required before work starts.'],
             'Anyone can start work and apply later.', 'conditions'),
        ]
        for texts, wording, failed_facet in probes:
            with self.subTest(wording=wording):
                result = check(self.pack(texts), [self.claim(wording, ['0', '1'])])
                self.assertEqual(result['mechanical'], 'valid')
                self.assertEqual(result['semantic'], 'not_assessed')
                entries = [{'claim': 0, 'facet': f,
                            'verdict': 'failed' if f == failed_facet else 'unresolved',
                            'reason': 'Synthetic counterexample requires source-to-wording review.'}
                           for f in FACETS]
                assessed = review(result, {'sha256': result['sha256'], 'claim_count': 1, 'entries': entries})
                self.assertEqual(assessed['facet_review'], 'rejected_or_unresolved')
                self.assertEqual(assessed['semantic'], 'not_assessed')
                self.assertEqual(assessed['release'], 'hold')

    def test_positive_conversational_control(self):
        result = check(self.pack(['Approval is required before work starts.']),
                       [self.claim('You need approval before starting work.', ['0'])])
        self.assertEqual(result['mechanical'], 'valid')
        self.assertEqual(result['semantic'], 'not_assessed')

    def test_header_alone_does_not_select_rows(self):
        pack = self.pack(['Population | Total | Endemic', 'Survey area | 104 | 16'])
        # Dependency direction must be supplied correctly by source review.
        pack['spans'][0] = Span('0', '0', 0, len(pack['passages']['0']), ('1',))
        pack['spans'][1] = Span('1', '1', 0, len(pack['passages']['1']))
        with self.assertRaisesRegex(ValueError, 'incomplete explicit'):
            check(pack, [self.claim('16 were endemic.', ['0'])])

    def test_stale_or_incomplete_review_is_rejected(self):
        pack = self.pack(['Approval is required before work starts.'])
        result = check(pack, [self.claim('You need approval first.', ['0'])])
        entries = [{'claim': 0, 'facet': f, 'verdict': 'preserved',
                    'reason': 'Explicit synthetic review fixture.'} for f in FACETS]
        decision = {'sha256': result['sha256'], 'claim_count': 1, 'entries': entries}
        self.assertEqual(review(result, decision)['release'], 'hold')
        changed = check(pack, [self.claim('Approval is optional.', ['0'])])
        with self.assertRaisesRegex(ValueError, 'stale review'):
            review(changed, decision)
        decision['entries'] = entries[:-1]
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            review(result, decision)

    def test_question_and_provenance_changes_invalidate_review(self):
        pack = self.pack(['Approval is required.'])
        pack.update(question='What is required?', provenance={'generation': 'old'})
        claim = self.claim('You need approval.', ['0'])
        original = check(pack, [claim])['sha256']
        pack['question'] = 'Is approval optional?'
        self.assertNotEqual(original, check(pack, [claim])['sha256'])
        pack['question'] = 'What is required?'
        pack['provenance']['generation'] = 'new'
        self.assertNotEqual(original, check(pack, [claim])['sha256'])

    def test_support_limits_fail_without_truncation_or_bundling(self):
        pack = self.pack(['a' * 601])
        with self.assertRaisesRegex(ValueError, 'quote allowance'):
            check(pack, [self.claim('A long source.', ['0'])])
        self.assertEqual(len(pack['passages']['0']), 601)
        pack = self.pack(['A'] * 11)
        with self.assertRaisesRegex(ValueError, 'explicit supports'):
            check(pack, [self.claim('Eleven supports.', [str(i) for i in range(11)])])

    def test_cycles_and_invalid_offsets_fail(self):
        pack = self.pack(['A', 'B'])
        pack['spans'][0] = Span('0', '0', 0, 1, ('1',))
        with self.assertRaisesRegex(ValueError, 'cycle'):
            check(pack, [self.claim('A', ['0', '1'])])
        pack['spans'][0] = Span('0', '0', 0, 2)
        with self.assertRaisesRegex(ValueError, 'span'):
            check(pack, [self.claim('A', ['0', '1'])])


if __name__ == '__main__':
    unittest.main()
