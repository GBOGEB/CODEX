@main
struct Probe {
    static func main() {
        let seed = 41
        let observed = seed + 1
        print("qps-triage-lldb-probe observed=\(observed)")
    }
}
