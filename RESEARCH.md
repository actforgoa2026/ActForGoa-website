# ActForGoa research library

The `/ask` route searches the complete local corpus and can generate answers with page-level citations. `/documents/:id` opens the complete extracted source, jumps to the cited page, highlights its passage, and provides the original file and a full-text download. Search and reading work without an AI credential.

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

Cited answers default to GPT-5.6 Luna through OpenRouter. Set `RESEARCH_CHAT_PROVIDER=openrouter` and put `OPENROUTER_API_KEY` in the server environment or ignored `.env.local`. `OPENROUTER_CHAT_MODEL` defaults to `openai/gpt-5.6-luna`. Qwen 3.7/3.8 Flash remain explicit comparison options, not automatic fallbacks. Keep the key out of chat, Git, command arguments, screenshots and all `VITE_*` variables. Restart the API after configuration changes.

Create an OpenRouter account, add a small prepaid balance, and create a dedicated ActForGoa key with a $5 monthly limit. Keep automatic top-ups off during evaluation. Put the key in Railway → actforgoa-reports → production → research → Variables as `OPENROUTER_API_KEY`. This research service is separate from the reporting service. Alibaba direct registration currently excludes India; OpenRouter avoids needing an individual Alibaba account.

The OpenRouter endpoint is fixed to `https://openrouter.ai/api/v1`. The selected model routes to OpenAI only, requires strict JSON-schema output, denies providers that collect data, disables fallbacks, uses low reasoning, and enforces reviewed token prices ($0.20 input / $1.20 output per million, verified 2026-10-26). Explicit Qwen configurations route to Alibaba with their own reviewed price ceilings; 3.7 supports JSON objects and 3.8 supports JSON schema. If those constraints cannot be met, the call fails with source search still available. Credit-purchase fees, tax, hosting and unrelated account usage are outside this inference budget.

`RESEARCH_MONTHLY_ANSWER_BUDGET_USD=5` and `RESEARCH_DAILY_ANSWER_LIMIT=100` cap model usage conservatively. Before dispatch, SQLite reserves the worst-case cost using a UTF-8 byte bound plus framing allowance and the 3,500-token completion cap (including reasoning; Qwen comparisons use 1,800). Failed requests retain their reservation. SDK retries and provider fallbacks are off. Reservations survive restarts and concurrent processes; the month resets in UTC. Set the monthly budget to zero to disable paid answers. Review price limits before changing model identifiers. Direct Alibaba (`RESEARCH_CHAT_PROVIDER=qwen`) and OpenAI (`RESEARCH_CHAT_PROVIDER=openai`) remain explicit alternatives; there is no automatic provider fallback.

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

The existing bundled `all-MiniLM-L6-v2` model runs locally through ONNX Runtime, limited to two CPU threads. Complete page text is split into overlapping 190-token passages without truncating page endings. Zvec cosine retrieval and SQLite FTS5 BM25 are combined by reciprocal rank fusion, then adjusted for question-concept coverage, with document diversity limits. Explicit legal queries receive a modest preference for government/court evidence among relevant candidates; this never establishes current legal force. Search supports an individual document/version scope and explicit Mhadei/Mahadayi/Mandovi aliases.

Answer context retains the page opening, publisher class, document-kind hint, legal-currency caveat, source-date metadata, guide-verification limitations and topics. Page context helps distinguish chapters of national reports; catalogue titles alone must not establish geographic scope. Tables with lost column alignment remain available in the reader, but the answer prompt excludes numerical claims derived from table fragments. Policies, proposals and historical observations must keep their dates and status.

`POST /api/chat` accepts `answer_style: "standard"` (default) or `"brief"`. Brief generation requests one paragraph without truncating text; answers retain per-paragraph citations and essential limitations; the server rejects more than two paragraphs or 120 words. They have separate cache keys. Invalid structure, invented citation IDs, incomplete output and overlong brief answers fail safely with source search still available; there are no automatic paid retries. Citation identity validation does not automatically establish factual support, so live claim review remains required.

Conversation, results, drafts and research mode are held only in application memory, separately for the whole collection and each document/version scope. Evidence links preserve a return path to that scope. Navigating through the app keeps this state; reloading or closing the tab clears it. No conversation is written to local storage.

The configured provider receives the question, bounded recent conversation and selected evidence. OpenRouter forwards them to Alibaba Qwen. Prompts are bounded below 24,000 UTF-8 bytes with extra framing allowance, and older history/lower-ranked passages are removed first. Qwen uses JSON-object output validated against a strict server-side schema; optional OpenAI Responses uses `store=False` and a structured schema. The server rejects empty or unknown citation IDs, supplies source links itself, and returns a clear error if output cannot be validated. Insufficient evidence produces an explicit abstention. These checks establish citation identity, not automated proof of factual entailment; the sources must still support the answer.

Validated answers without conversation history may be cached in server memory for ten minutes (up to 128 entries), keyed by the exact request, evidence, generation and model. History-bearing answers and errors are not cached. Cached answers do not make a paid request. The cache stores no disk data; expired entries are discarded on access or eviction.

The reader returns all extracted pages, including low-text pages, with notes. The Original page view renders the exact PDF page inside the reader; the full original is also downloadable as an attachment. Original PDFs preserve maps, figures, layout and tables. Physical PDF page numbers may differ from printed folios. Word sections are labelled as sections rather than invented page numbers. OCR is bounded, English-only and unverified; many historical scans still need review. Complex tables are not reconstructed as reliable measurements. Verify numerical relationships in the original document.

## Verification

```sh
npm test
npm run research:test
npm run build
.venv/bin/python scripts/evaluate_research.py
```

Backend tests exercise actual MiniLM and Zvec, immutable generations, page completeness, original checksums, unsafe path/host rejection and citation validation. Provider-contract tests use mocked HTTP transports through the real SDKs; they are not live-provider tests. They cover OpenRouter routing/price controls, citation rejection, malformed/truncated responses, safe provider failures, budget persistence/concurrency, prompt limits, cache isolation and document access. The actual-corpus evaluation checks top-five term coverage, passage offsets and every original checksum. It is a smoke test rather than an answer-quality benchmark. The report records its generation.

For live answer validation, configure a funded key, start the API against the real corpus, then run:

```sh
.venv/bin/python scripts/evaluate_live_chat.py --origin http://127.0.0.1:8091 --output reports/research-live-chat.json
```

This sends up to 50 real Goa questions and invokes the paid model. It verifies citation passage identity, reader endpoints, full text and original checksums, and records answers/evidence for human review. A passing mechanical check is not proof that each claim follows from its citation. Review supported claims, geographic scope, dates, uncertainty and appropriate abstention before enabling public answers. An unavailable key is a blocker for live testing, never a passed result.

References: [OpenRouter model pricing](https://openrouter.ai/qwen/qwen3.7-flash), [provider routing](https://openrouter.ai/docs/guides/routing/provider-selection), [fees](https://openrouter.ai/docs/faq), [Alibaba registration FAQ](https://www.alibabacloud.com/help/ja/account/step-1-register-an-alibaba-cloud-account).

## Deployment boundary

The API defaults to local access. Hosted public access requires an exact HTTPS `RESEARCH_PUBLIC_ORIGIN` and `RESEARCH_PUBLISH_CORPUS=1`. This explicit publication flag enables public source access, not authentication. Deploy the API separately from the Vercel frontend and from the reporting service, with one worker and one replica, a persistent data volume, exact allowed hosts, bounded request bodies/concurrency, aggregate search limits and a persistent daily answer-attempt limit. See `deploy/research/README.md`. Raw files are not copied into `public/` or `dist/`. Archived HTML is downloaded as an attachment under a sandbox policy, never rendered as trusted application HTML.

Public availability does not establish redistribution rights. The corpus preserves available rights metadata; unknown rights remain unknown. Historical legislation is not asserted to be consolidated or current. The knowledge base should be reviewed and expanded as sources change.
