import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createRequire} from 'node:module';
import {emptyDraft, parseTemplate, tableFields, visibleFields, type TableBlock} from '../src/template-model';
import {pdfTextRuns, templatePdfDefinition, templatePdfFonts} from '../src/template-pdf';
import {templateIdFromUrl, templatePath} from '../src/template-path';

const PdfPrinter = createRequire(import.meta.url)('pdfmake');
const fonts = Object.fromEntries(Object.entries(templatePdfFonts).map(([family, styles]) => [family,
 Object.fromEntries(Object.entries(styles).map(([style, filename]) => [style, resolve('public/assets/pdf-fonts', filename as string)])),
]));
const load = (filename: string) => parseTemplate(templateIdFromUrl(filename), readFileSync(`public/guides/templates/${filename}`, 'utf8'));
async function render(definition: ReturnType<typeof templatePdfDefinition>): Promise<Buffer> {
 return new Promise((resolve, reject) => {
  const doc = new PdfPrinter(fonts).createPdfKitDocument(definition);
  const chunks: Buffer[] = [];
  doc.on('data', (chunk: Buffer) => chunks.push(chunk));
  doc.on('error', reject);
  doc.on('end', () => resolve(Buffer.concat(chunks)));
  doc.end();
 });
}

test('all 18 forms create real PDFs with entered Latin and Devanagari text', async () => {
 for (const filename of readdirSync('public/guides/templates')) {
  const template = load(filename), draft = emptyDraft(template);
  draft.handover = draft.secondPoint = true;
  for (const block of template.blocks) if (block.kind !== 'table' && block.choice) draft.choices[block.choice] = true;
  for (const field of visibleFields(template, draft)) draft.values[field.id] = field.date ? '2026-10-28' : 'São Tomé — गोवा, गोंय\nEntered detail';
  const bytes = await render(templatePdfDefinition(template, draft));
  const raw = bytes.toString('latin1');
  assert(raw.startsWith('%PDF-1.'), filename);
  assert(raw.includes('%%EOF'), filename);
  assert(raw.includes('/ToUnicode'), `${filename}: fonts must preserve extractable Unicode`);
  assert(raw.includes('NotoSansDevanagari'), `${filename}: missing Devanagari font`);
 }
});

test('long repeating logs paginate, keep their rows and omit removed rows', async () => {
 const template = load('05-case-log.md'), draft = emptyDraft(template);
 const table = template.blocks.find(block => block.kind === 'table') as TableBlock;
 draft.rows[table.id] = Array.from({length: 30}, (_, i) => `entry-${i}`);
 for (const id of draft.rows[table.id]) for (let col = 0; col < table.headers.length; col++) {
  for (const field of tableFields(table, id, col)) draft.values[field.id] = `Saved ${id}\n${'Long observation. '.repeat(12)}`;
 }
 draft.rows[table.id].splice(10, 1);
 const definition = templatePdfDefinition(template, draft);
 const serialized = JSON.stringify(definition);
 assert(serialized.includes('Saved entry-29'));
 assert(!serialized.includes('Saved entry-10'));
 assert.equal(definition.pageOrientation, 'landscape');
 const bytes = await render(definition);
 const pages = bytes.toString('latin1').match(/\/Type \/Page\b/g) || [];
 assert(pages.length > 2, 'A long log must paginate instead of clipping');
});

test('PDF text keeps whole Devanagari graphemes and rejects unsupported characters visibly', () => {
 const value = 'São Tomé: गोवा, गोंय, क्षत्रिय';
 const runs = pdfTextRuns(value);
 assert.equal(runs.map(run => run.text).join(''), value);
 assert(runs.some(run => run.font === 'NotoSansDevanagari' && String(run.text).includes('क्षत्रिय')));
 assert.throws(() => pdfTextRuns('Keep this 🐢'), /Print \/ save PDF or Word/);
 assert.throws(() => pdfTextRuns('中文'), /keep every character/);
});

test('legacy form URLs map to editors without query or hash fragments in the ID', () => {
 assert.equal(templatePath('/guides/templates/01-complaint.txt?download=1#start'), '/templates/01-complaint');
 assert.equal(templatePath('07-building-checklist.md'), '/templates/07-building-checklist');
});
