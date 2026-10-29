# Goa map investigation audit — 29 October 2026

The live product has real satellite retrieval, but the investigation workflow is incomplete. Selecting a place, seeing imagery, asking a question and searching previous evidence were disconnected. At the first audit check, the main review site also served an older application without the satellite route. During this task, PR108 and a newer frontend landed; a timestamped follow-up now finds the map route, but its nested satellite API still returns 404. The standalone workspace is the current working entry: https://satellite-app-production.up.railway.app/map.

This audit preserves the concurrent PR108 place search, current-location access, larger Arc map controls and pointer drawing. It adds a practical first connection: selected-area evidence retrieval with dated citations, Amche intersections, explicit analysis controls and recovery for interrupted jobs. It improves the existing Decisions integration and adds explicit nested Vercel API handlers to address the known catch-all routing depth issue. It does **not** establish live OpenAI accuracy, individual-tree tracking, continuous monitoring or multi-year image comparison.

## Scope and evidence

Baseline: freshly fetched main `f20fc25b88681fc7228002a4ca63b8a1dbab2230`, including merged PR95 (`11582ac`) and hosted CDSE acceptance PR107. Implementation branch: `codex/satellite-query-audit`; this needs a new PR because PR95 is merged.

Evidence includes source and API contract review, fresh public HTTP/bundle checks, pinned public Amche dataset inspection, official provider documentation and offline regression tests. Current hosted credentials were not used to authenticate a browser. No connected browser tool is available in this executor, and no new desktop/phone captures were taken. Layout and interaction acceptance remain outstanding; HTTP 200 is not a successful map workflow. The exact immutable Vercel preview supplied in the browser context redirects public requests to Vercel SSO; its protected route was not inspected or conflated with the main alias. Earlier real retrieval evidence is explicitly historical: [hosted CDSE acceptance](../reports/satellite-cdse-2026-10-29/README.md). No new CDSE, OpenAI or Anthropic request was made for this audit.

[Sanitized live checks and verification](../reports/satellite-query-audit-2026-10-29/README.md) distinguish current observations from earlier hosted acceptance.

## Journey audit

Severity: P0 blocks the intended journey; P1 can mislead or prevent reliable analysis; P2 reduces usability or completeness. These are functional assessments, not measured user-conversion scores.

| Step | Baseline health and evidence | Change or remaining action |
| --- | --- | --- |
| 1. Enter the map | P0 at the first main review check: SPA 200 without the satellite route, satellite status 404. A newer frontend landed during the audit; the route now exists but API status still 404. Standalone serves the actual map/timeline. | Add explicit nested satellite API handlers and a standalone destination when access fails. Combined-site release owner must promote frontend and API wiring together. |
| 2. Understand access | P1: a swallowed session/status error leaves controls silently disabled. Unconfigured natural-language planning is prominent. | Separate sign-in, loading and service failure; retry access. Keep manual dates/topic primary and question planning optional. A verified account is not discarded for an upstream satellite authorization failure. |
| 3. Select a footprint | P1: whole-Goa viewport is offered despite the 25 km² limit; first drawing corner has no visible marker. | Validate viewport on movement; explain zoom/size restrictions. Show first corner, draft rectangle, invalid bounds and cancellation. Coordinates remain a keyboard alternative. |
| 4. Choose dates | P1: default question refers to 10 days while controls use 40 days; 120-day limit is not explained. | Remove the inconsistent question. Validate the ordered period and explain catalog limits before submission. Cross-year comparison remains a follow-up. |
| 5. Inspect observations | Usable foundation: actual acquisitions, explicit load, georeferenced display, opacity and cached timeline. Hosted CDSE acceptance verifies two real dates. | Preserve the full catalog/cache after comparison. Scrubbing still does not create provider work. Scene cloud percentage is not local clarity. |
| 6. Finish/recover analysis | P1: network failure loses the active job reference; users may submit again while work continues. | Actor-scoped job ID survives tab reload. Check job polls that reference; failed/expired jobs are explicit. Resuming restores the correct area **and dates**. This does not provide POST idempotency if the initial job-creation response itself is lost. |
| 7. Ask about history | P0 for spatial questions: history has no area filter; there is no evidence-query endpoint. | Authenticated `/evidence` and optional-area `/history`; actual acquisition intervals, exact/partial footprints, retained findings and source links. Search is explicitly deterministic retrieval, not a newly generated AI answer. |
| 8. Use local references | P1: Amche layers are drawings only; ecology reader links resolve against the wrong standalone host. | Server spatial intersection of pinned Amche sources, separately cited from observations. Ecology reader links use their configured research origin. Optional-source outages retain saved evidence. |
| 9. Interpret tree decisions | P1: one footprint-wide yes/no can be mistaken for the fate of a particular tree; scores are discarded; different numeric/model evidence is sometimes called contradictory. | Stable footprint ID, exact masked-image hashes and explicit scope. Retain validated optional provider scores as uncalibrated. Distinguish review-required differences from internally contradictory decisions. |

## Retrieval design implemented

The application now performs this bounded read-only search:

1. Resolve the authenticated actor from the existing server session. Require CSRF for browser POSTs. Never accept a caller-supplied actor or arbitrary remote URL.
2. Validate the selected Goa footprint, dates and optional topic. Filter completed, retained comparisons by actor, actual observation interval and topic in SQLite. Extract bounded metadata, not PNG bodies.
3. Check exact polygon intersections in a metre-based projection. Reject unknown, malformed or stale result/request footprints. Scan at most 300 eligible records and return at most 8 cards, explicitly reporting truncation.
4. Rank within this scope by spatial relationship, temporal overlap, shared question/finding words and recency. This is lexical ranking; it is not semantic search and cannot reliably understand negation, causal questions or multilingual synonyms.
5. Preserve each original comparison's scene IDs, acquisition dates, common usable fraction, numeric measurements, saved model proposals and source reference. Partial overlap does not turn whole-comparison metrics into measurements of the intersection. Counts must not be added across overlapping comparisons.
6. Optionally retrieve Amche intersections and ecology passages as separate reference evidence. Their source dates and uncertainty remain visible. A source outage is distinct from an empty match list.

No records, unknown coverage and low visibility are different states. A bounded scan with no matches does not claim that all retained history was searched. Saved investigations currently expire 30 days after creation; an old acquisition can be investigated now, but this is not a durable environmental archive.

The information-retrieval direction follows the [OpenAI retrieval guide](https://developers.openai.com/api/docs/guides/retrieval): constrain relevant metadata before ranking, preserve source identity, and evaluate hybrid lexical/semantic retrieval when it is added. A vector index cannot replace geometric intersection or acquisition-time filters. This patch deliberately exposes its simpler retrieval method rather than presenting keyword matches as an AI answer.

The next query layer should consume a typed evidence bundle containing observations, model proposals, dated reference records and background passages. It should cite every factual claim and return unresolved questions when evidence is absent. Treat retrieved text as data, never instructions. Evaluate retrieval with known relevant/irrelevant areas and periods before adding generative summaries. Public ecology retrieval continues to use the scoped read-only endpoint and does not generate research answers or alter research accounting.

## Amche source findings

The map uses OpenStreetMap as its navigable base. Amche supplies reference layers and a link into its full Atlas. Its deployed application lacks the location-sharing bridge present in upstream source, and its Mapbox token is restricted to Amche; it was not copied.

| Pinned collection | Audit findings | Interpretation |
| --- | --- | --- |
| Water Body Atlas 2025, Goa WRD via Amche | 3,854 polygon records; 5 duplicate raw IDs; SHA256 `55c34660d6ea7c820194072b83d54370b0037acfd4d687d95bc7a0551aac25fa` | Reference outlines, not current water extent or proof that all water bodies are mapped. |
| Private forests, June 2026 community collection | 831 multipolygons plus 18 location points; 3 invalid polygons; 46 duplicate raw IDs; SHA256 `2212306378794a01daacc57bbc809788c1f35286d797ca1af85ed2d42b97355a` | Incomplete, partially matched survey records. Point locations do not establish forest boundaries. Presence does not establish current canopy or legal designation. |

The new server adapter fetches only fixed, hash-pinned public snapshots without authentication, redirects or selected-area coordinates. It bounds bytes, features and vertices; quarantines invalid geometry; retains source/date/hash; uses snapshot-plus-row IDs rather than duplicate source labels; and unions intersecting polygons before computing coverage. It returns up to 20 matching records per layer. This joins reference records to the selected area; individual change patches and natural-language constraints such as “inside mapped forests” are not spatially joined yet. Owner names are excluded. Successful parsed sources are cached 24 hours; failures have a short cache. Coverage remains explicitly unestablished.

## Image decisions and scientific limits

The current [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) and [create reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) support the existing `/v1/decisions` integration with image and JSON inputs. The application retains seven fixed questions. Optional confidence and choice distributions are validated and retained; they are not validated satellite accuracy. No review cutoff has been calibrated against Goa field labels.

Both images use the same ground grid and common usable mask. New assessments carry a stable selected-footprint ID, clipped WGS84 geometry, grid CRS/bounds, area, 10 m grid and 20 m native SWIR/SCL resolution, common usable fraction and exact model-image hashes. Common grids do not demonstrate perfect registration. Resampling 20 m bands does not create 10 m information.

The tree workflow should be read as:

| Earlier canopy | Later canopy | Supported interpretation |
| --- | --- | --- |
| Yes | No | Possible loss across the resolvable common footprint, subject to visibility, vegetation type and model/numeric review. |
| Yes | Yes | Canopy exists somewhere on both dates. Partial loss or replacement can still have happened. |
| No | Yes | Possible newly visible canopy/vegetation; type, seasonality and registration need review. |
| No | No | No resolvable canopy identified in the common usable pixels; not proof that no individual tree exists. |
| Any uncertain/refusal | Any | The unresolved decision remains uncertain; missing visibility is never turned into “no”. |

Water and waste model choices describe **later presence**, not when a change occurred. Water has separate dated SCL-based gain/loss measurements, still affected by tides and seasonality. Ordinary litter, individual small trees and construction legality cannot be established with these inputs. Fire assessment currently receives RGB plus aggregate spectral statistics, not spatial NIR/SWIR imagery or FIRMS detections.

Numeric vegetation candidates and model judgments are different evidence types. Zero thresholded patches does not contradict a visual loss proposal. Conversely, vegetation reflectance loss can occur without canopy loss. These cases now require review; mutually inconsistent model answers remain explicit conflicts. Because the model sees numeric statistics, agreement is not independent corroboration.

For stronger spatial answers, introduce stable canopy-patch targets, matched before/after crops and masks, registration checks, seasonal comparators and subsequent-acquisition persistence. Preserve “last clear presence / first clear absence” intervals rather than inventing an event date. Freeze representative field-labelled Goa cases before tuning: harvest, dry-season change, clouds/shadows, river/tidal movement, construction, ambiguous dumps and unresolved small trees. Hold out places and dates; measure precision, misses, abstention and temporal correctness by class/season, including image-only/numeric-only/combined comparisons.

## Concurrent map update

PR108 merged while this audit was being completed. Its main commit `05720cb97e7a752a7a7555956d9d870f164a4f97` is reconciled into this branch, preserving Photon place search, user-requested location, drag/two-corner drawing, expansion/focus behavior and the larger map. New controls use the installed Arc/shadcn components as required by the updated AGENTS instructions. Its earlier screenshots establish that PR's checks, not rendered acceptance of this combined patch.

At 11:58 UTC, the main review frontend did include `/map`, while `/api/admin/satellite/status` still returned404. Existing release documentation identifies plain-Node Vercel catch-all depth behavior; this patch adds explicit satellite action/job handlers using the same proxy pattern as existing posts routes. Hosting configuration and upstream service readiness still need validation after deployment. The standalone also received a newer controls bundle during the task, without this patch's evidence-query UI. The report preserves both initial and follow-up snapshots rather than treating older deployment findings as current.

## Remaining implementation and acceptance

1. **Deploy and inspect this patch:** both existing standalone app and API packages need the new `/evidence` contract. Preserve volumes, named accounts, service tokens and configured CDSE variables. Complete desktop/phone selection, dates, query, low-clarity, partial-overlap, source-outage and job-recovery acceptance. No current visual acceptance is claimed.
2. **Enable actual Decisions:** this executor has no OpenAI binding and hosted acceptance reports Decisions unconfigured. Use the user's existing manual-key choice; do not repeat the rejected in-app creation. After securely configuring `OPENAI_API_KEY`, run the existing one-attempt validator against verified retained imagery. Keep cost/usage and failures recorded. A successful API response still requires field evaluation.
3. **Cross-year pairs:** retain bounded individual catalog windows, but allow separate before/after search windows tied to exactly the same area. Validate each selected acquisition in its own window, chronology and provenance. Bound work to two searches, two cache misses and one explicit classification; do not scan every date between endpoints. Freshness must refer to the after-window only. This is not implemented here.
4. **Acquisition identity:** catalog entries deduplicate by item ID; overlapping tiles can share an acquisition time. Current Process lookup selects a narrow time window rather than the exact catalog item. Reconcile acquisition/tile/version identity and provenance before deduplicating caches or claiming a selected tile was uniquely retrieved. [CDSE catalog](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Catalog.html), [S2L2A metadata](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html).
5. **Long-term/query coverage:** add durable watch areas and observation/event/coverage indexes, explicit retention controls, named-place resolution and evaluated hybrid retrieval. A PostgreSQL/PostGIS spatial/time index is appropriate when the bounded private SQLite scan no longer fits. Do not call the current selected-footprint history statewide monitoring.

There is no new deployment from this audit. The current cloud Railway credential remains bound to `backboard.railway.app`, while the documented deployment endpoint is `backboard.railway.com`; the toolset cannot edit that binding. This is separate from working hosted CDSE access. The combined review alias remains under the release coordinator. See [current deployment handoff](SATELLITE-LOCAL-DEPLOYMENT.md).
