# Directory enrichment

Sources checked 23 October 2026. Reconciled with merged CRM on 26 October 2026 in `codex/directory-enrichment-integration`, based on `f26ad87606c032ecac479c9f8028dacddce5e5a8`. Local only; not pushed, merged or deployed.

## What changed

- Seven locally served, credited photographs from the organisations’ own sites: AERO, WAG, Coastal Impact, Live Happy, Green Essentials, Sethu and Khoj-aao. Cards crop photographs; detail pages retain their full proportions. Missing or failed photos leave the text listing usable.
- Reviewed subject tags for 77 organisation records and snake-rescue/wildlife tags for 49 volunteer records. The other 27 organisations retain their broader source topics; unknown specialisms are not invented.
- Direct website/social/project links on 17 listings (including the existing Tara Trust links), email actions on 79, and name/address map searches on 56. Remaining entries link to their original source. Individual rescue volunteers do not receive map pins or inferred business locations.
- Official address updates for AERO (Sanquelim), WAG (Siolim), Goa Foundation (Panaji), Green Essentials (Socorro), and Sethu (Saligao).
- Archive keywords use a shareable exact `tag` filter at `/directory/archive`, with a visible removal control. Keyword search includes the new descriptions, tags, locality and address. Grid and list layouts both support photography.
- Details pages expose direct links, credits and enrichment sources. Original archival text remains intact, and the existing phone-redaction policy remains in force.

## CRM integration and route ownership

The CRM remains at `/directory` and `/directory/:recordId`; the original catalogue stays at `/directory/archive` and `/read/:id`. Shared community cards in discovery/search also receive the source-backed enrichment. No route definitions, homepage composition, topic/action menus, guides or reporting links are replaced.

- `src/content/crm-directory-map.json` explicitly connects 59 organisation records to reviewed catalogue details through their shared Connections API entry identity. The runtime additionally requires the expected original source URL and organisation record type. It never joins on a name or inferred location.
- All seven place/work photos are available in matching CRM rows and details. Reviewed addresses support map searches for five organisations. Other CRM records retain their existing source locations.
- CRM rows expose source-backed work tags plus direct web, participation, Instagram and email actions where the existing research provides them. Enrichment project links supplement the existing routes. Tags combine reviewed labels with all existing source specialisms, with complete detail sets and three-tag row previews. They search the CRM across collections; archive tags remain exact archive filters.
- CRM research JSON, schema, verification statuses, notes, browser storage key, backup/import/export logic and historical/deceased outreach restrictions are preserved. Original catalogue data remains byte-for-byte unchanged. Archive phone redaction remains intact.
- Generic Community/Explore directory links still target the CRM. The release coordinator owns conversion of older topic-taxonomy links to `/directory/archive?topic=...`; this commit does not replace those links or their newer routing fixes.

## Sources and maintenance

`src/content/directory-details.json` is the reviewed presentation layer. Record IDs match the source catalogue; each entry retains its sources. Photographs have a credit, source page, source image URL and local rendition, with provenance sidecars in `public/assets/directory/`. All seven photographs were visually inspected before selection. They remain attributable to their owners, with no open licence asserted.

The existing research CSV was used to identify candidate websites. Current official pages were then checked. COOJ's candidate domain redirected to a parking page and was excluded. Terra Conscious's website currently shows a coming-soon page; the sourced Instagram link is retained. An unrelated CEE carousel image was rejected. No stock or generated photos stand in for undocumented places.

`directory-link-checks.json` records the HTTP checks. Seventeen of 19 non-social URLs returned successful pages in the second pass; Flycatcher and The Future We Need returned 406 after successful first-pass retrievals. Flycatcher was also confirmed through the web reader. Social links were taken from official pages or the sourced research catalogue; they were not treated as proof of current volunteer availability. Check with each organisation before visiting or volunteering.

## Places API

This implementation needs no Google Places API key. Map search URLs work without one; photographs and details are curated from identified sources. A later Places integration could broaden photo and business-detail coverage, but would need place matching, restricted credentials, billing/quota management, required attribution and expiring photo-reference handling. Do not store Google photo names as permanent image URLs. See [Google Place Photos documentation](https://developers.google.com/maps/documentation/places/web-service/place-photos).

## Verification

- TypeScript and production build passed on the CRM plus reporting integration base. Vite reports the existing large-bundle warning (application chunk approximately 912 kB); no new dependency was added.
- All 48 tests passed, including nine directory checks for immutable source data, exact CRM identity joins, map safety, photo provenance, searchable tags, safe direct links and deceased-record restrictions.
- Impeccable source detector: zero primary findings and six advisories. One is the 12px photo credit; the rest are existing CRM typography. The current metadata/caption scale is retained rather than expanding the scope into a CRM redesign.
- Changed source contains no italic/oblique styling or decorative side-stripe containers.
- Final screenshots were recaptured from the production build using `npm run preview`, after the shared-dependency symlink prevented Vite development mode from serving the local font. Production browser checks confirmed `Manrope Variable` loaded (`document.fonts.check` true, status loaded), with no console warnings/errors. No source or configuration workaround was needed.
- CUA browser verification passed for representative CRM results/detail and archive grid/list/detail at 1440px desktop and 390px phone widths. Photos load, no horizontal overflow on inspected phone routes, tag searches retain the source record, keyword clearing restores 153 entries, and archive back navigation preserves list view. Current photos and captions were visually inspected.
- Evidence: `.impeccable/review/directory-integration/` (local, ignored screenshot artifacts). The full finish review requested one fix: preserve all original CRM focus areas on details. Reviewed and source tags now merge without duplicates; details show the complete set and rows show three. Targeted desktop/phone recaptures of Goa Foundation and Anthony de Souza resolved that finding. A subsequent full review of the corrected production-preview screenshot set returned `ship`, with no material fixes for this scoped refinement. No unrelated visual redesign was made.
- No push, merge or deployment has been performed. The coordinated release remains responsible for combined-branch verification and deployment.

## Integration handoff

Use the new integration commit from `codex/directory-enrichment-integration`, not the original `e2c99e8` / `4ab42ab` commits based on the earlier App layout. The worktree is `/Users/zakkrevitt/.codex/worktrees/directory-place-details/ActForGoa`. Original commits remain on `codex/directory-place-details` for history.

Dependencies: merged CRM PR #5 and the extracted `src/components/RecordCard.tsx`; rebased onto reporting PR #6 at `f26ad87`. The new base changes no frontend layout and the built application JS/CSS hashes remain unchanged. No environment variables, Places key, billing service, package additions or schema migration. Shared integration points are small additions in App, RecordCard, public-record, search and CRM; preserve the coordinator’s other search/menu/routing changes when applying them. New modules, enrichment JSON, seven images with sidecars and nine tests are self-contained.
