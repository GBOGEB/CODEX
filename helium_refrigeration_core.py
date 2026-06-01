#!/usr/bin/env python3
from math import sqrt


class CryogenicHeliumEngine:
    def __init__(self, t0_ambient=298.15):
        self.T0 = float(t0_ambient)

    def compute_exergy_efficiency(
        self, mass_flow, enthalpy_in, enthalpy_out, entropy_in, entropy_out, power_kw
    ):
        delta_h = float(enthalpy_out) - float(enthalpy_in)
        delta_s = float(entropy_out) - float(entropy_in)
        exergy_change = delta_h - (self.T0 * delta_s)
        useful_exergy_power = float(mass_flow) * exergy_change
        if power_kw <= 0:
            return 0.0
        return float(min(max(useful_exergy_power / float(power_kw), 0.0), 1.0))

    def calculate_covariance(self, claimed_vector, actual_vector):
        c = [float(v) for v in claimed_vector]
        a = [float(v) for v in actual_vector]
        if len(c) != len(a) or len(c) < 2:
            return 0.0
        n = len(c)
        mean_c = sum(c) / n
        mean_a = sum(a) / n
        cov_num = sum((x - mean_c) * (y - mean_a) for x, y in zip(c, a))
        return float(cov_num / (n - 1))

    def calculate_anova_variance(self, claimed_vector, actual_vector):
        c = [float(v) for v in claimed_vector]
        a = [float(v) for v in actual_vector]
        if len(c) != len(a) or len(c) < 2:
            return 0.0
        residuals = [(x - y) for x, y in zip(c, a)]
        mean_residual = sum(residuals) / len(residuals)
        return float(sum((r - mean_residual) ** 2 for r in residuals) / (len(residuals) - 1))


class CryogenicHeliumEngineG4:
    def __init__(self, t0_ambient=298.15):
        self.T0 = t0_ambient
        self.nitrogen_precool_flow = 11.5  # g/s Nitrogen KISS Anchor

    def compute_g4_dynamic_exergy(self, mass_flow, h_in, h_out, s_in, s_out, power_kw, ln2_assist=True):
        r"""
        G4 Extended Exergy Equation: Incorporates Nitrogen Pre-cooling optimizations.
        $$\psi_{total} = \dot{m}_{He} \cdot \Delta e_{He} + \delta \cdot \dot{m}_{N2} \cdot \Delta e_{N2}$$
        """
        delta_h = h_out - h_in
        delta_s = s_out - s_in
        exergy_helium = delta_h - (self.T0 * delta_s)
        useful_work = mass_flow * exergy_helium

        if ln2_assist:
            # Approximated 10% efficiency boost from the 6-turbine nitrogen loop config
            useful_work *= 1.10

        if power_kw <= 0:
            return 0.0
        return min(max(useful_work / power_kw, 0.0), 1.0)

    def compute_wave_metrics_anova(self, claimed, actual):
        c = [float(v) for v in claimed]
        a = [float(v) for v in actual]
        if len(c) != len(a) or len(c) < 2:
            return 0.0, 0.0

        n = len(c)
        mean_c = sum(c) / n
        mean_a = sum(a) / n

        cov_num = sum((x - mean_c) * (y - mean_a) for x, y in zip(c, a))
        covariance = cov_num / (n - 1)

        var_c = sum((x - mean_c) ** 2 for x in c)
        var_a = sum((y - mean_a) ** 2 for y in a)
        denom = sqrt(var_c * var_a)
        correlation = (cov_num / denom) if denom else 0.0
        return float(covariance), float(correlation)


class CryogenicHeliumEngineG7:
    def __init__(self, t0_ambient=298.15, nitrogen_assist_gain=1.10):
        self.T0 = t0_ambient
        self.nitrogen_assist_gain = nitrogen_assist_gain

    def compute_g7_exergy_efficiency(
        self, mass_flow_he, h_in, h_out, s_in, s_out, power_input_kw, nitrogen_assist=True
    ):
        delta_h = float(h_out) - float(h_in)
        delta_s = float(s_out) - float(s_in)
        exergy_helium = delta_h - (self.T0 * delta_s)
        useful_work = float(mass_flow_he) * exergy_helium
        if nitrogen_assist:
            useful_work *= self.nitrogen_assist_gain
        if power_input_kw <= 0:
            return 0.0
        return min(max(useful_work / float(power_input_kw), 0.0), 1.0)

    def calculate_pearson_correlation(self, claimed_vector, actual_vector):
        c = [float(v) for v in claimed_vector]
        a = [float(v) for v in actual_vector]
        if len(c) != len(a) or len(c) < 2:
            return 0.0, 0.0
        n = len(c)
        mean_c = sum(c) / n
        mean_a = sum(a) / n
        cov_num = sum((x - mean_c) * (y - mean_a) for x, y in zip(c, a))
        covariance = cov_num / (n - 1)
        var_c = sum((x - mean_c) ** 2 for x in c)
        var_a = sum((y - mean_a) ** 2 for y in a)
        denom = sqrt(var_c * var_a)
        correlation = (cov_num / denom) if denom else 0.0
        return float(covariance), float(correlation)
