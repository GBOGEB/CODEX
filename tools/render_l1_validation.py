"""Render the Ch15 L1 validation results page for the GISTAU portal.

Input:  governance/physics/CH15_CANONICAL_VALIDATION.yaml (coverage, tolerances)
        docs/gistau-ch15/data/l1_validation_results.json (committed CI record)
        docs/gistau-ch15/data/worked_examples.json (figure / page references)
Output: docs/gistau-ch15/l1_validation.html

Pure function of its inputs (no timestamps); a test fails if the committed page
is stale. Regenerate with:  python tools/render_l1_validation.py
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE = REPO_ROOT / "governance" / "physics" / "CH15_CANONICAL_VALIDATION.yaml"
RECORD = REPO_ROOT / "docs" / "gistau-ch15" / "data" / "l1_validation_results.json"
OUTPUT = REPO_ROOT / "docs" / "gistau-ch15" / "l1_validation.html"

QUANTITY_LABELS = {
    "enthalpy_j_g": ("Enthalpy", "J/g"),
    "entropy_j_gk": ("Entropy", "J/g·K"),
    "density_kg_m3": ("Density", "kg/m³"),
    "outlet_temperature_k": ("Outlet temperature", "K"),
    "inlet_enthalpy_j_g": ("Inlet enthalpy", "J/g"),
    "outlet_enthalpy_j_g": ("Outlet enthalpy", "J/g"),
    "mass_flow_g_s": ("Mass flow", "g/s"),
    "power_w_visible": ("Power", "W"),
    "power_w": ("Power", "W"),
    "isentropic_enthalpy_change_j_g": ("Isentropic enthalpy rise", "J/g"),
    "real_enthalpy_change_j_g": ("Real enthalpy rise", "J/g"),
    "inversion_temperature_k": ("Inversion temperature", "K"),
    "hot_outlet_temperature_k": ("Hot outlet temperature", "K"),
    "heat_load_w": ("Heat load", "W"),
    "lmtd_k": ("LMTD", "K"),
    "ua_w_k": ("UA", "W/K"),
}
TUPLE_LABELS = {
    "T00": "State point",
    "T01": "Room-temperature compressor",
    "T02": "JT valve / free expansion",
    "T03": "Heat exchanger",
    "T04": "Cryogenic expander",
    "T05": "Cryogenic compressor",
    "T06": "Equivalent power",
}


def _e(x: Any) -> str:
    return html.escape(str(x), quote=True)


def _fmt(x: float) -> str:
    return f"{x:.6g}"


def _dev(r: dict[str, Any]) -> str:
    if r["deviation_kind"] == "rel":
        return f"{r['deviation'] * 100:+.3f} %"
    return f"{r['deviation']:+.4g}"


def _tol(r: dict[str, Any]) -> str:
    return f"±{r['tolerance'] * 100:g} %" if r["deviation_kind"] == "rel" else f"±{r['tolerance']:g}"


def _load() -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    gate = yaml.safe_load(GATE.read_text(encoding="utf-8"))
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    data = json.loads((REPO_ROOT / gate["source"]).read_text(encoding="utf-8"))
    examples = data if isinstance(data, list) else data["examples"]
    return gate, record, {e["example_id"]: e for e in examples}


def render() -> str:
    gate, record, examples = _load()
    rec = record.get("record")
    pending = rec in (None, "PENDING_FIRST_CI_RECORD")
    rows = [] if pending else rec["rows"]
    open_items = gate.get("source_check_required", {}) or {}
    errata = gate.get("book_errata", {}) or {}

    def status_of(eid: str) -> tuple[str, str]:
        if eid in gate["checked"]:
            ex_rows = [r for r in rows if r["example_id"] == eid]
            if pending or not ex_rows:
                return "pending", "Awaiting CI record"
            ok = all(r["verdict"] == "PASS" for r in ex_rows)
            return ("pass", "Pass") if ok else ("fail", "Fail")
        if eid in open_items:
            return "open", "Open — source check"
        return "excluded", "Excluded"

    order = list(gate["checked"]) + list(open_items) + list(gate["excluded"])
    n_pass = sum(1 for eid in gate["checked"] if status_of(eid)[0] == "pass")
    n_q = sum(1 for r in rows if r["example_id"] in gate["checked"])
    n_q_pass = sum(1 for r in rows if r["example_id"] in gate["checked"] and r["verdict"] == "PASS")

    cards = []
    for eid in order:
        ex = examples[eid]
        cls, label = status_of(eid)
        tup = eid.split("-")[1]
        ref = f"Fig. {ex.get('figure', '').replace('Fig. ', '')}, p. {ex.get('page', '—')}" if ex.get("figure") else ""
        head = (
            f'<div class="ex-head"><span class="badge {cls}">{_e(label)}</span>'
            f'<h3>{_e(TUPLE_LABELS.get(tup, tup))}</h3>'
            f'<span class="ref">{_e(tup)} · {_e(ref)}</span></div>'
        )
        body = f'<p class="desc">{_e(ex.get("description", ""))}</p>'
        ex_rows = [r for r in rows if r["example_id"] == eid]
        if ex_rows:
            trs = "".join(
                "<tr>"
                f"<td>{_e(QUANTITY_LABELS.get(r['quantity'], (r['quantity'], ''))[0])}</td>"
                f"<td class='num'>{_fmt(r['expected'])}</td>"
                f"<td class='num'>{_fmt(r['computed'])}</td>"
                f"<td class='num'>{_e(_dev(r))}</td>"
                f"<td class='num'>{_e(_tol(r))}</td>"
                f"<td>{_e(QUANTITY_LABELS.get(r['quantity'], ('', ''))[1])}</td>"
                f"<td><span class='mark {('ok' if r['verdict'] in ('PASS', 'OPEN_MATCH') else 'bad')}'>{_e(r['verdict'].replace('_', ' ').lower())}</span></td>"
                "</tr>"
                for r in ex_rows
            )
            body += (
                '<div class="wrap"><table><thead><tr><th>Quantity</th><th>Book</th><th>Provider</th>'
                "<th>Deviation</th><th>Tolerance</th><th>Unit</th><th>Result</th></tr></thead>"
                f"<tbody>{trs}</tbody></table></div>"
            )
        if eid in open_items:
            body += f'<p class="why open-why"><strong>Why open:</strong> {_e(open_items[eid])}</p>'
        if eid in errata:
            e = errata[eid]
            body += (f'<p class="why"><strong>Book erratum, cell {_e(e["cell"])}</strong> '
                     f'(printed {_e(_fmt(e["printed"]))}, not compared): {_e(e["finding"])}</p>')
        if eid in gate["excluded"]:
            body += f'<p class="why"><strong>Why excluded:</strong> {_e(gate["excluded"][eid])}</p>'
        cards.append(f'<article class="ex {cls}" id="{_e(eid)}">{head}{body}</article>')

    prov = record.get("provenance", {})
    cp = "—" if pending else rec.get("coolprop_version", "—")
    summary = (
        "The CI record has not been committed yet."
        if pending
        else f"{n_pass} of {len(gate['checked'])} checked examples reproduce the book within its printed precision "
        f"({n_q_pass} of {n_q} quantities). "
        + (f"{len(open_items)} example is open pending a source check; " if open_items else "No example is open; ")
        + f"{len(gate['excluded'])} are excluded with a stated reason."
    )
    tol = gate["tolerances"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Ch15 L1 Validation</title>
<style>
/* Layout: portal header, summary strip, one card per worked example (status badge, book-vs-provider table, reason). */
:root {{
  --bg: #ffffff; --panel: #ffffff; --fg: #111111; --muted: #5a5a5a; --line: #111111; --soft: #d9d9d9;
  --ok: #007a33; --bad: #b00020; --open: #8a5a00; --open-bg: #fff4e5; --ex: #5a5a5a;
  --font: Arial, "Helvetica Neue", Helvetica, sans-serif; --mono: Consolas, "Liberation Mono", monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #181421; --panel: #241d33; --fg: #f5f2ff; --muted: #cfc2ef; --line: #8f7abd; --soft: #3a3150;
  --ok: #9cf2be; --bad: #ffb3b3; --open: #ffd27a; --open-bg: #3b2a00; --ex: #cfc2ef; color-scheme: dark;
}} }}
:root[data-theme="dark"] {{
  --bg: #181421; --panel: #241d33; --fg: #f5f2ff; --muted: #cfc2ef; --line: #8f7abd; --soft: #3a3150;
  --ok: #9cf2be; --bad: #ffb3b3; --open: #ffd27a; --open-bg: #3b2a00; --ex: #cfc2ef; color-scheme: dark;
}}
body {{ background: var(--bg); color: var(--fg); font-family: var(--font); margin: 0; line-height: 1.45; }}
.page {{ padding-inline: 16px; padding-block: 0 24px; max-width: 1100px; margin-inline: auto; }}
.topbar {{ padding-block: 16px; border-bottom: 4px solid var(--line); }}
.topbar h1 {{ margin: 0 0 6px; font-size: 1.5rem; text-wrap: balance; }}
.topbar p {{ margin: 0; color: var(--muted); max-width: 70ch; }}
.strip {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
.pill {{ border: 2px solid var(--line); border-radius: 999px; padding: 3px 10px; font-weight: bold; font-size: .82rem; }}
.summary {{ margin: 16px 0; font-size: 1.05rem; max-width: 75ch; }}
.list {{ display: grid; gap: 14px; }}
.ex {{ border: 3px solid var(--line); border-radius: 12px; padding: 14px 16px; background: var(--panel); min-width: 0; }}
.ex.pass {{ border-color: var(--ok); }} .ex.fail {{ border-color: var(--bad); }}
.ex.open {{ border-color: var(--open); background: var(--open-bg); }} .ex.excluded {{ border-color: var(--soft); }}
.ex-head {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 12px; }}
.ex-head h3 {{ margin: 0; font-size: 1.05rem; }}
.ref {{ color: var(--muted); font-size: .85rem; }}
.badge {{ border: 2px solid currentColor; border-radius: 999px; padding: 1px 9px; font-size: .78rem; font-weight: bold; }}
.badge.pass {{ color: var(--ok); }} .badge.fail {{ color: var(--bad); }} .badge.open {{ color: var(--open); }}
.badge.excluded, .badge.pending {{ color: var(--ex); }}
.desc {{ margin: 6px 0 0; color: var(--muted); }}
.why {{ margin: 8px 0 0; max-width: 80ch; }}
.wrap {{ overflow-x: auto; margin-top: 10px; }}
table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; font-size: .88rem; }}
th, td {{ border: 1px solid var(--soft); padding: 5px 8px; text-align: left; white-space: nowrap; }}
th {{ background: var(--fg); color: var(--bg); border-color: var(--fg); }} td.num {{ text-align: right; }}
.mark {{ font-weight: bold; }} .mark.ok {{ color: var(--ok); }} .mark.bad {{ color: var(--bad); }}
.foot {{ margin-top: 20px; color: var(--muted); font-size: .88rem; max-width: 80ch; }}
code {{ font-family: var(--mono); font-size: .9em; }} a {{ color: var(--fg); }}
a:focus-visible {{ outline: 3px solid var(--ok); outline-offset: 2px; }}
</style></head>
<body><div class="page">
<header class="topbar">
<h1>Ch15 L1 validation — worked examples</h1>
<p>Each Chapter 15 worked example, recomputed with the governing helium-4 provider (ABACUS, pinned) and compared with the book's printed values.</p>
<div class="strip">
<span class="pill">Governing provider: ABACUS (pinned) · CoolProp {_e(cp)}</span>
<span class="pill">Tolerances: {tol['temperature_abs_K']:g} K · {tol['enthalpy_abs_J_g']:g} J/g · {tol['entropy_abs_J_gK']:g} J/g·K · {tol['density_rel'] * 100:g} % ρ · {tol['derived_rel'] * 100:g} % derived</span>
</div>
</header>
<p class="summary">{_e(summary)}</p>
<section class="list">{''.join(cards)}</section>
<p class="foot">Coverage and tolerances: <code>governance/physics/CH15_CANONICAL_VALIDATION.yaml</code>. Numbers: <code>docs/gistau-ch15/data/l1_validation_results.json</code>,
{_e(prov.get('note', ''))}. Excluded and open examples are never counted as passing. <a href="index.html">Back to the GISTAU portal</a></p>
</div></body></html>
"""


def main() -> int:
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
