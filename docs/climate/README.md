# Goa SAPCC documentation

This collection contains the Goa State Action Plan for Climate Change for 2023–2033 and a resident-focused guide integrated into ActForGoa at `/climate-plan`.

- [Original PDF](goa-sapcc-2023-2033.pdf), unchanged government-hosted download, 9,222,768 bytes.
- [Reading guide](READING-GUIDE.md), 13 topics, 26 selected measures and the complete chapter and annexure index.
- [Provenance](PROVENANCE.json), retrieval, checksum, version evidence and extraction limitations.
- [Source index](../../src/content/climate-plan.json), the shared reviewed content for the website and reading guide.

## Research findings

The NITI for States repository returned the [complete PDF](https://www.nitiforstates.gov.in/public-assets/Policy/policy_files/GSSNAD000283.pdf) on 29 October 2026. Its cover names the period 2023–2033. PDF page 3 identifies Goa State Biodiversity Board as publisher, NABCONS as preparer, publication on 26 April 2023 and national approval in principle on 24 August 2022.

The [Goa Legislative Assembly answer to LAQ 168, dated 8 August 2025](https://static.goavidhansabha.gov.in/goalpub/docs/question_docs/file_8364a593-520a-4c6f-afb3-e202c84b26d1.pdf) identifies the 2023–2033 plan and provides the [GSBB download URL](https://gsbb.goa.gov.in/wp-content/uploads/2024/11/SAPCC8Aug2023.pdf). Direct retrieval returned HTTP 404 on 29 October 2026; the web reader returned 403. Its error response is retained in the corpus. The accessible NITI copy cannot be asserted byte-identical to that unavailable file.

The current [MoEFCC SAPCC table](https://napccindia.moef.gov.in/sapcc) describes Goa as prepared in 2023 with revision under preparation; the [Goa profile](https://napccindia.moef.gov.in/sapcc/state/goa) calls its plan v2.0. These are conflicting labels, so the integration identifies the document by its own cover period and publication date. No newer complete official edition was located in this research.

The archive also contains a 2020 consultation press note and the separate State Action Plan on Climate Change and Human Health. Neither replaces the statewide SAPCC. No existing record was deleted or silently relabelled.

## Reading and extraction caveats

- The original has 111 physical PDF pages. Most are two-page spreads, with printed numbering through 218. For printed pages 4–218, the PDF page is `floor((printed_page + 4) / 2)`. Printed p. 25 starts on PDF page 14; printed p. 162 starts on PDF page 83. Source links use physical PDF pages while labels preserve printed pages.
- Native extraction loses some ligatures and table reading order. Annexure VII, PDF pages 99–110, contains scanned minutes; headings and footers caused the generic extractor to miss the need for OCR. These pages are manually flagged for visual/OCR review. They have not been fully transcribed.
- The financing chapter is internally inconsistent. Printed p. 162 mentions ₹465 crore; p. 163 and the table continuing on p. 164 give ₹2,341.06 crore over ten years. These are plan estimates, not verified sanctions or expenditure. The resident guide flags the discrepancy instead of silently reconciling it.
- The cover period is 2023–2033, but some internal passages retain older dates, including the monitoring chapter's reference to a start in 2021. Do not infer current deadlines from relative timeframes in the tables.
- Maps describe planning scenarios, not parcel-level risk or regulatory classifications. Project status and department assignments reflect the source, not live availability. The navigator presents selected measures and questions, without implying the questions are instructions from government.

## Corpus and reproduction

`corpus/seeds-sapcc.json` records the three research URLs. The successful NITI source has ID `3710c85a419254abd7347c52`; native text and page records are in `corpus/text/` and `corpus/pages/`. The metadata and SQLite research search preserve the original URL and physical PDF page references.

```sh
.venv/bin/python scripts/ingest_goa_corpus.py --seeds corpus/seeds-sapcc.json --depth 0 --limit 3 --workers 2 --skip-index
python3 scripts/publish_climate_plan.py
.venv/bin/python scripts/ingest_goa_corpus.py --index-only
.venv/bin/python scripts/search_goa_corpus.py '"Goa State Action Plan"' --limit 5
```

The downloader reuses existing results. A deliberate refresh uses `--retry`; inspect the new source before changing the shared index or page mapping. Publishing checks the PDF checksum if the original is present. Keep the manually identified scanned-page flags in provenance when re-extracting.

The public build contains the authored index and reading guide; it links to the government PDF. The original is stored locally under docs and the content-addressed corpus, outside Vite's public directory. The publisher asserts copyright and no public redistribution licence has been established. Changes here do not update the hosted MCP service or deploy the site.

## Questions with source links

The resident navigator now has an “Ask about this plan” entry point, and topic pages can draft a question without sending it. The dedicated conversation uses the saved SAPCC edition and links answers to exact passages and original PDF pages. Its limitations remain visible: the plan describes proposals and historical conditions, not verified current delivery.

The hosted library already held this same PDF. The research integration refreshes its extraction rather than adding a duplicate. `scripts/extract_sapcc.py` separates the two printed pages, turns sideways tables, preserves native characters and cell positions, and flags the scanned minutes. `scripts/refresh_sapcc_index.py` stages a new immutable full-corpus generation while checking that every unrelated record and every base-generation file remains unchanged. It never switches `CURRENT.json` or changes usage accounting. See [research integration and acceptance](../../reports/sapcc/RESEARCH.md).
