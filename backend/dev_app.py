"""Private-development API: editable local pipeline, read-only live source index.

Never mounted by the production application. The separate dev allowance defaults
 to zero and must be explicitly authorized outside browser-editable settings.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import threading
import time
from uuid import uuid4
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from .answer_brief import ANSWER_BRIEF
from .anthropic_answers import AnthropicAnswers, maximum_cost
from .chat import ChatRequest, prepare_answer, normalize_answer, retrieval_query
from .hosting import PublicLimits
from .retrieval_intent import expand_retrieval_query

ROOT=Path(__file__).resolve().parents[1]
STATE=Path('/workspace/.research-private')
CONFIG=STATE/'settings.json'
BUDGET=STATE/'allowance.json'
UPSTREAM='https://research-production-b579.up.railway.app'
MODEL='claude-sonnet-5-5'
DEFAULT={'answer_brief':ANSWER_BRIEF,'extra_retrieval_terms':'','top_k':10,'expand_intent':True,'effort':'medium'}
app=FastAPI(title='Private ActForGoa research development')
slot=threading.BoundedSemaphore(1)

def config():
    return {**DEFAULT,**(json.loads(CONFIG.read_text()) if CONFIG.exists() else {})}

def allowance():
    if not BUDGET.exists():return 0
    data=json.loads(BUDGET.read_text())
    if datetime.now(timezone.utc).isoformat()>data['expires_at']:return 0
    return min(2,max(0,float(data['usd'])))

def limits():
    return PublicLimits(STATE/'usage',chats_per_day=30,monthly_usd=allowance())

def source_search(question,domain,limit=10,document=None,generation=None):
    cfg=config();query=expand_retrieval_query(question) if cfg['expand_intent'] else question
    query=(query+' '+cfg['extra_retrieval_terms']).strip()[:2000]
    params={'q':query,'domain':domain,'limit':limit}
    if document:params['document_id']=document
    if generation:params['generation']=generation
    with httpx.Client(timeout=30) as client:
        response=client.get(UPSTREAM+'/api/search',params=params)
        if response.status_code!=200:raise HTTPException(502,'The read-only source index could not respond.')
        return response.json(),query

@app.middleware('http')
async def local_only(request:Request,call_next):
    if request.client and request.client.host not in ('127.0.0.1','::1'):
        return Response(status_code=403)
    response=await call_next(request)
    response.headers['Cache-Control']='no-store'
    return response

@app.get('/api/status')
def status():
    with httpx.Client(timeout=20) as client:
        source=client.get(UPSTREAM+'/api/status');source.raise_for_status();data=source.json()
    amount=allowance();ready=bool(amount and os.getenv('ANTHROPIC_API_KEY'))
    if ready:
        from .anthropic_answers import maximum_request_cost
        ready=limits().preflight_single(maximum_request_cost(MODEL),datetime.now(timezone.utc).date().isoformat())['allowed']
    return {**data,'chat_ready':ready,'model':MODEL,'provider':'anthropic','dev_mode':True,'dev_budget_usd':amount,'chat_unavailable_reason':None if ready else 'dev_allowance_not_available'}

@app.get('/api/dev/config')
def read_config():return {**config(),'budget_usd':allowance(),'source_mode':'Read-only live source index; local retrieval and generation pipeline'}

class Settings(BaseModel):
    answer_brief:str=Field(max_length=8000)
    extra_retrieval_terms:str=Field(default='',max_length=300)
    top_k:int=Field(default=10,ge=1,le=20)
    expand_intent:bool=True
    effort:str='medium'

@app.put('/api/dev/config')
def write_config(settings:Settings):
    if settings.effort not in ('low','medium','high','xhigh'):raise HTTPException(422,'Unknown effort level')
    STATE.mkdir(mode=0o700,exist_ok=True);temporary=CONFIG.with_suffix('.tmp');temporary.write_text(json.dumps(settings.model_dump()));temporary.replace(CONFIG)
    return {'saved':True,'applies_to':'next request; no build or deployment'}

@app.get('/api/dev/revision')
def revision():
    paths=list((ROOT/'src').rglob('*'))+[ROOT/'dev/workbench.html']
    signature='|'.join(f'{p}:{p.stat().st_mtime_ns}' for p in paths if p.is_file())
    return {'frontend':hashlib.sha256(signature.encode()).hexdigest()}

@app.get('/api/search')
def search(q:str,domain:str='all',limit:int=8,document_id:str|None=None,generation:str|None=None):
    if domain not in ('all','legal','ecology'):raise HTTPException(422,'Unknown collection')
    result,_=source_search(q,domain,min(20,max(1,limit)),document_id,generation)
    return result

@app.post('/api/chat')
def chat(request:ChatRequest):
    if not allowance():raise HTTPException(503,'Dev AI testing is waiting for its separate spend allowance. Source search and settings are available.')
    if not os.getenv('ANTHROPIC_API_KEY'):raise HTTPException(503,'The workspace provider credential is not configured.')
    if not slot.acquire(blocking=False):raise HTTPException(429,'One development answer is already running.')
    started=time.perf_counter()
    try:
        cfg=config();result,query=source_search(retrieval_query(request),request.domain,cfg['top_k'],request.document_id,request.generation)
        retrieved=time.perf_counter();payload,selected=prepare_answer(request,result['results'])
        payload['system']=payload['system'].replace(ANSWER_BRIEF,cfg['answer_brief'])
        payload['output_config']={'effort':cfg['effort']}
        receipt=limits().reserve_stage(maximum_cost(MODEL,payload),datetime.now(timezone.utc).date().isoformat(),uuid4().hex,'draft')
        if not receipt['reserved']:raise HTTPException(429,'The separate dev testing allowance has been reached.')
        client=AnthropicAnswers(os.environ['ANTHROPIC_API_KEY'])
        try:raw=client.answer(MODEL,payload)
        finally:client.close()
        provider_done=time.perf_counter();answer=normalize_answer(raw,request,selected)
        answer['_dev']={'retrieval_query':query,'selected_sources':len(selected),'retrieval_ms':round((retrieved-started)*1000),'provider_ms':round((provider_done-retrieved)*1000),'total_ms':round((time.perf_counter()-started)*1000),'effort':cfg['effort']}
        return answer
    except HTTPException:raise
    except Exception as error:
        raise HTTPException(502,'The development answer failed or could not be validated. Its reservation remains counted.') from error
    finally:slot.release()

@app.get('/api/documents/{path:path}')
def document(path:str,request:Request):
    with httpx.Client(timeout=30) as client:
        response=client.get(UPSTREAM+'/api/documents/'+path,params=request.query_params)
    return Response(response.content,status_code=response.status_code,headers={k:v for k,v in response.headers.items() if k in ('content-type','content-disposition')})


@app.get('/api/dev/crm/stats')
def crm_stats():
    from .crm_store import stats
    return stats()

@app.get('/api/dev/crm/search')
def crm_search(q:str='',collection:str='community',location:str='',limit:int=20,offset:int=0):
    from .crm_store import search_records
    try:return search_records(q,collection,location,limit,offset)
    except ValueError as error:raise HTTPException(422,str(error)) from error

@app.get('/api/dev/crm/records/{record_id}')
def crm_record(record_id:str):
    from .crm_store import read_record
    try:return read_record(record_id)
    except KeyError as error:raise HTTPException(404,'CRM record not found') from error
