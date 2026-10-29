import type {IncomingMessage, ServerResponse} from 'node:http';

/** Keep one rate-limited geocoder gateway, including requests from the review site. */
export default async function handler(req:IncomingMessage,res:ServerResponse){
  res.setHeader('Cache-Control','no-store');res.setHeader('Content-Type','application/json; charset=utf-8');
  if(req.method!=='GET'){res.writeHead(405,{Allow:'GET'});return res.end(JSON.stringify({error:'Use search from the map.'}));}
  const q=new URL(req.url||'/','https://actforgoa-field-guide.vercel.app').searchParams.get('q')||'';
  if(q.length<3||q.length>120){res.writeHead(400);return res.end(JSON.stringify({error:'Enter a place or business name, between 3 and 120 characters.'}));}
  try{
    const upstream=await fetch('https://satellite-app-production.up.railway.app/api/map-places?'+new URLSearchParams({q}),{signal:AbortSignal.timeout(10000),redirect:'error'});
    const data=await upstream.json();res.writeHead(upstream.status);res.end(JSON.stringify(data));
  }catch{res.writeHead(502);res.end(JSON.stringify({error:'Place search is temporarily unavailable. You can still navigate the map.'}));}
}
