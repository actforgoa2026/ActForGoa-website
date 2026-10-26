# Community CRM

Open `/directory` from Community in the main navigation. `/crm` is an alias. The original website directory remains at `/directory/archive`.

## Find and review records

The snapshot contains 499 community records and 2,768 government records. Participation shows the 28 records with linked participation routes, rather than counting them as extra contacts.

Search names, organisations, work, villages, phone numbers or emails. Filters narrow by record type, focus, locality, activity evidence, source review, available contact methods, outreach stage or follow-up date. Search, filters, sorting and pagination are in the URL. Opening a record and returning preserves these choices.

Each record keeps public phone/email details, websites, social links, available source photographs, related records and source URLs. Shared office and referral routes retain their research labels. Activity evidence, source verification and your relationship stage are separate. Government listings do not independently establish current tenure or environmental work. Historical, undated and unresolved records keep their original distinctions. Contacts have not been called or email-delivery-tested.

## Browser notes and backups

Outreach stage, notes, last-contact date and follow-up date save as you edit, under `actforgoa.crm.v1` in localStorage. There is no server sync or sign-in. Storage belongs to this browser profile and exact site origin, including the port on localhost. Clearing site data removes these notes. Moving from a local preview to a deployed URL requires a backup import.

Use Export backup to download a versioned JSON file containing all local relationship data. Import backup validates the file and previews its record count before applying it. Existing notes are kept by default; select Replace matching notes to use the imported values for conflicts. Records absent from the current research snapshot are retained for later restoration. A malformed backup does not change stored notes. If browser storage is unavailable or full, the app shows an error rather than claiming the edit was saved.

Export results downloads all matching records, across pagination, as CSV with research fields and relationship fields. Formula-like values are prefixed with an apostrophe for spreadsheet safety, including international phone numbers. Use JSON backup for exact note restoration; CSV is for analysis and transfer to a future CRM.

Follow-up due dates use Goa time. Closed and Do not contact stages are excluded from due reminders. Deceased contributors are historical records and remain excluded from outreach even after importing a backup.

## Refresh the research snapshot

`scripts/publish_crm.py` reads the immutable `research/releases/2026-10-23/` CSVs and writes `public/data/crm.json`. It preserves the 37 source fields and stable record IDs, adds a community/government collection field, and validates uniqueness and participation references. The source CSVs are not modified.

```sh
python3 scripts/publish_crm.py
npm test
npm run build
```

For a later release, deliberately update the script's source version and expected counts, the displayed research date, and snapshot tests. Preserve IDs so existing notes continue to match. Review source changes before publishing. This feature does not perform a fresh crawl or silently advance verification dates.

## Verification on 25 October 2026

The production build and 28 tests passed. Browser checks covered search, combined filters, empty results, government and participation collections, pagination across reload, public contact links, notes/stage/date persistence, JSON backup download and restore with conflicts kept, invalid-backup rejection, and the downloaded five-row filtered CSV. Layouts were inspected at 1440px, 390px and the 508px app panel; no horizontal document overflow was observed. Browser console checks returned no warnings or errors. Full local screenshots and the finish review are under `.impeccable/review/crm/`.

Storage quota and denied-storage behavior are implemented but were not manually simulated. Same-origin tabs share stored notes, but simultaneous edits are not a team collaboration system. Research activity and contact availability remain those of the dated source snapshot. This implementation has not been deployed.

The finish review requested one pagination fix. Next/Previous now move keyboard focus and scroll to the result count, with the first new row visible below the header. Desktop and phone browser checks confirmed this behavior, and the reviewer scored that finding resolved with disposition `ship`. The detector reported no primary findings and five typography advisories; the compact CRM scale remains a scoped design choice.
