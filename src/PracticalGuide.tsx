import {supplementalPhoto} from './article-photos';
import {CurationStar} from './TeamAccess';
import {useEffect} from 'react';
import {Link, useLocation, useNavigate} from 'react-router-dom';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {ArrowLeft, ArrowRight, Download} from 'lucide-react';
import {guideDocuments, guideHeadingId, type GuideDocument} from './guides';
import {Button} from './components/arc/button/button';
import {templatePath} from './template-path';
import {guideForReaders} from './guide-presentation';

export function PracticalGuide({guide}: {guide: GuideDocument}) {
 const location = useLocation();
 const cover = supplementalPhoto(guide.title);
 const navigate = useNavigate();
 const markdown = guide.listed ? guideForReaders(guide.markdown) : guide.markdown;
 const headings = [...markdown.matchAll(/^## (.+)$/gm)].map(m => m[1]);
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
    <div className="curation-heading"><h1>{guide.heading}</h1>{guide.listed && <CurationStar recordId={guide.id} title={guide.title}/>}</div>
    {cover && <figure className="article-cover"><img className="detail-image" src={cover.src} alt={cover.alt}/><figcaption>Illustrative photo · <a href={cover.source}>{cover.credit}</a> · <a href={cover.licenseUrl}>{cover.license}</a> · resized & cropped</figcaption></figure>}
    {guide.summary && <p className="guide-summary">{guide.summary}</p>}
    <p className="guide-status"><strong>Draft for review.</strong> Sources checked 23 October 2026. Legal review and live service checks remain open. <Link to="/read/guide-verification">See what needs verification</Link>.</p>
    <details className="guide-contents" key={guide.id}>
     <summary>On this page</summary>
     <nav aria-label="Guide sections">{headings.map(h => <Link key={h} to={'#' + guideHeadingId(h)} replace state={location.state}>{h}</Link>)}</nav>
    </details>
    <div className="reading-body guide-body">
     <Markdown remarkPlugins={[remarkGfm]} components={{
      h2: ({children}) => <h2 id={guideHeadingId(String(children))}>{children}</h2>,
      a: ({href, children}) => href === 'https://gswa.goa.gov.in/gazette-notification/'
       ? <span><a href={href}>{children}</a> <span className="source-availability">(Source page was unavailable when checked on 26 October 2026. <a href="https://www.goa.gov.in/department_additiona/goa-state-wetland-authority-downloads/">Try the official downloads directory</a>; access could not be confirmed.)</span></span>
       : href?.startsWith('/guides/templates/')
       ? <Link to={templatePath(href)} state={{guideId:guide.id}}>{children}</Link>
       : href?.startsWith('/read/') || href === '/library'
       ? <Link to={href}>{children}</Link>
       : <a href={href} download={href?.startsWith('/guides/') ? '' : undefined}>{children}</a>,
      table: ({children}) => <div className="guide-table" role="region" aria-label="Reference table" tabIndex={0}><table>{children}</table></div>,
     }}>{markdown}</Markdown>
    </div>
   </article>
   <aside className="detail-aside guide-aside">
    {guide.templates.length > 0 && <section><h2>Forms to fill in</h2><p>Complete a form here, then save a PDF if you need a copy.</p>{guide.templates.map(t => <Link className="guide-download" key={t.url} to={templatePath(t.url)} state={{guideId:guide.id}}><span>{t.label}<small className="template-link-hint">Fill in form</small></span><ArrowRight size={16}/></Link>)}</section>}
    <section><h2>Sources and review</h2><Link className="guide-download" to="/read/guide-sources">Official source register<ArrowRight size={16}/></Link><Link className="guide-download" to="/read/guide-verification">Verification register<ArrowRight size={16}/></Link><a className="guide-download" href={guide.download} download>Download this guide<Download size={16}/></a><Link className="guide-download" to={'/contact?entry=' + encodeURIComponent(guide.title)}>Suggest a correction<ArrowRight size={16}/></Link></section>
    <section><h2>Related practical guides</h2>{guideDocuments.filter(g => g.listed && g.id !== guide.id).map(g => <Link className="guide-download" key={g.id} to={'/read/' + g.id}>{g.title}<ArrowRight size={16}/></Link>)}</section>
   </aside>
  </div>
 </main>;
}
