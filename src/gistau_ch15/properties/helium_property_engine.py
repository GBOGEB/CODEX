"""He-4 enthalpy polynomial engine and mass-balance verifier.

Adapted from GBOGEB/cryogenic-accelerator-workspace (src/physics_validator.py).
Provides a self-contained NIST-fitted polynomial for helium-4 enthalpy near the
lambda point (4–10 K range at 1 bar) and a mass-balance verification utility.

References
----------
NIST Standard Reference Database 23 — Helium fluid models.
"""

from __future__ import annotations

import numpy as np

from ..kernels.helium_reference import T_LAMBDA_K


class HeliumPropertyEngine:
    """Polynomial enthalpy model for He-4 at 1 bar.

    Coefficients are fitted to NIST data in the 4–10 K range.  For
    temperatures at or below the lambda point a low-temperature approximation
    is used instead (valid for orientation-level calculations only).

    Parameters
    ----------
    poly_coeffs:
        Optional 1-D array of coefficients ``[c0, c1, c2]`` for the quadratic
        polynomial ``h = c0 + c1·T + c2·T²`` [J/g].  Defaults to the values
        derived from NIST reference data.
    """

    #: Default polynomial coefficients [c0, c1, c2] (J/g) for 4–10 K at 1 bar
    DEFAULT_POLY_COEFFS: tuple[float, float, float] = (-1.24, 5.72, 12.31)

    def __init__(
        self,
        poly_coeffs: tuple[float, float, float] | None = None,
    ) -> None:
        coeffs = poly_coeffs if poly_coeffs is not None else self.DEFAULT_POLY_COEFFS
        self._coeffs = np.array(coeffs, dtype=float)

    def get_enthalpy(self, temperature_k: float, pressure_bar: float = 1.0) -> float:
        """Return specific enthalpy [J/g] for He-4 at the given state.

        Parameters
        ----------
        temperature_k:
            Temperature [K].  Must be positive.
        pressure_bar:
            Pressure [bar].  This implementation uses a single 1-bar
            polynomial; the argument is accepted for interface compatibility
            but currently ignored for pressures ≠ 1 bar.

        Returns
        -------
        float
            Enthalpy [J/g].
        """
        if temperature_k <= 0.0:
            raise ValueError(f"Temperature must be positive, got {temperature_k} K")
        # Below lambda point: use low-temperature power-law approximation
        if temperature_k < T_LAMBDA_K:
            return 4.22 * (temperature_k ** 5.6)
        t_vec = np.array([1.0, temperature_k, temperature_k ** 2])
        return float(np.dot(self._coeffs, t_vec))


def verify_mass_balance(
    total_heat_load_w: float,
    t_in_k: float = 4.2,
    t_out_k: float = 4.5,
    p_bar: float = 1.0,
    warn_limit_kg_s: float = 0.2,
    engine: HeliumPropertyEngine | None = None,
) -> dict:
    """Verify helium mass-flow balance against a thermal heat load.

    Formula: ``ṁ = Q_total / Δh``

    Parameters
    ----------
    total_heat_load_w:
        Total thermal load [W].
    t_in_k:
        Inlet temperature [K].
    t_out_k:
        Outlet temperature [K].
    p_bar:
        Operating pressure [bar].
    warn_limit_kg_s:
        Mass-flow threshold above which status becomes ``WARN_LIMIT`` [kg/s].
    engine:
        Optional pre-constructed :class:`HeliumPropertyEngine`.

    Returns
    -------
    dict
        Keys: ``calculated_mass_flow_kg_s``, ``enthalpy_in_j_g``,
        ``enthalpy_out_j_g``, ``delta_h_j_g``, ``system_verification_status``.
    """
    if engine is None:
        engine = HeliumPropertyEngine()
    h_in = engine.get_enthalpy(t_in_k, p_bar)
    h_out = engine.get_enthalpy(t_out_k, p_bar)
    delta_h = h_out - h_in
    if abs(delta_h) < 1e-12:
        raise ValueError("Enthalpy difference is effectively zero; check T_in/T_out.")
    # Convert W → J/s, enthalpy in J/g → multiply mass flow by 1000 to stay in kg/s
    mass_flow_kg_s = total_heat_load_w / (delta_h * 1000.0)
    status = "PASS" if mass_flow_kg_s < warn_limit_kg_s else "WARN_LIMIT"
    return {
        "calculated_mass_flow_kg_s": round(mass_flow_kg_s, 5),
        "enthalpy_in_j_g": round(h_in, 3),
        "enthalpy_out_j_g": round(h_out, 3),
        "delta_h_j_g": round(delta_h, 3),
        "system_verification_status": status,
    }


def main() -> None:
    """Run a demonstration mass-balance check with default parameters."""
    result = verify_mass_balance(total_heat_load_w=16.0)
    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
