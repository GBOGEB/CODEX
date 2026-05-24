#!/usr/bin/env python3
from __future__ import annotations

import statistics


class CryogenicHeliumEngine:
    def __init__(self, t0_ambient: float = 298.15) -> None:
        self.T0 = float(t0_ambient)
        self.modes = {
            "2K-SB": {"description": "Static Heat Load Benchmark", "target_temp": 2.0},
            "2K-OP": {"description": "Dynamic Load Operational Mode", "target_temp": 2.0},
        }

    def compute_exergy_efficiency(
        self,
        mass_flow: float,
        enthalpy_in: float,
        enthalpy_out: float,
        entropy_in: float,
        entropy_out: float,
        power_kw: float,
    ) -> float:
        delta_h = float(enthalpy_out) - float(enthalpy_in)
        delta_s = float(entropy_out) - float(entropy_in)
        exergy_change = delta_h - (self.T0 * delta_s)
        useful_exergy_power = float(mass_flow) * exergy_change
        if power_kw <= 0:
            return 0.0
        return float(min(max(useful_exergy_power / float(power_kw), 0.0), 1.0))

    def calculate_anova_variance(self, claimed_vector: list[float], actual_vector: list[float]) -> float:
        c = [float(x) for x in claimed_vector]
        a = [float(x) for x in actual_vector]
        if len(c) != len(a) or len(c) < 2:
            return 0.0
        mc = statistics.mean(c)
        ma = statistics.mean(a)
        return float(sum((x - mc) * (y - ma) for x, y in zip(c, a)) / (len(c) - 1))
