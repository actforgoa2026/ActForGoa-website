# Act for Goa research corpus

Public-source ingestion snapshot started on 22 October 2026. This collection supports later work on practical resources for people in Goa: building and land, farming, animals, pollution, coastal and wetland protection, forests, complaints, information rights and civic participation.

Snapshot: 1,155 included source records, including 686 distinct original PDF files (705 PDF source URLs). Included records comprise 330 from Act for Goa, 754 from government/court publishers, 51 from public research institutions, and 20 from other public publishers. A further 134 source URLs failed retrieval and 67 downloaded pages/files were excluded from research search. See `stats.json` for generated counts. This is not an exhaustive legal completeness claim.

This is an evidence collection. It is not a consolidated statement of current law. Individual files may be originals, amendments, draft proposals, historical compilations, policies, service guidance, judgments, commentary or reporting. A recent website upload does not establish that the law in a document is current. Document and topic classifications are retrieval aids that require editorial review.

## Start here

- `guides/README.md`: five practical guides covering reporting, building, farming, animal welfare and environmental protection, 17 reusable templates, sources and a verification register.

- `research/GAP_ANALYSIS.md`: comparison with the fuller Act for Goa website archive, ranked practical-guide gaps and an editorial work plan.
- `research/gap-review/review.json`: record-level evidence supporting the gap assessment.

- `stats.json`: generated counts, including failed and excluded records.
- `catalog.csv`: a spreadsheet-readable catalogue.
- `catalog.jsonl`: full machine-readable catalogue, one source URL per record.
- `research/coverage.json`: topic coverage and review gaps.
- `research/SOURCE_MAP.md`: a readable topic map with links to local originals and the editorial review queue.
- `research/external-additions.json`: external sources compared against direct links and identical files in the captured Act for Goa material. This measures collection additions, not semantic absence from the website.
- `research/validation.json`: file integrity and search checks.
- `research/failures.json`: downloads that failed, with the actual error.
- `search.sqlite`: local full-text search with document and physical PDF page references.

Validation passed for original-file checksums, extracted-text checksums, PDF page sequences and SQLite integrity. Eight subject searches returned results. Native extraction flagged 210 PDFs as requiring OCR; a supplementary single-worker pass attempted 65 pages across 58 documents and produced text on 61 pages. This does not complete scan transcription or legal verification.

## File layout

| Location | Contents |
| --- | --- |
| `raw/` | Original downloaded response bodies, named by SHA-256. Identical content shares the same file. HTTP error bodies are retained as evidence and excluded from usable sources. |
| `metadata/` | One JSON record per canonical source URL, including source URL, final URL, redirects, retrieval time in UTC, MIME type, HTTP status, checksums, local paths, discovery context, publisher classification and extraction caveats. |
| `text/` | Derived native PDF text, HTML body text, or DOCX main-document text. These are not corrected transcripts. |
| `pages/` | PDF text broken down by physical file page, preserving empty pages and extraction errors. Printed page labels may differ. |
| `ocr/` | Additional OCR, if performed, kept separate from native extraction. OCR is machine generated and not a verified legal transcript. |
| `research/` | Search-discovery snapshots, a snapshot of the existing Act for Goa archive, coverage, duplicate hashes, review gaps and validation results. Search snippets are discovery evidence, not downloaded originals. |
| `logs/` | Append-only fetch, robots-policy and link-discovery evidence, plus ingestion run logs. |
| `seeds*.json` | Explicit starting URLs and their research purpose; reproducible crawl inputs. |

Public government/court sources, intergovernmental repositories, research institutions, Act for Goa, civil-society material and journalism have distinct publisher labels. Hosting by a government does not by itself make a document legally operative. A civil-society-hosted court document retains the provenance of that host.

## Search locally

Run from `/Users/zakkrevitt/code/ActForGoa`:

```sh
.venv/bin/python scripts/search_goa_corpus.py 'khazan OR tenancy'
.venv/bin/python scripts/search_goa_corpus.py '"birth control"' --limit 5
.venv/bin/python scripts/search_goa_corpus.py '"coastal regulation"'
```

Search results return the source URL, local original/text paths, publisher class and physical PDF page. Search uses SQLite FTS5. It does not send the corpus to an AI service. Always inspect the original before quoting a clause, using a table, or relying on a map. Different URLs for an identical document may appear as separate source records; `research/duplicate-content.json` lists these groups.

## Reproduce and extend

```sh
.venv/bin/python scripts/ingest_goa_corpus.py --seeds corpus/seeds.json --depth 2 --limit 650
.venv/bin/python scripts/ingest_goa_corpus.py --seeds corpus/seeds-supplement.json --depth 1 --limit 360 --child-documents-only
.venv/bin/python scripts/ingest_goa_corpus.py --seeds corpus/seeds-priority.json --depth 1 --limit 400 --child-documents-only
.venv/bin/python scripts/curate_goa_corpus.py
```

The downloader uses public read-only GET requests, verifies TLS, checks robots directives, throttles each host, limits individual response bodies to 80 MiB, and records failures. It does not log into websites or submit complaints, requests or payments. Successful existing downloads are reused. `--retry` explicitly refetches the supplied seed set, including failures; use a small reviewed seed file when refreshing. The fetch log preserves earlier attempts. Raw files remain content addressed; the current per-URL metadata points at the most recently fetched version.

`--actforgoa` imports the then-current public WordPress archive under `data/wordpress.json`. This corpus has its own snapshot and does not modify the separate site migration archive. Web templates, technical import logs and insufficient-content pages are excluded from the research search index while their provenance is retained.

## Reading boundaries

- Confirm commencement, amendments, repeal, court stays, appeals and territorial applicability before presenting current legal guidance. No automatic legal consolidation was attempted.
- Goa has statewide, district, taluka, municipal, village and site-specific rules. A national rule or a law hosted by another state is not proof of the applicable local permission process.
- CRZ/CZMP, zoning maps, private forests and notified wetland boundaries need location-specific checking. Text extraction cannot establish a plot's classification.
- Old contact details, scheme amounts, eligibility and service availability are source evidence, not independently verified present-day services.
- Native PDF extraction can lose columns, tables, footnotes, glyphs and reading order. Low-text pages may be scans, maps or genuinely blank. OCR remains unverified and can misread section numbers and dates.
- English, Hindi, Konkani, Marathi and other source text is preserved as obtained. No translation or comprehensive language review was performed.
- Downloadable originals, usable native text, and legally verified guidance are different completion states. Failed URLs, extraction gaps and additional discovery candidates remain explicitly visible.
- This is a local research collection. Raw source files remain local; licensing clearance for their public republication has not been performed. The authored guide drafts are integrated into the separate field-guide review website with official source links and verification flags.
