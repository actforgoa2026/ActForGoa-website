# Local design follow-up — 30 October 2026

This follow-up was implemented and tested locally in `/Users/zakkrevitt/.codex/worktrees/actforgoa-design-iteration`. The user subsequently explicitly authorized shipping it. Release status and exact deployment identities are recorded separately; the verification below describes local acceptance.

## Implemented

- Topic submenu links retain Arc structure and use 24px labels on desktop and 20px on phones, with natural wrapping.
- The approved stippled landscape continues from the circular homepage into the topic section and appears beside catalogue headings. Map, chat and form workspaces remain compact.
- `/map` is a bounded workspace: persistent map on the left, independently scrolling analysis on the right. The Arc segmented control switches between Analyse, Results and Saved evidence. Opening a comparison reveals its results in this panel; Before/After controls switch the actual map image. On narrow screens the map sits above the scrolling tools.
- Official Arc DatePicker and Calendar sources replace native date fields for imagery searches and saved-history filtering. A documented portal adaptation prevents clipping inside the panel. Day serialization preserves the selected local calendar date.
- Map footer/preview content no longer extends the task into a separate scrolling page. Provider selection is unchanged: integrated development uses Leaflet/Photon as the basemap; Google Earth Engine supplies the satellite acquisitions. Standalone builds retain their explicitly configured Google map.
- `npm run dev:check -- --satellite-only` checks local access, imagery readiness and history independently of hosted corpus AI.

## Verification

Main and standalone production builds pass with existing bundle-size/config-loader warnings. Eleven focused Node tests pass, covering date serialization, imagery job recovery/cache boundaries, timeline ordering, area validation and provider build isolation. Calendar day tests also pass under America/Los_Angeles to detect UTC shifts. Typecheck and diff checks pass. The Impeccable layout scan returned no findings; changed UI source has no italic/oblique declarations or decorative side stripes.

Rendered checks cover 1280×720 and 1024×768 desktop workspaces plus 390×844 phone. At these standard sizes, document width and height match the viewport; panel scrolling leaves the map in place. A checked 844×390 landscape fallback uses normal document flow so the tools never collapse; its calendar remains within the short viewport. Calendar opening focuses the selected day, arrow keys navigate, Escape restores the field, and Tab after Clear reaches the next field. Phone calendars stay within the viewport and above map controls; expanded-map entry/exit works. Results and saved evidence remain alongside the map. Landscape and long submenu labels were checked at desktop and phone widths.

A bounded authenticated local Earth Engine test retrieved real Sentinel-2 observations for a 0.107 km² test footprint on 8 and 13 January 2026. The numeric comparison completed with 100% common usable coverage. Before/after toggling switched the map overlay correctly. These are historical acquisition dates used for functional testing, not a claim about current conditions or scientific field validation. No model request was made. Optional AI image assessment remains unconfigured locally.

Ignored evidence: `.impeccable/review/local-map/`, `.impeccable/review/landscape-*`, `.impeccable/review/topic-labels-*`, and `.reports/dev/earth-engine-livecheck.json`. Private credentials and account data remain outside Git.
