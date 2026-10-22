# Native verification

22 October 2026. Source branch: `codex/actforgoa-ios`. Canonical web base: `201df39b1649197c1d8190b8bee028b2fb27b402`.

## Confirmed

- All eight existing web tests pass; the Vite production build passes after extracting the unchanged ranking constants into shared JSON.
- Seven Swift core tests pass. Twelve web-generated reference cases check lexical scores and token IDs. Eleven nonempty queries check real native MiniLM embeddings against web reference embeddings (cosine agreement above 0.995). Real hybrid retrieval checks the snake-rescue source and V Recycle.
- Source IDs, historical dates, safe complete telephone numbers, email validation/encoding, and empty-result behavior are covered.
- iPhone Simulator Debug build succeeds on Xcode 27.1 for an iPhone 17e simulator running iOS 27.0.
- A signed physical-iPhone Debug build succeeds with the existing Dizko Labs development certificate. `codesign --verify --deep --strict` passes. `get-task-allow` is true. The bundle contains all 600 records and SHA-256 verification passes for its 28 canonical content files.
- All three final iPhone Simulator UI tests pass: empty search, the largest accessibility text size, and the search, reading, directory, library and contact preparation flow. The final result is `ios/build/UIPolish2.xcresult`. No call was placed and no email was sent.
- Rendered screens were inspected in light and dark appearance, with search results, a full reading view, directory rows, empty search, the largest accessibility text size and a prepared contact email. Source notes use an explicit contrasting semantic color. Preparing email dismisses the keyboard. Long extracted phone lists follow article content and expand after five numbers.
- The signed application is also packaged as `ios/device-build/ActForGoa-Development.ipa` (28 MB). Its development profile expires on 20 October 2027. The profile is specific to its registered devices; this is not a general distribution package.
- Nine shipping raster assets have embedded provenance. Changed Swift source contains no italic/oblique styling or decorative side stripes.

## Remaining before completion

- Independent visual finish review and documentation check.
- Physical phone installation and launch. No USB or network phone was visible during this run. `ios/scripts/install_on_phone.py` uses libimobiledevice's USB installation service without opening Device Hub or Xcode, and verifies the installed bundle version. The script requires one connected, trusted phone included in the signed app's development profile.
- Physical-device performance, gestures, VoiceOver, Mail handoff and telephone handoff are not yet verified.
- CI workflow is authored locally; no GitHub run, push, merge or deployment has happened in this task.

No Device Hub was launched or used. Simulator captures and UI tests ran headlessly through the installed CoreSimulator service and XCTest. Landscape, older supported iOS versions, physical-device accessibility and external app handoffs remain outside the verified scope.

The Swift search implementation shares the model, index, tokenizer vocabulary and ranking rules with web. Floating-point scores can vary slightly between the quantized native and web runtimes, so close semantic ties may order differently. The app's imported content updates with a new app build.
