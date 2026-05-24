#!/usr/bin/env python3
import numpy as np


class CryogenicHeliumEngine:
    def __init__(self, t0_ambient=298.15):
        self.T0 = t0_ambient
        self.modes = {
            "2K-SB": {"description": "Static Heat Load Benchmark", "target_temp": 2.0},
            "2K-OP": {"description": "Dynamic Load Operational Mode", "target_temp": 2.0},
        }

    def compute_exergy_efficiency(
        self,
        mass_flow,
        enthalpy_in,
        enthalpy_out,
        entropy_in,
        entropy_out,
        power_kw,
    ):
        delta_h = enthalpy_out - enthalpy_in
        delta_s = entropy_out - entropy_in
        exergy_change = delta_h - (self.T0 * delta_s)
        useful_exergy_power = mass_flow * exergy_change

        if power_kw <= 0:
            return 0.0
        return min(max(useful_exergy_power / power_kw, 0.0), 1.0)

    def calculate_anova_variance(self, claimed_vector, actual_vector):
        c = np.array(claimed_vector, dtype=float)
        a = np.array(actual_vector, dtype=float)
        if len(c) != len(a) or len(c) < 2:
            return 0.0
        covariance_matrix = np.cov(c, a)
        return float(covariance_matrix[0, 1])
