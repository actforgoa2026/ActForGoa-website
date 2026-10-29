"""Loopback-only local SDK workspace. Never imported by production."""
import asyncio
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
import secrets
from urllib.parse import urlparse
from typing import Literal
import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, PlainTextResponse, Response, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from .local_corpus import LocalCorpus, STATE
from .local_budget import BudgetUnavailable, DevBudget, MODEL, request_bound
from .chat import ChatRequest
from .research_agent import run_agent
from . import crm_store

ROOT=Path(__file__).resolve().parents[1]
CONFIG=STATE/'settings.json'
DEFAULT={'answer_brief':'Give a concise takeaway, then useful deeper detail. Explain unfamiliar terms simply.','extra_retrieval_terms':'','effort':'medium'}
crm_store.STATE=STATE/'crm'
PROXY_TOKEN=secrets.token_urlsafe(48)
budget=DevBudget()
slot=asyncio.Lock()

@asynccontextmanager
async def lifespan(app):
    app.state.corpus=LocalCorpus()
    yield

app=FastAPI(title='ActForGoa local research agent',lifespan=lifespan,docs_url=None,redoc_url=None)

@app.get('/api/curation')
def no_shared_curation():return {'starredIds':[]}

@app.get('/api/admin/session')
def no_admin():raise HTTPException(401,'Local research has no shared admin session.')

def corpus():return app.state.corpus
def config():return {**DEFAULT,**(json.loads(CONFIG.read_text()) if CONFIG.exists() else {})}
def generation(value):
    if value and value!=corpus().generation:raise HTTPException(404,'This dev copy contains the current generation only. Older generations remain in the preserved source archive.')

@app.middleware('http')
async def private_loopback(request, call_next):
    if request.client and request.client.host not in ('127.0.0.1','::1','testclient'):return Response(status_code=403)
    if request.url.hostname not in ('localhost','127.0.0.1','::1','testserver'):return Response(status_code=403)
    origin=request.headers.get('origin')
    allowed={'http://127.0.0.1:4276','http://localhost:4276','http://127.0.0.1:8093','http://localhost:8093'}
    if origin and origin not in allowed:return Response(status_code=403)
    if request.headers.get('sec-fetch-site')=='cross-site':return Response(status_code=403)
    if request.method not in ('GET','HEAD','OPTIONS') and request.headers.get('content-type','').split(';')[0]!='application/json':return Response(status_code=415)
    response=await call_next(request);response.headers['Cache-Control']='no-store';response.headers['X-Content-Type-Options']='nosniff'
    return response

@app.exception_handler(KeyError)
async def missing(request,error):return PlainTextResponse('Record or page not found',status_code=404)

@app.exception_handler(ValueError)
async def invalid(request,error):return PlainTextResponse(str(error),status_code=422)

@app.get('/api/status')
def status():
    lib=corpus();b=budget.status();key=bool(os.getenv('ANTHROPIC_API_KEY'))
    return {'search_ready':True,'chat_ready':b['ready'] and key,'provider':'anthropic','model':MODEL,
            'stats':lib.manifest['stats'],'generation':lib.generation,'domains':['legal','ecology'],
            'domain_counts':{d:sum(d in v for v in lib.domains.values()) for d in ('legal','ecology')},
            'search_mode':'fts5-all-extracted-pages','outside_context_supported':False,'dev_mode':True,
            'credential_ready':key,'budget':b,'chat_unavailable_reason':b['reason'] or (None if key else 'The server credential is unavailable.'),
            'crm':crm_store.stats()}

@app.get('/api/dev/config')
def read_config():return {**config(),'budget':budget.status()}

class Settings(BaseModel):
    model_config=ConfigDict(extra='forbid')
    answer_brief:str=Field(max_length=8000)
    extra_retrieval_terms:str=Field(default='',max_length=300)
    effort:Literal['low','medium','high'] = 'medium'

@app.put('/api/dev/config')
def write_config(settings:Settings):
    if settings.effort not in ('low','medium','high'):raise HTTPException(422,'Unknown effort')
    temporary=CONFIG.with_suffix('.tmp');temporary.write_text(json.dumps(settings.model_dump(),ensure_ascii=False));temporary.chmod(0o600);temporary.replace(CONFIG)
    return {'saved':True}

@app.get('/api/dev/catalogue')
def catalogue(q:str='',domain:str='all',offset:int=0,limit:int=20):return corpus().catalogue(q,domain,offset,limit)

@app.get('/api/search')
def search(q:str=Query(min_length=1,max_length=2000),domain:str='all',limit:int=8,offset:int=0,document_id:str|None=None,generation:str|None=None):
    if generation and generation!=corpus().generation:raise HTTPException(404,'Generation unavailable in this dev copy')
    return corpus().search((q+' '+config()['extra_retrieval_terms']).strip(),limit,document_id,domain,offset)

@app.get('/api/documents/{doc_id}')
def document(doc_id:str,generation:str|None=None):
    globals()['generation'](generation);return corpus().document(doc_id)

@app.get('/api/documents/{doc_id}/pages')
def pages(doc_id:str,generation:str|None=None,start:int=1,limit:int=10):
    globals()['generation'](generation);return {'pages':corpus().pages(doc_id,start,limit)}

@app.get('/api/documents/{doc_id}/passages/{passage_id}')
def passage(doc_id:str,passage_id:str,generation:str|None=None):
    globals()['generation'](generation)
    if passage_id.startswith(doc_id+':p'):
        _,page,start,end=passage_id.split(':');return corpus().evidence(doc_id,int(page[1:]),int(start),int(end))
    with corpus().connect() as db:
        row=db.execute('SELECT page,start,end,text FROM chunks WHERE id=? AND doc_id=?',(passage_id,doc_id)).fetchone()
    if not row:raise KeyError('Passage not found')
    return dict(row)

@app.get('/api/documents/{doc_id}/original')
def original(doc_id:str,generation:str|None=None):
    globals()['generation'](generation);path,meta=corpus().original(doc_id)
    return FileResponse(path,media_type='application/pdf' if meta['format']=='pdf' else 'application/octet-stream',filename=doc_id+path.suffix,headers={'Content-Security-Policy':"sandbox; default-src 'none'",'ETag':'"'+meta['sha256']+'"'})

@app.get('/api/documents/{doc_id}/text')
def text_document(doc_id:str,generation:str|None=None):
    globals()['generation'](generation);corpus().document(doc_id)
    return FileResponse(corpus().root/'agent-documents'/(doc_id+'.txt'),media_type='text/plain; charset=utf-8',filename=doc_id+'.txt')

@app.get('/api/documents/{doc_id}/pages/{page}/image')
def page_image(doc_id:str,page:int,generation:str|None=None):
    import pymupdf
    globals()['generation'](generation);path,meta=corpus().original(doc_id)
    if meta['format']!='pdf':raise KeyError('Not a PDF')
    with pymupdf.open(path) as pdf:
        if not 1<=page<=len(pdf):raise KeyError('Page outside document')
        p=pdf[page-1];scale=min(2,1800/max(p.rect.width,p.rect.height))
        return Response(p.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).tobytes('png'),media_type='image/png')

@app.get('/api/dev/crm/stats')
def crm_stats():return crm_store.stats()
@app.get('/api/dev/crm/search')
def crm_search(q:str='',collection:str='all',location:str='',offset:int=0,limit:int=20):return crm_store.search_records(q,collection,location,limit,offset)
@app.get('/api/dev/crm/records/{record_id}')
def crm_record(record_id:str):return crm_store.read_record(record_id)

@app.post('/api/chat')
async def chat(request:ChatRequest):
    b=budget.status()
    if not b['ready']:raise HTTPException(503,b['reason'])
    if not os.getenv('ANTHROPIC_API_KEY'):raise HTTPException(503,'The server credential is unavailable.')
    generation(request.generation)
    if slot.locked():raise HTTPException(429,'Another local answer is running.')
    async with slot:
        try:
            return await asyncio.wait_for(run_agent(request,corpus(),config(),os.getenv('ACTFORGOA_AGENT_PROXY','http://127.0.0.1:8093/provider'),PROXY_TOKEN,b['remaining_usd']),timeout=180)
        except Exception:
            raise HTTPException(502,'The local agent could not finish a verified answer. Any provider reservations remain counted. Browse the sources or refine the question.') from None

def authenticate_proxy(request):
    if not secrets.compare_digest(request.headers.get('x-api-key',''),PROXY_TOKEN) or request.headers.get('origin'):raise HTTPException(403,'SDK transport only')

@app.post('/provider/v1/messages/count_tokens')
async def count_tokens(request:Request):
    authenticate_proxy(request);raw=await request.body()
    return {'input_tokens':len(raw)+16384}

@app.post('/provider/v1/messages')
async def messages(request:Request):
    authenticate_proxy(request)
    raw=await request.body()
    if len(raw)>180000:raise HTTPException(413,'Local request limit')
    payload=json.loads(raw)
    # Fix output cap before reservation; every SDK retry is a new charged attempt.
    payload['max_tokens']=min(4096,payload.get('max_tokens',4096))
    try:amount=request_bound(payload);budget.reserve(amount)
    except (BudgetUnavailable,ValueError) as error:raise HTTPException(429,str(error)) from None
    key=os.getenv('ANTHROPIC_API_KEY')
    if not key:raise HTTPException(503,'Server credential unavailable')
    client=httpx.AsyncClient(timeout=90,follow_redirects=False)
    try:
        upstream=await client.send(client.build_request('POST','https://api.anthropic.com/v1/messages',headers={'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json'},json=payload),stream=True)
    except Exception:
        await client.aclose();raise HTTPException(502,'Provider connection failed; reservation retained.') from None
    async def stream():
        try:
            async for block in upstream.aiter_bytes():yield block
        finally:await upstream.aclose();await client.aclose()
    return StreamingResponse(stream(),status_code=upstream.status_code,media_type=upstream.headers.get('content-type','application/json'))
