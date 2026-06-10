// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "AbacusDebugSpine",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "abacus-debug-spine",
            targets: ["AbacusDebugSpine"]
        )
    ],
    targets: [
        .executableTarget(
            name: "AbacusDebugSpine",
            path: "Sources/AbacusDebugSpine"
        )
    ]
)
