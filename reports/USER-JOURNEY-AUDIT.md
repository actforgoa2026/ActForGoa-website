# Reader journey and copy audit

Reviewed 23 October 2026. Scope: the existing ActForGoa preview, its shared page templates, all 600 original catalogue records, and the five listed practical guides. This is a local content and route audit, not a new full crawl of actforgoa.org or a live availability check of every organisation.

## Main journey

Home → topic → need → next action. 8 topics, 34 first-level needs, and 4 waste-type choices. Topic pages put large choices before the directory and reading. Waste is first; snake help is one option within Nature & wildlife. The homepage discovery feed still includes all 533 eligible entries. Original article and gallery photographs remain.

### Waste & recycling

- Report illegal dumping
- Get extra rubbish collected: Household rubbish; Furniture or bulky items; Garden or food waste; Electronics or batteries
- Find a recycler
- Start composting
- Report a missed collection
- Organise a clean-up

### Water & environment

- Report a water problem
- Report pollution or sewage
- Collect rainwater
- Protect a river, lake or coast

### Community & rights

- Report a local problem
- Request official records
- Volunteer locally
- Find community support

### Nature & wildlife

- Help an injured animal
- Report tree cutting
- Find wildlife or snake help
- Join a conservation project

### Food & farming

- Start growing food
- Get crop or soil advice
- Register or get farming support
- Report crop damage

### Building & transport

- Build or repair a property
- Report a construction concern
- Report a road or access problem
- Find planning or design help

### Health & wellbeing

- Find health organisations
- Find disability support
- Find mental health support
- Help someone in the community

### Culture & heritage

- Learn about Goan heritage
- Protect a heritage place
- Read local stories
- Share a story or project

## Copy changes

- Removed retrieval dates, crawl explanations, search-engine implementation wording, raw API links, and the site-in-progress footer from the visitor journey.
- Replaced internal verification codes and publication instructions in the five reading guides with short, practical checks. Kept relevant health, legal, availability and historical-document cautions.
- Moved editorial status and detailed review links into an optional About this guide disclosure at the end. The source Markdown, JSON and review register remain unchanged.
- Replaced raw HTTP error codes on downloads with a useful availability message.
- Removed duplicate organisation-availability text. No phone numbers were restored to the frontend; original catalogue fields remain intact.
- Automated phrase scan covered title, summary, body and blocks of all 600 original records. No crawl/retrieval/API/review-process phrases matched there; the clutter originated in the shared templates and authored guide presentation. Original article dates and substantive quoted content were retained.

## Verification

- Production build and 22 automated tests pass. Tests cover every leaf destination, catalogue ID, guide anchor and template path; all topics; guide presentation; search; discovery completeness; source preservation; and frontend phone hiding.
- Browser checks: 1440px desktop and 390px phone menus, nested waste choices, reporting links, service detail/back navigation, input focus, mobile menu, guide contents and two-column table reflow. Topic controls are 100px high on phones. No horizontal document overflow in checked screens. Guide body is 18px with 31.5px leading.
- Service detail/back restored scrollY 386.5 to 386.5 in the checked journey. The mobile menu exit layer now stops intercepting input while closing.
- No italic/oblique declarations or decorative side borders found in source. Impeccable implementation scan: 28 advisory type-ramp findings, no non-advisory findings. Existing and superseded CSS size declarations account for much of the advisory list; current rendered hierarchy was inspected.
- Official government complaint service and GSPCB complaint page were read successfully. No report, booking, email or complaint was submitted. Buttons link to services or information; the site does not pretend to book a collection itself.

## Practical limits

This pass does not certify current service availability or complete the legal/editorial review of the source guides. Original contact records and downloads can be historical; relevant checks remain in reader language. Actual booking, multilingual content and direct message delivery remain separate functionality.
