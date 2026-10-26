# Local research validation

Validated on 22 October 2026 against index `20261022T155701-21661179`.

## Verified

- Production TypeScript/Vite build and 8 existing frontend tests pass.
- 13 research backend tests pass, including actual MiniLM embeddings and Zvec retrieval, immutable generations, full-document integrity, safe file routes, PDF page rendering, and citation validation.
- Actual archive: 16/16 retrieval smoke queries; 1,156/1,156 original file checksums. See `research-evaluation.json` for per-query results. Term coverage is not a factual-answer benchmark.
- Browser journeys at 1280×720 and 390×844: source search, empty results, unavailable-answer-service state, citation-to-exact-passage navigation, page navigation, final page, full-text download, original PDF download and original PDF page view.
- Browser-downloaded State Water Policy 2021 PDF matches its archived SHA-256; its downloaded full text matches the complete API response.
- Cited-answer UI was exercised through the real Responses SDK and an explicitly labelled mock HTTP provider. Source passages, index, citation links and full documents were real. No request was sent to OpenAI in this test.
- Answer → citation → reader → page navigation → return preserves conversation, draft and research mode on desktop and phone. Document-scoped research retains its document/version, results and draft; returning to the whole collection restores its independent conversation. Reload clears this memory.
- Authored research UI uses the existing Literata/Manrope, paper/green palette and layout conventions. No authored italic/oblique elements or decorative side borders were found. Original source pages retain their original typography.

## Coverage and limits

- Index: 1,156 documents, 21,220 pages/sections, 78,432 passages.
- Ecology seed ingestion: 37 successful downloads and 15 explicit failures. Some successful URLs are abstracts or index pages. See `ecology-ingestion.json` for details.
- 110 pages use unverified English OCR; 2,343 pages have little extractable text. 56 corrupted-text pages remain accessible in the reader but are excluded from search. Complex tables and multi-column layouts need checking against the original page.
- Citation validation verifies evidence identifiers and links, not factual entailment. Live model answer quality, latency, billing and credentials remain untested.
- No API key was created or saved: the secure local destination confirmation was declined. Source search and document access work without that key.
- This is a local worktree implementation. It has not been pushed, merged or deployed. The test-only fixture server is stopped; the local Vite preview and real research API remain available.

The design reviewer’s report and viewport captures are local artifacts under `.impeccable/review/`.
