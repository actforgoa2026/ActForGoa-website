import {useEffect} from 'react';
import {Link, useParams} from 'react-router-dom';
import {ArrowLeft, ArrowRight, ArrowUpRight, Download} from 'lucide-react';
import {topicFlows, actionHref, type TopicFlow, type TopicAction} from './topic-flows';
import {TopicIcon} from './components/TopicIcon';
import {RecordCard} from './components/RecordCard';
import {hybridSearch} from './search';
import type {RecordItem} from './types';

export function TopicChoices({flow, parent}: {flow:TopicFlow; parent?:TopicAction}) {
 const choices=parent?.choices ?? flow.actions;
 return <section className="topic-choices" aria-labelledby={'choices-'+flow.slug}>
  <h2 id={'choices-'+flow.slug}>{parent?.question || 'What would you like to do?'}</h2>
  <nav className={"choice-grid"+(choices.length===4 ? " choice-grid-pairs" : "")} aria-label={parent?.question || 'Choose what you need'}>
   {choices.map(action => <Link className="choice-link" key={action.id} to={actionHref(flow,action,parent)}>
    <TopicIcon name={action.icon}/><span>{action.label}</span><ArrowRight size={22}/>
   </Link>)}
  </nav>
 </section>;
}

export function TopicPage({records}: {records:RecordItem[]}) {
 const {slug,actionId,choiceId}=useParams();
 const flow=topicFlows.find(f=>f.slug===slug);
 const parent=flow?.actions.find(a=>a.id===actionId);
 const action=choiceId ? parent?.choices?.find(a=>a.id===choiceId) : parent;
 const missing=!flow || (actionId && !parent) || (choiceId && !action);
 useEffect(()=>{const previous=document.title;document.title=(action?.label || flow?.label || 'Find help')+' | ActForGoa';return()=>{document.title=previous;};},[flow,action]);
 if(missing || !flow) return <main className="shell topic-page"><h1>That option isn’t available.</h1><Link className="text-link" to="/">Choose a topic <ArrowRight size={20}/></Link></main>;
 const related=records.filter(r=>r.topics.includes(flow.topic));
 const people=related.filter(r=>r.kind==='organisation' || r.kind==='contact');
 const peopleIds=action?.peopleIds || flow.actions.flatMap(a=>a.peopleIds || []);
 const pinnedPeople=peopleIds.flatMap(id=>people.find(r=>r.id===id) || []);
 const matchedPeople=action ? hybridSearch(people,action.query,null).map(x=>x.record) : people;
 const rankedPeople=action?.peopleIds?.length ? pinnedPeople : [...new Map([...pinnedPeople,...matchedPeople].map(r=>[r.id,r])).values()];
 const reading=related.filter(r=>r.kind==='resource' || r.kind==='story');
 const rankedReading=(action ? hybridSearch(reading,action.query,null).map(x=>x.record) : [...reading]).sort((a,b)=>Number(!!b.image || b.editorialStatus==='authored-practical-guide')-Number(!!a.image || a.editorialStatus==='authored-practical-guide'));
 const linkedIds=(action?.links || []).filter(l=>l.href.startsWith('/read/')).map(l=>l.href.slice(6).split('#')[0]);
 const pinned=[...(action?.resourceIds || (action ? [] : flow.actions.flatMap(a=>a.resourceIds || []))),...linkedIds].flatMap(id=>records.find(r=>r.id===id) || []);
 const readingEntries=[...new Map([...pinned,...rankedReading].map(r=>[r.id,r])).values()].slice(0,6);
 const searchParams=new URLSearchParams({topic:flow.topic});
 if(action) searchParams.set('q',action.query);
 return <main className="shell topic-page">
  <nav className="topic-breadcrumb" aria-label="Breadcrumb">
   <Link to="/">Home</Link><span aria-hidden="true">/</span>
   {action ? <><Link to={'/topics/'+flow.slug}>{flow.label}</Link><span aria-hidden="true">/</span></> : <span aria-current="page">{flow.label}</span>}
   {choiceId && parent && <><Link to={'/topics/'+flow.slug+'/'+parent.id}>{parent.label}</Link><span aria-hidden="true">/</span></>}
   {action && <span aria-current="page">{action.label}</span>}
  </nav>
  <header className="topic-page-heading"><TopicIcon name={action?.icon || flow.icon}/><h1>{action?.label || flow.label}</h1></header>
  {!action ? <TopicChoices flow={flow}/> : action.choices ? <TopicChoices flow={flow} parent={action}/> : <>
   {!!action.links?.length && <section className="action-destinations" aria-label="Take your next step"><div className="choice-grid">
    {action.links.map(link => link.href.startsWith('#') || link.href.startsWith('/read/') || (link.href.startsWith('/') && !link.download)
     ? <Link className="choice-link" key={link.href} to={link.href} state={{fromCatalogue:true}}><span>{link.label}</span><ArrowRight size={24}/></Link>
     : <a className="choice-link" key={link.href} href={link.href} download={link.download || undefined}><span>{link.label}</span>{link.download ? <Download size={24}/> : <ArrowUpRight size={24}/>}</a>)}
   </div></section>}
   {!!action.steps?.length && <section className="action-steps"><h2>How to get started</h2><ol>{action.steps.map(step=><li key={step}>{step}</li>)}</ol></section>}
  </>}
  <section className="topic-directory" aria-labelledby="topic-people">
   <div className="section-heading"><h2 id="topic-people">People & organisations</h2><Link className="text-link" to={'/directory?'+searchParams}>See all <ArrowRight size={18}/></Link></div>
   {rankedPeople.length ? <div className="card-grid">{rankedPeople.slice(0,6).map(r=><RecordCard key={r.id} record={r}/>)}</div> : <p>No matching organisations yet. <Link className="text-link" to={'/directory?topic='+encodeURIComponent(flow.topic)}>Browse the wider directory <ArrowRight size={18}/></Link></p>}
  </section>
  {!!readingEntries.length && <section className="topic-reading" aria-labelledby="topic-reading">
   <div className="section-heading"><h2 id="topic-reading">Guides & useful reading</h2><Link className="text-link" to={'/library?'+searchParams}>See all guides <ArrowRight size={18}/></Link></div>
   <div className="card-grid">{readingEntries.map(r=><RecordCard key={r.id} record={r}/>)}</div>
  </section>}
  <Link className="back-link" to={action ? '/topics/'+flow.slug : '/'}><ArrowLeft size={18}/>{action ? 'Choose a different need' : 'Choose a different topic'}</Link>
 </main>;
}
