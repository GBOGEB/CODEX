#!/usr/bin/env python3


class CryogenicHeliumEngineG9:
    def __init__(self, t0_ambient=298.15):
        self.T0 = t0_ambient
        self.n2_precool_flow = 11.5

    def compute_g9_exergy_efficiency(self, mass_flow_he, h_in, h_out, s_in, s_out, power_input_kw, nitrogen_assist=True):
        delta_h = h_out - h_in
        delta_s = s_out - s_in
        exergy_helium = delta_h - (self.T0 * delta_s)
        useful_work = mass_flow_he * exergy_helium
        if nitrogen_assist:
            useful_work *= 1.10
        if power_input_kw <= 0:
            return 0.0
        return min(max(useful_work / power_input_kw, 0.0), 1.0)

    def calculate_g9_covariance_correlation(self, claimed_vector, actual_vector):
        c = [float(x) for x in claimed_vector]
        a = [float(x) for x in actual_vector]
        if len(c) != len(a) or len(c) < 2:
            return 0.0, 0.0

        n = len(c)
        c_mean = sum(c) / n
        a_mean = sum(a) / n
        covariance = sum((ci - c_mean) * (ai - a_mean) for ci, ai in zip(c, a)) / (n - 1)

        c_var = sum((ci - c_mean) ** 2 for ci in c) / (n - 1)
        a_var = sum((ai - a_mean) ** 2 for ai in a) / (n - 1)
        if c_var <= 0 or a_var <= 0:
            return covariance, 0.0

        correlation = covariance / ((c_var ** 0.5) * (a_var ** 0.5))
        return float(covariance), float(correlation)
