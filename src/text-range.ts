export type TextRangeParts = { before: string; selected: string; after: string };

/**
 * Split a Python text[start:end] range: zero-based Unicode code points, end exclusive.
 * These are neither UTF-16 code units nor grapheme indices. Never normalize source text.
 * Invalid or empty spans return null so callers can show the complete unmarked source.
 */
export function splitCodePointRange(text: string, start: unknown, end: unknown): TextRangeParts | null {
  if (typeof start !== 'number' || typeof end !== 'number'
    || !Number.isSafeInteger(start) || !Number.isSafeInteger(end)
    || start < 0 || end <= start) return null;

  let point = 0;
  let offset = 0;
  let left = 0;
  for (const character of text) {
    if (point === start) left = offset;
    offset += character.length;
    point++;
    if (point === end) {
      return { before: text.slice(0, left), selected: text.slice(left, offset), after: text.slice(offset) };
    }
  }
  return null;
}
