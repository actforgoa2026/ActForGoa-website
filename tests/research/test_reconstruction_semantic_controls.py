"""Preserve semantic negatives: the new schema does not magically prove claims."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from backend.chat import ChatRequest,prepare_answer
from backend.reconstruction import prepare_reconstruction,normalize_reconstruction
from backend.source_spans import verify_annotated_payload
from tests.research.test_claim_fidelity_controls import CONTROLS,NEGATIVE_CONTROLS
from tests.research.span_fixtures import select_response


@pytest.mark.parametrize('case',CONTROLS,ids=lambda c:c['id'])
@pytest.mark.parametrize('draft_kind',['supported','bad','insufficient'])
def test_supported_reconstruction_keeps_all_evidence_and_fills_source_coverage(case,draft_kind):
    request=ChatRequest(question=case['question'])
    original=prepare_answer(request,deepcopy(case['evidence']),provider='anthropic')
    # Plans contain no prose. Exercise both empty recovery and an untrusted
    # need label that suggests the old unsupported answer, never treated as evidence.
    draft={'status':'insufficient_evidence','points':[],'units':[]}
    if draft_kind!='insufficient':
        label='Source coverage' if draft_kind=='supported' else 'Assert the unsupported conclusion'
        draft['points']=[{'need':label,'coverage':'missing','gaps':['support']}]
    prepared=prepare_reconstruction(request,original,draft)
    payload=json.loads(prepared.messages[-1]['content'])
    restored,_=verify_annotated_payload({k:payload[k] for k in ('question','sources','evidence')},json.loads(original.messages[-1]['content']))
    assert [(e['id'],e['text']) for e in restored['evidence']]==[(e['id'],e['text']) for e in case['evidence']]
    unit={'primary_support':case['supports'][0],'supports':case['supports'][1:],'text':case['supported_text']}
    answer,_=normalize_reconstruction(json.dumps(select_response({'status':'answered','paragraphs':[{'claims':[unit]}]},payload)),prepared)
    assert answer['paragraphs'][0]['text']==case['supported_text']
    # Authored fixture success establishes deterministic mechanics, not a model
    # correction/semantic pass. Actual final answers still need source review.


@pytest.mark.parametrize('case,wrong',NEGATIVE_CONTROLS)
def test_quote_valid_wrong_reconstruction_remains_semantically_failed(case,wrong):
    request=ChatRequest(question=case['question']);original=prepare_answer(request,case['evidence'],provider='anthropic')
    prepared=prepare_reconstruction(request,original,{'status':'insufficient_evidence','points':[],'units':[]})
    unit={'primary_support':case['supports'][0],'supports':case['supports'][1:],'text':wrong}
    answer,_=normalize_reconstruction(json.dumps(select_response({'status':'answered','paragraphs':[{'claims':[unit]}]},json.loads(prepared.messages[-1]['content']))),prepared)
    assert answer['paragraphs'][0]['text']==wrong
    assert case['review_expectation']['forbidden_change']
