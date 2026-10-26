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
 if(args[0]==='deploy') process.stdout.write('https://actforgoa-field-guide-test.vercel.app');
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
  mkdirSync(join(root,'bin')); mkdirSync(join(root,'.git'));
  const executable=join(root,'bin','mock.cjs');
  writeFileSync(executable,mock,{mode:0o755});
  for(const command of ['git','npm','vercel']) symlinkSync(executable,join(root,'bin',command));
  writeFileSync(join(root,'evidence.json'),JSON.stringify({treeSha:scenario==='wrong-tree'?'old-tree':'tree-a',desktop:true,mobile:true,previousDeploymentId:'old',routes:['/','/topics/waste','/directory','/directory/archive','/emergency','/report','/read/guide-farming','/templates/18-service-enquiry']}));
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

for(const scenario of ['dirty','stale','wrong-tree','main-during-build','alias-during-build','failed-build']) {
 test(`release refuses ${scenario} without changing the public alias`,()=>{
  const result=runRelease(scenario);
  assert.notEqual(result.status,0);
  assert(!result.calls.some(x=>x.tool==='vercel'&&x.args[0]==='promote'));
 });
}

test('release stages a configured build and promotes only after repeated boundary checks',()=>{
 const result=runRelease('ok');
 assert.equal(result.status,0,result.stderr);
 const deployment=result.calls.findIndex(x=>x.tool==='vercel'&&x.args[0]==='deploy');
 const promotion=result.calls.findIndex(x=>x.tool==='vercel'&&x.args[0]==='promote');
 assert(deployment>=0&&promotion>deployment);
 assert(result.calls[deployment].args.includes('--skip-domain'));
 assert(result.calls[deployment].args.includes('VITE_REPORT_API_ORIGIN=https://reports-production-42c8.up.railway.app'));
 assert(result.calls.slice(deployment+1,promotion).some(x=>x.tool==='git'&&x.args[0]==='fetch'));
 assert(result.calls.slice(deployment+1,promotion).some(x=>x.tool==='vercel'&&x.args[1]==='https://actforgoa-field-guide.vercel.app'));
 assert.equal(result.calls[promotion].args[1],'https://actforgoa-field-guide-test.vercel.app');
});
