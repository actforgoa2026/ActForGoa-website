"""Falsification cases for a proposal, not production acceptance tests."""
from pathlib import Path
import tempfile
import unittest

from claim_evidence_contract import audit_unit, locate_excerpt, publication_year, read_capture


def source(text, **extra):
    return {'text': text, **extra}


def support(identifier, quote):
    return {'citation_id': identifier, 'quote': quote}


class MechanicalDoesNotMeanEntailed(unittest.TestCase):
    def test_atomic_exact_pair_still_allows_quantifier_reversal(self):
        quote = 'Most of these herbaceous endemics occur on rocky outcrops.'
        evidence = {'plants': source(quote)}
        claim = 'Most regional endemics are herbaceous plants of rocky outcrops.'
        result = audit_unit(claim, [support('plants', quote)], evidence)
        self.assertEqual(result['mechanical'], 'valid')  # Known false implication.
        self.assertEqual(result['semantic'], 'not_assessed')
        self.assertEqual(result['release'], 'hold')
        strict = audit_unit(claim, [support('plants', quote)], evidence, excerpt_only=True)
        self.assertIn('non_extractive_transformation', strict['issues'])

    def test_short_misplaced_citation_still_passes_pairing(self):
        evidence = {'plants': source('These plants are endemic to Region A.'),
                    'birds': source('These birds are endemic to Country B.')}
        claim = 'The sources classify endemism by Region A or Country B.'
        own = [support('plants', evidence['plants']['text'])]
        result = audit_unit(claim, own, evidence)
        self.assertEqual(result['mechanical'], 'valid')
        self.assertEqual([r['citation_id'] for r in result['resolved']], ['plants'])
        self.assertEqual(result['release'], 'hold')
        self.assertIn('non_extractive_transformation',
                      audit_unit(claim, own, evidence, excerpt_only=True)['issues'])

    def test_other_semantic_failures_defeat_short_quote_pairing(self):
        pairs = [
            ('The survey did not establish a causal link.', 'The survey established a causal link.'),
            ('Ten birds were recorded at this wetland.', 'Ten birds occur across the state.'),
            ('The policy proposes annual monitoring.', 'Authorities perform annual monitoring.'),
            ('The fee is 25 units for certified copies.', 'The application fee is 25 units.'),
        ]
        for quote, claim in pairs:
            with self.subTest(claim=claim):
                result = audit_unit(claim, [support('a', quote)], {'a': source(quote)})
                self.assertEqual(result['mechanical'], 'valid')
                self.assertEqual(result['release'], 'hold')

    def test_copy_only_also_rejects_a_valid_paraphrase(self):
        quote = 'The river flows west.'
        result = audit_unit('The river flows westward.', [support('a', quote)],
                            {'a': source(quote)}, excerpt_only=True)
        self.assertIn('non_extractive_transformation', result['issues'])

    def test_even_exact_copy_can_omit_qualifying_context(self):
        passage = 'An outdated draft said the fee is 25 units. This fee was withdrawn.'
        quote = 'the fee is 25 units'
        result = audit_unit(quote, [support('a', quote)], {'a': source(passage)}, excerpt_only=True)
        self.assertEqual(result['mechanical'], 'valid')  # Cherry-picking remains possible.
        self.assertEqual(result['semantic'], 'not_assessed')
        self.assertEqual(result['release'], 'hold')


class ExactSupportChecks(unittest.TestCase):
    def test_offsets_preserve_original_whitespace(self):
        passage = 'Context. Most of these plants\n  grow on plateaus. More context.'
        quote = 'Most of these plants grow on plateaus.'
        span = locate_excerpt(passage, quote)
        self.assertEqual(passage[span['start']:span['end']], 'Most of these plants\n  grow on plateaus.')

    def test_unknown_invented_ambiguous_and_changed_quotes_rejected(self):
        for quote in ['River flows.', 'river flows!', 'river ... flows.', '', 'river']:
            with self.subTest(quote=quote):
                self.assertIsNone(locate_excerpt('river flows. Another river follows.', quote))
        self.assertEqual(audit_unit('A claim.', [support('unknown', 'A claim.')], {})['mechanical'], 'reject')

    def test_context_must_be_on_its_own_unit(self):
        evidence = {'row': source('Bird A   Region A', context_ids=['header']),
                    'header': source('Species   Endemic to')}
        claim = 'Bird A is endemic to Region A.'
        result = audit_unit(claim, [support('row', evidence['row']['text'])], evidence)
        self.assertIn('missing_own_context', result['issues'])
        paired = audit_unit(claim, [support(i, e['text']) for i, e in evidence.items()], evidence)
        self.assertEqual(paired['mechanical'], 'valid')
        self.assertEqual(paired['semantic'], 'not_assessed')

    def test_length_does_not_claim_to_measure_atomicity(self):
        quote = 'First fact and second fact are unrelated.'
        result = audit_unit(quote, [support('a', quote)], {'a': source(quote)})
        self.assertEqual(result['mechanical'], 'valid')
        self.assertEqual(result['semantic'], 'not_assessed')
        self.assertIn('claim_word_limit', audit_unit('word ' * 36, [support('a', quote)], {'a': source(quote)})['issues'])

    def test_capture_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'capture.json'
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                read_capture(path, '0' * 64)


class AppOwnedSourceDates(unittest.TestCase):
    def test_agreeing_publication_fields_generate_year(self):
        result = publication_year(source('A fact.', source_date_metadata=[
            {'field': 'prism.publicationDate', 'value': '2025-05-04'},
            {'field': 'citation_online_date', 'value': '2025/05/04'}]))
        self.assertEqual(result['year'], 2025)
        self.assertEqual(result['label'], 'Source publication year: 2025 (publisher metadata)')

    def test_catalogue_upload_retrieval_and_generic_dates_cannot_supply_year(self):
        result = publication_year(source('A fact.', title='2025 report', url='/2025/05/report.pdf',
            retrieved_at='2026-10-27', source_date_metadata=[{'field': 'dc.date', 'value': '2024-01-01'}]))
        self.assertEqual(result['state'], 'unknown')
        self.assertIsNone(result['year'])

    def test_conflicting_or_invalid_publication_metadata_is_not_resolved_by_guess(self):
        for values in [('2024-01-01', '2025-01-01'), ('2025-02-30',), ('2025/04-01',), ('about 2025',)]:
            with self.subTest(values=values):
                result = publication_year(source('A fact.', source_date_metadata=[
                    {'field': 'prism.publicationDate', 'value': value} for value in values]))
                self.assertEqual(result['state'], 'conflict')
                self.assertIsNone(result['year'])

    def test_year_belongs_only_to_own_supports_not_another_claim(self):
        evidence = {'dated': source('Dated fact.', source_date_metadata=[
                        {'field': 'citation_online_date', 'value': '2025'}]),
                    'undated': source('Undated fact.')}
        result = audit_unit('Undated fact.', [support('undated', 'Undated fact.')], evidence)
        self.assertEqual(result['resolved'][0]['publication']['state'], 'unknown')


if __name__ == '__main__':
    unittest.main()
