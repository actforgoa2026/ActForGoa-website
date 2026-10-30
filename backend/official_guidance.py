"""Reviewed official summaries, separate from the immutable research corpus.

Only this committed allowlist is readable; no user URL or live webpage is fetched
inside a model run. IDs bind citations to the exact reviewed summary and source.
"""
import hashlib
import json
from pathlib import Path

SAPCC_SHA256 = 'd1b64d562f93c9cbabc39e1d4be65f0515a06734792cfa5ea4eebf9544ff3cc6'
DATA = Path(__file__).with_name('data') / 'flood-preparedness.json'


def flood_guidance():
    data = json.loads(DATA.read_text())
    sources = []
    for source in data['sources']:
        digest = hashlib.sha256(json.dumps(source, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        sources.append({
            'id': f"guidance:{source['key']}:{digest[:16]}",
            'document_id': f"official:{source['key']}",
            'title': source['title'], 'publisher': source['publisher'],
            'text': source['text'], 'page': source['page'], 'label': source['label'],
            'url': source['url'], 'reader_url': source['url'], 'format': source['format'],
            'origin': 'official_guidance_summary', 'publisher_class': 'official_preparedness_guidance',
            'generation': data['version'], 'sha256': digest, 'matches': ['flood preparedness'],
            'retrieved_at': data['checked_on'], 'checked_on': data['checked_on'],
            'published_on': source['published_on'],
            'warning': 'ActForGoa summary of official guidance. Source checked on ' + data['checked_on'] +
                       '; publication date not stated. General preparedness, not a live flood warning or evacuation order.',
        })
    return {'topic': 'floods', 'checked_on': data['checked_on'],
            'alerts_url': data['alerts_url'], 'sources': sources}


def guidance_allowed(corpus, document_id):
    return not document_id or corpus.document(document_id).get('sha256') == SAPCC_SHA256
