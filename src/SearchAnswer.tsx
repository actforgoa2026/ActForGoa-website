import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Button } from './components/arc/button/button';
import { cachedSearchAnswer, fetchSearchAnswer, type SearchAnswer as Answer } from './search-answer';
import './search-answer.css';

export function SearchAnswer({ question }: { question: string }) {
  const location = useLocation();
  const returnTo = location.pathname + location.search;
  const [answer, setAnswer] = useState<Answer | undefined>(() => cachedSearchAnswer(question));
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [busy, setBusy] = useState(!answer);
  useEffect(() => {
    const controller = new AbortController();
    setBusy(true); setError('');
    fetchSearchAnswer(question, controller.signal).then(value => {
      if (!controller.signal.aborted) setAnswer(value);
    }).catch((cause: Error) => {
      if (!controller.signal.aborted) setError(cause.message || 'The answer could not load. The results below are still available.');
    }).finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [question, attempt]);

  return <section className="search-answer" aria-labelledby="search-answer-heading" aria-busy={busy}>
    <h2 id="search-answer-heading">A short answer</h2>
    <p className="search-answer-context">AI summary from the ActForGoa corpus. Check the cited sources before acting.</p>
    <div aria-live="polite" aria-atomic="false">
      {busy && !answer && <p className="search-answer-status" role="status">Looking through our saved sources… The articles and other results are ready below.</p>}
      {error && <div className="search-answer-fallback"><p role="status">{error}</p><Button variant="ghost" onClick={() => setAttempt(value => value + 1)}>Try answer again</Button></div>}
      {answer?.status === 'insufficient_evidence' && <p className="search-answer-status">Our saved sources do not contain enough evidence for a reliable answer to this question. Try a more specific place or issue, or explore the results below.</p>}
      {answer?.status === 'answered' && answer.paragraphs.map((paragraph, index) => <p className="search-answer-paragraph" key={index}>
        {paragraph.text}{paragraph.citations.map(id => {
          const number = answer.citations.findIndex(source => source.id === id);
          const source = answer.citations[number];
          return <Link className="search-answer-citation" key={id} to={source.reader_url} state={{ researchReturn: returnTo }} aria-label={`Source ${number + 1}: ${source.title}, ${source.label}`}>[{number + 1}]</Link>;
        })}
      </p>)}
    </div>
    {answer?.status === 'answered' && answer.notice && <p className="search-answer-notice">{answer.notice}</p>}
    {answer?.status === 'answered' && <details className="search-answer-sources"><summary>Sources for this answer ({answer.citations.length})</summary>
      <ol>{answer.citations.map(source => <li key={source.id}><Link to={source.reader_url} state={{ researchReturn: returnTo }}>{source.title}<span>{source.label}</span></Link></li>)}</ol>
    </details>}
    <div className="search-answer-footer">
      <Link className="text-link" to={'/ask?' + new URLSearchParams({ q: question })}>Explore the research <ArrowRight size={16} aria-hidden="true" /></Link>
      <p>Your search and relevant saved passages are sent to OpenRouter to prepare this answer. No live web search is used.</p>
    </div>
  </section>;
}
