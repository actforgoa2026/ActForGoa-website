"""Local-only bridge to the existing research API, preserving its usage accounting."""
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

UPSTREAM = 'https://research-production-b579.up.railway.app'

@asynccontextmanager
async def lifespan(app):
    async with httpx.AsyncClient(timeout=80, follow_redirects=False) as client:
        app.state.client = client
        yield

app = FastAPI(lifespan=lifespan)

@app.api_route('/{path:path}', methods=['GET', 'POST'])
async def forward(path: str, request: Request):
    allowed = path in ('api/status', 'api/search', 'api/chat', 'healthz') or path.startswith('api/documents/')
    if not allowed or (request.method == 'POST' and path != 'api/chat'):
        return Response(status_code=404)
    try:
        response = await app.state.client.request(
            request.method, UPSTREAM + '/' + path, params=request.query_params,
            content=await request.body(),
            headers={'Origin': 'https://actforgoa-field-guide.vercel.app', 'Content-Type':'application/json'},
        )
    except httpx.HTTPError:
        return Response('{"detail":"The live research API could not connect."}', status_code=502, media_type='application/json')
    headers = {key:value for key,value in response.headers.items() if key.lower() in ('content-type','content-disposition')}
    return Response(response.content, status_code=response.status_code, headers=headers)
