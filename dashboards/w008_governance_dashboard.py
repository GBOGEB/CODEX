"""W008 Federation Runtime Visualization and Governance Dashboard.

Reads federation artifacts and generates docs/w008-governance-dashboard.html.
"""

import html
import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _esc(value) -> str:
    return html.escape(str(value))


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _score_color(value: float) -> str:
    if value >= 0.80:
        return "var(--ok)"
    if value >= 0.70:
        return "var(--warn)"
    return "var(--crit)"


def _bool_badge(value: bool) -> str:
    if value:
        return '<span class="badge ok">✓ YES</span>'
    return '<span class="badge crit">✗ NO</span>'


def _federation_status(geti: float, pci: float) -> tuple[str, str]:
    if geti >= 0.80 and pci >= 0.80:
        return "HEALTHY", "var(--ok)"
    if geti >= 0.70 and pci >= 0.70:
        return "DEGRADED", "var(--warn)"
    return "CRITICAL", "var(--crit)"


def _evidence_count(member: dict) -> int:
    return sum([
        bool(member.get("runtime_exists")),
        bool(member.get("runtime_validated")),
        bool(member.get("deployment_exists")),
    ])


def _runtime_state(member: dict) -> str:
    if member.get("deployment_exists") and member.get("runtime_validated"):
        return "VALIDATED_DEPLOYED"
    if member.get("runtime_validated"):
        return "EXECUTED_VALIDATED"
    if member.get("runtime_exists"):
        return "EXECUTED_ONLY"
    return "REPO_ONLY"


def _state_color(state: str) -> str:
    return {
        "VALIDATED_DEPLOYED": "var(--ok)",
        "EXECUTED_VALIDATED": "var(--info)",
        "EXECUTED_ONLY": "var(--warn)",
        "REPO_ONLY": "var(--crit)",
    }.get(state, "var(--muted)")


def _build_d1(rollup: dict) -> str:
    agg = rollup.get("aggregated", rollup)
    geti = float(agg["geti"])
    pci = float(agg["pci"])
    ef = float(agg["expansion_factor"])
    status, status_color = _federation_status(geti, pci)
    members = rollup.get("members", [])
    wave = _esc(rollup.get("wave", "—"))
    subwave = _esc(rollup.get("subwave", "—"))

    rows = ""
    for summary in rollup.get("repo_summaries", []):
        m = _esc(summary["member"])
        g = float(summary["geti"])
        p = float(summary["pci"])
        e = float(summary["expansion_factor"])
        rows += (
            f"<tr>"
            f"<td>{m}</td>"
            f"<td style='color:{_score_color(g)}'>{_esc(f'{g:.4f}')}</td>"
            f"<td style='color:{_score_color(p)}'>{_esc(f'{p:.4f}')}</td>"
            f"<td>{_esc(f'{e:.4f}')}</td>"
            f"</tr>\n"
        )

    return f"""
  <section class="panel">
    <h2>D1 — Federation Health</h2>
    <p class="muted">Wave <strong>{wave}</strong> · Subwave <strong>{subwave}</strong> · Members: {_esc(', '.join(members))}</p>
    <div class="kpi-row">
      <div class="kpi">
        <div class="kpi-label">GETI</div>
        <div class="kpi-value" style="color:{_score_color(geti)}">{_esc(f'{geti:.4f}')}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">PCI</div>
        <div class="kpi-value" style="color:{_score_color(pci)}">{_esc(f'{pci:.4f}')}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Expansion Factor</div>
        <div class="kpi-value">{_esc(f'{ef:.4f}')}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Federation Status</div>
        <div class="kpi-value" style="color:{status_color}">{_esc(status)}</div>
      </div>
    </div>
    <table>
      <thead><tr><th>Member</th><th>GETI</th><th>PCI</th><th>Expansion Factor</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </section>"""


def _build_d2(registry: dict) -> str:
    rows = ""
    for member in registry.get("runtime_registry", []):
        repo = _esc(member.get("repo", "—"))
        state = _runtime_state(member)
        state_col = _state_color(state)
        evidence = _evidence_count(member)
        truth = float(member.get("truth_score", 0.0))
        coverage = _pct(truth)
        rows += (
            f"<tr>"
            f"<td>{repo}</td>"
            f"<td style='color:{state_col}'>{_esc(state)}</td>"
            f"<td style='text-align:center'>{_esc(str(evidence))}/3</td>"
            f"<td style='color:{_score_color(truth)}'>{_esc(coverage)}</td>"
            f"</tr>\n"
        )

    wave = _esc(registry.get("wave", "—"))
    subwave = _esc(registry.get("subwave", "—"))

    return f"""
  <section class="panel">
    <h2>D2 — Runtime Registry</h2>
    <p class="muted">Wave <strong>{wave}</strong> · Subwave <strong>{subwave}</strong></p>
    <table>
      <thead>
        <tr>
          <th>Repository</th>
          <th>Runtime State</th>
          <th>Evidence Count</th>
          <th>Coverage %</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </section>"""


def _build_d3(bottleneck: dict) -> str:
    dom_repo = _esc(bottleneck.get("dominant_repo", "—"))
    dom_wave = _esc(bottleneck.get("dominant_wave", "—"))
    dom_bn = _esc(bottleneck.get("dominant_bottleneck", "—").upper())
    rec_action = _esc(bottleneck.get("recommended_next_action", "—"))
    count = _esc(str(bottleneck.get("bottleneck_count", 0)))
    ts = _esc(bottleneck.get("timestamp", "—"))

    bn_rows = ""
    for bn in bottleneck.get("bottlenecks", []):
        m = _esc(bn.get("member", "—"))
        w = float(bn.get("weight", 0.0))
        flags = _esc(", ".join(bn.get("flags", [])).upper())
        bn_rows += (
            f"<tr>"
            f"<td>{m}</td>"
            f"<td>{flags}</td>"
            f"<td style='color:{_score_color(w)}'>{_esc(f'{w:.2f}')}</td>"
            f"</tr>\n"
        )

    return f"""
  <section class="panel">
    <h2>D3 — Bottleneck Analysis</h2>
    <p class="muted">Timestamp: {ts} · Bottleneck count: {count}</p>
    <div class="kpi-row">
      <div class="kpi">
        <div class="kpi-label">Dominant Repo</div>
        <div class="kpi-value" style="color:var(--warn)">{dom_repo}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Dominant Wave</div>
        <div class="kpi-value">{dom_wave}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Dominant Bottleneck</div>
        <div class="kpi-value" style="color:var(--crit)">{dom_bn}</div>
      </div>
    </div>
    <p class="notice"><strong>Recommended Action:</strong> {rec_action}</p>
    <table>
      <thead><tr><th>Member</th><th>Flags</th><th>Weight</th></tr></thead>
      <tbody>{bn_rows}</tbody>
    </table>
  </section>"""


def _build_d4(report: dict) -> str:
    truth_matrix = report.get("truth_matrix", {})
    rows_data = truth_matrix.get("rows", [])

    target_members = {"ABACUS", "CODEX", "ARTSTYLE"}

    rows = ""
    for row in rows_data:
        member = row.get("member", "—")
        truth_state = _esc(row.get("truth_state", "—"))
        truth_score = float(row.get("truth_score", 0.0))

        # lineage: has runtime_exists
        lineage = _bool_badge(bool(row.get("runtime_exists")))
        # federation: has runtime_validated
        federation = _bool_badge(bool(row.get("runtime_validated")))
        # renderability: has deployment_exists
        renderability = _bool_badge(bool(row.get("deployment_exists")))
        # drift: truth_score below threshold indicates drift risk
        drift_risk = truth_score < 0.80
        drift = (
            '<span class="badge warn">⚠ DRIFT RISK</span>'
            if drift_risk
            else '<span class="badge ok">✓ STABLE</span>'
        )

        # highlight target members
        style = " style='font-weight:bold'" if member in target_members else ""
        rows += (
            f"<tr{style}>"
            f"<td>{_esc(member)}</td>"
            f"<td style='color:{_score_color(truth_score)}'>"
            f"{_esc(f'{truth_score:.2f}')}</td>"
            f"<td style='color:{_state_color(truth_state)}'>{truth_state}</td>"
            f"<td>{lineage}</td>"
            f"<td>{federation}</td>"
            f"<td>{renderability}</td>"
            f"<td>{drift}</td>"
            f"</tr>\n"
        )

    wave = _esc(report.get("wave", "—"))
    subwave = _esc(report.get("subwave", "—"))

    return f"""
  <section class="panel">
    <h2>D4 — Governance Rollup</h2>
    <p class="muted">Wave <strong>{wave}</strong> · Subwave <strong>{subwave}</strong>
      · Tracking: lineage, federation, renderability, drift</p>
    <table>
      <thead>
        <tr>
          <th>Member</th>
          <th>Truth Score</th>
          <th>Truth State</th>
          <th>Lineage</th>
          <th>Federation</th>
          <th>Renderability</th>
          <th>Drift</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </section>"""


def main() -> None:
    repo_root = Path(__file__).parent.parent

    rollup = _load_json(repo_root / "metrics" / "federation" / "federation_rollup.json")
    _ = _load_json(repo_root / "metrics" / "federation" / "federation_scree.json")
    registry = _load_json(
        repo_root / "federation" / "runtime_registry" / "runtime_registry.json"
    )
    bottleneck = _load_json(repo_root / "bottleneck_report.json")
    report = _load_json(
        repo_root / "federation" / "runtime_registry" / "runtime_registry_report.json"
    )

    d1 = _build_d1(rollup)
    d2 = _build_d2(registry)
    d3 = _build_d3(bottleneck)
    d4 = _build_d4(report)

    generated_ts = report.get("subwave", "W007.2A")

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>W008 Federation Governance Dashboard</title>
  <style>
    :root {{
      --bg:#0b1220; --panel:#121b2f; --card:#1a2540; --line:#33446f;
      --txt:#edf2ff; --muted:#9cb0df; --ok:#50d890; --warn:#ffcb6b;
      --info:#8ad3ff; --crit:#f87171;
    }}
    body {{ margin:0; font-family:Inter,Arial,sans-serif; background:var(--bg); color:var(--txt); }}
    main {{ max-width:1200px; margin:0 auto; padding:20px; }}
    h1,h2,h3 {{ margin:0 0 10px; }}
    .muted {{ color:var(--muted); font-size:.9rem; }}
    .panel {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
              padding:18px; margin-bottom:18px; }}
    .kpi-row {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
                gap:12px; margin:14px 0; }}
    .kpi {{ background:var(--panel); border:1px solid var(--line); border-radius:8px;
            padding:12px; text-align:center; }}
    .kpi-label {{ color:var(--muted); font-size:.8rem; text-transform:uppercase;
                  letter-spacing:.05em; margin-bottom:6px; }}
    .kpi-value {{ font-size:1.5rem; font-weight:700; }}
    table {{ width:100%; border-collapse:collapse; margin-top:10px; font-size:.9rem; }}
    th,td {{ border-bottom:1px solid var(--line); padding:8px 10px; text-align:left; }}
    th {{ color:var(--muted); font-weight:600; font-size:.8rem; text-transform:uppercase; }}
    .badge {{ display:inline-block; border-radius:999px; padding:2px 8px;
              font-size:.8rem; font-weight:600; border:1px solid var(--line); }}
    .badge.ok {{ color:#0b1220; background:var(--ok); border-color:var(--ok); }}
    .badge.warn {{ color:#0b1220; background:var(--warn); border-color:var(--warn); }}
    .badge.crit {{ color:#0b1220; background:var(--crit); border-color:var(--crit); }}
    .notice {{ background:var(--panel); border-left:3px solid var(--warn);
               padding:10px 14px; border-radius:4px; margin:12px 0; font-size:.9rem; }}
    a {{ color:var(--info); }}
    .back {{ display:block; margin-bottom:16px; }}
    header {{ border-bottom:1px solid var(--line); padding-bottom:14px; margin-bottom:18px; }}
  </style>
</head>
<body>
<main>
  <a class="back" href="index.html">← Back to index</a>
  <header>
    <h1>W008 — Federation Runtime Visualization &amp; Governance Dashboard</h1>
    <p class="muted">
      Subwave: <strong>{_esc(generated_ts)}</strong> ·
      Artifact consumption layer for federation governance visibility.
    </p>
  </header>
{d1}
{d2}
{d3}
{d4}
</main>
</body>
</html>
"""

    out_path = repo_root / "docs" / "w008-governance-dashboard.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()
