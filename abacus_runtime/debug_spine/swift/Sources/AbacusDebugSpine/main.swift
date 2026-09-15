import Foundation

let trackID = "ABACUS_DEBUG_SPINE_W002"
let requiredEvents = [
    "session.created",
    "federation.profile.bound",
    "dap.initialized",
    "dap.request.normalized",
    "breakpoint.bound",
    "execution.paused",
    "render.snapshot",
    "session.closed",
]

struct Arguments {
    var traceOutput: String = "runtime/logs/abacus_debug_spine_w002_trace.jsonl"
    var sessionID: String = "abacus-debug-spine-local"
    var targetLanguage: String = "Swift"
    var mode: String = "launch"
    var program: String = ""
    var processID: Int? = nil
    var repository: String = ProcessInfo.processInfo.environment["GITHUB_REPOSITORY"] ?? "GBOGEB/CODEX"
    var branch: String = ProcessInfo.processInfo.environment["GITHUB_REF_NAME"] ?? "triage/w84-lldb-dap-swift-federation-keb"
    var commitSHA: String = ProcessInfo.processInfo.environment["GITHUB_SHA"] ?? "local-dev"
}

struct Endpoint: Encodable {
    let name: String
    let `protocol`: String
    let role: String
}

struct Backbone: Encodable {
    let language: String
    let responsibility: String
}

struct FederationProfile: Encodable {
    let target_language: String
    let target_adapter: String
    let canonical_control_adapter: String
    let request_mode: String
    let transport: String
    let semantic_owner: String
}

struct Target: Encodable {
    let language: String
    let program: String
    let process_id: Int?
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

struct NormalizedDAPRequest: Encodable {
    let command: String
    let adapter: String
    let program: String
    let process_id: Int?
    let stop_on_entry: Bool
}

struct TraceLine: Encodable {
    let session_id: String
    let track_id: String
    let adapter: Endpoint
    let backbone: Backbone
    let federation: FederationProfile
    let target: Target
    let github: GitHubContext
    let normalized_request: NormalizedDAPRequest
    let event: EventPayload
    let render: RenderState
}

enum FederationError: Error, CustomStringConvertible {
    case unsupportedLanguage(String)
    case unsupportedMode(String)
    case missingProgram
    case missingProcessID

    var description: String {
        switch self {
        case .unsupportedLanguage(let language):
            return "unsupported target language: \(language)"
        case .unsupportedMode(let mode):
            return "unsupported DAP request mode: \(mode)"
        case .missingProgram:
            return "launch mode requires --program"
        case .missingProcessID:
            return "attach mode requires --process-id"
        }
    }
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
            case "--session-id":
                parsed.sessionID = value
            case "--target-language":
                parsed.targetLanguage = value
            case "--mode":
                parsed.mode = value
            case "--program":
                parsed.program = value
            case "--process-id":
                parsed.processID = Int(value)
            case "--repository":
                parsed.repository = value
            case "--branch":
                parsed.branch = value
            case "--commit-sha":
                parsed.commitSHA = value
            default:
                index += 1
                continue
            }
            index += 2
            continue
        }

        index += 1
    }

    return parsed
}

func normalizeLanguage(_ language: String) throws -> (canonical: String, adapter: String, transport: String) {
    switch language.lowercased() {
    case "swift":
        return ("Swift", "lldb-dap", "native-dap")
    case "python", "py":
        return ("Python", "debugpy", "federated-dap")
    case "javascript", "js", "node":
        return ("JavaScript", "js-debug", "federated-dap")
    case "typescript", "ts":
        return ("TypeScript", "js-debug", "federated-dap")
    default:
        throw FederationError.unsupportedLanguage(language)
    }
}

func makeFederationProfile(arguments: Arguments) throws -> FederationProfile {
    let language = try normalizeLanguage(arguments.targetLanguage)
    let mode = arguments.mode.lowercased()
    guard mode == "launch" || mode == "attach" else {
        throw FederationError.unsupportedMode(arguments.mode)
    }

    return FederationProfile(
        target_language: language.canonical,
        target_adapter: language.adapter,
        canonical_control_adapter: "lldb-dap",
        request_mode: mode,
        transport: language.transport,
        semantic_owner: "CODEX/KEB"
    )
}

func makeNormalizedRequest(arguments: Arguments, profile: FederationProfile) throws -> NormalizedDAPRequest {
    if profile.request_mode == "launch" {
        guard !arguments.program.isEmpty else {
            throw FederationError.missingProgram
        }
        return NormalizedDAPRequest(
            command: "launch",
            adapter: profile.target_adapter,
            program: arguments.program,
            process_id: nil,
            stop_on_entry: true
        )
    }

    guard let processID = arguments.processID else {
        throw FederationError.missingProcessID
    }
    return NormalizedDAPRequest(
        command: "attach",
        adapter: profile.target_adapter,
        program: arguments.program,
        process_id: processID,
        stop_on_entry: false
    )
}

func makeTraceLines(arguments: Arguments) throws -> [TraceLine] {
    let formatter = ISO8601DateFormatter()
    let timestamp = formatter.string(from: Date())
    let profile = try makeFederationProfile(arguments: arguments)
    let request = try makeNormalizedRequest(arguments: arguments, profile: profile)

    return requiredEvents.map { eventName in
        TraceLine(
            session_id: arguments.sessionID,
            track_id: trackID,
            adapter: Endpoint(
                name: "lldb-dap",
                protocol: "Debug Adapter Protocol",
                role: "canonical-session-control"
            ),
            backbone: Backbone(
                language: "Swift",
                responsibility: "session-state-and-request-normalization"
            ),
            federation: profile,
            target: Target(
                language: profile.target_language,
                program: arguments.program,
                process_id: arguments.processID
            ),
            github: GitHubContext(
                repository: arguments.repository,
                branch: arguments.branch,
                commit_sha: arguments.commitSHA
            ),
            normalized_request: request,
            event: EventPayload(
                name: eventName,
                timestamp: timestamp,
                evidence_ref: "debug-spine://\(arguments.sessionID)/\(eventName)"
            ),
            render: RenderState(
                required: true,
                status: eventName == "render.snapshot" ? "rendered" : "pending"
            )
        )
    }
}

func run() throws {
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

    print("ABACUS LLDB-DAP Swift federation trace emitted: \(outputURL.path)")
}

do {
    try run()
} catch {
    fputs("ABACUS LLDB-DAP Swift federation failed closed: \(error)\n", stderr)
    exit(2)
}
