# CRM search and filters

Implemented from `origin/main` at `3858a45754bd467c4fdc23598b2f4e9a3c30a782` in the isolated `codex/crm-discovery` worktree. No deployment is performed by this feature branch; the ORCHESTRATOR owns the combined review-site promotion. No new dependencies, data migration, environment variables or backend changes are required.

The directory now exposes work, location and record-type filters, with large Arc buttons for collections, phone/email availability and due follow-ups. Counts predict the result of each choice while retaining the other criteria. Removable active filters and an empty-state action can broaden the collection without discarding the search. A compact-screen action focuses and scrolls to results.

Search prioritises exact and partial names, then identity, work and place matches. It normalises accents, punctuation and phone formatting, retains all query terms and respects an explicitly selected sort. Source text is cached per immutable record in memory. Local notes are not searched or transmitted. Switching collections keeps deliberate filters, and rapid control changes no longer overwrite a previous pending URL update.

## Verification

- All 108 JavaScript tests passed. Four new behavioral tests cover ranking, normalization, invalid enums and counts under combined filters. The 14 CRM/enrichment tests passed again after refinements.
- TypeScript client/server compilation and the Vite production build passed.
- A local Node benchmark over all 3,267 records measured search plus all facet counts at 29.4 ms on first use and a 2.1 ms average / 6.4 ms maximum over 29 warmed runs. These are local measurements, not a field-performance claim.
- Chrome interaction checks at 1440 × 1100, 768 × 1024, 390 × 844 and 320 × 720. No horizontal overflow. Collection and quick-filter buttons measured 52 px high. No radio inputs/roles, italic/oblique computed styles or console errors on the CRM view.
- Rapidly selecting wildlife rescue, Ponda and phone availability retained all three criteria and returned Ali Shaikh and Ankeet Gaude. Opening a record and Back to results retained the query. Removing the locality returned 47 records; Next focused “Showing 26–47”; a new locality reset pagination.
- Searching “maria” ranked Maria Fatima and Maria Gomes before a partial-name match. Combining it with phone availability produced an honest empty community result; Search all records returned the nine government matches while retaining the query and phone filter.
- The phone results shortcut focuses the live result count. Active-filter removal returns focus to Search CRM. Tab reaches the collection buttons. A long locality filter wraps at 320 px, and the empty state offers recovery.
- Existing tests continue to verify enrichment joins, all displayed tag links, source provenance, notes backup/merge rules, due-date rules and filtered CSV export. No source records, local-note schema or detail editing behaviors changed. No live personal notes were modified during UI checks.
- Impeccable source scan: zero primary findings. Two advisories concern pre-existing 38 px detail and 30 px phone headings; neither is introduced by this change. The design sidecar was already stale and was not regenerated as part of this feature.

## Captures and finish review

`desktop-filters.jpg` shows a combined filter and the first result. `phone-filters.jpg` and `phone-results.jpg` cover the compact flow, `tablet-filters.jpg` the intermediate layout, and `narrow-long-filter.jpg` long criterion wrapping. Captures were made from the local Vite development build in Chrome using viewport emulation, not a physical phone.

Finish verdict: ready for coordinated integration. The existing warm paper, green, upright Manrope, source cautions and open record rows are preserved. No decorative side stripes were added. Physical-device and other-browser checks were not performed. This report and the PR do not establish a live release.
