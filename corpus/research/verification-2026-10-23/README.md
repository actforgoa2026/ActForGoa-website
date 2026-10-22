# Official-source verification, 23 October 2026

This review updated all five practical guides, six supporting templates and the public verification/source registers. It does not establish current legal consolidation, a parcel's legal position, live office acceptance or clinical service availability.

- evidence-manifest.json: 26 reviewed official sources, exact URLs, physical PDF locators, limits, local originals and SHA-256 hashes. Retrieval timestamps are UTC; the review date is Asia/Kolkata.
- flag-status.json: all 33 topic flags, supported findings, remaining questions and suggested reviewers. No authority was contacted and no form, payment or complaint was submitted.
- czmp-browser-evidence.json: read-only GCZMA Final CZMP Goa menu and its 17 observed links.
- source-urls.json and seeds*.json: bounded source discovery/download inputs.
- publication-checks.json: local tests, build and byte-matched download checks; the visual and production stage must be updated after completion.

Original source files, extraction/page metadata and machine OCR remain in the main local corpus under /Users/zakkrevitt/code/ActForGoa/corpus. Only selected evidence metadata is versioned here; original documents are not republished on the website. Download failures remain failures, not evidence of non-existence.

Downloads used HTTPS certificate verification. A macOS curl fallback used system TLS trust for servers whose certificate chains failed in Python; certificate checks were not disabled. Native PDF text and English OCR derivatives are stored separately. NCDC physical page 16, crop-loss procedure page 4, AWBI SOP page 4 and CZMP Map 1 were visually inspected. PIB content was extracted from its article div because its ASP.NET form wrapper caused the generic extractor to omit article text.

The corpus was reindexed and audited after retrieval: no raw/text/OCR hash or PDF page-sequence errors, SQLite integrity OK. The guide source register distinguishes original Acts/notifications, official explanatory material and local service checks.
