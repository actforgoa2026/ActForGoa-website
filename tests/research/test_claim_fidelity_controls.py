"""Keep neutral semantic-review controls executable without pretending to judge them."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from backend.anthropic_provider import message_request, normalize_native_answer
from backend.chat import ChatRequest, prepare_answer
from backend.providers import chat_config

CONTROLS = json.loads(Path(__file__).with_name('claim_fidelity_controls.json').read_text())['cases']
NEGATIVE_CONTROLS = [
    pytest.param(case, text, id=f"{case['id']}-{index}")
    for case in CONTROLS
    for index, text in enumerate([case['unsupported_text'], *case.get('unsupported_variants', [])])
]


@pytest.mark.parametrize('case', CONTROLS, ids=lambda case: case['id'])
@pytest.mark.parametrize('style', ['brief', 'standard'])
@pytest.mark.parametrize('model,effort', [('claude-haiku-5-5', 'low'),
                                         ('claude-haiku-5-5', 'medium'),
                                         ('claude-sonnet-5-5', 'medium')])
def test_all_needed_control_evidence_reaches_both_models_unchanged(case, style, model, effort, monkeypatch):
    monkeypatch.setenv('RESEARCH_CHAT_PROVIDER', 'anthropic')
    monkeypatch.setenv('ANTHROPIC_CHAT_MODEL', model)
    monkeypatch.setenv('ANTHROPIC_CHAT_EFFORT', effort)
    evidence = deepcopy(case['evidence'])
    prepared = prepare_answer(ChatRequest(question=case['question'], answer_style=style),
                              evidence, provider='anthropic')
    wire = message_request(chat_config(), prepared)
    visible = json.loads(wire['messages'][-1]['content'])
    assert visible['question'] == case['question']
    assert [(p['id'], p['text']) for p in visible['evidence']] == [(p['id'], p['text']) for p in evidence]
    assert prepared.evidence == evidence == case['evidence']
    assert wire['model'] == model and wire['max_tokens'] == (12000 if model == 'claude-haiku-5-5' else 9000)
    assert wire['thinking'] == {'type': 'adaptive'} and wire['output_config']['effort'] == effort
    assert len(json.dumps(wire['output_config']['format']['schema'], separators=(',', ':')).encode()) <= 4096
    assert len(json.dumps(prepared.messages, ensure_ascii=False, separators=(',', ':')).encode()) <= 24000
    unit = {'text': case['supported_text'], 'primary_support': case['supports'][0],
            'supports': case['supports'][1:]}
    native = {'status': 'answered', **({'paragraph': unit} if style == 'brief' else {'paragraphs': [unit]})}
    normalized = json.loads(normalize_native_answer(json.dumps(native), prepared))
    assert normalized['paragraphs'] == [{'text': unit['text'], 'citations': [p['id'] for p in evidence]}]


@pytest.mark.parametrize('case,unsupported_text', NEGATIVE_CONTROLS)
def test_mechanical_acceptance_is_not_a_semantic_verdict(case, unsupported_text):
    # These deliberately wrong statements retain real local quotes. A semantic
    # review must reject them; this test documents the mechanical guard's limit.
    prepared = prepare_answer(ChatRequest(question=case['question']), case['evidence'], provider='anthropic')
    unit = {'text': unsupported_text, 'primary_support': case['supports'][0],
            'supports': case['supports'][1:]}
    normalized = json.loads(normalize_native_answer(json.dumps({'status': 'answered', 'paragraphs': [unit]}), prepared))
    assert normalized['paragraphs'][0]['text'] == unsupported_text
