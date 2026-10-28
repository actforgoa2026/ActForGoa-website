import {useEffect, useState} from 'react';
import {Link, useParams} from 'react-router-dom';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {ArrowLeft, ArrowRight} from 'lucide-react';
import {adminApi, AdminApiError, type PublicBlogPost, type PublicBlogPostSummary} from './admin-api';
import {Button} from './components/arc/button/button';
import './admin.css';

export function StoryBody({body}: {body: string}) {
  return <div className="blog-prose"><Markdown remarkPlugins={[remarkGfm]} skipHtml components={{
    a: ({children, href}) => <a href={href} rel="noopener noreferrer">{children}</a>,
    img: ({src, alt}) => src ? <img src={src} alt={alt || ''} loading="lazy" referrerPolicy="no-referrer"/> : null,
    h1: ({children}) => <h2>{children}</h2>,
  }}>{body}</Markdown></div>;
}
export function blogDate(value: string | null | undefined) {
  return value && !Number.isNaN(Date.parse(value)) ? new Intl.DateTimeFormat('en-IN', {day: 'numeric', month: 'short', year: 'numeric', timeZone: 'Asia/Kolkata'}).format(new Date(value)) : '';
}

export default function Blog() {
  const {slug} = useParams();
  const [posts, setPosts] = useState<PublicBlogPostSummary[]>([]);
  const [post, setPost] = useState<PublicBlogPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [missing, setMissing] = useState(false);
  const [retry, setRetry] = useState(0); const [nextCursor, setNextCursor] = useState<string | null>(null); const [morePending, setMorePending] = useState(false); const [moreError, setMoreError] = useState('');
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError(''); setMissing(false); setPost(null); setPosts([]); setNextCursor(null); setMoreError('');
    (slug ? adminApi<{post: PublicBlogPost}>(`/api/blog/${encodeURIComponent(slug)}`, {signal: controller.signal}).then(data => setPost(data.post))
      : adminApi<{posts: PublicBlogPostSummary[]; nextCursor: string | null}>('/api/blog', {signal: controller.signal}).then(data => { setPosts(data.posts); setNextCursor(data.nextCursor); }))
      .catch(error => { if (controller.signal.aborted) return; if (error instanceof AdminApiError && error.status === 404) setMissing(true); else setError(error instanceof Error ? error.message : 'Stories could not be loaded.'); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [slug, retry]);
  useEffect(() => { document.title = `${post?.title || 'Community journal'} | ActForGoa`; }, [post]);
  async function loadMore() {
    if (!nextCursor) return; setMorePending(true); setMoreError('');
    try { const data = await adminApi<{posts: PublicBlogPostSummary[]; nextCursor: string | null}>(`/api/blog?cursor=${encodeURIComponent(nextCursor)}`); setPosts(previous => [...previous, ...data.posts.filter(post => !previous.some(item => item.id === post.id))]); setNextCursor(data.nextCursor); }
    catch (error) { setMoreError(error instanceof Error ? error.message : 'More stories could not be loaded.'); } finally { setMorePending(false); }
  }
  return <main className="blog-page">
    <Link className="admin-text-link" to={slug ? '/blog' : '/'}><ArrowLeft size={16}/>{slug ? 'All stories' : 'ActForGoa home'}</Link>
    {!slug && <Link className="admin-text-link blog-archive-link" to="/blog/archive">Original story archive <ArrowRight size={16}/></Link>}
    {loading ? <p role="status" className="admin-state">Loading stories…</p> : missing ? <section className="admin-state"><h1>Story not available</h1><p>It may have moved or is no longer published.</p><Link className="admin-text-link" to="/blog">Browse the journal <ArrowRight size={16}/></Link></section>
      : error ? <div className="admin-state"><p role="alert">{error}</p><Button variant="secondary" onClick={() => setRetry(value => value + 1)}>Try again</Button></div>
      : post ? <article className="blog-article"><div className="admin-eyebrow">Community journal</div><h1>{post.title}</h1><p className="blog-deck">{post.excerpt}</p><p className="blog-byline">{post.authorName}{post.publishedAt ? ` · ${blogDate(post.publishedAt)}` : ''}</p><StoryBody body={post.body}/>{post.tags.length > 0 && <ul className="admin-tags" aria-label="Story topics">{post.tags.map(tag => <li key={tag}>{tag}</li>)}</ul>}</article>
      : <><header className="blog-heading"><div className="admin-eyebrow">Stories from the community</div><h1>Good work, shared.</h1><p>People, ideas and practical progress from across Goa.</p></header>{posts.length ? <div className="blog-grid">{posts.map(story => <article className="blog-card" key={story.id}><div className="admin-eyebrow">{blogDate(story.publishedAt)}</div><h2><Link to={`/blog/${encodeURIComponent(story.slug)}`}>{story.title}</Link></h2><p>{story.excerpt}</p><span className="blog-byline">{story.authorName}</span><Link className="admin-text-link" to={`/blog/${encodeURIComponent(story.slug)}`}>Read story <ArrowRight size={16}/></Link></article>)}</div> : <div className="admin-state"><h2>Our next chapter is taking shape.</h2><p>New stories will appear here when the team publishes them.</p></div>}{moreError && <p className="admin-error" role="alert">{moreError}</p>}{nextCursor && <div className="admin-load-more"><Button variant="secondary" loading={morePending} onClick={loadMore}>More stories</Button></div>}</>}
  </main>;
}
