"""Explicit public-host configuration and bounded public-service operations."""
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3
import threading
import time
from urllib.parse import urlsplit
from starlette.responses import JSONResponse

class RequestSizeLimit:
    def __init__(self, app, maximum=65536):self.app=app;self.maximum=maximum
    async def __call__(self, scope, receive, send):
        if scope['type']!='http' or scope['method'] not in ('POST','PUT','PATCH'):
            return await self.app(scope,receive,send)
        messages=[];size=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            size+=len(message.get('body',b''))
            if size>self.maximum:
                return await JSONResponse({'detail':'Request is too large.'},status_code=413)(scope,receive,send)
            messages.append(message)
            if not message.get('more_body',False):break
        async def buffered_receive():
            return messages.pop(0) if messages else await receive()
        await self.app(scope,buffered_receive,send)

def public_config():
    origin=os.getenv('RESEARCH_PUBLIC_ORIGIN','').rstrip('/')
    if not origin:return None,['localhost','127.0.0.1','testserver']
    url=urlsplit(origin)
    if url.scheme!='https' or not url.hostname or url.path or url.query or url.fragment or url.username:
        raise ValueError('RESEARCH_PUBLIC_ORIGIN must be an HTTPS origin')
    if os.getenv('RESEARCH_PUBLISH_CORPUS')!='1':
        raise ValueError('Public research requires RESEARCH_PUBLISH_CORPUS=1')
    hosts=['localhost','127.0.0.1','healthcheck.railway.app',url.hostname]
    for host in os.getenv('RESEARCH_ALLOWED_HOSTS','').split(',')+[os.getenv('RAILWAY_PUBLIC_DOMAIN','')]:
        host=host.strip()
        if host and (host=='*' or '/' in host or ':' in host):raise ValueError('Research hosts must be exact hostnames')
        if host:hosts.append(host)
    return origin,hosts

class PublicLimits:
    """Single-instance aggregate limits. No client identifiers are collected."""
    def __init__(self, root, search_per_minute=120, chats_per_day=100):
        self.root=Path(root);self.search_limit=search_per_minute;self.chat_limit=chats_per_day
        self.searches=deque();self.lock=threading.Lock()
    def allow_search(self):
        now=time.monotonic()
        with self.lock:
            while self.searches and self.searches[0]<now-60:self.searches.popleft()
            if len(self.searches)>=self.search_limit:return False
            self.searches.append(now);return True
    def reserve_answer(self):
        # Persistent reservation counts failed provider attempts too, preventing retries bypassing the budget.
        self.root.mkdir(parents=True,exist_ok=True)
        today=datetime.now(timezone.utc).date().isoformat()
        with self.lock,sqlite3.connect(self.root/'answer-usage.sqlite') as db:
            db.execute('CREATE TABLE IF NOT EXISTS usage(day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
            db.execute('BEGIN IMMEDIATE')
            count=db.execute('SELECT attempts FROM usage WHERE day=?',(today,)).fetchone()
            if count and count[0]>=self.chat_limit:return False
            db.execute('INSERT INTO usage VALUES (?,1) ON CONFLICT(day) DO UPDATE SET attempts=attempts+1',(today,))
            db.execute('DELETE FROM usage WHERE day<?',(today,))
        return True
