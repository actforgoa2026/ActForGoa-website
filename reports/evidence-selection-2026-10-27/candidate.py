"""Single offline candidate: field-weighted lexical relevance plus existing RRF.

Titles identify a document; bodies provide evidence. Use length-normalized term
frequency instead of five-character-prefix coverage. This is pointwise scoring,
not the previously rejected second-passage novelty selector.
"""
from collections import Counter
import math
import re
from urllib.parse import urlencode

from backend.library import authority_score, page_heading, LEGAL_TERMS


def words(text):
    # Match the existing lexical tokenizer's whole-word behavior. In particular,
    # "notify" and "notifications" must not become the same five-letter prefix.
    return re.findall(r'[^\W_]+', text.lower(), re.UNICODE)


def revise(record, limit):
    candidates = record['candidates']
    if not candidates:
        return [], {}
    terms = set(record['terms'])
    body = {r['id']: Counter(words(r['text'])) for r in candidates}
    title = {r['id']: Counter(words(r['meta'].get('title', ''))) for r in candidates}
    average = max(sum(sum(counts.values()) for counts in body.values())/len(body), 1)
    document_frequency = Counter()
    for row in candidates:
        document_frequency.update(terms.intersection(body[row['id']].keys() | title[row['id']].keys()))
    lexical = {}
    for row in candidates:
        identifier = row['id']
        length = sum(body[identifier].values())
        normalization = .25 + .75*length/average
        value = 0
        for term in terms:
            frequency = body[identifier][term]/normalization + .5*bool(title[identifier][term])
            if frequency:
                idf = math.log(1+(len(candidates)-document_frequency[term]+.5)/(document_frequency[term]+.5))
                value += idf*frequency*2.2/(frequency+1.2)
        lexical[identifier] = value
    maximum = max(lexical.values(), default=0) or 1
    legal_query = bool(LEGAL_TERMS.intersection(terms))
    scores = {r['id']: authority_score(r['rrf']+.05*lexical[r['id']]/maximum, r['meta'], legal_query)
              for r in candidates}
    hits, counts, seen = [], Counter(), []
    generation = record['generation']
    for row in sorted(candidates, key=lambda r: scores[r['id']], reverse=True):
        if counts[row['doc_id']] >= 2:
            continue
        tokens = re.findall(r'\w+', row['text'].lower())
        shingles = set(zip(tokens, tokens[1:]))
        if shingles and any(len(shingles & old)/max(len(shingles | old), 1) > .9 for old in seen):
            continue
        seen.append(shingles)
        counts[row['doc_id']] += 1
        meta = row['meta']
        qs = urlencode({'generation': generation, 'page': row['page'], 'passage': row['id']})
        hits.append({'id': row['id'], 'document_id': row['doc_id'], 'page': row['page'],
                     'label': row['label'], 'start': row['start'], 'end': row['end'],
                     'title': meta.get('title') or meta['url'], 'url': meta['url'],
                     'text': row['text'], 'origin': row['origin'], 'warning': row['warning'],
                     'page_heading': page_heading(row['page_context']),
                     'retrieved_at': meta.get('retrieved_at'), 'format': meta.get('format'),
                     'matches': row['channels'],
                     **{key: meta.get(key) for key in ('publisher_class', 'legal_currency', 'source_date_metadata', 'topics', 'document_kind_hint', 'guide_verification')},
                     'reader_url': f'/documents/{row["doc_id"]}?{qs}', 'generation': generation})
        if len(hits) >= limit:
            break
    return hits, {'scores': scores, 'lexical': lexical}
