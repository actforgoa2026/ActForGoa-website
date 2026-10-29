import {Fragment, useEffect, useRef, useState} from 'react';
import {Link, useLocation, useParams} from 'react-router-dom';
import {ArrowLeft, ArrowRight, Download, Plus, Printer, Share2, Trash2} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {Textarea} from './components/arc/textarea/textarea';
import SegmentedControl from './components/arc/segmented-control/segmented-control';
import {Switch} from './components/arc/switch/switch';
import {Checkbox} from './components/arc/checkbox/checkbox';
import {templates} from './template-catalogue';
import {templatePurpose} from './template-path';
import {blockVisible, emptyDraft, fillTemplate, restoreDraft, tableFields, tableRowIds, templateNote, visibleFields, type Draft, type Field, type TableBlock, type Template} from './template-model';
import RecipientGuide from './RecipientGuide';
import './template-editor.css';

const draftsInThisTab = new Map<string, Draft>();
const storageKey = (id: string) => `actforgoa:template:v1:${id}`;
const recordLabels = ['Permissions and approved plans', 'Inspection reports and findings', 'Complaint decisions and action taken', 'Rules, service standards and checklists', 'Responsible office and transfer records'];

function readDraft(template: Template, purpose?: Draft['purpose']) {
 const initialPurpose = (draft: Draft) => purpose && template.id === '11-farming-support-or-damage' ? {...draft, purpose} : draft;
 try {
  const saved = restoreDraft(template, localStorage.getItem(storageKey(template.id)));
  return {draft: initialPurpose(draftsInThisTab.get(template.id) || saved || emptyDraft(template)), saved: !!saved, storageError: ''};
 } catch {
  return {draft: initialPurpose(draftsInThisTab.get(template.id) || emptyDraft(template)), saved: false, storageError: 'This browser cannot save drafts. You can still fill in this document and save a PDF.'};
 }
}

function DocumentPreview({template, draft}: {template: Template; draft: Draft}) {
 return <article className="template-document" aria-label="Filled document">
  <h2>{template.title}</h2>
  <p className="document-note">{templateNote(template)}</p>
  {fillTemplate(template, draft).map((block, i) => block.kind === 'table'
   ? <div className="document-table" key={i} tabIndex={0} role="region" aria-label="Document table"><table><thead><tr>{block.headers.map((h, c) => <th scope="col" key={c}>{h}</th>)}</tr></thead><tbody>{block.rows.map((row, r) => <tr key={r}>{row.map((cell, c) => <td key={c}>{cell}</td>)}</tr>)}</tbody></table></div>
   : block.kind === 'heading' ? <h3 key={i}>{block.text}</h3> : <p key={i}>{block.text}</p>)}
 </article>;
}

function Editor({template}: {template: (typeof templates)[number]}) {
 const location = useLocation();
 const [initial] = useState(() => readDraft(template, templatePurpose(location.search)));
 const [draft, setDraft] = useState<Draft>(initial.draft);
 const currentDraft = useRef(draft);
 currentDraft.current = draft;
 const [saveOnDevice, setSaveOnDevice] = useState(initial.saved);
 const [storageError, setStorageError] = useState(initial.storageError);
 const [view, setView] = useState('fill');
 const [message, setMessage] = useState('');
 const [error, setError] = useState('');
 const [exporting, setExporting] = useState<'pdf' | 'word' | null>(null);
 const [pdf, setPdf] = useState<{blob: Blob; url: string; filename: string} | null>(null);
 const [clearRequested, setClearRequested] = useState(false);
 const [undo, setUndo] = useState<{draft: Draft; save: boolean} | null>(null);
 const [focusRow, setFocusRow] = useState<string | null>(null);
 const formRef = useRef<HTMLDivElement>(null);
 const fields = visibleFields(template, draft);
 const answered = fields.filter(f => draft.values[f.id]?.trim()).length;
 const choices = template.blocks.filter(b => b.kind !== 'table' && b.choice);
 const back = typeof location.state?.guideId === 'string' && /^guide-[a-z-]+$/.test(location.state.guideId) ? location.state.guideId : template.guideId;
 const returnTo = typeof location.state?.returnTo === 'string' && /^\/topics\/[a-z0-9/-]+$/.test(location.state.returnTo) ? location.state.returnTo : null;

 useEffect(() => {setPdf(null);}, [draft]);
 useEffect(() => () => {if (pdf) URL.revokeObjectURL(pdf.url);}, [pdf]);

 useEffect(() => {
  const previous = document.title;
  document.title = `${template.label} template | ActForGoa`;
  return () => { document.title = previous; };
 }, [template.label]);

 useEffect(() => {
  draftsInThisTab.set(template.id, draft);
  if (!saveOnDevice) return;
  try {
   localStorage.setItem(storageKey(template.id), JSON.stringify({version: 1, templateId: template.id, draft}));
   setStorageError('');
  } catch {
   setStorageError('Your latest changes could not be saved on this device. Keep this page open and download a copy.');
  }
 }, [template.id, draft, saveOnDevice]);

 useEffect(() => {
  if ((!answered && !Object.values(draft.values).some(v => v.trim())) || (saveOnDevice && !storageError)) return;
  const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ''; };
  window.addEventListener('beforeunload', warn);
  return () => window.removeEventListener('beforeunload', warn);
 }, [answered, draft.values, saveOnDevice, storageError]);

 useEffect(() => {
  if (!focusRow) return;
  formRef.current?.querySelector<HTMLElement>(`[data-row="${CSS.escape(focusRow)}"] input`)?.focus();
  setFocusRow(null);
 }, [focusRow]);

 function updateField(id: string, value: string) {
  setDraft(previous => ({...previous, values: {...previous.values, [id]: value}}));
  setError(''); setMessage('');
 }
 function setSaving(enabled: boolean) {
  if (!enabled) {
   try { localStorage.removeItem(storageKey(template.id)); setStorageError(''); }
   catch { setStorageError('This browser could not remove the saved copy. Clear this site’s browser data to remove it.'); }
  }
  setSaveOnDevice(enabled);
 }
 function fieldControl(field: Field) {
  const common = {id: field.id, label: field.label, value: draft.values[field.id] || '', onChange: (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => updateField(field.id, event.target.value), description: field.label === 'To' ? undefined : field.hint || undefined, maxLength: 30000};
  const control = field.multiline ? <Textarea {...common} rows={3} /> : <Input {...common} type={field.date ? 'date' : 'text'} />;
  const recipient = field.label === 'To' || (/^0[34]-/.test(template.id) && field.hint === 'Public authority and address');
  return <div className="template-field" key={field.id}>{control}{recipient && <RecipientGuide templateId={template.id} onChoose={value => updateField(field.id, value)}/>}</div>;
 }
 function addRow(block: TableBlock) {
  const rowId = crypto.randomUUID();
  setDraft(previous => ({...previous, rows: {...previous.rows, [block.id]: [...tableRowIds(block, previous), rowId]}}));
  setFocusRow(rowId);
  setMessage('Entry added.');
 }
 function removeRow(block: TableBlock, rowId: string) {
  setDraft(previous => {
   const values = {...previous.values};
   for (const key of Object.keys(values)) if (key.startsWith(`${block.id}-${rowId}-`)) delete values[key];
   return {...previous, values, rows: {...previous.rows, [block.id]: tableRowIds(block, previous).filter(id => id !== rowId)}};
  });
  setMessage('Entry removed.');
  requestAnimationFrame(() => document.getElementById(`add-${block.id}`)?.focus());
 }
 function tableEditor(block: TableBlock) {
  const ids = tableRowIds(block, draft);
  return <section className="template-table-editor" key={block.id} aria-label={block.title}>
   {ids.map((rowId, index) => {
    const row = block.repeatable ? block.rows[0] : block.rows[index];
    const title = block.repeatable ? `Entry ${index + 1}` : row[0];
    const rowFields = block.headers.flatMap((_, col) => tableFields(block, rowId, col));
    const completed = rowFields.filter(f => draft.values[f.id]?.trim()).length;
    return <details className="template-entry" key={rowId} open={block.repeatable || undefined} data-row={rowId}>
     <summary><span>{title}</span><span className="entry-count">{completed} of {rowFields.length} filled</span></summary>
     <div className="template-fields">
      {rowFields.map(field => <div key={field.id}>
       {/Status or not applicable/.test(field.label) && <div className="template-choice"><Checkbox label="Confirmed with supporting evidence" checked={draft.values[field.id] === 'Confirmed'} onCheckedChange={checked => updateField(field.id, checked === true ? 'Confirmed' : '')}/></div>}
       {fieldControl(field)}
      </div>)}
      {block.repeatable && ids.length > 1 && <Button type="button" variant="ghost" onClick={() => removeRow(block, rowId)} aria-label={`Remove entry ${index + 1}`}><Trash2 size={16}/>Remove entry</Button>}
     </div>
    </details>;
   })}
   {block.repeatable && <Button id={`add-${block.id}`} type="button" variant="secondary" disabled={ids.length >= 100} onClick={() => addRow(block)}><Plus size={16}/>Add entry</Button>}
  </section>;
 }
 function checkExport() {
  if (!answered) { setError('Fill in at least one detail before saving a copy.'); return false; }
  if (choices.length && !choices.some(b => b.kind !== 'table' && draft.choices[b.choice!])) { setError('Choose at least one record to request.'); return false; }
  setError(''); return true;
 }
 async function downloadWord() {
  if (!checkExport()) return;
  setExporting('word'); setMessage('');
  try {
   const {createTemplateDocx, downloadBlob} = await import('./template-export');
   downloadBlob(await createTemplateDocx(template, draft), `${template.id}-filled.docx`);
   setMessage('Your Word document is ready. Check your browser’s downloads.');
  } catch { setError('The Word document could not be created. Try again, or use Print / save PDF.'); }
  finally { setExporting(null); }
 }
 async function savePdf() {
  if (!checkExport()) return;
  setExporting('pdf'); setMessage('');
  try {
   const {createTemplatePdf} = await import('./template-pdf');
   const {downloadBlob} = await import('./template-download');
   const blob = await createTemplatePdf(template, draft);
   if (currentDraft.current !== draft) throw new Error('Your details changed while the PDF was being prepared. Save PDF again for the latest version.');
   const filename = `${template.id}-filled.pdf`;
   setPdf({blob, filename, url: URL.createObjectURL(blob)});
   downloadBlob(blob, filename);
   setMessage('Your PDF is ready. If it did not save, open it below and save it to your files.');
  } catch (cause) { setError(cause instanceof Error ? cause.message : 'The PDF could not be created. Use Print / save PDF or Word instead.'); }
  finally { setExporting(null); }
 }
 async function sharePdf() {
  if (!pdf) return;
  try { await navigator.share({files: [new File([pdf.blob], pdf.filename, {type: 'application/pdf'})], title: template.label}); }
  catch (cause) { if (!(cause instanceof DOMException && cause.name === 'AbortError')) setError('Sharing is unavailable here. Open the PDF below to save it.'); }
 }
 function clearDraft() {
  setUndo({draft, save: saveOnDevice});
  setSaving(false);
  setDraft(emptyDraft(template));
  setClearRequested(false);
  setMessage('Draft cleared.'); setError('');
 }

 return <main className="shell template-editor">
  <Link className="back-link" to={returnTo || (back ? `/read/${back}` : '/library')}><ArrowLeft size={16}/>Back to {returnTo ? 'your next step' : back ? 'guide' : 'library'}</Link>
  <header className="template-heading">
   <h1>{template.label}</h1>
   <p>Fill in the details, review your document, then save a PDF.</p>
   <details className="template-context"><summary>About this draft</summary><p>This is an ActForGoa draft, not an official application. Check the receiving office’s requirements before submitting. Blank fields appear as “Not provided” in your document.</p></details>
  </header>
  <div className="template-toolbar">
   <Switch label="Save draft locally" checked={saveOnDevice} onCheckedChange={setSaving} aria-describedby="draft-storage-hint"/>
   <details className="template-storage"><summary>Privacy & storage</summary><p id="draft-storage-hint">{saveOnDevice && !storageError ? 'Saved in this browser. Anyone using this browser may be able to open it.' : 'Your entries stay in this tab until you close or refresh it. They are not sent to a server.'}</p></details>
   {storageError && <p role="alert">{storageError}</p>}
  </div>
  <div className="template-mobile-view"><SegmentedControl label="Template view" value={view} onValueChange={setView} options={[{value:'fill',label:'Fill in details'},{value:'preview',label:'Review & save'}]}/></div>
  <div className="template-layout" data-view={view}>
   <div className="template-form" ref={formRef}>
    <div className="template-section-title"><h2>Your details</h2><span>{answered} of {fields.length} fields filled</span></div>
    <p className="template-help">Leave unknown details blank.</p>
    {template.blocks.some(b => b.group === 'support') && <div className="template-purpose"><h3>What is this enquiry about?</h3><SegmentedControl label="Enquiry purpose" value={draft.purpose} onValueChange={value => setDraft(d => ({...d, purpose:value as Draft['purpose']}))} options={[{value:'support',label:'Support before spending'},{value:'damage',label:'Report damage'}]}/></div>}
    <div className="template-fields">
     {template.blocks.map(block => {
      if (block.kind === 'heading' && block.group === 'handover') return <Fragment key={block.id}><div className="option-toggle"><Switch label="Include a handover record" checked={draft.handover} onCheckedChange={value => setDraft(d => ({...d, handover:value}))} aria-describedby="handover-help"/><p id="handover-help" className="template-help">For an animal accepted into someone’s care.</p></div>{draft.handover && <h3 className="template-subheading">{block.text}</h3>}</Fragment>;
      if (block.kind === 'heading' && block.group === 'secondPoint') return <Fragment key={block.id}><div className="option-toggle"><Switch label="Include a second consultation point" checked={draft.secondPoint} onCheckedChange={value => setDraft(d => ({...d, secondPoint:value}))}/></div>{draft.secondPoint && <h3 className="template-subheading">{block.text}</h3>}</Fragment>;
      if (!blockVisible(block, draft)) return null;
      if (block.kind === 'table') return tableEditor(block);
      if (block.kind === 'heading') return <h3 className="template-subheading" key={block.id}>{block.text}</h3>;
      if (block.choice) {
       const index = choices.findIndex(b => b.id === block.id);
       return <section className="template-record-choice" key={block.id}>
        {index === 0 && <><h3>Which records do you need?</h3><p className="template-help">Select the requests that apply to your case.</p></>}
        <div className="template-choice"><Checkbox label={recordLabels[index]} checked={draft.choices[block.choice] || false} onCheckedChange={checked => setDraft(d => ({...d, choices:{...d.choices, [block.choice!]:checked === true}}))}/></div>
        {draft.choices[block.choice] && <div className="template-fields"><p className="template-help">{block.text.replace(/\[[^\]]*\]/g, '…')}</p>{block.fields.map(fieldControl)}</div>}
       </section>;
      }
      return block.fields.length ? <div key={block.id} className="template-fields">{block.fields.length > 1 && <p className="template-sentence">{block.text.replace(/\[[^\]]*\]/g, '…')}</p>}{block.fields.map(fieldControl)}</div> : null;
     })}
    </div>
    <div className="template-reset">
     {clearRequested ? <><p>Clear all entries in this template?</p><Button variant="secondary" onClick={clearDraft}>Clear draft</Button><Button variant="ghost" onClick={() => setClearRequested(false)}>Keep editing</Button></> : <Button variant="ghost" onClick={() => setClearRequested(true)}><Trash2 size={16}/>Clear draft</Button>}
     {undo && <Button variant="ghost" onClick={() => {setDraft(undo.draft);setSaveOnDevice(undo.save);setUndo(null);setMessage('Draft restored.');}}>Undo clear</Button>}
    </div>
   </div>
   <aside className="template-preview">
    <div className="template-preview-tools">
     <h2>Document preview</h2>
     <p>Review the wording and any missing details before you send it.</p>
     <div className="template-actions">
      <Button onClick={savePdf} loading={exporting === 'pdf'} disabled={!!exporting}><Download size={17}/>Save PDF</Button>
      <Button variant="secondary" disabled={!!exporting} onClick={() => {if (checkExport()) window.print();}}><Printer size={17}/>Print / save PDF</Button>
     </div>
     {pdf && <div className="template-pdf-ready"><a className="text-link" href={pdf.url} target="_blank" rel="noopener noreferrer">Open your completed PDF<ArrowRight size={17}/></a>{typeof navigator.canShare === 'function' && navigator.canShare({files: [new File([pdf.blob], pdf.filename, {type: 'application/pdf'})]}) && <Button variant="secondary" onClick={sharePdf}><Share2 size={17}/>Share PDF</Button>}</div>}
     <details className="template-export-options"><summary>Other ways to save</summary><Button variant="ghost" onClick={downloadWord} loading={exporting === 'word'} disabled={!!exporting}><Download size={17}/>Save Word document</Button><p className="template-help">Print / save PDF uses your device’s print menu. All entries and exports stay on your device.</p></details>
     {error && <p role="alert" className="template-feedback">{error}</p>}
     <p role="status" className="template-feedback">{message}</p>
    </div>
    <DocumentPreview template={template} draft={draft}/>
   </aside>
  </div>
  <div className="template-mobile-next"><Button variant="secondary" onClick={() => {setView(view === 'fill' ? 'preview' : 'fill');document.querySelector('.template-mobile-view')?.scrollIntoView({block:'start'});}}>{view === 'fill' ? 'Review & save' : 'Back to details'}<ArrowRight size={16}/></Button></div>
 </main>;
}

export default function TemplateEditor() {
 const {id} = useParams();
 const location = useLocation();
 const template = templates.find(t => t.id === id);
 if (!template) return <main className="shell empty-state"><h1>Template not found</h1><p>Choose a template from one of the practical guides.</p><Link className="back-link" to="/library">Back to library<ArrowRight size={16}/></Link></main>;
 return <Editor key={`${template.id}:${templatePurpose(location.search) ?? ''}`} template={template}/>;
}
