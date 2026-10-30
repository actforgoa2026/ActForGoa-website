import {createHmac, randomBytes, timingSafeEqual} from 'node:crypto';
import type {IncomingMessage, ServerResponse} from 'node:http';
import {forwardSatellite} from './satellite-proxy.ts';

const cookieName='afg_map_visitor';
const lifetime=30*24*60*60;
const equal=(a:string,b:string)=>{const left=Buffer.from(a),right=Buffer.from(b);return left.length===right.length&&timingSafeEqual(left,right);};
const routePattern=/^\/api\/satellite\/(session|status|plan|catalog|compare|history|observation|evidence|environment|preview|jobs\/[a-f0-9-]{36})$/;

/** Public map access. A signed browser cookie separates saved jobs without an account. */
export function createPublicSatellite(options:{publicOrigin:string;local?:boolean;now?:()=>number}){
  const buckets=new Map<string,{start:number;count:number}>();
  const now=options.now??Date.now;
  function allow(key:string,maximum:number){
    const time=now();
    for(const [id,bucket] of buckets)if(time-bucket.start>=60_000)buckets.delete(id);
    let bucket=buckets.get(key);
    if(!bucket){if(buckets.size>=4000)return false;bucket={start:time,count:0};buckets.set(key,bucket);}
    return ++bucket.count<=maximum;
  }
  return async(req:IncomingMessage&{body?:unknown},res:ServerResponse)=>{
    res.setHeader('Cache-Control','no-store');
    res.setHeader('Content-Type','application/json; charset=utf-8');
    res.setHeader('X-Content-Type-Options','nosniff');
    const reply=(status:number,data:unknown)=>{res.writeHead(status);res.end(JSON.stringify(data));};
    const fail=(status:number,error:string)=>reply(status,{error});
    const match=new URL(req.url||'/','http://localhost').pathname.match(routePattern);
    if(!match)return fail(404,'This map route does not exist.');
    const action=match[1],method=req.method||'GET';
    const expectedMethod=action==='session'||action==='status'||action.startsWith('jobs/')?'GET':'POST';
    if(method!==expectedMethod){res.setHeader('Allow',expectedMethod);return fail(405,'Method not allowed.');}
    const allowed=new Set([options.publicOrigin,...(!options.local?['https://actforgoa-field-guide.vercel.app']:[]),...(process.env.SATELLITE_PUBLIC_ORIGINS||'').split(',').map(value=>value.trim()).filter(Boolean)]);
    if(req.headers['sec-fetch-site']==='cross-site'||(req.headers.origin&&!allowed.has(req.headers.origin)))return fail(403,'Open the map on the ActForGoa site.');
    const secret=process.env.SATELLITE_SERVICE_TOKEN||'';
    if(secret.length<32)return fail(503,'Satellite imagery is temporarily unavailable. Please try again shortly.');
    const sign=(value:string)=>createHmac('sha256',secret).update('actforgoa-public-map:'+value).digest('base64url');
    const cookies=(req.headers.cookie||'').split(';').map(value=>value.trim()).filter(value=>value.startsWith(cookieName+'='));
    const raw=cookies.length===1?cookies[0].slice(cookieName.length+1):'';
    const parsed=raw.match(/^([A-Za-z0-9_-]{32})\.(\d{10})\.([A-Za-z0-9_-]{43})$/);
    const seconds=Math.floor(now()/1000);
    let id=parsed&&Number(parsed[2])>seconds&&Number(parsed[2])<=seconds+lifetime&&equal(parsed[3],sign(parsed[1]+'.'+parsed[2]))?parsed[1]:null;
    if(action==='session'){
      if(!allow('sessions',120)){res.setHeader('Retry-After','60');return fail(429,'The map is busy. Try again in a minute.');}
      id??=randomBytes(24).toString('base64url');
      const value=id+'.'+(seconds+lifetime);
      res.setHeader('Set-Cookie',`${cookieName}=${value}.${sign(value)}; HttpOnly; SameSite=Strict; Path=/api/satellite; Max-Age=${lifetime}${options.local?'':'; Secure'}`);
      return reply(200,{visitorId:'visitor_'+id,csrfToken:sign('csrf:'+id)});
    }
    if(!id)return fail(401,'Your map session expired. Retry to reconnect.');
    if(method==='POST'){
      const csrf=req.headers['x-csrf-token'];
      if(typeof csrf!=='string'||!equal(csrf,sign('csrf:'+id)))return fail(403,'Reload the map to reconnect securely.');
      if(!/^application\/json(?:;|$)/i.test(req.headers['content-type']||''))return fail(415,'Send JSON using the map.');
    }
    if(!allow(id+':'+method,method==='GET'?120:30)){res.setHeader('Retry-After','60');return fail(429,'Please wait a minute before requesting more imagery.');}
    let body:unknown;
    if(method==='POST'){
      try{
        const chunks:Buffer[]=[];let size=0;
        if(Number(req.headers['content-length'])>16_384)return fail(413,'This map request is too large.');
        if(req.body!==undefined){const bytes=Buffer.isBuffer(req.body)?req.body:Buffer.from(typeof req.body==='string'?req.body:JSON.stringify(req.body));chunks.push(bytes);size=bytes.length;}
        else for await(const chunk of req){size+=chunk.length;if(size>16_384)return fail(413,'This map request is too large.');chunks.push(Buffer.from(chunk));}
        if(size>16_384)return fail(413,'This map request is too large.');
        body=JSON.parse(Buffer.concat(chunks).toString());
        if(!body||typeof body!=='object'||Array.isArray(body))return fail(400,'Check the map request and try again.');
      }catch{return fail(400,'Check the map request and try again.');}
    }
    return forwardSatellite('/api/admin/satellite/'+action,method,'visitor_'+id,body,res,{local:options.local});
  };
}
