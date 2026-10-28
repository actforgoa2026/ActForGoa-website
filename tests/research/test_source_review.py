import hashlib
import json
import unittest
from unittest.mock import patch

from backend.chat import ChatRequest, prepare_answer
from backend.source_review import answer_exclusion


class SourceReviewTests(unittest.TestCase):
    def setUp(self):
        self.bad = dict(id='bad', document_id='document', url='https://example.org/source',
                        text='Ambiguous original wording.', generation='gen', page=1)
        self.good = dict(self.bad, id='good', text='Clear independent evidence.')
        self.review = dict(passage_id='bad', document_id='document', source_url=self.bad['url'],
                           text_sha256=hashlib.sha256(self.bad['text'].encode()).hexdigest(),
                           reason='Ambiguous source wording; inspect the original.')
        self.patcher = patch('backend.source_review.EXCLUSIONS', {'bad': self.review})
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_exact_review_excludes_answer_but_does_not_mutate_original(self):
        original = json.dumps(self.bad, sort_keys=True)
        payload, selected = prepare_answer(ChatRequest(question='What does it say?'), [self.bad, self.good])
        self.assertEqual([p['id'] for p in selected], ['good'])
        self.assertNotIn(self.bad['text'], json.dumps(payload))
        self.assertEqual(json.dumps(self.bad, sort_keys=True), original)
        self.assertEqual(answer_exclusion(self.bad), self.review['reason'])

    def test_changed_bytes_or_identity_require_new_review(self):
        for key, value in [('text', 'Corrected wording.'), ('document_id', 'another'), ('url', 'https://example.org/other')]:
            changed = dict(self.bad, **{key: value})
            self.assertIsNone(answer_exclusion(changed))
            _, selected = prepare_answer(ChatRequest(question='What does it say?'), [changed])
            self.assertEqual(len(selected), 1)

    def test_excluded_required_context_removes_whole_table_group(self):
        table = dict(self.good, supporting_context=[self.bad])
        _, selected = prepare_answer(ChatRequest(question='What does the table show?'), [table])
        self.assertEqual(selected, [])
