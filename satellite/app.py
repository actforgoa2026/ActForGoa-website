"""Authenticated REST and stateless MCP over the same bounded service."""
from contextlib import asynccontextmanager
import hmac
import os
from pathlib import Path
import re
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from .domain import CatalogRequest, CompareRequest, Query, DomainError
from .service import SatelliteService


def create_app(service=None):
    service = service or SatelliteService(str(Path(os.getenv('SATELLITE_DATA_DIR','.reports/satellite'))/'jobs.sqlite'))
    hosts = ['localhost', 'localhost:*', '127.0.0.1', '127.0.0.1:*', '[::1]', '[::1]:*']
    origins = ['http://localhost', 'http://localhost:*', 'http://127.0.0.1', 'http://127.0.0.1:*']
    public_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
    if public_domain and re.fullmatch(r'[a-zA-Z0-9.-]+', public_domain):
        hosts.append(public_domain)
        origins.append('https://' + public_domain)
    mcp = FastMCP('ActForGoa observations', stateless_http=True, json_response=True,
                  transport_security=TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=origins))

    @mcp.tool()
    def plan_goa_observation(question: str, bbox: list[float] | None = None):
        """Interpret a question; no observations are claimed by planning."""
        return service.plan(Query(question=question, area={'bbox':bbox} if bbox else None))

    @mcp.tool()
    def list_goa_observations(bbox: list[float], start_date: str, end_date: str):
        """List actual Sentinel-2 acquisitions for a small selected Goa area."""
        return service.catalog(CatalogRequest(area={'bbox':bbox},start_date=start_date,end_date=end_date))

    @mcp.tool()
    def compare_goa_observations(bbox: list[float], start_date: str, end_date: str, before_id: str, after_id: str, intent: str):
        """Start a bounded comparison of two catalog scenes; returns a job ID."""
        return service.compare(CompareRequest(area={'bbox':bbox},start_date=start_date,end_date=end_date,before_id=before_id,after_id=after_id,intent=intent),'mcp')

    @mcp.tool()
    def get_goa_comparison(job_id: str):
        """Read an MCP-created comparison and its evidence. Website jobs are separate."""
        return service.store.get(job_id,'mcp')

    @asynccontextmanager
    async def lifespan(app):
        async with mcp.session_manager.run():
            yield
        service.close()

    app = FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)
    app.state.service = service

    @app.middleware('http')
    async def protect(request: Request, call_next):
        def reject(status, message, code='invalid_request'):
            return JSONResponse({'error':message,'code':code},status_code=status,
                                headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})
        if request.url.path != '/healthz':
            mcp_request = request.url.path.startswith('/mcp')
            expected = os.getenv('SATELLITE_MCP_TOKEN' if mcp_request else 'SATELLITE_SERVICE_TOKEN','')
            actual = request.headers.get('authorization','')
            if len(expected) < 32 or not hmac.compare_digest(actual, 'Bearer '+expected):
                return reject(401, 'Authentication required.', 'unauthorized')
            actor = request.headers.get('x-actor-id','')
            if not mcp_request and not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',actor):
                return reject(403, 'A verified user identity is required.')
            request.state.actor = actor
            try:
                declared_size = int(request.headers.get('content-length','0'))
            except ValueError:
                return reject(400, 'Invalid request length.')
            if declared_size > 16_384:
                return reject(413, 'Request too large.')
            chunks, size = [], 0
            async for chunk in request.stream():
                size += len(chunk)
                if size > 16_384:
                    return reject(413, 'Request too large.')
                chunks.append(chunk)
            request._body = b''.join(chunks)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @app.exception_handler(DomainError)
    async def domain_error(request, error):
        return JSONResponse({'error':error.message,'code':error.code},status_code=error.status)

    @app.exception_handler(RequestValidationError)
    async def invalid(request,error):
        # Pydantic input/context can contain user prompts; do not echo whole bodies.
        return JSONResponse({'error':'Check the Goa area, dates and selected observations. Areas must be at most 25 km² and date ranges at most 120 days.','code':'invalid_request'},status_code=422)

    @app.exception_handler(httpx.HTTPError)
    async def upstream_error(request,error):
        return JSONResponse({'error':'An external provider could not respond. No result was inferred.','code':'provider_unavailable'},status_code=502)

    @app.get('/healthz')
    def health():
        return {'status':'ok','service':'goa-satellite'}

    @app.get('/status')
    def status():
        return {'imagery_ready':bool(os.getenv('CDSE_CLIENT_ID') and os.getenv('CDSE_CLIENT_SECRET')),
                'planner_ready':bool(os.getenv('ANTHROPIC_API_KEY')),'decisions_ready':bool(os.getenv('OPENAI_API_KEY')),
                'statewide_ready':False,'validation':'pending','scope':'Goa only','max_area_km2':25}

    @app.post('/plan')
    def plan(query:Query):
        return service.plan(query)

    @app.post('/catalog')
    def catalog(query:CatalogRequest):
        return service.catalog(query)

    @app.post('/compare',status_code=202)
    def compare(query:CompareRequest,request:Request):
        return service.compare(query,request.state.actor)

    @app.get('/jobs/{job_id}')
    def job(job_id:str,request:Request):
        return service.store.get(job_id,request.state.actor)

    app.mount('/',mcp.streamable_http_app())
    return app
