# Forms and PDF export — 28 October 2026

Implemented in the cloud feature worktree from `fa43cf8`. Not merged or deployed by this workstream.

## Pathway audit

All 43 form actions across the eight topic menus open on-site editors. They cover complaint/follow-up/RTI letters, animal assistance, farming plans/registration/support/damage, building checklists/permission/completion enquiries, environmental inspection requests and local service enquiries. No topic action has a download attribute, blank-template URL, PDF URL or downloads-directory destination. Building routes now offer the building checklist and permission enquiry directly. The crop-damage path selects the damage branch; the scheme path selects support. The editor returns visitors to their originating topic path.

All 18 authored forms remain available through their guides. Guide Markdown template links and discovery tools open the editors. No new official form is invented. Original template files remain as evidence/source copies; visitors do not need them to use the editors.

The historical archive reader also contains ten named application/battery/e-waste PDF records. These are original-source references, separate from the authored forms. The three building/trade PDF URLs on `act4goa.org` are recorded unreachable in `reports/link-audit.csv`; the original PDF archive is absent from this cloud checkout. Some battery/e-waste records predate current rules. This change does not claim those historical PDFs are current official forms or replace them with fabricated equivalents. Official submissions may still require the receiving authority's current prescribed form; the editor retains that distinction.

## Export and phone behavior

Save PDF creates a file directly in the browser; entries are never sent to a server. A persistent Open PDF link lets phone users save to Files, and file sharing appears where the browser supports it. Print/save PDF and Word remain alternatives. The PDF preserves paragraph wording, chosen sections, table headers, repeating rows, missing-field labels and dates. Wide tables use landscape pages; long rows can continue onto later pages. An export cannot silently save an earlier draft if entries change during preparation.

Bundled SIL-licensed Noto Sans and Noto Sans Devanagari support Latin and Devanagari text. Whole grapheme clusters stay together for shaping. Unsupported characters produce an explicit print/Word fallback rather than a PDF with replacement boxes. The PDF library and fonts load only when a PDF is requested. Notes about editing raw bracketed templates are omitted from completed documents; legal/procedural cautions remain.

## Verification

- `NODE_USE_ENV_PROXY=1 npm test`: 140/140 passed. The inherited proxy setting is necessary for the existing remote MCP test in this cloud environment.
- `npm run build`: passed; PDF code is a separate lazy chunk. Vite reports its standard large-chunk advisory for pdfmake.
- All 18 forms generated real PDFs containing entered Latin/Devanagari text. A long repeated case log generated multiple pages, preserving final rows and excluding removed rows.
- Cloud Chromium at 1440×1000 and 390×844: opened the crop-damage topic action, confirmed damage preselection, filled every visible field, saved a PDF and opened the recovery link. No page errors or horizontal body overflow.
- PyMuPDF extracted the browser-generated files: accented Latin and Devanagari text retained; damage section present; unused support section absent. Rendered PDF inspected for readable typography and layout.
- Evidence is in ignored `.reports/forms/`: browser smoke JSON, desktop/phone fill/review screenshots, browser PDFs, rendered sample PDFs and test/build logs. Root must verify the final combined tree before release.

The Impeccable skill referenced by `AGENTS.md` was not installed in the cloud. Existing `DESIGN.md` and Arc components were used, with rendered desktop/phone checks. No Device Hub was launched.
