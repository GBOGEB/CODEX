from __future__ import annotations


def specific_flow_exergy(
    h_j_kg: float,
    s_j_kgk: float,
    h0_j_kg: float,
    s0_j_kgk: float,
    t0_k: float,
) -> float:
    """Specific flow exergy approximation.

    ex = (h - h0) - T0 * (s - s0)

    This kernel intentionally remains simple and explicit until real-fluid
    backend validation is integrated.
    """

    return (h_j_kg - h0_j_kg) - t0_k * (s_j_kgk - s0_j_kgk)
