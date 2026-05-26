import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import yaml


def verify_mass_fractions(fractions: list) -> bool:
    """Enforces absolute precision validation for fluid stream components to 4 decimal places."""
    # Use Decimal for deterministic fixed-point arithmetic at 4 decimal places
    four_decimal_places = Decimal("0.0001")
    decimal_fractions = [Decimal(str(f)).quantize(four_decimal_places, rounding=ROUND_HALF_UP) for f in fractions]
    total = sum(decimal_fractions)
    expected = Decimal("1.0000")
    
    if total != expected:
        print("CRITICAL FAULT: Stream mass fraction cumulative totals deviate from SSOT boundary condition.")
        print(f"Expected: {expected}, Calculated: {total}, Delta: {abs(expected - total)}")
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
        f"[Mode: 2K-OP] Target Flow: {target_flow:.4f} g/s "
        f"(Tol: {tolerance * 100:.1f}%) | Detected: {nominal_flow:.4f} g/s"
    )
    return lower_bound <= round(nominal_flow, 4) <= upper_bound


def run_governance_assimilation(ssot_path: str, active_flow: float, active_efficiency: float, mass_mix: list) -> bool:
    """Parses incoming SSOT parameters from the federated plane and enforces runtime compliance gates.
    
    Returns:
        bool: True if all gates pass, False otherwise.
    """
    print("Executing Predatory Assimilation: Processing G10-TUPLE-HE-REF...")

    try:
        with open(ssot_path, "r", encoding="utf-8") as f:
            ssot_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Execution Halt: Failed to bind to governance contract mapping layer. Details: {e}")
        return False

    # Validate yaml.safe_load() return value
    if ssot_data is None or not isinstance(ssot_data, dict):
        print("CRITICAL FAULT: SSOT file is empty or malformed (expected dict, got None or non-dict).")
        return False

    # Validate schema structure with explicit checks
    ssot_root = ssot_data.get("ssot")
    if not ssot_root or not isinstance(ssot_root, dict):
        print("CRITICAL FAULT: SSOT schema missing 'ssot' root key or it is not a dict.")
        return False

    components = ssot_root.get("components")
    if not components or not isinstance(components, list):
        print("CRITICAL FAULT: SSOT schema missing 'components' list under 'ssot' root.")
        return False

    # Find target component with safe navigation
    he_tuple = None
    for c in components:
        if isinstance(c, dict) and c.get("id") == "G10-TUPLE-HE-REF":
            he_tuple = c
            break
    
    if not he_tuple:
        print("CRITICAL FAULT: Component identifier G10-TUPLE-HE-REF missing from runtime substrate.")
        return False

    # Extract mode configurations with explicit schema validation
    modes = he_tuple.get("modes")
    if not modes or not isinstance(modes, dict):
        print("CRITICAL FAULT: Component G10-TUPLE-HE-REF missing 'modes' configuration.")
        return False

    ksb_mode = modes.get("2K-SB")
    if not ksb_mode or not isinstance(ksb_mode, dict):
        print("CRITICAL FAULT: Mode '2K-SB' missing or malformed in G10-TUPLE-HE-REF.")
        return False

    kop_mode = modes.get("2K-OP")
    if not kop_mode or not isinstance(kop_mode, dict):
        print("CRITICAL FAULT: Mode '2K-OP' missing or malformed in G10-TUPLE-HE-REF.")
        return False

    target_eff = ksb_mode.get("target_efficiency")
    if target_eff is None:
        print("CRITICAL FAULT: '2K-SB.target_efficiency' parameter missing.")
        return False

    target_flow = kop_mode.get("nominal_flow_g_s")
    if target_flow is None:
        print("CRITICAL FAULT: '2K-OP.nominal_flow_g_s' parameter missing.")
        return False

    gates = [
        verify_mass_fractions(mass_mix),
        validate_2k_static_benchmark(active_efficiency, target_eff),
        validate_2k_operational_flow(active_flow, target_flow),
    ]

    if not all(gates):
        print("\n[RESULT] G10 RUNTIME GOVERNANCE GATE: FAILED VERIFICATION")
        return False

    print("\n[RESULT] G10 RUNTIME GOVERNANCE GATE: PASS")
    print("All thermodynamic invariants align with MINERVA_QPLANT system baseline specification rules.")
    return True


if __name__ == "__main__":
    mock_mass_fractions = [0.9995, 0.0005]
    simulated_flow = 11.4850
    simulated_efficiency = 0.3620

    # Resolve SSOT path relative to this module's parent directory
    module_parent_dir = Path(__file__).parent.parent
    ssot_path = module_parent_dir / "SSOT" / "g10_runtime_governance_ssot.yaml"

    success = run_governance_assimilation(
        ssot_path=str(ssot_path),
        active_flow=simulated_flow,
        active_efficiency=simulated_efficiency,
        mass_mix=mock_mass_fractions,
    )
    
    sys.exit(0 if success else 1)
