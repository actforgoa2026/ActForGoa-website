import { ButtonLink } from './components/arc/button/button-link';
import {useEffect} from 'react';
import {useLanguage} from './language';
import {translatePriority} from './priority-translations';
import {Link, useLocation, useParams} from 'react-router-dom';
import {ArrowLeft, ArrowRight, ArrowUpRight, Download} from 'lucide-react';
import {topicFlows, allTopicActions, actionHref, type TopicFlow, type TopicAction} from './topic-flows';
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
 const positive=choices.filter(action=>!action.concern);
 const concerns=choices.filter(action=>action.concern);
 const renderChoices=(items:TopicAction[]) => <nav className={"choice-grid"+(items.length===2 || items.length===4 ? " choice-grid-pairs" : "")} aria-label={parent?.question || 'Choose what you need'}>
   {items.map(action => <ButtonLink wrap variant="secondary" className="topic-action-link" key={action.id} to={actionHref(flow,action,parent)}>
    <TopicIcon name={action.icon}/><span className="choice-copy" lang={translatePriority(action.label, language) === action.label ? "en" : language}><span>{translatePriority(action.label, language)}</span>{action.description && <span className="choice-description" lang="en">{action.description}</span>}</span><ArrowRight size={22} aria-hidden="true"/>
   </ButtonLink>)}
  </nav>;
 return <section className="topic-choices" aria-labelledby={'choices-'+flow.slug}>
  <h2 id={'choices-'+flow.slug} lang={translatePriority(parent?.question || 'What would you like to do?', language) === (parent?.question || 'What would you like to do?') ? 'en' : language}>{translatePriority(parent?.question || 'What would you like to do?', language)}</h2>
  {positive.length > 0 && renderChoices(positive)}
  {concerns.length > 0 && <div className="topic-concerns"><h3>Need help with a problem?</h3>{renderChoices(concerns)}</div>}
 </section>;
}

export function TopicPage({records}: {records:RecordItem[]}) {
 const starredIds=useStarredIds();
 const { language }=useLanguage();
 const location=useLocation();
 const {slug,actionId,choiceId}=useParams();
 const flow=topicFlows.find(f=>f.slug===slug);
 const parent=flow && allTopicActions(flow).find(a=>a.id===actionId);
 const action=choiceId ? parent?.choices?.find(a=>a.id===choiceId) : parent;
 const missing=!flow || (actionId && !parent) || (choiceId && !action);
 useEffect(()=>{const previous=document.title;document.title=(action?.label || flow?.label || 'Find help')+' | ActForGoa';return()=>{document.title=previous;};},[flow,action]);
 if(missing || !flow) return <main className="shell topic-page"><h1>That option isn’t available.</h1><Link className="text-link" to="/">Choose a topic <ArrowRight size={20}/></Link></main>;
 const related=records.filter(r=>(flow.catalogueTopics ?? [flow.topic]).some(topic=>r.topics.includes(topic)));
 const people=topicPeople(records,flow,action);
 // Explicit action recommendations retain their editorial order.
 const rankedPeople=action ? people : prioritizeStarred(people,starredIds,record=>record.id);
 const reading=related.filter(r=>r.kind==='resource' || r.kind==='story');
 const rankedReading=(action ? hybridSearch(reading,action.query,null).map(x=>x.record) : [...reading]).sort((a,b)=>Number(!!b.image || b.editorialStatus==='authored-practical-guide')-Number(!!a.image || a.editorialStatus==='authored-practical-guide'));
 const linkedIds=(action?.links || []).filter(l=>l.href.startsWith('/read/')).map(l=>l.href.slice(6).split('#')[0]);
 const pinned=[...actionsInBranch(action ? [action] : flow.actions).flatMap(a=>a.resourceIds || []),...linkedIds].flatMap(id=>records.find(r=>r.id===id) || []);
 const readingEntries=[...new Map([...pinned,...prioritizeStarred(rankedReading,starredIds,record=>record.id)].map(r=>[r.id,r])).values()].slice(0,6);
 const searchParams=new URLSearchParams(flow.catalogueTopics ? {q:action?.query || flow.label} : {topic:flow.topic});
 if(action) searchParams.set('q',action.query);
 return <main className="shell topic-page">
  <nav className="topic-breadcrumb" aria-label="Breadcrumb">
   <Link to="/">Home</Link>{action && <span aria-hidden="true">/</span>}
   {action ? <><Link to={'/topics/'+flow.slug}>{translatePriority(flow.label, language)}</Link></> : null}
   {choiceId && parent && <><span aria-hidden="true">/</span><Link to={'/topics/'+flow.slug+'/'+parent.id}>{translatePriority(parent.label, language)}</Link></>}
  </nav>
  <header className="topic-page-heading"><TopicIcon name={action?.icon || flow.icon}/><h1 lang={translatePriority(action?.label || flow.label, language) === (action?.label || flow.label) ? 'en' : language}>{translatePriority(action?.label || flow.label, language)}</h1></header>
  {(action?.description || (!action && flow.introduction)) && <p className="topic-introduction" lang="en">{action?.description || flow.introduction}</p>}
  {!action ? <TopicChoices flow={flow}/> : action.choices ? <TopicChoices flow={flow} parent={action}/> : <>
   {!!action.links?.length && <section className="action-destinations" aria-label="Take your next step"><div className="choice-grid">
    {action.links.map(link => link.href.startsWith('#') || link.href.startsWith('/read/') || (link.href.startsWith('/') && !link.download)
     ? <ButtonLink wrap variant="secondary" className="topic-action-link" key={link.href} to={link.href} state={{fromCatalogue:true,...(link.href.startsWith('/templates/') ? {returnTo:location.pathname} : {})}}><TopicIcon name={link.icon || action.icon}/><span lang={translatePriority(link.label, language) === link.label ? "en" : language}>{translatePriority(link.label, language)}</span><ArrowRight size={24}/></ButtonLink>
     : <ButtonLink wrap variant="secondary" className="topic-action-link" key={link.href} href={link.href} download={link.download || undefined}><TopicIcon name={link.icon || action.icon}/><span lang={translatePriority(link.label, language) === link.label ? "en" : language}>{translatePriority(link.label, language)}</span>{link.download ? <Download size={24}/> : <ArrowUpRight size={24}/>}</ButtonLink>)}
   </div></section>}
   {!!action.steps?.length && <section className="action-steps"><h2>How to get started</h2><ol>{action.steps.map(step=><li key={step} lang={translatePriority(step, language) === step ? "en" : language}>{translatePriority(step, language)}</li>)}</ol></section>}
   {action.infographic && <figure className="topic-infographic"><a href={action.infographic.source}><img src={action.infographic.src} alt={action.infographic.alt} loading="lazy" /></a><figcaption>{action.infographic.caption} <a href={action.infographic.source}>Open the original infographic</a></figcaption></figure>}
  </>}
  <nav className="topic-support" aria-label="More ways to take part">
    <Link to={'/topics/'+flow.slug+'/schemes'}>Government schemes <ArrowRight size={18}/></Link>
    <Link to={'/topics/'+flow.slug+'#topic-people'}>Key organisations and partners <ArrowRight size={18}/></Link>
    <Link to={'/contact?'+new URLSearchParams({reason:'Suggest an improvement',subject:action?.label || flow.label})}>Suggest an improvement <ArrowRight size={18}/></Link>
  </nav>
  {(rankedPeople.length > 0 || !action) && <section className="topic-directory" aria-labelledby="topic-people">
   <div className="section-heading"><h2 id="topic-people">Key organisations and partners</h2><Link className="text-link" to={'/directory/archive?'+searchParams}>See all <ArrowRight size={18}/></Link></div>
   <p className="topic-archive-note">Archived listings · confirm current availability.</p>
   {rankedPeople.length ? <div className="card-grid">{rankedPeople.slice(0,6).map(r=><RecordCard key={r.id} record={r}/>)}</div> : <p>No matching organisations yet. <Link className="text-link" to={'/directory/archive?topic='+encodeURIComponent(flow.topic)}>Browse the wider directory <ArrowRight size={18}/></Link></p>}
  </section>}
  {!!readingEntries.length && <section className="topic-reading" id="topic-reading" aria-labelledby="topic-reading-heading">
   <div className="section-heading"><h2 id="topic-reading-heading">Guides & useful reading</h2><Link className="text-link" to={'/library?'+searchParams}>See all guides <ArrowRight size={18}/></Link></div>
   <div className="card-grid">{readingEntries.map(r=><RecordCard key={r.id} record={r}/>)}</div>
  </section>}


 </main>;
}
