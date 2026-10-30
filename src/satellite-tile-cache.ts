/** Public navigation tiles only. Exact observations retain their private API cache. */
const CACHE_NAME='satellite-earth-engine-tiles-v1';
const MAX_AGE=45*60*1000;
const MAX_BYTES=24*1024*1024;
const MAX_TILES=96;
type Entry={blob:Blob;expires:number};
type Pending={promise:Promise<Blob>;resolve:(blob:Blob)=>void;reject:(error:unknown)=>void;signals:Set<AbortSignal>;url:string;expires:number};

/** Zoom 14 is about 9 m/pixel in Goa. Higher zooms magnify those same pixels. */
export function earthEngineTile(x:number,y:number,zoom:number){
  const z=Math.min(zoom,14),scale=2**(zoom-z);
  return {z,x:Math.floor(x/scale),y:Math.floor(y/scale),scale,left:-((x%scale+scale)%scale)*256,top:-((y%scale+scale)%scale)*256};
}

export function tileIntersectsBounds(x:number,y:number,z:number,bounds:readonly number[]){
  const size=2**z,latitude=(row:number)=>Math.atan(Math.sinh(Math.PI*(1-2*row/size)))*180/Math.PI;
  return (x+1)/size*360-180>bounds[0]&&x/size*360-180<bounds[2]&&latitude(y)>bounds[1]&&latitude(y+1)<bounds[3];
}

export class EarthEngineTileCache {
  readonly stats={downloads:0,memoryHits:0,diskHits:0,shared:0};
  private memory=new Map<string,Entry>();
  private pending=new Map<string,Pending>();
  private queue:Pending[]=[];
  private active=0;
  private bytes=0;
  private invalidated=new Set<string>();
  private writes:Promise<unknown>=Promise.resolve();
  private storage:Promise<Cache|null>;
  constructor(private fetcher:typeof fetch=(input,init)=>fetch(input,init),storage?:Promise<Cache|null>,private now=Date.now){
    this.storage=storage??(typeof caches==='undefined'?Promise.resolve(null):caches.open(CACHE_NAME).catch(()=>null));
  }

  load(url:string,signal:AbortSignal,expires=this.now()+MAX_AGE):Promise<Blob>{
    signal.throwIfAborted();
    const destination=new URL(url);
    if(destination.protocol!=='https:'||destination.hostname!=='earthengine.googleapis.com'||destination.username||destination.password)
      return Promise.reject(new Error('Unexpected imagery destination.'));
    const cached=this.memory.get(url);
    if(cached){
      this.memory.delete(url);this.bytes-=cached.blob.size;
      if(cached.expires>this.now()){
        this.remember(url,cached);this.stats.memoryHits++;return Promise.resolve(cached.blob);
      }
    }
    let pending=this.pending.get(url);
    if(pending)this.stats.shared++;
    else{
      let resolve!:(blob:Blob)=>void,reject!:(error:unknown)=>void;
      const promise=new Promise<Blob>((yes,no)=>{resolve=yes;reject=no;});
      pending={promise,resolve,reject,signals:new Set(),url,expires:Math.min(expires,this.now()+MAX_AGE)};
      this.pending.set(url,pending);this.queue.push(pending);
    }
    pending.signals.add(signal);
    this.pump();
    return pending.promise;
  }

  private remember(url:string,entry:Entry){
    this.memory.set(url,entry);this.bytes+=entry.blob.size;
    while(this.memory.size>MAX_TILES||this.bytes>MAX_BYTES){
      const key=this.memory.keys().next().value!;
      this.bytes-=this.memory.get(key)!.blob.size;this.memory.delete(key);
    }
  }

  invalidate(url:string){
    const cached=this.memory.get(url);
    if(cached){this.bytes-=cached.blob.size;this.memory.delete(url);}
    this.invalidated.add(url);
    this.writes=this.writes.catch(()=>{}).then(async()=>{await (await this.storage)?.delete(url);}).catch(()=>{}).finally(()=>this.invalidated.delete(url));
  }

  private pump(){
    while(this.active<12&&this.queue.length){
      const item=this.queue.shift()!;
      if([...item.signals].every(signal=>signal.aborted)){
        this.pending.delete(item.url);item.reject(new DOMException('Tile is no longer visible.','AbortError'));continue;
      }
      this.active++;
      void this.retrieve(item).then(item.resolve,item.reject).finally(()=>{
        this.pending.delete(item.url);this.active--;this.pump();
      });
    }
  }

  private async retrieve(item:Pending){
    const cache=await this.storage;
    try{
      const saved=this.invalidated.has(item.url)?undefined:await cache?.match(item.url);
      if(saved&&Number(saved.headers.get('x-satellite-expires'))>this.now()){
        const blob=await saved.blob();
        this.remember(item.url,{blob,expires:Number(saved.headers.get('x-satellite-expires'))});
        this.stats.diskHits++;return blob;
      }
    }catch{/* Storage is optional; blocked/full storage must not block imagery. */}
    this.stats.downloads++;
    const response=await this.fetcher(item.url,{credentials:'omit',referrerPolicy:'no-referrer',signal:AbortSignal.timeout(45000)});
    if(!response.ok||!response.headers.get('content-type')?.startsWith('image/'))throw new Error('Earth Engine could not load this tile.');
    const blob=await response.blob();
    if(blob.size>2*1024*1024)throw new Error('Earth Engine returned an oversized tile.');
    this.remember(item.url,{blob,expires:item.expires});
    // Serialize disk writes/eviction, off the display path. CacheStorage lives
    // in this browser, never in Git or a public service worker/CDN cache.
    if(cache)this.writes=this.writes.catch(()=>{}).then(async()=>{
      await cache.put(item.url,new Response(blob,{headers:{'content-type':blob.type,'x-satellite-expires':String(item.expires),'x-satellite-bytes':String(blob.size)}}));
      const keys=await cache.keys();let bytes=0,count=0;
      for(const key of [...keys].reverse()){
        const saved=await cache.match(key);
        const size=Number(saved?.headers.get('x-satellite-bytes'))||0;
        const expired=Number(saved?.headers.get('x-satellite-expires'))<=this.now();
        if(expired||++count>MAX_TILES||bytes+size>MAX_BYTES)await cache.delete(key);
        else bytes+=size;
      }
    }).catch(()=>{});
    return blob;
  }
}
