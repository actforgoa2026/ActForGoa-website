import {Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, HeadingLevel, PageOrientation} from 'docx';
import {fillTemplate, templateNote, type Template, type Draft} from './template-model';
export {downloadBlob} from './template-download';

export async function createTemplateDocx(template: Template, draft: Draft): Promise<Blob> {
 const filled = fillTemplate(template, draft);
 const wide = filled.some(b => b.kind === 'table' && b.headers.length > 4);
 const paragraph = (text: string, bold = false) => new Paragraph({children: text.split('\n').flatMap((line, i) => [new TextRun({text: line, bold, ...(i ? {break: 1} : {})})]), spacing: {after: 140}, keepNext: bold});
 const children = [new Paragraph({text: template.title, heading: HeadingLevel.TITLE}), paragraph(templateNote(template)), ...filled.map(block => {
  if (block.kind !== 'table') return block.kind === 'heading'
   ? new Paragraph({text: block.text, heading: HeadingLevel.HEADING_2}) : paragraph(block.text);
  return new Table({width: {size: 100, type: WidthType.PERCENTAGE}, rows: [block.headers, ...block.rows].map((row, i) => new TableRow({tableHeader: i === 0, children: row.map(text => new TableCell({width: {size: 100 / row.length, type: WidthType.PERCENTAGE}, children: [paragraph(text, i === 0)], margins: {top: 100, bottom: 100, left: 100, right: 100}}))}))});
 })];
 return Packer.toBlob(new Document({creator: 'ActForGoa', title: template.title,
  styles: {default: {document: {run: {font: 'Arial', size: 22, color: '000000'}, paragraph: {spacing: {line: 280}}}, title: {run: {font: 'Arial', size: 36, bold: true, color: '000000'}, paragraph: {spacing: {after: 240}}}, heading2: {run: {font: 'Arial', size: 26, bold: true, color: '000000'}, paragraph: {spacing: {before: 240, after: 140}}}}},
  sections: [{properties: {page: {size: {width: 11906, height: 16838, orientation: wide ? PageOrientation.LANDSCAPE : PageOrientation.PORTRAIT}, margin: {top: 900, bottom: 900, left: 900, right: 900}}}, children}],
 }));
}
