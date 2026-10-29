import {useEffect} from 'react';
import {useLanguage} from './language';
import {translatePriority} from './priority-translations';
import {Link, useLocation, useParams} from 'react-router-dom';
import {ArrowRight, ArrowUpRight, Download} from 'lucide-react';
import {topicFlows, actionHref, type TopicFlow, type TopicAction} from './topic-flows';
import {TopicIcon} from './components/TopicIcon';
import {RecordCard} from './components/RecordCard';
import {hybridSearch} from './search';
import {actionsInBranch, topicPeople} from './topic-records';
import type {RecordItem} from './types';
import {useStarredIds} from './CurationProvider';
import {prioritizeStarred} from './curation';

export function TopicChoices({flow, parent}: {flow:TopicFlow; parent?:TopicAction}) {
 const { language }=useLanguage();
 const choices=parent?.choices ?? flow.actions;
 return <section className="topic-choices" aria-label={parent?.question || flow.label}>
  {parent?.question && <h2>{translatePriority(parent.question, language)}</h2>}
  <nav className={"choice-grid"+(choices.length===2 || choices.length===4 ? " choice-grid-pairs" : "")} aria-label={parent?.question || 'Choose what you need'}>
   {choices.map(action => <Link className="choice-link" key={action.id} to={actionHref(flow,action,parent)}>
    <TopicIcon name={action.icon}/><span lang={translatePriority(action.label, language) === action.label ? "en" : language}>{translatePriority(action.label, language)}</span><ArrowRight size={22}/>
   </Link>)}
  </nav>
 </section>;
}

export function TopicPage({records}: {records:RecordItem[]}) {
 const starredIds=useStarredIds();
 const { language }=useLanguage();
 const location=useLocation();
 const {slug,actionId,choiceId}=useParams();
 const flow=topicFlows.find(f=>f.slug===slug);
 const parent=flow?.actions.find(a=>a.id===actionId);
 const action=choiceId ? parent?.choices?.find(a=>a.id===choiceId) : parent;
 const missing=!flow || (actionId && !parent) || (choiceId && !action);
 useEffect(()=>{const previous=document.title;document.title=(action?.label || flow?.label || 'Find help')+' | ActForGoa';return()=>{document.title=previous;};},[flow,action]);
 if(missing || !flow) return <main className="shell topic-page"><h1>That option isn’t available.</h1><Link className="text-link" to="/">Choose a topic <ArrowRight size={20}/></Link></main>;
 const related=records.filter(r=>r.topics.includes(flow.topic));
 const people=topicPeople(records,flow,action);
 // Explicit action recommendations retain their editorial order.
 const rankedPeople=action ? people : prioritizeStarred(people,starredIds,record=>record.id);
 const reading=related.filter(r=>r.kind==='resource' || r.kind==='story');
 const rankedReading=(action ? hybridSearch(reading,action.query,null).map(x=>x.record) : [...reading]).sort((a,b)=>Number(!!b.image || b.editorialStatus==='authored-practical-guide')-Number(!!a.image || a.editorialStatus==='authored-practical-guide'));
 const linkedIds=(action?.links || []).filter(l=>l.href.startsWith('/read/')).map(l=>l.href.slice(6).split('#')[0]);
 const pinned=[...actionsInBranch(action ? [action] : flow.actions).flatMap(a=>a.resourceIds || []),...linkedIds].flatMap(id=>records.find(r=>r.id===id) || []);
 const readingEntries=[...new Map([...pinned,...prioritizeStarred(rankedReading,starredIds,record=>record.id)].map(r=>[r.id,r])).values()].slice(0,3);
 const searchParams=new URLSearchParams({topic:flow.topic});
 if(action) searchParams.set('q',action.query);
 return <main className="shell topic-page">
  <nav className="topic-breadcrumb" aria-label="Breadcrumb">
   <Link to="/">Home</Link>{action && <span aria-hidden="true">/</span>}
   {action ? <><Link to={'/topics/'+flow.slug}>{translatePriority(flow.label, language)}</Link></> : null}
   {choiceId && parent && <><span aria-hidden="true">/</span><Link to={'/topics/'+flow.slug+'/'+parent.id}>{translatePriority(parent.label, language)}</Link></>}
  </nav>
  <header className="topic-page-heading"><TopicIcon name={action?.icon || flow.icon}/><h1 lang={language}>{translatePriority(action?.label || flow.label, language)}</h1></header>
  {!action ? <TopicChoices flow={flow}/> : action.choices ? <TopicChoices flow={flow} parent={action}/> : <>
   {!!action.links?.length && <section className="action-destinations" aria-label="Take your next step"><div className="choice-grid">
    {action.links.map(link => link.href.startsWith('#') || link.href.startsWith('/read/') || (link.href.startsWith('/') && !link.download)
     ? <Link className="choice-link" key={link.href} to={link.href} state={{fromCatalogue:true,...(link.href.startsWith('/templates/') ? {returnTo:location.pathname} : {})}}><TopicIcon name={link.icon || action.icon}/><span lang={translatePriority(link.label, language) === link.label ? "en" : language}>{translatePriority(link.label, language)}</span><ArrowRight size={24}/></Link>
     : <a className="choice-link" key={link.href} href={link.href} download={link.download || undefined}><TopicIcon name={link.icon || action.icon}/><span lang={translatePriority(link.label, language) === link.label ? "en" : language}>{translatePriority(link.label, language)}</span>{link.download ? <Download size={24}/> : <ArrowUpRight size={24}/>}</a>)}
   </div></section>}
   {!!action.steps?.length && <section className="action-steps"><h2 lang={language}>{translatePriority('How to get started', language)}</h2><ol>{action.steps.map(step=><li key={step} lang={translatePriority(step, language) === step ? "en" : language}>{translatePriority(step, language)}</li>)}</ol></section>}
  </>}
  {!!readingEntries.length && <section className="topic-reading" aria-labelledby="topic-reading">
   <div className="section-heading"><h2 id="topic-reading" lang={language}>{translatePriority("Guides & useful reading", language)}</h2><Link className="text-link" to={'/library?'+searchParams}><span lang={language}>{translatePriority("See all guides", language)}</span> <ArrowRight size={18}/></Link></div>
   <div className="card-grid">{readingEntries.map(r=><RecordCard key={r.id} record={r}/>)}</div>
  </section>}
  {(rankedPeople.length > 0) && <section className="topic-directory" aria-labelledby="topic-people">
   <div className="section-heading"><h2 id="topic-people" lang={language}>{translatePriority("People & organisations", language)}</h2><Link className="text-link" to={'/directory/archive?'+searchParams}><span lang={language}>{translatePriority("See all", language)}</span> <ArrowRight size={18}/></Link></div>
   <p className="topic-archive-note">Archived listings · confirm current availability.</p>
   <div className="card-grid">{rankedPeople.slice(0,3).map(r=><RecordCard key={r.id} record={r} compact/>)}</div>
  </section>}

 </main>;
}
