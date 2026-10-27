# ActForGoa research library

The `/ask` route searches the complete local corpus and can generate answers with page-level citations. `/documents/:id` opens the complete extracted source, jumps to the cited page, highlights its passage, and provides the original file and a full-text download. Search and reading work without an OpenAI credential.

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

Cited answers use the server's `OPENAI_API_KEY` from the process environment or the ignored `.env.local`. Use the secure OpenAI Platform setup flow to provision it. No credential belongs in a `VITE_*` variable or the browser. `OPENAI_CHAT_MODEL` defaults to `gpt-5-mini` and must support Responses structured outputs. Restart the API after configuring a key or publishing a new index.

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

OpenAI receives the question, bounded recent conversation and selected evidence. Responses use `store=False` and a structured schema. The server rejects empty or unknown citation IDs, supplies source links itself, and returns a clear error if output cannot be validated. Insufficient evidence produces an explicit abstention. These checks establish citation identity, not automated proof of factual entailment; the sources must still support the answer.

The reader returns all extracted pages, including low-text pages, with notes. The Original page view renders the exact PDF page inside the reader; the full original is also downloadable as an attachment. Original PDFs preserve maps, figures, layout and tables. Physical PDF page numbers may differ from printed folios. Word sections are labelled as sections rather than invented page numbers. OCR is bounded, English-only and unverified; many historical scans still need review. Complex tables are not reconstructed as reliable measurements. Verify numerical relationships in the original document.

## Verification

```sh
npm test
npm run research:test
npm run build
.venv/bin/python scripts/evaluate_research.py
```

Backend tests exercise actual MiniLM and Zvec, immutable generations, page completeness, original checksums, unsafe path/host rejection and citation validation. One test uses a mocked OpenAI HTTP transport through the real Responses SDK; it is not a live-provider test. The actual-corpus evaluation checks top-five term coverage, passage offsets and every original checksum. It is a smoke test rather than an answer-quality benchmark. The report records its generation.

## Deployment boundary

This is a local service, not a production deployment. Host checks, loopback binding and same-origin request checks are deliberately local. A hosted deployment needs authenticated access, persistent storage, backups, operational limits and a review of redistribution rights for each source before exposing saved originals. Raw files are not copied into `public/` or `dist/`. Archived HTML is downloaded as an attachment under a sandbox policy, never rendered as trusted application HTML.

Public availability does not establish redistribution rights. The corpus preserves available rights metadata; unknown rights remain unknown. Historical legislation is not asserted to be consolidated or current. The knowledge base should be reviewed and expanded as sources change.
