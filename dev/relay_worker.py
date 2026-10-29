"""Outbound HTTPS relay to the private sandbox; local code stays live and editable."""
import asyncio
import base64
import json
from pathlib import Path
import httpx

STATE = Path('/workspace/.research-private/connection.json')
RELOAD = '''<script>let revision;setInterval(async()=>{try{let r=await fetch('/api/dev/revision');if(!r.ok)return;let value=(await r.json()).frontend;if(revision&&revision!==value)location.reload();revision=value;}catch{}},2000);</script>'''

async def main():
    state=json.loads(STATE.read_text())
    headers={'Authorization':'Bearer '+state['worker']}
    async with httpx.AsyncClient(timeout=110,headers=headers) as remote, httpx.AsyncClient(timeout=90,trust_env=False) as local:
        async def forward(item):
            try:
                if not item['path'].startswith('/') or item['path'].startswith('//'):raise ValueError('Invalid path')
                response=await local.request(item['method'],'http://127.0.0.1:4176'+item['path'],headers=item['headers'],content=base64.b64decode(item['body']))
                content=response.content
                if 'text/html' in response.headers.get('content-type',''):
                    content=content.replace(b'</body>',RELOAD.encode()+b'</body>') if b'</body>' in content else content+RELOAD.encode()
                result={'status':response.status_code,'headers':{k:v for k,v in response.headers.items() if k.lower() in ['content-type','content-disposition','cache-control']},'body':base64.b64encode(content).decode()}
            except Exception:
                result={'status':502,'headers':{'content-type':'application/json'},'body':base64.b64encode(b'{"detail":"The local development server could not respond."}').decode()}
            try:await remote.post(state['url']+'/__relay/result/'+item['id'],json=result)
            except httpx.HTTPError:pass
        tasks=set()
        print('Private development relay connected',flush=True)
        while True:
            try:
                response=await remote.post(state['url']+'/__relay/poll');response.raise_for_status()
                for item in response.json()['requests']:
                    task=asyncio.create_task(forward(item));tasks.add(task);task.add_done_callback(tasks.discard)
            except httpx.HTTPError:
                await asyncio.sleep(2)

if __name__=='__main__':asyncio.run(main())
