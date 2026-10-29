"""Verify the actual provider request contains readable, attributable excerpts."""
from copy import deepcopy
import json

import httpx

from backend.anthropic_answers import AnthropicAnswers
from backend.chat import ChatRequest, answer_question, prepare_answer


def test_provider_receives_exact_excerpts_and_locations_not_just_search_metadata():
    excerpts = [
        {'id': 'passage-first', 'document_id': 'document-first', 'title': 'Coastal survey',
         'text': 'At Site A, mangroves sheltered juvenile fish.\nThis observation alone does not establish conditions at Site B.',
         'page': 17, 'label': 'PDF page 17', 'url': 'https://example.org/survey.pdf',
         'source_date_metadata': {'publication_date': '2020-06-01'}, 'start': 32, 'end': 168},
        {'id': 'passage-second', 'document_id': 'document-second', 'title': 'Field notes',
         'text': 'The second survey did not measure juvenile fish at Site B. “Not measured” does not mean absent.',
         'page': 3, 'label': 'Section 3', 'url': 'https://example.org/notes'},
    ]
    calls = []

    def provider(request):
        calls.append(request)
        wire = json.loads(request.content)
        context = json.loads(wire['messages'][0]['content'])
        assert context['evidence'] == excerpts
        assert context['question'] == 'What do these surveys establish about juvenile fish?'
        assert context['conversation_context_not_evidence'] == []
        return httpx.Response(200, json={'stop_reason': 'tool_use', 'content': [{
            'type': 'tool_use', 'name': 'answer_library_question', 'input': {
                'coverage': 'partial', 'paragraph_1': {
                    'text': 'Juvenile fish were observed at Site A; the second survey did not measure them at Site B.',
                    'supports': [item['id'] for item in excerpts],
                }, 'paragraph_2': None, 'paragraph_3': None, 'paragraph_4': None, 'paragraph_5': None, 'limitation': 'The excerpts do not establish the presence or absence of juvenile fish at Site B.',
            },
        }]})

    client = AnthropicAnswers('fixture-only', httpx.Client(transport=httpx.MockTransport(provider)))
    try:
        result = answer_question(client, 'claude-haiku-5-5', ChatRequest(
            question='What do these surveys establish about juvenile fish?'), excerpts)
    finally:
        client.close()
    assert len(calls) == 1
    assert [item['id'] for item in result['citations']] == ['passage-first', 'passage-second']
    assert result['paragraphs'][0]['text'].startswith('Juvenile fish were observed')


def test_context_budget_preserves_whole_excerpts_and_followup_is_not_evidence():
    small = {'id': 'small', 'text': 'Permission may be required, except where the stated exemption applies.',
             'document_id': 'doc-small', 'page': 4, 'label': 'Page 4'}
    evidence = [{'id': 'oversized', 'text': 'x' * 40000 + ' except for the named exemption.'}, small]
    before = deepcopy(evidence)
    request = ChatRequest(question='Does that always apply?', history=[
        {'role': 'user', 'content': 'Which permissions apply?'},
        {'role': 'assistant', 'content': 'Earlier model output is not source evidence.'},
    ])
    payload, selected = prepare_answer(request, evidence)
    context = json.loads(payload['messages'][0]['content'])
    assert context['evidence'] == [small]
    assert selected == [small] and evidence == before
    assert context['conversation_context_not_evidence'][0]['content'] == 'Which permissions apply?'
    assert all('Earlier model output' not in item['text'] for item in context['evidence'])


def test_reviewed_locator_claims_cannot_substitute_for_source_passages():
    item={'id':'x','text':'The actual source excerpt.',
          'source_date_metadata':{'publication_date':'2020-06-01','reviewed_locator_and_dates':'A factual claim absent from the excerpt.'},
          'guide_verification':{'location':'Page4: unsupported procedural summary','limitations':'Check later amendments.'}}
    payload,selected=prepare_answer(ChatRequest(question='What does this establish?'),[item])
    wire=json.loads(payload['messages'][0]['content'])['evidence'][0]
    assert wire['text']==item['text']
    assert wire['source_date_metadata']=={'publication_date':'2020-06-01'}
    assert wire['guide_verification']=={'limitations':'Check later amendments.'}
    assert selected[0]['source_date_metadata']==item['source_date_metadata']


def test_complementary_document_passages_are_budgeted_together():
    first={'id':'first','document_id':'manual','text':'Application step. '+('x'*6000)}
    last={'id':'last','document_id':'manual','text':'Required fee and exemption. '+('y'*6000)}
    independent={'id':'other','document_id':'other','text':'A separate short source.'}
    _, selected=prepare_answer(ChatRequest(question='How can I apply?'),[first,independent,last])
    ids={item['id'] for item in selected}
    assert ('first' in ids)==('last' in ids)
    assert 'other' in ids


def test_document_conversation_keeps_complete_context_when_all_passages_do_not_fit():
    doc = 'a' * 24 + '-' + 'b' * 12
    generation = 'fixture-version'
    header = {'id': 'header', 'document_id': doc, 'generation': generation, 'page': 4,
              'start': 0, 'end': 500, 'text': 'Conditions and exceptions. ' + 'h' * 500}
    evidence = [{'id': f'passage-{i}', 'document_id': doc, 'generation': generation, 'page': 4,
                 'text': f'Complete passage {i}. ' + 'x' * 3200, 'supporting_context': [header]}
                for i in range(4)]
    before = deepcopy(evidence)
    request = ChatRequest(question='What does this document propose?', document_id=doc, generation=generation)
    payload, selected = prepare_answer(request, evidence)
    ids = {item['id'] for item in selected}
    assert 'passage-0' in ids and 'header' in ids
    assert 1 <= len(ids - {'header'}) < 4
    assert all('header' in item['context_ids'] for item in selected if item['id'] != 'header')
    originals = {item['id']: item['text'] for item in [*evidence, header]}
    assert all(item['text'] == originals[item['id']] for item in selected)
    assert evidence == before
    from backend.anthropic_answers import MAX_PROMPT_BYTES
    assert len(json.dumps(payload, ensure_ascii=False).encode()) <= MAX_PROMPT_BYTES
    # Collection-wide grouping still keeps complementary passages together.
    _, general = prepare_answer(ChatRequest(question=request.question), evidence)
    assert general == []
