// Development adapter only: keep the production answer engine unchanged.
function clarifyPremisesQuestion(question){
 if(typeof question!=='string'||question.length>1200||/\b(sand ?bars?|pressure|steel bars?|bar association|bar exam)\b/i.test(question))return question;
 const venue=question.match(/\b(bar|pub|restaurant|cafe|café|shop|hotel|guesthouse|office|warehouse|factory|school|clinic)\b/i)?.[1];
 if(!venue||!/\b(build|building|construct\w*|erect|renovat\w*|convert\w*|rebuild\w*|open|start|set up|operate)\b/i.test(question))return question;
 return `For premises intended as a ${venue}, explain what the supplied excerpts establish about building permission, construction, development approval, technical clearance, commercial premises, land use and change of use. Original question: ${question}. Separate these from operating licences. Do not assume a new building, local-body jurisdiction or any licence requirement that the evidence does not establish. Answer supported parts even if venue-specific licensing evidence is absent. Describe only gaps in the retrieved excerpts, not the whole corpus.`;
}
export default async function handler(req,res){
 const incoming=new URL(req.url,'https://dev.invalid');
 const endpoint=incoming.searchParams.get('endpoint')||incoming.pathname.replace(/^\/api\//,'');
 incoming.searchParams.delete('endpoint');
 if(!/^(status|search|chat|documents\/[a-zA-Z0-9/?=_-]+)$/.test(endpoint)||!['GET','POST'].includes(req.method)||(req.method==='POST'&&endpoint!=='chat')){res.statusCode=404;res.end();return;}
 try{
  const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>65536){res.statusCode=413;res.end();return;}chunks.push(chunk);}
  let body=Buffer.concat(chunks);
  if(req.method==='POST'&&endpoint==='chat'){const input=JSON.parse(body.toString());input.question=clarifyPremisesQuestion(input.question);body=Buffer.from(JSON.stringify(input));}
  const upstream=new URL('/api/'+endpoint,'https://research-production-b579.up.railway.app');upstream.search=incoming.search;
  if(endpoint==='search'){const original=upstream.searchParams.get('q')||'';if(clarifyPremisesQuestion(original)!==original)upstream.searchParams.set('q',original+' building construction development permission technical clearance commercial premises land use change of use');}
  const result=await fetch(upstream,{method:req.method,headers:{'Origin':'https://actforgoa-field-guide.vercel.app','Content-Type':'application/json'},body:req.method==='POST'?body:undefined,signal:AbortSignal.timeout(80000)});
  res.statusCode=result.status;for(const name of ['content-type','content-disposition']){const value=result.headers.get(name);if(value)res.setHeader(name,value);}res.setHeader('Cache-Control','no-store');
  res.end(Buffer.from(await result.arrayBuffer()));
 }catch{res.statusCode=502;res.setHeader('Content-Type','application/json');res.end(JSON.stringify({detail:'The answer service could not connect. Please try again.'}));}
}