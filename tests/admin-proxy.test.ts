import assert from 'node:assert/strict';
import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { once } from 'node:events';
import test from 'node:test';
import { configuredAdminOrigin, createAdminProxy } from '../server/admin-proxy.ts';

async function withProxy(handler:(req:IncomingMessage,res:ServerResponse)=>Promise<unknown>, run:(url:string)=>Promise<void>) {
  const server=createServer((req,res)=>{void handler(req,res);});
  server.listen(0,'127.0.0.1'); await once(server,'listening');
  const address=server.address(); assert(address && typeof address !== 'string');
  try {await run(`http://127.0.0.1:${address.port}`);}
  finally {server.closeAllConnections(); server.close(); await once(server,'close');}
}

test('service configuration accepts only a fixed HTTPS origin',()=>{
  assert.equal(configuredAdminOrigin('https://admin.example/'),'https://admin.example');
  for(const value of ['http://localhost','https://user:pass@admin.example','https://admin.example/path','https://admin.example?url=other']) assert.equal(configuredAdminOrigin(value),null);
});

test('proxy preserves auth cookies, CSRF and origin without forwarding arbitrary headers',async()=>{
  const upstream: typeof fetch=async(url,init)=>{
    assert.equal(url,'https://admin.example/api/admin/login');
    const headers=new Headers(init?.headers);
    assert.equal(headers.get('origin'),'https://site.example');
    assert.equal(headers.get('cookie'),'admin-session=test');
    assert.equal(headers.get('x-csrf-token'),'test-token');
    assert.equal(headers.get('authorization'),null);
    assert.deepEqual(JSON.parse(Buffer.from(init?.body as Uint8Array).toString()),{email:'editor@example.com',password:'example-only'});
    return new Response('{"user":{"name":"Editor"}}',{headers:{'set-cookie':'session=new; HttpOnly; Secure; SameSite=Strict; Path=/api/admin'}});
  };
  await withProxy(createAdminProxy({origin:'https://admin.example',fetcher:upstream}),async(url)=>{
    const response=await fetch(url+'/api/admin/login',{method:'POST',headers:{origin:'https://site.example',cookie:'admin-session=test','x-csrf-token':'test-token',authorization:'must-not-forward','content-type':'application/json'},body:JSON.stringify({email:'editor@example.com',password:'example-only'})});
    assert.equal(response.status,200); assert.match(response.headers.get('set-cookie') || '',/HttpOnly/);
  });
});

test('invalid paths cannot become proxy destinations and oversized writes are refused',async()=>{
  let calls=0;
  const fetcher:typeof fetch=async()=>{calls++;return new Response('{}');};
  await withProxy(createAdminProxy({origin:'https://admin.example',fetcher}),async(url)=>{
    assert.equal((await fetch(url+'/api/admin/secrets')).status,404);
    assert.equal((await fetch(url+'/api/admin/posts',{method:'POST',body:'x'.repeat(420001)})).status,413);
  });
  assert.equal(calls,0);
});

test('public curation forwards no admin cookie and upstream redirects are not followed',async()=>{
  const fetcher:typeof fetch=async(_url,init)=>{
    assert.equal(new Headers(init?.headers).get('cookie'),null);
    assert.equal(init?.redirect,'manual');
    return new Response(null,{status:302,headers:{location:'https://elsewhere.example'}});
  };
  await withProxy(createAdminProxy({origin:'https://admin.example',fetcher}),async(url)=>{
    assert.equal((await fetch(url+'/api/curation',{headers:{cookie:'admin-session=test'}})).status,502);
  });
});
