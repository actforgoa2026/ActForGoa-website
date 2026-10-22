// swift-tools-version: 5.9
import PackageDescription
let package = Package(
    name: "ActForGoaCore", platforms: [.iOS("18.0"), .macOS(.v14)],
    products: [.library(name: "ActForGoaCore", targets: ["ActForGoaCore"])],
    dependencies: [.package(url: "https://github.com/microsoft/onnxruntime-swift-package-manager", exact: "1.24.2")],
    targets: [
        .target(name: "ActForGoaCore", dependencies: [.product(name: "onnxruntime", package: "onnxruntime-swift-package-manager")], path: "ActForGoa/Core"),
        .testTarget(name: "ActForGoaCoreTests", dependencies: ["ActForGoaCore"], path: "Tests", resources: [.copy("search-fixtures.json")])
    ]
)
