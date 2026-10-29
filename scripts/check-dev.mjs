/** Readiness and read-only search checks. No model answer or imagery retrieval is dispatched. */
const base='http://127.0.0.1:4173';
const read=async path=>{const r=await fetch(base+path,{signal:AbortSignal.timeout(20000)});if(!r.ok)throw Error(`${path}: HTTP ${r.status}`);return r.json();};
const status=await read('/api/status');
if(!status.search_ready||!status.chat_ready)throw Error('Research search or answers are not ready.');
const search=await read('/api/search?'+new URLSearchParams({q:'Goa mangroves',domain:'ecology'}));
if(!search.results?.length)throw Error('No research passages returned.');
const admin=await read('/api/admin/config');if(!admin.available)throw Error('Local account service unavailable.');
console.log(JSON.stringify({research:{model:status.model,documents:status.stats.documents,generation:status.generation,chat_ready:status.chat_ready,search_results:search.results.length},local_accounts:admin.available,paid_requests:0},null,2));

const {readFileSync,writeFileSync}=await import('node:fs');
const credentials=JSON.parse(readFileSync('.reports/dev/account.json','utf8'));
const login=await fetch(base+'/api/admin/login',{method:'POST',headers:{Origin:base,'Content-Type':'application/json'},body:JSON.stringify(credentials)});
if(!login.ok)throw Error(`Local sign-in failed: HTTP ${login.status}`);
const cookie=login.headers.getSetCookie().map(value=>value.split(';')[0]).join('; ');
const session=await (await fetch(base+'/api/admin/session',{headers:{Cookie:cookie}})).json();
const headers={Origin:base,Cookie:cookie,'Content-Type':'application/json','X-CSRF-Token':session.csrfToken};
try {
 const satelliteResponse=await fetch(base+'/api/admin/satellite/status',{headers});
 if(!satelliteResponse.ok)throw Error(`Satellite status failed: HTTP ${satelliteResponse.status}`);
 const satellite=await satelliteResponse.json();
 if(!satellite.imagery_ready)throw Error('Satellite imagery provider is not configured.');
 const historyResponse=await fetch(base+'/api/admin/satellite/history',{method:'POST',headers,body:JSON.stringify({limit:1})});
 if(!historyResponse.ok)throw Error(`Saved history failed: HTTP ${historyResponse.status}`);
 const history=await historyResponse.json();
 const invalid=await fetch(base+'/api/chat',{method:'POST',headers:{Origin:base,'Content-Type':'application/json'},body:JSON.stringify({question:''})});
 if(invalid.status!==422)throw Error(`Chat validation route returned ${invalid.status}; expected 422 without a model call.`);
 const record={checked:new Date().toISOString(),local_login:true,satellite,saved_comparisons:history.items.length,hosted_chat_validation:invalid.status,paid_requests:0};
 writeFileSync('.reports/dev/readiness.json',JSON.stringify(record,null,2)+'\n');
 console.log(JSON.stringify(record,null,2));
} finally { await fetch(base+'/api/admin/logout',{method:'POST',headers,body:'{}'}); }
