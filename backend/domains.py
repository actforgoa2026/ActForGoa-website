"""Conservative library sections; a section label is not legal verification."""
import re
from typing import Literal

Domain = Literal['all', 'legal', 'ecology']
LEGAL_WORDS = re.compile(r'\b(?:law|laws|legislation|legal|act|rules|regulations|notification|gazette|rti|panchayat|permission|court|tribunal)\b', re.I)
ECOLOGY_WORDS = re.compile(r'\b(?:ecology|ecological|ecosystem|biodiversity|wildlife|habitat|wetland|mangrove|forest|river|water|khazan|laterite|plateau|environment|environmental|climate|coastal|agriculture|farming|animal)\b', re.I)


def document_domains(metadata):
    explicit = metadata.get('domains')
    if isinstance(explicit, list):
        return [domain for domain in ('legal', 'ecology') if domain in explicit]
    # Old immutable generations remain queryable without writing to their indexes.
    description = ' '.join(str(metadata.get(key) or '') for key in ('title', 'topics', 'document_kind_hint'))
    domains = []
    if metadata.get('guide_verification') or LEGAL_WORDS.search(description):
        domains.append('legal')
    if metadata.get('ecology_source') or ECOLOGY_WORDS.search(description):
        domains.append('ecology')
    return domains


def legal_authority_multiplier(metadata, domain):
    # Only reorder already relevant results; official does not mean current.
    return 1.15 if domain == 'legal' and metadata.get('publisher_class') == 'government_or_court' else 1.0
