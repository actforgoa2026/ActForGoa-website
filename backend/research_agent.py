"""Claude Agent SDK with only corpus/CRM readers and a clarification tool."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, create_sdk_mcp_server, query, tool
from pydantic import BaseModel, ConfigDict, Field
from . import crm_store
from .local_budget import MODEL
from .local_corpus import STATE

ROOT=Path(__file__).resolve().parents[1]

class Paragraph(BaseModel):
    model_config=ConfigDict(extra='forbid')
    text:str=Field(min_length=1,max_length=2000)
    supports:list[str]=Field(min_length=1,max_length=6)

class AgentAnswer(BaseModel):
    model_config=ConfigDict(extra='forbid')
    paragraphs:list[Paragraph]=Field(max_length=8)
    clarification:str|None
    limitation:str|None
    followups:list[str]=Field(max_length=3)

class ResearchTools:
    def __init__(self, corpus, domain='all', document_id=None, extra_terms=''):
        self.corpus=corpus;self.domain=domain;self.document_id=document_id
        self.extra_terms=extra_terms;self.evidence={};self.citable_ids=set();self.trace=[];self.questions=[]

    def record(self, result):
        for evidence in result.get('results',[])+result.get('pages',[]):self.evidence[evidence['id']]=evidence
        return result

    @staticmethod
    def evidence_for_agent(evidence):
        # Full metadata stays in the immutable corpus and read_document result.
        # Avoid repeating PDF metadata and file paths with every search/page hit.
        fields=('id','document_id','title','text','page','label','start','end','url','reader_url','generation','sha256','format','origin','warning','answer_excluded')
        return {k:evidence[k] for k in fields if k in evidence}

    def catalogue(self, args):return self.corpus.catalogue(args.get('query',''),self.domain,args.get('offset',0),min(20,args.get('limit',10)))
    def search(self,args):
        result=self.record(self.corpus.search((args['query']+' '+self.extra_terms).strip(),min(12,args.get('limit',8)),self.document_id,self.domain,args.get('offset',0)))
        return {**result,'results':[self.evidence_for_agent(e) for e in result['results']]}
    def read(self,args):
        if self.document_id and args['document_id']!=self.document_id:raise ValueError('This conversation is scoped to one document')
        result=self.record(self.corpus.read_document(args['document_id'],args.get('page',1),args.get('offset',0),args.get('max_chars',18000)))
        self.citable_ids.update(e['id'] for e in result['pages'])
        return {**result,'pages':[self.evidence_for_agent(e) for e in result['pages']]}
    def crm_search(self,args):return crm_store.search_records(args.get('query',''),args.get('collection','all'),args.get('location',''),min(20,args.get('limit',10)),args.get('offset',0))
    def crm_read(self,args):
        result=crm_store.read_record(args['record_id']);r=result['record'];identifier='crm:'+r['record_id']
        text=json.dumps(r,ensure_ascii=False,sort_keys=True)
        self.evidence[identifier]={'id':identifier,'document_id':r['record_id'],'title':r['name'],'page':1,'label':'Public CRM record','text':text,'url':result['snapshot']['source_url'],'reader_url':result['crm_url'],'format':'crm','origin':'public_snapshot','warning':r.get('verification_status',''),'retrieved_at':r.get('checked_on',''),'generation':result['snapshot']['version'],'matches':['crm']}
        self.citable_ids.add(identifier)
        return {'snapshot':result['snapshot'],'crm_url':result['crm_url'],'citation_id':identifier,'citable_text':text}
    def clarify(self,args):self.questions.append(args['question']);return {'question':args['question'],'instruction':'Return this question in clarification and wait for the user in the next conversation turn.'}

    def server(self):
        schemas={
            'browse_catalogue':('Browse every document with stable pagination and metadata; empty query lists the full catalogue.',{'query':str,'offset':int,'limit':int},self.catalogue),
            'search_documents':('Search all extracted pages with FTS5. Use multiple distinct searches for different concepts. All original warnings are retained.',{'query':str,'offset':int,'limit':int},self.search),
            'read_document':('Read a complete document one page at a time. Follow next_cursor for full page/document text; no text is silently omitted.',{'document_id':str,'page':int,'offset':int,'max_chars':int},self.read),
            'query_crm':('Browse or search the complete public CRM; collection is community, government or all. Filter by location. Not personal CRM notes.',{'query':str,'collection':str,'location':str,'offset':int,'limit':int},self.crm_search),
            'read_crm_record':('Read one complete CRM record with provenance and verification notes before citing it.',{'record_id':str},self.crm_read),
            'ask_clarifying_question':('Ask for a missing fact that materially changes the answer. Return it to the user and wait.',{'question':str},self.clarify),
        }
        built=[]
        for name,(description,schema,fn) in schemas.items():
            async def handler(args, fn=fn, name=name):
                try:
                    result=fn(args);self.trace.append({'tool':name,'arguments':args})
                    return {'content':[{'type':'text','text':json.dumps(result,ensure_ascii=False)}]}
                except (KeyError,ValueError) as error:
                    return {'content':[{'type':'text','text':str(error)}],'isError':True}
            built.append(tool(name,description,schema)(handler))
        self.names=['mcp__research__'+name for name in schemas]
        return create_sdk_mcp_server(name='research',version='1.0.0',tools=built)

def validate_answer(raw, readers, domain):
    result=AgentAnswer.model_validate(raw);paragraphs=[];cited={}
    for p in result.paragraphs:
        ids=[]
        for identifier in p.supports:
            evidence=readers.evidence.get(identifier)
            if not evidence or identifier not in readers.citable_ids or not evidence['text'].strip():raise ValueError('Citation must identify a source read in this conversation')
            if evidence.get('answer_excluded'):raise ValueError('This source span has a preserved answer exclusion')
            if identifier not in ids:ids.append(identifier)
            # Resolve the complete, exact source text like backend.chat does.
            # The model selects IDs; it never has to retype damaged PDF glyphs.
            cited[identifier]=evidence
        paragraphs.append({'text':p.text,'citations':ids})
    return {'status':'answered' if paragraphs else 'insufficient_evidence','summary_first':True,'paragraphs':paragraphs,'citations':list(cited.values()),'clarification':result.clarification or (readers.questions[-1] if readers.questions else None),'followups':result.followups,'library_notice':result.limitation,'outside_context':None,'domain':domain,'_dev':{'tool_calls':readers.trace,'citation_check':'Read-source ID validation and exact original text resolution; not automatic semantic acceptance.'}}

def agent_options(readers, prompt, proxy_url, proxy_token, budget_usd, effort='medium'):
    server=readers.server();cwd=STATE/'sdk-session';cwd.mkdir(exist_ok=True)
    return ClaudeAgentOptions(
        model=MODEL,tools=[],allowed_tools=readers.names,mcp_servers={'research':server},
        system_prompt=prompt,setting_sources=[],skills=[],plugins=[],agents={},
        cwd=str(cwd),max_turns=10,max_budget_usd=budget_usd,effort=effort,
        enable_file_checkpointing=False,
        env={'ANTHROPIC_API_KEY':proxy_token,'ANTHROPIC_AUTH_TOKEN':'','ANTHROPIC_BASE_URL':proxy_url,
             'CLAUDE_CODE_OAUTH_TOKEN':'','CLAUDE_CONFIG_DIR':str(STATE/'sdk-config'),
             'CLAUDE_CODE_USE_BEDROCK':'0','CLAUDE_CODE_USE_VERTEX':'0',
             'CLAUDE_CODE_MAX_OUTPUT_TOKENS':'4096','DISABLE_NONESSENTIAL_TRAFFIC':'1'},
        output_format={'type':'json_schema','schema':AgentAnswer.model_json_schema()},
        extra_args={'no-session-persistence':None},
    )

async def run_agent(request, corpus, config, proxy_url, proxy_token, remaining):
    readers=ResearchTools(corpus,request.domain,request.document_id,config['extra_retrieval_terms'])
    # Mandatory trust/citation rules remain outside the editable voice brief.
    prompt=(ROOT/'dev/agent-prompt.txt').read_text()+'\nAdditional answer style instructions:\n'+config['answer_brief']
    options=agent_options(readers,prompt,proxy_url,proxy_token,remaining,config['effort'])
    incoming=json.dumps({'question':request.question,'history':[m.model_dump() for m in request.history],'domain':request.domain},ensure_ascii=False)
    run_id=uuid4().hex
    diagnostic={'run_id':run_id,'started_at':datetime.now(timezone.utc).isoformat(),'status':'incomplete'}
    try:
        async for message in query(prompt=incoming,options=options):
            if isinstance(message,ResultMessage):
                diagnostic.update(sdk_subtype=message.subtype,sdk_is_error=message.is_error,sdk_reported_cost_usd=message.total_cost_usd,sdk_turns=message.num_turns)
                if message.is_error or not message.structured_output:raise ValueError('The agent did not complete a structured answer')
                diagnostic['status']='validating_citations'
                diagnostic['structured_answer']=message.structured_output
                diagnostic['citation_ids']=[p.get('supports') for p in message.structured_output.get('paragraphs',[])]
                diagnostic['read_source_ids']=sorted(readers.citable_ids)
                answer=validate_answer(message.structured_output,readers,request.domain)
                diagnostic['status']='verified_citations'
                answer['_dev'].update(run_id=run_id,sdk_reported_cost_usd=message.total_cost_usd,sdk_turns=message.num_turns)
                return answer
        raise ValueError('No agent result')
    except BaseException as error:
        # Exception messages and SDK stderr may contain source text or credentials.
        diagnostic['exception_type']=type(error).__name__
        raise
    finally:
        diagnostic['finished_at']=datetime.now(timezone.utc).isoformat()
        diagnostic['tool_calls']=[item['tool'] for item in readers.trace]
        folder=STATE/'diagnostics';folder.mkdir(mode=0o700,exist_ok=True)
        path=folder/('agent-'+run_id+'.json')
        with path.open('x') as output:
            path.chmod(0o600);json.dump(diagnostic,output,indent=2)
