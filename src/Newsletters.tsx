import {useEffect} from 'react';
import {Link, useParams} from 'react-router-dom';
import {ArrowLeft, Download} from 'lucide-react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import archive from './content/newsletters.json';
import './newsletters.css';

export default function Newsletters() {
 const {issueId} = useParams();
 const issue = archive.find(item => item.id === issueId);
 useEffect(() => { document.title = `${issue?.title || 'Newsletters'} | ActForGoa`; }, [issue]);
 if (issueId && !issue) return <main className="shell newsletter-page"><h1>Newsletter not found</h1><p>Choose an issue from the archive.</p><Link to="/newsletters">All newsletters</Link></main>;
 return <main className="shell newsletter-page">
  <Link className="back-link" to={issue ? '/newsletters' : '/library'}><ArrowLeft size={16}/>{issue ? 'All newsletters' : 'Back to resources'}</Link>
  {issue ? <article className="newsletter-article">
   <header><h1>{issue.title}</h1><p className="newsletter-date">{issue.date}</p><p className="newsletter-archive-note">From the ActForGoa archive. Events, contacts and opportunities are described as they were when this issue was published.</p>
    <div className="newsletter-source-links"><a href={issue.source} target="_blank" rel="noopener noreferrer">View original issue</a>{issue.pdf && <><a href={issue.pdf} target="_blank" rel="noopener noreferrer">Open PDF</a><a href={issue.pdf} download><Download size={16}/>Save PDF</a></>}</div>
   </header>
   {issue.pdf && <p className="newsletter-transcription-note">Text transcribed from the published PDF. Report names in the original PDF have no linked destinations; their wording is retained below.</p>}
   <div className="newsletter-prose"><Markdown remarkPlugins={[remarkGfm]} skipHtml components={{
    a: ({href, children}) => <a href={href} target={/^https?:/.test(href || '') ? '_blank' : undefined} rel="noopener noreferrer">{children}</a>,
    img: ({src,alt}) => <img src={src} alt={alt || ''} loading="lazy"/>,
    em: ({children}) => <span>{children}</span>,
    h1: ({children}) => <h2>{children}</h2>,
   }}>{issue.markdown || ''}</Markdown></div>
   {issue.pdf && <details className="newsletter-original-layout"><summary>View the original layout and illustrations</summary><div className="newsletter-pdf-pages">
    {[1,2,3,4].map(page => <figure key={page}><img src={`/assets/newsletters/2025-year-end-page-${page}.webp`} alt={`Original year-end newsletter 2024–2025, page ${page} of 4. Article text is transcribed above.`} loading="lazy" width={1132} height={1600}/><figcaption>Page {page} of 4</figcaption></figure>)}
   </div></details>}
   <div className="newsletter-end"><p>Original issue checked 29 October 2026. {issue.pdf ? 'The text was transcribed and checked against all four pages; original spellings and historical wording are retained.' : 'The web edition preserves the published content with email controls removed and the greeting made generic.'}</p><Link to="/newsletters">Browse another issue</Link></div>
  </article> : <>
   <header className="newsletter-heading"><h1>Newsletters</h1><p>Stories, projects and community updates from the original ActForGoa archive.</p></header>
   <div className="newsletter-list">{archive.map(item => <article key={item.id}><div><h2><Link to={`/newsletters/${item.id}`}>{item.title}</Link></h2><p className="newsletter-issue-date">{item.date}</p><p>{item.summary}</p></div><Link className="newsletter-read-link" to={`/newsletters/${item.id}`}>Read issue</Link></article>)}</div>
   <p className="newsletter-index-note">Five original issues, checked 29 October 2026. <a href="https://actforgoa.org/newsletters/" target="_blank" rel="noopener noreferrer">View the original archive</a>.</p>
  </>}
 </main>;
}
