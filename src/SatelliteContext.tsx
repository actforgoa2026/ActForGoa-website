import type {SatelliteContext as Context} from './satellite-api';

export function SatelliteContext({context}:{context:Context}){
  return <section className="satellite-library" aria-label="Ecology library context"><h3>What the ecology library can add</h3><p>{context.message}</p>
    {context.state==='no_matches'&&<p>No usable ecology passages matched this question. This is not evidence that no relevant research exists.</p>}
    {context.sources.map((source,index)=><article key={source.id+'-'+index}><h4><a href={source.reader_url}>[{index+1}] {source.title}</a></h4>
      <p className="satellite-excerpt">{source.text}{source.excerpt_truncated?'…':''}</p>
      <p className="satellite-note">{source.label}{source.retrieved_at?' · Retrieved '+source.retrieved_at:''}</p>
      {source.warning&&<p className="satellite-note">{source.warning}</p>}
      <a href={source.url} target="_blank" rel="noreferrer">Original source ↗</a>
    </article>)}
  </section>;
}
