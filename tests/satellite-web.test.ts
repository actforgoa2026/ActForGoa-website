import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createSatelliteWeb} from '../server/satellite-web.ts';

test('standalone satellite serves only its frontend and authenticated API surface',async()=>{
  const root=await mkdtemp(join(tmpdir(),'satellite-web-'));
  await mkdir(join(root,'static/assets'),{recursive:true});
  await writeFile(join(root,'static/satellite.html'),'<h1>Satellite</h1>');
  await writeFile(join(root,'static/assets/app.js'),'window.loaded=true;');
  await writeFile(join(root,'private.json'),'private sentinel');
  const {server}=createSatelliteWeb({publicOrigin:'http://127.0.0.1:4173',databasePath:join(root,'auth/admin.sqlite'),staticRoot:join(root,'static'),local:true});
  await new Promise<void>(r=>server.listen(0,'127.0.0.1',r));
  const address=server.address();assert(address&&typeof address==='object');const origin=`http://127.0.0.1:${address.port}`;
  try{
    for(const path of ['/','/map','/admin']){const r=await fetch(origin+path);assert.equal(r.status,200);assert.equal(r.headers.get('cache-control'),'no-cache');assert.equal(r.headers.get('x-frame-options'),'DENY');assert.match(await r.text(),/Satellite/);}
    const asset=await fetch(origin+'/assets/app.js');assert.equal(asset.status,200);assert.match(asset.headers.get('content-type')||'',/javascript/);
    for(const path of ['/private.json','/.env.local','/assets/%2e%2e%2f%2e%2e%2fprivate.json','/api/admin/posts','/api/blog','/api/curation'])assert.equal((await fetch(origin+path)).status,404,path);
    assert.equal((await fetch(origin+'/api/admin/config')).status,200);
    assert.equal((await fetch(origin+'/api/map-places?q=a')).status,400);
    assert.equal((await fetch(origin+'/api/map-places?q=Panaji',{method:'POST'})).status,405);
    assert.equal((await fetch(origin+'/api/admin/satellite/status')).status,401);
    assert.equal((await fetch(origin+'/api/admin/session')).status,401);
    assert.equal((await fetch(origin+'/map',{method:'POST'})).status,405);
    assert.equal((await fetch(origin+'/api/admin/login',{method:'POST',headers:{Origin:'https://untrusted.example','Content-Type':'application/json'},body:'{}'})).status,403);
  }finally{await new Promise<void>(r=>server.close(()=>r()));await rm(root,{recursive:true,force:true});}
});
