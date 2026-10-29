// Private, session-based HTTP relay. No provider credentials leave the workspace.
import http from 'node:http';
import {readFileSync} from 'node:fs';
import {randomBytes,timingSafeEqual} from 'node:crypto';
const secrets=JSON.parse(readFileSync(new URL('./relay-secrets.json',import.meta.url)));
let invite=secrets.invite;
const sessions=new Set();const queue=[];const waiting=new Map();let poller=null;let lastPoll=0;
const equal=(a,b)=>typeof a==='string'&&a.length===b.length&&timingSafeEqual(Buffer.from(a),Buffer.from(b));
const json=(res,status,data)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(data));};
async function body(req,max=30*1024*1024){const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>max)throw Error('Too large');chunks.push(chunk);}return Buffer.concat(chunks);}
function flush(){if(poller&&queue.length){const response=poller;poller=null;json(response,200,{requests:queue.splice(0,30)});}}
const login=`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>Private ActForGoa workspace</title><main style="font:18px system-ui;max-width:560px;margin:15vh auto;padding:24px"><h1>Private research workspace</h1><p id="message">Use your private invitation link to enter.</p><script>
const invite=new URLSearchParams(location.hash.slice(1)).get('invite');
if(invite){history.replaceState(null,'','/');fetch('/__login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({invite})}).then(async r=>{if(r.ok)location.replace('/dev/workbench.html');else document.getElementById('message').textContent='This invitation has expired or has already been used.';});}
</script></main>`;
http.createServer(async(req,res)=>{
 res.setHeader('Cache-Control','no-store');res.setHeader('X-Robots-Tag','noindex, nofollow');res.setHeader('Referrer-Policy','no-referrer');res.setHeader('X-Content-Type-Options','nosniff');
 const path=new URL(req.url,'https://private.invalid').pathname;
 try{
  if(path.startsWith('/__relay/')){
   if(!equal(req.headers.authorization||'','Bearer '+secrets.worker)){json(res,401,{error:'Unauthorized'});return;}
   if(path==='/__relay/invite'&&req.method==='POST'){const input=JSON.parse((await body(req,4096)).toString());if(typeof input.invite!=='string'||input.invite.length<32){json(res,400,{});return;}invite=input.invite;json(res,200,{ok:true});return;}
   if(path==='/__relay/poll'&&req.method==='POST'){
    lastPoll=Date.now();if(poller)json(poller,200,{requests:[]});poller=res;flush();setTimeout(()=>{if(poller===res){poller=null;json(res,200,{requests:[]});}},20000);return;
   }
   if(path.startsWith('/__relay/result/')&&req.method==='POST'){
    const id=path.slice('/__relay/result/'.length);const pending=waiting.get(id);
    if(pending){waiting.delete(id);clearTimeout(pending.timer);const result=JSON.parse((await body(req)).toString());pending.response.writeHead(result.status,result.headers);pending.response.end(Buffer.from(result.body,'base64'));}
    json(res,200,{ok:true});return;
   }
   json(res,404,{});return;
  }
  if(path==='/__login'&&req.method==='POST'){
   const input=JSON.parse((await body(req,4096)).toString());if(!invite||!equal(input.invite,invite)){json(res,401,{error:'Invalid invitation'});return;}
   invite=null;const session=randomBytes(32).toString('hex');sessions.add(session);res.setHeader('Set-Cookie',`research_dev=${session}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=18000`);json(res,200,{ok:true});return;
  }
  const session=req.headers.cookie?.split(';').map(v=>v.trim()).find(v=>v.startsWith('research_dev='))?.slice(13);
  if(!session||!sessions.has(session)){res.setHeader('Content-Type','text/html; charset=utf-8');res.statusCode=401;res.end(login);return;}
  if(Date.now()-lastPoll>45000){json(res,503,{error:'The development workspace is not connected. Reconnect its relay worker.'});return;}
  const id=randomBytes(12).toString('hex');const requestBody=await body(req,1024*1024);
  const timer=setTimeout(()=>{waiting.delete(id);if(!res.writableEnded)json(res,504,{error:'The development request timed out.'});},95000);
  waiting.set(id,{response:res,timer});queue.push({id,method:req.method,path:req.url,headers:{accept:req.headers.accept||'*/*','content-type':req.headers['content-type']||''},body:requestBody.toString('base64')});flush();
 }catch{if(!res.headersSent)json(res,400,{error:'Invalid request'});else res.end();}
}).listen(4174,'0.0.0.0',()=>console.log('Private development gateway listening'));
