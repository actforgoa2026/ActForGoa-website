# Local homepage and archive refinement

Implemented only in the local design-iteration checkout. No commit, push or deployment.

- Homepage search and suggestions use the installed Arc SearchField and Button directly. Page CSS owns layout only. Removed Pause motion, Find your next step and decorative link arrows. OS reduced-motion preference still stops the orbit and rotating headline, including changes while the page is open.
- Eight illustrated topic links occupy most of the available viewport, with a four-by-two desktop and two-by-four phone arrangement. Arc ButtonLink appearance is integrated by the chat/shared-controls work; the generous page layout remains.
- Article cards retain original images when present. Missing images produce text cards rather than repeating a generic photo chosen from a broad topic tag. Supplemental guide imagery is limited to explicit landscape subjects.
- SiteFooter uses a new generated green stippled Goa panorama, open typography and ordinary navigation links. There is no nonfunctional subscription form.
- Five newsletter issues are imported as local reading routes: `/newsletters`, `/newsletters/2025-year-end`, `/newsletters/2022-december`, `/newsletters/2022-august`, `/newsletters/2022-july`, `/newsletters/2022-april`. The legacy `/read/wp-8905` route redirects to the new archive.

## Newsletter sources and provenance

All five original issue requests returned HTTP 200 on 29 October 2026. The source archive is <https://actforgoa.org/newsletters/>.

- <https://actforgoa.org/wp-content/uploads/2026/03/2024-2025-Act-for-Goa-Year-End-Newsletter.pdf>
- <https://mailchi.mp/eb66242be2b6/k7ncfe5st3>
- <https://mailchi.mp/4f827fac9f80/panchayat-elections-are-this-wednesday-heres-what-you-need-to-know-16519023>
- <https://mailchi.mp/17f3965c491d/act-for-goa-stay-informed-take-action-16513439>
- <https://mailchi.mp/56c61bdf0566/actforgoas-first-newsletter-16099003>

The four HTML editions preserve the original articles, links and images. Email navigation, tracking, duplicate mastheads and subscription controls are omitted; mail-merge greetings use “reader”. Heading case is normalized. All records retain source and date. `scripts/import-newsletters.py` performs the bounded import and records asset hashes in `public/newsletters/provenance.json`.

The 2025 PDF contains four image-only pages; direct text extraction is empty. Its article body was transcribed and checked against all four rendered pages, stored in `src/content/newsletter-text/2025-year-end.md`, and appears as upright readable text by default. Original spelling and historic claims remain attributed to the newsletter. Original illustrations and layout are available in a disclosure, with an unchanged local PDF for opening or downloading. `pdfinfo -url` finds no link annotations in the source PDF: references such as “workshop report” and “2-month update” have no destinations in the published file. The reader states this instead of inventing links. Historical contact availability and article-linked external resources were not newly verified.

## Footer asset

`public/assets/footer/goa-stippled-landscape.webp` was generated with the built-in image_gen tool and converted to WebP. Its sibling JSON records the exact source output, prompt, date and use. The image is a decorative imagined cultural landscape, not documentary evidence or a map. No original article images were regenerated.

## Local checks

- `node --import tsx --test tests/article-photos.test.ts tests/newsletters.test.ts`: three passing tests.
- `npx tsc -b`: passed.
- Scoped `git diff --check`: passed.
- Browser: desktop 1440×900 and phone 390×844, no horizontal overflow. Eight topic choices fit in the phone viewport after their heading is scrolled into view. Homepage search for “wetland” routes to `/topics/water`. Original-layout disclosure opens all four page previews; all four December issue images loaded.
- Screenshots under `.impeccable/review/`: home-desktop-final.png, home-mobile-final.png, topics-desktop-final.png, topics-mobile-final.png, footer-desktop.png, footer-mobile.png, newsletters-desktop.png, newsletter-reader-desktop.png, newsletter-reader-mobile.png. Topic screenshots precede the final shared Arc ButtonLink appearance pass; geometry is unchanged. Full-site reviewer owns final cross-page acceptance.
