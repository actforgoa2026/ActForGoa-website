"""Source headers must be real, citable text and survive budgeting with their rows."""
from copy import deepcopy
import json

import pytest

from backend.chat import (ChatRequest, GroundedAnswer, MAX_PROMPT_BYTES,
                          prepare_answer, validate_answer)
from backend.anthropic_provider import normalize_native_answer, message_request
from backend.providers import ChatConfig
from backend.source_context import preceding_table_chunk, with_source_context


TEXT = ('   Table- 4: Items and recorded areas\n\n'
        ' Sl. No   Item                                  Recorded in\n\n'
        '  1.     First item                             Region A\n\n'
        '  2.     Second item                            Region B\n\n'
        '  3.     Third item                             Region C\n\n'
        '  4.     Fourth item                            Region D\n\n')


def chunk(identifier, start, end, **extra):
    return dict(id=identifier, document_id='document', generation='saved-v1',
                page=3, label='PDF page 3', start=start, end=end, text=TEXT[start:end],
                title='Saved source', warning='Check original layout.', **extra)


def fixture():
    start=TEXT.index('  3.')
    header=chunk('header',3,TEXT.index('  3.'))
    rows=chunk('rows',start,len(TEXT),supporting_context=[header])
    return rows,header


def test_preceding_header_is_an_existing_exact_chunk_with_columns():
    rows,header=fixture()
    assert preceding_table_chunk(TEXT,rows['start'],rows['end'],[header,rows])==header
    assert 'Recorded in' in header['text']
    assert preceding_table_chunk(TEXT,header['start'],header['end'],[header,rows]) is None
    assert preceding_table_chunk(TEXT,rows['start'],rows['end'],[dict(header,text='Invented header')]) is None
    assert preceding_table_chunk(TEXT,rows['start'],rows['end'],[dict(header,end=10,text=TEXT[3:10])]) is None


def test_caption_is_not_guessed_from_title_or_carried_across_sections():
    rows,header=fixture()
    assert preceding_table_chunk(' ' * rows['start']+rows['text'],rows['start'],rows['end'],[header]) is None
    boundary='\nUnrelated Section\n'
    text=TEXT[:rows['start']]+boundary+TEXT[rows['start']:]
    assert preceding_table_chunk(text,rows['start']+len(boundary),len(text),[header]) is None
    prose='The source describes the district in ordinary prose.\nNo aligned columns are present.'
    assert preceding_table_chunk(TEXT+prose,len(TEXT),len(TEXT+prose),[header]) is None


@pytest.mark.parametrize('boundary',[
    'Conservation status', '3. Conservation status', '3. Conservation Status',
    '3.  Conservation status', 'The next observations use a different classification.',
    'Wrapped cell continuation',
])
def test_ambiguous_intervening_prose_or_heading_blocks_header_carryover(boundary):
    rows,header=fixture()
    inserted='\n'+boundary+'\n\n'
    page=TEXT[:rows['start']]+inserted+TEXT[rows['start']:]
    assert preceding_table_chunk(page,rows['start']+len(inserted),len(page),[header]) is None


@pytest.mark.parametrize('columns',['',' Sl. No   Item\n\n',' 1   2   3\n\n'])
def test_caption_without_complete_textual_column_labels_is_not_header_context(columns):
    original=' Sl. No   Item                                  Recorded in\n\n'
    page=TEXT.replace(original,columns)
    start=page.index('  3.')
    header=dict(id='header',start=3,end=start,text=page[3:start])
    assert preceding_table_chunk(page,start,len(page),[header]) is None


def test_most_recent_table_caption_has_its_own_header():
    rows,header=fixture()
    second=TEXT.replace('Table- 4:','Table 5:')
    page=TEXT+second
    target_start=len(TEXT)+rows['start']
    second_header={**header,'id':'second-header','start':len(TEXT)+3,
                   'end':len(TEXT)+header['end'],'text':second[3:header['end']]}
    assert preceding_table_chunk(page,target_start,len(page),[header,second_header])==second_header


def test_non_caption_and_extra_unlabeled_row_field_stay_ambiguous():
    rows,header=fixture()
    for page in (TEXT.replace('Table- 4:','Table of contents:'),
                 TEXT.replace('Third item                             Region C',
                              'Third item                             Region C    Unknown field')):
        start=page.index('  3.')
        context={**header,'end':start,'text':page[3:start]}
        assert preceding_table_chunk(page,start,len(page),[context]) is None


def test_context_expansion_preserves_ids_text_and_deduplicates_existing_hit():
    rows,header=fixture();original=deepcopy([rows,header])
    result=with_source_context([rows,header])
    assert [item['id'] for item in result]==['rows','header']
    assert result[0]['context_ids']==['header']
    assert all(item['text']==TEXT[item['start']:item['end']] for item in result)
    assert [rows,header]==original
    assert all('supporting_context' not in item for item in result)
    for field,value in [('document_id','different'),('generation','other'),('page',4)]:
        with pytest.raises(ValueError,match='identity'):
            with_source_context([{**rows,'supporting_context':[{**header,field:value}]}])
    with pytest.raises(ValueError,match='conflicting'):
        with_source_context([rows,{**header,'text':'Changed source.'}])


def test_prompt_and_citations_include_both_exact_source_excerpts():
    rows,header=fixture()
    prepared=prepare_answer(ChatRequest(question='What do the source columns mean?'),[rows],provider='anthropic')
    assert [item['id'] for item in prepared.evidence]==['rows','header']
    payload=json.loads(prepared.messages[-1]['content'])
    assert payload['evidence'][0]['context_ids']==['header']
    assert payload['evidence'][1]['text']==header['text']
    claim={'status':'answered','paragraphs':[{'text':'The listed area is Region C.','citations':['rows']}]}
    with pytest.raises(ValueError,match='context'):
        validate_answer(GroundedAnswer.model_validate(claim),prepared.evidence)
    claim['paragraphs'][0]['citations'].append('header')
    result=validate_answer(GroundedAnswer.model_validate(claim),prepared.evidence)
    assert [item['id'] for item in result['citations']]==['rows','header']


def test_native_context_requires_actual_header_text_support_not_only_metadata():
    rows,header=fixture()
    prepared=prepare_answer(ChatRequest(question='What is shown?'),[rows],provider='anthropic')
    answer={'status':'answered','paragraphs':[{'text':'The source lists Region C.',
        'primary_support':{'citation_id':'rows','field':'text','quote':'Third item'},
        'supports':[{'citation_id':'header','field':'warning','quote':header['warning']}]}]}
    with pytest.raises(ValueError,match='evidence contract'):
        normalize_native_answer(json.dumps(answer),prepared)
    answer['paragraphs'][0]['supports'][0]={'citation_id':'header','field':'text','quote':'Recorded in'}
    assert json.loads(normalize_native_answer(json.dumps(answer),prepared))['paragraphs'][0]['citations']==['rows','header']


@pytest.mark.parametrize('change',['omit_wire','omit_local','change_wire'])
def test_visible_context_mismatch_is_rejected_before_dispatch_and_after_response(change):
    rows,header=fixture()
    prepared=prepare_answer(ChatRequest(question='What is shown?'),[rows],provider='anthropic')
    if change=='omit_local':
        prepared.evidence[0].pop('context_ids')
    else:
        payload=json.loads(prepared.messages[-1]['content'])
        if change=='omit_wire':payload['evidence'][0].pop('context_ids')
        # Same byte length so the separate prompt-budget guard does not mask
        # the context-identity check this fixture is exercising.
        else:payload['evidence'][0]['context_ids']=['absent']
        prepared.messages[-1]['content']=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
    config=ChatConfig('anthropic','claude-sonnet-5-5','Anthropic','ANTHROPIC_API_KEY',
                      'https://api.anthropic.com/v1',max_output_tokens=9000)
    with pytest.raises(ValueError,match='context'):
        message_request(config,prepared)
    output={'status':'answered','paragraphs':[{'text':'Region C is listed.',
        'primary_support':{'citation_id':'rows','field':'text','quote':'Region C'},
        'supports':[{'citation_id':'header','field':'text','quote':'Recorded in'}]}]}
    with pytest.raises(ValueError,match='evidence contract'):
        normalize_native_answer(json.dumps(output),prepared)


def test_prompt_budget_never_keeps_rows_without_their_required_header():
    rows,header=fixture()
    normal=chunk('ordinary',0,50)
    large={**header,'text':'Original oversized header. '*3000}
    prepared=prepare_answer(ChatRequest(question='What is supported?'),
                            [normal,{**rows,'supporting_context':[large]}],provider='anthropic')
    assert [item['id'] for item in prepared.evidence]==['ordinary']
    assert len(json.dumps(prepared.messages,ensure_ascii=False,separators=(',',':')).encode())<=MAX_PROMPT_BYTES
