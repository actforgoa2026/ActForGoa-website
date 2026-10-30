# Official flood preparedness in SAPCC research

The user requested practical official guidance alongside SAPCC proposals. The implementation adds a bounded Claude Agent SDK source tool and renders each source category separately. It is ready for integration into the active research-assistant release; this feature branch has not deployed or made paid model calls.

## Sources checked on 30 October 2026

- [Goa Directorate of Fire & Emergency Services: Floods](https://dfes.goa.gov.in/floods/), specifically flood warnings and the flood dos and don’ts. Its unrelated closing paragraph about grass fires is excluded.
- [NIDM: Do’s and Don’ts for Common Disasters](https://nidm.mha.gov.in/PDF/IEC/DOS_E_24.pdf#page=5), physical PDF page 5, Floods. Linked from the institute’s current [awareness-materials catalogue](https://nidm.mha.gov.in/iec.asp). The downloaded 20-page PDF is scanned; page 5 was rendered and inspected directly. The older nidm.gov.in/www.nidm.gov.in URL failed hostname verification and is not shipped.
- [NDMA Sachet](https://sachet.ndma.gov.in/) is linked for live official alerts. The assistant does not fetch or assert current alert, shelter, route or evacuation status.

Publication dates are not established. A checked date records source review, not publication or proof of present local conditions. The committed JSON contains concise ActForGoa paraphrases, explicitly labelled as summaries rather than original quotations. Downloaded originals remain in ignored verification evidence. No source PDF or corpus generation is rewritten.

## Behavior and boundaries

`read_official_guidance(topic="floods")` exposes only the two reviewed summaries. It performs no network requests and accepts no arbitrary URL. It is available to general research and to the SAPCC source verified by its original checksum; other document scopes remain unchanged. Reading the tool is required before a guidance ID can be cited. Citation IDs bind to the exact reviewed summary and source metadata.

The agent is instructed to use this tool for practical flooding questions and keep SAPCC risks/proposals separate from before/during/after resident steps. Validation rejects paragraphs mixing official-guidance and corpus evidence. The frontend independently groups by actual source provenance, omits malformed mixed paragraphs, and provides original PDF-page or government-webpage links. Each official source exposes the checked date, undetermined publication date and summary provenance. General preparedness is distinguished from live local instructions. The prompt preserves conditions on evacuation, electricity, returning home and drinking water.

The existing corpus, SDK provider/model, budgets and accounting remain unchanged. The runtime packaging already copies backend/data, so no data-volume activation is required. Caches containing preparedness answers must include the official-guidance version/content in their invalidation boundary; retained examples must not bypass read-source validation during generation.

## Validation

- 256 frontend tests, 225 backend research tests and production build pass. Existing build chunk-size and Python SWIG warnings remain.
- New tests cover exact read-before-citation, source allowlisting, other-document boundaries, mixed-source rejection and independent UI grouping.
- Browser UI exercised at 1440×1000, 768×1000, 390×844 and 320×640. The preview uses an explicitly mocked model response with real citation metadata and live source reads; this is not hosted semantic acceptance.
- Both answer sections, checked-date caveats, original links, source-summary disclosures and preserved follow-up draft verified. The Goa government citation opens its real source in a separate tab. No browser errors or horizontal overflow; no computed italic/oblique type or decorative side stripes in the changed surface.
- At short phone heights, the existing fixed transcript exposed only a few lines. A bounded CSS correction uses normal page scrolling in windows up to 620px wide and 700px high. Larger phone/tablet/desktop behavior is retained.
- Impeccable’s existing session context and current Figtree/Arc surface contract were retained; clarify, craft-floor and polish guidance applied. The shared design system is unchanged. No Device Hub was used.

Evidence is under `.reports/flood-preparedness/`: browser screenshots/checks, downloaded source hashes, preview fixtures and test/build logs. The displayed preview is not a live AI answer. Live semantic acceptance and integrated deployment belong to the active release coordinator recorded in issue #89.

## Download fingerprints

- `nidm-current.pdf`: `bc5a0b943d66290d5d8c1bf88c45a693c63e5cffa5189fde9c0e1781975c83c4` (24376159 bytes).
- `goa-dfes.html`: `66a2272dc6db544d6ca25359855830c7942f32e8531247d0490a8cc8830ddaa1` (161583 bytes).
