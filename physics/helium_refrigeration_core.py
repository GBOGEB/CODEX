from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import sys

import yaml


class RuntimeGovernanceError(Exception):
    """Raised when runtime governance inputs or SSOT bindings are invalid."""


def _to_4dp_decimal(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def verify_mass_fractions(fractions: list) -> bool:
    """Enforces absolute precision validation for fluid stream components to 4 decimal places."""
    try:
        total = sum((_to_4dp_decimal(f) for f in fractions), Decimal("0.0000"))
    except (InvalidOperation, ValueError, TypeError):
        print("CRITICAL FAULT: Stream mass fractions contain invalid values.")
        return False

    total = total.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    expected = Decimal("1.0000")
    if total != expected:
        delta = abs(expected - total).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        print("CRITICAL FAULT: Stream mass fraction cumulative totals deviate from SSOT boundary condition.")
        print(f"Expected: {expected}, Calculated: {total}, Delta: {delta}")
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


def run_governance_assimilation(
    ssot_path: str, active_flow: float, active_efficiency: float, mass_mix: list
) -> bool:
    """Parses incoming SSOT parameters and enforces runtime compliance gates."""
    print(
        f"Executing G10 runtime governance validation for component "
        f"G10-TUPLE-HE-REF using SSOT: {ssot_path}"
    )

    try:
        with open(ssot_path, "r", encoding="utf-8") as f:
            ssot_data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        raise RuntimeGovernanceError(
            f"Failed to bind to governance contract mapping layer. Details: {e}"
        ) from e

    if ssot_data is None:
        ssot_data = {}
    if not isinstance(ssot_data, dict):
        raise RuntimeGovernanceError("Invalid SSOT payload: expected top-level mapping.")

    ssot_root = ssot_data.get("ssot")
    if not isinstance(ssot_root, dict):
        raise RuntimeGovernanceError("Invalid SSOT payload: missing 'ssot' mapping.")

    components = ssot_root.get("components")
    if not isinstance(components, list):
        raise RuntimeGovernanceError("Invalid SSOT payload: 'ssot.components' must be a list.")

    he_tuple = next(
        (c for c in components if isinstance(c, dict) and c.get("id") == "G10-TUPLE-HE-REF"),
        None,
    )
    if not he_tuple:
        raise RuntimeGovernanceError(
            "Component identifier G10-TUPLE-HE-REF missing from runtime substrate."
        )

    modes = he_tuple.get("modes")
    if not isinstance(modes, dict):
        raise RuntimeGovernanceError("Invalid SSOT payload: missing component modes mapping.")

    mode_2k_sb = modes.get("2K-SB")
    mode_2k_op = modes.get("2K-OP")
    if not isinstance(mode_2k_sb, dict) or not isinstance(mode_2k_op, dict):
        raise RuntimeGovernanceError("Invalid SSOT payload: required 2K mode mappings are missing.")

    target_eff = mode_2k_sb.get("target_efficiency")
    target_flow = mode_2k_op.get("nominal_flow_g_s")
    if not isinstance(target_eff, (int, float)) or not isinstance(target_flow, (int, float)):
        raise RuntimeGovernanceError(
            "Invalid SSOT payload: numeric targets required for 2K-SB and 2K-OP modes."
        )

    gates = [
        verify_mass_fractions(mass_mix),
        validate_2k_static_benchmark(active_efficiency, float(target_eff)),
        validate_2k_operational_flow(active_flow, float(target_flow)),
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

    try:
        is_valid = run_governance_assimilation(
            ssot_path="SSOT/g10_runtime_governance_ssot.yaml",
            active_flow=simulated_flow,
            active_efficiency=simulated_efficiency,
            mass_mix=mock_mass_fractions,
        )
    except RuntimeGovernanceError as e:
        print(f"Execution Halt: {e}")
        sys.exit(1)

    sys.exit(0 if is_valid else 1)
