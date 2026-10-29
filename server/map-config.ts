import type {IncomingMessage,ServerResponse} from 'node:http';

/** Intentionally public, website-restricted credential. Never use the private server key. */
export function serveMapConfig(req:IncomingMessage,res:ServerResponse,browserKey=process.env.GOOGLE_MAPS_BROWSER_KEY){
  res.setHeader('Cache-Control','no-store');res.setHeader('Content-Type','application/json; charset=utf-8');
  if(req.method!=='GET'){res.writeHead(405,{Allow:'GET'});return res.end(JSON.stringify({error:'Use GET.'}));}
  if(!browserKey||!/^AIza[\w-]{35}$/.test(browserKey)){res.writeHead(503);return res.end(JSON.stringify({error:'Google Maps is not configured for this site.'}));}
  res.writeHead(200);res.end(JSON.stringify({browserKey}));
}
