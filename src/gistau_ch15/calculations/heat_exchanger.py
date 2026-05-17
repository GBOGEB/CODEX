from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HeatExchangerResult:
    hot_inlet_k: float
    hot_outlet_k: float
    cold_inlet_k: float
    cold_outlet_k: float
    effectiveness: float
    q_transfer_w: float


def calculate_heat_exchanger(
    hot_inlet_k: float,
    cold_inlet_k: float,
    hot_capacity_rate_wk: float,
    cold_capacity_rate_wk: float,
    effectiveness: float,
) -> HeatExchangerResult:
    """Simplified epsilon-NTU style fallback heat exchanger.

    This deterministic implementation is intentionally conservative until
    canonical validation and REFPROP/HEPAK coupling are added.
    """

    if not 0.0 <= effectiveness <= 1.0:
        raise ValueError("effectiveness must be between 0 and 1")

    cmin = min(hot_capacity_rate_wk, cold_capacity_rate_wk)
    qmax = cmin * max(hot_inlet_k - cold_inlet_k, 0.0)
    q = effectiveness * qmax

    hot_out = hot_inlet_k - q / max(hot_capacity_rate_wk, 1e-9)
    cold_out = cold_inlet_k + q / max(cold_capacity_rate_wk, 1e-9)

    return HeatExchangerResult(
        hot_inlet_k=hot_inlet_k,
        hot_outlet_k=hot_out,
        cold_inlet_k=cold_inlet_k,
        cold_outlet_k=cold_out,
        effectiveness=effectiveness,
        q_transfer_w=q,
    )
