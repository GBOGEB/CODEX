#!/usr/bin/env python3


class CryogenicHeliumEngineG8:
    def __init__(self, t0_ambient=298.15):
        self.T0 = t0_ambient

    def compute_g8_exergy_efficiency(self, mass_flow_he, h_in, h_out, s_in, s_out, power_input_kw, nitrogen_assist=True):
        delta_h = h_out - h_in
        delta_s = s_out - s_in
        exergy_helium = delta_h - (self.T0 * delta_s)
        useful_work = mass_flow_he * exergy_helium
        if nitrogen_assist:
            useful_work *= 1.10
        if power_input_kw <= 0:
            return 0.0
        return min(max(useful_work / power_input_kw, 0.0), 1.0)

    def calculate_g8_covariance_correlation(self, claimed_vector, actual_vector):
        c = [float(x) for x in claimed_vector]
        a = [float(x) for x in actual_vector]
        n = len(c)
        if n != len(a) or n < 2:
            return 0.0, 0.0

        mean_c = sum(c) / n
        mean_a = sum(a) / n
        cov = sum((c[i] - mean_c) * (a[i] - mean_a) for i in range(n)) / (n - 1)

        var_c = sum((x - mean_c) ** 2 for x in c) / (n - 1)
        var_a = sum((x - mean_a) ** 2 for x in a) / (n - 1)
        if var_c <= 0 or var_a <= 0:
            return cov, 0.0
        corr = cov / ((var_c ** 0.5) * (var_a ** 0.5))
        return float(cov), float(corr)

    def calculate_g8_anova(self, claimed_vector, actual_vector):
        return self.calculate_g8_covariance_correlation(claimed_vector, actual_vector)
