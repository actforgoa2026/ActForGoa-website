# Hosted satellite imagery verification — 29 October 2026

Live workspace: https://satellite-app-production.up.railway.app/map

The user explicitly authorized configuring newly saved CDSE credentials and completing hosted imagery, timeline and comparison checks. No application source changed during this operation.

## Deployment identity

| Service | Source | Railway deployment |
| --- | --- | --- |
| Satellite API | `11582ac536b92937fa881a7fc9d9db8b83f6205a` | `9014df8b-69de-4178-8072-135f96239875` |
| Satellite app | `b0fadeee3bcaf1daa88f2adf71fa6b28ceca14f7` | `4bd7fc4b-8d60-487b-8219-bc978d07324f` |

Both deployments are successful. The API reused its existing container image, digest `sha256:3abe2aff6916c3b22ed76d5156a456fb5b18ed218d50cd98a7fe9c86ad31edd2`. All 14 satellite runtime files match the accepted package. The accepted local integration checkpoint was `1c4ac7c0a855f0ff8a44ef3063f09ab9e327014c`; a subsequent connector refresh found main at `21e4dcac46b4299d586b79e229ff4faa3dc46fc4`. This documentation handoff starts from that newer main and preserves PR #105. Its separate review-site release is not part of this satellite credential operation. The app package and public assets retain their previously verified hashes.

## Actual hosted checks

- Real CDSE OAuth validation returned HTTP 200 before configuration. Values were transferred through CLI stdin and never logged. Authenticated service status now reports `imagery_ready: true`.
- A new 1.19 km² area near Ribandar/Chimbel, bounding box `[73.865, 15.492, 73.875, 15.502]`, returned ten acquisitions for the actual browser search window September 19–October 29. The browser automation's attempted narrower date fill did not change the native date controls; the effective window and response are recorded without claiming otherwise.
- Explicit loads of October 20 and October 25 produced real Sentinel-2 rasters and 109×113 map-overlay/comparison images. Provenance matches each selected catalog acquisition, including Process tile identifiers and retrieval timestamps.
- October 20 was approximately 98% locally usable and October 25 approximately 42%. Common usable coverage was 41.1%; the comparison correctly saved an inconclusive result and did not claim an environmental change.
- Desktop 1440×1000: real overlay, acquisition labels, earlier/later buttons, keyboard slider navigation, two-image comparison and source captions passed.
- Phone-sized browser 390×844: fresh named-account login, saved-history search/reopening, dated overlays, earlier/later buttons, image loading from the server cache and stacked comparison images passed. This is browser viewport verification, not a physical-device or touch-gesture test.
- Both viewport checks had no horizontal overflow or italic/oblique DOM text. The phone check recorded no browser console errors. Existing source/style verification remains applicable because frontend bytes did not change.
- Public map and API health return 200. Anonymous API status, app satellite status and staff session endpoints return 401.

## Usage and preservation

Production reservations increased from zero to five catalog operations, two observation operations and one comparison. The initial catalog, two observation validations, comparison validation and phone catalog refresh account for all five searches. The result lists fit in one catalog page each. Exactly two new observation jobs completed and two raw raster cache entries exist. Their bytes and provenance remained unchanged through comparison and the phone cache reload, with no third retrieval or observation job. No AI planning or classification request ran.

The hosted runtime does not persist CDSE response processing-unit headers. The exact provider PU charge was therefore not measured; request counts are not presented as a currency charge. One separate pre-configuration OAuth validation was performed; the service authenticated independently for its imagery requests.

The original saved comparison's content digest is unchanged: `c0e0f610dc50b2d69a0bf0f0b749142f8a5a4ac5f7d9b520db678e9a840b0bd7`. A fresh active-database backup was made before configuration, with SHA-256 `20c796367adf072aff2de54fe191644e8ace1fb74aa4bf638ef74c9c8f61d302`. Original volumes and service tokens remain in place, with one running replica per service. The staff account was verified by signing out and signing back in. Temporary SSH access was revoked and its local key files removed.

Optional satellite question interpretation, image classification and ecology-library integration remain unconfigured. Statewide monitoring and field-validation claims remain unavailable. Existing recorded results retain their recorded labels; the new hosted comparison is separate.

The combined review-site frontend, research runtime/accounting and actforgoa.org were not changed. Other agents and heartbeat remain paused. Private detailed evidence, audits and desktop/phone screenshots are retained locally in `.reports/satellite-cdse-20261029/`.
