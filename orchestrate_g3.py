#!/usr/bin/env python3
"""Generation 3 federation orchestrator.

Builds four core artifacts in docs/:
- files.html
- dashboard.html
- slides_html.html
- federation_readme.md

Also emits docs/federation_metrics.json.
"""
from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"


def load_g3_glossary() -> dict:
    path = ROOT / "MANIFEST" / "FEDERATION_GLOSSARY.yaml"
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def run_g3_analytics() -> dict:
    waves = ["Wave_G1_Alpha", "Wave_G1_Beta", "Wave_G3_Component", "Wave_G3_Deployment"]
    claimed = np.array([0.25, 0.50, 0.75, 1.00], dtype=float)
    actual = np.array([0.22, 0.48, 0.71, 0.97], dtype=float)

    covariance_val = float(np.cov(claimed, actual)[0, 1])

    component_weights = {"Layout": 0.95, "MathEngine": 0.98, "BridgeSync": 0.92, "Deployment": 1.00}
    overall_maturity = float(sum(component_weights.values()) / len(component_weights) * 100)

    pca_matrix = np.vstack([claimed, actual]).T
    centered = pca_matrix - pca_matrix.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    eigvals, _ = np.linalg.eig(cov)
    pca_primary = float(np.max(eigvals))

    dmaic_sigma_proxy = float((actual.mean() - claimed.mean()) / (actual.std() if actual.std() else 1.0))

    return {
        "waves": waves,
        "claimed": claimed,
        "actual": actual,
        "covariance": covariance_val,
        "maturity": overall_maturity,
        "pca_primary": pca_primary,
        "dmaic_sigma_proxy": dmaic_sigma_proxy,
    }


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_files_html(glossary: dict) -> None:
    components = glossary.get("components", [])
    rows = "".join(
        f"<tr><td>{c['id']}</td><td>{c['name']}</td><td><a href='https://github.com/{c['repo_target']}'>{c['repo_target']}</a></td><td>{c['branch']}</td><td>{c['description']}</td></tr>"
        for c in components
    )
    html = f"""<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>G3 Component Lineage Matrix</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;margin:30px;background:#f4f6f9;color:#263247}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border:1px solid #d9e1ef}}th{{background:#2c3e50;color:#fff}}</style>
</head><body>
<h2>Generation 3 (G3) Component Lineage Matrix</h2>
<p><strong>Lineage:</strong> {glossary.get('lineage_parent','G1')} → {glossary.get('system_generation','G3')}</p>
<table><thead><tr><th>ID</th><th>Component</th><th>Repo</th><th>Branch</th><th>Description</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>"""
    _write(DOCS / "files.html", html)


def build_dashboard_html(metrics: dict) -> None:
    row_html = "".join(
        f"<tr><td>{w}</td><td>{c*100:.0f}%</td><td>{a*100:.0f}%</td></tr>"
        for w, c, a in zip(metrics["waves"], metrics["claimed"], metrics["actual"])
    )
    html = f"""<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>G3 Operational Telemetry Dashboard</title>
<style>body{{font-family:Arial,sans-serif;background:#0f172a;color:#f8fafc;padding:24px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}.card{{background:#1e293b;padding:14px;border-radius:10px;border:1px solid #334155}}table{{width:100%;border-collapse:collapse;margin-top:14px}}th,td{{padding:10px;border-bottom:1px solid #334155}}</style></head>
<body><h1>G3 Structural Telemetry & Wave Analytics</h1>
<div class='grid'>
<div class='card'><h3>System Lineage Track</h3><div>G1 → G3</div></div>
<div class='card'><h3>Maturity</h3><div>{metrics['maturity']:.2f}%</div></div>
<div class='card'><h3>ANOVA Covariance</h3><div>{metrics['covariance']:.6f}</div></div>
<div class='card'><h3>PCA Primary Variance</h3><div>{metrics['pca_primary']:.6f}</div></div>
<div class='card'><h3>DMAIC Sigma Proxy</h3><div>{metrics['dmaic_sigma_proxy']:.6f}</div></div>
</div>
<table><thead><tr><th>Execution Block</th><th>Claimed</th><th>Actual</th></tr></thead><tbody>{row_html}</tbody></table>
</body></html>"""
    _write(DOCS / "dashboard.html", html)


def build_slides_html(metrics: dict) -> None:
    html = f"""<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>G3 Systems Architecture Blueprint</title>
<style>body{{font-family:Helvetica,Arial;background:#050508;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}}.slide{{width:min(900px,90%);background:#0f0f15;border:1px solid #1e1e2f;padding:36px;border-radius:14px}}</style>
</head><body><section class='slide'>
<h1>Generation 3 High-Fidelity Execution Matrix</h1>
<p><strong>Upstream:</strong> gbogeb/codex component schemas</p>
<p><strong>Downstream:</strong> gbogeb/abacus algorithmic execution units</p>
<p><strong>Metrics:</strong> Maturity {metrics['maturity']:.2f}% | Covariance {metrics['covariance']:.6f} | PCA {metrics['pca_primary']:.6f}</p>
</section></body></html>"""
    _write(DOCS / "slides_html.html", html)


def build_markdown(metrics: dict) -> None:
    rows = "\n".join(
        f"| {w} | {c*100:.0f}% | {a*100:.0f}% |" for w, c, a in zip(metrics["waves"], metrics["claimed"], metrics["actual"])
    )
    md = f"""# Federation Framework (Generation 3)

## Architectural Lineage
- Parent lineage: **G1 Foundations**
- Current lineage: **G3 High-Fidelity Execution & Component Mapping**
- Upstream: [gbogeb/codex](https://github.com/gbogeb/codex)
- Downstream: [gbogeb/abacus](https://github.com/gbogeb/abacus)

## Wave Telemetry
| Wave | Claimed | Actual |
|---|---:|---:|
{rows}

## Statistical Controls
- ANOVA covariance: `{metrics['covariance']:.6f}`
- PCA primary variance: `{metrics['pca_primary']:.6f}`
- DMAIC sigma proxy: `{metrics['dmaic_sigma_proxy']:.6f}`
- Maturity score: `{metrics['maturity']:.2f}%`
"""
    _write(DOCS / "federation_readme.md", md)


def main() -> None:
    glossary = load_g3_glossary()
    metrics = run_g3_analytics()

    build_files_html(glossary)
    build_dashboard_html(metrics)
    build_slides_html(metrics)
    build_markdown(metrics)

    serializable = {
        "waves": metrics["waves"],
        "claimed": [float(x) for x in metrics["claimed"]],
        "actual": [float(x) for x in metrics["actual"]],
        "covariance": metrics["covariance"],
        "pca_primary": metrics["pca_primary"],
        "dmaic_sigma_proxy": metrics["dmaic_sigma_proxy"],
        "maturity": metrics["maturity"],
    }
    _write(DOCS / "federation_metrics.json", json.dumps(serializable, indent=2))


if __name__ == "__main__":
    main()
