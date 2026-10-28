# PDF fonts

Noto Sans and Noto Sans Devanagari regular/bold are bundled for completed form PDFs. The editor fetches them only when someone requests a PDF. All files use the SIL Open Font License in `OFL.txt`.

Source: https://github.com/notofonts/noto-fonts/tree/main/hinted/ttf (retrieved 28 October 2026).

The exact cmap intersection of each regular/bold pair is recorded in `src/content/pdf-font-coverage.json`. PDF text selects a font for each complete Unicode grapheme. Unsupported text triggers an explicit print/Word fallback instead of silently replacing characters. Do not substitute font files without updating that coverage file and testing the export.
