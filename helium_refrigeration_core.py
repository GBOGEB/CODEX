#!/usr/bin/env python3
from math import sqrt


def _covariance_correlation(claimed_vector, actual_vector):
    """Shared helper: Pearson sample covariance and correlation coefficient."""
    c = [float(v) for v in claimed_vector]
    a = [float(v) for v in actual_vector]
    n = len(c)
    if n != len(a) or n < 2:
        return 0.0, 0.0

    mean_c = sum(c) / n
    mean_a = sum(a) / n

    cov_num = sum((x - mean_c) * (y - mean_a) for x, y in zip(c, a))
    covariance = cov_num / (n - 1)

    var_c = sum((x - mean_c) ** 2 for x in c)
    var_a = sum((y - mean_a) ** 2 for y in a)
    denom = sqrt(var_c * var_a)
    correlation = (cov_num / denom) if denom else 0.0
    return float(covariance), float(correlation)


class CryogenicHeliumEngine:
    """Baseline cryogenic helium engine (generation-agnostic interface).

    Power is expressed in kW; enthalpy and entropy in consistent kJ-based units.
    """

    def __init__(self, t0_ambient=298.15):
        self.T0 = t0_ambient

    def compute_exergy_efficiency(
        self,
        mass_flow,
        enthalpy_in,
        enthalpy_out,
        entropy_in,
        entropy_out,
        power_kw,
    ):
        """Compute flow exergy efficiency.

        Returns:
            Efficiency clamped to ``[0.0, 1.0]``, or ``0.0`` when
            *power_kw* is non-positive.
        """
        delta_h = float(enthalpy_out) - float(enthalpy_in)
        delta_s = float(entropy_out) - float(entropy_in)
        useful_work = float(mass_flow) * (delta_h - self.T0 * delta_s)
        if power_kw <= 0:
            return 0.0
        return min(max(useful_work / float(power_kw), 0.0), 1.0)

    def calculate_covariance(self, claimed, actual):
        """Return Pearson sample covariance of two equal-length vectors."""
        cov, _ = _covariance_correlation(claimed, actual)
        return cov

    def calculate_anova_variance(self, claimed, actual):
        """Return mean squared difference between two equal-length vectors."""
        c = [float(v) for v in claimed]
        a = [float(v) for v in actual]
        n = len(c)
        if n != len(a) or n < 2:
            return 0.0
        return sum((ci - ai) ** 2 for ci, ai in zip(c, a)) / n


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
        return _covariance_correlation(claimed, actual)


class CryogenicHeliumEngineG7:
    """G7 cryogenic helium engine — nitrogen assist *increases* efficiency.

    Nitrogen assist applies a 10% *gain* (factor 1.10) to the computed useful
    work, raising efficiency compared to the unassisted case.
    """

    def __init__(self, t0_ambient=298.15, nitrogen_assist_gain=1.10):
        self.T0 = t0_ambient
        self.nitrogen_assist_gain = nitrogen_assist_gain

    def compute_g7_exergy_efficiency(
        self,
        mass_flow_he,
        h_in,
        h_out,
        s_in,
        s_out,
        power_input_kw,
        nitrogen_assist=True,
    ):
        """Compute exergy efficiency of the G7 cryogenic helium engine.

        Args:
            mass_flow_he: Helium mass flow rate (kg/s).
            h_in: Inlet specific enthalpy (kJ/kg).
            h_out: Outlet specific enthalpy (kJ/kg).
            s_in: Inlet specific entropy (kJ/(kg·K)).
            s_out: Outlet specific entropy (kJ/(kg·K)).
            power_input_kw: Shaft power input (kW).
            nitrogen_assist: When ``True`` a 10% gain is applied to useful
                work, *increasing* the computed efficiency.

        Returns:
            Exergy efficiency in ``[0.0, 1.0]``.
        """
        delta_h = float(h_out) - float(h_in)
        delta_s = float(s_out) - float(s_in)
        useful_work = float(mass_flow_he) * (delta_h - self.T0 * delta_s)
        if nitrogen_assist:
            useful_work *= self.nitrogen_assist_gain
        if power_input_kw <= 0:
            return 0.0
        return min(max(useful_work / float(power_input_kw), 0.0), 1.0)

    def calculate_pearson_correlation(self, claimed_vector, actual_vector):
        """Return (covariance, Pearson r) for two numeric vectors."""
        return _covariance_correlation(claimed_vector, actual_vector)
