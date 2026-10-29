import {createReadStream} from 'node:fs';
import {stat} from 'node:fs/promises';
import {extname, resolve, sep} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createAdminServer} from './admin.ts';
import {createPlaceSearch,serveMapPlaces} from './map-places.ts';
import {serveMapConfig} from './map-config.ts';

/** Standalone satellite frontend, using the same named-account auth and proxy. */
export function createSatelliteWeb(options:{publicOrigin:string;databasePath:string;staticRoot:string;local?:boolean}){
  const {server,store}=createAdminServer({...options,knownRecordIds:new Set<string>(),trustRailwayProxy:Boolean(process.env.RAILWAY_PROJECT_ID)});
  const admin=server.listeners('request')[0] as (req:import('node:http').IncomingMessage,res:import('node:http').ServerResponse)=>void;
  const root=resolve(options.staticRoot);
  const searchPlaces=createPlaceSearch();
  server.removeAllListeners('request');
  server.on('request',async(req,res)=>{
    res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');res.setHeader('X-Frame-Options','DENY');
    res.setHeader('X-Robots-Tag','noindex, nofollow');
    let pathname:string;
    try{pathname=decodeURIComponent(new URL(req.url||'/','http://localhost').pathname);}catch{res.writeHead(400);return res.end();}
    if(pathname.startsWith('/api/')){
      if(pathname==='/api/map-config')return serveMapConfig(req,res);
      if(pathname==='/api/map-places')return serveMapPlaces(req,res,searchPlaces);
      if(!/^\/api\/admin\/(?:config|login|logout|session|satellite\/.+)$/.test(pathname)){res.writeHead(404);return res.end();}
      return admin(req,res);
    }
    if(!['GET','HEAD'].includes(req.method||'GET')){res.writeHead(405,{Allow:'GET, HEAD'});return res.end();}
    const route=['/','/map','/admin'].includes(pathname);
    const target=resolve(root,route?'satellite.html':'.'+pathname);
    if(!target.startsWith(root+sep)||(!route&&!pathname.startsWith('/assets/'))){res.writeHead(404);return res.end();}
    try{
      const file=await stat(target);if(!file.isFile())throw Error('Not a file');
      const types:Record<string,string>={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.woff2':'font/woff2','.png':'image/png','.svg':'image/svg+xml'};
      res.writeHead(200,{'Content-Type':types[extname(target)]||'application/octet-stream','Content-Length':file.size,'Cache-Control':route?'no-cache':'public, max-age=31536000, immutable'});
      if(req.method==='HEAD')return res.end();
      createReadStream(target).on('error',()=>res.destroy()).pipe(res);
    }catch{res.writeHead(404);res.end();}
  });
  return {server,store};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
  process.umask(0o077);
  const {server}=createSatelliteWeb({publicOrigin:process.env.ADMIN_PUBLIC_ORIGIN||'',databasePath:resolve(process.env.ADMIN_DATA_DIR||'/data/admin','admin.sqlite'),staticRoot:process.env.SATELLITE_STATIC_ROOT||'dist-satellite',local:process.env.NODE_ENV!=='production'});
  server.listen(Number(process.env.PORT||8080),'0.0.0.0');
  for(const signal of ['SIGINT','SIGTERM'] as const)process.on(signal,()=>server.close(()=>process.exit(0)));
}
