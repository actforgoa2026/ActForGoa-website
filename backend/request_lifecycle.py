"""ASGI request clock/security without a middleware task hiding disconnects."""
import time
from urllib.parse import urlsplit

from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse


class RequestLifecycle:
    def __init__(self, app, public_origin=None):
        self.app, self.public_origin = app, public_origin

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        scope.setdefault('state', {})['request_started_at'] = time.monotonic()
        origin = Headers(scope=scope).get('origin')
        if scope['method'] not in ('GET', 'HEAD', 'OPTIONS') and origin:
            if ((self.public_origin and origin != self.public_origin)
                    or (not self.public_origin and urlsplit(origin).hostname not in ('localhost', '127.0.0.1'))):
                response = JSONResponse({'detail': 'This origin is not allowed to use the research service.'}, status_code=403)
                return await response(scope, receive, send)

        async def guarded_send(message):
            if message['type'] == 'http.response.start':
                headers = MutableHeaders(scope=message)
                headers['X-Content-Type-Options'] = 'nosniff'
                headers['Referrer-Policy'] = 'no-referrer'
                headers['Cache-Control'] = 'private, no-store'
            await send(message)
        await self.app(scope, receive, guarded_send)
