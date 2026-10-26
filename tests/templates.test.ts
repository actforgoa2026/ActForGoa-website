import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync} from 'node:fs';
import {parseTemplate, emptyDraft, visibleFields, filledText, restoreDraft, type TableBlock} from '../src/template-model.ts';
import {createTemplateDocx} from '../src/template-export.ts';
import {guideDocuments} from '../src/guides.ts';
import {createRequire} from 'node:module';
const AdmZip = createRequire(import.meta.url)('adm-zip');
const load = (file: string) => parseTemplate(file.replace(/\.(txt|md)$/, ''), readFileSync(`public/guides/templates/${file}`, 'utf8'));

test('all 18 templates expose every placeholder and export filled values without bracket instructions', async () => {
 const files = readdirSync('public/guides/templates');
 assert.equal(files.length, 18);
 for (const file of files) {
  const template = load(file), draft = emptyDraft(template);
  draft.handover = draft.secondPoint = true;
  for (const b of template.blocks) if (b.kind !== 'table' && b.choice) draft.choices[b.choice] = true;
  for (const purpose of ['support', 'damage'] as const) {
   draft.purpose = purpose;
   const fields = visibleFields(template, draft);
   assert(fields.length > 0, file);
   assert.equal(new Set(fields.map(f => f.id)).size, fields.length, file);
   fields.forEach((f, i) => draft.values[f.id] = f.date ? '2026-10-23' : `Filled ${i}: Goa & São Tomé <sample>\nSecond line`);
   const text = filledText(template, draft);
   assert(!/\[[^\]]*\]/.test(text), file);
   assert(!text.includes('Not provided'), file);
   assert(text.includes('São Tomé'), file);
   const blob = await createTemplateDocx(template, draft);
   const zip = new AdmZip(Buffer.from(await blob.arrayBuffer()));
   const xml = zip.readAsText('word/document.xml');
   assert(xml.includes('São Tomé'), file);
   assert(xml.includes('&lt;sample&gt;'), file);
   assert(!xml.includes('<w:i/>'), file);
  }
 }
});

test('guide template links all resolve to source-backed editor IDs', () => {
 const bundled = JSON.parse(readFileSync('src/content/templates.json', 'utf8'));
 for (const file of readdirSync('public/guides/templates')) assert.equal(bundled[file], readFileSync(`public/guides/templates/${file}`, 'utf8'), file);
 const ids = new Set(readdirSync('public/guides/templates').map(f => f.replace(/\.(txt|md)$/, '')));
 for (const guide of guideDocuments) for (const t of guide.templates) assert(ids.has(t.url.split('/').pop()!.replace(/\.(txt|md)$/, '')));
});

test('handover data survives toggling but is excluded when switched off', () => {
 const template = load('12-animal-assistance.txt'), draft = emptyDraft(template);
 draft.handover = true;
 const field = visibleFields(template, draft).find(f => f.label === 'Accepted by and role')!;
 assert(field);
 draft.values[field.id] = 'Test rescue handover';
 assert(filledText(template, draft).includes('Test rescue handover'));
 draft.handover = false;
 assert(!filledText(template, draft).includes('Test rescue handover'));
 assert(!visibleFields(template, draft).some(f => f.id === field.id));
 assert(filledText(template, draft).includes('Keep original photographs'));
});

test('RTI requests include only selected records and preserve statutory wording', () => {
 const template = load('03-rti-records-request.txt'), draft = emptyDraft(template);
 const choices = template.blocks.filter(b => b.kind !== 'table' && b.choice);
 assert.equal(choices.length, 5);
 const selected = choices[1];
 assert(selected.kind !== 'table');
 draft.choices[selected.choice!] = true;
 draft.values[selected.fields[0].id] = 'Test property';
 const text = filledText(template, draft);
 assert(text.includes('inspection reports'));
 assert(text.includes('Test property'));
 assert(!text.includes('development permission/technical clearance'));
 assert(text.includes('section 6(3)'));
});

test('support and damage enquiry branches are exclusive while shared fields remain', () => {
 const template = load('11-farming-support-or-damage.txt'), draft = emptyDraft(template);
 let text = filledText(template, draft);
 assert(text.includes('Proposed activity and estimated cost'));
 assert(!text.includes('Observed damage:'));
 draft.purpose = 'damage';
 text = filledText(template, draft);
 assert(!text.includes('Proposed activity and estimated cost'));
 assert(text.includes('Observed damage:'));
 assert(text.includes('Evidence index:'));
});

test('repeated log entries retain independent values and removed rows do not export', () => {
 const template = load('05-case-log.md'), draft = emptyDraft(template);
 const table = template.blocks.find(b => b.kind === 'table') as TableBlock;
 draft.rows[table.id].push('second');
 const fields = visibleFields(template, draft);
 fields.filter(f => f.label === 'Document or action').forEach((f, i) => draft.values[f.id] = `Action ${i + 1}`);
 assert(filledText(template, draft).includes('Action 2'));
 draft.rows[table.id] = ['second'];
 const text = filledText(template, draft);
 assert(!text.includes('Action 1'));
 assert(text.includes('Action 2'));
});

test('draft restoration rejects corrupt, wrong-template and malformed row data', () => {
 const template = load('05-case-log.md'), draft = emptyDraft(template);
 assert.equal(restoreDraft(template, '{bad'), null);
 assert.equal(restoreDraft(template, JSON.stringify({version:1,templateId:'wrong',draft})), null);
 draft.rows[Object.keys(draft.rows)[0]] = ['duplicate','duplicate'];
 const restored = restoreDraft(template, JSON.stringify({version:1,templateId:template.id,draft}))!;
 assert.deepEqual(restored.rows[Object.keys(restored.rows)[0]], ['first']);
});
