"""Build the GISTAU Ch15 deck content YAML from committed sources (no hand-typed figures).

Sources:
  governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml         authority, policy, NIST rows, output check
  governance/physics/CH15_CANONICAL_VALIDATION.yaml         L1 coverage and tolerances
  docs/gistau-ch15/data/l1_validation_results.json          committed L1 CI record
  docs/gistau-ch15/data/nist_reference / pin                NIST TN 1334 rows
  src/gistau_ch15/properties/fallback_helium.py             basic-incarnation domain
Output:
  slides/src/gistau_ch15/deck_content.yaml   (input to slides/deck_orchestrator.py)

Deterministic; a test fails if the committed YAML is stale. Regenerate with:
  python tools/build_gistau_deck_content.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PIN = REPO_ROOT / "governance" / "physics" / "HE4_PROPERTY_AUTHORITY_PIN.yaml"
GATE = REPO_ROOT / "governance" / "physics" / "CH15_CANONICAL_VALIDATION.yaml"
RECORD = REPO_ROOT / "docs" / "gistau-ch15" / "data" / "l1_validation_results.json"
OUTPUT = REPO_ROOT / "slides" / "src" / "gistau_ch15" / "deck_content.yaml"
PORTAL = "https://gbogeb.github.io/CODEX/gistau-ch15/"

EXAMPLE_NAMES = {
    "WE-T00-REFPROP-HSD-PT-002": "T00 state point, 1 bar / 300 K",
    "WE-T02-FREE-EXPANSION-HEAT-001": "T02 free expansion, 14 to 1 bar + 100 W",
    "WE-T02-MASS-FLOW-004": "T02 mass flow from heat input",
    "WE-T02-INVERSION-HELIUM-002": "T02 JT inversion, 14 to 1 bar",
    "WE-T03-HEAT-EXCHANGER-001": "T03 heat exchanger, 300/200 K",
    "WE-T04-CRYOGENIC-EXPANDER-001": "T04 expander, 14 to 1.2 bar",
    "WE-T05-CRYOGENIC-COMPRESSOR-001": "T05 cold compressor, 0.5 to 1.2 bar",
}
QUANTITIES = {
    "enthalpy_j_g": ("h", "J/g"), "entropy_j_gk": ("s", "J/g·K"), "density_kg_m3": ("ρ", "kg/m³"),
    "outlet_temperature_k": ("T out", "K"), "inlet_enthalpy_j_g": ("h in", "J/g"), "outlet_enthalpy_j_g": ("h out", "J/g"),
    "mass_flow_g_s": ("ṁ", "g/s"), "power_w_visible": ("P", "W"), "power_w": ("P", "W"),
    "isentropic_enthalpy_change_j_g": ("Δh isent", "J/g"), "real_enthalpy_change_j_g": ("Δh real", "J/g"),
    "inversion_temperature_k": ("T inv", "K"), "hot_outlet_temperature_k": ("T hot out", "K"), "heat_load_w": ("Q", "W"),
    "lmtd_k": ("LMTD", "K"), "ua_w_k": ("UA", "W/K"),
}


def _backend():
    src = str(REPO_ROOT / "src")
    if src not in sys.path:
        sys.path.append(src)
    from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend

    return FallbackHeliumBackend


def _g(x: float) -> str:
    return f"{x:.6g}"


def build() -> dict[str, Any]:
    pin = yaml.safe_load(PIN.read_text(encoding="utf-8"))
    gate = yaml.safe_load(GATE.read_text(encoding="utf-8"))
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    rec = record["record"]
    auth, consts, parity = pin["authority"], pin["pinned_constants"], pin["policy_parity"]
    xc = pin["output_crosscheck"]
    nist = xc["nist_reference"]
    b = _backend()
    open_items = gate.get("source_check_required", {}) or {}
    errata = gate.get("book_errata", {}) or {}

    checked_rows = [r for r in rec["rows"] if r["example_id"] in gate["checked"]]
    n_pass_q = sum(1 for r in checked_rows if r["verdict"] == "PASS")
    n_pass_ex = sum(
        1 for eid in gate["checked"] if all(r["verdict"] == "PASS" for r in checked_rows if r["example_id"] == eid)
    )

    def dev(r: dict[str, Any]) -> str:
        return f"{r['deviation'] * 100:+.3f} %" if r["deviation_kind"] == "rel" else f"{r['deviation']:+.4g}"

    l1_checklist = []
    for eid in list(gate["checked"]) + list(open_items):
        rows = [r for r in rec["rows"] if r["example_id"] == eid]
        status = "pass" if eid in gate["checked"] and all(r["verdict"] == "PASS" for r in rows) else (
            "open (source check)" if eid in open_items else "fail"
        )
        l1_checklist.append(
            {
                "id": EXAMPLE_NAMES.get(eid, eid),
                "result": status,
                "book vs provider": " · ".join(
                    f"{QUANTITIES[r['quantity']][0]} {_g(r['expected'])} vs {_g(r['computed'])} {QUANTITIES[r['quantity']][1]}" for r in rows
                ),
            }
        )

    slides = [
        {
            "title": "GISTAU Chapter 15: from book to validated model",
            "section": "OVERVIEW",
            "body": [
                "Chapter 15 thermodynamic tools rebuilt as code, a CI-gated validation and an online engineering portal.",
                f"Helium-4 physics is governed by {auth['repository']} at {auth['commit_sha'][:7]} ({auth['runtime_dependency']}); CODEX consumes it and never governs it.",
                f"L1 validated model: {n_pass_ex} of {len(gate['checked'])} checked worked examples reproduce the book ({n_pass_q} of {len(checked_rows)} quantities); "
                + (f"{len(open_items)} open pending a source check." if open_items else f"no open items; {len(errata)} printed book cell recorded as an erratum."),
            ],
            "objectives": [
                "L0 parse and trace: book source to tuples to source snippets",
                "L1 validated model: reproduce the Ch15 worked examples within the book's printed precision (current)",
                "L2 digital shadow: QPS Line-S triage scenarios from design data and evidence registers",
                "L3 twin: live PLC/historian feed (later)",
            ],
        },
        {
            "title": "Who governs helium-4 physics",
            "section": "AUTHORITY",
            "governance": [
                {"gate": f"0 < T <= {consts['qplant_hepak_band_K'][1]:g} K", "rule": "HEPAK governs, including He-II below the lambda point"},
                {"gate": f"T > {consts['qplant_hepak_band_K'][1]:g} K", "rule": "CoolProp (Ortiz-Vega EOS) governs, including supercritical"},
                {"gate": f"T < {consts['lambda_point_K']:g} K", "rule": "CoolProp out of range in any role (COOLPROP_OUT_OF_RANGE)"},
                {"gate": "NIST", "rule": "validation reference only, never governing"},
            ],
            "body": [
                f"CODEX and pinned ABACUS routing: {parity['status']} at every probe ({', '.join(f'{p:g}' for p in parity['probes_K'])} K).",
                f"Pin covers {len(pin['pinned_files'])} ABACUS files by git blob and sha256; meta checksum {pin['meta_checksum_sha256'][:12]}…",
            ],
        },
        {
            "title": "L1 validation: Ch15 worked examples",
            "section": "VALIDATION",
            "checklist": l1_checklist,
            "notes": [
                (
                    f"Tolerances: {gate['tolerances']['temperature_abs_K']:g} K, {gate['tolerances']['enthalpy_abs_J_g']:g} J/g, "
                    f"{gate['tolerances']['entropy_abs_J_gK']:g} J/g·K, {gate['tolerances']['density_rel'] * 100:g} % density, "
                    f"{gate['tolerances']['derived_rel'] * 100:g} % derived."
                ),
                f"{len(gate['excluded'])} examples excluded with a stated reason (duplicate, nitrogen, HEPAK-governed two-phase); never counted as passing.",
                f"Recorded from CI run {record['provenance']['recorded_from']['run_id']}; CI fails if the record drifts.",
            ],
        },
        {
            "title": "Source check: T05 cryogenic compressor",
            "section": "VALIDATION",
            "body": [open_items[eid] for eid in open_items] + [
                f"Book erratum, cell {e['cell']}: printed {e['printed']:g}. {e['finding']}" for e in errata.values()
            ] or ["No open items."],
            "changes": ["Open: verify Fig. 15.31 (p. 638) against the printed book."] if open_items else [
                "Resolved: transcription checked against the printed book; the erratum cell is recorded, never compared."
            ],
        },
        {
            "title": "Independent reference: NIST TN 1334",
            "section": "VALIDATION",
            "body": [
                "Governing provider checked against NIST TN 1334 (Arp & McCarty) rows; enthalpy compared as differences (different reference states).",
                f"Tolerance {nist['tolerances']['density_rel'] * 100:g} % on density and Δh; all rows at T ≤ 4.5 K, so the check is advisory.",
                "First CI comparison: all rows within tolerance (CODEX #1007).",
            ],
            "checklist": [
                {"id": f"Row {s['id']}", "state": f"{s['T_K']:g} K / {s['p_Pa'] / 1000:g} kPa"}
                for s in nist["states"]
            ],
        },
        {
            "title": "Cross-check incarnation: ideal-gas helium",
            "section": "CROSS-CHECK",
            "body": [
                "A deliberately simple ideal-gas model runs beside the governing provider; disagreement is a signal, never averaged away.",
                f"Measured validity domain: T ≥ {b.DOMAIN_T_MIN_K:g} K and ideal-gas density ≤ {b.DOMAIN_RHO_MAX_KG_M3:g} kg/m³.",
                f"Physics outputs of the governing provider hashed in CI: {xc['output_checksum_sha256'][:12]}… over {len(xc['grid_T_K']) * len(xc['grid_p_kPa'])} grid points.",
            ],
        },
        {
            "title": "Engineering toolbox and portal",
            "section": "TOOLS",
            "body": [
                "Six calculators in the browser: state point, compressor, JT valve, expander, heat exchanger, equivalent power.",
                "Plotly views: T–s diagram with isobars, heat-exchanger end temperatures, power breakdown, validity-domain map.",
                "Browser maths is a mirror of the Python engine; a CI test requires identical results.",
            ],
            "artifacts": [
                f"{PORTAL}toolbox.html",
                f"{PORTAL}l1_validation.html",
                f"{PORTAL}physics_authority.html",
                f"{PORTAL}",
            ],
        },
        {
            "title": "CI gates behind every number",
            "section": "GOVERNANCE",
            "governance": [
                {"gate": "Pin verification", "rule": "ABACUS checkout must match the pinned commit, git blobs and sha256"},
                {"gate": "Physics output checksum", "rule": "provider outputs over the grid must equal the recorded checksum"},
                {"gate": "Basic incarnation", "rule": "within tolerance everywhere inside its measured domain"},
                {"gate": "NIST TN 1334", "rule": "governing provider within tolerance of the reference rows"},
                {"gate": "L1 worked examples", "rule": "checked examples pass; committed record equals the fresh run"},
            ],
        },
        {
            "title": "Next steps",
            "section": "PLAN",
            "checklist": [
                {"id": "T05", "next": "Fig. 15.31 checked against the printed book; L1 re-recorded with T05 checked", "state": "open" if open_items else "done"},
                {"id": "Ch.3", "next": "Add the GISTAU Chapter 3 source and build the book navigator", "state": "open"},
                {"id": "HEPAK", "next": "Bind HEPAK receipts to validate the two-phase examples (T ≤ 4.5 K)", "state": "open"},
                {"id": "L2", "next": "QPS Line-S triage scenarios on the validated provider", "state": "planned"},
            ],
        },
    ]
    return {
        "metadata": {
            "deck_id": "gistau-ch15-validated-model",
            "version": "0.7.0",
            "status": "Review",
            "project": "GISTAU Chapter 15 — Validated Thermodynamic Model",
            "owner": "CODEX GISTAU workstream (generated from committed sources)",
        },
        "slides": slides,
    }


def render() -> str:
    header = "# Generated by tools/build_gistau_deck_content.py from committed sources. Do not edit by hand.\n"
    return header + yaml.safe_dump(build(), sort_keys=False, allow_unicode=True, width=200)


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
