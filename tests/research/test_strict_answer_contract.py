"""Regressions for real citation identity, damaged source text and length failures."""
from copy import deepcopy
import json
import pytest
from backend.chat import ChatRequest, normalize_answer, prepare_answer, provider_schema

EVIDENCE = [{'id': 'a44740d147d1894cd1304efd76dad111', 'title': 'ZSI Goa bird report',
             'text': 'Western Ghats bu\x00tterﬂies. Only the surveyed herbaceous subset occurs here.'}]
REQUEST = ChatRequest(question='What geographic range does the source identify?')

def answer(text='The passage discusses Western Ghats butterflies.'):
    return {'coverage':'full', 'paragraph_1':{'supports':[EVIDENCE[0]['id']], 'text':text},
            **{f'paragraph_{i}':None for i in range(2,6)}, 'outside_context':None, 'limitation':None}

def test_wire_schema_restricts_source_references_and_never_asks_to_retype_damaged_text():
    payload,selected=prepare_answer(REQUEST,EVIDENCE)
    tool=payload['tools'][0]; props=tool['input_schema']['$defs']['ReferencedParagraph']['properties']
    assert tool['strict'] is True
    assert props['supports']['items']['enum']==[EVIDENCE[0]['id']]
    assert list(props)==['supports','text']
    assert selected==EVIDENCE
    assert json.loads(payload['messages'][0]['content'])['evidence'][0]['text']==EVIDENCE[0]['text']
    result=normalize_answer(answer(),REQUEST,EVIDENCE)
    assert result['citations']==EVIDENCE  # exact original including NUL and qualifiers
    for identifier in [EVIDENCE[0]['title'],'unknown','no-library-source']:
        raw=answer();raw['paragraph_1']['supports']=[identifier]
        with pytest.raises(ValueError):normalize_answer(raw,REQUEST,EVIDENCE)
    raw=answer();raw['paragraph_1']['supports']=[{'citation_id':EVIDENCE[0]['id'],'quote':'Repaired text'}]
    with pytest.raises(ValueError):normalize_answer(raw,REQUEST,EVIDENCE)

def test_five_paragraphs_300_words_preserved_and_overflow_rejected_without_truncation():
    raw=answer()
    for i in range(1,6):raw[f'paragraph_{i}']={'supports':[EVIDENCE[0]['id']],'text':' '.join(['Word']*60)}
    assert len(normalize_answer(raw,REQUEST,EVIDENCE)['paragraphs'])==5
    raw['paragraph_5']['text']+=' extra'
    with pytest.raises(ValueError,match='too long'):normalize_answer(raw,REQUEST,EVIDENCE)
    raw=answer();raw['paragraph_6']=deepcopy(raw['paragraph_1'])
    with pytest.raises(ValueError):normalize_answer(raw,REQUEST,EVIDENCE)
    raw=answer();raw['paragraph_3']=raw['paragraph_1'];raw['paragraph_1']=None
    with pytest.raises(ValueError,match='contiguous'):normalize_answer(raw,REQUEST,EVIDENCE)

def test_schema_omits_unsupported_constraints_but_retains_server_support_bounds():
    schema=json.dumps(provider_schema(EVIDENCE))
    for forbidden in ['minLength','maxLength','maxItems','pattern']:assert forbidden not in schema
    raw=answer();raw['paragraph_1']['supports']*=7
    with pytest.raises(ValueError):normalize_answer(raw,REQUEST,EVIDENCE)
    raw=answer();raw['paragraph_1']['citations']=[EVIDENCE[0]['id']]
    with pytest.raises(ValueError):normalize_answer(raw,REQUEST,EVIDENCE)

def test_prompt_budget_does_not_authorize_omitted_sources():
    payload,selected=prepare_answer(REQUEST,EVIDENCE+[{'id':'omitted','text':'x'*40000}])
    assert selected==EVIDENCE
    assert payload['tools'][0]['input_schema']['$defs']['ReferencedParagraph']['properties']['supports']['items']['enum']==[EVIDENCE[0]['id']]
