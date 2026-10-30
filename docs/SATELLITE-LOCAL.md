# Local satellite workspace

Run from this checkout:

```sh
npm run dev:satellite
```

Open http://127.0.0.1:4176/map. Vite updates the UI as files change; uvicorn reloads the satellite Python service. Ctrl+C stops both. Ports 4176 (UI), 4177 (hot reload) and 8096 (API) must be free. This workflow does not deploy or merge anything.

The launcher uses the existing `.venv` with `requirements-satellite.txt` and installed Node dependencies. It reads the already-saved browser key from `~/.config/actforgoa/google-maps-browser.key`, Earth Engine authorization from `~/.config/earthengine/credentials`, and `OPENAI_API_KEY` from `~/.config/actforgoa/openai.env`. Secrets stay on the server; only the deliberately public, website-restricted browser key reaches the client. Google Cloud project: `actforgoa-translation`. The browser key permits Maps JavaScript and Places API (New) on the hosted origin and the user-approved `http://127.0.0.1:4176` origin. Use that exact local address.

The launcher creates a browser visitor session automatically, without an account. It binds all three ports to loopback, rejects foreign Host/Origin and cross-site API requests, and keeps the visitor session/CSRF checks on the satellite proxy. Browser sessions, saved comparisons and raster cache are isolated under ignored `.reports/satellite-local/` with private permissions. Hosted users, data and credentials are unchanged. The launcher refuses a production/Railway environment. It does not connect the ecology-library service or load a Google server key for optional current weather/air quality; those hosted capabilities are separate from the local Earth Engine and Maps workspace.

## Investigation flow

- Earth Engine's dated cloud-masked Sentinel-2 median is the navigation overview. It is labelled and never used as the analysis input.
- Drawing a rectangle keeps the selection visible, searches the selected period and loads its latest exact acquisition. Progress and errors appear on the map.
- Real Arc date pickers choose the search period. Google Streets and Places search remain available for navigation.
- On desktop, dates and analysis controls occupy a scrolling panel beside the map. On phone, these sections stack.
- Suggested before/after dates use lower scene cloud cover on distinct days. Scene clouds are only a hint; local common clear coverage decides whether AI can run.
- **Analyse change with AI** retrieves exact observations, computes spectral evidence, and calls OpenAI Decisions when coverage is sufficient. The change synopsis reports completed, skipped or unavailable AI explicitly. The text combines checked measurements and discrete image assessments; it is not a second freeform model response or field verification.
- Completed comparisons remain in the local investigation history. Links in the synopsis reveal their source images, visibility, numeric evidence and model decisions.

## Verified on 29 October 2026

The user's initial 20 September/25 October pair had 0% common usable coverage and correctly skipped AI. A new comparison over the same selected footprint using 10/20 October had 100% common usable coverage. OpenAI Decisions (`gpt-6-luna`) completed seven image decisions. It proposed canopy present on both dates and no visible canopy loss; the numeric check found no qualifying vegetation-loss patches. These results do not rule out smaller changes or individual-tree removal.

Own browser drawing check retained its rectangle, returned 20 acquisitions and automatically loaded the exact 25 October image. Desktop (1440 × 900) and phone (390 × 844) checks covered Arc calendar rendering, future-date bounds, Escape focus return, saved results, synopsis evidence links, map imagery and overflow. 142 Python satellite tests, 226 Node tests and the production build passed. Local Host/Origin/CSRF rejection and three loopback listeners were verified. No deployment, push or merge was performed.
