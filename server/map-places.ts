import type {IncomingMessage, ServerResponse} from 'node:http';

export type MapPlace = {id:string;name:string;detail:string;longitude:number;latitude:number};
export class PlaceSearchError extends Error {constructor(public status:number,message:string){super(message);}}

/** One bounded, cached Photon gateway shared by all visitors of the single-replica app.
 * Explicit searches only; no autocomplete, reverse lookup, or request logging.
 * https://github.com/komoot/photon#demo-server
 */
export function createPlaceSearch({fetcher=fetch,now=Date.now,endpoint=process.env.SATELLITE_GEOCODER_URL||'https://photon.komoot.io/api/'}={}) {
  const origin=new URL(endpoint);
  if(origin.protocol!=='https:'||origin.username||origin.password)throw Error('Geocoder must be an HTTPS endpoint without credentials.');
  const cache=new Map<string,{expires:number;places:MapPlace[]}>();
  let nextRequest=0,busy=false,day='',requests=0;
  return async(query:string):Promise<MapPlace[]>=>{
    const q=query.trim().replace(/\s+/g,' ');
    if(q.length<3||q.length>120||/[\x00-\x1f]/.test(q))throw new PlaceSearchError(400,'Enter a place or business name, between 3 and 120 characters.');
    const key=q.toLocaleLowerCase('en'),time=now(),saved=cache.get(key);
    if(saved&&saved.expires>time)return saved.places;
    const today=new Date(time).toISOString().slice(0,10);
    if(today!==day){day=today;requests=0;}
    if(busy||time<nextRequest)throw new PlaceSearchError(429,'Place search is busy. Try again in a few seconds.');
    if(requests>=400)throw new PlaceSearchError(429,'Place search has reached today’s limit. You can still pan, draw, or use your location.');
    busy=true;nextRequest=time+1500;requests++;
    try{
      const url=new URL(origin);url.search=new URLSearchParams({q,bbox:'73.5,14.7,74.6,16',limit:'5',lang:'en'}).toString();
      const response=await fetcher(url,{headers:{'Accept':'application/json','User-Agent':'ActForGoa/1.0 (+https://satellite-app-production.up.railway.app/map)'},signal:AbortSignal.timeout(8000),redirect:'error'});
      if(!response.ok)throw Error('Provider unavailable');
      if(Number(response.headers.get('content-length'))>100000)throw Error('Response too large');
      const reader=response.body?.getReader();if(!reader)throw Error('Missing response');
      let bytes=0;const chunks:Uint8Array[]=[];
      try{while(true){const chunk=await reader.read();if(chunk.done)break;bytes+=chunk.value.length;if(bytes>100000)throw Error('Response too large');chunks.push(chunk.value);}}finally{await reader.cancel();}
      const data=JSON.parse(Buffer.concat(chunks).toString('utf8'));
      if(!Array.isArray(data.features))throw Error('Invalid response');
      const places:MapPlace[]=[];
      for(const feature of data.features.slice(0,10)){
        const p=feature.properties,coordinates=feature.geometry?.coordinates;
        if(feature.geometry?.type!=='Point'||!Array.isArray(coordinates)||coordinates.length!==2||!p)continue;
        const [longitude,latitude]=coordinates;
        if(!Number.isFinite(longitude)||!Number.isFinite(latitude)||longitude<73.5||longitude>74.6||latitude<14.7||latitude>16||typeof p.name!=='string')continue;
        const name=p.name.slice(0,160),detail=[...new Set([p.street,p.district,p.city,p.state].filter((v):v is string=>typeof v==='string'&&v!==name))].join(', ').slice(0,240);
        places.push({id:String(p.osm_type||'')+String(p.osm_id||places.length),name,detail,longitude,latitude});
        if(places.length===5)break;
      }
      if(cache.size>=256)cache.delete(cache.keys().next().value!);
      cache.set(key,{expires:time+86400000,places});return places;
    }catch(error){if(error instanceof PlaceSearchError)throw error;throw new PlaceSearchError(502,'Place search is temporarily unavailable. Try again, or navigate the map.');}
    finally{busy=false;}
  };
}

export async function serveMapPlaces(req:IncomingMessage,res:ServerResponse,search:ReturnType<typeof createPlaceSearch>){
  res.setHeader('Content-Type','application/json; charset=utf-8');res.setHeader('Cache-Control','no-store');
  if(req.method!=='GET'){res.writeHead(405,{Allow:'GET'});return res.end(JSON.stringify({error:'Use search from the map.'}));}
  try{
    if((req.url?.length||0)>700)throw new PlaceSearchError(400,'Search is too long.');
    const url=new URL(req.url||'/','http://localhost');
    const places=await search(url.searchParams.get('q')||'');res.writeHead(200);res.end(JSON.stringify({places}));
  }catch(error){const e=error instanceof PlaceSearchError?error:new PlaceSearchError(502,'Place search is unavailable.');res.writeHead(e.status,e.status===429?{'Retry-After':'3'}:{});res.end(JSON.stringify({error:e.message}));}
}
