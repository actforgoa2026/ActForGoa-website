import json
from unittest.mock import patch

from backend.chat import (
    COUNTERFACTUAL_GUIDANCE, INSTRUCTIONS, ChatRequest, prepare_answer,
)


SOURCE = {
    'id': 'pump-condition', 'document_id': 'manual', 'page': 2,
    'text': 'If the pump were not stopped, there would be danger. The operator may stop it and report within one hour.',
}


def test_original_counterfactual_gets_guidance_without_source_rewriting():
    payload, selected = prepare_answer(ChatRequest(question='When is the report due?'), [SOURCE])
    assert payload['system'] == INSTRUCTIONS + '\n' + COUNTERFACTUAL_GUIDANCE
    assert selected == [SOURCE]
    assert json.loads(payload['messages'][0]['content'])['evidence'][0]['text'] == SOURCE['text']


def test_question_and_history_cannot_masquerade_as_counterfactual_evidence():
    request = ChatRequest(question=SOURCE['text'], history=[{'role': 'user', 'content': SOURCE['text']}])
    ordinary = dict(SOURCE, id='ordinary', text='The operator records each inspection.')
    payload, selected = prepare_answer(request, [ordinary])
    assert payload['system'] == INSTRUCTIONS
    assert selected == [ordinary]


def test_guidance_is_budgeted_atomically_with_its_source():
    request = ChatRequest(question='When is the report due?')
    payload, _ = prepare_answer(request, [SOURCE])
    limit = len(json.dumps(payload, ensure_ascii=False).encode()) - 1
    with patch('backend.chat.MAX_PROMPT_BYTES', limit):
        bounded, selected = prepare_answer(request, [SOURCE])
    assert selected == []
    assert bounded['system'] == INSTRUCTIONS
    assert len(json.dumps(bounded, ensure_ascii=False).encode()) <= limit
