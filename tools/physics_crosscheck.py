"""Cross-check the pinned ABACUS helium-4 provider against GISTAU's basic incarnation.

Runs the governing provider (ABACUS ``models.helium_properties.provider.state_tp``
at the commit in governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml) over the
grid declared in the pin, then:

1. **Output meta checksum**: sha256 of the provider's rounded outputs plus the
   CoolProp version. A different number means the governing physics changed
   (other commit, other CoolProp, other coefficients) and must be re-pinned on
   purpose.
2. **Basic-incarnation cross-check**: the ideal-gas backend is compared with
   the provider. Inside its declared validity domain deviations must stay
   within the pin's tolerances; outside it they are reported, never judged.
   Disagreement is a signal, never averaged away.

Usage (CI, after checking out ABACUS at the pinned commit):
    python tools/physics_crosscheck.py --abacus _abacus --report out.json          # record
    python tools/physics_crosscheck.py --abacus _abacus --report out.json --check  # gate
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PIN_PATH = REPO_ROOT / "governance" / "physics" / "HE4_PROPERTY_AUTHORITY_PIN.yaml"
PENDING = "PENDING_FIRST_CI_RECORD"

ProviderFn = Callable[[float, float], dict[str, float]]


def _sig(value: float, digits: int) -> float:
    return float(f"{value:.{digits}g}")


def load_pin(path: Path = PIN_PATH) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def grid_points(spec: dict[str, Any]) -> list[tuple[float, float]]:
    """In-domain grid (T x p) followed by the explicit out-of-domain probes."""
    points = [(float(t), float(p)) for t in spec["grid_T_K"] for p in spec["grid_p_kPa"]]
    points += [(float(t), float(p)) for t, p in spec["probes_T_K_p_kPa"]]
    return points


def abacus_provider(abacus_root: Path) -> tuple[ProviderFn, str]:
    """Import ABACUS's governed provider from a checkout; return (fn, CoolProp version)."""
    root = str(abacus_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    module = importlib.import_module("models.helium_properties.provider")

    def fn(t_k: float, p_kpa: float) -> dict[str, float]:
        st = module.state_tp(t_k, p_kpa * 1000.0)
        return {"density_kg_m3": st.density_kg_m3, "enthalpy_J_kg": st.enthalpy_J_kg, "entropy_J_kgK": st.entropy_J_kgK}

    coolprop = importlib.import_module("CoolProp")
    return fn, str(getattr(coolprop, "__version__", "unknown"))


def basic_incarnation() -> tuple[ProviderFn, Callable[[float, float], bool]]:
    src = str(REPO_ROOT / "src")
    if src not in sys.path:
        sys.path.append(src)
    from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend

    backend = FallbackHeliumBackend()

    def fn(t_k: float, p_kpa: float) -> dict[str, float]:
        st = backend.state_pt("helium", p_kpa, t_k)
        return {"density_kg_m3": st.density_kg_m3, "enthalpy_J_kg": st.enthalpy_j_kg, "entropy_J_kgK": st.entropy_j_kgk}

    def in_domain(t_k: float, p_kpa: float) -> bool:
        return backend.in_validity_domain(p_kpa, t_k)  # backend signature is (p, T)

    return fn, in_domain


def output_checksum(rows: list[dict[str, Any]], coolprop_version: str, digits: int) -> str:
    payload = {
        "coolprop_version": coolprop_version,
        "rows": [
            {"T_K": r["T_K"], "p_kPa": r["p_kPa"], **{k: _sig(v, digits) for k, v in r["governing"].items()}}
            for r in rows
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run(
    spec: dict[str, Any],
    governing: ProviderFn,
    basic: ProviderFn,
    in_domain: Callable[[float, float], bool],
    coolprop_version: str,
) -> dict[str, Any]:
    ref_t, ref_p = spec["reference_T_K_p_kPa"]
    g_ref, b_ref = governing(ref_t, ref_p), basic(ref_t, ref_p)
    tol = spec["tolerances_in_domain"]
    rows: list[dict[str, Any]] = []
    for t, p in grid_points(spec):
        g, b = governing(t, p), basic(t, p)
        d_rho = (b["density_kg_m3"] - g["density_kg_m3"]) / g["density_kg_m3"]
        dh_g, dh_b = g["enthalpy_J_kg"] - g_ref["enthalpy_J_kg"], b["enthalpy_J_kg"] - b_ref["enthalpy_J_kg"]
        ds_g, ds_b = g["entropy_J_kgK"] - g_ref["entropy_J_kgK"], b["entropy_J_kgK"] - b_ref["entropy_J_kgK"]
        is_ref = (t, p) == (float(ref_t), float(ref_p))
        abs_dh = dh_b - dh_g
        rel_dh = 0.0 if is_ref else abs_dh / max(abs(dh_g), 1e-12)
        abs_ds = ds_b - ds_g
        dom = in_domain(t, p)
        failures = []
        if dom:
            if abs(d_rho) > tol["density_rel"]:
                failures.append("density")
            # Ideal-gas h has no pressure dependence, so isothermal points have
            # dh_basic = 0 and a relative test is ill-conditioned. Judge the
            # absolute deviation against the sensible enthalpy h_basic = cp*T.
            if abs(abs_dh) > tol["delta_h_frac_of_cpT"] * b["enthalpy_J_kg"]:
                failures.append("delta_h")
            if abs(abs_ds) > tol["delta_s_abs_J_kgK"]:
                failures.append("delta_s")
        rows.append(
            {
                "T_K": t,
                "p_kPa": p,
                "in_domain": dom,
                "governing": g,
                "basic": b,
                "density_rel_dev": d_rho,
                "delta_h_rel_dev": rel_dh,
                "delta_h_abs_dev_J_kg": abs_dh,
                "delta_s_abs_dev_J_kgK": abs_ds,
                "verdict": ("FAIL:" + ",".join(failures)) if failures else ("PASS" if dom else "NOT_APPLICABLE"),
            }
        )
    in_rows = [r for r in rows if r["in_domain"]]

    def worst(key: str, subset: list[dict[str, Any]]) -> float:
        return max((abs(r[key]) for r in subset), default=float("nan"))

    return {
        "coolprop_version": coolprop_version,
        "output_checksum_sha256": output_checksum(rows, coolprop_version, spec["round_significant_digits"]),
        "points": len(rows),
        "in_domain_points": len(in_rows),
        "in_domain_failures": sum(1 for r in in_rows if r["verdict"].startswith("FAIL")),
        "worst_in_domain": {k: worst(k, in_rows) for k in ("density_rel_dev", "delta_h_abs_dev_J_kg", "delta_s_abs_dev_J_kgK")},
        "worst_out_of_domain": {
            k: worst(k, [r for r in rows if not r["in_domain"]])
            for k in ("density_rel_dev", "delta_h_abs_dev_J_kg", "delta_s_abs_dev_J_kgK")
        },
        "rows": rows,
    }


def nist_check(nist: dict[str, Any], governing: ProviderFn) -> dict[str, Any]:
    """Advisory validation of the governing provider against NIST TN 1334 rows.

    Density is compared directly; enthalpy only as differences from the
    reference row, because NIST and CoolProp use different h reference states.
    All rows are <= 4.5 K (HEPAK-governed under QPLANT policy), so this is a
    reference check of the provider, never a governance decision.
    """
    tol = nist["tolerances"]
    ref_id = nist["reference_state"]
    states = {s["id"]: s for s in nist["states"]}
    g = {sid: governing(s["T_K"], s["p_Pa"] / 1000.0) for sid, s in states.items()}
    ref, g_ref = states[ref_id], g[ref_id]
    rows = []
    for sid, s in states.items():
        row: dict[str, Any] = {"id": sid, "T_K": s["T_K"], "p_Pa": s["p_Pa"], "failures": []}
        if "density_kg_m3" in s:
            dev = (g[sid]["density_kg_m3"] - s["density_kg_m3"]) / s["density_kg_m3"]
            row["density_rel_dev"] = dev
            if abs(dev) > tol["density_rel"]:
                row["failures"].append("density")
        if sid != ref_id:
            dh_nist = s["enthalpy_J_kg"] - ref["enthalpy_J_kg"]
            dh_gov = g[sid]["enthalpy_J_kg"] - g_ref["enthalpy_J_kg"]
            dev = (dh_gov - dh_nist) / dh_nist
            row["delta_h_from_ref_rel_dev"] = dev
            if abs(dev) > tol["delta_h_rel"]:
                row["failures"].append("delta_h")
        row["verdict"] = ("FAIL:" + ",".join(row["failures"])) if row["failures"] else "PASS"
        rows.append(row)
    return {"rows": rows, "failures": sum(1 for r in rows if r["failures"]), "checks": len(rows)}


def gate(report: dict[str, Any], spec: dict[str, Any]) -> list[str]:
    """Problems that fail the --check gate."""
    problems = []
    if report["in_domain_points"] == 0:
        problems.append("ZERO_IN_DOMAIN_POINTS: a cross-check that compares nothing is a failure")
    if report["in_domain_failures"]:
        problems.append(f"IN_DOMAIN_TOLERANCE: {report['in_domain_failures']} point(s) outside tolerance")
    expected = spec.get("output_checksum_sha256", PENDING)
    if expected == PENDING:
        problems.append("OUTPUT_CHECKSUM_NOT_RECORDED: record it in the pin first")
    elif expected != report["output_checksum_sha256"]:
        problems.append(f"OUTPUT_DRIFT: provider outputs {report['output_checksum_sha256']} != pinned {expected}")
    nist = report.get("nist_reference")
    if nist is not None and nist["failures"]:
        problems.append(f"NIST_REFERENCE_TOLERANCE: {nist['failures']} of {nist['checks']} NIST TN 1334 checks outside tolerance")
    if spec.get("coolprop_version") and spec["coolprop_version"] != report["coolprop_version"]:
        problems.append(f"COOLPROP_VERSION: {report['coolprop_version']} != pinned {spec['coolprop_version']}")
    return problems


def _fmt(x: float) -> str:
    return "nan" if isinstance(x, float) and math.isnan(x) else f"{x:.3g}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--abacus", type=Path, required=True)
    ap.add_argument("--pin", type=Path, default=PIN_PATH)
    ap.add_argument("--report", type=Path, help="write the full JSON report here")
    ap.add_argument("--check", action="store_true", help="fail on drift, in-domain tolerance or missing record")
    args = ap.parse_args(argv)

    spec = load_pin(args.pin)["output_crosscheck"]
    governing, cp_version = abacus_provider(args.abacus)
    basic, in_domain = basic_incarnation()
    report = run(spec, governing, basic, in_domain, cp_version)
    if "nist_reference" in spec:
        report["nist_reference"] = nist_check(spec["nist_reference"], governing)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")

    wi, wo = report["worst_in_domain"], report["worst_out_of_domain"]
    print(
        f"::notice title=Physics crosscheck::CoolProp {report['coolprop_version']} | output checksum "
        f"{report['output_checksum_sha256']} | in-domain {report['in_domain_points']}/{report['points']} points, "
        f"{report['in_domain_failures']} fail | worst in-domain rho {_fmt(wi['density_rel_dev'])}, "
        f"dh {_fmt(wi['delta_h_abs_dev_J_kg'])} J/kg, ds {_fmt(wi['delta_s_abs_dev_J_kgK'])} J/kgK | worst outside rho "
        f"{_fmt(wo['density_rel_dev'])}, dh {_fmt(wo['delta_h_abs_dev_J_kg'])} J/kg, ds {_fmt(wo['delta_s_abs_dev_J_kgK'])} J/kgK"
    )
    lines = [
        f"{r['T_K']:g}K/{r['p_kPa']:g}kPa {r['verdict']} rho {r['density_rel_dev']:+.3%} "
        f"dh {r['delta_h_abs_dev_J_kg']:+.0f}J/kg ds {r['delta_s_abs_dev_J_kgK']:+.1f}J/kgK"
        for r in report["rows"]
    ]
    for line in lines:
        print(line)
    if "nist_reference" in report:
        nr = report["nist_reference"]
        cells = []
        for r in nr["rows"]:
            parts = [f"{r['id']} {r['T_K']:g}K/{r['p_Pa'] / 1000:g}kPa {r['verdict']}"]
            if "density_rel_dev" in r:
                parts.append(f"rho {r['density_rel_dev']:+.3%}")
            if "delta_h_from_ref_rel_dev" in r:
                parts.append(f"dh-from-ref {r['delta_h_from_ref_rel_dev']:+.3%}")
            cells.append(" ".join(parts))
        print(f"::notice title=NIST TN 1334 reference ({nr['checks'] - nr['failures']}/{nr['checks']} pass)::" + " | ".join(cells))
    # Per-row table as annotations (job logs are not always reachable): 3 chunks.
    chunk = math.ceil(len(lines) / 3)
    for i in range(0, len(lines), chunk):
        print(f"::notice title=Crosscheck rows {i + 1}-{min(i + chunk, len(lines))}::" + " | ".join(lines[i : i + chunk]))
    if args.check:
        problems = gate(report, spec)
        for p in problems:
            print(f"::error title=Physics crosscheck::{p}")
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
