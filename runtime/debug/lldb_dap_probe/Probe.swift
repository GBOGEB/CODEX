@main
struct Probe {
    static func main() {
        let seed = 41
        let observed = seed + 1
        print("lldb-dap-swift-probe observed=\(observed)")
    }
}
