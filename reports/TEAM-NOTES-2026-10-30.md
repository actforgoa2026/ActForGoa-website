# ActForGoa team notes implementation

Local preview: http://127.0.0.1:4197/

Published and verified: https://actforgoa-field-guide.vercel.app/. See the [final combined release record](notes-release-2026-10-30/README.md) for exact source/deployments, public browser acceptance, security configuration, rollback and remaining team dependencies. Earlier local-only statements below describe their dated checkpoints.

The site now puts climate and cultural resilience, greener everyday choices and community participation first. Reporting remains available after affirmative actions. The user subsequently authorized shipping the integrated preview. Release checks and deployment records follow in the combined release report; earlier local-only checkpoints below are historical.

## Action plan and implementation

| Team intention | Implemented locally | Where to review |
| --- | --- | --- |
| Restore the eco mission and shorten the homepage | Exact requested opener, “Love Goa. Give back to Goa.” tagline, static heading, no floating-image carousel, three requested shortcuts. The homepage ends with field-guide navigation and optional Instagram updates. | `/` |
| Make the heading work on phones | “Helping people to” is one smaller line above “Care for Goa”. Checked at 320, 390, 768, 1200 and 1440 pixels without a stranded “to” or horizontal overflow. | `/` |
| Keep the established Arc UI | Actual Arc SearchField, Button, Input, Textarea, Alert, ConfirmMorph and responsive SiteHeader. Navigation links share Arc Button styles and motion through a small native-link extension. | Homepage, topic menus, heritage form |
| Update the main topics | Fourteen topic menus plus the Climate Action Plan shortcut cover all fifteen requested areas. The older topic URLs and useful deep links remain available. | Homepage topic buttons |
| Put giving back before reporting | Positive choices come first. Reporting branches appear below a separate problem-help heading. Each topic has context, schemes, organisation signposting and a contextual improvement link. | `/topics/waste`, `/topics/water`, `/topics/nature` |
| Consolidate waste actions | Segregation, composting, recycling, reduction, zero-waste options, pre-loved options, organise or join a clean-up, local initiatives, circularity and recommendations. One reporting branch covers dumping, missed collection and extra collection. | `/topics/waste` |
| Expand biodiversity actions | Conservation by habitat, native tree planting, experiences, monitoring, local initiatives and animal help. Tree-cutting reporting includes the requested archived infographic and process links. | `/topics/nature` |
| Care for water and participate in local planning | Recharge guidance, reducing pollution, testing, habitat care, Panchayat and Gram Sabha information, development planning and initiative enquiries. | `/topics/water`, `/topics/community` |
| Build and travel responsibly | Construction footprint, waste disposal, cooling, car pooling, female taxi information, eco-building professionals and access support. Historical service information is labelled; current availability is not promised. | `/topics/planning` |
| Combine health support | Health and mental health share one branch. Air pollution and waste-burning health information are available separately. | `/topics/health` |
| Celebrate Goan heritage | A story form with an optional Google Maps pin, source credits, browser draft saving and removal with Undo, and an email prepared for team review. No story is sent or published automatically. | `/topics/culture/celebrate`, `/heritage/share` |
| Add the remaining green topics | Responsible tourism, local food and farming, carbon reduction, flooding and fires, green business, laws and responsibilities, education and courses. | Corresponding homepage topics |
| Collaborative Action | Homepage, header and initiative links go directly to `https://actforgoa.lovable.app/`. The temporary local `/collaborate` URL also redirects there. Lovable content is not imported into the public site, following the final instruction. | Explore the field guide; Take action menu |
| Optional Instagram feed | Arc disclosure button loads the real ActForGoa profile embed. Rendered posts were verified in the browser. | End of homepage |

## Google Maps

The heritage flow uses Google Maps. Legacy Leaflet source remains for compatibility, but the public heritage and satellite routes use Google. Google Maps now loads an interactive map: click or tap to place a pin, drag to adjust it, or use the keyboard and “Pin map centre”. The form has no coordinate-entry or copy/paste step. Pins are included in the prepared email and restored with browser drafts. Removing a pin also clears it from the map. Failed map loads retain the story and offer a retry.

The local preview uses the existing website-restricted “Satellite browser maps” key in the `actforgoa-translation` Google Cloud project, where Maps JavaScript API is already enabled. The exact origin `http://127.0.0.1:4197` was added to its allowed websites. The existing two origins and API restrictions (Maps JavaScript and Places API New) were preserved. No unrestricted or server key is exposed. The integrated preview reads the existing public browser key server-side from its local configuration and exposes it through `/api/map-config`. Heritage and satellite share one Maps SDK loader. The restricted browser key is intentionally public; private server credentials stay server-side. Production uses `GOOGLE_MAPS_BROWSER_KEY` and the exact field-guide website restriction. No billing settings changed.

Verified actual map clicks, keyboard dragging with changed email coordinates, stale-email clearing after moving a pin, save/reload restoration, pin removal, and the centre-pin control. Desktop and 320px/390px layouts have no horizontal overflow or italic text. Pointer dragging and two-finger gestures on physical phones remain untested; keyboard dragging exercised the same Google marker drag-end handler. Screenshots and logs are in `.reports/team-notes-2026-10-30/`.

## Details still needed from the team

- Current coordinators and participation links for the named Innovation Labs, Water Collective and Wise Progress Hub. Their menu entries provide enquiry routes and the Collaborative Action site while these are pending.
- The latest approved Green Viksit recommendations. Existing 2025 archive links remain explicitly labelled.
- Current pre-loved store listings and confirmation of female-driver service availability. No unverified booking claims or contact details were invented.
- Editorial review of new Hindi and Konkani copy. New English phrases are explicitly tracked in `src/content/mission-translation-pending.json`; existing translations remain intact.
- A future editorial publishing workflow if heritage stories should become publicly visible map pins. The current form prepares a review email and supports a browser-local draft.

## Validation

- At the original NOTES checkpoint, 96 automated tests passed, including topic destinations, preserved deep links, affirmative-before-report ordering, home-search routing, translation fallback accounting, draft handling, pin validation and email encoding.
- TypeScript checks and production build passed.
- Rendered all fourteen topic roots at 320px after the Arc restoration, with no horizontal overflow or computed italic type. Checked the homepage at five widths from 320px to 1440px.
- Verified desktop navigation, mobile sheet and keyboard Escape/focus behavior; interactive Google Maps and pin-to-email flow; Instagram embed; waste reporting choices; tree-cutting infographic; contextual improvement form.
- Impeccable scan found no non-advisory issues. Remaining advisories refer to existing Arc radii/theme values and typography; the established paper-and-green design was preserved. Changed source was checked for italic/oblique styling and decorative side stripes.
- Synthetic browser draft removed after testing. No email sent, public story published, live deployment performed, or Device Hub opened.

Browser checks use desktop viewport emulation, not physical iOS or Android hardware.

## Integrated preview and release authorization

The isolated `ActForGoa-public-map` checkout combines these notes with the latest public Earth Engine workspace, current Arc/Figtree components, SAPCC, CRM and research features. Port4197 serves that integrated source; port4176 stays running. Shared-SDK heritage-to-map-to-heritage navigation and an actual Google Maps pin click passed. The integrated main build passed; 274 of275 tests passed on the first full run, with the transient remote MCP test passing both retry cases. Final exact-tree validation is recorded separately after reconciliation with fresh main.
