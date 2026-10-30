import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync, symlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {spawnSync} from 'node:child_process';

const wrapper = resolve('scripts/deploy-review.mjs');
const mock = `#!/usr/bin/env node
const fs=require('node:fs'), path=require('node:path');
const tool=path.basename(process.argv[1]), args=process.argv.slice(2);
const history=fs.existsSync('calls.jsonl')?fs.readFileSync('calls.jsonl','utf8').trim().split('\\n').map(JSON.parse):[];
const deployed=history.some(x=>x.tool==='vercel'&&x.args[0]==='deploy');
const promoted=history.some(x=>x.tool==='vercel'&&x.args[0]==='promote');
fs.appendFileSync('calls.jsonl',JSON.stringify({tool,args})+'\\n');
const scenario=process.env.RELEASE_TEST_SCENARIO;
if(tool==='git') {
 if(args[0]==='status') process.stdout.write(scenario==='dirty'?' M src/App.tsx':'');
 if(args[0]==='rev-parse') {
  const value=args[1]==='--git-common-dir'?path.resolve('.git'):args[1]==='HEAD^{tree}'?'tree-a':args[1]==='origin/main'&&(scenario==='stale'||scenario==='main-during-build'&&deployed)?'commit-b':'commit-a';
  process.stdout.write(value);
 }
}
if(tool==='vercel') {
 if(args[0]==='curl') {
  if(args[1]==='/landing') {
   process.stdout.write(scenario==='landing-spa-rewrite'?'<html>Main app</html>':'<title>ActForGoa · Answers for Goa. Backed by sources.</title><script src="/landing/assets/index-test.js"></script>');
  } else if(args[1]?.startsWith('/landing/assets/')) {
   process.stdout.write('HTTP/2 200\\ncontent-type: '+(scenario==='landing-asset-missing'?'text/html':args[1].endsWith('.js')?'application/javascript':'image/webp'));
  } else if(args.includes('/api/mcp')) {
   const req=JSON.parse(args[args.indexOf('--data')+1]);
   let result=req.method==='initialize'?{protocolVersion:'2025-03-26',serverInfo:{name:'actforgoa'}}:req.method==='tools/list'?{tools:['search_site','search_directory','search_research'].map(name=>({name}))}:{content:[{type:'text',text:JSON.stringify({results:scenario==='mcp-empty'?[]:[{id:'source'}]})}]};
   process.stdout.write(JSON.stringify(scenario==='mcp-error'?{jsonrpc:'2.0',id:req.id,error:{code:-32603,message:'failed'}}:{jsonrpc:'2.0',id:req.id,result}));
  } else if(args.some(x=>x.startsWith('/api/admin/posts/'))) {
   const path=args[1];
   const missing=scenario==='article-route-missing'&&!path.endsWith('publish')||scenario==='publish-route-missing'&&path.endsWith('/publish')||scenario==='unpublish-route-missing'&&path.endsWith('/unpublish');
   process.stdout.write(missing?'NOT_FOUND\\n404':scenario==='article-auth-missing'?'{}\\n200':'{"error":"Sign in to continue."}\\n401');
  } else if(args[1]?.startsWith('/api/admin/satellite/')) {
   process.stdout.write(scenario==='satellite-environment-missing'&&args[1].endsWith('/environment')?'NOT_FOUND\\n404':'{"error":"Sign in to continue."}\\n401');
  } else if(args[1]?.startsWith('/assets/newsletters/')) {
   process.stdout.write('HTTP/2 200\\ncontent-type: '+(scenario==='newsletter-spa-rewrite'?'text/html':args[1].endsWith('.pdf')?'application/pdf':'image/webp'));
  } else if(args.includes('/api/admin/config')) process.stdout.write(JSON.stringify({available:scenario!=='admin-unavailable'}));
  else if(args.includes('/api/blog')) process.stdout.write(JSON.stringify(scenario==='blog-unavailable'?{error:'unavailable'}:{posts:[]}));
  else process.stdout.write(JSON.stringify({search_ready:scenario!=='research-unavailable',chat_ready:scenario!=='answers-unavailable',domains:scenario==='research-unscoped'?[]:['legal','ecology'],domain_counts:{legal:3,ecology:5}}));
 }
 if(args[0]==='deploy') {
  const deployment={id:scenario==='wrong-deployment'?'unexpected':'new',url:'https://actforgoa-field-guide-test.vercel.app'};
  process.stdout.write(JSON.stringify(scenario==='flat-json'?deployment:{status:'ok',deployment}));
 }
 if(args[0]==='inspect') {
  const staged=args[1].includes('-test.');
  const id=staged||promoted?'new':scenario==='alias-during-build'&&deployed?'other':'old';
  process.stdout.write(JSON.stringify({id,readyState:staged&&scenario==='failed-build'?'ERROR':'READY'}));
 }
}
`;

function runRelease(scenario:string, check=false) {
 const root=mkdtempSync(join(tmpdir(),'actforgoa-release-test-'));
 try {
  mkdirSync(join(root,'bin')); mkdirSync(join(root,'.git')); mkdirSync(join(root,'api')); writeFileSync(join(root,'api','mcp.ts'),'');
  mkdirSync(join(root,'api','admin')); writeFileSync(join(root,'api','admin','[...path].ts'),'');
  mkdirSync(join(root,'api','admin','satellite')); writeFileSync(join(root,'api','admin','satellite','[action].ts'),'');
  mkdirSync(join(root,'landing')); writeFileSync(join(root,'landing','index.html'),'');
 const executable=join(root,'bin','mock.cjs');
  writeFileSync(executable,mock,{mode:0o755});
  for(const command of ['git','npm','vercel']) symlinkSync(executable,join(root,'bin',command));
  writeFileSync(join(root,'evidence.json'),JSON.stringify({treeSha:scenario==='wrong-tree'?'old-tree':'tree-a',desktop:true,mobile:true,previousDeploymentId:'old',routes:['/',...(scenario==='missing-explore'?[]:['/explore']),'/topics/waste','/directory','/directory/archive','/emergency','/report','/read/guide-farming','/templates/18-service-enquiry','/ask','/ask/legal','/ask/ecology','/admin','/blog','/blog/archive','/documents/verified-source']}));
  const result=spawnSync(process.execPath,[wrapper,'--evidence','evidence.json',...(check?['--check']:[])],{cwd:root,encoding:'utf8',env:{...process.env,PATH:join(root,'bin')+':'+process.env.PATH,RELEASE_TEST_SCENARIO:scenario}});
  const calls=existsSync(join(root,'calls.jsonl'))?readFileSync(join(root,'calls.jsonl'),'utf8').trim().split('\n').map(line=>JSON.parse(line)):[];
  assert(!existsSync(join(root,'.git','actforgoa-release.lock')),'release lock must be released');
  return {...result,calls};
 } finally {rmSync(root,{recursive:true,force:true});}
}

test('release preflight checks evidence without building or promoting',()=>{
 const result=runRelease('ok',true);
 assert.equal(result.status,0,result.stderr);
 assert(!result.calls.some(x=>x.tool==='npm'||x.args[0]==='deploy'||x.args[0]==='promote'));
});

for(const scenario of ['dirty','stale','wrong-tree','missing-explore','main-during-build','alias-during-build','failed-build','research-unavailable','answers-unavailable','research-unscoped','admin-unavailable','article-route-missing','publish-route-missing','unpublish-route-missing','article-auth-missing','blog-unavailable','wrong-deployment','mcp-error','mcp-empty','satellite-environment-missing','newsletter-spa-rewrite','landing-spa-rewrite','landing-asset-missing']) {
 test(`release refuses ${scenario} without changing the public alias`,()=>{
  const result=runRelease(scenario);
  assert.notEqual(result.status,0);
  assert(!result.calls.some(x=>x.tool==='vercel'&&x.args[0]==='promote'));
 });
}

for(const scenario of ['ok','flat-json']) test(`release stages ${scenario} output and promotes only after repeated boundary checks`,()=>{
 const result=runRelease(scenario);
 assert.equal(result.status,0,result.stderr);
 const deployment=result.calls.findIndex(x=>x.tool==='vercel'&&x.args[0]==='deploy');
 const promotion=result.calls.findIndex(x=>x.tool==='vercel'&&x.args[0]==='promote');
 assert(deployment>=0&&promotion>deployment);
 assert(result.calls[deployment].args.includes('--skip-domain'));
 assert(result.calls[deployment].args.includes('--json'));
 assert(result.calls[deployment].args.includes('VITE_REPORT_API_ORIGIN=https://reports-production-42c8.up.railway.app'));
 assert(result.calls.slice(deployment+1,promotion).some(x=>x.tool==='git'&&x.args[0]==='fetch'));
 assert(result.calls.slice(deployment+1,promotion).some(x=>x.tool==='vercel'&&x.args[1]==='https://actforgoa-field-guide.vercel.app'));
 assert(result.calls.slice(deployment+1,promotion).some(x=>x.tool==='vercel'&&x.args[0]==='curl'&&x.args.includes('/api/status')&&x.args.includes('https://actforgoa-field-guide-test.vercel.app')));
 assert.equal(result.calls.slice(deployment+1,promotion).filter(x=>x.tool==='vercel'&&x.args.includes('/api/mcp')).length,5);
 assert.equal(result.calls.slice(deployment+1,promotion).filter(x=>x.tool==='vercel'&&x.args[1]?.startsWith('/api/admin/posts/')).length,3);
 assert.equal(result.calls[promotion].args[1],'https://actforgoa-field-guide-test.vercel.app');
});
