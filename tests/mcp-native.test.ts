import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdirSync, mkdtempSync, rmSync} from 'node:fs';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';

test('compiled MCP module loads under native Node ESM without tsx', () => {
 const root=resolve('.reports'); mkdirSync(root,{recursive:true});
 const output=mkdtempSync(join(root,'mcp-native-'));
 try {
  const compile=spawnSync(process.execPath,['node_modules/typescript/bin/tsc','-p','tsconfig.api.json','--noEmit','false','--allowImportingTsExtensions','false','--outDir',output],{encoding:'utf8',timeout:30000});
  assert.equal(compile.status,0,compile.stderr || compile.stdout);
  const entry=pathToFileURL(join(output,'api','mcp.js')).href;
  const load=spawnSync(process.execPath,['--input-type=module','-e',`const m=await import(${JSON.stringify(entry)}); if(typeof m.default !== 'function') process.exit(1);`],{encoding:'utf8',timeout:15000});
  assert.equal(load.status,0,load.stderr || load.stdout);
 } finally { rmSync(output,{recursive:true,force:true}); }
});
