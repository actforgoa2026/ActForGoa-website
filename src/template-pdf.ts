import type {Content, ContentText, TDocumentDefinitions, TFontDictionary} from 'pdfmake/interfaces';
import coverage from './content/pdf-font-coverage.json';
import {fillTemplate, templateNote, type Draft, type Template} from './template-model';

type FontName = keyof typeof coverage;
const fontNames: FontName[] = ['NotoSans', 'NotoSansDevanagari'];
const supports = (font: FontName, character: string) => {
 const code = character.codePointAt(0)!;
 return /[\n\r\t\u200c\u200d]/u.test(character) || coverage[font].some(([start, end]) => code >= start && code <= end);
};

/** Select by whole grapheme so Devanagari vowel marks and conjuncts stay together. */
export function pdfTextRuns(text: string): ContentText[] {
 const runs: ContentText[] = [];
 const segments = new Intl.Segmenter('en', {granularity: 'grapheme'}).segment(text.replace(/\r\n?/g, '\n').replace(/\t/g, '    '));
 for (const {segment} of segments) {
  const order: FontName[] = /\p{Script=Devanagari}/u.test(segment) ? ['NotoSansDevanagari', 'NotoSans'] : fontNames;
  const font = order.find(name => [...segment].every(character => supports(name, character)));
  if (!font) throw new Error('This PDF font does not support some of your text. Use Print / save PDF or Word to keep every character.');
  const previous = runs.at(-1);
  if (previous?.font === font) previous.text = String(previous.text) + segment;
  else runs.push({text: segment, font});
 }
 return runs;
}

export function templatePdfDefinition(template: Template, draft: Draft): TDocumentDefinitions {
 const blocks = fillTemplate(template, draft);
 const text = (value: string): ContentText => ({text: pdfTextRuns(value)});
 const content: Content[] = [
  {...text(template.title), style: 'title'},
  ...(template.note ? [{...text(templateNote(template)), style: 'note'}] : []),
  ...blocks.map((block): Content => {
   if (block.kind !== 'table') return {...text(block.text), style: block.kind === 'heading' ? 'heading' : 'body'};
   return {
    table: {
     headerRows: 1,
     widths: block.headers.map(() => '*'),
     body: [block.headers.map(value => ({...text(value), bold: true, fillColor: '#eef4f0'})), ...block.rows.map(row => row.map(value => text(value)))],
    },
    // Permit rows to split: a long observation must not disappear beyond the page.
    layout: {hLineColor: () => '#cbd4ce', vLineColor: () => '#cbd4ce', hLineWidth: () => .5, vLineWidth: () => .5, paddingLeft: () => 6, paddingRight: () => 6, paddingTop: () => 6, paddingBottom: () => 6},
    fontSize: 9, margin: [0, 4, 0, 14],
   };
  }),
 ];
 return {
  info: {title: template.title, author: 'ActForGoa', creator: 'ActForGoa form editor'},
  pageSize: 'A4', pageOrientation: blocks.some(block => block.kind === 'table' && block.headers.length > 4) ? 'landscape' : 'portrait',
  pageMargins: [40, 40, 40, 44],
  defaultStyle: {font: 'NotoSans', fontSize: 10, lineHeight: 1.3, color: '#14251c'},
  styles: {title: {fontSize: 19, bold: true, margin: [0, 0, 0, 14]}, note: {fontSize: 9, color: '#46594b', margin: [0, 0, 0, 18]}, heading: {fontSize: 13, bold: true, margin: [0, 14, 0, 8]}, body: {margin: [0, 0, 0, 10]}},
  content,
  footer: (current, total) => ({text: `${current} / ${total}`, alignment: 'center', fontSize: 8, margin: [0, 16, 0, 0]}),
 };
}

export const templatePdfFonts: TFontDictionary = Object.fromEntries(fontNames.map(name => [name, {
 normal: `${name}-Regular.ttf`, bold: `${name}-Bold.ttf`, italics: `${name}-Regular.ttf`, bolditalics: `${name}-Bold.ttf`,
}]));

let virtualFonts: Promise<Record<string, string>> | undefined;
async function loadFonts(): Promise<Record<string, string>> {
 if (!virtualFonts) virtualFonts = Promise.all(fontNames.flatMap(name => ['Regular', 'Bold'].map(async weight => {
  const filename = `${name}-${weight}.ttf`;
  const response = await fetch(`/assets/pdf-fonts/${filename}`, {signal: AbortSignal.timeout(15000)});
  if (!response.ok) throw new Error('The PDF fonts could not load. Try again, or use Print / save PDF.');
  const bytes = new Uint8Array(await response.arrayBuffer());
  let binary = '';
  for (let offset = 0; offset < bytes.length; offset += 8192) binary += String.fromCharCode(...bytes.subarray(offset, offset + 8192));
  return [filename, btoa(binary)] as const;
 }))).then(entries => Object.fromEntries(entries)).catch(() => {
  virtualFonts = undefined;
  throw new Error('The PDF could not load. Try again, or use Print / save PDF.');
 });
 return virtualFonts;
}

/** Fonts and PDF code are loaded only when the visitor requests a PDF. Entries stay on-device. */
export async function createTemplatePdf(template: Template, draft: Draft): Promise<Blob> {
 const definition = templatePdfDefinition(template, draft);
 const [{default: pdfMake}, fonts] = await Promise.all([import('pdfmake/build/pdfmake'), loadFonts()]);
 return new Promise((resolve, reject) => {
  try {
   // Using the stream also catches layout/font failures; the legacy getBlob callback
   // does not expose pdfmake's asynchronous rejection to its caller.
   const stream = pdfMake.createPdf(definition, undefined, templatePdfFonts, fonts).getStream();
   const chunks: ArrayBuffer[] = [];
   stream.on('data', (chunk: Uint8Array) => chunks.push(new Uint8Array(chunk).buffer));
   stream.on('error', reject);
   stream.on('end', () => resolve(new Blob(chunks, {type: 'application/pdf'})));
   stream.end();
  }
  catch (error) { reject(error); }
 });
}
