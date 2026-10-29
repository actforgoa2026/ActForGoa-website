"""Read the verified two-page Goa SAPCC without interleaving its book pages.

Only native PDF text is used. Table cells retain their column positions; no
missing headings, OCR, financial totals or cross-page rows are reconstructed.
The saved original is never modified, and locators remain physical PDF pages.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import pymupdf

SOURCE_SHA256 = 'd1b64d562f93c9cbabc39e1d4be65f0515a06734792cfa5ea4eebf9544ff3cc6'
VERSION = 'goa-sapcc-native-spreads-v1'


def clean(text):
    return re.sub(r'\s+', ' ', text).strip()


def read_half(document, number, clip):
    source = document[number]
    lines = [line for block in source.get_text('dict', clip=clip)['blocks']
             for line in block.get('lines', [])]
    direction = Counter(tuple(line['dir']) for line in lines).most_common(1)
    rotate = {(0., -1.): 270, (0., 1.): 90, (-1., 0.): 180}.get(direction[0][0], 0) if direction else 0
    with pymupdf.open() as temporary:
        width, height = (clip.height, clip.width) if rotate in (90, 270) else (clip.width, clip.height)
        page = temporary.new_page(width=width, height=height)
        page.show_pdf_page(page.rect, document, number, clip=clip, rotate=rotate)
        tables = [table for table in page.find_tables().tables if table.row_count > 1 and table.col_count > 1]
        # A nested grid can be reported as a second table. Keep its outer grid.
        tables = [table for table in tables if not any(
            other is not table and pymupdf.Rect(table.bbox) in pymupdf.Rect(other.bbox)
            and pymupdf.Rect(table.bbox).get_area() < pymupdf.Rect(other.bbox).get_area() for other in tables)]
        lines = [line for block in page.get_text('rawdict')['blocks'] for line in block.get('lines', [])]
        used = set()

        def take_text(rect):
            result = []
            for i, line in enumerate(lines):
                characters = []
                for j, span in enumerate(line['spans']):
                    for k, char in enumerate(span['chars']):
                        box = pymupdf.Rect(char['bbox'])
                        centre = pymupdf.Point((box.x0 + box.x1) / 2, (box.y0 + box.y1) / 2)
                        if (i, j, k) not in used and centre in rect and centre in page.rect:
                            characters.append(char['c'])
                            used.add((i, j, k))
                if characters:
                    result.append(''.join(characters))
            return clean(' '.join(result))

        events = []
        for table in tables:
            rows = []
            for row in table.rows:
                # Assign native characters by their centres exactly once, so a
                # glyph crossing a cell border cannot appear in both cells.
                rows.append('\t'.join(take_text(pymupdf.Rect(cell)) if cell else ''
                                      for cell in row.cells))
            events.append((table.bbox[1], table.bbox[0], '\n'.join(rows)))
        for i, line in enumerate(lines):
            box = pymupdf.Rect(line['bbox'])
            text = clean(''.join(char['c'] for j, span in enumerate(line['spans'])
                                for k, char in enumerate(span['chars']) if (i, j, k) not in used
                                and pymupdf.Point((char['bbox'][0] + char['bbox'][2]) / 2,
                                                  (char['bbox'][1] + char['bbox'][3]) / 2) in page.rect))
            if text:
                # Keep the book footer out of the middle of a sideways table.
                y = box.y0 if tuple(line['dir']) == (1., 0.) else page.rect.height + box.y0
                events.append((y, box.x0, text))
        return '\n'.join(text for _, _, text in sorted(events)), rotate, len(tables)


def extract(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('This extractor is reviewed only for the retained SAPCC edition')
    pages = []
    with pymupdf.open(stream=raw, filetype='pdf') as document:
        if len(document) != 111:
            raise ValueError('Unexpected source page count')
        for index, page in enumerate(document):
            halves = [pymupdf.Rect(0, 0, page.rect.width / 2, page.rect.height),
                      pymupdf.Rect(page.rect.width / 2, 0, page.rect.width, page.rect.height)]
            parts = [read_half(document, index, half) for half in halves]
            text = '\n\n'.join(part[0] for part in parts)
            number = index + 1
            warning = ('Native text from two printed pages, read left then right. '
                       'Table cells are separated by tabs; blank cells are retained. '
                       'Rows continuing across pages are not reconstructed. Check the original for tables and figures.')
            if 99 <= number <= 110:
                warning = 'Scanned committee minutes: native text is incomplete; these pages are not answer evidence. Read the original page image.'
            elif sum(character.isalnum() for character in text) < 100:
                warning = 'Little native text; this may be an image or cover. Check the original page.'
            pages.append({'page': number, 'label': f'PDF page {number}', 'text': text,
                          'origin': VERSION, 'warning': warning,
                          'rotated_halves': sum(bool(part[1]) for part in parts),
                          'tables': sum(part[2] for part in parts)})
    return pages


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    pages = extract(args.pdf)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pages': len(pages), 'tables': sum(p['tables'] for p in pages),
                      'rotated_halves': sum(p['rotated_halves'] for p in pages), 'version': VERSION}))
