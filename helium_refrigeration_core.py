#!/usr/bin/env python3
from src.gistau_ch15.kernels.exergy import specific_flow_exergy


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
        exergy_change = specific_flow_exergy(
            h_j_kg=enthalpy_out,
            s_j_kgk=entropy_out,
            h0_j_kg=enthalpy_in,
            s0_j_kgk=entropy_in,
            t0_k=self.T0,
        )
        useful_exergy_power = mass_flow * exergy_change

        if power_kw <= 0:
            return 0.0
        power_w = power_kw * 1000.0
        return min(max(useful_exergy_power / power_w, 0.0), 1.0)

    def calculate_covariance(self, claimed_vector, actual_vector):
        c = [float(value) for value in claimed_vector]
        a = [float(value) for value in actual_vector]
        if len(c) != len(a) or len(c) < 2:
            return 0.0

        c_mean = sum(c) / len(c)
        a_mean = sum(a) / len(a)
        covariance = sum(
            (claimed - c_mean) * (actual - a_mean) for claimed, actual in zip(c, a)
        ) / (len(c) - 1)
        return float(covariance)

    def calculate_anova_variance(self, claimed_vector, actual_vector):
        c = [float(value) for value in claimed_vector]
        a = [float(value) for value in actual_vector]
        if len(c) != len(a) or len(c) < 2:
            return 0.0

        residuals = [claimed - actual for claimed, actual in zip(c, a)]
        residual_mean = sum(residuals) / len(residuals)
        variance = sum((value - residual_mean) ** 2 for value in residuals) / (
            len(residuals) - 1
        )
        return float(variance)
