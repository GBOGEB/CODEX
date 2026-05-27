#!/usr/bin/env python3

try:
    from gistau_ch15.kernels.exergy import specific_flow_exergy
except ModuleNotFoundError:  # pragma: no cover - local script execution path
    from src.gistau_ch15.kernels.exergy import specific_flow_exergy


class CryogenicHeliumEngineG8:
    def __init__(self, t0_ambient=298.15, nitrogen_assist_gain=1.10):
        self.T0 = t0_ambient
        self.nitrogen_assist_gain = nitrogen_assist_gain

    def compute_g8_exergy_efficiency(self, mass_flow_he, h_in, h_out, s_in, s_out, power_input_w, nitrogen_assist=True):
        """Compute exergy efficiency of the G8 cryogenic helium engine.

        Args:
            mass_flow_he: Helium mass flow rate (kg/s).
            h_in: Inlet specific enthalpy (J/kg).
            h_out: Outlet specific enthalpy (J/kg).
            s_in: Inlet specific entropy (J/(kg·K)).
            s_out: Outlet specific entropy (J/(kg·K)).
            power_input_w: Shaft power input (W).
            nitrogen_assist: Whether nitrogen pre-cool assist gain is applied.

        Returns:
            Exergy efficiency in [0.0, 1.0].
        """
        exergy_helium = specific_flow_exergy(
            h_j_kg=float(h_out),
            s_j_kgk=float(s_out),
            h0_j_kg=float(h_in),
            s0_j_kgk=float(s_in),
            t0_k=float(self.T0),
        )
        useful_work = mass_flow_he * exergy_helium
        if nitrogen_assist:
            useful_work *= self.nitrogen_assist_gain
        if power_input_w <= 0:
            return 0.0
        return min(max(useful_work / power_input_w, 0.0), 1.0)

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
