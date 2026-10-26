export type Field = {id: string; label: string; hint: string; multiline: boolean; date: boolean};
type BaseBlock = {id: string; group?: string};
export type TextBlock = BaseBlock & {kind: 'paragraph' | 'heading'; text: string; fields: Field[]; choice?: string};
export type TableBlock = BaseBlock & {kind: 'table'; headers: string[]; rows: string[][]; repeatable: boolean; title: string};
export type TemplateBlock = TextBlock | TableBlock;
export type Template = {id: string; title: string; note: string; blocks: TemplateBlock[]};
export type Draft = {values: Record<string, string>; rows: Record<string, string[]>; choices: Record<string, boolean>; handover: boolean; secondPoint: boolean; purpose: 'support' | 'damage'};
export type FilledBlock = {kind: 'paragraph' | 'heading'; text: string} | {kind: 'table'; headers: string[]; rows: string[][]};
const slots = /\[([^\]]*)\]/g;
const sentenceCase = (text: string) => text === text.toUpperCase() ? text.charAt(0) + text.slice(1).toLowerCase() : text;
const cleanHeading = (text: string) => sentenceCase(text.replace(/^#+\s*/, '').replace(/^DRAFT TEMPLATE:\s*/, ''));

export function fieldsFor(text: string, prefix: string, context = ''): Field[] {
 const matches = [...text.matchAll(slots)];
 return matches.map((match, i) => {
  const before = text.slice(0, match.index).trim();
  const hint = match[1].trim();
  const colonLabel = matches.length === 1 && before.includes(':') ? before.slice(0, before.indexOf(':')) : '';
  let label = context || colonLabel || (hint.length < 75 ? hint : 'Details');
  if (matches.length > 1 && context) label = `${context}: ${hint}`;
  label = label.replace(/^\d+\.\s*/, '').replace(/:$/, '');
  label = label.charAt(0).toUpperCase() + label.slice(1);
  const date = /^date$/i.test(hint) && /date|reminder/i.test(label);
  return {id: `${prefix}-${i}`, label: label || 'Details', hint: hint && hint !== label ? hint : '', date,
   multiline: !date && (text.trim().startsWith('[') || /observ|condition|hazard|description|attachment|evidence|question|concern|situation|ground|timing|address|documents|scope|activity|action|record|details|effect|uncertainty/i.test(label) || hint.length > 65)};
 });
}

export function parseTemplate(id: string, source: string): Template {
 const lines = source.replace(/\r/g, '').trim().split('\n');
 const title = cleanHeading(lines.shift()!);
 const firstContent = lines.find(line => line.trim()) || '';
 // Some letters begin with a fillable greeting rather than an instruction note.
 const note = firstContent.includes('[') ? '' : firstContent;
 if (note) lines.splice(lines.indexOf(note), 1);
 const blocks: TemplateBlock[] = [];
 let group: string | undefined;
 let heading = '';
 let context = '';
 let rtiChoices = false;
 for (let i = 0; i < lines.length; i++) {
  const line = lines[i].trim();
  if (!line) continue;
  const blockId = `b${i}`;
  if (/^HANDOVER$/.test(line)) group = 'handover';
  if (/^POINT 2$/.test(line)) group = 'secondPoint';
  if (/^A\. SUPPORT/.test(line)) group = 'support';
  if (/^B\. DAMAGE/.test(line)) group = 'damage';
  if (/^(Keep original|Evidence index:|Access difficulties,)/.test(line)) group = undefined;
  if (line === 'Select and adapt:') { rtiChoices = true; continue; }
  if (rtiChoices && !/^\d+\./.test(line)) rtiChoices = false;
  if (line.startsWith('|') && /^\|[\s:|-]+\|$/.test(lines[i + 1]?.trim() || '')) {
   const cells = (row: string) => row.trim().slice(1, -1).split('|').map(cell => cell.trim());
   const headers = cells(line);
   const rows: string[][] = [];
   i += 2;
   while (lines[i]?.trim().startsWith('|')) rows.push(cells(lines[i++]));
   i--;
   blocks.push({id: blockId, kind: 'table', headers, rows, group, title: heading || title,
    repeatable: rows.length === 1 && rows[0].every(cell => cell.includes('['))});
  } else if (/^#{1,3}\s/.test(line) || (/^[A-Z][A-Z0-9 .,/-]+$/.test(line) && !line.includes('['))) {
   heading = cleanHeading(line);
   context = '';
   blocks.push({id: blockId, kind: 'heading', text: heading, fields: [], group});
  } else {
   const fields = fieldsFor(line, blockId, line.startsWith('[') ? context : '');
   blocks.push({id: blockId, kind: 'paragraph', text: line, fields, group, choice: rtiChoices ? blockId : undefined});
   context = line.endsWith(':') ? line.slice(0, -1) : '';
  }
 }
 return {id, title, note, blocks};
}

export function emptyDraft(template: Template): Draft {
 return {values: {}, choices: {}, rows: Object.fromEntries(template.blocks.filter((b): b is TableBlock => b.kind === 'table' && b.repeatable).map(b => [b.id, ['first']])), handover: false, secondPoint: false, purpose: 'support'};
}

export function blockVisible(block: TemplateBlock, draft: Draft) {
 if (block.group === 'handover' && !draft.handover) return false;
 if (block.group === 'secondPoint' && !draft.secondPoint) return false;
 if (block.group === 'support' || block.group === 'damage') return block.group === draft.purpose;
 return true;
}

export const tableRowIds = (block: TableBlock, draft: Draft) => block.repeatable ? draft.rows[block.id] || ['first'] : block.rows.map((_, i) => String(i));
export function tableFields(block: TableBlock, rowId: string, col: number): Field[] {
 const row = block.repeatable ? block.rows[0] : block.rows[Number(rowId)];
 return fieldsFor(row[col], `${block.id}-${rowId}-c${col}`, block.headers[col]);
}

export function visibleFields(template: Template, draft: Draft): Field[] {
 return template.blocks.filter(block => blockVisible(block, draft)).flatMap(block => {
  if (block.kind === 'table') return tableRowIds(block, draft).flatMap(rowId => block.headers.flatMap((_, c) => tableFields(block, rowId, c)));
  return block.choice && !draft.choices[block.choice] ? [] : block.fields;
 });
}

function fill(text: string, fields: Field[], draft: Draft) {
 let i = 0;
 return text.replace(slots, () => {
  const field = fields[i++];
  const value = draft.values[field.id]?.trim();
  if (!value) return 'Not provided';
  if (field.date && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
   const [y, m, d] = value.split('-').map(Number);
   return new Intl.DateTimeFormat('en-GB', {day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'}).format(new Date(Date.UTC(y, m - 1, d)));
  }
  return value;
 });
}

export function fillTemplate(template: Template, draft: Draft): FilledBlock[] {
 return template.blocks.filter(block => blockVisible(block, draft)).flatMap((block): FilledBlock[] => {
  if (block.kind === 'table') return [{kind: 'table', headers: block.headers, rows: tableRowIds(block, draft).map(rowId => {
   const row = block.repeatable ? block.rows[0] : block.rows[Number(rowId)];
   return row.map((cell, c) => fill(cell, tableFields(block, rowId, c), draft));
  })}];
  if (block.choice && !draft.choices[block.choice]) return [];
  return [{kind: block.kind, text: fill(block.text, block.fields, draft)}];
 });
}

export function filledText(template: Template, draft: Draft) {
 const blocks = fillTemplate(template, draft);
 return [template.title, template.note, ...blocks.map(b => b.kind === 'table' ? [b.headers, ...b.rows].map(row => row.join(' | ')).join('\n') : b.text)].join('\n\n');
}

// Saved drafts are untrusted data. Bound their shape before they reach the editor.
export function restoreDraft(template: Template, raw: string | null): Draft | null {
 if (!raw) return null;
 try {
  const parsed = JSON.parse(raw);
  if (parsed.version !== 1 || parsed.templateId !== template.id || !parsed.draft || typeof parsed.draft !== 'object') return null;
  const draft = emptyDraft(template), data = parsed.draft;
  for (const [key, value] of Object.entries(data.values || {})) if (typeof value === 'string') draft.values[key] = value.slice(0, 30000);
  for (const [key, value] of Object.entries(data.choices || {})) if (typeof value === 'boolean') draft.choices[key] = value;
  for (const block of template.blocks) if (block.kind === 'table' && block.repeatable) {
   const rows = data.rows?.[block.id];
   if (Array.isArray(rows) && rows.length && rows.length <= 100 && rows.every(r => typeof r === 'string' && /^[a-zA-Z0-9-]+$/.test(r)) && new Set(rows).size === rows.length) draft.rows[block.id] = rows;
  }
  draft.handover = data.handover === true;
  draft.secondPoint = data.secondPoint === true;
  draft.purpose = data.purpose === 'damage' ? 'damage' : 'support';
  return draft;
 } catch { return null; }
}
