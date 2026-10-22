# Archive coverage and findings

Snapshot: 22 October 2026. Public, read-only crawl of https://actforgoa.org/.

- 10,568 distinct fetched URLs; 1.35 GiB of response bodies.
- 2,806 HTML responses, including failures and legacy attachment pages.
- 600 searchable records: 49 contact, 104 organisation, 72 page, 237 resource, 138 story.
- 164 linked document references; 60 with extracted PDF text.
- 5,036 unique linked destinations audited. See LINK-AUDIT.md and link-audit.csv.

## Important findings

- The pages API fails when it renders legacy page content. A metadata-only field selection recovered 152 public page records; HTML supplies their content.
- The Connections directory API fails in its default rendering path. Selecting public contact fields and paginating with offset recovered 104 entries. Its page parameter repeats the first page; offset 100 yielded the final 4 entries.
- The public media API reports 2,207 records in its total header but actually returns 1,288 unique records across all 23 pages. This discrepancy remains unresolved; no private or authenticated endpoint was accessed. Linked responsive images, CSS and document traversal expand asset coverage independently.
- The library has 24 archive pages and 237 recovered resources.
- The snake rescue list is dated 22 October 2018. Its 49 named contact rows are indexed separately; current availability is not verified. Seven-digit local numbers are preserved as text, without inventing an area code.
- Original relative footer links such as community and greenviksitgoa resolve beneath individual article URLs, creating thousands of questionable destinations. These are retained in the graph; many return access restrictions, which are not labelled confirmed dead.
- The site contains old theme examples, shop/account pages, exposed shortcode text, a placeholder email address, and old staging links. 56 template/account pages are explicitly excluded from the rebuilt public search but remain archived.
- Some HTTP 200 responses contain WordPress critical errors. These are classified as soft errors separately from genuine successes.

## Boundaries and incomplete coverage

This is a deep public snapshot, not a claim to have recovered the private WordPress database. Robots exclusions, calendar loops, authenticated endpoints, login flows, form submissions, donation actions, query traps, syndication duplicates, and response bodies above 80 MiB were excluded. Third-party sites were link-checked, not recursively crawled. Linked documents were archived where accessible. JavaScript-only private community content, social-platform posts behind restrictions, and unlinked files are outside coverage.

PDF text extraction is best-effort; scanned pages have not been OCRed. Semantic indexing includes at most the first 3,200 words of each record/document aggregate; full extracted text remains in the local data folder and SQLite FTS index. Titles and wording are source material and can contain historical or inaccurate claims.

Missing static anchors are candidates for review, not automatically broken links: some are controlled by the original JavaScript. See data/fragment-audit.json.

## Files

- `archive/raw/`, `archive/assets/`: exact bodies, locally retained, named by URL hash.
- `archive/manifests/fetches.jsonl`: append-only fetch evidence with timestamps, status, redirects, checksums, and paths.
- `archive/site-responses.tar.gz`: portable copy of raw HTML/API/sitemap responses and fetch manifest.
- `data/fetch-manifest.json.gz`: latest metadata per URL.
- `data/links.json.gz`, `data/library-links.json.gz`, `data/fragment-links.json.gz`: link graph including raw references and referring pages.
- `data/catalog.sqlite`, `data/catalog.json`: normalized catalogue and contact/topic/document tables.
- `data/document-text/`: extracted PDFs; `data/forms.json`: original form field inventory. Forms were not submitted.
- `reports/page-inventory.csv`, `reports/link-audit.csv`: reviewable inventories.

## Reproduction

Create the Python environment, install requirements, run `npm run crawl`, then run `scripts/recover_directory.py`, `scripts/crawl_library.py`, `npm run extract`, `npm run audit:links`, `scripts/inventory.py`, and `npm run index:semantic`. Fetches resume from the manifest. Cached successes are reused; use a new archive directory for a fresh-date crawl.