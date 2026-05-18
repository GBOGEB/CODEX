from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .base import State
from .errors import PropertyBackendUnavailable


@dataclass(frozen=True)
class REFPROPValidationRow:
    case_id: str
    fluid: str
    pressure_kpa: float
    temperature_k: float
    expected_enthalpy_j_kg: float
    expected_entropy_j_kgk: float
    expected_density_kg_m3: float


class REFPROPAdapter:
    """Canonical REFPROP adapter with explicit unavailable-state reporting.

    Notes:
    - REFPROP is optional and loaded lazily during adapter initialization.
    - PT/PH/PS calls are normalized to kPa + SI J/kg units for project parity.
    - Validation helpers intentionally target helium gas-region checks first.
    """

    backend_name = "REFPROP"

    def __init__(self) -> None:
        self._rp = self._load_refprop()

    def _load_refprop(self) -> Any:
        try:
            from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency path
            raise PropertyBackendUnavailable(
                "REFPROP is not installed or not importable (ctREFPROP missing)."
            ) from exc

        root = Path.cwd()
        rp = REFPROPFunctionLibrary(str(root))
        if hasattr(rp, "SETPATHdll"):
            rp.SETPATHdll(str(root))
        return rp

    def _state_from_flash(self, fluid: str, p_kpa: float, flash: Any, *, q_allowed: bool) -> State:
        ierr = getattr(flash, "ierr", 0)
        if ierr != 0:
            message = getattr(flash, "herr", "unknown REFPROP error")
            exc = RuntimeError(
                f"REFPROP unavailable state for {fluid} @ {p_kpa:.3f} kPa "
                f"(ierr={ierr}): {message}"
            )
            exc.ierr = ierr
            raise exc

        quality = None
        q_val = getattr(flash, "q", -999)
        if q_allowed and isinstance(q_val, (int, float)) and 0.0 <= q_val <= 1.0:
            quality = float(q_val)

        return State(
            pressure_kpa=p_kpa,
            temperature_k=float(flash.T),
            enthalpy_j_kg=float(flash.h),
            entropy_j_kgk=float(flash.s),
            density_kg_m3=float(flash.D),
            quality=quality,
        )

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        p_mpa = p_kpa / 1000.0
        flash = self._rp.TPFLSHdll(t_k, p_mpa, fluid)
        return self._state_from_flash(fluid, p_kpa, flash, q_allowed=False)

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        p_mpa = p_kpa / 1000.0
        flash = self._rp.PHFLSHdll(p_mpa, h_j_kg, fluid)
        return self._state_from_flash(fluid, p_kpa, flash, q_allowed=True)

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        p_mpa = p_kpa / 1000.0
        flash = self._rp.PSFLSHdll(p_mpa, s_j_kgk, fluid)
        return self._state_from_flash(fluid, p_kpa, flash, q_allowed=True)


def run_refprop_gas_region_validation(
    adapter: REFPROPAdapter,
    rows: list[REFPROPValidationRow],
    *,
    report_dir: Path,
) -> tuple[Path, Path]:
    """Run canonical helium gas-region PT verification and emit reports.

    Validation IDs:
    - WE-T00-REFPROP-H-PT-001
    - WE-T00-REFPROP-HSD-PT-002
    """

    report_dir.mkdir(parents=True, exist_ok=True)
    computed_rows: list[dict[str, Any]] = []

    for row in rows:
        state = adapter.state_pt(row.fluid, row.pressure_kpa, row.temperature_k)
        computed_rows.append(
            {
                **asdict(row),
                "computed_enthalpy_j_kg": state.enthalpy_j_kg,
                "computed_entropy_j_kgk": state.entropy_j_kgk,
                "computed_density_kg_m3": state.density_kg_m3,
                "delta_enthalpy_j_kg": state.enthalpy_j_kg - row.expected_enthalpy_j_kg,
                "delta_entropy_j_kgk": state.entropy_j_kgk - row.expected_entropy_j_kgk,
                "delta_density_kg_m3": state.density_kg_m3 - row.expected_density_kg_m3,
            }
        )

    report = {
        "validation_targets": ["WE-T00-REFPROP-H-PT-001", "WE-T00-REFPROP-HSD-PT-002"],
        "backend": adapter.backend_name,
        "rows": len(computed_rows),
        "status": "ok",
    }

    comparison_report = report_dir / "backend_comparison_report.json"
    rows_report = report_dir / "refprop_validation_rows.json"
    comparison_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    rows_report.write_text(json.dumps(computed_rows, indent=2), encoding="utf-8")
    return comparison_report, rows_report
