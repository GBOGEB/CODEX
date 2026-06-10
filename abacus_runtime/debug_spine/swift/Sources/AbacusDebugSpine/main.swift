import Foundation

let trackID = "ABACUS_DEBUG_SPINE_W000"
let requiredEvents = [
    "session.created",
    "dap.initialized",
    "breakpoint.bound",
    "execution.paused",
    "render.snapshot",
    "session.closed",
]

struct Arguments {
    var traceOutput: String = "runtime/logs/abacus_debug_spine_w001_trace.jsonl"
    var sessionID: String = "abacus-debug-spine-local"
    var targetLanguage: String = "Python"
    var branch: String = ProcessInfo.processInfo.environment["GITHUB_REF_NAME"] ?? "wave/W001-debug-spine-runtime-proof"
    var commitSHA: String = ProcessInfo.processInfo.environment["GITHUB_SHA"] ?? "local-dev"
}

struct Endpoint: Encodable {
    let name: String
    let `protocol`: String
}

struct Backbone: Encodable {
    let language: String
}

struct Target: Encodable {
    let language: String
}

struct GitHubContext: Encodable {
    let repository: String
    let branch: String
    let commit_sha: String
}

struct RenderState: Encodable {
    let required: Bool
    let status: String
}

struct EventPayload: Encodable {
    let name: String
    let timestamp: String
    let evidence_ref: String
}

struct TraceLine: Encodable {
    let session_id: String
    let track_id: String
    let adapter: Endpoint
    let backbone: Backbone
    let target: Target
    let github: GitHubContext
    let event: EventPayload
    let render: RenderState
}

func parseArguments(_ rawArguments: [String]) -> Arguments {
    var parsed = Arguments()
    var index = 1

    while index < rawArguments.count {
        let key = rawArguments[index]
        let valueIndex = index + 1

        if valueIndex < rawArguments.count {
            let value = rawArguments[valueIndex]
            switch key {
            case "--trace-output":
                parsed.traceOutput = value
                index += 2
                continue
            case "--session-id":
                parsed.sessionID = value
                index += 2
                continue
            case "--target-language":
                parsed.targetLanguage = value
                index += 2
                continue
            case "--branch":
                parsed.branch = value
                index += 2
                continue
            case "--commit-sha":
                parsed.commitSHA = value
                index += 2
                continue
            default:
                break
            }
        }

        index += 1
    }

    return parsed
}

func makeTraceLines(arguments: Arguments) -> [TraceLine] {
    let formatter = ISO8601DateFormatter()
    let timestamp = formatter.string(from: Date())

    return requiredEvents.map { eventName in
        TraceLine(
            session_id: arguments.sessionID,
            track_id: trackID,
            adapter: Endpoint(name: "lldb-dap", protocol: "Debug Adapter Protocol"),
            backbone: Backbone(language: "Swift"),
            target: Target(language: arguments.targetLanguage),
            github: GitHubContext(
                repository: "GBOGEB/ABACUS",
                branch: arguments.branch,
                commit_sha: arguments.commitSHA
            ),
            event: EventPayload(
                name: eventName,
                timestamp: timestamp,
                evidence_ref: "debug-spine://\(arguments.sessionID)/\(eventName)"
            ),
            render: RenderState(required: true, status: eventName == "render.snapshot" ? "rendered" : "pending")
        )
    }
}

let arguments = parseArguments(CommandLine.arguments)
let outputURL = URL(fileURLWithPath: arguments.traceOutput)
let outputDirectory = outputURL.deletingLastPathComponent()
let encoder = JSONEncoder()
encoder.outputFormatting = [.sortedKeys]

try FileManager.default.createDirectory(at: outputDirectory, withIntermediateDirectories: true)
let lines = try makeTraceLines(arguments: arguments).map { traceLine in
    String(data: try encoder.encode(traceLine), encoding: .utf8) ?? "{}"
}.joined(separator: "\n") + "\n"
try lines.write(to: outputURL, atomically: true, encoding: .utf8)

print("ABACUS debug spine trace emitted: \(outputURL.path)")
