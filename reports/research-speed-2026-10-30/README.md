# Research speed release — 30 October 2026

The three public starter questions now have reviewed saved answers. Fresh questions and follow-ups still invoke the production Claude Agent SDK. Batched search/read reduces tool round trips, and metadata-only timings separate provider, tool and total duration. The frontend sends one answer request instead of an extra preliminary search.

## Reviewed runtime and acceptance

- Backend source: `333cb3bda02773ba301ba56a559102adb1bc574c`.
- Railway deployment: `96bfcdbe-22e5-4ab9-9f16-3986ad1ac2f7`, existing research service and persistent volume.
- Source/package audit: all 28 runtime files match the clean package. No corpus or usage ledger was included in the service package.
- Tests: 231 research Python tests, 259 Node tests, TypeScript check and production build passed. The release wrapper repeats Node tests/build before frontend promotion.
- Impeccable context, optimize and polish checks completed. Eighteen routes rendered at 1440×1000 and 390×844, with additional 320×640 and 768×1000 research checks. No horizontal overflow or italic styling in the checked research UI. Template preview and PDF export passed; no real private report was submitted.

| Reviewed starter | First generation, wall time | Saved answer, public API | Model calls on saved answer |
| --- | ---: | ---: | ---: |
| Wetland protection | 13.328 s | 0.522 s | 0 |
| Panchayat waste | 24.248 s | 0.513 s | 0 |
| Khazan water management | 16.667 s | 0.371 s | 0 |

These are individual observed requests, not population percentiles. The cache improves these exact starters; arbitrary questions still require live research. Saved paragraphs and citations are identical to the reviewed answers. Cache hits were verified to leave production attempt/spend counters unchanged. Runtime, corpus generation, source database and public CRM changes invalidate approval; entries expire after seven days. Follow-ups, scoped queries and user conversations do not use the starter cache.

The combined runtime includes PR #124's official flood guidance. Hosted follow-up `9a89dbf1a4c449daa4f43c5bef10d2e6` followed the cached khazan answer, called `search_and_read` twice and `read_official_guidance` once, made four metered model calls, and completed in 19.784 seconds. Manual review compared its claims with original SAPCC pages 20–22 and 76–78 and the verified official summaries. The answer separates proposals from implementation, labels the separate agriculture policy, and cites official preparedness independently of the climate plan. Desktop/phone rendering and an exact highlighted SAPCC page-77 passage passed. General advice remains distinct from live alerts.

## Corrections found during hosted acceptance

All failed attempts remain charged in the production ledger:

- `b9ff91d64a914bdca09b65f581cc6145`: unread discovery citation rejected; discovery IDs are now withheld in every scope until a page is read.
- `cc36d01829f74ae19bfd80d57d269594`: expanded official-guidance hash rejected; duplicate full checksum is no longer exposed in the model tool payload. Original source checksum and exact-ID validation remain intact.
- `95392b5fb6494765bb1b7eb98b924092`: exact citations passed, but manual review rejected a mixed-source opening paragraph. The prompt now requires a library-only opening and separate official guidance. The subsequent corrected-runtime run above passed.

Accepted starters were carried forward only after explicit re-review under the final fingerprint; they were not regenerated. No development ledger was used.

## Preservation and limits

Generation `20261030-sapcc-native-v2` remains intact: 1,174 original files, 21,534 pages and 79,548 chunks. All original checksums and the source database checksum are unchanged. The pre-release production SQLite backup exists on the persistent volume. Every baseline reservation/import row remains present, and previous daily counters are unchanged.

After acceptance: 48 model attempts on 30 October; October conservative reservations total $45.052337 of the existing $50 cap. These reservations are not the provider's final billed cost. Limits remain 500 attempts/day through October, then 100/day and $5/month in November. No budget increase or ledger reset occurred.

Protected local evidence is in `.reports/research-speed-20261030/`: `final-audit.json`, `timing-results.json`, accepted answer envelopes, route screenshots, `accepted-followup-desktop.txt`, responsive follow-up screenshots and the exact original-citation screenshot. Provider logs retain metadata only. Rollback backend deployment: `986679ef-46fd-4a65-9086-01085913e051`. Frontend promotion and final public verification are recorded in issue #89 after `release:review` completes.
