"""Read-only ecology passage retrieval; never bypass research answer acceptance."""
from datetime import datetime, timezone
import json
import os
import re
from urllib.parse import urlsplit
import httpx

TOPICS = {'canopy_loss':'Goa forests vegetation seasonal changes', 'surface_water':'Goa rivers wetlands seasonal water tides',
          'land_change':'Goa development land use ecological impacts', 'waste':'Goa waste dumping pollution', 'fire':'Goa forest fires vegetation'}


class EcologyContext:
    def __init__(self, client):
        self.http=client

    def search(self, question, intent):
        unavailable={'state':'unavailable','sources':[], 'message':'Ecology-library context could not be retrieved. The imagery evidence is retained.'}
        raw=os.getenv('SATELLITE_RESEARCH_ORIGIN','')
        if not raw:
            return {**unavailable,'state':'not_configured','message':'The ecology-library connection is not configured for this service.'}
        try:
            origin=urlsplit(raw)
            local=origin.scheme=='http' and origin.hostname in {'localhost','127.0.0.1'} and os.getenv('SATELLITE_ALLOW_LOCAL_RESEARCH')=='true'
            if (origin.scheme!='https' and not local) or not origin.netloc or origin.username or origin.password or origin.path not in {'','/'} or origin.query or origin.fragment:
                return unavailable
            query=(question.strip()+' '+TOPICS[intent]).strip()[:1500]
            with self.http.stream('GET',raw.rstrip('/')+'/api/search', params={'q':query,'domain':'ecology','limit':4},timeout=8,follow_redirects=False) as response:
                if response.status_code!=200:return unavailable
                chunks=[];size=0
                for chunk in response.iter_bytes():
                    size+=len(chunk)
                    if size>512_000:return unavailable
                    chunks.append(chunk)
            body=json.loads(b''.join(chunks))
            if body.get('domain')!='ecology' or not isinstance(body.get('results'),list):return unavailable
            sources=[]
            for source in body['results'][:4]:
                if not isinstance(source,dict):continue
                if any(not isinstance(source.get(key),str) or not source[key] for key in ('id','title','text','url','reader_url','generation')):continue
                if source.get('domains') and 'ecology' not in source['domains']:continue
                publisher=urlsplit(source['url']);reader=urlsplit(source['reader_url'])
                if publisher.scheme not in {'https','http'} or not publisher.netloc or publisher.username or publisher.password:continue
                if reader.scheme or reader.netloc or not re.fullmatch(r'/documents/[A-Za-z0-9_-]{1,200}',reader.path):continue
                sources.append({key:source[key][:bound] for key,bound in [('id',300),('title',500),('text',1800),('url',2000),('reader_url',2000),('generation',200)]} |
                    {'label':str(source.get('label',''))[:120],'retrieved_at':str(source.get('retrieved_at',''))[:100],
                     'warning':str(source.get('warning',''))[:500],'excerpt_truncated':len(source['text'])>1800})
            return {'state':'available' if sources else 'no_matches','sources':sources,'query':query,
                'searched_at':datetime.now(timezone.utc).isoformat(),
                'message':'These library passages provide context. They do not establish the cause of this observed change or current conditions at this location.'}
        except (httpx.HTTPError,ValueError,TypeError,KeyError,AttributeError):
            return unavailable
