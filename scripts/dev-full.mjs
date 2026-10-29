/** Loopback-only development: hot reload, hosted research, local editorial and satellite data. */
import {spawn, execFileSync} from 'node:child_process';
import {readFileSync, writeFileSync, mkdirSync, existsSync, openSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomBytes} from 'node:crypto';
import {createServer} from 'node:net';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
process.chdir(root);
process.umask(0o077);
const output=resolve('.reports/dev');
const configPath=resolve(process.env.ACTFORGOA_DEV_CONFIG||'.reports/dev/config.json');
if(!existsSync(configPath))throw Error('Missing local setup. See docs/LOCAL-DEVELOPMENT.md.');
const config=JSON.parse(readFileSync(configPath,'utf8'));
const origin=new URL(config.researchOrigin);
if(origin.protocol!=='https:'||origin.pathname!=='/'||origin.username||origin.password)throw Error('Use an exact HTTPS research service origin.');
mkdirSync(output,{recursive:true});
// Refuse collisions before starting any processes; never kill another workspace's server.
for(const port of [4173,4187,4188,8095])await new Promise((resolvePort,reject)=>{
 const probe=createServer();probe.once('error',()=>reject(Error(`Port ${port} is in use. Stop this workspace's previous dev command first.`)));
 probe.listen(port,'127.0.0.1',()=>probe.close(resolvePort));
});
const tokenPath=resolve(output,'satellite-token');
if(!existsSync(tokenPath))writeFileSync(tokenPath,randomBytes(32).toString('hex'),{mode:0o600});
const token=readFileSync(tokenPath,'utf8').trim();
const base={...process.env};
// Provider secrets are supplied only to the service that uses them, never to Vite.
for(const key of Object.keys(base))if(/^(ANTHROPIC_|OPENAI_|CDSE_|EARTH_ENGINE_|GOOGLE_MAPS_|SATELLITE_|RESEARCH_|VITE_)/.test(key))delete base[key];
const satellite={...base,SATELLITE_SERVICE_TOKEN:token,SATELLITE_DATA_DIR:resolve(output,'satellite'),SATELLITE_IMAGERY_PROVIDER:'earth-engine',
 EARTH_ENGINE_PROJECT:config.earthEngineProject,EARTH_ENGINE_CREDENTIALS_JSON:readFileSync(config.earthEngineCredentials,'utf8'),
 SATELLITE_RESEARCH_ORIGIN:origin.origin};
if(config.googleMapsKeychainService){
 try{satellite.GOOGLE_MAPS_API_KEY=execFileSync('security',['find-generic-password','-s',config.googleMapsKeychainService,'-w'],{encoding:'utf8',stdio:['ignore','pipe','pipe']}).trim();}
 catch{console.warn('Google current conditions unavailable: saved server key could not be read.');}
}
if(config.anthropicEnvFile){
 const line=readFileSync(config.anthropicEnvFile,'utf8').split(/\r?\n/).find(v=>/^ANTHROPIC_API_KEY=/.test(v));
 if(line)satellite.ANTHROPIC_API_KEY=line.slice(line.indexOf('=')+1).trim().replace(/^(["'])(.*)\1$/,'$2');
}
const children=[];let stopping=false;
function stop(code=0){if(stopping)return;stopping=true;for(const child of children)if(child.exitCode===null)child.kill('SIGTERM');process.exitCode=code;}
function launch(name,command,args,env){
 const log=openSync(resolve(output,name+'.log'),'a',0o600);
 const child=spawn(command,args,{cwd:root,env,stdio:['ignore',log,log]});children.push(child);
 child.on('error',error=>{console.error(`${name} could not start: ${error.message}`);stop(1);});
 child.on('exit',code=>{if(!stopping){console.error(`${name} exited (${code}); see .reports/dev/${name}.log`);stop(code||1);}});
 return child;
}
launch('satellite',config.satellitePython,['-m','uvicorn','satellite.app:create_app','--factory','--host','127.0.0.1','--port','8095','--no-access-log'],satellite);
launch('reporting',process.execPath,['--import','tsx','server/reporting.ts'],{...base,REPORT_PORT:'4187',REPORT_DATA_DIR:resolve(output,'reports')});
launch('admin',process.execPath,['--import','tsx','server/admin.ts'],{...base,ADMIN_PUBLIC_ORIGIN:'http://127.0.0.1:4173',ADMIN_PORT:'4188',ADMIN_DATA_DIR:resolve(output,'admin'),SATELLITE_API_ORIGIN:'http://127.0.0.1:8095',SATELLITE_SERVICE_TOKEN:token});
launch('web',process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1'],{...base,RESEARCH_API_ORIGIN:origin.origin,RESEARCH_BROWSER_ORIGIN:config.researchBrowserOrigin});
writeFileSync(resolve(output,'runtime.json'),JSON.stringify({started:new Date().toISOString(),pid:process.pid,children:children.map(c=>c.pid),url:'http://127.0.0.1:4173',research:origin.origin,satellite:'http://127.0.0.1:8095',accountFile:'.reports/dev/account.json'},null,2)+'\n');
console.log('Dev environment: http://127.0.0.1:4173\nAI: /ask · Satellite: /map · Local account: .reports/dev/account.json\nLogs: .reports/dev/ · Readiness: npm run dev:check\nCtrl+C stops only these owned processes.');
process.on('SIGINT',()=>stop());process.on('SIGTERM',()=>stop());
