# Native verification

22 October 2026. Source branch: `codex/actforgoa-ios`. Canonical web base: `0e466bf` (practical guides published while native work was in progress, then merged into this branch).

## Confirmed

- All eleven web tests pass; the Vite production build passes after extracting the unchanged ranking constants into shared JSON and incorporating the published practical guides.
- Nine Swift core tests pass. Fifteen web-generated reference cases check lexical scores and token IDs. Fourteen nonempty queries check real native MiniLM embeddings against web reference embeddings (cosine agreement above 0.995). Real hybrid retrieval checks the snake-rescue source and V Recycle. The practical guide tests verify reference citations, native table structure and bundled downloads.
- Source IDs, historical dates, safe complete telephone numbers, email validation/encoding, and empty-result behavior are covered.
- iPhone Simulator Debug build succeeds on Xcode 27.1 for an iPhone 17e simulator running iOS 27.0.
- A signed physical-iPhone Debug build succeeds with the existing Dizko Labs development certificate. `codesign --verify --deep --strict` passes. `get-task-allow` is true. The bundle contains all 605 searchable entries, two additional review registers, and 17 templates. SHA-256 verification passes for its 53 canonical content files.
- All five iPhone Simulator UI tests pass: empty search, the largest accessibility text size, search/reading/directory/library/contact preparation, practical guides/templates, and guide navigation/file sharing. Results are `ios/build/Guides.xcresult` (four tests) and `ios/build/GuideNavigationCapture.xcresult` (the additional test). No call was placed, no email sent and no file shared with another person.
- Rendered screens were inspected in light and dark appearance, with search results, a full reading view, directory rows, empty search, the largest accessibility text size and a prepared contact email. Source notes use an explicit contrasting semantic color. Preparing email dismisses the keyboard. Long extracted phone lists follow article content and expand after five numbers.
- Practical-guide evidence covers the draft header, stacked table rows, section navigation, verification register, template preview, landscape reading and the system share sheet showing Copy and Save to Files. The first landscape/share captures caught transition frames and were replaced with settled screen captures.
- The signed application is also packaged as `ios/device-build/ActForGoa-Development.ipa` (28 MB). Its development profile expires on 20 October 2027. The profile is specific to its registered devices; this is not a general distribution package.
- Nine shipping raster assets have embedded provenance. Changed Swift source contains no italic/oblique styling or decorative side stripes.
- Independent Impeccable finish review returned `ship` for all 18 supplied captures, including the native guide additions. The verdict is scoped to those rendered states, not physical-device certification.
- Native design documentation is complete in `ios/DESIGN.md`. The independent documenter compared the implementation with the existing web system and preserved the root design files. Pre-existing stale root design metadata is recorded without repair.

## Remaining before completion

- Physical phone installation and launch. No USB or network phone was visible during this run. `ios/scripts/install_on_phone.py` uses libimobiledevice's USB installation service without opening Device Hub or Xcode, and verifies the installed bundle version. The script requires one connected, trusted phone included in the signed app's development profile.
- Physical-device performance, gestures, VoiceOver, Mail handoff and telephone handoff are not yet verified.
- CI workflow is authored locally; no GitHub run, push, merge of native work into `main`, or production web deployment has happened in this task.

No Device Hub was launched or used. Simulator captures and UI tests ran headlessly through the installed CoreSimulator service and XCTest. Landscape was checked for the practical guide reader; other landscape screens, older supported iOS versions, physical-device accessibility and external app handoffs remain outside the verified scope.

The Swift search implementation shares the model, index, tokenizer vocabulary and ranking rules with web. Floating-point scores can vary slightly between the quantized native and web runtimes, so close semantic ties may order differently. The app's imported content updates with a new app build.
