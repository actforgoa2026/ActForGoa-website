import {useEffect} from 'react';
import {Link, useLocation, useNavigate} from 'react-router-dom';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {ArrowLeft, ArrowRight, Download} from 'lucide-react';
import {guideDocuments, guideHeadingId, type GuideDocument} from './guides';
import {Button} from './components/arc/button/button';
import {TopicIcon} from './components/TopicIcon';
import {topicFor} from './topic-flows';
import {guideForReaders} from './guide-presentation';

export function PracticalGuide({guide}: {guide: GuideDocument}) {
 const location = useLocation();
 const navigate = useNavigate();
 const markdown = guide.listed ? guideForReaders(guide.markdown) : guide.markdown;
 const headings = [...markdown.matchAll(/^## (.+)$/gm)].map(m => m[1]);
 const contents = <nav aria-label="Guide sections">{headings.map(h => <Link key={h} to={'#' + guideHeadingId(h)} replace state={location.state}>{h}</Link>)}</nav>;
 useEffect(() => {
  const previous = document.title;
  document.title = guide.title + ' | ActForGoa';
  return () => { document.title = previous; };
 }, [guide.title]);
 return <main className="detail shell practical-guide">
  {location.state?.fromCatalogue
   ? <Button variant="ghost" className="back-link" onClick={() => navigate(-1)}><ArrowLeft size={16}/>{location.state?.fromHome ? 'Back to exploring' : 'Back to results'}</Button>
   : <Link className="back-link" to="/library"><ArrowLeft size={16}/>Back to library</Link>}
  <div className="detail-layout">
   <article>
    <header className="guide-intro">
    <TopicIcon name={topicFor(guide.topics[0])?.icon || 'book'}/>
    <div>
    <h1>{guide.heading}</h1>
    {guide.summary && <p className="guide-summary">{guide.summary}</p>}
    </div>
    </header>
    <details className="guide-contents guide-mobile-contents" key={guide.id}>
     <summary>On this page</summary>
     {contents}
    </details>
    <div className="reading-body guide-body">
     <Markdown remarkPlugins={[remarkGfm]} components={{
      h2: ({children}) => <h2 id={guideHeadingId(String(children))}>{children}</h2>,
      a: ({href, children}) => href?.startsWith('/read/') || href === '/library'
       ? <Link to={href}>{children}</Link>
       : <a href={href} download={href?.startsWith('/guides/') ? '' : undefined}>{children}</a>,
      table: ({children}) => <div className="guide-table" role="region" aria-label="Reference table" tabIndex={0}><table>{children}</table></div>,
     }}>{markdown}</Markdown>
    </div>
    <details className="source-links"><summary>About this guide</summary><p>This guide is still being reviewed. Check current requirements with the relevant service before acting.</p><Link to="/read/guide-sources">Official sources</Link><Link to="/read/guide-verification">Detailed review notes</Link></details>
   </article>
   <aside className="detail-aside guide-aside">
    {guide.listed ? <section className="guide-desktop-contents"><h2>On this page</h2>{contents}</section> : <details className="guide-contents guide-desktop-contents"><summary>On this page</summary>{contents}</details>}
    {guide.templates.length > 0 && <section><h2>Templates to use</h2><p>Download, edit and use the required official form where one applies.</p>{guide.templates.map(t => <a className="guide-download" key={t.url} href={t.url} download><span>{t.label}</span><Download size={16}/></a>)}</section>}
    <section><h2>Save or share</h2><a className="guide-download" href={guide.download} download>Download this guide<Download size={16}/></a><Link className="guide-download" to={'/contact?entry=' + encodeURIComponent(guide.title)}>Suggest a correction<ArrowRight size={16}/></Link></section>
    <section><h2>Related practical guides</h2>{guideDocuments.filter(g => g.listed && g.id !== guide.id).map(g => <Link className="guide-download" key={g.id} to={'/read/' + g.id}>{g.title}<ArrowRight size={16}/></Link>)}</section>
   </aside>
  </div>
 </main>;
}
