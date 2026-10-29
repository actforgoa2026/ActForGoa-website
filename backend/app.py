"""Local research API with explicit, bounded public-host configuration."""
import asyncio
import re
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache
import os
from pathlib import Path
import threading
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse, Response
import pymupdf
from starlette.middleware.trustedhost import TrustedHostMiddleware
from dotenv import load_dotenv
from .anthropic_answers import AnthropicAnswers, AnthropicAPIError, configured_model, maximum_cost, maximum_request_cost
from .domains import Domain
from .embeddings import ROOT
from .library import Library
from .hosting import public_config, PublicLimits, RequestSizeLimit, UsageLedgerUnavailable
from .chat import ChatRequest, answer_question, prepare_answer, retrieval_query

load_dotenv(ROOT/'.env.local')

def create_app(root=None, index_root=None, client=None):
    root=Path(root or os.getenv('RESEARCH_DATA_ROOT') or ROOT)
    public_origin,hosts=public_config()
    ledger_required=os.getenv('RESEARCH_REQUIRE_EXISTING_USAGE','1' if public_origin else '0')=='1'
    # Keep the same durable ledger path across releases; never reset production usage.
    limits=PublicLimits(root/'.research-usage',chats_per_day=min(100,int(os.getenv('RESEARCH_DAILY_ANSWER_LIMIT','100'))),
                        monthly_usd=min(5,float(os.getenv('RESEARCH_MONTHLY_BUDGET_USD','5'))),require_existing=ledger_required,
                        release_allowance=os.getenv('RESEARCH_RELEASE_ALLOWANCE_20261028')=='1',
                        hackathon_allowance=os.getenv('RESEARCH_HACKATHON_ALLOWANCE_20261029')=='1')
    model=configured_model()
    agent_enabled=os.getenv('RESEARCH_AGENT_ENABLED')=='1'
    @asynccontextmanager
    async def lifespan(app):
        try:app.state.library=Library(root,index_root)
        except (FileNotFoundError, KeyError, ValueError):app.state.library=None
        # Existing public services must restore their ledger, never silently start
        # a new allowance because a volume or data-root selector was misplaced.
        ledger_ready=limits.existing_ledger_ready()
        app.state.client=(client or (AnthropicAnswers(os.environ['ANTHROPIC_API_KEY']) if os.getenv('ANTHROPIC_API_KEY') and os.getenv('RESEARCH_CHAT_ENABLED')=='1' else None)) if ledger_ready else None
        app.state.agent=None
        if agent_enabled and app.state.client and app.state.library:
            from .production_agent import ProductionAgent
            app.state.agent=ProductionAgent(app.state.library,limits,root/'.research-agent',os.environ['ANTHROPIC_API_KEY'])
        yield
        if app.state.client and client is None:app.state.client.close()
        app.state.library=None
    app=FastAPI(title='ActForGoa research',lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=hosts)
    app.add_middleware(RequestSizeLimit)
    search_slots=threading.BoundedSemaphore(4)
    chat_slots=threading.BoundedSemaphore(2)

    @app.middleware('http')
    async def local_security(request:Request,call_next):
        origin=request.headers.get('origin')
        if request.method not in ['GET','HEAD','OPTIONS'] and origin:
            from urllib.parse import urlsplit
            if (public_origin and origin!=public_origin) or (not public_origin and urlsplit(origin).hostname not in ['localhost','127.0.0.1']):
                return JSONResponse({'detail':'This origin is not allowed to use the research service.'},status_code=403)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Cache-Control']='private, no-store'
        return response

    @app.exception_handler(KeyError)
    async def missing(request,error):return JSONResponse({'detail':'Document or index version not found.'},status_code=404)

    def library():
        if app.state.library is None:raise HTTPException(503,'Research index is not ready. Run the research index builder and restart the API.')
        return app.state.library

    @app.get('/healthz')
    def health():
        if app.state.library is None:raise HTTPException(503,'Research index is not ready.')
        return {'ready':True,'generation':app.state.library.generation}

    def retrieve(*args):
        if limits and not limits.allow_search():raise HTTPException(429,'Research is busy. Please try again in a minute.')
        if not search_slots.acquire(blocking=False):raise HTTPException(429,'Research is busy. Please try again shortly.')
        try:return library().search(*args)
        finally:search_slots.release()

    def chat_unavailable_reason():
        if not limits.existing_ledger_ready():
            return 'usage_ledger_unavailable' if (root/'.research-usage/answer-usage.sqlite').is_file() else 'usage_ledger_missing'
        if agent_enabled and not app.state.agent:return 'agent_not_configured'
        return None if app.state.client else 'not_configured'

    @app.get('/api/status')
    def status():
        lib=app.state.library
        reason=chat_unavailable_reason()
        if reason is None:
            try:
                from .agent_protocol import MAX_REQUEST_MICROUSD
                capacity=limits.preflight_single(MAX_REQUEST_MICROUSD if agent_enabled else maximum_request_cost(model),datetime.now(timezone.utc).date().isoformat())
                if not capacity['allowed']:reason=capacity['reason']
            except UsageLedgerUnavailable:reason='usage_ledger_unavailable'
        return {'search_ready':lib is not None,'chat_ready':bool(lib and reason is None),'generation':lib.generation if lib else None,
                'stats':lib.manifest['stats'] if lib else {},'model':model,'provider':'anthropic',
                'domains':['legal','ecology'],'domain_counts':lib.domain_counts() if lib else {'legal':0,'ecology':0},
                'outside_context_supported':not agent_enabled,'answer_mode':'agent_library_first' if agent_enabled else 'library_first',
                'agent':{'engine':'claude-agent-sdk','tools':['browse_catalogue','search_documents','read_document','query_crm','read_crm_record','ask_clarifying_question']} if app.state.agent else None,
                'chat_unavailable_reason':reason,
                'embedding_model':'all-MiniLM-L6-v2','search_mode':'zvec+fts5+rrf' if lib else 'unavailable'}

    @app.get('/api/search')
    def search(q:str=Query(min_length=1,max_length=2000),limit:int=Query(default=8,ge=1,le=20),document_id:str|None=None,generation:str|None=None,domain:Domain='all'):
        return {'results':retrieve(q,limit,document_id,generation,domain),'generation':generation or library().generation,'domain':domain}

    @app.get('/api/documents/{doc_id}')
    def document(doc_id:str,generation:str|None=None):return library().document(doc_id,generation)

    @app.get('/api/documents/{doc_id}/pages')
    def pages(doc_id:str,generation:str|None=None,start:int=Query(default=1,ge=1),limit:int=Query(default=10,ge=1,le=50)):
        return {'pages':library().pages(doc_id,generation,start,limit)}

    @app.get('/api/documents/{doc_id}/passages/{passage_id}')
    def passage(doc_id:str,passage_id:str,generation:str|None=None):
        """start/end are zero-based Python Unicode code-point offsets; end is exclusive."""
        if passage_id.startswith(doc_id+':p'):
            match=re.fullmatch(re.escape(doc_id)+r':p(\d+):(\d+):(\d+)',passage_id)
            if not match:raise KeyError('Passage not found')
            page,start,end=map(int,match.groups())
            rows=library().pages(doc_id,generation,page,1)
            if not rows or rows[0]['page']!=page or not 0<=start<end<=len(rows[0]['text']):raise KeyError('Passage not found')
            return {'page':page,'start':start,'end':end,'text':rows[0]['text'][start:end]}
        with library().connect(generation) as db:
            row=db.execute('SELECT page,start,end,text FROM chunks WHERE id=? AND doc_id=?',(passage_id,doc_id)).fetchone()
        if not row:raise KeyError('Passage not found')
        return dict(row)

    @app.get('/api/documents/{doc_id}/original')
    def original(doc_id:str,generation:str|None=None):
        path,meta=library().original(doc_id,generation)
        pdf=meta['format']=='pdf'
        return FileResponse(path,media_type='application/pdf' if pdf else 'application/octet-stream',
            filename=doc_id+path.suffix,content_disposition_type='attachment',
            headers={'Content-Security-Policy':"sandbox; default-src 'none'",'ETag':'"'+meta['sha256']+'"'})

    image_slots=threading.BoundedSemaphore(2)
    @lru_cache(maxsize=16)
    def render_page(doc_id,generation,page):
        path,meta=library().original(doc_id,generation)
        if meta['format']!='pdf':raise KeyError('Not a PDF')
        with image_slots, pymupdf.open(stream=path.read_bytes(),filetype='pdf') as pdf:
            if page>len(pdf):raise KeyError('Page not found')
            source=pdf[page-1]
            scale=min(2,2000/max(source.rect.width,source.rect.height))
            return source.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).tobytes('png')

    @app.get('/api/documents/{doc_id}/pages/{page}/image')
    def original_page(doc_id:str,page:int,generation:str|None=None):
        if page<1:raise KeyError('Page not found')
        return Response(render_page(doc_id,generation or library().generation,page),media_type='image/png')

    @app.get('/api/documents/{doc_id}/text',response_class=PlainTextResponse)
    def full_text(doc_id:str,generation:str|None=None):
        doc=library().document(doc_id,generation)
        with library().connect(generation) as db:
            rows=db.execute('SELECT label,text,warning FROM pages WHERE doc_id=? ORDER BY page',(doc_id,)).fetchall()
        body='\n\n'.join(f'=== {p["label"]} ===\n'+(f'[Extraction note: {p["warning"]}]\n' if p['warning'] else '')+p['text'] for p in rows)
        return PlainTextResponse(doc['title']+'\n'+doc['url']+'\n\n'+body,headers={'Content-Disposition':f'attachment; filename="{doc_id}.txt"'})

    def legacy_chat(request:ChatRequest):
        lib=library()
        if chat_unavailable_reason():raise HTTPException(503,'Answers are currently unavailable. You can still search and read the full sources.')
        if not request.question.strip():raise HTTPException(422,'Enter a question.')
        if not chat_slots.acquire(blocking=False):raise HTTPException(429,'Two answers are already being prepared. Please try again shortly.')
        try:
            # Include recent user context to resolve follow-ups, never treat model history as evidence.
            retrieval=retrieval_query(request)
            evidence=retrieve(retrieval,10,request.document_id,request.generation,request.domain)
            if not evidence and not request.include_outside_context:
                return {'status':'insufficient_evidence','paragraphs':[],'citations':[],'outside_context':None,
                        'domain':request.domain,'coverage':'none','library_notice':'Our library has no matching evidence. Try different terms.'}
            prepared=prepare_answer(request,evidence)
            receipt=limits.reserve_stage(maximum_cost(model,prepared[0]),datetime.now(timezone.utc).date().isoformat(),uuid4().hex,'draft')
            if not receipt['reserved']:
                raise HTTPException(429,'The answer budget has been reached. Search and full documents are still available.')
            return answer_question(app.state.client,model,request,evidence,prepared)
        except UsageLedgerUnavailable:
            raise HTTPException(503,'Answers are currently unavailable. You can still search and read the full sources.') from None
        except AnthropicAPIError as error:
            status=getattr(error,'status_code',None)
            detail='The answer service is unavailable. Search and full documents still work.'
            if status==401:detail='The answer service rejected its configured credential. Ask the maintainer to check it.'
            if status==429:detail='The answer service has reached its usage limit. Try again later or read the sources.'
            raise HTTPException(502,detail) from None
        except ValueError:
            raise HTTPException(502,'The answer could not be verified against its citations. Try again or read the sources.') from None
        finally:chat_slots.release()
    @app.post('/internal-agent/v1/messages/count_tokens')
    async def agent_count_tokens(request:Request):
        if not app.state.agent:raise HTTPException(404)
        return await app.state.agent.count_tokens(request)

    @app.post('/internal-agent/v1/messages')
    async def agent_messages(request:Request):
        if not app.state.agent:raise HTTPException(404)
        return await app.state.agent.messages(request)

    @app.post('/api/chat')
    async def chat(request:ChatRequest):
        if not agent_enabled:return await asyncio.to_thread(legacy_chat,request)
        library()
        if chat_unavailable_reason():raise HTTPException(503,'Answers are currently unavailable. Search and full documents still work.')
        if not request.question.strip():raise HTTPException(422,'Enter a question.')
        if not chat_slots.acquire(blocking=False):raise HTTPException(429,'Two investigations are already running. Please try again shortly.')
        try:return await app.state.agent.answer(request)
        except HTTPException:raise
        except UsageLedgerUnavailable:raise HTTPException(503,'Production accounting is unavailable. Search and full documents still work.') from None
        except Exception:raise HTTPException(502,'The investigation could not finish a verified answer. Any model attempts remain counted. Read the sources or refine your question.') from None
        finally:chat_slots.release()
    return app

app=create_app()
