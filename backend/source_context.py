"""Attach existing, exact source chunks that explain a selected table fragment.

No source text, offsets, IDs or catalogue metadata are rewritten. A preceding
caption is useful only when its actual column header is in the same indexed
chunk. Cross-page and ambiguous layouts are deliberately not reconstructed.
"""
import re


CAPTION = re.compile(
    r'^[ \t]*Table\s*[-–.]?\s*(?:\d+(?:[.\-]\d+)*|[IVX]+|[A-Z])'
    r'(?=\s|[:.\-–]|$)\s*[:.\-–]?[^\n]{0,180}$', re.I | re.M)
ROW = re.compile(r'^\s*\d+[.)]?\s{2,}\S')


def tabular_lines(text):
    """Require repeated aligned columns; a single spaced prose line is not a table."""
    return [line for line in text.splitlines()
            if len(re.split(r'\t+| {2,}', line.strip())) >= 2
            and (ROW.match(line) or len(re.findall(r'\S', line)) >= 12)]


def preceding_prose_chunk(page_text, start, end, chunks):
    """Carry an existing overlapping predecessor for a mid-sentence fragment.

    A fragment such as 'from Goa. Out of these...' cannot establish the subject
    of its own count. Keep the preceding original chunk as citable context,
    never reconstruct a sentence or guess an antecedent from a document title.
    """
    text = page_text[start:end].lstrip()
    if not start or not text:
        return None
    if not (text[0].islower() or text[0] in '.,;:)' or re.match(r'^(These|Those|They|Their|This|Such|It)\b', text)):
        return None
    candidates = [chunk for chunk in chunks
                  if chunk['start'] < start < chunk['end']
                  and chunk['text'] == page_text[chunk['start']:chunk['end']]]
    return max(candidates, key=lambda chunk: chunk['start'], default=None)


def preceding_table_chunk(page_text, start, end, chunks):
    """Return one existing header-bearing chunk, never a guessed column label.

Only an explicit same-page caption before the selected, visibly tabular text
qualifies. Require the caption and first data row in one chunk so that the
intervening original header is supplied too. A later section heading breaks the
association. The bounded source chunk remains independently citable.
"""
    selected = page_text[start:end]
    if len(tabular_lines(selected)) < 2:
        return None
    captions = [match for match in CAPTION.finditer(page_text[:end]) if match.start() < start]
    if not captions:
        return None
    caption = captions[-1]
    first_row = None
    first_row_start = None
    first_row_columns = None
    offset = caption.end()
    for line in page_text[caption.end():].splitlines(keepends=True):
        if ROW.match(line):
            first_row_start = offset
            first_row = offset + len(line)
            first_row_columns = len(re.split(r'\t+| {2,}', line.strip()))
            break
        offset += len(line)
        if offset - caption.start() > 1600:
            return None
    if first_row is None or first_row > end:
        return None
    # The caption alone cannot define an unlabeled column. Require an actual
    # aligned, textual header row covering at least the first data row's fields.
    # Wrapped or number-only headers remain ambiguous rather than guessed.
    header_rows = [re.split(r'\t+| {2,}', line.strip())
                   for line in page_text[caption.end():first_row_start].splitlines()]
    row_columns = [len(re.split(r'\t+| {2,}', line.strip()))
                   for line in selected.splitlines() if ROW.match(line)]
    required_columns = max([first_row_columns, *row_columns])
    if not any(len(cells) >= required_columns >= 2
               and all(any(char.isalpha() for char in cell) for cell in cells)
               for cells in header_rows):
        return None
    # Carry a header only through uninterrupted numbered rows with the same
    # column count. Any intervening prose, heading (in any case), numbered
    # section or wrapped/partial row is ambiguous and stops the association.
    for line in page_text[first_row:start].splitlines():
        if line.strip() and (not ROW.match(line)
                or len(re.split(r'\t+| {2,}', line.strip())) != first_row_columns):
            return None
    candidates = [chunk for chunk in chunks
                  if chunk['start'] <= caption.start() + len(caption.group()) - len(caption.group().lstrip())
                  and chunk['end'] >= first_row
                  and chunk['text'] == page_text[chunk['start']:chunk['end']]]
    if not candidates:
        return None
    chosen = min(candidates, key=lambda chunk: chunk['end'] - chunk['start'])
    if chosen['start'] == start and chosen['end'] == end:
        return None
    return chosen


def with_source_context(primary):
    """Flatten source context atomically while retaining all original passages."""
    selected = []
    known = {}
    for hit in primary:
        item = {key: value for key, value in hit.items() if key != 'supporting_context'}
        context = hit.get('supporting_context', [])
        if context:
            item['context_ids'] = [entry['id'] for entry in context if entry['id'] != hit['id']]
        selected.append(item)
        known[item['id']] = item
    for hit in primary:
        for context in hit.get('supporting_context', []):
            # A context from another document/version cannot qualify this hit.
            if any(context.get(key) != hit.get(key) for key in ('document_id', 'generation', 'page')):
                raise ValueError('Source context identity differs from its passage')
            if context['id'] in known:
                if any(context.get(key) != known[context['id']].get(key)
                       for key in ('document_id', 'generation', 'page', 'start', 'end', 'text')):
                    raise ValueError('Source context ID has conflicting text or locators')
                continue
            item = {key: value for key, value in context.items() if key != 'supporting_context'}
            selected.append(item)
            known[item['id']] = item
    return selected
