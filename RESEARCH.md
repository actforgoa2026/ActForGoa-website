# ActForGoa research library

The `/ask` route searches the complete local corpus and can generate answers with page-level citations. `/documents/:id` opens the complete extracted source, jumps to the cited page, highlights its passage, and provides the original file and a full-text download. Search and reading work without a model credential. `/ask/legal` and `/ask/ecology` use separate library sections.

## Run locally

Use Python 3.12 on macOS ARM64 or a platform supported by Zvec and ONNX Runtime.

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-research.txt
npm ci
npm run research:ingest
npm run research:index
npm run research:dev
```

Open http://127.0.0.1:4174/ask. The API listens only on 127.0.0.1:8091; Vite proxies `/api`. Both processes stop when the launcher exits. For an existing archive, ingestion reuses saved successful responses; `scripts/ingest_ecology.py --retry-failed` retries only transient transport failures. It preserves access denials and certificate failures.

The original corpus must be present in `corpus/`. `scripts/ingest_goa_corpus.py` also supports additional curated seed files. The checked-in ecology manifest can reproduce the accessible ecology subset; the broader archive has its own seed lists. Raw data is intentionally excluded from Git and the frontend build.

Cited answers use the server-only `ANTHROPIC_API_KEY` and `RESEARCH_CHAT_ENABLED=1`. `ANTHROPIC_CHAT_MODEL` defaults to the previously reviewed `claude-haiku-5-5`; model availability and answer quality still need a live-provider check before activation. Credentials never belong in `VITE_*`, browser code or Git. Restart after configuring a key or publishing an index. The public service requires its existing usage ledger by default; missing volume/accounting data keeps answers disabled instead of creating a fresh allowance.

To add the canonical authored legal guides to a restored corpus, run `python scripts/ingest_legal_guides.py --data-root /path/to/restored-data`, then rebuild with `python scripts/build_research_index.py --data-root /path/to/restored-data`. They are explicitly draft commentary, not primary legislation. The separate `refresh_verified_legal_sources.py` reconciles the verified official originals only when their actual bytes and metadata are available. See [cloud handoff](docs/RESEARCH-CLOUD-HANDOFF.md).

## What is stored

- `corpus/raw/`: original response bytes named by SHA-256. PDFs, Word files and HTML remain separate from extracted text.
- `corpus/metadata/`, `pages/`, `text/`, `ocr/`: provenance, native text, physical PDF page locations, existing OCR and extraction flags.
- `corpus/extracted/`: improved extraction snapshots keyed by original checksum and extraction version. Remove a specific cached extraction to deliberately retry its OCR; existing index generations remain immutable.
- `corpus/ecology-seeds.json`: primary and supporting sources from the ecological research, plus two verified full-text alternatives.
- `corpus/ecology-research-snapshot.json`: the editorial research report, retained for context and not indexed as primary evidence.
- `corpus/ecology-ingestion-report.json`: successful downloads and explicit failures. A downloaded webpage may be an abstract or index, not a full paper.
- `.research-index/generations/<version>/`: SQLite documents, pages, chunks and FTS5; Zvec vectors; manifest and extraction failures.
- `.research-index/embeddings.sqlite`: reusable embedding cache. `.research-index/CURRENT.json` is switched atomically only after a complete build.

Keep original bytes, extraction snapshots and index generations together in backups. Old citation links include an index generation and document-content version; deleting that generation invalidates those links. Never edit a published generation in place. Rebuild and restart the API to publish updates. Only one index builder should run for a given index directory at once.

## Retrieval and answers

The existing bundled `all-MiniLM-L6-v2` model runs locally through ONNX Runtime, limited to two CPU threads. Complete page text is split into overlapping 190-token passages without truncating page endings. Zvec cosine retrieval and SQLite FTS5 BM25 are combined by reciprocal rank fusion, with document diversity limits. Search supports an individual document/version scope and explicit Mhadei/Mahadayi/Mandovi aliases.

Conversation, results, drafts and research mode are held only in application memory, separately for the whole collection and each document/version scope. Evidence links preserve a return path to that scope. Navigating through the app keeps this state; reloading or closing the tab clears it. No conversation is written to local storage.

Anthropic receives the question, bounded recent conversation and selected evidence in one Messages request, with no automatic retries. Library answers are concise synthesis: every cited paragraph must provide an exact supporting source quote, and all citation IDs/quote bytes are checked locally. At most 180 words of library answer and 80 words of outside context are accepted. These checks establish citation identity and quoted support, not automated proof of semantic entailment; live answer-quality review remains necessary.

When library coverage is incomplete, optional general AI context is returned in a separate `outside_context` object with `provenance: model_knowledge`. It is not a web search and is never presented as a verified external source. A fully supported library answer cannot include outside context. Requests can disable it entirely. Specific outside-library legal duties, deadlines, current officeholders and contact details are prohibited in the provider instructions.

Domain filtering occurs before both Zvec and FTS5 candidate retrieval. Explicit domain metadata takes precedence; legacy generations use conservative title/topic/provenance classification without rewriting their bytes. The status endpoint reports the actual domain document counts, not a claim of exhaustive coverage. Primary official evidence receives a small relevance-bounded preference within legal search; this does not establish legal currency.

The same persistent `.research-usage/answer-usage.sqlite` ledger reserves each provider attempt before dispatch, with a unique receipt, a hard maximum of 100 attempts per UTC day and $5 of conservative reserved cost per month. Failure and validation rejection do not refund reservations. Existing reservations and reconciliation tables are preserved.

The reader returns all extracted pages, including low-text pages, with notes. The Original page view renders the exact PDF page inside the reader; the full original is also downloadable as an attachment. Original PDFs preserve maps, figures, layout and tables. Physical PDF page numbers may differ from printed folios. Word sections are labelled as sections rather than invented page numbers. OCR is bounded, English-only and unverified; many historical scans still need review. Complex tables are not reconstructed as reliable measurements. Verify numerical relationships in the original document.

## Verification

```sh
npm test
npm run research:test
npm run build
.venv/bin/python scripts/evaluate_research.py
```

Backend tests exercise actual MiniLM and Zvec, immutable generations, page completeness, original checksums, unsafe path/host rejection and citation validation. Provider contract tests use an HTTP mock for the native Anthropic adapter; they are not live-provider tests. Domain tests use real MiniLM/Zvec indexes and temporary fixture ledgers. The actual-corpus evaluation checks top-five term coverage, passage offsets and every original checksum. It is a smoke test rather than an answer-quality benchmark. The report records its generation.

## Deployment boundary

The API defaults to local access. Hosted public access requires an exact HTTPS `RESEARCH_PUBLIC_ORIGIN` and `RESEARCH_PUBLISH_CORPUS=1`. This explicit publication flag enables public source access, not authentication. Deploy the API separately from the Vercel frontend and from the reporting service, with one worker and one replica, a persistent data volume, exact allowed hosts, bounded request bodies/concurrency, aggregate search limits and a persistent daily answer-attempt limit. See `deploy/research/README.md`. Raw files are not copied into `public/` or `dist/`. Archived HTML is downloaded as an attachment under a sandbox policy, never rendered as trusted application HTML.

Public availability does not establish redistribution rights. The corpus preserves available rights metadata; unknown rights remain unknown. Historical legislation is not asserted to be consolidated or current. The knowledge base should be reviewed and expanded as sources change.
