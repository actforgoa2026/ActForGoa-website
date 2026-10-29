import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {copyFileSync,existsSync,mkdirSync,readFileSync,readdirSync,writeFileSync} from 'node:fs';
import {dirname,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const position=process.argv.indexOf('--output');
if(position<0||!process.argv[position+1])throw Error('Use --output <new staging directory>.');
const output=resolve(process.argv[position+1]);
if(existsSync(output))throw Error('Use a new output directory.');
const git=(...args)=>execFileSync('git',args,{cwd:root,encoding:'utf8'}).trim();
if(git('status','--porcelain','--untracked-files=all'))throw Error('Commit and verify source before packaging.');
const service=resolve(output,'service');mkdirSync(service,{recursive:true});
const mappings=[['deploy/admin/package.json','package.json'],['deploy/admin/package-lock.json','package-lock.json'],['deploy/satellite-app/Dockerfile','Dockerfile'],['deploy/satellite-app/railway.json','railway.json'],...['server/admin.ts','server/admin-store.ts','server/admin-accounts.ts','server/satellite-proxy.ts','server/satellite-web.ts','server/map-places.ts','shared/admin.ts'].map(p=>[p,p])];
for(const [source,target] of mappings){const path=resolve(service,target);mkdirSync(dirname(path),{recursive:true});copyFileSync(resolve(root,source),path);}
execFileSync(process.execPath,['node_modules/vite/bin/vite.js','build','--config','vite.satellite.config.ts','--outDir',resolve(service,'dist-satellite')],{cwd:root,stdio:'inherit'});
function files(dir){return readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(resolve(dir,e.name)):[resolve(dir,e.name)]);}
writeFileSync(resolve(output,'manifest.json'),JSON.stringify({commit:git('rev-parse','HEAD'),tree:git('rev-parse','HEAD^{tree}'),scope:'Satellite frontend and auth runtime only; no catalogue, credentials, accounts, imagery or research corpus.',files:files(service).map(path=>{const b=readFileSync(path);return {path:relative(service,path),bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};})},null,2)+'\n');
console.log('Satellite app staged at '+service);
