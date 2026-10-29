import { useEffect, useState } from 'react';
import { Link, useNavigationType, useParams, useSearchParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, ArrowUpRight, BookOpen, FileDown } from 'lucide-react';
import { SearchField } from './components/arc/search-field/search-field';
import { Button } from './components/arc/button/button';
import { ButtonLink } from './components/arc/button/button-link';
import {
  climatePlan, planTopics, planPageHref, planPdfPage, planPageLabel,
  searchPlanTopics, searchPlanChapters, type PlanReference, type PlanTopic,
} from './climate-plan';
import './climate-plan.css';
import { climatePlanResearchPath } from './climate-plan-research';

const source = climatePlan.source;
const viewNames = { topics: 'By topic', chapters: 'Chapter index', source: 'About the source' };
type PlanView = keyof typeof viewNames;

function SourceLink({ reference }: { reference: PlanReference }) {
  return <a className="plan-source-link" href={planPageHref(reference.start)} target="_blank" rel="noreferrer"
    aria-label={`${reference.label}, printed ${planPageLabel(reference)}, PDF page ${planPdfPage(reference.start)}. Opens government PDF in a new tab.`}>
    <span>{reference.label} · {planPageLabel(reference)}</span><ArrowUpRight size={16} aria-hidden="true" />
  </a>;
}

function TopicNavigation({ topicId, search }: { topicId: string; search: string }) {
  return <nav aria-label="Climate plan topics">
    {planTopics.map(topic => <Link key={topic.id} to={`/climate-plan/${topic.id}${search}`}
      aria-current={topic.id === topicId ? 'page' : undefined}>{topic.title}</Link>)}
  </nav>;
}

function TopicDetail({ topic, search }: { topic: PlanTopic; search: string }) {
  const [copied, setCopied] = useState(false);
  const [copyFailed, setCopyFailed] = useState(false);
  async function copyQuestion() {
    try {
      await navigator.clipboard.writeText(`${topic.question}\n\nReference: Goa SAPCC 2023–2033, ${topic.references.map(reference => `${reference.label}, ${planPageLabel(reference)}`).join('; ')}.\n${planPageHref(topic.references[0].start)}`);
      setCopied(true);
      setCopyFailed(false);
    } catch {
      setCopyFailed(true);
    }
  }
  return <>
    <Link className="back-link" to={`/climate-plan${search}`}><ArrowLeft size={16} aria-hidden="true" />All climate plan topics</Link>
    <div className="plan-detail-layout">
      <aside className="plan-topic-rail">
        <h2>Explore the plan</h2>
        <TopicNavigation topicId={topic.id} search={search} />
      </aside>
      <article className="plan-reading">
        <header>
          <h1>{topic.title}</h1>
          <p className="plan-intro">{topic.summary}</p>
          <p className="plan-edition">Goa SAPCC 2023–2033 · Published April 2023</p>
          <ButtonLink className="plan-chat-link" variant="secondary" size="sm" to={climatePlanResearchPath}
            state={{draftQuestion: `What does Goa’s SAPCC propose for ${topic.title.toLowerCase()}?`}}>Ask about this topic<ArrowRight size={17} aria-hidden="true" /></ButtonLink>
        </header>
        <details className="plan-mobile-topics"><summary>Choose another topic</summary><TopicNavigation topicId={topic.id} search={search} /></details>
        <section className="plan-actions" aria-labelledby="plan-actions-heading">
          <h2 id="plan-actions-heading">What the plan says</h2>
          <p>Selected measures, explained by ActForGoa. These describe the plan; current delivery and availability need confirmation.</p>
          {topic.actions.map(action => <section className="plan-action" key={action.title}>
            <h3>{action.title}</h3>
            <p>{action.description}</p>
            <p className="plan-agencies"><strong>Named in the plan:</strong> {action.agencies}.</p>
            <SourceLink reference={action.reference} />
          </section>)}
          {topic.note && <p className="plan-note">{topic.note}</p>}
        </section>
        <section className="plan-next-step" aria-labelledby="plan-question-heading">
          <h2 id="plan-question-heading">A question to take forward</h2>
          <p>Use this at a community meeting or when asking the relevant department for an update.</p>
          <p className="plan-question">{topic.question}</p>
          <div className="plan-question-tools">
            <Button variant="secondary" onClick={copyQuestion}>{copied ? 'Copy again' : 'Copy question & reference'}</Button>
            <Link to="/templates/03-rti-records-request" className="text-link">Prepare a records request<ArrowRight size={17} aria-hidden="true" /></Link>
          </div>
          <p className="plan-copy-status" role="status">{copyFailed ? 'Copy is unavailable in this browser. Select the question above and copy it manually.' : copied ? 'Question and source reference copied. Nothing has been sent.' : ''}</p>
        </section>
        <section className="plan-read-more" aria-labelledby="plan-read-more-heading">
          <h2 id="plan-read-more-heading">Read the full context</h2>
          <p>Links open the government PDF in a new tab. Most PDF pages contain two printed pages. If your viewer starts at the cover, use the page numbers below.</p>
          {topic.references.map(reference => <div className="plan-reference" key={reference.label}>
            <SourceLink reference={reference} />
            <span>PDF page {planPdfPage(reference.start)}</span>
          </div>)}
        </section>
        <section className="plan-related" aria-labelledby="plan-related-heading">
          <h2 id="plan-related-heading">Connected topics</h2>
          {topic.related.map(id => <Link key={id} to={`/climate-plan/${id}${search}`} className="text-link">{planTopics.find(candidate => candidate.id === id)?.title}<ArrowRight size={17} aria-hidden="true" /></Link>)}
        </section>
        <Link className="text-link" to="/climate-plan?view=source">About this source and its limitations<ArrowRight size={17} aria-hidden="true" /></Link>
      </article>
    </div>
  </>;
}

function SourceDetails() {
  return <article className="plan-source-details">
    <h2>The document behind this guide</h2>
    <dl className="plan-source-facts">
      <div><dt>Plan</dt><dd>{source.title}, {source.period}</dd></div>
      <div><dt>Published by</dt><dd>{source.publisher}, prepared through {source.preparedWith}</dd></div>
      <div><dt>Publication date</dt><dd>26 April 2023, recorded on PDF page 3</dd></div>
      <div><dt>Copy used here</dt><dd>NITI for States government repository · 111 PDF pages · 9.2 MB</dd></div>
      <div><dt>Source checked</dt><dd>29 October 2026</dd></div>
    </dl>
    <h3>How to use the references</h3>
    <p>The book’s printed numbers run to 218, but the file has 111 pages because most are two-page spreads. Our links open the matching PDF page and also show the printed numbers. Some mobile PDF viewers ignore page links; use the displayed PDF page number in that case.</p>
    <h3>A guide to the plan, with room to go deeper</h3>
    <p>ActForGoa wrote these topic summaries and selected 26 measures to help residents find their way. The chapter index covers all ten chapters, seven annexures and the appendix. Search covers this authored index and selected measures. It does not search every word in the PDF.</p>
    <p>“Mitigation” means reducing the emissions that cause climate change. “Adaptation” means preparing for and responding to its effects. The plan contains both.</p>
    <h3>What needs a fresh check</h3>
    <p>Project statuses, department assignments, schemes and timelines reflect the source document. They do not confirm what is available or complete today. We have not treated the plan as a live progress report or as a source of property-level permissions.</p>
    <p>The plan contains inconsistent budget totals and some older timeline wording. <Link to="/climate-plan/funding">Read the funding notes</Link> before using those figures. The scanned committee minutes in Annexure VII are available in the PDF, but their text is not reliably extracted.</p>
    <h3>Where the copy comes from</h3>
    <p>The <a href={source.assemblyUrl} target="_blank" rel="noreferrer">Goa Assembly answer of 8 August 2025</a> identifies the 2023–2033 plan and links to GSBB. That GSBB download returned an error when checked. We used the accessible NITI for States copy; we could not compare its bytes with the unavailable GSBB file.</p>
    <div className="plan-source-options">
      <a className="text-link" href={source.url} target="_blank" rel="noreferrer">Open government PDF<ArrowUpRight size={17} aria-hidden="true" /></a>
      <a className="text-link" href={source.originalUrl} target="_blank" rel="noreferrer">Try GSBB link · unavailable at last check<ArrowUpRight size={17} aria-hidden="true" /></a>
      <a className="text-link" href="/guides/goa-climate-plan.md" download>Download this reading guide<FileDown size={17} aria-hidden="true" /></a>
    </div>
  </article>;
}

export default function ClimatePlan() {
  const { topicId } = useParams();
  const [params, setParams] = useSearchParams();
  const navigationType = useNavigationType();
  const urlQuery = params.get('q') ?? '';
  const [query, setQuery] = useState(urlQuery);
  // Keep typing synchronous while router transitions persist the shareable URL.
  // Back/Forward and view links restore their query; our own replacements do not
  // overwrite a newer keystroke with an earlier navigation result.
  useEffect(() => {
    if (navigationType !== 'REPLACE') setQuery(urlQuery);
  }, [urlQuery, navigationType]);
  const requestedView = params.get('view');
  const view: PlanView = requestedView === 'chapters' || requestedView === 'source' ? requestedView : 'topics';
  const returnParams = new URLSearchParams(params);
  returnParams.delete('view');
  query ? returnParams.set('q', query) : returnParams.delete('q');
  const topicSearch = returnParams.size ? `?${returnParams}` : '';
  const topic = planTopics.find(candidate => candidate.id === topicId);
  const results = view === 'chapters' ? searchPlanChapters(query) : searchPlanTopics(query);
  const updateQuery = (value: string) => {
    setQuery(value);
    const next = new URLSearchParams(params);
    value ? next.set('q', value) : next.delete('q');
    setParams(next, { replace: true, preventScrollReset: true });
  };
  if (topicId) return <main className="shell climate-plan" lang="en">
    {topic ? <TopicDetail key={topic.id} topic={topic} search={topicSearch} /> : <div className="plan-unavailable"><h1>That climate topic isn’t here.</h1><p>Choose a topic from the plan’s overview.</p><Link className="text-link" to="/climate-plan">Explore the climate plan<ArrowRight size={18} aria-hidden="true" /></Link></div>}
  </main>;

  return <main className="shell climate-plan" lang="en">
    <Link className="back-link" to="/library"><ArrowLeft size={16} aria-hidden="true" />Resource library</Link>
    <header className="plan-heading">
      <div>
        <h1>Goa’s climate action plan</h1>
        <p className="plan-intro">Find proposals for everyday life.</p>
        <p className="plan-edition">State Action Plan for Climate Change (SAPCC) · 2023–2033</p>
        <ButtonLink className="plan-chat-link" variant="secondary" size="sm" to={climatePlanResearchPath}>Ask about this plan<ArrowRight size={17} aria-hidden="true" /></ButtonLink>
      </div>
      <div className="plan-original">
        <ButtonLink href={source.url} className="plan-pdf-button" target="_blank" rel="noreferrer"><BookOpen size={19} aria-hidden="true" />Open full plan<ArrowUpRight size={17} aria-hidden="true" /></ButtonLink>
        <span>Government PDF · 111 pages · 9.2 MB</span>
      </div>
    </header>
    <nav className="plan-view-nav" aria-label="Ways to explore the climate plan">
      {(Object.entries(viewNames) as [PlanView, string][]).map(([key, label]) => {
        const next = new URLSearchParams(params);
        query ? next.set('q', query) : next.delete('q');
        key === 'topics' ? next.delete('view') : next.set('view', key);
        return <Link key={key} to={`/climate-plan${next.size ? `?${next}` : ''}`} aria-current={view === key ? 'page' : undefined} preventScrollReset>{label}</Link>;
      })}
    </nav>
    {view === 'source' ? <SourceDetails /> : <>
      <div className="plan-search">
        <SearchField label={view === 'topics' ? 'Search topics and selected actions' : 'Search the chapter index'} value={query} onValueChange={updateQuery} placeholder={view === 'topics' ? 'Try flooding or solar' : 'Try water or finance'} aria-describedby="plan-search-help" />
        <p id="plan-search-help">{view === 'topics' ? 'From the 2023 plan. Check current delivery locally.' : 'Printed pages are shown first. Links open the PDF in a new tab.'}</p>
      </div>
      <div className="plan-results-heading"><h2>{view === 'topics' ? 'What matters to you?' : 'Read the plan in order'}</h2><p role="status">{results.length} {view === 'topics' ? 'topics' : 'sections'}{query.trim() ? ' found' : ' to explore'}</p></div>
      {!results.length ? <section className="plan-empty"><h3>No {view === 'topics' ? 'topics' : 'chapters'} match “{query}”.</h3><p>Try a shorter phrase, such as water or health. To search the whole document, open the PDF and use its search.</p><Button variant="secondary" onClick={() => updateQuery('')}>Clear search</Button></section>
        : view === 'topics' ? <div className="plan-topic-grid">{searchPlanTopics(query).map(item => <Link className="plan-topic-row" key={item.id} to={`/climate-plan/${item.id}${topicSearch}`}>
          <div><h3>{item.title}</h3><p>{item.summary}</p><span>{item.references[0].label} · {planPageLabel(item.references[0])}</span></div><ArrowRight size={21} aria-hidden="true" />
        </Link>)}</div>
        : <div className="plan-chapters">{searchPlanChapters(query).map(chapter => <section className="plan-chapter" key={chapter.id}>
          <div><h3><a href={planPageHref(chapter.start)} target="_blank" rel="noreferrer">{chapter.title}<ArrowUpRight size={18} aria-hidden="true" /></a></h3><p>{chapter.description}</p>
            {chapter.children && <details><summary>Browse sector sections</summary><div>{chapter.children.map(child => <SourceLink key={child.label} reference={child} />)}</div></details>}
          </div><p className="plan-page-numbers">{planPageLabel(chapter)}<span>PDF page {planPdfPage(chapter.start)}</span></p>
        </section>)}</div>}
      <div className="plan-bottom-note"><p>Published by the Goa State Biodiversity Board in April 2023. Reading guide by ActForGoa. Source copy checked 29 October 2026.</p><Link className="text-link" to="/climate-plan?view=source">About the source<ArrowRight size={17} aria-hidden="true" /></Link></div>
    </>}
  </main>;
}
