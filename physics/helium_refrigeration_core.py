#!/usr/bin/env python3
import numpy as np


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

        Formula:
        $$\psi = \dot{m}_{He} \cdot \left[ (h_{out} - h_{in}) - T_0(s_{out} - s_{in}) \right]$$
        """
        delta_h = h_out - h_in
        delta_s = s_out - s_in
        exergy_helium = delta_h - (self.T0 * delta_s)
        useful_work = mass_flow_he * exergy_helium

        if nitrogen_assist:
            # Accounts for the targeted 10% helium mass flow optimization reduction
            useful_work *= 1.10

        if power_input_kw <= 0:
            return 0.0
        return min(max(useful_work / power_input_kw, 0.0), 1.0)

    def calculate_wave_anova(self, claimed_vector, actual_vector):
        """
        Performs analysis of variance tracking to calculate project deployment alignment.
        """
        c = np.array(claimed_vector, dtype=float)
        a = np.array(actual_vector, dtype=float)
        if len(c) != len(a) or len(c) < 2:
            return 0.0, 0.0

        covariance_matrix = np.cov(c, a)
        covariance = float(covariance_matrix[0, 1])
        correlation = float(np.corrcoef(c, a)[0, 1])
        return covariance, correlation
