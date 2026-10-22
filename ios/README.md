# ActForGoa for iPhone

Native SwiftUI field guide for iOS 18 and later. The interface uses native tabs, navigation, search, lists, sheets, Safari, sharing, telephone links and Mail composition. The bundled catalogue and MiniLM model work offline; original sources, linked documents, calls and email need the appropriate connection or app. No account, remote AI, analytics or submission service is used.

## Build

From the repository root:

```sh
python3 ios/scripts/sync_resources.py
open ios/ActForGoa.xcodeproj
```

Choose the `ActForGoa` scheme. The project is committed. Regenerate it with `python3 ios/scripts/generate_project.py` after adding source files. Xcode resolves the pinned Microsoft ONNX Runtime 1.24.2 Swift package. The sync build phase always copies the current web catalogue, index, tokenizer, model, images, provenance and shared search rules into the app bundle. Generated copies are ignored by Git.

Build without launching a device tool:

```sh
xcodebuild -project ios/ActForGoa.xcodeproj -scheme ActForGoa \
  -configuration Debug -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath ios/build -jobs 4 build CODE_SIGNING_ALLOWED=NO
```

Select the appropriate development team for an iPhone build. Do not launch Device Hub, or use a physical-device workflow that might launch it, without the user's explicit approval for that occasion. A request to install the app does not supply that approval.

## Keep web and native in parity

| Web feature | Native implementation |
| --- | --- |
| Search-first Explore, starter queries, topics | Explore tab with system search, immediate starter actions and topic rows |
| Keyword ranking and intent expansion | Swift search engine reading the same `shared/search-config.json` |
| Offline MiniLM hybrid retrieval | Native ONNX Runtime, Swift WordPiece, same model, vectors, thresholds and scoring |
| Grouped results, counts, pagination, filters | Native sections, topic/type menus and show-more actions |
| Directory, library, stories | Directory and Library tabs; stories inside Community |
| List/grid views | Open native list or image-rich adaptive layout via “Show images” |
| Detail, historical dates, contacts, downloads, sources, related entries | Native reading screen with source notices and links |
| Shareable entries | System share sheet with canonical web URL; `actforgoa://read/<id>` deep link |
| About, participation, contact/correction | Community, About, native form, reviewable Mail composition |

The canonical data remains `public/data/` and the model remains `public/models/`. Never edit `ios/ActForGoa/Content/`. Web content updates reach installed phones in the next development build; this app does not silently fetch a different corpus. The separate ongoing `corpus/` research is not imported until it becomes part of the canonical web catalogue.

When changing a web route or capability, update this table, the corresponding native flow, and its tests in the same PR. Shared data and ranking changes trigger the native CI workflow. Swift and JavaScript use different quantized runtime kernels: reference vectors must have cosine agreement above 0.995, and practical retrieval tests must still pass. Exact floating-point ordering of closely matched semantic results is not promised.

## Verification

```sh
npm ci
npm test
npm run build
node --import tsx ios/scripts/export_search_fixtures.ts
swift test --package-path ios --jobs 4
```

Reference cases come from the current web implementation, not hand-authored expected Swift results. They cover tokenization, lexical scores, real model embeddings, practical retrieval, source integrity, safe telephone links, date presentation, and email escaping. `ActForGoaUITests` covers real iPhone Simulator flows and captures screenshots. See `VERIFICATION.md` for this build's evidence and limitations.

The app contains no web view shell. Safari is used only when a person explicitly opens an original source or document. Search executes natively off the main actor. Query changes cancel result delivery from older searches. Contact messages remain in view state until the user opens Mail or the system share sheet; the app never sends them automatically.

## Install over USB without Device Hub

The open-source `ideviceinstaller` communicates directly with the phone's installation service through libimobiledevice/usbmuxd. It does not open Device Hub or Xcode. With a signed Debug build and the phone connected, unlocked and trusted:

```sh
brew install ideviceinstaller libimobiledevice
python3 ios/scripts/install_on_phone.py
```

The script verifies the signature and development entitlement, selects only a connected USB phone included in the embedded provisioning profile, installs the app, and checks the installed bundle version. It refuses an absent or ambiguous target. It does not turn on Developer Mode, change trust settings or open the app. Enable Developer Mode on the phone if iOS requests it. A successful install is not physical UI verification.
