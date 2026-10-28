"""Choose complementary evidence within the documents selected by hybrid search.

Document retrieval remains responsible for source relevance. Within its slots,
prefer coverage of the requested details over repeated document/title words.
Citation text and locators are never changed here.
"""
from collections import Counter
from itertools import combinations
import math
import re
import unicodedata

from snowballstemmer.english_stemmer import EnglishStemmer


DISCOURSE = frozenset('according saved official specify specifies stated state must under user guide manual list whom much someone outside before after should found does i not you yours us our'.split())


def select_passages(query, candidates, baseline_ids, scores, stop_words):
    """Return candidate IDs in the existing document-slot order (at most two).

Joint coverage avoids spending one slot on a cover and the other on a generic
introduction. A relevance term preserves preference for stronger hybrid hits.
The objective contains no source IDs, named topics, or question-specific rules.
"""
    # Snowball objects are not thread-safe; use one per search, with a bounded
    # request-local token cache rather than a shared mutable model.
    stemmer = EnglishStemmer()
    token_cache = {}

    def tokens(text):
        if text not in token_cache:
            words = re.findall(r'[^\W_]+', unicodedata.normalize('NFKC', text).lower())
            token_cache[text] = frozenset(stemmer.stemWords(
                [word for word in words if word not in stop_words and word not in DISCOURSE]))
        return token_cache[text]

    query_terms = tokens(query)
    pools = {}
    for identifier, (row, meta) in candidates.items():
        pools.setdefault(row['doc_id'], []).append(identifier)
    slots = Counter(candidates[i][0]['doc_id'] for i in baseline_ids)
    chosen = {}
    for document, count in slots.items():
        pool = pools[document]
        title = candidates[pool[0]][1].get('title', '')
        focus = query_terms - tokens(title)
        if not focus or count > 2:
            chosen[document] = [i for i in baseline_ids if candidates[i][0]['doc_id'] == document]
            continue
        bodies = {i: tokens(candidates[i][0]['text']) for i in pool}
        frequency = Counter(term for body in bodies.values() for term in body)
        weights = {term: 1 + math.log((len(pool) + 1) / (frequency[term] + 1)) for term in focus}
        total = sum(weights.values()) or 1
        strongest = max(scores[i] for i in pool) or 1

        def coverage(ids):
            covered = set().union(*(bodies[i] for i in ids))
            return sum(weights[t] for t in focus & covered) / total

        def objective(ids):
            relevance = sum(scores[i] for i in ids) / (len(ids) * strongest)
            return coverage(ids) + .5 * relevance, sum(scores[i] for i in ids)

        group = max(combinations(pool, min(count, len(pool))), key=objective)
        chosen[document] = sorted(group, key=lambda i: (coverage([i]), scores[i]), reverse=True)

    used = Counter()
    result = []
    for identifier in baseline_ids:
        document = candidates[identifier][0]['doc_id']
        result.append(chosen[document][used[document]])
        used[document] += 1
    return result
