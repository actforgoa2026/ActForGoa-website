"""Local research API with explicit, bounded public-host configuration."""
from contextlib import asynccontextmanager
from functools import lru_cache
import os
import logging
from pathlib import Path
import threading
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse, Response
import pymupdf
from starlette.middleware.trustedhost import TrustedHostMiddleware
from dotenv import load_dotenv
from openai import APIError
from pydantic import ValidationError
from .embeddings import ROOT
from .library import Library
from .hosting import public_config, PublicLimits, RequestSizeLimit
from .chat import ChatRequest, answer_question, prepare_answer, AnswerCache
from .providers import chat_config
from .anthropic_provider import AnthropicAPIError

load_dotenv(ROOT/'.env.local')

def create_app(root=None, index_root=None, client=None):
    root=Path(root or os.getenv('RESEARCH_DATA_ROOT') or ROOT)
    public_origin,hosts=public_config()
    limits=PublicLimits(Path(os.getenv('RESEARCH_USAGE_ROOT') or root/'.research-usage'),chats_per_day=int(os.getenv('RESEARCH_DAILY_ANSWER_LIMIT','100')),
                        monthly_usd=os.getenv('RESEARCH_MONTHLY_ANSWER_BUDGET_USD','5'))
    config=chat_config()
    answers=AnswerCache()
    @asynccontextmanager
    async def lifespan(app):
        try:app.state.library=Library(root,index_root)
        except (FileNotFoundError, KeyError, ValueError):app.state.library=None
        app.state.client=client or config.client()
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

    @app.get('/api/status')
    def status():
        lib=app.state.library
        return {'search_ready':lib is not None,'chat_ready':bool(lib and app.state.client),'generation':lib.generation if lib else None,
                'stats':lib.manifest['stats'] if lib else {},'model':config.model,
                'provider':config.provider,'provider_label':config.label,
                'embedding_model':'all-MiniLM-L6-v2','search_mode':'zvec+fts5+rrf' if lib else 'unavailable'}

    @app.get('/api/search')
    def search(q:str=Query(min_length=1,max_length=2000),limit:int=Query(default=8,ge=1,le=20),document_id:str|None=None,generation:str|None=None):
        return {'results':retrieve(q,limit,document_id,generation),'generation':generation or library().generation}

    @app.get('/api/documents/{doc_id}')
    def document(doc_id:str,generation:str|None=None):return library().document(doc_id,generation)

    @app.get('/api/documents/{doc_id}/pages')
    def pages(doc_id:str,generation:str|None=None,start:int=Query(default=1,ge=1),limit:int=Query(default=10,ge=1,le=50)):
        return {'pages':library().pages(doc_id,generation,start,limit)}

    @app.get('/api/documents/{doc_id}/passages/{passage_id}')
    def passage(doc_id:str,passage_id:str,generation:str|None=None):
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

    @app.post('/api/chat')
    def chat(request:ChatRequest):
        lib=library()
        if not app.state.client:raise HTTPException(503,'Answers are not configured yet. You can still search and read the full sources.')
        if not request.question.strip():raise HTTPException(422,'Enter a question.')
        if not chat_slots.acquire(blocking=False):raise HTTPException(429,'Two answers are already being prepared. Please try again shortly.')
        try:
            # Include recent user context to resolve follow-ups, never treat model history as evidence.
            previous=next((m.content for m in reversed(request.history) if m.role=='user'),'')
            retrieval=request.question+(' '+previous[:500] if len(request.question.split())<8 else '')
            evidence=retrieve(retrieval,10,request.document_id,request.generation)
            if not evidence:return {'status':'insufficient_evidence','paragraphs':[],'citations':[],'notice':'No evidence was found. Try different terms.'}
            prepared=prepare_answer(request,evidence)
            cache_key=answers.key(config,prepared) if not request.history else None
            cached=answers.get(cache_key) if cache_key else None
            if cached is not None:return cached
            if not limits.reserve_answer(config.maximum_cost_microusd(prepared.input_token_bound)):
                raise HTTPException(429,'The answer allowance has been reached. You can still search and read the full sources.')
            answer=answer_question(app.state.client,config,prepared)
            if cache_key:answers.put(cache_key,answer)
            return answer
        except (APIError, AnthropicAPIError) as error:
            status=getattr(error,'status_code',None)
            detail='The answer service is unavailable. Search and full documents still work.'
            if status==401:detail='The answer service rejected its configured credential. Ask the maintainer to check it.'
            if status==402:detail='The answer service has no available credit. Search and full documents still work.'
            if status==429:detail='The answer service has reached its usage limit. Try again later or read the sources.'
            raise HTTPException(502,detail) from None
        except ValueError as error:
            # Log failure categories only: never provider payloads, questions or evidence.
            reason=','.join(e['type']+':'+'.'.join(map(str,e['loc'])) for e in error.errors(include_input=False)) if isinstance(error,ValidationError) else str(error)
            logging.getLogger(__name__).warning('Answer validation failed: %s',reason)
            raise HTTPException(502,'The answer could not be verified against its citations. Try again or read the sources.') from None
        finally:chat_slots.release()
    return app

app=create_app()
