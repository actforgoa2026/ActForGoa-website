"""Explicit test-only UI server. No requests reach OpenAI; do not use for real answers.

Run: .venv/bin/python -m uvicorn tests.research.ui_fixture_server:app --host 127.0.0.1 --port 8092
Requires npm run build and the real research index. Stop after browser verification.
"""
import json
import httpx
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from backend.app import create_app
from backend.embeddings import ROOT

def provider(request):
    payload=json.loads(json.loads(request.content)['input'][-1]['content'])
    evidence=payload['evidence']
    output={'status':'answered','paragraphs':[
        {'text':'Interface test fixture. Live model generation is not being tested. This response checks that a citation opens the exact retrieved passage and its full source document.','citations':[evidence[0]['id']]},
        {'text':'The source cards below contain real passages from the local archive. Their page numbers, saved originals and document versions can be checked through the reader.','citations':[evidence[1]['id']]}]}
    return httpx.Response(200,json={'id':'resp_ui_fixture','object':'response','created_at':1,'status':'completed','model':'gpt-5-mini','output':[{'type':'message','id':'msg_ui_fixture','role':'assistant','status':'completed','content':[{'type':'output_text','text':json.dumps(output),'annotations':[]}]}]})

client=OpenAI(api_key='test-fixture-only',http_client=httpx.Client(transport=httpx.MockTransport(provider)))
app=create_app(client=client)
app.mount('/assets',StaticFiles(directory=ROOT/'dist/assets'))
app.mount('/data',StaticFiles(directory=ROOT/'public/data'))
@app.get('/{path:path}')
def frontend(path:str):return FileResponse(ROOT/'dist/index.html')
