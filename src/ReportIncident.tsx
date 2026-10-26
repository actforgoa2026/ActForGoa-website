import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Check, LocateFixed, MapPin, Upload, X } from 'lucide-react';
import { Button } from './components/arc/button/button';
import { Input } from './components/arc/input/input';
import { Textarea } from './components/arc/textarea/textarea';
import { categories, emptyDraft, MAX_PHOTOS, MAX_PHOTO_BYTES, validateReport, type ReportDraft } from '../shared/reporting';
import { reportApi } from './report-api';
import { createSubmissionIdentity } from '../shared/submission-identity';
import { useReportDraftGuard } from './use-report-draft-guard';
import './reporting.css';

type Photo = { file: File; url: string };
type Receipt = { id: string; createdAt: string };
const localTime = () => { const d = new Date(); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16); };
export default function ReportIncident() {
  const [draft, setDraft] = useState<ReportDraft>({ ...emptyDraft });
  const [when, setWhen] = useState(localTime);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [viewPhoto, setViewPhoto] = useState<Photo | null>(null);
  const photoDialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { if (viewPhoto) photoDialog.current?.showModal(); else photoDialog.current?.close(); }, [viewPhoto]);
  const photosRef = useRef(photos); photosRef.current = photos;
  const [step, setStep] = useState(0);
  const [error, setError] = useState('');
  const [photoError, setPhotoError] = useState('');
  const [addingPhotos, setAddingPhotos] = useState(false);
  const photoLock = useRef(false);
  const mounted = useRef(true);
  const [locating, setLocating] = useState(false);
  const [locationMessage, setLocationMessage] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [coordinatesOpen, setCoordinatesOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [receipt, setReceipt] = useState<Receipt | null>(null);
  const [service, setService] = useState<'checking' | 'local' | 'ready' | 'offline'>('checking');
  const submissionIdentity = useRef(createSubmissionIdentity());
  const changed = useRef(false);
  const submitLock = useRef(false);
  const guard = useReportDraftGuard(() => changed.current && !receipt, busy);
  const heading = useRef<HTMLHeadingElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const [website, setWebsite] = useState('');
  const update = <K extends keyof ReportDraft>(key: K, value: ReportDraft[K]) => { changed.current = true; setDraft(d => ({ ...d, [key]: value })); setError(''); };
  function checkService() {
    setService('checking');
    fetch(reportApi('/api/reports/config'), { signal: AbortSignal.timeout(8000) }).then(async r => {
      if (!r.ok) throw new Error(); const data = await r.json();
      if (data.available !== true) throw new Error(); setService(data.local ? 'local' : 'ready');
    }).catch(() => setService('offline'));
  }
  useEffect(() => { mounted.current = true; checkService(); return () => { mounted.current = false; photosRef.current.forEach(p => URL.revokeObjectURL(p.url)); }; }, []);
  useEffect(() => { if (step || receipt) heading.current?.focus(); }, [step, receipt]);
  function go(next: number) { setError(''); setStep(next); heading.current?.scrollIntoView({ block: 'start' }); }
  async function addPhotos(files: FileList | null) {
    if (!files || photoLock.current) return;
    setPhotoError('');
    if (files.length + photosRef.current.length > MAX_PHOTOS) { setPhotoError('You can add up to 3 photos. Remove one before adding another.'); return; }
    photoLock.current = true; setAddingPhotos(true);
    const accepted: Photo[] = [];
    for (const file of Array.from(files)) {
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || !file.size || file.size > MAX_PHOTO_BYTES) {
        setPhotoError('Use JPG, PNG or WebP photos under 8 MB each. On an iPhone, export HEIC photos as JPG first.'); continue;
      }
      const url = URL.createObjectURL(file);
      try {
        const img = new Image(); img.src = url; await img.decode();
        if (img.naturalWidth * img.naturalHeight > 40000000) throw new Error();
        accepted.push({ file, url });
      } catch { URL.revokeObjectURL(url); setPhotoError('One photo could not be opened or is too large. Choose a different photo.'); }
    }
    photoLock.current = false; setAddingPhotos(false);
    if (!mounted.current) { accepted.forEach(p => URL.revokeObjectURL(p.url)); return; }
    changed.current = true;
    setPhotos(current => { const merged = [...current, ...accepted]; const excess = merged.splice(MAX_PHOTOS); excess.forEach(p => URL.revokeObjectURL(p.url)); return merged; });
  }
  function removePhoto(index: number) { setPhotos(current => { URL.revokeObjectURL(current[index].url); return current.filter((_, i) => i !== index); }); changed.current = true; }
  function locate() {
    if (!navigator.geolocation) { setLocationMessage('Location is not available in this browser. Enter the place below.'); return; }
    setLocating(true); setLocationMessage('');
    navigator.geolocation.getCurrentPosition(position => {
      const { latitude: lat, longitude: lng, accuracy } = position.coords;
      setLatitude(lat.toFixed(6)); setLongitude(lng.toFixed(6));
      update('coordinates', { latitude: lat, longitude: lng, accuracy }); setCoordinatesOpen(true);
      setLocationMessage(`Location added, accurate to about ${Math.round(accuracy)} metres. Check that it is where the incident happened.`); setLocating(false);
    }, () => { setLocationMessage('Couldn’t get your location. You can still enter the place or coordinates below.'); setLocating(false); }, { timeout: 10000, maximumAge: 0, enableHighAccuracy: true });
  }
  function next(e: FormEvent<HTMLFormElement>) {
    e.preventDefault(); setError('');
    if (step === 0) {
      if (!draft.category || draft.description.trim().length < 10) { setError('Choose a category and describe what you saw in at least 10 characters.'); return; }
      if (!when || !Number.isFinite(Date.parse(when)) || Date.parse(when) > Date.now() + 60000) { setError('Choose a valid time in the past.'); return; }
      update('observedAt', new Date(when).toISOString()); go(1);
    } else if (step === 1) {
      let coordinates = null;
      if (latitude || longitude) {
        const lat = Number(latitude), lng = Number(longitude);
        if (!latitude.trim() || !longitude.trim() || !Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) { setError('Enter both valid latitude and longitude values, or clear both.'); return; }
        coordinates = { latitude: lat, longitude: lng, ...(draft.coordinates?.accuracy === undefined ? {} : { accuracy: draft.coordinates.accuracy }) };
      }
      if (!when || !Number.isFinite(Date.parse(when)) || Date.parse(when) > Date.now() + 60000) { setError('Choose a valid time in the past.'); return; }
      const observedAt = new Date(when).toISOString();
      const candidate = { ...draft, coordinates, observedAt, consent: true };
      try { validateReport(candidate); } catch (e) { setError((e as Error).message); return; }
      update('coordinates', coordinates); update('observedAt', observedAt); go(2);
    } else void send();
  }
  async function send() {
    if (submitLock.current) return;
    try { validateReport(draft); } catch (e) { setError((e as Error).message); return; }
    submitLock.current = true; setBusy(true); setError('');
    const form = new FormData(); form.set('report', JSON.stringify(draft)); form.set('website', website);
    photos.forEach(p => form.append('photos', p.file));
    try {
      const response = await fetch(reportApi('/api/reports'), { method: 'POST', headers: { 'Idempotency-Key': submissionIdentity.current(JSON.stringify([draft, photos.map(p => p.url)])) }, body: form, signal: AbortSignal.timeout(60000) });
      const result = await response.json().catch(() => null);
      if (!response.ok || typeof result?.id !== 'string' || typeof result?.createdAt !== 'string') throw new Error(result?.error ?? 'The report could not be saved. Your details are still here; please try again.');
      setReceipt(result); changed.current = false;
      photos.forEach(p => URL.revokeObjectURL(p.url)); setPhotos([]); setDraft({ ...emptyDraft });
    } catch (e) { setError(e instanceof Error && e.name !== 'TypeError' && e.name !== 'TimeoutError' ? e.message : 'We couldn’t confirm your submission. Your details are still here. Try again; a retry won’t create a duplicate.'); }
    finally { submitLock.current = false; setBusy(false); }
  }
  function downloadReceipt() {
    if (!receipt) return;
    const url = URL.createObjectURL(new Blob([`ActForGoa report receipt\nReference: ${receipt.id}\nReceived: ${receipt.createdAt}\nStatus: Awaiting review\n${service === 'local' ? 'Local preview only. Saved on this computer.' : 'Saved to the private ActForGoa inbox.'}\nThis is not an official complaint acknowledgement.\n`], { type: 'text/plain' }));
    const a = document.createElement('a'); a.href = url; a.download = `${receipt.id}.txt`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return <main className="report-page shell">
    <header className="report-heading"><h1 ref={heading} tabIndex={-1}>{receipt ? 'Your report is saved.' : 'Report an infraction'}</h1>
      <p>{receipt ? 'Keep your reference number for any follow-up.' : 'Seen something that could harm Goa? Record what happened and where.'}</p>
      {!receipt && <p className="report-privacy">Reports go to the private ActForGoa review inbox.</p>}
    </header>
    {receipt ? <section className="report-receipt" aria-label="Report receipt">
      <Check size={30} aria-hidden="true" /><h2>Awaiting review</h2>
      <p className="report-reference">{receipt.id}</p>
      <p>{service === 'local' ? 'This is a local preview. Your report is saved on this computer, not sent to a live team.' : 'Your report is in the private ActForGoa inbox.'} This is not an official complaint acknowledgement.</p>
      <div className="report-actions"><Button type="button" onClick={downloadReceipt}>Download receipt</Button><Button type="button" variant="secondary" onClick={() => { setReceipt(null); setStep(0); setWhen(localTime()); setLatitude(''); setLongitude(''); setCoordinatesOpen(false); setLocationMessage(''); setPhotoError(''); }}>Report another incident</Button></div>
      <Link className="text-link" to="/read/guide-reporting">Read the guide to official complaints <ArrowRight size={16} /></Link>
    </section> : <div className="report-layout"><div>
      <ol className="report-steps" aria-label="Report progress">{['What happened', 'Where & when', 'Review & send'].map((label, i) => <li key={label} aria-current={step === i ? 'step' : undefined}><span>{i < step ? <Check size={15} aria-hidden="true" /> : i + 1}</span>{label}</li>)}</ol>
      {service === 'local' && <p className="report-service" role="status">Local preview. Reports are saved on this computer for testing.</p>}
      {service === 'offline' && <div className="report-service" role="status"><p>Reporting is temporarily unavailable. You can prepare your details here, but they cannot be sent yet.</p><Button type="button" size="sm" variant="ghost" onClick={checkService}>Check again</Button></div>}
      <form onSubmit={next}><fieldset className="report-form report-fields" disabled={busy} aria-busy={busy}>
        <div className="report-honeypot" aria-hidden="true"><label>Website<input tabIndex={-1} autoComplete="off" value={website} onChange={e => setWebsite(e.target.value)} /></label></div>
        {step === 0 && <>
          <fieldset className="report-categories"><legend>What did you see?</legend><p className="report-help">Choose the closest category. A report records a concern, not a confirmed violation.</p>
            {categories.map(c => <button key={c.id} type="button" className="report-category" aria-pressed={draft.category === c.id} onClick={() => update('category', c.id)}><span><strong>{c.label}</strong><span>{c.description}</span></span>{draft.category === c.id && <Check size={24} aria-hidden="true" />}</button>)}
          </fieldset>
          <Textarea label="What happened?" required minLength={10} maxLength={3000} rows={4} value={draft.description} onChange={e => update('description', e.target.value)} placeholder="Describe what you saw, how much, and whether it is still happening." description="Stick to what you observed. Avoid names or identifying people unnecessarily." />
          <section className="report-upload" aria-labelledby="photo-label"><h2 id="photo-label">Photos <span>(optional)</span></h2><p className="report-help">Up to 3 photos. JPG, PNG or WebP, 8 MB each.</p>
            <input ref={fileInput} id="report-photos" className="report-file-input" type="file" accept="image/jpeg,image/png,image/webp" multiple aria-label="Add photos" onChange={e => { void addPhotos(e.target.files); e.target.value = ''; }} />
            <div className="report-photo-grid">{photos.map((p, i) => <figure key={p.url}><button type="button" className="report-photo-button" onClick={() => setViewPhoto(p)} aria-label={`View selected photo ${i + 1} at full size`}><img src={p.url} alt={`Selected photo ${i + 1}`} /><span className="report-photo-open">View full photo</span></button><figcaption><span>{p.file.name}</span><Button type="button" size="sm" variant="ghost" aria-label={`Remove photo ${i + 1}`} onClick={() => removePhoto(i)}><X size={18} /></Button></figcaption></figure>)}</div>
            <Button type="button" variant="secondary" disabled={addingPhotos || photos.length >= MAX_PHOTOS} onClick={() => fileInput.current?.click()}><Upload size={18} aria-hidden="true" />{addingPhotos ? 'Preparing photos…' : photos.length ? 'Add another photo' : 'Add photos'}</Button>
            {photoError && <p className="report-error" role="alert">{photoError}</p>}
            <p className="report-help">Photograph only from a safe place. Photos are resized and embedded metadata is removed; keep the originals for an official complaint.</p>
          </section>
        </>}
        {step === 1 && <>
          <h2>Place the incident</h2>
          <Input label="Place or nearby landmark" required minLength={3} maxLength={500} value={draft.location} onChange={e => update('location', e.target.value)} placeholder="Village or town, road and a nearby landmark" description="Describe the incident location, even if you also add coordinates." />
          <div className="report-location-actions"><Button type="button" variant="secondary" disabled={locating} onClick={locate}><LocateFixed size={18} />{locating ? 'Finding location…' : 'Use my current location'}</Button><Button type="button" variant="ghost" onClick={() => setCoordinatesOpen(!coordinatesOpen)} aria-expanded={coordinatesOpen}>Enter coordinates</Button></div>
          {locationMessage && <p className="report-help" role="status">{locationMessage}</p>}
          {coordinatesOpen && <div className="report-coordinate-fields"><Input label="Latitude" inputMode="decimal" value={latitude} onChange={e => { setLatitude(e.target.value); update('coordinates', null); }} placeholder="e.g. 15.4909" /><Input label="Longitude" inputMode="decimal" value={longitude} onChange={e => { setLongitude(e.target.value); update('coordinates', null); }} placeholder="e.g. 73.8278" /><Button type="button" variant="ghost" onClick={() => { setLatitude(''); setLongitude(''); update('coordinates', null); setLocationMessage(''); }}>Clear coordinates</Button></div>}
          <Input label="When did you see it?" type="datetime-local" required max={localTime()} value={when} onChange={e => { setWhen(e.target.value); changed.current = true; }} description="Use the local time on your device." />
          <Input label="Your email (optional)" type="email" autoComplete="email" maxLength={254} value={draft.email} onChange={e => update('email', e.target.value)} description="Leave this blank to report without contact details. An email lets a reviewer follow up." />
        </>}
        {step === 2 && <>
          <div className="report-section-title"><h2>Check your report</h2><Button type="button" variant="ghost" onClick={() => go(0)}>Edit details</Button></div>
          <dl className="report-summary"><div><dt>Category</dt><dd>{categories.find(c => c.id === draft.category)?.label}</dd></div><div><dt>What happened</dt><dd>{draft.description}</dd></div><div><dt>Location</dt><dd>{draft.location}{draft.coordinates && <span className="report-coordinate-value"><MapPin size={16} />{draft.coordinates.latitude.toFixed(6)}, {draft.coordinates.longitude.toFixed(6)}{draft.coordinates.accuracy !== undefined ? ` (±${Math.round(draft.coordinates.accuracy)} m)` : ''}</span>}</dd></div><div><dt>Observed</dt><dd>{new Date(draft.observedAt).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}</dd></div><div><dt>Contact</dt><dd>{draft.email || 'No contact details provided'}</dd></div></dl>
          {photos.length > 0 ? <div className="report-photo-grid">{photos.map((p, i) => <button key={p.url} type="button" className="report-photo-button" onClick={() => setViewPhoto(p)} aria-label={`View report photo ${i + 1} at full size`}><img src={p.url} alt={`Report photo ${i + 1}`} /><span className="report-photo-open">View full photo {i + 1}</span></button>)}</div> : <p className="report-help">No photos attached.</p>}
          <label className="report-consent"><input type="checkbox" required checked={draft.consent} onChange={e => update('consent', e.target.checked)} /><span>I want to send these details and photos to the private ActForGoa review inbox. They describe what I observed to the best of my knowledge.</span></label>
        </>}
        {error && <p className="report-error" role="alert">{error}</p>}
        <div className="report-actions">{step > 0 && <Button type="button" variant="ghost" disabled={busy} onClick={() => go(step - 1)}><ArrowLeft size={17} />Back</Button>}<Button type="submit" disabled={busy || addingPhotos || (step === 2 && service !== 'ready' && service !== 'local')}>{busy ? 'Saving report…' : step === 2 ? 'Send report' : step === 1 ? 'Review report' : 'Continue'}{!busy && <ArrowRight size={17} />}</Button><span className="report-help">{step === 2 ? 'Your report stays private.' : `${step + 1} of 3`}</span></div>
      </fieldset></form>
    </div><aside className="report-aside"><h2>A useful record starts with what you saw.</h2><p>Add the location, time and any photos you can safely take. You don’t need to know which law may apply.</p><h3>What happens next</h3><p>Your report goes into a private review inbox. It is not published or automatically sent to an authority.</p><h3>Immediate danger?</h3><p>This inbox is not an emergency service.</p><Link className="text-link" to="/emergency">Find emergency help <ArrowRight size={16} /></Link><Link className="text-link" to="/read/guide-reporting">How to make an official complaint <ArrowRight size={16} /></Link></aside></div>}
    {guard.dialog}
    <dialog ref={photoDialog} className="report-photo-dialog" aria-label="Full photo preview" onClose={() => setViewPhoto(null)}><div className="report-section-title"><h2>Photo preview</h2><Button type="button" variant="ghost" onClick={() => setViewPhoto(null)} aria-label="Close photo preview"><X size={20} /></Button></div>{viewPhoto && <img src={viewPhoto.url} alt={`Full photo: ${viewPhoto.file.name}`} />}</dialog>
  </main>;
}
