# Local design and function iteration

29 October 2026. Preview: http://127.0.0.1:4173. Nothing pushed or deployed.

## Design and controls

- Kept the circular photo homepage, eight topic icons, forest green and cream palette. The topic section fills most of a desktop viewport.
- Used actual uiArc public-registry SearchField, Button, Input, Textarea, SegmentedControl, MorphSelect, Switch, Checkbox and Slider components. ButtonLink shares Arc Button styles and motion while retaining real link semantics. Source attribution is in `src/components/arc/PROVENANCE.md`.
- Removed extra search containers. Library searches are capped at 560px including the submit button; Directory search is capped at 520px. Fields fit their columns on phones.
- Kept upright self-hosted Figtree, centered navigation, selective offset shadows and the components’ keyboard, loading and reduced-motion behavior. Removed surplus directional arrows and the homepage Pause motion / Find your next step controls.
- Directory replaces Community in the main navigation and uses a sliding selector. Actual Arc dropdowns keep the filters compact.
- Map uses nearly the full viewport below a compact header and title, with floating native controls and an expand option. Dates and supporting evidence follow below.
- Restored source-specific article images rather than repeating a generic mangrove cover. New stippled Goa footer is reused on pages with a footer.

## Reading, forms and chat

- Story topic changes preserve the reader’s current scroll position and tuck practical-help choices into a disclosure.
- Forms have a compact introduction and draft controls; recipient guidance searches available source-backed local-office records and fills the editable To field only when the user chooses an office.
- Report category selection scrolls and focuses the description. Explicit, optional dictation appends recognized speech and handles unsupported browsers, permissions, stop and error states.
- Chat starter actions show the question and progress immediately. The transcript and composer occupy separate rows, preventing answer overlap. New chat returns to the starting menu; Browse library opens readable corpus selections and full saved documents.
- Government contact routes show Forest, Agriculture and Veterinary contact details first, with published source links and review dates. The directory is incomplete and does not establish jurisdiction or response availability.
- External HTTP(S) links open in a separate tab with noopener/noreferrer. Internal routes, phone/email actions and downloads retain their appropriate behavior.
- All five original newsletter issues are available locally. The 2025 image-only PDF has checked readable text plus optional original page images. Its report references have no embedded destinations in the original PDF; the reader says so.

## Verification

All 238 Node tests pass, including new contact routing, dictation state, newsletter content, article photos, browse results and external-link policy checks. Production build and TypeScript pass; the build retains a non-blocking large-chunk warning for existing bundles. Prior satellite Python verification passed 140 tests. Changed-source scans found no italic/oblique styling or decorative side stripes.

Desktop and phone captures are in `.impeccable/review`. Current Directory and Library renders measured 390px document width at a 390×844 viewport. Browser interaction checks covered Arc dropdown filtering and Escape, local-directory tag filtering, exact story-scroll preservation, form recipient selection, report focus, checkbox/switch keyboard control, corpus browsing and full-text reading, newsletter readers, and external links opening another tab. Saved map evidence opens locally; Arc opacity and date sliders work by keyboard. No new AI answer or paid imagery retrieval was dispatched in this finish pass.

Live microphone recognition was not exercised; it requires a supported browser and the user’s microphone permission. Dictation lifecycle/error behavior is covered by automated tests. Photo preview source handlers are preserved and compile, but Chrome’s file-access setting prevented an automated local-photo upload check; that permission was left unchanged. Browsable research shelves use existing read-only search and are not an exhaustive document inventory. Source availability and original-document limits remain visible.

## Review record

The first finish review requested native Arc migration for remaining controls, removal of custom topic button skins and current design documentation. Those fixes were applied. The repeat review accepted those fixes and found one checkbox focus-outline spacing issue. Its label gap was increased to 8px; the final phone capture shows a clear 3px gap beyond the focus outline. The final reviewer disposition is `ship` for the scored fixes, with no remaining findings. This is not a claim of an exhaustive independent audit of every route.
