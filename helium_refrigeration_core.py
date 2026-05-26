#!/usr/bin/env python3


class CryogenicHeliumEngineG7:
    def __init__(self, t0_ambient=298.15):
        self.T0 = t0_ambient

    def compute_g7_exergy_efficiency(self, mass_flow_he, h_in, h_out, s_in, s_out, power_input_kw, nitrogen_assist=True):
        delta_h = h_out - h_in
        delta_s = s_out - s_in
        exergy_helium = delta_h - (self.T0 * delta_s)
        useful_work = mass_flow_he * exergy_helium

        if nitrogen_assist:
            useful_work *= 1.10

        if power_input_kw <= 0:
            return 0.0
        return min(max(useful_work / power_input_kw, 0.0), 1.0)

    def calculate_pearson_correlation(self, claimed_vector, actual_vector):
        if len(claimed_vector) != len(actual_vector) or len(claimed_vector) < 2:
            return 0.0, 0.0

        c = [float(v) for v in claimed_vector]
        a = [float(v) for v in actual_vector]
        n = len(c)
        c_mean = sum(c) / n
        a_mean = sum(a) / n

        covariance = sum((x - c_mean) * (y - a_mean) for x, y in zip(c, a)) / (n - 1)
        c_var = sum((x - c_mean) ** 2 for x in c) / (n - 1)
        a_var = sum((y - a_mean) ** 2 for y in a) / (n - 1)
        denom = (c_var * a_var) ** 0.5
        correlation = covariance / denom if denom > 0 else 0.0
        return float(covariance), float(correlation)
