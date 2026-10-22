# Architecture and functionality

## A source-backed catalogue

The original site is WordPress with custom resource and portfolio types, Connections directory entries, donation/contact plugins, old shop/template pages, a newer community area, and a large media library. The new interface reads a derived catalogue; it does not require the original plugins to render successfully.

Raw bytes and metadata are saved first. Extraction is repeatable and keeps original content separate from UI copy. The public catalogue stores title, type, source URL, public API URL where available, source status, dates, text blocks, topics, contacts, locations, document links, images, and verification status. All imported contacts are `source-listed-unverified`.

## Tables

| Table | Purpose |
| --- | --- |
| `records` | Canonical searchable entries and source provenance |
| `contacts` | Phone/email values and safe action URLs, linked to a source record |
| `documents` | Original document URL, retrieval status, archive path, extracted text path |
| `record_topics` | Many-to-many presentation topics |
| `search` | SQLite FTS5 over complete extracted text and topics |

The JSON files additionally preserve original WordPress taxonomies and source link edges. `forms.json` inventories form fields and actions without submitting them. `page-inventory.json` covers HTML responses including errors and non-migrated pages.

## Search

1. Weighted lexical ranking prioritises titles, then body text; source contacts and document text are included.
2. Explicit, reviewable intent expansions connect everyday language such as rubbish to waste/recycling, and snake to rescue/wildlife.
3. [MiniLM sentence embeddings](https://huggingface.co/Xenova/all-MiniLM-L6-v2) retrieve related passages by cosine similarity. The quantized model, tokenizer, runtime and index are served from the same deployment. [Transformers.js](https://huggingface.co/docs/transformers.js/api/pipelines) runs it in a worker.
4. Results below the semantic threshold are discarded; qualifying results combine semantic and lexical scores. No generated answer is presented as fact.
5. Filtering and grid/list presentation operate over the same set of records. Query and filter state live in the URL. Queried Everything results are grouped into people/organisations, guides/reading, stories/projects and about/action. Ranking is preserved within groups; groups appear in the order of their strongest result. Initially six results per group are shown, with load-more expansion. Ungrouped views initially show 24 records.

Documents are embedded in overlapping 160-word passages, with a maximum of 3,200 indexed words per record/document aggregate. This is a preview performance boundary, not full-document semantic coverage. The full extracted text remains in the archive and SQLite FTS5 index. A future server-side search service should index every passage, include editorial confidence/recency weighting, use an evaluation set, and support language-specific retrieval.

The model is downloaded on first search and retained by browser caching where available. Keyword results are immediately usable. Worker failures show the keyword fallback; stale worker responses are ignored. This is semantic retrieval, not a generative chatbot.

## Pages

- `/`: search-first field guide, starter queries, topics, practical guides, community spotlight.
- `/search`: all record kinds, topic and type filters, semantic and keyword ranking.
- `/directory`: 104 organisations and 49 source-listed rescue contacts; list/grid views.
- `/library`: 237 civic resources.
- `/stories`: 138 stories and projects.
- `/read/:id`: readable source text, original date, contacts, documents, links and correction path.
- `/about`: original organisational content, annual reports/press links, and preview/source explanation.
- `/get-involved`: original participation paths and email preparation.
- `/contact`: reviewable email preparation with a correction context when opened from a record.

## Editorial separation

Topics are automatically derived and need editorial review. They are presentation metadata, not an assertion that an organisation provides every associated service. Some source content makes historical availability or efficacy claims; the interface labels source dates and unverified contacts. No new telephone number, organisation, location coordinate, testimonial, or impact statistic was invented.

Short local telephone numbers remain text; only complete Indian numbers receive `tel:` actions. Public directory contacts use the actual directory page and individual public API source, not guessed service websites. Form fields remain local until the visitor opens their email app and sends the message.

## Next production increment

Use the same model in a managed SQL database with an editorial UI. Add `last_verified_at`, `verified_by`, `review_due_at`, language, service geography, service hours, contact consent/publication authority, expiry date, and source-change history. Separate incoming correction/submission records from approved public records. Add reliable mail delivery and rate limiting. Introduce verified emergency pathways only after appropriate source checking. Do not train or generate guidance from old contact lists as if they were current.
