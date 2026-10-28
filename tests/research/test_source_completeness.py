"""Exact instruction revision and stale identity checks, not semantic acceptance."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from backend import reconstruction
from backend.chat import AnswerCache
from backend.phase_effort import PIPELINE_VERSION
from backend.span_instructions import legacy_span_answer_instructions as span_answer_instructions
from scripts import evaluate_anthropic_acceptance as acceptance
from tests.research.span_fixtures import previous_source_completeness_prompt
from tests.research.test_answer_pipeline import setup
from tests.research.test_anthropic_acceptance import setup as legacy_setup
from tests.research.test_two_pass_acceptance import setup as acceptance_setup


@pytest.mark.parametrize('phase', ['draft', 'reconstruction'])
@pytest.mark.parametrize('style', ['standard', 'brief'])
def test_only_four_reviewed_sections_change_and_exact_approved_prompts_match(phase, style):
    docs = Path(__file__).parents[2] / 'docs'
    old = json.loads((docs / 'research-required-coverage-parity.json').read_text())
    new = json.loads((docs / 'research-source-completeness-parity.json').read_text())
    before = previous_source_completeness_prompt(phase, style).encode()
    after = span_answer_instructions(phase, style).encode()
    for body, record in [(before, old), (after, new)]:
        pin = record['rendered_instructions'][phase][style]
        assert (len(body), hashlib.sha256(body).hexdigest()) == (pin['utf8_bytes'], pin['sha256'])
    assert len(after) - len(before) == 41


@pytest.mark.parametrize('change', [
    lambda p: p.update(pipeline='two_pass_v8'),
    lambda p: p['pipeline_spec'].update(version='two_pass_v8'),
    lambda p: p['pipeline_spec'].update(capture_version=7),
])
def test_stale_v8_plan_stops_before_packet_key_and_ledger(acceptance_setup, monkeypatch, change):
    plan, config, *_ = acceptance_setup; change(plan)
    def no_access(*_):
        pytest.fail('Stale instruction identity must fail before packet/key/ledger access')
    for name in ('verify_packets', 'dotenv_values', 'inspect_ledger'):
        monkeypatch.setattr(acceptance, name, no_access)
    with pytest.raises(ValueError):
        acceptance.preflight(plan, 'test', config)


def test_v8_cache_cannot_supply_v9_despite_same_workflow_and_effort(setup, monkeypatch):
    config, _, original, *_ = setup
    current = AnswerCache.key(config, original)
    historical = reconstruction.reconstruction_cache_identity(original, PIPELINE_VERSION)
    historical['spec'].update(version='two_pass_v8', capture_version=7)
    historical['draft_instructions'] = previous_source_completeness_prompt('draft', original.answer_style)
    historical['correction_instructions'] = previous_source_completeness_prompt('reconstruction', original.answer_style)
    with monkeypatch.context() as m:
        m.setattr(reconstruction, 'reconstruction_cache_identity', lambda *_: deepcopy(historical))
        previous = AnswerCache.key(replace(config, pipeline='two_pass_v8'), original)
    cache = AnswerCache(); cache.put(previous, {'fixture': 'unaccepted prior answer'})
    assert previous != current and cache.get(current) is None
    with pytest.raises(ValueError):
        AnswerCache.key(replace(config, pipeline='two_pass_v8'), original)
    assert reconstruction.pipeline_spec()['answer_workflow'] == 'evidence_plan_first_v1'
