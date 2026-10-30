# Public ActForGoa map

The visitor route is `/map` inside the existing ActForGoa field guide. The earlier satellite deployment had inherited staff authentication; imagery is now available without a user account. The backend can remain separately hosted without sending people to its URL.

## Access and data

- `GET /api/satellite/session` automatically issues a signed, HttpOnly, same-site browser cookie and a CSRF token. It creates no staff account and exposes no provider credential.
- Requests retain the same browser URL. Explicit Vercel entries proxy only the allowed satellite paths to `SATELLITE_WEB_ORIGIN`, defaulting to the existing satellite app gateway. That gateway signs visitor identity and uses the existing service credential for the Python API.
- Visitor identities have a separate `visitor_` namespace. Saved comparisons and jobs remain scoped to that visitor. Staff cookies, caller-supplied bearer credentials and actor headers are never forwarded through the public transport.
- The browser cookie lasts 30 days and renews on use. Saved-job retention remains 30 days. Clearing browser site data or rotating the service signing secret removes access to the visitor history. Old staff jobs are not exposed or reassigned.
- Origin, CSRF, request size, route, response size and redirect checks remain. The public gateway adds bounded per-process request throttling. Existing Python provider budgets and global reservations are unchanged; this is not an unlimited anonymous AI endpoint.
- Production gateway origins include its configured public origin and the existing field-guide origin. Additional exact origins, such as an approved staging deployment, can be configured with `SATELLITE_PUBLIC_ORIGINS`. It does not accept arbitrary browser origins.

## Responsive behavior

At 1000 pixels and below, the map and analysis follow normal document flow. Search and draw/location/expand controls sit above the map, with a 360–560 pixel canvas that responds to viewport height. The page scrolls as one document, and all analysis controls remain reachable. The map source/date caption and opacity control stack. The desktop retains an independently scrolling analysis column beside the map. Before/after selectors stack at all sizes; source availability detail remains in an accessible disclosure.

## Shared Earth Engine workspace and grid

`App.tsx` now routes `/map` to the latest `SatelliteWorkspace`, reconciled from the satellite-google owner's working tree at main `2c7e006`. Both entries use Google Maps with the cached Earth Engine Sentinel-2 map layer. No Leaflet/OSM import is selected, and the user explicitly removed the map-view selector: Earth Engine is the only view. The latest tile cache, preview renewal, catalogue cache, minimal Arc accordions and portalled Arc calendars are preserved with anonymous visitor transport.

The control grid uses equal date columns, shared outer edges, 48px controls, 8/12px internal gutters and deliberate responsive reflow. Search and Update/Draw/location/expand form coherent tool rows. The analysis panel uses full-column aligned selectors, paired actions and two-column coordinates. The rule is recorded in AGENTS.md and DESIGN.md and in the user's standing preferences.

## Verification

Before the NOTES merge, all 266 Node tests and 144 Python satellite tests passed; both production builds passed. The combined release owner is running the complete suite after NOTES reconciliation. Regression coverage includes anonymous bootstrap, renewal/expiry, forgery/duplicate-cookie rejection, visitor isolation, CSRF/origin/body/rate checks, protected staff access, Vercel transport, old URL redirect, both map-provider bundles and tile/catalogue caches.

The real anonymous browser journey on the integrated Google/Earth Engine canvas loaded the exact 25 October 2026 Sentinel-2 acquisition for a small public Panaji test footprint, with no model call. Resized browser checks cover 320, 390, 768 and 1440px, equal control geometry, no horizontal overflow, Arc calendar bounds/Escape, and expanded-map exit. Screenshots and geometry are in ignored `.reports/public-map/`. The layout detector reports no findings. Changed source contains no italic/oblique styles or sideflag borders. Physical-phone touch and Safari were not tested. Existing Arc animated-text duplicate-key console warnings remain.

## Local runtime handoff

After the user-authorized NOTES handoff, the specific NOTES Vite process PID 45852 was verified in `/Users/zakkrevitt/code/ActForGoa` and stopped; its checkout was not altered by this map chat. The integrated separate worktree serves `http://127.0.0.1:4197/map`, Python API 8098 and HMR 4184. The old 4183 preview redirects there. The owner's4176 runner is untouched. NOTES has reconciled its requested site changes into the integrated worktree.

The existing public Google browser key permits exactly 4176,4197 and the hosted satellite origin. A temporary 4183 addition was removed after the authorized port handoff; the original three website restrictions and same two API restrictions are restored. No secret was rotated. The local acceptance harness disables paid model providers.

## Release state and sequence

Source is local only on `codex/satellite-public-map`, based on `2c7e006`. The NOTES chat now owns the user-authorized combined release; at this map handoff, nothing has been pushed, merged or deployed by this chat. The primary dirty checkout and other ongoing satellite work are untouched.

Publishing requires the updated satellite app gateway and the updated main-site frontend/API together. The public transport itself does not require a Python change; include the latest `satellite/earth_engine.py` and `satellite/service.py` when shipping the reconciled preview expiry and catalogue-cache improvements. Preserve the existing API database, imagery bytes, budgets and credentials. Include `server/satellite-public.ts` in both gateway/admin packages, preserve existing volumes and credentials, verify a staged same-origin visitor request end to end, and publish through the existing guarded main-site workflow. Verify that old satellite `/`, `/map` and `/admin` public URLs redirect to `https://actforgoa-field-guide.vercel.app/map` and that real public imagery loads there without login. Do not change `actforgoa.org` as part of this correction.

Before main-site publication, configure its `/api/map-config` with the intentionally public `GOOGLE_MAPS_BROWSER_KEY` and allow the exact approved field-guide origin on that key. Preserve the Maps JavaScript/Places New restriction and existing origins. Never substitute the private server key. The local origin configuration is not proof of hosted readiness.
