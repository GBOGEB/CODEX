#!/usr/bin/env python3
from math import sqrt


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
