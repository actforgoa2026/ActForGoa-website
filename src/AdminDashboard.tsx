import {useEffect, useMemo, useRef, useState, type FormEvent} from 'react';
import {Link, useSearchParams} from 'react-router-dom';
import {ArrowLeft, ArrowRight, BookOpen, Check, ExternalLink, FileText, LayoutDashboard, LogOut, Plus, RefreshCw, Save, Search, ShieldCheck, Star, Users, X} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import {adminApi, AdminApiError, type AdminSession, type BlogPost, type BlogPostSummary, type CuratedStar, type PostInput} from './admin-api';
import {curationRecords, emptyPost, filterCuration, parseTags, postChanged, postInput, postStatus, slugFromTitle, validatePost} from './admin-model';
import type {CRMSnapshot} from './crm-model';
import type {RecordItem} from './types';
import {practicalGuideRecords} from './guide-records';
import {reviewPolytechnicSnapshot} from './polytechnic-directory';
import {blogDate, StoryBody} from './Blog';
import './admin.css';

type Tool = 'overview' | 'community' | 'blog';
const tools = [{id: 'overview', label: 'Overview', icon: LayoutDashboard}, {id: 'community', label: 'Community & resources', icon: Users}, {id: 'blog', label: 'Blog', icon: FileText}] as const;
const message = (error: unknown) => error instanceof Error ? error.message : 'Something went wrong. Please try again.';

function Login({onLogin, renewing = false, onCancel}: {onLogin: (session: AdminSession) => void; renewing?: boolean; onCancel?: () => void}) {
  const [email, setEmail] = useState(''); const [password, setPassword] = useState('');
  const [pending, setPending] = useState(false); const [error, setError] = useState('');
  async function submit(event: FormEvent) {
    event.preventDefault(); setPending(true); setError('');
    try { onLogin(await adminApi<AdminSession>('/api/admin/login', {method: 'POST', body: {email: email.trim(), password}})); setPassword(''); }
    catch (error) { setError(message(error)); }
    finally { setPending(false); }
  }
  return <section className="admin-login" aria-labelledby="admin-login-title"><div className="admin-login-mark"><ShieldCheck size={28}/></div><div className="admin-eyebrow">ActForGoa · Team workspace</div><h1 id="admin-login-title">{renewing ? 'Sign in again' : 'Welcome back.'}</h1><p>{renewing ? 'Your edits stay open while you renew your sign-in.' : 'Curate the people doing good work. Share the stories that matter.'}</p>
    <form onSubmit={submit}><Input label="Email address" type="email" autoComplete="username" autoFocus required maxLength={254} value={email} onChange={event => setEmail(event.target.value)}/><Input label="Password" type="password" autoComplete="current-password" required maxLength={256} value={password} onChange={event => setPassword(event.target.value)}/>{error && <p className="admin-error" role="alert">{error}</p>}<Button type="submit" loading={pending}>Sign in <ArrowRight size={16}/></Button></form>
    <p className="admin-note">Access is by invitation. Ask your team administrator if you need an account.</p>{onCancel ? <Button variant="ghost" onClick={onCancel}>Keep editing</Button> : <Link className="admin-text-link" to="/"><ArrowLeft size={16}/>Back to the website</Link>}
  </section>;
}

function RenewSessionDialog({onLogin, onCancel}: {onLogin: (session: AdminSession) => void; onCancel: () => void}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { const element = dialog.current; element?.showModal(); return () => element?.close(); }, []);
  return <dialog ref={dialog} className="admin-modal" aria-label="Renew your sign-in" onCancel={onCancel}><Login renewing onCancel={onCancel} onLogin={onLogin}/></dialog>;
}

export default function AdminDashboard() {
  const [session, setSession] = useState<AdminSession | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState(''); const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    document.title = 'Team workspace | ActForGoa'; const controller = new AbortController(); setLoading(true); setError('');
    adminApi<AdminSession>('/api/admin/session', {signal: controller.signal}).then(setSession).catch(error => { if (!controller.signal.aborted && !(error instanceof AdminApiError && error.status === 401)) setError(message(error)); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [attempt]);
  if (loading) return <main className="admin-state" role="status">Opening the team workspace…</main>;
  if (error) return <main className="admin-login"><ShieldCheck size={28}/><h1>Workspace unavailable</h1><p role="alert">{error}</p><Button onClick={() => setAttempt(value => value + 1)}>Try again</Button><Link className="admin-text-link" to="/">Back to the website</Link></main>;
  return session ? <Workspace session={session} onSession={setSession} onLogout={() => setSession(null)}/> : <main className="admin-login-page"><Login onLogin={setSession}/></main>;
}

function Workspace({session, onSession, onLogout}: {session: AdminSession; onSession: (session: AdminSession) => void; onLogout: () => void}) {
  const [params, setParams] = useSearchParams();
  const selectedTool = params.get('tool'); const tool: Tool = selectedTool === 'community' || selectedTool === 'blog' ? selectedTool : 'overview';
  const [posts, setPosts] = useState<BlogPostSummary[]>([]);
  const [postCounts, setPostCounts] = useState({draft: 0, published: 0}); const [totalPosts, setTotalPosts] = useState(0); const [postRefresh, setPostRefresh] = useState(0);
  const [nextCursor, setNextCursor] = useState<string | null>(null); const [morePending, setMorePending] = useState(false); const [openingPost, setOpeningPost] = useState(false); const openRequest = useRef(0); const postListRequest = useRef(0); const [stars, setStars] = useState<CuratedStar[]>([]); const [starsReady, setStarsReady] = useState(false);
  const [records, setRecords] = useState<ReturnType<typeof curationRecords>>([]);
  const [loading, setLoading] = useState(true); const [catalogueLoading, setCatalogueLoading] = useState(true);
  const [error, setError] = useState(''); const [catalogueError, setCatalogueError] = useState(''); const [notice, setNotice] = useState('');
  const [attempt, setAttempt] = useState(0); const [pendingStar, setPendingStar] = useState(''); const [loggingOut, setLoggingOut] = useState(false);
  const [renewing, setRenewing] = useState(false); const [expired, setExpired] = useState(false);
  const [query, setQuery] = useState(''); const [group, setGroup] = useState(''); const [onlyStarred, setOnlyStarred] = useState(false); const [page, setPage] = useState(1);
  const [postQuery, setPostQuery] = useState(''); const [postFilter, setPostFilter] = useState('all');
  const [editing, setEditing] = useState<BlogPost | 'new' | null>(null); const [editorKey, setEditorKey] = useState(0); const [dirty, setDirty] = useState(false);
  const dirtyRef = useRef(dirty); dirtyRef.current = dirty;
  const starMap = useMemo(() => new Map(stars.map(star => [star.recordId, star])), [stars]);
  const starredIds = useMemo(() => new Set(starMap.keys()), [starMap]);
  const knownIds = useMemo(() => new Set(records.map(record => record.id)), [records]);
  const orphaned = catalogueLoading || catalogueError ? [] : stars.filter(star => !knownIds.has(star.recordId));
  const filtered = useMemo(() => filterCuration(records, query, group, starredIds, onlyStarred), [records, query, group, starredIds, onlyStarred]);
  const lastPage = Math.max(1, Math.ceil(filtered.length / 20)); const currentPage = Math.min(page, lastPage); const visible = filtered.slice((currentPage - 1) * 20, currentPage * 20);
  const filteredPosts = posts;
  function failed(error: unknown) { setError(message(error)); if (error instanceof AdminApiError && (error.status === 401 || error.status === 403)) setExpired(true); }
  useEffect(() => {
    const controller = new AbortController(); setError(''); setStarsReady(false);
    adminApi<{stars: CuratedStar[]}>('/api/admin/stars', {signal: controller.signal})
      .then(data => { setStars(data.stars); setStarsReady(true); }).catch(error => { if (!controller.signal.aborted) failed(error); });
    return () => controller.abort();
  }, [attempt, session.user.id]);
  useEffect(() => {
    const controller = new AbortController(); const request = ++postListRequest.current; setLoading(true); setNextCursor(null); setMorePending(false);
    const timer = setTimeout(() => {
      const query = new URLSearchParams({q: postQuery, status: postFilter});
      adminApi<{posts: BlogPostSummary[]; nextCursor: string | null; total: number; counts: {draft: number; published: number}}>(`/api/admin/posts?${query}`, {signal: controller.signal})
        .then(data => { if (request !== postListRequest.current) return; setPosts(data.posts); setNextCursor(data.nextCursor); setTotalPosts(data.total); setPostCounts(data.counts); })
        .catch(error => { if (!controller.signal.aborted) failed(error); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    }, 200);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [attempt, session.user.id, postQuery, postFilter, postRefresh]);
  useEffect(() => {
    const controller = new AbortController(); setCatalogueLoading(true); setCatalogueError('');
    Promise.all([adminApi<CRMSnapshot>('/data/crm.json', {signal: controller.signal}), adminApi<RecordItem[]>('/data/catalog.json', {signal: controller.signal})])
      .then(([crm, catalogue]) => { if (!Array.isArray(crm.records) || !Array.isArray(catalogue)) throw Error('The directory could not be read.'); setRecords(curationRecords(reviewPolytechnicSnapshot(crm).records, [...practicalGuideRecords, ...catalogue])); })
      .catch(error => { if (!controller.signal.aborted) setCatalogueError(message(error)); }).finally(() => { if (!controller.signal.aborted) setCatalogueLoading(false); });
    return () => controller.abort();
  }, [attempt]);
  useEffect(() => {
    const beforeUnload = (event: BeforeUnloadEvent) => { if (dirtyRef.current) { event.preventDefault(); event.returnValue = ''; } };
    const leave = (event: MouseEvent) => {
      if (!dirtyRef.current || event.defaultPrevented || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
      const anchor = (event.target as Element)?.closest('a');
      if (!anchor || anchor.target === '_blank' || anchor.hasAttribute('download') || anchor.getAttribute('href')?.startsWith('#')) return;
      if (!window.confirm('Leave this page and discard your unsaved story changes?')) { event.preventDefault(); event.stopPropagation(); }
    };
    window.addEventListener('beforeunload', beforeUnload); document.addEventListener('click', leave, true);
    return () => { window.removeEventListener('beforeunload', beforeUnload); document.removeEventListener('click', leave, true); };
  }, []);
  function canLeave() { return !dirty || window.confirm('Discard your unsaved story changes?'); }
  function changeTool(next: Tool) { if (tool === next) return; if (!canLeave()) return; ++openRequest.current; setOpeningPost(false); setDirty(false); setEditing(null); setNotice(''); if (next === 'overview') { setPostQuery(''); setPostFilter('all'); } const nextParams = new URLSearchParams(); if (next !== 'overview') nextParams.set('tool', next); setParams(nextParams); }
  async function edit(post: BlogPostSummary | 'new' | null) {
    if (!canLeave()) return;
    const request = ++openRequest.current; setNotice('');
    if (post === null || post === 'new') { setDirty(false); setEditing(post); setEditorKey(value => value + 1); return; }
    setOpeningPost(true); setError('');
    try { const data = await adminApi<{post: BlogPost}>(`/api/admin/posts/${encodeURIComponent(post.id)}`); if (request !== openRequest.current) return; setDirty(false); setEditing(data.post); setEditorKey(value => value + 1); }
    catch (error) { if (request === openRequest.current) failed(error); }
    finally { if (request === openRequest.current) setOpeningPost(false); }
  }
  async function loadMorePosts() {
    if (!nextCursor) return; const request = postListRequest.current; setMorePending(true); setError('');
    try { const data = await adminApi<{posts: BlogPostSummary[]; nextCursor: string | null}>(`/api/admin/posts?${new URLSearchParams({cursor: nextCursor, q: postQuery, status: postFilter})}`); if (request !== postListRequest.current) return; setPosts(previous => [...previous, ...data.posts.filter(post => !previous.some(item => item.id === post.id))]); setNextCursor(data.nextCursor); }
    catch (error) { if (request === postListRequest.current) failed(error); } finally { if (request === postListRequest.current) setMorePending(false); }
  }
  async function toggleStar(recordId: string) {
    setPendingStar(recordId); setError(''); setNotice(''); const removing = starMap.has(recordId);
    try { const data = await adminApi<{stars: CuratedStar[]}>('/api/admin/stars', {method: 'PUT', csrfToken: session.csrfToken, body: {recordId, starred: !removing}}); setStars(data.stars); setNotice(removing ? 'Removed from team picks.' : 'Added to team picks.'); }
    catch (error) { failed(error); } finally { setPendingStar(''); }
  }
  async function logout() {
    if (!canLeave()) return; setLoggingOut(true); setError('');
    try { await adminApi('/api/admin/logout', {method: 'POST', csrfToken: session.csrfToken, body: {}}); onLogout(); } catch (error) { failed(error); } finally { setLoggingOut(false); }
  }
  function saved(post: BlogPost) { setPosts(previous => [post, ...previous.filter(item => item.id !== post.id)]); setEditing(post); setDirty(false); setPostRefresh(value => value + 1); }

  return <div className="admin-shell">
    <aside className="admin-sidebar"><Link className="admin-brand" to="/">ActForGoa<span>Team workspace</span></Link><div className="admin-sidebar-label">WORKSPACE</div><nav aria-label="Workspace tools">{tools.map(item => <button type="button" key={item.id} aria-current={tool === item.id ? 'page' : undefined} onClick={() => changeTool(item.id)}><item.icon size={19}/>{item.label}{item.id === 'blog' && postCounts.draft > 0 && <span className="admin-nav-count">{postCounts.draft}</span>}</button>)}</nav><div className="admin-sidebar-footer"><Link className="admin-text-link" to="/" target="_blank" rel="noopener noreferrer">View website <ExternalLink size={15}/></Link><div className="admin-person"><span className="admin-avatar" aria-hidden="true">{(session.user.name || session.user.email).slice(0, 1).toUpperCase()}</span><span><strong>{session.user.name}</strong><small>{session.user.role === 'admin' ? 'Administrator' : 'Editor'}</small></span></div><Button variant="ghost" size="sm" loading={loggingOut} onClick={logout}><LogOut size={16}/>Sign out</Button></div></aside>
    <main className="admin-main"><div className="admin-topline"><span>WORKSPACE / {tools.find(item => item.id === tool)?.label.toUpperCase()}</span><span className="admin-team-label"><ShieldCheck size={14}/>Team access</span></div>
      {error && <div className="admin-error" role="alert"><p>{error}</p>{expired ? <Button size="sm" variant="secondary" onClick={() => setRenewing(true)}>Sign in again</Button> : <Button size="sm" variant="ghost" onClick={() => setAttempt(value => value + 1)}>Retry loading</Button>}</div>}{notice && <p role="status" className="admin-success"><Check size={16}/>{notice}</p>}
      {tool === 'overview' && <><header className="admin-heading"><div><div className="admin-eyebrow">A little care makes a difference</div><h1>Your community, well connected.</h1><p>Bring useful people and resources forward. Keep Goa’s stories moving.</p></div></header><div className="admin-stat-grid"><div><Star size={20}/><strong>{starsReady ? stars.length : '—'}</strong><span>Team picks</span></div><div><FileText size={20}/><strong>{loading ? '—' : postCounts.draft}</strong><span>Stories in draft</span></div><div><BookOpen size={20}/><strong>{loading ? '—' : postCounts.published}</strong><span>Published stories</span></div></div><div className="admin-tool-grid"><section className="admin-panel"><Users size={28}/><h2>Help people find the right people.</h2><p>Star trusted organisations, community members and resources. Your team’s choices get priority when they match a visitor’s search.</p><Button variant="secondary" onClick={() => changeTool('community')}>Curate the directory <ArrowRight size={16}/></Button></section><section className="admin-panel"><FileText size={28}/><h2>Make good work visible.</h2><p>Draft, preview and publish stories from across Goa. Work stays private until you choose to publish.</p><Button variant="secondary" onClick={() => changeTool('blog')}>Open the blog <ArrowRight size={16}/></Button></section></div><section className="admin-panel admin-recent"><div className="admin-section-heading"><h2>Recently edited stories</h2><Button size="sm" variant="ghost" onClick={() => changeTool('blog')}>View all <ArrowRight size={16}/></Button></div>{loading ? <p role="status">Loading your workspace…</p> : posts.length ? posts.slice(0, 4).map(post => <button className="admin-recent-row" key={post.id} onClick={() => { changeTool('blog'); edit(post); }}><span><strong>{post.title || 'Untitled draft'}</strong><small>{blogDate(post.updatedAt)}</small></span><span className="admin-badge">{postStatus(post)}</span><ArrowRight size={16}/></button>) : <p>No stories yet. Start with a community update or a useful local guide.</p>}</section></>}
      {tool === 'community' && <><header className="admin-heading"><div><div className="admin-eyebrow">Community curation</div><h1>Make the best work easier to find.</h1><p>Team picks rise within relevant results. Starring a record does not verify its details.</p></div><span className="admin-count"><Star size={17}/>{starsReady ? stars.length : '—'} team picks</span></header><div className="admin-filters"><label className="admin-search"><Search size={18}/><input aria-label="Search community and resources" placeholder="Search a name, cause or place" value={query} onChange={event => { setQuery(event.target.value); setPage(1); }}/></label><label className="admin-select"><span className="sr-only">Record group</span><select value={group} onChange={event => { setGroup(event.target.value); setPage(1); }}><option value="">All records</option><option value="community">Community & organisations</option><option value="government">Government</option><option value="resource">Resources & stories</option></select></label><button className="admin-filter-toggle" type="button" aria-pressed={onlyStarred} onClick={() => { setOnlyStarred(value => !value); setPage(1); }}><Star size={16} fill={onlyStarred ? 'currentColor' : 'none'}/>Team picks</button></div>{catalogueError && <div role="alert" className="admin-error">{catalogueError}<Button variant="secondary" onClick={() => setAttempt(value => value + 1)}>Reload directory</Button></div>}{loading || catalogueLoading ? <p className="admin-state" role="status">Loading the directory…</p> : <><p className="admin-result-count">{filtered.length.toLocaleString('en-IN')} matching records</p><div className="admin-curation-list">{visible.map(record => { const star = starMap.get(record.id); return <article className="admin-curation-row" key={record.id}><button className="admin-star" type="button" disabled={!!pendingStar || !starsReady} aria-pressed={!!star} aria-label={`${star ? 'Unstar' : 'Star'} ${record.title}`} onClick={() => toggleStar(record.id)}><Star size={21} fill={star ? 'currentColor' : 'none'}/></button><div className="admin-record-copy"><div className="admin-eyebrow">{record.kind}</div><h2><Link to={record.href} target="_blank" rel="noopener noreferrer">{record.title}<ExternalLink size={13}/></Link></h2><p>{record.summary}</p><div className="admin-record-evidence">{record.evidence}</div>{star && <div className="admin-star-credit">Picked by {star.updatedBy.name} · {blogDate(star.updatedAt)}</div>}</div><span className="admin-record-topic">{record.topics.slice(0, 2).join(' · ')}</span></article>; })}{!visible.length && <div className="admin-state"><h2>No matches yet.</h2><p>Try a broader search or choose another record group.</p><Button variant="ghost" onClick={() => { setQuery(''); setGroup(''); setOnlyStarred(false); setPage(1); }}>Clear filters</Button></div>}</div><div className="admin-pagination"><Button size="sm" variant="secondary" disabled={currentPage <= 1} onClick={() => setPage(currentPage - 1)}>Previous</Button><span>Page {currentPage} of {lastPage}</span><Button size="sm" variant="secondary" disabled={currentPage >= lastPage} onClick={() => setPage(currentPage + 1)}>Next</Button></div></>}{orphaned.length > 0 && <section className="admin-panel"><h2>Picks to review</h2><p>These records are no longer in the current directory. They are not promoted publicly.</p>{orphaned.map(star => <div className="admin-orphan" key={star.recordId}><code>{star.recordId}</code><Button size="sm" variant="ghost" disabled={!!pendingStar || !starsReady} onClick={() => toggleStar(star.recordId)}>Remove pick</Button></div>)}</section>}</>}
      {tool === 'blog' && (openingPost ? <p className="admin-state" role="status">Opening your story…</p> : editing ? <PostEditor key={editorKey} post={editing === 'new' ? null : editing} session={session} onSaved={saved} onDirty={setDirty} onClose={() => edit(null)} onExpired={() => { setExpired(true); setRenewing(true); }}/> : <><header className="admin-heading"><div><div className="admin-eyebrow">Community journal</div><h1>Stories worth sharing.</h1><p>A place for local voices, useful knowledge and work in progress.</p></div><Button onClick={() => edit('new')} disabled={loading || openingPost}><Plus size={18}/>New story</Button></header><div className="admin-filters"><label className="admin-search"><Search size={18}/><input aria-label="Search stories" placeholder="Find a story" maxLength={200} value={postQuery} onChange={event => setPostQuery(event.target.value)}/></label><label className="admin-select"><span className="sr-only">Story status</span><select value={postFilter} onChange={event => setPostFilter(event.target.value)}><option value="all">All stories</option><option value="draft">Drafts</option><option value="published">Published</option></select></label><Link className="admin-text-link" to="/blog" target="_blank" rel="noopener noreferrer">View journal <ExternalLink size={15}/></Link></div>{loading ? <p className="admin-state" role="status">Loading stories…</p> : filteredPosts.length ? <div className="admin-post-list">{filteredPosts.map(post => <article className="admin-post-row" key={post.id}><div><span className={`admin-badge ${post.status === 'published' ? 'is-published' : ''}`}>{postStatus(post)}</span><h2><button type="button" onClick={() => edit(post)}>{post.title || 'Untitled draft'}</button></h2><p>{post.excerpt || 'Add an introduction to help readers find this story.'}</p><small>{post.authorName} · Updated {blogDate(post.updatedAt)}</small></div><Button variant="ghost" size="sm" onClick={() => edit(post)}>Edit story <ArrowRight size={16}/></Button></article>)}</div> : <div className="admin-state"><FileText size={32}/><h2>{postCounts.draft + postCounts.published > 0 ? 'No matching stories.' : 'Every good story starts somewhere.'}</h2><p>{postCounts.draft + postCounts.published > 0 ? 'Try another search or status.' : 'Open a draft, gather your thoughts, and share it when you’re ready.'}</p>{postCounts.draft + postCounts.published === 0 && <Button onClick={() => edit('new')}><Plus size={16}/>Write the first story</Button>}</div>}{nextCursor && <div className="admin-load-more"><p>Showing {posts.length} of {totalPosts} matching stories.</p><Button variant="secondary" loading={morePending} onClick={loadMorePosts}>Load more stories</Button></div>}</>)}
    </main>{renewing && <RenewSessionDialog onCancel={() => setRenewing(false)} onLogin={next => { onSession(next); setRenewing(false); setExpired(false); setError(''); setNotice('You are signed in. Your open edits are ready to save.'); }}/>}
  </div>;
}

function PostEditor({post, session, onSaved, onDirty, onClose, onExpired}: {post: BlogPost | null; session: AdminSession; onSaved: (post: BlogPost) => void; onDirty: (dirty: boolean) => void; onClose: () => void; onExpired: () => void}) {
  const [saved, setSaved] = useState(post); const [draft, setDraft] = useState<PostInput>(() => post ? postInput(post) : emptyPost()); const [tags, setTags] = useState(post?.tags.join(', ') || '');
  const [slugEdited, setSlugEdited] = useState(!!post); const [preview, setPreview] = useState(false); const [pending, setPending] = useState('');
  const [error, setError] = useState(''); const [notice, setNotice] = useState(''); const [confirm, setConfirm] = useState<'publish' | 'unpublish' | null>(null); const [conflict, setConflict] = useState(false);
  const actualDraft = {...draft, tags: parseTags(tags)}; const dirty = postChanged(actualDraft, saved); const words = draft.body.trim().split(/\s+/).filter(Boolean).length;
  useEffect(() => { onDirty(dirty); }, [dirty, saved?.version, onDirty]);
  function update(key: keyof Omit<PostInput, 'tags'>, value: string) { setDraft(previous => ({...previous, [key]: value, ...(key === 'title' && !slugEdited ? {slug: slugFromTitle(value)} : {})})); setNotice(''); setConfirm(null); }
  function apply(next: BlogPost) { setSaved(next); setDraft(postInput(next)); setTags(next.tags.join(', ')); setSlugEdited(true); onSaved(next); }
  function failure(error: unknown) { setError(message(error)); setConflict(error instanceof AdminApiError && error.status === 409); if (error instanceof AdminApiError && (error.status === 401 || error.status === 403)) onExpired(); }
  async function save() {
    const invalid = validatePost(actualDraft); if (invalid) throw new Error(invalid);
    if (saved && !dirty) return saved;
    const result = await adminApi<{post: BlogPost}>(saved ? `/api/admin/posts/${encodeURIComponent(saved.id)}` : '/api/admin/posts', {method: saved ? 'PATCH' : 'POST', csrfToken: session.csrfToken, body: {...actualDraft, ...(saved ? {version: saved.version} : {})}});
    apply(result.post); return result.post;
  }
  async function saveDraft() {
    setPending('save'); setError(''); setNotice('');
    try { const next = await save(); setNotice(next.status === 'published' ? 'Changes saved. Publish when you want to update the live story.' : 'Draft saved for your team.'); setConflict(false); }
    catch (error) { failure(error); } finally { setPending(''); }
  }
  async function publish(action: 'publish' | 'unpublish') {
    setPending(action); setError(''); setNotice('');
    try {
      if (action === 'publish') { const invalid = validatePost(actualDraft, true); if (invalid) throw Error(invalid); }
      const current = action === 'publish' ? await save() : saved;
      if (!current) throw Error('Save a draft before changing its publication status.');
      const result = await adminApi<{post: BlogPost}>(`/api/admin/posts/${encodeURIComponent(current.id)}/${action}`, {method: 'POST', csrfToken: session.csrfToken, body: {version: current.version}});
      if (action === 'unpublish' && dirty) { setSaved(result.post); onSaved(result.post); }
      else apply(result.post);
      setNotice(action === 'publish' ? 'Published. Your story is now in the public journal.' : dirty ? 'Unpublished. Your unsaved edits are still open.' : 'Unpublished. This story is now a private draft.'); setConfirm(null); setConflict(false);
    } catch (error) { failure(error); } finally { setPending(''); }
  }
  async function reload() {
    if (!saved || !window.confirm('Load the latest saved story? Your unsaved text will be discarded.')) return;
    setPending('reload'); setError('');
    try { const result = await adminApi<{post: BlogPost}>(`/api/admin/posts/${encodeURIComponent(saved.id)}`); apply(result.post); setConflict(false); setNotice('Loaded the latest saved version.'); }
    catch (error) { failure(error); } finally { setPending(''); }
  }
  return <section className="admin-editor"><div className="admin-editor-toolbar"><Button variant="ghost" size="sm" disabled={!!pending} onClick={onClose}><ArrowLeft size={16}/>All stories</Button><span className="admin-editor-save-state" role="status">{dirty ? 'Unsaved changes' : saved ? `Saved ${blogDate(saved.updatedAt)}` : 'New draft'}</span><Button size="sm" variant="secondary" disabled={!!pending || (!dirty && !!saved)} onClick={saveDraft}><Save size={16}/>{pending === 'save' ? 'Saving…' : 'Save draft'}</Button></div><header className="admin-heading"><div><div className="admin-eyebrow">{saved ? postStatus(saved) : 'New story'}</div><h1>{saved ? 'Give your story room.' : 'What’s happening in Goa?'}</h1><p>Keep it useful, clear and grounded in the people doing the work.</p></div><div className="admin-preview-toggle" role="group" aria-label="Editor view"><button type="button" aria-pressed={!preview} onClick={() => setPreview(false)}>Write</button><button type="button" aria-pressed={preview} onClick={() => setPreview(true)}>Preview</button></div></header>{error && <div className="admin-error" role="alert"><p>{error}</p>{conflict && <><p>Your text is still here. Copy anything you want to keep before loading the latest team version.</p><Button variant="secondary" size="sm" disabled={!!pending} onClick={reload}><RefreshCw size={15}/>Load latest version</Button></>}</div>}{notice && <p className="admin-success" role="status"><Check size={16}/>{notice}</p>}
    <div className="admin-editor-grid"><div className="admin-editor-canvas">{preview ? <article className="admin-story-preview"><div className="admin-eyebrow">Preview · not a publication</div><h2>{draft.title || 'Your story title'}</h2><p className="blog-deck">{draft.excerpt || 'Your short introduction will appear here.'}</p><p className="blog-byline">{saved?.authorName || session.user.name}</p>{draft.body ? <StoryBody body={draft.body}/> : <p className="admin-note">Your story will appear here as you write.</p>}</article> : <><Input label="Story title" placeholder="A clear, welcoming title" value={draft.title} maxLength={180} onChange={event => update('title', event.target.value)} disabled={!!pending}/><Textarea label="Short introduction" description="A sentence or two for the journal listing. Up to 500 characters." value={draft.excerpt} maxLength={500} rows={3} onChange={event => update('excerpt', event.target.value)} disabled={!!pending}/><Textarea className="admin-story-input" label="Story" description="Use Markdown: ## Heading, [source](https://example.org), or ![Describe the image](https://example.org/photo.jpg)." value={draft.body} maxLength={100000} rows={20} onChange={event => update('body', event.target.value)} disabled={!!pending}/><div className="admin-word-count">{words.toLocaleString('en-IN')} words · {draft.body.length.toLocaleString('en-IN')} / 100,000 characters</div></>}</div><aside className="admin-editor-settings"><section className="admin-panel"><h2>Story details</h2><Input label="URL name" value={draft.slug} maxLength={100} description="Lowercase letters, numbers and hyphens." onChange={event => { setSlugEdited(true); update('slug', event.target.value); }} disabled={!!pending}/><p className="admin-url-preview">/blog/{draft.slug || 'your-story'}</p><Input label="Topics" value={tags} maxLength={510} description="Separate tags with commas. Up to 12." onChange={event => { setTags(event.target.value); setNotice(''); setConfirm(null); }} disabled={!!pending}/></section><section className="admin-panel admin-publish-panel"><h2>Ready to share?</h2><p>{saved?.status === 'published' ? 'Saved edits stay private until you publish this version.' : 'Only your team can see this draft. Publishing makes it visible on the website.'}</p><Button disabled={!!pending} onClick={() => { const invalid = validatePost(actualDraft, true); if (invalid) setError(invalid); else { setError(''); setConfirm('publish'); } }}>{saved?.status === 'published' ? 'Publish changes' : 'Publish story'}<ArrowRight size={16}/></Button>{saved?.status === 'published' && <><Link className="admin-text-link" to={`/blog/${encodeURIComponent(saved.publishedSlug || saved.slug)}`} target="_blank" rel="noopener noreferrer">View live story <ExternalLink size={15}/></Link><Button size="sm" variant="ghost" disabled={!!pending} onClick={() => setConfirm('unpublish')}>Unpublish story</Button></>}{confirm && <div className="admin-confirm" role="region" aria-label="Confirm publication"><strong>{confirm === 'publish' ? 'Publish this version?' : 'Remove this story from the website?'}</strong><p>{confirm === 'publish' ? 'The title, introduction and story shown in Preview will be visible to everyone.' : 'The story will remain available to your team as a draft.'}</p><Button size="sm" disabled={!!pending} onClick={() => publish(confirm)}>{pending ? 'Working…' : confirm === 'publish' ? 'Yes, publish' : 'Yes, unpublish'}</Button><Button size="sm" variant="ghost" disabled={!!pending} onClick={() => setConfirm(null)}><X size={14}/>Cancel</Button></div>}</section></aside></div>
  </section>;
}
