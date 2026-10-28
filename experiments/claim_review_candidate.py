"""Offline review contract. No provider, corpus, ledger or runtime imports.

Dependency completeness and reviewer decisions are deliberately separate.
Dependencies must come from source review; this module cannot discover them.
"""
from dataclasses import dataclass
import hashlib
import json

FACETS = ('subject', 'modality', 'measure', 'population', 'date', 'conditions', 'uncertainty')


@dataclass(frozen=True)
class Span:
    id: str
    passage: str
    start: int
    end: int
    requires: tuple[str, ...] = ()


def check(pack, claims):
    """Check original offsets and explicit closure; never add a missing support.

    pack is an offline source-review artifact, not model-authored context.
    Original passages remain intact even where only one span is selected.
    """
    passages, spans = pack['passages'], pack['spans']
    if len({s.id for s in spans}) != len(spans):
        raise ValueError('duplicate span')
    lookup = {s.id: s for s in spans}
    for s in spans:
        if s.passage not in passages or not 0 <= s.start < s.end <= len(passages[s.passage]):
            raise ValueError('invalid original span')
        if any(d not in lookup for d in s.requires):
            raise ValueError('missing dependency')
    def visit(identifier, path):
        if identifier in path:
            raise ValueError('dependency cycle')
        for dependency in lookup[identifier].requires:
            visit(dependency, path | {identifier})
    for s in spans:
        visit(s.id, set())
    if not claims:
        raise ValueError('no claims; abstention needs separate semantic review')
    for claim in claims:
        if set(claim) != {'text', 'supports', 'facets'} or not claim['text'].strip():
            raise ValueError('invalid claim')
        ids = claim['supports']
        if not ids or len(ids) > 6 or len(set(ids)) != len(ids) or any(i not in lookup for i in ids):
            raise ValueError('invalid explicit supports')
        if set(claim['facets']) != set(FACETS):
            raise ValueError('missing facet review entries')
        for identifiers in claim['facets'].values():
            if not isinstance(identifiers, list) or any(i not in ids for i in identifiers):
                raise ValueError('facet evidence must be explicitly selected')
        for identifier in ids:
            selected_span = lookup[identifier]
            if selected_span.end - selected_span.start > 1600:
                raise ValueError('selected support exceeds existing quote allowance')
            if any(d not in ids for d in lookup[identifier].requires):
                raise ValueError('incomplete explicit support selection')
    # Bind later review to these exact bytes; edited claims invalidate decisions.
    frozen = json.dumps({'pack': {**pack, 'spans': [s.__dict__ for s in spans]},
                         'claims': claims},
                        ensure_ascii=False, sort_keys=True).encode()
    return {'sha256': hashlib.sha256(frozen).hexdigest(),
            'claim_count': len(claims),
            'mechanical': 'valid', 'semantic': 'not_assessed', 'release': 'hold'}


def review(result, decisions):
    """Human evidence review, never inferred from structural success.

    Each claim/facet requires an explicit verdict, including not-applicable with
    rationale. A disagreeing or missing decision cannot be averaged away.
    """
    expected = {(index, facet) for index in range(decisions['claim_count']) for facet in FACETS}
    entries = decisions['entries']
    keys = [(e['claim'], e['facet']) for e in entries]
    if (decisions['claim_count'] != result['claim_count']
            or decisions['sha256'] != result['sha256'] or len(keys) != len(set(keys))
            or set(keys) != expected or decisions['claim_count'] < 1):
        raise ValueError('incomplete or stale review')
    if any(e['verdict'] not in ('preserved', 'not_applicable', 'failed', 'unresolved')
           or not e['reason'].strip() for e in entries):
        raise ValueError('review requires reasoned verdicts')
    accepted = all(e['verdict'] in ('preserved', 'not_applicable') for e in entries)
    return {**result, 'facet_review': 'recorded_pass' if accepted else 'rejected_or_unresolved',
            'semantic': 'not_assessed', 'release': 'hold'}
