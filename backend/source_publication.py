"""A year label from explicit supplied publication metadata, not source verification."""
from datetime import date
import re


PUBLICATION_FIELDS = frozenset({
    'prism.publicationDate', 'citation_online_date',
    'citation_publication_date', 'datePublished',
})
DATE = re.compile(r'([0-9]{4})(?:([-\/])([0-9]{2})\2([0-9]{2}))?\Z')


def publication_context(metadata):
    """Keep unknown provenance unknown; never use titles or retrieval/upload dates.

    A year-only label tolerates different dates in the same year. Malformed or
    conflicting recognized values remain unresolved, even alongside a valid one.
    The raw metadata stays in the evidence payload unchanged.
    """
    if not isinstance(metadata, list):
        return None
    values = [item.get('value') for item in metadata
              if isinstance(item, dict) and isinstance(item.get('field'), str)
              and item['field'] in PUBLICATION_FIELDS]
    if not values:
        return None
    years = set()
    for value in values:
        match = DATE.fullmatch(value) if isinstance(value, str) else None
        try:
            if match is None:
                raise ValueError()
            year = int(match[1])
            date(year, int(match[3] or 1), int(match[4] or 1))
        except ValueError:
            return {'year': None, 'label': 'Source publication year unresolved: invalid metadata.'}
        years.add(year)
    if len(years) != 1:
        return {'year': None, 'label': 'Source publication year unresolved: conflicting metadata.'}
    year = years.pop()
    return {'year': year, 'label': f'Source publication year: {year:04d} (source metadata).'}
