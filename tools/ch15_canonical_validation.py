"""L1 gate: reproduce the Ch15 worked examples with the governing helium-4 provider.

The governing provider is ABACUS ``models.helium_properties.provider.state_tp``
at the pinned commit (see governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml).
This tool adds no physics: (p, h) and (p, s) states are found by bisection on
temperature over the provider's own state_tp, which is monotonic in T at fixed
p for single-phase helium above the lambda point.

Usage (CI, after checking out ABACUS at the pinned commit):
    python tools/ch15_canonical_validation.py --abacus _abacus [--report out.json] [--check]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = REPO_ROOT / "governance" / "physics" / "CH15_CANONICAL_VALIDATION.yaml"

State = dict[str, float]
ProviderFn = Callable[[float, float], State]  # (T_K, p_kPa) -> {density_kg_m3, enthalpy_J_kg, entropy_J_kgK}

T_LOW_K = 2.18  # just above the lambda point (2.1768 K): CoolProp helium EOS lower limit
T_HIGH_K = 300.0


def _solve_t(provider: ProviderFn, p_kpa: float, key: str, target: float, lo: float = T_LOW_K, hi: float = T_HIGH_K) -> float:
    """Temperature at which provider(T, p)[key] == target (bisection; key monotonic in T)."""
    f_lo = provider(lo, p_kpa)[key] - target
    f_hi = provider(hi, p_kpa)[key] - target
    if f_lo * f_hi > 0:
        raise ValueError(f"{key}={target} not bracketed at {p_kpa} kPa between {lo} and {hi} K")
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        f_mid = provider(mid, p_kpa)[key] - target
        if (f_mid > 0) == (f_hi > 0):
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
        if hi - lo < 1e-9:
            break
    return 0.5 * (lo + hi)


def compute(example: dict[str, Any], provider: ProviderFn) -> dict[str, float]:
    """Return the quantities the worked example reports, computed from the provider (book units)."""
    eid, i = example["example_id"], example["inputs"]
    if eid == "WE-T00-REFPROP-HSD-PT-002":
        s = provider(i["temperature_k"], i["pressure_bar"] * 100.0)
        return {"enthalpy_j_g": s["enthalpy_J_kg"] / 1000, "entropy_j_gk": s["entropy_J_kgK"] / 1000, "density_kg_m3": s["density_kg_m3"]}
    if eid == "WE-T02-FREE-EXPANSION-HEAT-001":
        h_in = provider(i["inlet_temperature_k"], i["inlet_pressure_bar"] * 100.0)["enthalpy_J_kg"]
        h_out = h_in + i["thermal_power_w"] / (i["mass_flow_g_s"] / 1000.0)
        t_out = _solve_t(provider, i["outlet_pressure_bar"] * 100.0, "enthalpy_J_kg", h_out)
        return {"outlet_temperature_k": t_out, "inlet_enthalpy_j_g": h_in / 1000, "outlet_enthalpy_j_g": h_out / 1000}
    if eid == "WE-T02-MASS-FLOW-004":
        h_in = provider(i["inlet_temperature_k"], i["inlet_pressure_bar"] * 100.0)["enthalpy_J_kg"]
        h_out = provider(i["outlet_temperature_k"], i["outlet_pressure_bar"] * 100.0)["enthalpy_J_kg"]
        return {
            "mass_flow_g_s": i["thermal_power_w"] / (h_out - h_in) * 1000.0,
            "inlet_enthalpy_j_g": h_in / 1000,
            "outlet_enthalpy_j_g": h_out / 1000,
        }
    if eid in ("WE-T04-CRYOGENIC-EXPANDER-001", "WE-T05-CRYOGENIC-COMPRESSOR-001"):
        p1, p2 = i["inlet_pressure_bar"] * 100.0, i["outlet_pressure_bar"] * 100.0
        inlet = provider(i["inlet_temperature_k"], p1)
        t2s = _solve_t(provider, p2, "entropy_J_kgK", inlet["entropy_J_kgK"])
        h2s = provider(t2s, p2)["enthalpy_J_kg"]
        eta = i["isentropic_efficiency"]
        expander = eid.startswith("WE-T04")
        dh = (inlet["enthalpy_J_kg"] - h2s) * eta if expander else (h2s - inlet["enthalpy_J_kg"]) / eta
        h2 = inlet["enthalpy_J_kg"] - dh if expander else inlet["enthalpy_J_kg"] + dh
        t2 = _solve_t(provider, p2, "enthalpy_J_kg", h2)
        mdot = i["mass_flow_g_s"] / 1000.0
        out = {"outlet_temperature_k": t2, "outlet_enthalpy_j_g": h2 / 1000}
        out["power_w_visible" if expander else "power_w"] = (-mdot * dh) if expander else (mdot * dh)
        return out
    raise KeyError(f"no computation defined for {eid}")


def _tolerance(quantity: str, expected: float, tol: dict[str, float]) -> tuple[str, float]:
    if quantity.endswith("temperature_k"):
        return "abs", tol["temperature_abs_K"]
    if quantity.startswith("density"):
        return "rel", tol["density_rel"]
    if quantity.endswith("enthalpy_j_g"):
        return "abs", tol["enthalpy_abs_J_g"]
    if quantity.startswith("entropy"):
        return "abs", tol["entropy_abs_J_gK"]
    return "rel", tol["derived_rel"]


def validate(gate: dict[str, Any], examples: list[dict[str, Any]], provider: ProviderFn) -> dict[str, Any]:
    by_id = {e["example_id"]: e for e in examples}
    open_items = gate.get("source_check_required", {}) or {}
    listed = set(gate["checked"]) | set(gate["excluded"]) | set(open_items)
    unaccounted = sorted(set(by_id) - listed)
    unknown = sorted(listed - set(by_id))
    rows = []
    for eid in list(gate["checked"]) + list(open_items):
        got = compute(by_id[eid], provider)
        for quantity, expected in by_id[eid]["expected_outputs"].items():
            if quantity not in got:
                continue
            kind, limit = _tolerance(quantity, expected, gate["tolerances"])
            dev = got[quantity] - expected if kind == "abs" else (got[quantity] - expected) / expected
            rows.append(
                {
                    "example_id": eid,
                    "quantity": quantity,
                    "expected": expected,
                    "computed": got[quantity],
                    "deviation": dev,
                    "deviation_kind": kind,
                    "tolerance": limit,
                    "verdict": ("PASS" if abs(dev) <= limit else "FAIL") if eid not in open_items else (
                        "OPEN_MATCH" if abs(dev) <= limit else "OPEN_MISMATCH"
                    ),
                }
            )
    failures = [r for r in rows if r["verdict"] == "FAIL"]
    gated = [r for r in rows if r["example_id"] not in open_items]
    return {
        "gate_id": gate["gate_id"],
        "examples_total": len(by_id),
        "examples_checked": len(gate["checked"]),
        "examples_excluded": len(gate["excluded"]),
        "examples_source_check_required": sorted(open_items),
        "unaccounted_examples": unaccounted,
        "unknown_gate_entries": unknown,
        "quantities_checked": len(gated),
        "failures": len(failures),
        "status": "PASS" if gated and not failures and not unaccounted and not unknown else "FAIL",
        "rows": rows,
    }


def _sig(x: float, digits: int = 8) -> float:
    return float(f"{x:.{digits}g}")


def record_view(report: dict[str, Any]) -> dict[str, Any]:
    """Canonical, comparable view of a run (rounded) for the committed record."""
    return {
        "coolprop_version": report.get("coolprop_version"),
        "status": report["status"],
        "examples_checked": report["examples_checked"],
        "examples_source_check_required": report["examples_source_check_required"],
        "examples_excluded": report["examples_excluded"],
        "rows": [
            {
                "example_id": r["example_id"],
                "quantity": r["quantity"],
                "expected": r["expected"],
                "computed": _sig(r["computed"]),
                "deviation": _sig(r["deviation"], 4),
                "deviation_kind": r["deviation_kind"],
                "tolerance": r["tolerance"],
                "verdict": r["verdict"],
            }
            for r in report["rows"]
        ],
    }


def compare_record(fresh: dict[str, Any], recorded: dict[str, Any]) -> list[str]:
    """Differences between a fresh run and the committed record (record = fresh, rounded)."""
    problems = []
    if recorded.get("record") in (None, "PENDING_FIRST_CI_RECORD"):
        return ["RECORD_PENDING: copy the 'L1 record' annotation into the record file"]
    rec = recorded["record"]
    for key in ("coolprop_version", "status", "examples_checked", "examples_source_check_required", "examples_excluded"):
        if fresh[key] != rec.get(key):
            problems.append(f"RECORD_DRIFT {key}: fresh {fresh[key]!r} != recorded {rec.get(key)!r}")
    f_rows = {(r["example_id"], r["quantity"]): r for r in fresh["rows"]}
    r_rows = {(r["example_id"], r["quantity"]): r for r in rec.get("rows", [])}
    if set(f_rows) != set(r_rows):
        problems.append(f"RECORD_DRIFT rows: fresh-only {sorted(set(f_rows) - set(r_rows))}, recorded-only {sorted(set(r_rows) - set(f_rows))}")
    for k in sorted(set(f_rows) & set(r_rows)):
        a, b = f_rows[k], r_rows[k]
        if a["verdict"] != b["verdict"] or a["expected"] != b["expected"] or abs(a["computed"] - b["computed"]) > 1e-6 * max(1.0, abs(b["computed"])):
            problems.append(f"RECORD_DRIFT {k[0]}:{k[1]}: fresh {a['computed']} {a['verdict']} != recorded {b['computed']} {b['verdict']}")
    return problems


def _load_examples(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data["examples"]


def _abacus_provider(abacus: Path) -> tuple[ProviderFn, str]:
    spec = importlib.util.spec_from_file_location("physics_crosscheck", REPO_ROOT / "tools" / "physics_crosscheck.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.abacus_provider(abacus)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--abacus", type=Path, required=True)
    ap.add_argument("--gate", type=Path, default=GATE_PATH)
    ap.add_argument("--report", type=Path)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit-record", action="store_true", help="print the canonical record as an annotation")
    ap.add_argument("--expect-record", type=Path, help="fail unless the committed record matches this run")
    args = ap.parse_args(argv)

    gate = yaml.safe_load(args.gate.read_text(encoding="utf-8"))
    examples = _load_examples(REPO_ROOT / gate["source"])
    provider, cp_version = _abacus_provider(args.abacus)
    report = validate(gate, examples, provider)
    report["coolprop_version"] = cp_version
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")

    cells = [
        f"{r['example_id'].replace('WE-', '')}:{r['quantity']} {r['verdict']} {r['computed']:.4g} vs {r['expected']:g} "
        f"({r['deviation']:+.3g}{'' if r['deviation_kind'] == 'abs' else ' rel'})"
        for r in report["rows"]
    ]
    print(
        f"::notice title=Ch15 canonical validation ({report['status']})::CoolProp {cp_version} | "
        f"{report['examples_checked']} checked, {len(report['examples_source_check_required'])} open (source check), "
        f"{report['examples_excluded']} excluded of {report['examples_total']} | "
        f"{report['quantities_checked']} quantities, {report['failures']} fail"
    )
    half = (len(cells) + 1) // 2
    for i in range(0, len(cells), half):
        print("::notice title=Ch15 worked examples::" + " | ".join(cells[i : i + half]))
    view = record_view(report)
    if args.emit_record:
        print("::notice title=L1 record::" + json.dumps(view, sort_keys=True, separators=(",", ":")))
    if args.expect_record:
        problems = compare_record(view, json.loads(args.expect_record.read_text(encoding="utf-8")))
        for prob in problems:
            print(f"::error title=L1 record::{prob}")
        if problems:
            return 1
    if args.check and report["status"] != "PASS":
        print(f"::error title=Ch15 canonical validation::status {report['status']} (failures {report['failures']}, "
              f"unaccounted {report['unaccounted_examples']}, unknown {report['unknown_gate_entries']})")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
