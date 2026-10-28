"""Reviewed source defects, scoped to exact preserved passage bytes.

An exclusion affects generated-answer evidence only. The original document,
passage, offsets and search result remain available for inspection. A changed
passage requires a fresh review rather than inheriting an old exclusion.
"""
import hashlib
import json
from pathlib import Path


REVIEWS = json.loads(Path(__file__).with_suffix('.json').read_text())
if REVIEWS.get('version') != 1:
    raise ValueError('Unsupported source review registry')
EXCLUSIONS = {entry['passage_id']: entry for entry in REVIEWS['answer_exclusions']}


def answer_exclusion(passage):
    review = EXCLUSIONS.get(passage.get('id'))
    if (review and passage.get('document_id') == review['document_id']
            and passage.get('url') == review['source_url']
            and hashlib.sha256(passage.get('text', '').encode()).hexdigest() == review['text_sha256']):
        return review['reason']
    return None
