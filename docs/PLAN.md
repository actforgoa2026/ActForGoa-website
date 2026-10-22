# ActForGoa archive and rebuild plan

## 1. Preserve and map the existing site

1. Save robots directives, sitemap indexes, API schema, public content types, taxonomies, and paginated records.
2. Crawl canonical public internal URLs from navigation, sitemaps, API records, pagination, and content links. Respect robots exclusions and avoid administrative, login, calendar-loop, and form-submission endpoints.
3. Save exact response bytes, HTTP status, final URL, fetch time, MIME type, SHA-256, and local path. Archive referenced media, scripts, stylesheets, fonts, and downloadable documents. Recurse through CSS dependencies.
4. Extract main content separately from navigation and footer; retain raw HTML as the authority. Capture titles, headings, dates, structured metadata, images, contacts, external links, documents, forms, and relationships.
5. Audit internal and external links. Retry candidate failures. Separate confirmed 404/410, server errors, access restrictions, timeouts, redirects, and non-HTTP links. Preserve referring pages for repairs.
6. Publish machine-readable manifests, a link graph, content inventory, SQLite database, and a human-readable coverage report. Record every exclusion and incomplete fetch. Never describe an unbounded web crawl as exhaustive.

## 2. Turn source content into useful databases

- Records: pages, organisations, resources, stories, projects, events, and opportunities.
- Contacts: telephone numbers, email addresses, websites, location text, source record, and verification state.
- Documents: local copies, source URL, text extraction, and parent resource.
- Topics: original categories plus a small, explicit mapping to user needs.
- Links: source, target, anchor text, relation, response, and audit state.
- Search index: weighted title, summary, topics, text, contacts, and locally generated semantic vectors.

Store provenance and original wording alongside presentation fields. Do not silently infer emergency availability or current validity from an old post.

## 3. Build the field guide

1. Search-first home with useful starter queries, topic browsing, and real community content.
2. Hybrid search with plain-language queries, result-type filters, accessible empty states, and shareable URLs.
3. Directory with list and grid views; source-linked detail pages and click-to-call/email actions.
4. Reading library with preserved long-form content and links to original documents.
5. About and participation paths using original organisational copy and links.
6. Contact and correction forms that honestly prepare email when no mail-delivery backend is configured.
7. Mobile layout, keyboard support, local assets, and no required account.

## 4. Verify and deliver

- Data checks: counts, provenance, unique IDs, phone extraction, duplicate records, and broken-link classifications.
- Search checks: snake rescue, waste segregation, composting, community groups, planning, and unrelated queries.
- Browser checks: desktop and phone, filters, reading views, contact forms, navigation, no-results states, back/forward, and overflow.
- Run Impeccable detector and fresh finish review; record design tokens and remaining limitations.
- Create a private GitHub repository containing source, scripts, derived data, plans, and reports. Keep bulky raw archives local with checksums and reproduction commands.
- Deploy a Vercel preview and verify the deployed build. Preserve the existing production website.

## Scope and follow-up

The crawl covers publicly accessible information, not authenticated content, private submissions, or entire third-party websites. Third-party targets are audited; linked public documents are archived where accessible. Future production work includes editorial contact verification, content ownership and update workflows, multilingual support, a durable submissions backend, and an approved domain cutover.
