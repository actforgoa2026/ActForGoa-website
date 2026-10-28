# Live Copernicus validation — 28 October 2026

Continues satellite checkpoint `133bd4e`, with current main `a786df5` merged without conflicts. Both CDSE secrets report ready in this executor, and real client-credentials OAuth succeeds. No credentials or access tokens are included in this report.

## Real provider result

The approximately 1.19 km² test area is the prototype's default bounding box, `[73.82, 15.48, 73.83, 15.49]`, within Goa. The 18 September–28 October 2026 catalog query returned ten acquisitions without truncation. The pair was deliberately selected for low scene-wide cloud cover; this is a retrieval smoke test, not a representative accuracy evaluation.

| Check | Result |
| --- | --- |
| OAuth, catalog, two Process requests | HTTP 200 |
| Before acquisition | 10 October 2026, 05:44:41.348 UTC / 11:14:41.348 IST |
| After acquisition | 20 October 2026, 05:44:40.053 UTC / 11:14:40.053 IST |
| Actual Process timestamps | Exactly match the corresponding catalog acquisitions |
| Actual Process tile paths | Contain the corresponding selected Sentinel-2 product IDs |
| Bundle members | `spectral.tif`, `userdata.json` |
| Numeric TIFFs | Eight float32 bands, 108 × 113 pixels, identical EPSG:32643 grid and 10 m spacing |
| Evalscript output order | B04, B03, B02, B08, B11, B12, SCL, dataMask; SCL/mask values validated |
| Common usable coverage | 100% of rasterized area under the current SCL mask and buffer |
| Paired pixels | 11,925 |
| Exploratory vegetation-loss candidates | 0 at the existing reflectance and 900 m² thresholds |
| Corrected run's provider-reported usage | 0.45450926254445223 processing units, including its catalog request |

This establishes successful retrieval, alignment and numeric comparison for this pair. It does **not** establish individual-tree detection, absence of cutting, field accuracy, or full coverage of the latest ten days. The selected interval overlaps the 18–28 October query window. No Decisions classification ran. SWIR and scene classification remain native 20 m despite the 10 m output grid.

## Failure found and corrected

The original Process request listed TIFF and JSON outputs but omitted `Accept: application/tar`. The real service returned only a TIFF, and the adapter correctly rejected it because acquisition provenance was missing. The fix explicitly requests the TAR bundle. The corrected request returned both members and passed provenance/grid validation. A regression test asserts the header, and another confirms that a standalone TIFF still fails closed.

The initial failed retrieval is preserved locally at `.reports/cdse-live-20261028/process-1.tar` (the bytes are a TIFF despite that diagnostic filename). Its processing-unit header was not retained by the initial diagnostic, so its usage is unknown; do not treat the corrected run's total as the entire session's usage. A separate initial catalog request reported 0.02 units. There were three Process attempts in total: one unbundled failure, then two successful bundled images. No automatic retries or model calls were made.

The new `scripts/validate-satellite-live.py` records each response's safe status/type/usage immediately, saves raw imagery privately, and preserves a failed report. It never records OAuth responses, authorization headers or credential values. Every run requires a new output directory. With no scene IDs it queries the catalog only; with two explicit IDs it retrieves at most two images and stops on failure.

## Evidence and checks

- [validation.json](validation.json): exact runtime source hashes, acquisition provenance, response metadata, TIFF checks, numeric comparison and provider-reported usage. Its `source_commit` is the parent before the correction was committed; the source hashes identify the actual tested files.
- [catalog.json](catalog.json): actual dated catalog results and scene-wide cloud percentages.
- [before.png](before.png) and [after.png](after.png): actual true-colour previews, with acquisition metadata in the validation report. Contains modified Copernicus Sentinel data (2026). These are not synthetic fixtures.
- Python satellite tests: **29 passed**, including the new live-response regression. Existing dependency deprecation warnings remain.
- Node tests: **181 passed**. Production build: **passed**, with the existing large-chunk warning.
- Local HTTP replay of the recorded real CDSE responses: comparison job completes, results match the live numeric evidence, the query-window relation remains `overlaps_window`, classification is unavailable without a key, and another actor cannot read the job. [Replay evidence](service-replay.json). This made no additional provider requests and is not a second live retrieval.
- Packaging: **15 allowlisted files**, hashes checked against both committed source and staged package. [Manifest](package-manifest.json), source commit `ebf570a771396ad126960400faeef9f0ea50b9a8`. No raw imagery, report directories, credentials or environment files are packaged.
- Docker build and runtime smoke: **passed**. Health, unauthenticated rejection, authenticated status, safe missing-provider response, four MCP tools, persistent quotas, interrupted-job handling and SQLite mode `0600` checked. [Container evidence](container-smoke.json). No provider credentials were passed to the container.

The first Docker image built but could not start: Rasterio required `libexpat.so.1`, absent from the slim Python base. The final Dockerfile installs `libexpat1`; its optional build-only proxy CA mount preserves TLS verification and is absent from the final image. [Failed startup evidence](container-first-attempt.json). A subsequent host-side persistence probe could not read the root-owned private database; the final probe runs inside the container without changing its permissions. [Probe record](container-harness-attempt.json).

Raw TAR/TIFF files remain in ignored `.reports/`; they are excluded from the service package. No provider keys were copied into deployment configuration. No merge to main or deployment has been performed. OpenAI Decisions setup, field evaluation, Amche context ingestion/place resolution, statewide indexing, FIRMS and coordinated hosted acceptance remain outstanding.
