# NOTES and public map release

Published and independently verified on 30 October 2026 at https://actforgoa-field-guide.vercel.app/.

## Published source

- NOTES/public map: [PR127](https://github.com/actforgoa2026/ActForGoa-website/pull/127), merged as `50291720b886f84eca32ae7ac2bd8dfcfe15938c`.
- Phone map/header and expanded-map layering: [PR129](https://github.com/actforgoa2026/ActForGoa-website/pull/129), merged as `87207f0fd73cf9d37ea5b42c7a36aebb2a6e1769`.
- Final runtime commit: `7ede7b29255933a468149635972a76c0645bf195`.
- Final runtime tree: `a78f0b813cc3fc13579281b93f8d1720e5612657`.
- Current Vercel deployment: `dpl_E4dHjcZFCzeiR1wwbvBysrAwb3vy`.
- Immutable URL: https://actforgoa-field-guide-pzfrsab1j-zakkrevitt-gmailcoms-projects.vercel.app.
- Immediate frontend rollback baseline: `dpl_59Hcgb6KL2cpydMBJksKg6sv8jUL`.

The initial NOTES promotion was `dpl_dpggLDGjzCbYL1PauqpbTTS5iXCi`. Subsequent user-authorized `/AI` work preserved those changes. The final AI composer release included the merged map-layering fix and passed the unchanged guarded release workflow. Vercel API metadata independently confirms the final commit/tree above; public browser verification confirms the actual behavior. No additional deployment was necessary after that combined promotion. Original WordPress `actforgoa.org` remains unchanged.

## Team intentions delivered

The [team-notes action plan](../TEAM-NOTES-2026-10-30.md) maps every requested area to its implementation and remaining team dependencies. The standard homepage uses the exact opener, “Helping people to Care for Goa”, the requested three mission lines, normal rectilinear header and established Arc/Figtree components. The mobile heading no longer strands “to”. Fourteen topic menus plus the Climate Action Plan shortcut emphasize practical affirmative actions before reporting, with schemes, partner signposting and contextual improvement links.

Waste actions include join/organise a cleanup, zero-waste and pre-loved options, and one reporting branch. Biodiversity includes habitat conservation, planting, experiences and the archived tree-cutting process infographic. Health support is combined; responsible construction, transport and female-driver information retain availability caveats. The heritage form supports a Google Maps pin and a browser draft, then prepares an email for team review. Collaborative Action links directly to https://actforgoa.lovable.app/ as finally requested.

Current Innovation Lab/collective coordinator links, approved Green Viksit recommendations, current pre-loved/female-driver service confirmations, and new Hindi/Konkani editorial review still depend on the team. Enquiry routes and labelled historical sources are provided. Heritage stories do not publish automatically; a public publishing workflow remains future scope.

## Google Maps and satellite services

The user explicitly approved the exact `https://actforgoa-field-guide.vercel.app` website restriction. It was added to the existing browser key while preserving localhost4176/4197, the existing Railway website, and the Maps JavaScript / Places API (New) restrictions. The restricted browser key is intentionally public through `/api/map-config`; private provider credentials remain server-side. No key rotation or billing change.

Heritage and satellite share one Google Maps SDK loader. Heritage users click/tap to drop a pin, drag to adjust, or use keyboard controls and “Pin map centre”; coordinates need not be copied. Actual live map clicks created a removable pin. Synthetic unsaved pins were removed after verification; no story email or report was sent.

Satellite runtime source `57a3eb8b4398b1c0fec8ec13e4d06b0c31745b42` was deployed by the coordinated backend owner:

| Service | Current deployment | Previous deployment |
| --- | --- | --- |
| Satellite API | `fa0b1552-b5e6-46b2-80e4-8d5ebec46020` | `2454a251-1b10-4deb-82c3-b3113243ba03` |
| Public/staff gateway | `7b9a57c4-3567-4a24-a2a2-635d47db9f42` | `1beec385-cb3a-4a58-be91-374d234ebd3e` |

The owner verified all packaged runtime hashes, fresh SQLite backup integrity, preservation of the original jobs/observations and staff accounts, unchanged configuration/credential hashes and nondecreasing accounting. Signed visitor sessions, visitor isolation, renewal, CSRF/origin rejection and staff authentication checks passed. Temporary Railway SSH access was revoked. Private backups and evidence are outside Git.

Live acceptance retrieved actual Sentinel-2 imagery acquired on 25 October 2026 at 11:14am IST, showing 10 acquisitions, 95% locally usable pixels and 5% cloud/shadow uncertainty for the selected area. A later final browser check confirmed the anonymous Google/Earth Engine overview. No satellite AI analysis ran. Existing evidence, corpus, reporting data and browser-local CRM ownership were preserved.

## Verification and limits

- All 279 Node tests and the main production build passed before promotion. The satellite owner verified 144 Python tests and the standalone build.
- The release guard checked research readiness, scoped collections, admin/editorial and staff satellite authentication, public satellite session/readiness/job routes, map configuration, public journal, newsletter content types and MCP before promotion.
- Initial guarded attempts safely stopped for a transient GitHub fetch timeout and then a newer main commit. No failed guard was bypassed. The later guarded composer release included all merged source.
- Forty final public renders cover 20 routes at 1440px and 390px: home, explore, waste topic, directory/archive, emergency, report, farming guide, template, research/all/legal/ecology, admin, blog/archive, an actual source document, heritage, map, climate plan and `/AI`. Async pages were awaited and rechecked after their initial loading views. No horizontal page overflow or computed italic type was found.
- Rendered screenshots were inspected. Live phone scrolling confirms the site header stays above map controls. Phone/desktop expanded maps and the portalled Arc calendar render above the header and exit correctly.
- Earlier focused checks covered all 14 topic roots at 320px, five homepage widths, navigation/keyboard focus, PDF exports on desktop/phone, topic search, report-step behavior, heritage draft restore/removal/Undo, keyboard pin dragging and pin-to-email content. No real report/story was submitted.
- Actual Impeccable context/playbook/craft-floor workflow was used in the local executor. Changed source and rendered output were checked for italic/oblique text and decorative side stripes. The established design was preserved.
- Existing Arc animated-text duplicate-key warnings and Vercel's nonfatal `vite/client` function-transpilation diagnostic were observed in prior checks; successful builds and actual service probes do not imply a warning-free console.
- Physical touch devices and Safari were not tested. Device Hub was never opened. AI answer accuracy and current third-party service availability are not established by these UI checks.

Protected local evidence is in `.reports/notes-integration/`: `public-browser.json`, `public-{desktop,phone}-contact.jpg`, `published-home-{desktop,phone}.png`, `published-google-pin-phone.png`, `published-phone-header-fixed.png`, `published-desktop-expanded-calendar.png`, `live-metadata.json`, test/build logs and release logs. Backend evidence is in the satellite owner's `reports/satellite-combined-release-2026-10-30.md` and ignored `.reports/satellite-combined-release-20261030/`.

Local4176 and integrated4197 were both still listening and returned HTTP200 for `/map` after final public verification. The shared dirty primary checkout was not reset or sweep-committed. This release record is documentation only and excluded from deployment uploads.
