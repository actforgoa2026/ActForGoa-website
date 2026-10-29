"""Regression cases from the retained source, including native rotated cells."""
from collections import Counter
from pathlib import Path

import pymupdf
import pytest

from scripts.extract_sapcc import extract, read_half

SOURCE = Path(__file__).resolve().parents[2] / 'docs/climate/goa-sapcc-2023-2033.pdf'


@pytest.mark.parametrize('number', [1, 13, 38, 42, 44, 72, 76, 83])
def test_spreads_preserve_every_native_character_once(number):
    with pymupdf.open(SOURCE) as pdf:
        page = pdf[number - 1]
        halves = [pymupdf.Rect(0, 0, page.rect.width / 2, page.rect.height),
                  pymupdf.Rect(page.rect.width / 2, 0, page.rect.width, page.rect.height)]
        text = '\n'.join(read_half(pdf, number - 1, clip)[0] for clip in halves)
        assert Counter(c for c in text if not c.isspace()) == Counter(
            c for c in page.get_text('text', sort=False) if not c.isspace())
        assert ' ' * 20 not in text
        if number == 42:
            row = next(line.split('\t') for line in text.splitlines() if '300 MW of solar' in line)
            assert row[:4] == ['4', '300 MW of solar to be set up by 2030', 'proposed', 'GEDA']
            assert 'Rs. 10 crores per annum' in row
            assert '10 years' in row


def test_extractor_rejects_a_different_edition(tmp_path):
    wrong = tmp_path / 'wrong.pdf'
    wrong.write_bytes(b'not the reviewed edition')
    with pytest.raises(ValueError, match='reviewed only'):
        extract(wrong)
