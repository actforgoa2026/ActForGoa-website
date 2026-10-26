import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Button } from './components/arc/button/button';
import { Input } from './components/arc/input/input';
import { Textarea } from './components/arc/textarea/textarea';
import { categories, statuses, statusLabels, type ReportDraft } from '../shared/reporting';
import { reportApi } from './report-api';
import { useReportDraftGuard } from './use-report-draft-guard';
import './reporting.css';

type SavedReport = { id: string; data: ReportDraft; createdAt: string; status: typeof statuses[number]; note: string; updatedAt: string; photos: string[] };
function PrivatePhoto({ path, token, index }: { path: string; token: string; index: number }) {
  const [url, setUrl] = useState(''); const [error, setError] = useState(false);
  useEffect(() => {
    setUrl(''); setError(false);
    const controller = new AbortController(); let objectUrl = '';
    fetch(reportApi(path), { headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15000)]) }).then(async r => {
      if (!r.ok) throw new Error(); const blob = await r.blob();
      if (controller.signal.aborted) return;
      objectUrl = URL.createObjectURL(blob); setUrl(objectUrl);
    }).catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => { controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [path, token]);
  return url ? <a href={url} target="_blank" rel="noreferrer"><img className="report-private-photo" src={url} alt={`Submitted photo ${index + 1}. Open full size.`} /></a> : <p role="status">{error ? 'This photo couldn’t load. Close and reopen the report to retry.' : 'Loading photo…'}</p>;
}
function ReviewItem({ report, token, saved, dirtyChanged }: { dirtyChanged: (id: string, dirty: boolean, saving: boolean) => void; report: SavedReport; token: string; saved: (updated: SavedReport) => void }) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState(report.status); const [note, setNote] = useState(report.note);
  const [busy, setBusy] = useState(false); const [message, setMessage] = useState('');
  useEffect(() => { setStatus(report.status); setNote(report.note); }, [report.status, report.note, report.updatedAt]);
  const saveLock = useRef(false);
  useEffect(() => {
    dirtyChanged(report.id, status !== report.status || note !== report.note, busy);
    return () => dirtyChanged(report.id, false, false);
  }, [report.id, report.status, report.note, status, note, busy, dirtyChanged]);
  async function save(e: FormEvent) {
    e.preventDefault(); if (saveLock.current) return; saveLock.current = true; setBusy(true); setMessage('');
    try {
      const r = await fetch(reportApi(`/api/reports/${report.id}`), { method: 'PATCH', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ status, note, updatedAt: report.updatedAt }), signal: AbortSignal.timeout(10000) });
      const data = await r.json(); if (!r.ok) throw new Error(data.error);
      saved({ ...report, status, note, updatedAt: data.updatedAt }); setMessage('Review saved.');
    } catch (e) { setMessage(e instanceof Error ? e.message : 'Couldn’t save. Try again.'); } finally { saveLock.current = false; setBusy(false); }
  }
  return <details className="report-inbox-item" onToggle={e => setOpen(e.currentTarget.open)}><summary>{categories.find(c => c.id === report.data.category)?.label} · {report.data.location}<span>{statusLabels[report.status]} · Received {new Date(report.createdAt).toLocaleString()}</span></summary>
    {open && <div className="report-inbox-details"><dl className="report-summary"><div><dt>Reference</dt><dd>{report.id}</dd></div><div><dt>Observed</dt><dd>{new Date(report.data.observedAt).toLocaleString()}</dd></div><div><dt>What happened</dt><dd>{report.data.description}</dd></div><div><dt>Location</dt><dd>{report.data.location}{report.data.coordinates && <span className="report-coordinate-value">{report.data.coordinates.latitude}, {report.data.coordinates.longitude}{report.data.coordinates.accuracy !== undefined ? ` (±${Math.round(report.data.coordinates.accuracy)} m)` : ''}</span>}</dd></div><div><dt>Contact</dt><dd>{report.data.email || 'No contact details supplied'}</dd></div></dl>
      {report.photos.map((id, i) => <PrivatePhoto key={id} path={`/api/reports/${report.id}/photos/${id}`} token={token} index={i} />)}
      <form onSubmit={save}><fieldset className="report-review-form report-fields" disabled={busy}><label>Status<select value={status} onChange={e => { setStatus(e.target.value as SavedReport['status']); setMessage(''); }}>{statuses.map(s => <option key={s} value={s}>{statusLabels[s]}</option>)}</select></label><Textarea label="Private review note" maxLength={3000} value={note} onChange={e => { setNote(e.target.value); setMessage(''); }} description="Record what was checked and any follow-up. Status changes do not contact the reporter or an authority." /><Button type="submit" disabled={busy}>{busy ? 'Saving…' : 'Save review'}</Button>{message && <p role="status">{message}</p>}</fieldset></form>
    </div>}
  </details>;
}
export default function ReportInbox() {
  const [key, setKey] = useState(''); const [token, setToken] = useState('');
  const [reports, setReports] = useState<SavedReport[]>([]); const [cursor, setCursor] = useState<string | null>(null);
  const [refreshVersion, setRefreshVersion] = useState(0);
  const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const dirty = useRef(new Set<string>()); const saving = useRef(new Set<string>());
  const [reviewSaving, setReviewSaving] = useState(false);
  const dirtyChanged = useCallback((id: string, changed: boolean, busy: boolean) => {
    if (changed) dirty.current.add(id); else dirty.current.delete(id);
    if (busy) saving.current.add(id); else saving.current.delete(id);
    setReviewSaving(saving.current.size > 0);
  }, []);
  const guard = useReportDraftGuard(() => dirty.current.size > 0, reviewSaving);
  const loadLock = useRef(false);
  async function load(value: string, after: string | null = null) {
    if (loadLock.current) return; loadLock.current = true;
    setBusy(true); setError('');
    try {
      const r = await fetch(reportApi(`/api/reports/review${after ? `?cursor=${encodeURIComponent(after)}` : ''}`), { headers: { Authorization: `Bearer ${value}` }, signal: AbortSignal.timeout(10000) });
      const data = await r.json();
      if (!r.ok || !Array.isArray(data.reports)) throw new Error(data.error ?? 'The review inbox is unavailable.');
      if (!after) setRefreshVersion(v => v + 1);
      setToken(value); setKey(''); setReports(current => after ? [...current, ...data.reports.filter((r: SavedReport) => !current.some(c => c.id === r.id))] : data.reports); setCursor(data.nextCursor ?? null);
    } catch (e) { setError(e instanceof Error && e.name !== 'SyntaxError' ? e.message : 'The review inbox is unavailable. Check that the reporting service is running.'); }
    finally { loadLock.current = false; setBusy(false); }
  }
  return <main className="report-page shell"><header className="report-heading"><h1>Report inbox</h1><p>Private reports for review. Submissions describe suspected infractions and need checking.</p></header>
    {!token ? <form className="report-inbox-login" onSubmit={e => { e.preventDefault(); void load(key); }}><Input label="Review key" type="password" required value={key} autoComplete="off" onChange={e => setKey(e.target.value)} description="Use the review key provided by the site administrator. It stays in this tab’s memory until you leave or sign out." /><Button type="submit" disabled={busy}>{busy ? 'Opening…' : 'Open inbox'}</Button><Link className="text-link" to="/report">Make a report</Link></form> : <>
      <div className="report-inbox-toolbar"><p>{reports.length} report{reports.length === 1 ? '' : 's'} loaded</p><div><Button type="button" variant="ghost" disabled={busy || reviewSaving} onClick={() => guard.confirm(() => void load(token))}>Refresh</Button><Button type="button" variant="secondary" disabled={busy || reviewSaving} onClick={() => guard.confirm(() => { setToken(''); setReports([]); setCursor(null); setError(''); })}>Sign out</Button></div></div>
      {!reports.length && <p>No reports yet. New submissions will appear here.</p>}
      <div className="report-inbox-list">{reports.map(r => <ReviewItem key={`${refreshVersion}-${r.id}`} report={r} token={token} dirtyChanged={dirtyChanged} saved={updated => setReports(items => items.map(item => item.id === updated.id ? updated : item))} />)}</div>
      {cursor && <Button type="button" variant="secondary" disabled={busy} onClick={() => void load(token, cursor)}>{busy ? 'Loading…' : 'Load more reports'}</Button>}
    </>}{error && <p className="report-error" role="alert">{error}</p>}
    {guard.dialog}
  </main>;
}
