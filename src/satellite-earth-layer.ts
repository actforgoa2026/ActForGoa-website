import {EarthEngineTileCache,earthEngineTile,tileIntersectsBounds} from './satellite-tile-cache';

export type EarthTileState={pending:number;failed:number;loaded:number};

/** A Google map type that reuses native-resolution Earth Engine parent tiles. */
export class EarthEngineLayer implements google.maps.MapType {
  readonly tileSize=new google.maps.Size(256,256);
  readonly minZoom=8;
  readonly maxZoom=19;
  readonly name='Earth Engine';
  readonly alt='Dated Sentinel-2 navigation overview';
  readonly projection=null;
  readonly radius=6378137;
  private tiles=new Map<Element,{abort:AbortController;state:'pending'|'loaded'|'failed';objectUrl?:string}>();
  private frame=0;
  private disposed=false;
  private started=performance.now();
  constructor(private template:string,private cache:EarthEngineTileCache,private changed:(state:EarthTileState)=>void,private expires?:number,private bounds?:readonly number[]){}

  getTile(point:google.maps.Point,zoom:number,owner:Document){
    if(![...this.tiles.values()].some(entry=>entry.state==='pending'))this.started=performance.now();
    const tile=owner.createElement('div');
    Object.assign(tile.style,{width:'256px',height:'256px',overflow:'hidden',position:'relative'});
    if(this.disposed)return tile;
    // The provider clips the overview to Goa. Avoid fetching known empty tiles.
    if(this.bounds&&!tileIntersectsBounds(point.x,point.y,zoom,this.bounds))return tile;
    const parent=earthEngineTile(point.x,point.y,zoom);
    const url=this.template.replace('{z}',String(parent.z)).replace('{x}',String(parent.x)).replace('{y}',String(parent.y));
    const entry:{abort:AbortController;state:'pending'|'loaded'|'failed';objectUrl?:string}={abort:new AbortController(),state:'pending'};
    this.tiles.set(tile,entry);this.notify();
    void this.cache.load(url,entry.abort.signal,this.expires).then(blob=>{
      if(entry.abort.signal.aborted)return;
      const image=owner.createElement('img');image.alt='';image.draggable=false;
      Object.assign(image.style,{position:'absolute',maxWidth:'none',width:`${256*parent.scale}px`,height:`${256*parent.scale}px`,left:`${parent.left}px`,top:`${parent.top}px`,imageRendering:parent.scale>1?'pixelated':'auto'});
      entry.objectUrl=URL.createObjectURL(blob);
      image.onload=()=>{if(!entry.abort.signal.aborted){entry.state='loaded';this.notify();}};
      image.onerror=()=>{if(!entry.abort.signal.aborted){this.cache.invalidate(url);entry.state='failed';this.notify();}};
      image.src=entry.objectUrl;tile.append(image);
    }).catch(error=>{if(!entry.abort.signal.aborted){if(import.meta.env.DEV)console.debug('Earth Engine tile error',error instanceof Error?error.message:'Tile unavailable');entry.state='failed';this.notify();}});
    return tile;
  }

  releaseTile(tile:Element|null){
    if(!tile)return;
    const entry=this.tiles.get(tile);
    entry?.abort.abort();if(entry?.objectUrl)URL.revokeObjectURL(entry.objectUrl);
    this.tiles.delete(tile);tile.replaceChildren();this.notify();
  }

  private notify(){
    if(this.disposed||this.frame)return;
    this.frame=requestAnimationFrame(()=>{
      this.frame=0;
      const state={pending:0,loaded:0,failed:0};
      for(const entry of this.tiles.values())state[entry.state]++;
      this.changed(state);
      if(import.meta.env.DEV&&!state.pending&&state.loaded)console.debug('Earth Engine tiles',JSON.stringify({elapsedMs:Math.round(performance.now()-this.started),visible:state.loaded,...this.cache.stats}));
    });
  }

  dispose(){
    this.disposed=true;cancelAnimationFrame(this.frame);
    for(const tile of this.tiles.keys())this.releaseTile(tile);
  }
}
