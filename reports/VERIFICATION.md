# Verification record

22 October 2026. This is a client-review preview, not a production cutover.

## Automated checks

`npm test`: 8 passed. Checks cover natural-language snake ranking, colloquial waste queries, named volunteer/locality lookup, honest empty results, semantic matches without lexical overlap, unique source-backed records, safe complete telephone actions, and embedding index integrity.

`npm run build`: TypeScript and Vite production build passed. The model/runtime are intentionally lazy-loaded; first-use semantic search has a substantial download (roughly 50 MB uncompressed). Immediate keyword search remains usable.

Impeccable detector ran on `src/App.tsx` and `src/styles.css`: no findings. Source and rendered styles were checked for italic/oblique text and decorative side stripes.

## Browser checks

Inspected desktop at 1440 pixels, the user's 1280-pixel viewport, and mobile at 390 pixels using the in-app browser. Screenshots are retained locally in `.impeccable/review/`.

- Home, mobile navigation, topic chips, directory list/grid controls and waste filter.
- Natural-language snake query with actual browser semantic inference reaching “Matched by meaning and keywords.” The original volunteer list ranks first; source dates and unverified-contact notices remain visible.
- Named contacts, complete `tel:` actions, source links, library cards, and long-form reading.
- Library contains 237 resources; directory includes organisations and individual source-listed contacts.
- Nonsense query returns the empty state after semantic inference completes.
- Correction form prepares an encoded email containing the record context. No message was sent, and the preview stores no submissions.
- Mobile document width equals the 390-pixel viewport after the responsive layout correction. No rendered italic elements were found in the checked state.
- After review fixes, measured mobile search inputs are 16px, explanatory/source notices 14px, and status text 12px. Queried Everything results render separate labelled sections; all original filters and layouts remain available.

## Deployment

Public client-review URL: https://actforgoa-field-guide.vercel.app/. This is a new, separate Vercel project using its own production alias; the original ActForGoa domain and hosting are unchanged. The public homepage returned HTTP 200 with `X-Robots-Tag: noindex, nofollow`.

The deployed browser completed actual local semantic inference for “Who can help with a snake in my lawn?”, displayed the original rescue resource first, and recorded no warnings/errors in the fresh tab. Load-more increased rendered results and the original source detail route opened correctly.

Final deployment: `dpl_5Zykdjd5o1w63ycnktJ6xd2rPjTs`, 22 October 2026. Verified the grouped query on the public alias: 7 guides, 51 people/organisations, 2 stories, 1 about/action match. Hard-reloading the query URL worked; selecting People & organisations then browser Back restored Everything. No warnings/errors were recorded. The deployed mobile homepage measured 390px viewport/document width with a 16px search input. Final screenshots are `deployed-mobile.png` and `deployed-home.png` in the local review folder.

## Design review

An independent Impeccable finish reviewer returned `fix` for result grouping, mobile text size, and a redundant spotlight eyebrow. All three were implemented in one batch, rebuilt, and recaptured at the same 11 required views. The reviewer returned `ship`, scoring all three fixes resolved and all captures valid. This is a verdict on the listed fixes, not an independent exhaustive interaction or accessibility audit. See `DESIGN-REVIEW.md` for the original findings and verdict.

## Limits

This is not a full WCAG audit or an exhaustive device/browser matrix. VoiceOver, Android/iOS browsers, older devices, slow networks and load tests remain unverified. Current availability of imported contacts is unverified; the rescue list is from 2018. Historical medical/legal source content requires editorial review before a public launch. Semantic indexing is capped at 3,200 words per record/document aggregate; full text is preserved locally. The email preparation flow is functional but is not a server-backed contact or moderation system.

The crawl report records robots boundaries, API count discrepancies, inaccessible material, and PDF extraction limits. The raw archive is intentionally excluded from the deployed app.
