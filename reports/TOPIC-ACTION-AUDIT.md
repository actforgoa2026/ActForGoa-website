# Topic action menus

Verified locally on 25 October 2026. This change extends the existing waste-menu pattern to the other seven topics without replacing the visual system or source catalogue.

## What people can do

Each topic starts with four large choices. Where needed, a second question narrows the situation to two to four options. The resulting page puts specific destinations above brief instructions, relevant organisations and reading.

| Topic | Needs covered | Examples of the next step |
| --- | --- | --- |
| Water & environment | Supply, pollution, rainwater, rivers and coasts | Government complaint service, pollution form, rainwater specialists, coastal authority |
| Community & rights | Complaints, official records, volunteering, community support | Complaint tracking, RTI template and officer directory, legal aid, selected local groups |
| Nature & wildlife | Injured animals, tree cutting, wildlife, conservation | Veterinary services, Forest Department contacts, animal assistance note, conservation groups |
| Food & farming | Growing, soil and crop advice, registration and schemes, crop damage | Soil-testing laboratories, ICAR advice, agriculture office, planning and enquiry templates |
| Building & transport | Building and repairs, construction concerns, roads and access, professionals | Official building forms, project enquiries, complaint service, design and systems specialists |
| Health & wellbeing | Health services, disability support, mental health support, community care | Health-centre directory, specific support organisations, IPHB outpatient services, COOJ public email |
| Culture & heritage | Local heritage, protection, stories, sharing | Archaeology Department, restoration professionals, selected stories, correctly preselected contact forms |

There are 84 rendered routes across these seven trees, including 57 final outcomes. All final outcomes have at least two usable next actions; none sends its primary action to a generic search, directory or library page. Reading-focused culture options intentionally lead to selected stories.

## Implementation

- Curated organisations are resolved across the complete catalogue because original topic tags are incomplete. For example, IPHB can appear under mental health even though its source tag is Community & rights.
- Non-waste action pages show only their explicitly selected organisations. Empty unrelated directories are omitted. Parent menus gather the organisations and resources from their children.
- Next-action buttons use the same large outline-icon treatment as menu choices. Two-choice menus use two desktop columns, and phone menus remain a single column.
- Nested pages offer a direct return to their immediate parent menu.
- Sharing a story or organisation preselects the correct contact-form purpose. The form continues to prepare an email for the user to review and send.
- A general service-enquiry template was added to both the corpus and public download folder. Original records, photos and contact data were preserved; phone-number display remains unchanged and hidden.

## Verification

- Production build passed; 24 tests passed.
- Crawled all 84 routes in the browser at 1280px and 390px widths. No horizontal overflow; every final outcome has actions. At 390px all choice targets are at least 100px tall and all local action anchors resolve.
- Visually inspected full-page desktop and phone captures for all seven topics, including a final-action page for soil testing. Tested contact-purpose selection and returning from a directory record to the chosen need.
- Verified template source/public filename and byte parity, record identifiers, cross-topic routes, section anchors, parent/child paths and source-backed email destinations.
- Fetched all 14 distinct HTTPS action destinations successfully. Their responses were HTTP 200 with content. This establishes reachability, not live service availability, booking capability, legal currency or email deliverability.
- Impeccable detector ran once. Its 28 findings are pre-existing type-ramp advisories in unchanged CSS declarations. No new type sizes, italic/oblique styling or decorative side-stripe containers were introduced.
- A fresh Impeccable finish reviewer returned `ship` with no material fixes after inspecting all fourteen full-page captures. Type, outline controls, open record layouts, action hierarchy and phone layout matched the existing design direction.

Local browser evidence is under `.impeccable/review/all-topics/`: `route-audit-desktop.json`, `route-audit-mobile.json`, `external-links.json`, `detector.json`, and fourteen full-page captures. The desktop route crawl preceded the final omission of empty directories; the phone crawl and final captures include that change.

## Destination notes

The official Goa grievance, Pollution Control Board, coastal authority, PIO directory, legal aid, veterinary, forest, agriculture, ICAR, planning, health, IPHB and archaeology links were checked. COOJ's website returned a holding-page redirect, so the action uses its public email already present in the original catalogue. No email was sent. The unavailable museum website was not used.

These menus help people identify and prepare the next step. They do not submit complaints, make appointments, book services or assert that an organisation can currently respond. Existing source descriptions and supplementary reading remain archival content and may need separate editorial updates.
