# Local development and testing

Run from the isolated design checkout with `npm run dev:full`. The current preview is [localhost:4173](http://127.0.0.1:4173). Vite hot reloads frontend edits. `Ctrl+C` stops only processes owned by this command. It refuses occupied ports rather than stopping another workspace.

## What runs where

| Test | Open | Runtime and data |
| --- | --- | --- |
| Design, topics and directory | `/`, `/topics/waste`, `/directory` | Local source and catalogue with hot reload. |
| Corpus questions and sources | `/ask`, `/ask/legal`, `/ask/ecology` | Existing hosted research service, Claude Sonnet 5.5, 1,174 documents at setup. Its shared usage ledger and limits remain authoritative. |
| Map and imagery analysis | `/map` | Local satellite API on loopback 8095, real Earth Engine Sentinel-2 access, numeric comparison and local saved investigations. The integrated page uses OpenStreetMap/Photon for its base map and place search. |
| Editorial and saved investigations | `/admin` | Local SQLite snapshot and accounts on loopback 4188. Changes here do not publish to the hosted site. |
| Incident reporting | Relevant reporting flow | Local reporting service on loopback 4187 and separate local storage. |

The separate Google Maps preview on port 4176 remains its own integration checkout; the larger map layout was applied there too. The integrated development environment does not depend on that preview process.

## Sign in and try the workflows

Use the existing local test account stored in the private, ignored `.reports/dev/account.json`. It was copied with the local test database, preserving its actor ID and saved comparisons. Do not commit this file or paste it into public issues.

1. Open `/ask` to ask a corpus question. Choose **Find sources** to test retrieval without an AI answer. Follow a source link to its exact passage and original document.
2. Sign in at `/admin`, then open `/map`. Draw a small area in Goa, or use **Set area by coordinates**. The maximum is 25 km².
3. Select dates and find observations. Load dated images, select an earlier/later pair, and run the numeric comparison. Saved history and evidence search use the local database. Existing retained comparisons can be reopened without retrieving new imagery.
4. Expand **Current conditions and directions** to check weather and air quality. These readings are separate from historical imagery.
5. The optional question planner prepares an investigation when selected. It does not replace explicit area selection.

Live AI, imagery and environmental requests use real providers when you initiate them. Setup readiness checks do not dispatch an AI answer, imagery retrieval or paid batch. OpenAI image classification is unconfigured, as in the existing integration; numerical image analysis is available. Field validation and statewide monitoring are outside this preview's claims.

## Configuration and checks

Private `.reports/dev/config.json` holds paths and service origins. It references the existing Python runtime, read-only Earth Engine credential, and saved server-key Keychain entry. Credentials are loaded only into the service needing them. Vite receives the hosted research origin, never provider secrets. All owned servers bind to `127.0.0.1`.

The committed launcher expects these configuration keys: `researchOrigin`, `researchBrowserOrigin`, `satellitePython`, `earthEngineProject`, `earthEngineCredentials`; optional `googleMapsKeychainService` and `anthropicEnvFile`. The latter enables only the satellite question planner; corpus AI continues to use the hosted service selected by the user. No new provider account or credential is created.

`npm run dev:check` verifies hosted research readiness, real corpus retrieval, local sign-in, satellite readiness, saved history and chat input validation without paid dispatch. Results are in `.reports/dev/readiness.json`. Service logs and owned process IDs are in `.reports/dev/`. `npm run build`, `npm test`, and the satellite Python suite cover code checks.

The local admin and satellite databases were snapshotted with SQLite's backup API. They are independent of both hosted storage and the port-4176 workspace. The startup command reuses them on later runs; it never resets usage or saved records. Provider secrets and account details remain ignored and private.
