import { useEffect, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Download, ExternalLink, Mail, Phone, Upload } from 'lucide-react';
import { Button } from './components/arc/button/button';
import { SearchField } from './components/arc/search-field/search-field';
import { Input } from './components/arc/input/input';
import { Textarea } from './components/arc/textarea/textarea';
import SegmentedControl from './components/arc/segmented-control/segmented-control';
import { activityLabel, activityLabels, backupJSON, emptyNote, exportCSV, filterRecords, filtersFrom, isDue, mergeBackup, parseBackup, safeUrl, split, stages, storageKey, verification, verificationLabels, words, type CRMNote, type CRMRecord, type CRMSnapshot, type Stage, type Workspace } from './crm-model';
import './crm.css';

function download(name: string, text: string, type = 'application/json') {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = name; anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function readWorkspace(): Workspace { const raw = localStorage.getItem(storageKey); return raw ? parseBackup(raw) : {}; }
function Select({ label, value, onChange, options, all, disabled }: { label: string; value: string; onChange: (value: string) => void; options: Record<string, string>; all?: string; disabled?: boolean }) {
  return <label className="crm-select"><span>{label}</span><select value={value} onChange={e => onChange(e.target.value)} disabled={disabled}>
    {all && <option value="">{all}</option>}{Object.entries(options).map(([key, text]) => <option key={key} value={key}>{text}</option>)}
  </select></label>;
}
function External({ href, children }: { href: string; children: ReactNode }) {
  const url = safeUrl(href); return url ? <a href={url} target="_blank" rel="noopener noreferrer">{children}<ExternalLink size={14} aria-hidden="true" /></a> : null;
}
function Sources({ value }: { value: string }) {
  return <ul className="crm-sources">{Array.from(new Set(split(value))).filter(safeUrl).map((url, i) => <li key={url}><External href={url}>{i + 1}. {new URL(url).hostname.replace(/^www\./, '')}<span className="crm-source-path">{new URL(url).pathname.slice(0, 160)}</span></External></li>)}</ul>;
}
function Photo({ record }: { record: CRMRecord }) {
  const [failed, setFailed] = useState(false);
  return !failed && safeUrl(record.profile_photo_url) ? <figure className="crm-photo"><img src={safeUrl(record.profile_photo_url)} alt={`${record.name}: ${words(record.photo_kind)}`} referrerPolicy="no-referrer" onError={() => setFailed(true)} /><figcaption>{words(record.photo_kind)} · <External href={record.photo_source_url}>Source</External></figcaption></figure> : null;
}

export default function CRM() {
  const [data, setData] = useState<CRMSnapshot | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [workspace, setWorkspace] = useState<Workspace>({});
  const [storageError, setStorageError] = useState('');
  const [feedback, setFeedback] = useState('');
  const [pending, setPending] = useState<Workspace | null>(null);
  const [replace, setReplace] = useState(false);
  const [importError, setImportError] = useState('');
  const [params, setParams] = useSearchParams();
  const { recordId } = useParams();
  useEffect(() => setFeedback(''), [recordId]);
  const chooser = useRef<HTMLInputElement>(null);
  const resultStart = useRef<HTMLParagraphElement>(null);
  const focusNextPage = useRef(false);
  const filters = filtersFrom(params);
  useEffect(() => {
    const controller = new AbortController(); setLoadError(false);
    fetch('/data/crm.json', { signal: controller.signal }).then(r => { if (!r.ok) throw Error(); return r.json(); }).then(value => {
      if (!Array.isArray(value.records) || !Array.isArray(value.opportunities) || !value.version) throw Error();
      setData(value);
    }).catch(e => { if (e.name !== 'AbortError') setLoadError(true); });
    return () => controller.abort();
  }, [retry]);
  useEffect(() => {
    const load = () => { try { setWorkspace(readWorkspace()); setStorageError(''); } catch { setStorageError('Browser notes could not be read. Export the stored backup before restoring a valid backup. Your stored data has not been changed.'); } };
    load(); const sync = (event: StorageEvent) => { if (event.key === storageKey || event.key === null) load(); };
    window.addEventListener('storage', sync); return () => window.removeEventListener('storage', sync);
  }, []);
  const opportunityIds = useMemo(() => new Set(data?.opportunities.flatMap(r => split(r.related_record_ids)) || []), [data]);
  const byId = useMemo(() => new Map(data?.records.map(r => [r.record_id, r]) || []), [data]);
  const results = useMemo(() => filterRecords(data?.records || [], opportunityIds, filters, workspace), [data, opportunityIds, params, workspace]);
  const selected = recordId ? byId.get(recordId) : undefined;
  const page = Math.min(Math.max(1, Math.floor(Number(params.get('page'))) || 1), Math.max(1, Math.ceil(results.length / 25)));
  useLayoutEffect(() => {
    if (!focusNextPage.current) return;
    focusNextPage.current = false;
    resultStart.current?.focus({ preventScroll: true });
    resultStart.current?.scrollIntoView({ block: 'start', behavior: 'instant' });
  }, [page]);
  const shown = results.slice((page - 1) * 25, page * 25);
  const types = useMemo(() => Object.fromEntries([...new Set(data?.records.map(r => r.record_type))].sort().map(s => [s, words(s)])), [data]);
  const topics = useMemo(() => Object.fromEntries([...new Set(data?.records.flatMap(r => split(r.focus_areas)))].filter(t => !t.endsWith('_lead')).sort().map(s => [s, words(s)])), [data]);
  const query = params.toString() ? '?' + params.toString() : '';
  const recordLink = (id: string) => '/directory/' + encodeURIComponent(id) + query;
  function change(key: string, value: string, replaceHistory = false) {
    const next = new URLSearchParams(params); value ? next.set(key, value) : next.delete(key);
    if (key === 'page') focusNextPage.current = true;
    if (key !== 'page') next.delete('page'); setParams(next, { replace: replaceHistory, preventScrollReset: true });
  }
  function save(id: string, update: Partial<CRMNote>) {
    setFeedback('');
    try {
      const current = readWorkspace();
      const note = { ...(current[id] || emptyNote(byId.get(id)!)), ...update, updatedAt: new Date().toISOString() };
      if (byId.get(id)?.activity_status === 'deceased_historical_record') { note.stage = 'do_not_contact'; note.followUp = ''; }
      const next = { ...current, [id]: note }; localStorage.setItem(storageKey, backupJSON(next));
      setWorkspace(next); setStorageError(''); setFeedback('Saved in this browser.');
    } catch { setStorageError('Could not save in this browser. Check storage permissions or available space. Your last saved notes are unchanged.'); }
  }
  function exportBackup() {
    try { download('actforgoa-crm-backup.json', localStorage.getItem(storageKey) || backupJSON(workspace)); setFeedback('Backup downloaded. Keep it to restore notes on another browser.'); }
    catch { setStorageError('Browser storage is unavailable. No backup was exported.'); }
  }
  async function importFile(file?: File) {
    setImportError(''); setPending(null); setReplace(false);
    if (!file) return;
    try { if (file.size > 10_000_000) throw Error('Choose a backup smaller than 10 MB.'); const incoming = parseBackup(await file.text()); setPending(incoming); }
    catch (e) { setImportError(e instanceof Error ? e.message : 'This backup could not be read.'); }
  }
  function applyImport() {
    if (!pending) return;
    try {
      let current: Workspace;
      try { current = readWorkspace(); } catch { if (!replace) throw Error('Export the stored backup, then select Replace matching notes to restore this backup.'); current = {}; }
      const merged = mergeBackup(current, pending, replace);
      // Historical records never become outreach prospects through an import.
      for (const r of data?.records || []) if (r.activity_status === 'deceased_historical_record' && merged[r.record_id]) merged[r.record_id] = { ...merged[r.record_id], stage: 'do_not_contact', followUp: '' };
      localStorage.setItem(storageKey, backupJSON(merged)); setWorkspace(merged); setPending(null); setStorageError(''); setFeedback('Backup imported. Notes are saved in this browser.');
    } catch (e) { setImportError(e instanceof Error ? e.message : 'Could not save the imported backup.'); }
  }
  return <main className="crm shell">
    <header className="crm-heading"><div><h1>Goa community CRM</h1><p>Find the people, organisations and public offices working across Goa.</p></div>
      <div className="crm-actions"><Button variant="secondary" onClick={exportBackup}><Download size={16} aria-hidden="true" />Export backup</Button><Button variant="secondary" onClick={() => chooser.current?.click()}><Upload size={16} aria-hidden="true" />Import backup</Button><input className="crm-file" type="file" accept=".json,application/json" ref={chooser} aria-label="Import CRM backup file" onChange={e => { void importFile(e.target.files?.[0]); e.target.value = ''; }} /></div>
    </header>
    <p className="crm-context">Notes stay in this browser. Export a backup to move or keep them. Research snapshot: 22–23 October 2026.</p>
    {storageError && <p className="crm-notice" role="alert">{storageError}</p>}
    <p className={feedback ? 'crm-feedback' : 'crm-feedback-empty'} role="status">{feedback}</p>
    {importError && <p role="alert" className="crm-notice">{importError}</p>}
    {pending && <section className="crm-import" aria-label="Review backup import"><h2>Review backup</h2><p>{Object.keys(pending).length} saved records. {Object.keys(pending).filter(id => workspace[id]).length} already have notes in this browser. Existing notes are kept by default. Records outside this snapshot remain in the backup.</p><label><input type="checkbox" checked={replace} onChange={e => setReplace(e.target.checked)} />Replace matching notes with the imported version</label><div className="crm-actions"><Button onClick={applyImport}>Import notes</Button><Button variant="ghost" onClick={() => setPending(null)}>Cancel</Button></div></section>}
    {loadError ? <section className="crm-empty"><h2>The directory couldn’t load.</h2><p>Your browser notes are still stored separately.</p><Button onClick={() => setRetry(retry + 1)}>Try again</Button></section> : !data ? <p role="status" className="crm-empty">Loading the research directory…</p> : recordId ? <>
      <Link className="crm-back" to={'/directory' + query}><ArrowLeft size={17} aria-hidden="true" />Back to results</Link>
      {selected ? <RecordDetail key={selected.record_id} record={selected} note={workspace[selected.record_id] || emptyNote(selected)} save={save} byId={byId} recordLink={recordLink} opportunities={data.opportunities.filter(o => split(o.related_record_ids).includes(selected.record_id))} /> : <section className="crm-empty"><h2>Record not found</h2><p>This record isn’t in the current research snapshot. Return to the directory to search again.</p></section>}
    </> : <>
      <div className="crm-search"><SearchField label="Search CRM" placeholder="Search names, work, villages or contacts" value={filters.q} onValueChange={value => change('q', value, true)} /></div>
      <SegmentedControl label="Directory collection" value={filters.collection} onValueChange={value => { const next = new URLSearchParams(); if (filters.q) next.set('q', filters.q); next.set('collection', value); setParams(next, { preventScrollReset: true }); }} options={[{ value: 'community', label: 'Community', accessory: <span className="crm-count">{data.records.filter(r => r.collection === 'community').length.toLocaleString('en-IN')}</span> }, { value: 'government', label: 'Government', accessory: <span className="crm-count">{data.records.filter(r => r.collection === 'government').length.toLocaleString('en-IN')}</span> }, { value: 'opportunities', label: 'Participation', accessory: <span className="crm-count">{opportunityIds.size}</span> }, { value: 'all', label: 'All records', accessory: <span className="crm-count">{data.records.length.toLocaleString('en-IN')}</span> }]} />
      {filters.collection === 'opportunities' && <p className="crm-context">Participation routes include enquiries, courses and past intakes. Check each record’s dates and availability.</p>}
      <details className="crm-filters"><summary>Filters{Object.entries(filters).filter(([k,v]) => !['q','collection','sort'].includes(k) && v).length > 0 ? ' · Active' : ''}</summary><div className="crm-filter-grid">
        <Select label="Record type" value={filters.type} onChange={v => change('type', v)} options={types} all="All types" />
        <Select label="Focus area" value={filters.focus} onChange={v => change('focus', v)} options={topics} all="All focus areas" />
        <Input label="Village or area" value={filters.location} placeholder="e.g. Canacona" onInput={e => change('location', e.currentTarget.value, true)} />
        <Select label="Activity evidence" value={filters.activity} onChange={v => change('activity', v)} options={activityLabels} all="Any activity status" />
        <Select label="Source verification" value={filters.verification} onChange={v => change('verification', v)} options={verificationLabels} all="Any verification status" />
        <Select label="Contact availability" value={filters.contact} onChange={v => change('contact', v)} options={{ phone: 'Has a phone', email: 'Has an email', missing: 'No phone or email' }} all="Any contact availability" />
        <Select label="Outreach stage" value={filters.stage} onChange={v => change('stage', v)} options={stages} all="All stages" />
        <label className="crm-checkbox"><input type="checkbox" checked={filters.due} onChange={e => change('due', e.target.checked ? '1' : '')} />Follow-up due (Goa time)</label>
      </div><Button variant="ghost" onClick={() => setParams(filters.collection === 'community' ? {} : { collection: filters.collection }, { preventScrollReset: true })}>Clear search and filters</Button></details>
      <div className="crm-result-tools"><p ref={resultStart} tabIndex={-1} className="crm-result-start" role="status"><strong>{results.length.toLocaleString('en-IN')} records</strong>{results.length > 0 && <span> · Showing {(page - 1) * 25 + 1}–{Math.min(page * 25, results.length)}</span>}</p><div className="crm-actions"><Select label="Sort by" value={filters.sort} onChange={v => change('sort', v)} options={{ name: 'Name', activity: 'Latest evidence date', followup: 'Follow-up date' }} /><Button variant="ghost" disabled={!results.length} onClick={() => download('actforgoa-filtered-contacts.csv', exportCSV(results, workspace), 'text/csv;charset=utf-8')}>Export results</Button></div></div>
      {shown.length ? <table className="crm-table"><thead><tr><th>People & organisations</th><th>Activity & verification</th><th>Public contact</th><th>Your next step</th></tr></thead><tbody>{shown.map(r => {
        const note = workspace[r.record_id] || emptyNote(r);
        return <tr key={r.record_id}><td><span className="crm-meta">{words(r.record_type)}{r.goa_location && ' · ' + r.goa_location}</span><Link className="crm-name" to={recordLink(r.record_id)}>{r.name}<ArrowRight size={18} aria-hidden="true" /></Link><p className="crm-summary">{r.summary}</p></td>
          <td><span className="crm-mobile-label">Activity & verification</span><strong>{activityLabel(r)}</strong>{r.activity_evidence_date && <span className="crm-meta">Evidence: {r.activity_evidence_date}</span>}<span className="crm-verification">{verificationLabels[verification(r)]}</span></td>
          <td><span className="crm-mobile-label">Public contact</span>{r.activity_status === 'deceased_historical_record' ? <span>Historical record</span> : <><span>{r.public_phone ? 'Phone listed' : 'No phone listed'}</span><span>{r.public_email ? 'Email listed' : 'No email listed'}</span></>}<span className="crm-meta">{r.public_phone || r.public_email ? 'Contact delivery untested' : 'See referral routes'}</span></td>
          <td><span className="crm-mobile-label">Your next step</span><span>{stages[note.stage]}</span>{note.followUp && <span className={isDue(note) ? 'crm-due' : 'crm-meta'}>{isDue(note) ? 'Due' : 'Follow up'} {note.followUp}</span>}</td></tr>;
      })}</tbody></table> : <section className="crm-empty"><h2>No matching records</h2><p>Try a different name or village, or clear your filters.</p><Button variant="secondary" onClick={() => setParams({})}>Reset directory</Button></section>}
      <nav className="crm-pagination" aria-label="CRM result pages"><Button variant="secondary" disabled={page <= 1} onClick={() => change('page', String(page - 1))}>Previous</Button><span>Page {page} of {Math.max(1, Math.ceil(results.length / 25))}</span><Button variant="secondary" disabled={page * 25 >= results.length} onClick={() => change('page', String(page + 1))}>Next</Button></nav>
      <p className="crm-context">A listing is not proof of current service or willingness to collaborate. <Link to="/directory/archive">Browse the original site directory</Link>.</p>
    </>}
  </main>;
}

function RecordDetail({ record: r, note, save, byId, recordLink, opportunities }: { record: CRMRecord; note: CRMNote; save: (id: string, update: Partial<CRMNote>) => void; byId: Map<string, CRMRecord>; recordLink: (id: string) => string; opportunities: CRMRecord[] }) {
  const deceased = r.activity_status === 'deceased_historical_record';
  const socialFields = { instagram_url: 'Instagram', facebook_url: 'Facebook', linkedin_url: 'LinkedIn', x_url: 'X', youtube_url: 'YouTube' };
  return <article className="crm-detail"><div className="crm-record-main">
    <header><span className="crm-meta">{words(r.record_type)} · {r.goa_location || r.jurisdiction || 'Goa'}</span><h2>{r.name}</h2>{(r.role || r.organization) && <p className="crm-affiliation">{[r.role, r.organization].filter(Boolean).join(' · ')}</p>}<p className="crm-description">{r.summary}</p><p className="crm-topics">{split(r.focus_areas).filter(t => !t.endsWith('_lead')).map(words).join(' · ')}</p></header>
    <section className="crm-evidence"><h3>Activity & verification</h3><dl><div><dt>Activity</dt><dd>{activityLabel(r)}{r.activity_evidence_date && <span> · Evidence dated {r.activity_evidence_date}</span>}</dd></div><div><dt>Source review</dt><dd>{verificationLabels[verification(r)]}</dd></div><div><dt>Research checked</dt><dd>{r.checked_on || 'Not recorded'}</dd></div><div><dt>Contact verification</dt><dd>{r.public_phone || r.public_email ? 'Publicly listed. Phone and email delivery have not been tested.' : 'No direct public phone or email established.'}</dd></div></dl><p>{r.activity_verification_notes || 'Recent environmental activity was not assessed for this government record. An official listing does not independently confirm current tenure.'}</p>{r.activity_evidence_url && <External href={r.activity_evidence_url}>Read activity evidence</External>}
      <details><summary>Full verification notes</summary><p>{r.verification_status.split(';').map(words).join('. ')}.</p>{r.notes && <p>{r.notes}</p>}<p>Record ID: {r.record_id}</p></details>
    </section>
    <section className="crm-contacts"><h3>Public contact details</h3>{deceased ? <p>This is a historical record of a deceased contributor. It is excluded from outreach.</p> : <><p className="crm-context">{words(r.contact_kind) || 'No direct route verified'}. Shared office and referral routes may serve multiple people.</p><div className="crm-contact-links">{split(r.public_phone).filter(p => /^\+\d+$/.test(p)).map(phone => <a key={phone} href={'tel:' + phone}><Phone size={17} aria-hidden="true" />{phone}</a>)}{split(r.public_email).filter(e => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e)).map(email => <a key={email} href={'mailto:' + email}><Mail size={17} aria-hidden="true" />{email}</a>)}{!r.public_phone && !r.public_email && <p>No public phone or email was verified.</p>}<External href={r.website_url}>Website or reference page</External>{Object.entries(socialFields).map(([field, label]) => <External key={field} href={r[field]}>{label}</External>)}</div>{r.referral_route && <p className="crm-description">{r.referral_route}</p>}</>}
      {r.contact_source_urls && <details><summary>Sources for these contacts</summary><Sources value={r.contact_source_urls} /></details>}
    </section>
    {(opportunities.length > 0 || r.how_to_help || r.volunteer_url) && <section><h3>Ways to get involved</h3><p>{words(r.volunteer_status).replaceAll(';', '.')}</p>{r.how_to_help && <p>{r.how_to_help}</p>}<External href={r.volunteer_url}>Participation details</External><p className="crm-context">Confirm current dates, eligibility and availability with the organiser. A listed route may have a closed intake.</p></section>}
    {split(r.related_record_ids).some(id => byId.has(id)) && <section><h3>Related people & organisations</h3><ul className="crm-related">{split(r.related_record_ids).filter(id => byId.has(id)).map(id => <li key={id}><Link to={recordLink(id)}>{byId.get(id)!.name}<ArrowRight size={16} aria-hidden="true" /></Link></li>)}</ul></section>}
    <section><h3>Research sources</h3><Sources value={r.source_urls} /><Photo record={r} />{r.profile_photo_url && <p className="crm-context">Image reuse permission has not been established.</p>}</section>
  </div><aside className="crm-workspace" aria-label="Relationship notes"><h3>Your relationship</h3><p className="crm-context">Saved on this browser. These notes do not change the research or its verification status.</p>
    <Select label="Outreach stage" value={note.stage} disabled={deceased} onChange={stage => save(r.record_id, { stage: stage as Stage })} options={stages} />
    <Input label="Last contact" type="date" value={note.lastContact} disabled={deceased} onInput={e => save(r.record_id, { lastContact: e.currentTarget.value })} />
    <Input label="Follow-up date" type="date" value={note.followUp} disabled={deceased || ['closed','do_not_contact'].includes(note.stage)} onInput={e => save(r.record_id, { followUp: e.currentTarget.value })} />
    {isDue(note) && <p className="crm-due">Follow-up due {note.followUp}</p>}
    <Textarea label="Notes" placeholder="Context, conversations and next steps" value={note.notes} maxLength={50000} rows={7} onChange={e => save(r.record_id, { notes: e.target.value })} />
    {note.updatedAt && <p className="crm-context">Last saved {new Date(note.updatedAt).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} (Goa time).</p>}
  </aside></article>;
}
