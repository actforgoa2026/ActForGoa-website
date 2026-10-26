# Main-search corpus answer design review

26 October 2026. Scope: the ordinary extension that places a short cited answer above normal search results. The fresh finish reviewer returned **SHIP**, with no material findings in the submitted interface scope. This documentation pass checked the current source, all seven supplied browser captures, and the accompanying check and detector records against the incumbent system.

The verdict covers the rendered search extension and source-reader handoff. It does not approve backend answer semantics, claim-level source support, consolidated current law, provider activation, or public deployment.

## Contract and system fit

The governing context is `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`, and the “Corpus answer extension” contract in `.impeccable/surfaces/src-app-tsx.md`. The Impeccable context workflow ran once for `src/App.tsx`; its documentation playbook and existing-surface preservation rule were consulted.

This is an Operate/Read extension of the established field guide. It retains warm paper, green text, upright Manrope, shared Arc controls, and open content separated by horizontal structural rules. The answer introduces no filled card, decorative side stripe, new font family, palette, raster asset, or motion vocabulary. Its 18px answer text and 1.75 leading match the local surface contract. Source CSS keeps that reading size on phones, with a 26px phone heading and wrapping for long text and source titles.

The answer follows the submitted search field and any existing emergency section. Catalogue filters, counts, and results continue below it. Numbered links sit beside the paragraphs they qualify; a native source disclosure exposes document titles and page labels. The existing document reader provides original and full-text downloads and a “Back to search results” route. “Explore the research” carries the question into the research interface. Provider disclosure and the request to check cited sources remain visible in the answer section.

Loading, missing evidence, and error states use the same open layout. The error state supplies the installed Arc ghost retry button, while the catalogue remains available. The section has a heading, busy state, and polite live region; citation links include source title and page context in their accessible names. This source inspection does not claim a full assistive-technology audit.

## Source checked

| File | Observed responsibility |
| --- | --- |
| `src/SearchAnswer.tsx` | Answer hierarchy, states, inline citations, source disclosure, retry, research handoff, and provider disclosure. |
| `src/search-answer.css` | Open ruled layout, inherited colour and typography, answer measure, wrapping, and phone spacing. |
| `src/search-answer.ts` | Frontend response validation, local document-link restrictions, brief request, cancellation, timeout, and bounded answer cache. |
| `src/App.tsx` | Search-only insertion after emergency access and before existing search controls/results. |
| `src/Research.tsx` | Question prefill and source-reader return to the originating search URL. |

The new source files contain no italic/oblique styling or decorative side-border/pseudo-element treatment. The small App and Research diffs do not introduce visual styling. Existing shared components and system tokens remain the visual authority.

## Rendered evidence

All seven files below were opened and visually inspected in this documentation pass. Their actual image headers confirm the listed dimensions. They contain JPEG data under the supplied `.png` filenames; the evidence files were preserved unchanged.

| Capture | Size | Evidence inspected |
| --- | --- | --- |
| [desktop.png](../.impeccable/review/desktop.png) | 1440 × 1000 | Search field, two cited paragraphs, closed source disclosure, research link, and provider copy. |
| [user-1280.png](../.impeccable/review/user-1280.png) | 1280 × 720 | Answer hierarchy and reading measure at the smaller desktop viewport. |
| [mobile.png](../.impeccable/review/mobile.png) | 390 × 844 | Compact shared header, search field, upright readable answer, and inline citations. |
| [mobile-sources.png](../.impeccable/review/mobile-sources.png) | 390 × 844 | Expanded numbered sources, wrapped long title, PDF page label, and continuation into existing filters. |
| [mobile-results.png](../.impeccable/review/mobile-results.png) | 390 × 844 | Guides selection, result count, list control, and open resource rows. |
| [mobile-fallback.png](../.impeccable/review/mobile-fallback.png) | 390 × 844 | Citation-verification failure, retry, research link, and continuation toward catalogue controls. |
| [citation-reader.png](../.impeccable/review/citation-reader.png) | 1440 × 1000 | Back-to-search link, source identity, original/full-text actions, and PDF page 698. |

[law-search-checks.json](../.impeccable/review/law-search-checks.json) records a real provider response already cached on the local service at port 8093, using generation `20261026T131818-law-23a2e6a6`. The record states that no new model request was made for the capture pass. It reports no horizontal overflow or italic/oblique text, 18px answer text with 31.5px leading, retained Guides filtering and cached answer after source return, exact page/passage navigation, research question prefill, and usable catalogue results after fallback. Those interaction results are attributed to the recorded browser pass; this documenter did not repeat them. The page-698 screenshot does not itself show the highlighted passage within the captured viewport.

[law-search-detector.json](../.impeccable/review/law-search-detector.json) is an empty findings array (`[]`). The supplied captures and current CSS show no decorative side stripes. [law-search-release.md](law-search-release.md) records the parent’s frontend tests, research tests, and production build; this documentation-only pass did not rerun tests, build, browser automation, or provider requests.

## Preservation and remaining boundary

No durable design-system change was approved. `DESIGN.md` and `.impeccable/design.json` are preserved. The earlier context pass was reported to have identified the sidecar as older than `DESIGN.md`; this is previously reported drift, not a newly reproduced diagnostic. It is recorded without repair, in keeping with Impeccable’s ordinary-extension rule.

For preservation verification, the system-file SHA-256 values at this documentation pass are:

- `DESIGN.md`: `f2eb807766ba5b579c19c18970028d88afded8618ab980b5f209bc3ab2121db3`
- `.impeccable/design.json`: `1ce1def38f9048197d735cf3b59a769e894fbb5a037b51aea24fdd2ae3667f10`

The interface documentation is complete at the reviewer’s SHIP scope. Backend retrieval/model behavior, brief-response enforcement, cost controls, legal-source currency, and whether every claim is supported require the coordinated backend evaluation. Live activation and deployment require separate release evidence. No public deployment is established by this report.

## Final notice refinement

26 October 2026. The backend-provided source-limitations notice is now retained by the main-search client. Current source inspection confirms that `notice` is optional, a provided value must be a string, and malformed values cause the response to be rejected. The added regression test checks retained notice text and rejects null, numeric, object, and array values. The documenter inspected this test source without rerunning the test suite.

For an answered response, a nonempty notice renders after the answer paragraphs and before the source disclosure. It uses upright inherited Manrope, the existing muted colour, 14px text, 1.7 leading, a 75ch maximum measure, and 16px block margins. It remains an open paragraph on the page ground. No system token, panel, side stripe, or new visual treatment is introduced.

The same finish reviewer returned **RESOLVED, SHIP THIS FIX** after inspecting the current source and five fresh captures. This is a resolved-fix verdict for notice validation and presentation, supplementing the earlier full interface review. It is not a new approval of backend answer semantics or legal currency.

The documenter also opened and visually inspected all five supplied images. Image headers confirm their dimensions; like the earlier evidence, these are JPEG images under `.png` filenames.

| Fresh capture | Size | Evidence inspected |
| --- | --- | --- |
| [desktop-notice.png](../.impeccable/review/desktop-notice.png) | 1440 × 1000 | Complete answer, inline citations, muted legal-source notice, source disclosure, and research handoff. |
| [mobile-notice-top.png](../.impeccable/review/mobile-notice-top.png) | 390 × 844 | Search and answer hierarchy before the lower notice section. |
| [mobile-notice.png](../.impeccable/review/mobile-notice.png) | 390 × 844 | Fully wrapped notice directly after the answer and before sources; continuation into existing search controls. |
| [user-1280-notice.png](../.impeccable/review/user-1280-notice.png) | 1280 × 720 | Search and answer hierarchy at the smaller desktop viewport. |
| [user-1280-notice-detail.png](../.impeccable/review/user-1280-notice-detail.png) | 1280 × 720 | Complete notice, source disclosure, research link, and provider copy in the scrolled answer view. |

The inspected notice text is readable and wraps without visible clipping or horizontal overflow. The captures show upright type and no decorative side stripes. The reviewer’s corresponding no-overflow result is reported evidence; this documentation recheck did not run browser measurements or interactions. Earlier interaction checks remain attributed to their original browser pass.

Only this report was appended during the final documentation recheck. Both system-file hashes still match the preservation values above. The preexisting sidecar drift and all backend, legal-currency, and deployment boundaries remain unchanged.
