# Visual cleanup — 29 October 2026

Implementation: `cdfc4de`, isolated branch `codex/visual-cleanup`, based on freshly fetched `origin/main` `1c4ac7c`.

Menus use destination labels without explanatory paragraphs. Work and volunteer links move into Take action. Homepage topic subtitles, repeated discovery descriptions and inserted topic/tool/participation panels are removed. Catalogue headings use plain names. Article cards show images and titles without excerpts or repeated kind/date/topic metadata; draft-guide status remains. Topic pages show three reading picks followed by three compact organisation links; full catalogues remain accessible. Breadcrumbs no longer repeat the title. Original article bodies, source corrections, draft notices and archived-service warnings remain.

Supplemental topic covers use Wikimedia Commons photographs of Goa: paddy fields, Candolim–Nerul mangroves and Panaji, plus the existing licensed Vagator photograph. Local WebP files avoid runtime dependence on an external image service. Visible author/source/license attribution is retained, with modification notices on articles and public asset sidecars. Original images take precedence. Supplemental photographs are illustrative, not evidence of the article's event or people. Organisations without real photos do not get invented imagery. Archive articles, authored guides and journal articles without inline images receive covers. Journal summaries have no image/body field; their cards use illustrative covers without adding requests for every article body.

## Verification

- 211 Node tests passed with `NODE_USE_ENV_PROXY=1 npm test`; includes two new checks for archived-article cover coverage, original image precedence, local assets, credit/license presence, topic matching and directory exclusion.
- Production build passed. Existing bundle-size advisory remains.
- Chromium at 1440, 390 and 320 pixels: homepage, waste topic, compost action, library, stories and an original article. No page errors, overflow or unloaded images after eagerly loading lazy images for inspection. See `browser.json`.
- Final menu checks at all three widths: Work with us, Volunteer, Get involved and Emergency services remain available; Volunteer navigates to its original article. Compost action opens its correct heading. Topic sections each contain three entries, with one shared archive note. See `menus.json`.
- Local public-blog API fixtures verify list/detail layouts, absent-image covers, original inline-image preservation and no duplicated excerpt. Authored reporting guide has a cover. No horizontal overflow at any width. These are local fixtures, not a live editorial-service acceptance test. See `blog-fixtures.json`.
- Final desktop and phone screenshots were inspected. No Device Hub launched. Impeccable skill/tool is unavailable in this executor; existing `.impeccable` design files were inspected, but no Impeccable detector pass is claimed.
- `git diff --check` passed.

Implemented and locally tested. Not merged or deployed. No alias changes, provider requests, private-account writes or backend changes. Release coordinator retains deployment ownership under `AGENTS.md` and `docs/RELEASING.md`.
