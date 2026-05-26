import sys
import yaml


def verify_mass_fractions(fractions: list) -> bool:
    """Enforces absolute precision validation for fluid stream components to 4 decimal places."""
    total = sum(round(f, 4) for f in fractions)
    expected = round(1.0000, 4)
    if total != expected:
        print("CRITICAL FAULT: Stream mass fraction cumulative totals deviate from SSOT boundary condition.")
        print(f"Expected: {expected:.4f}, Calculated: {total:.4f}, Delta: {abs(expected - total):.4f}")
        return False
    return True


def validate_2k_static_benchmark(calculated_efficiency: float, target_efficiency: float) -> bool:
    """Validates 2K Static Benchmark (2K-SB) operating mode limits."""
    print(
        f"[Mode: 2K-SB] Target Efficiency Min: {target_efficiency:.4f} | "
        f"System Efficiency: {calculated_efficiency:.4f}"
    )
    return calculated_efficiency >= target_efficiency


def validate_2k_operational_flow(nominal_flow: float, target_flow: float, tolerance: float = 0.05) -> bool:
    """Validates 2K Dynamic Operational (2K-OP) nominal mass flow rates."""
    lower_bound = round(target_flow * (1.0 - tolerance), 4)
    upper_bound = round(target_flow * (1.0 + tolerance), 4)
    print(
        f"[Mode: 2K-OP] Target Flow: {target_flow:.4f} g/s (Tol: {tolerance*100:.1f}%) | "
        f"Detected: {nominal_flow:.4f} g/s"
    )
    return lower_bound <= round(nominal_flow, 4) <= upper_bound


def run_governance_assimilation(ssot_path: str, active_flow: float, active_efficiency: float, mass_mix: list):
    """Parses incoming SSOT parameters and enforces runtime compliance gates."""
    print("Executing Predatory Assimilation: Processing G10-TUPLE-HE-REF...")

    try:
        with open(ssot_path, "r", encoding="utf-8") as f:
            ssot_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Execution Halt: Failed to bind to governance contract mapping layer. Details: {e}")
        sys.exit(1)

    he_tuple = next((c for c in ssot_data["ssot"]["components"] if c["id"] == "G10-TUPLE-HE-REF"), None)
    if not he_tuple:
        print("CRITICAL FAULT: Component identifier G10-TUPLE-HE-REF missing from runtime substrate.")
        sys.exit(1)

    target_eff = he_tuple["modes"]["2K-SB"]["target_efficiency"]
    target_flow = he_tuple["modes"]["2K-OP"]["nominal_flow_g_s"]

    gates = [
        verify_mass_fractions(mass_mix),
        validate_2k_static_benchmark(active_efficiency, target_eff),
        validate_2k_operational_flow(active_flow, target_flow),
    ]

    if not all(gates):
        print("\n[RESULT] G10 RUNTIME GOVERNANCE GATE: FAILED VERIFICATION")
        sys.exit(1)

    print("\n[RESULT] G10 RUNTIME GOVERNANCE GATE: PASS")
    print("All thermodynamic invariants align with MINERVA_QPLANT system baseline specification rules.")


if __name__ == "__main__":
    mock_mass_fractions = [0.9995, 0.0005]
    simulated_flow = 11.4850
    simulated_efficiency = 0.3620

    run_governance_assimilation(
        ssot_path="SSOT/g10_runtime_governance_ssot.yaml",
        active_flow=simulated_flow,
        active_efficiency=simulated_efficiency,
        mass_mix=mock_mass_fractions,
    )
