/** Satellite-only hot-reload environment. Never included in a deployment package. */
import {createServer as createHttpServer} from 'node:http';
import {createServer as createTcpServer} from 'node:net';
import {randomBytes} from 'node:crypto';
import {existsSync,mkdirSync,readFileSync,chmodSync} from 'node:fs';
import {homedir} from 'node:os';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import {createServer as createViteServer} from 'vite';
import {createAdminServer} from '../server/admin.ts';
import {serveMapConfig} from '../server/map-config.ts';

if(process.env.NODE_ENV==='production'||process.env.RAILWAY_PROJECT_ID)throw Error('This development server runs only on your Mac.');
process.umask(0o077);
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');process.chdir(root);
const origin='http://127.0.0.1:4176',apiOrigin='http://127.0.0.1:8096';
for(const port of [4176,4177,8096])await new Promise((done,reject)=>{const test=createTcpServer();test.once('error',()=>reject(Error(`Port ${port} is in use. Stop the previous satellite dev process first.`)));test.listen(port,'127.0.0.1',()=>test.close(done));});
const privateRoot=resolve(root,'.reports/satellite-local');mkdirSync(privateRoot,{recursive:true,mode:0o700});chmodSync(privateRoot,0o700);
const config=resolve(homedir(),'.config/actforgoa');
const saved=(name)=>{const path=resolve(config,name);return existsSync(path)?readFileSync(path,'utf8').trim():'';};
const openai=saved('openai.env').match(/^OPENAI_API_KEY\s*=\s*["']?([^\s"']+)/m)?.[1];
const browserKey=saved('google-maps-browser.key');
const earthPath=resolve(homedir(),'.config/earthengine/credentials');
const env={...process.env,SATELLITE_DATA_DIR:resolve(privateRoot,'imagery'),SATELLITE_SERVICE_TOKEN:randomBytes(32).toString('hex'),SATELLITE_MCP_TOKEN:randomBytes(32).toString('hex'),SATELLITE_IMAGERY_PROVIDER:'earth-engine',EARTH_ENGINE_PROJECT:process.env.EARTH_ENGINE_PROJECT||'actforgoa-translation',PYTHONUNBUFFERED:'1'};
if(existsSync(earthPath))env.EARTH_ENGINE_CREDENTIALS_JSON=readFileSync(earthPath,'utf8');
if(openai){env.OPENAI_API_KEY=openai;env.SATELLITE_CLASSIFIER='openai-decisions';}
if(!env.EARTH_ENGINE_CREDENTIALS_JSON)throw Error('The saved Earth Engine connection was not found.');
const python=resolve(root,'.venv/bin/python');if(!existsSync(python))throw Error('Install requirements-satellite.txt into .venv first.');
const api=spawn(python,['-m','uvicorn','satellite.app:create_app','--factory','--host','127.0.0.1','--port','8096','--reload','--reload-dir','satellite','--no-access-log'],{cwd:root,env,stdio:['ignore','inherit','inherit']});
process.env.SATELLITE_API_ORIGIN=apiOrigin;process.env.SATELLITE_SERVICE_TOKEN=env.SATELLITE_SERVICE_TOKEN;
const {server:admin,store}=createAdminServer({publicOrigin:origin,databasePath:resolve(privateRoot,'admin.sqlite'),knownRecordIds:new Set(),local:true});
const adminHandler=admin.listeners('request')[0];
const email='local-satellite@localhost.test',password=randomBytes(32).toString('hex');
await store.provision(email,'Local satellite workspace',password,'editor');
let session=await store.login(email,password,null);
const vite=await createViteServer({configFile:resolve(root,'vite.satellite.config.ts'),server:{host:'127.0.0.1',middlewareMode:true,watch:{ignored:['**/dist/**','**/dist-server/**','**/dist-api/**','**/.reports/**']},hmr:{port:4177,host:'127.0.0.1'}},appType:'custom'});
const server=createHttpServer(async(req,res)=>{
  const path=new URL(req.url||'/',origin).pathname;
  const navigation=req.method==='GET'&&req.headers['sec-fetch-mode']==='navigate'&&['/','/map','/admin'].includes(path);
  if(req.headers.host!=='127.0.0.1:4176'||(req.headers.origin&&req.headers.origin!==origin)||(!navigation&&req.headers['sec-fetch-site']==='cross-site')){
    res.writeHead(403);return res.end('Open the local satellite workspace on '+origin+'/map');
  }
  res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');res.setHeader('X-Content-Type-Options','nosniff');
  if(path==='/api/map-config')return serveMapConfig(req,res,browserKey);
  // Local-only session: normal CSRF/authenticated proxy, isolated local account/data.
  // The listener is loopback-only, rejects foreign Host/Origin and cross-site requests.
  if(path==='/api/admin/session'&&req.method==='GET'){
    if(session.expiresAt<Date.now()+60000)session=await store.login(email,password,null);
    res.writeHead(200,{'Content-Type':'application/json','Cache-Control':'no-store','Set-Cookie':`afg_admin_session=${session.token}; HttpOnly; SameSite=Strict; Path=/api/admin; Max-Age=43200`});
    return res.end(JSON.stringify({user:session.user,csrfToken:session.csrfToken}));
  }
  if(path.startsWith('/api/admin/satellite/'))return adminHandler(req,res);
  if(path.startsWith('/api/')){res.writeHead(404);return res.end();}
  if(['/','/map','/admin'].includes(path)){
    try{const html=await vite.transformIndexHtml(req.url||'/map',readFileSync(resolve(root,'satellite.html'),'utf8'));res.writeHead(200,{'Content-Type':'text/html','Cache-Control':'no-store'});res.end(html);}catch(error){vite.ssrFixStacktrace(error);res.writeHead(500);res.end('The local satellite build could not load. Check the dev terminal.');}
    return;
  }
  vite.middlewares(req,res,()=>{res.writeHead(404);res.end();});
});
let stopping=false;
async function stop(){if(stopping)return;stopping=true;server.close();await vite.close();api.kill('SIGTERM');store.db.close();}
process.on('SIGINT',()=>void stop());process.on('SIGTERM',()=>void stop());
api.on('exit',code=>{if(!stopping){console.error('Local satellite API stopped:',code);void stop();}});
server.listen(4176,'127.0.0.1',()=>console.log(`Satellite workspace: ${origin}/map\nLive reload enabled. Local account and imagery are isolated from the hosted app. Ctrl+C stops both servers.`));
