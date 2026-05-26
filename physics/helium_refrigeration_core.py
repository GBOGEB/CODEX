#!/usr/bin/env python3
import math


class CryogenicHeliumEngineG5:
    def __init__(self, t0_ambient=298.15):
        self.T0 = t0_ambient
        self.n2_precool_flow = 11.5  # g/s Nitrogen "KISS" anchor baseline

    def compute_g5_exergy_efficiency(
        self,
        mass_flow_he,
        h_in,
        h_out,
        s_in,
        s_out,
        power_input_kw,
        nitrogen_assist=True,
    ):
        """
        Calculates localized plant exergy efficiency for the G5 tracking layer.

        Args:
            mass_flow_he: Helium mass flow rate (g/s).
            h_in: Specific enthalpy at inlet (kJ/kg).
            h_out: Specific enthalpy at outlet (kJ/kg).
            s_in: Specific entropy at inlet (kJ/kg·K).
            s_out: Specific entropy at outlet (kJ/kg·K).
            power_input_kw: Shaft/compressor power input (kW).
            nitrogen_assist: When True, applies a 10% helium mass-flow reduction
                to model nitrogen pre-cooling assistance.
            t0_ambient: Dead-state (ambient) temperature in Kelvin used for the
                exergy calculation; defaults to 298.15 K (25 °C) as set on the
                engine instance.

        Returns:
            Dimensionless exergy efficiency in [0, 1].  Consistent units require
            (mass_flow_he [g/s] × exergy_helium [kJ/kg]) and power_input_kw [kW]
            to be expressed in the same power dimension (multiply g/s by 1e-3 to
            convert to kg/s before calling, or use kg/s directly).

        Formula:
        $$\\psi = \\dot{m}_{He} \\cdot \\left[ (h_{out} - h_{in}) - T_0(s_{out} - s_{in}) \\right]$$
        """
        delta_h = h_out - h_in
        delta_s = s_out - s_in
        exergy_helium = delta_h - (self.T0 * delta_s)
        useful_work = mass_flow_he * exergy_helium

        if nitrogen_assist:
            # Applies 10% helium mass-flow reduction due to nitrogen pre-cooling assistance
            useful_work *= 0.90

        if power_input_kw <= 0:
            return 0.0
        return min(max(useful_work / power_input_kw, 0.0), 1.0)

    def calculate_wave_anova(self, claimed_vector, actual_vector):
        """
        Calculates sample covariance and Pearson correlation between two milestone vectors.

        Args:
            claimed_vector: Sequence of claimed milestone completion values.
            actual_vector: Sequence of actual milestone completion values.

        Returns:
            Tuple of (sample_covariance, pearson_correlation).
            Returns (0.0, 0.0) if vectors have mismatched lengths, fewer than 2
            elements, or zero variance in either vector.
        """
        c = [float(v) for v in claimed_vector]
        a = [float(v) for v in actual_vector]
        if len(c) != len(a) or len(c) < 2:
            return 0.0, 0.0

        n = len(c)
        mean_c = sum(c) / n
        mean_a = sum(a) / n

        covariance = sum((c[i] - mean_c) * (a[i] - mean_a) for i in range(n)) / (n - 1)

        var_c = sum((v - mean_c) ** 2 for v in c) / (n - 1)
        var_a = sum((v - mean_a) ** 2 for v in a) / (n - 1)

        if var_c <= 0.0 or var_a <= 0.0:
            return covariance, 0.0

        correlation = covariance / math.sqrt(var_c * var_a)
        return covariance, correlation
