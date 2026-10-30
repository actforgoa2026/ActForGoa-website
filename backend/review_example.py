"""Operator-only approval after checking each claim. No provider requests; no ledger writes.

python -m backend.review_example --input /protected/answer.json --review-note '...'
Input contains request and answer objects from a completed production investigation.
"""
import argparse
import json
import os
from pathlib import Path
from types import SimpleNamespace
from .chat import ChatRequest
from .hosting import PublicLimits
from .production_agent import ProductionAgent

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--review-note',required=True)
    args=parser.parse_args();root=Path(os.environ['RESEARCH_DATA_ROOT'])
    generation=json.loads((root/'.research-index/CURRENT.json').read_text())['generation']
    library=SimpleNamespace(root=root,generation=generation,generation_dir=lambda g:root/'.research-index/generations'/g)
    agent=ProductionAgent(library,PublicLimits(root/'.research-usage',require_existing=True),root/'.research-agent','unused-no-provider-call')
    data=json.loads(args.input.read_text());request=ChatRequest.model_validate(data['request']);answer=data['answer']
    if request.generation and request.generation!=generation:raise ValueError('Review against the active generation')
    if answer.get('agent',{}).get('engine')!='claude-agent-sdk' or not answer['agent'].get('run_id'):raise ValueError('Expected a completed SDK investigation')
    path=agent.examples.approve(request,answer,agent.corpus(),review_note=args.review_note)
    print(json.dumps({'approved':True,'file':str(path),'generation':generation}))

if __name__=='__main__':main()
