from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from gistau_ch15.properties.errors import PropertyBackendUnavailable


@dataclass(frozen=True)
class CoolPropGridPoint:
    point_id: str
    region: str
    temperature_k: float
    pressure_mbar: float
    backend: str
    available: bool
    enthalpy_j_kg: float | None
    entropy_j_kgk: float | None
    density_kg_m3: float | None
    specific_volume_m3_kg: float | None
    gibbs_j_kg: float | None
    exergy_j_kg: float | None
    status: str
    notes: str


def _target_points() -> list[tuple[str, str, float, float]]:
    """Initial low-temperature helium state grid targets.

    Pressure is stored in mbar so it aligns with the visual portal and VLP
    operating-region language. CoolProp receives pressure in Pa.
    """

    return [
        ("P-A-SUPPLY", "SHe supply about 4.5 K / 3 bar", 4.5, 3000.0),
        ("P-VLP-RETURN-2K", "VLP return 2 K / 26 mbar", 2.0, 26.0),
        ("P-VLP-RETURN-5K", "VLP return 5 K / 26 mbar", 5.0, 26.0),
        ("P-VLP-RETURN-10K", "VLP return 10 K / 26 mbar", 10.0, 26.0),
        ("P-DOME-31MBAR", "dome focus 1.8 K / 31 mbar", 1.8, 31.0),
        ("P-DOME-2BAR", "dome focus 5 K / 2 bar", 5.0, 2000.0),
        ("P-CC-250MBAR", "cold compressor stage 5 K / 250 mbar", 5.0, 250.0),
        ("P-CC-550MBAR", "cold compressor stage 8 K / 550 mbar", 8.0, 550.0),
    ]


def _unavailable_rows(reason: str) -> list[CoolPropGridPoint]:
    rows: list[CoolPropGridPoint] = []
    for point_id, region, temperature_k, pressure_mbar in _target_points():
        rows.append(
            CoolPropGridPoint(
                point_id=point_id,
                region=region,
                temperature_k=temperature_k,
                pressure_mbar=pressure_mbar,
                backend="CoolProp",
                available=False,
                enthalpy_j_kg=None,
                entropy_j_kgk=None,
                density_kg_m3=None,
                specific_volume_m3_kg=None,
                gibbs_j_kg=None,
                exergy_j_kg=None,
                status="backend_unavailable",
                notes=reason,
            )
        )
    return rows


def build_coolprop_state_grid(fluid: str = "Helium", ambient_temperature_k: float = 300.0) -> list[CoolPropGridPoint]:
    """Build a CoolProp-backed state grid if CoolProp is installed.

    The function is intentionally CI-safe. If CoolProp is missing, it returns
    explicit unavailable rows instead of raising.
    """

    try:
        import CoolProp.CoolProp as CP  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency path
        return _unavailable_rows(f"CoolProp unavailable: {exc}")

    rows: list[CoolPropGridPoint] = []
    for point_id, region, temperature_k, pressure_mbar in _target_points():
        pressure_pa = pressure_mbar * 100.0
        try:
            h = float(CP.PropsSI("H", "T", temperature_k, "P", pressure_pa, fluid))
            s = float(CP.PropsSI("S", "T", temperature_k, "P", pressure_pa, fluid))
            rho = float(CP.PropsSI("D", "T", temperature_k, "P", pressure_pa, fluid))
            g = h - temperature_k * s
            exergy = h - ambient_temperature_k * s
            rows.append(
                CoolPropGridPoint(
                    point_id=point_id,
                    region=region,
                    temperature_k=temperature_k,
                    pressure_mbar=pressure_mbar,
                    backend="CoolProp",
                    available=True,
                    enthalpy_j_kg=h,
                    entropy_j_kgk=s,
                    density_kg_m3=rho,
                    specific_volume_m3_kg=None if rho == 0 else 1.0 / rho,
                    gibbs_j_kg=g,
                    exergy_j_kg=exergy,
                    status="ok",
                    notes="CoolProp state call succeeded",
                )
            )
        except Exception as exc:  # pragma: no cover - backend state-domain path
            rows.append(
                CoolPropGridPoint(
                    point_id=point_id,
                    region=region,
                    temperature_k=temperature_k,
                    pressure_mbar=pressure_mbar,
                    backend="CoolProp",
                    available=True,
                    enthalpy_j_kg=None,
                    entropy_j_kgk=None,
                    density_kg_m3=None,
                    specific_volume_m3_kg=None,
                    gibbs_j_kg=None,
                    exergy_j_kg=None,
                    status="state_error",
                    notes=str(exc),
                )
            )
    return rows


def build_coolprop_state_grid_report() -> list[dict[str, Any]]:
    return [asdict(row) for row in build_coolprop_state_grid()]
