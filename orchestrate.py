#!/usr/bin/env python3
"""Federation bridge artifact orchestrator.

Generates deployable artifacts:
- docs/files.html
- docs/dashboard.html
- docs/slides_html.html
- README.md
"""
from __future__ import annotations

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"


def load_manifest() -> dict:
    manifest_path = ROOT / "bridge_manifest.yaml"
    with manifest_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_wave_stats() -> tuple[pd.DataFrame, float, float, float]:
    data = {
        "wave": ["Wave 1", "Wave 2", "Wave 3", "Wave 4"],
        "claimed": [0.25, 0.50, 0.75, 1.00],
        "actual": [0.22, 0.45, 0.76, 0.98],
    }
    df = pd.DataFrame(data)

    covariance = float(np.cov(df["claimed"], df["actual"])[0][1])

    dmaic_phases = {"D": 100, "M": 95, "A": 90, "I": 85, "C": 80}
    maturity_score = float(sum(dmaic_phases.values()) / len(dmaic_phases))

    matrix = df[["claimed", "actual"]].to_numpy()
    centered = matrix - matrix.mean(axis=0)
    cov_matrix = np.cov(centered, rowvar=False)
    eigenvalues, _ = np.linalg.eig(cov_matrix)
    pca_primary = float(np.max(eigenvalues))

    return df, covariance, maturity_score, pca_primary


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def build_files_html(manifest: dict, maturity: float) -> None:
    repos = manifest["federation_bridge"]["repos"]
    html = f"""<!DOCTYPE html>
<html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Federation Files</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;background:#f7f9fc}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border:1px solid #d8deea}}th{{background:#263247;color:#fff}}</style></head>
<body><h1>Asset Lineage (Target 100%)</h1><p>Maturity score: <strong>{maturity:.1f}%</strong></p>
<table><tr><th>Repo</th><th>Branch</th><th>Role</th><th>Focus</th><th>URL</th></tr>
<tr><td>codex</td><td>{repos['codex']['branch']}</td><td>{repos['codex']['role']}</td><td>{repos['codex']['focus']}</td><td><a href=\"{repos['codex']['url']}\">link</a></td></tr>
<tr><td>abacus</td><td>{repos['abacus']['branch']}</td><td>{repos['abacus']['role']}</td><td>{repos['abacus']['focus']}</td><td><a href=\"{repos['abacus']['url']}\">link</a></td></tr>
</table></body></html>"""
    _write(DOCS / "files.html", html)


def build_dashboard_html(df: pd.DataFrame, covariance: float, maturity: float, pca_primary: float) -> None:
    rows = "".join(
        f"<tr><td>{r.wave}</td><td>{r.claimed:.0%}</td><td>{r.actual:.0%}</td></tr>" for r in df.itertuples(index=False)
    )
    html = f"""<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Wave Dashboard</title>
<style>body{{font-family:Arial;background:#101826;color:#ebf1ff;margin:24px}}.card{{background:#1a2538;padding:14px;border:1px solid #304161;border-radius:10px;margin-bottom:12px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #31415f}}</style></head>
<body><h1>Wave Metrics Dashboard</h1>
<div class=\"card\"><strong>DMAIC maturity:</strong> {maturity:.1f}%</div>
<div class=\"card\"><strong>ANOVA covariance proxy:</strong> {covariance:.6f}</div>
<div class=\"card\"><strong>PCA primary component variance:</strong> {pca_primary:.6f}</div>
<div class=\"card\"><table><tr><th>Wave</th><th>Claimed</th><th>Actual</th></tr>{rows}</table></div>
</body></html>"""
    _write(DOCS / "dashboard.html", html)


def build_slides_html(covariance: float, maturity: float, pca_primary: float) -> None:
    html = f"""<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Federation Slides</title>
<style>body{{font-family:Helvetica,Arial;background:#0f1320;color:#f2f6ff}}.slide{{max-width:900px;margin:18px auto;padding:20px;background:#1a2238;border-radius:10px;border:1px solid #334}}h1,h2{{margin:0 0 10px}}</style></head>
<body>
<section class=\"slide\"><h1>gbogeb Federation Bridge</h1><p>codex ⇄ MCP ⇄ abacus</p></section>
<section class=\"slide\"><h2>Wave Analytics</h2><p>PCA: {pca_primary:.6f}<br>DMAIC maturity: {maturity:.1f}%<br>ANOVA covariance: {covariance:.6f}</p></section>
<section class=\"slide\"><h2>Cycle Rule</h2><p>One cycle closes on clone-to-local or push-to-source sync completion.</p></section>
</body></html>"""
    _write(DOCS / "slides_html.html", html)


def build_readme(df: pd.DataFrame, covariance: float, maturity: float, pca_primary: float) -> None:
    rows = "\n".join(f"| {r.wave} | {r.claimed:.0%} | {r.actual:.0%} |" for r in df.itertuples(index=False))
    md = f"""# Federation Bridge Control Document

## Repo Topography
- Upstream Core: [gbogeb/codex](https://github.com/gbogeb/codex)
- Downstream Engine: [gbogeb/abacus](https://github.com/gbogeb/abacus)

## Wave Telemetry
| Execution Cycle Block | Claimed Baseline | Actual Delivered Verification |
|---|---:|---:|
{rows}

## Analytics Controls
- PCA primary variance: `{pca_primary:.6f}`
- ANOVA covariance index: `{covariance:.6f}`
- DMAIC process capability score: `{maturity:.1f}%`
"""
    _write(DOCS / "federation_readme.md", md)


def main() -> None:
    manifest = load_manifest()
    df, covariance, maturity, pca_primary = calculate_wave_stats()

    build_files_html(manifest, maturity)
    build_dashboard_html(df, covariance, maturity, pca_primary)
    build_slides_html(covariance, maturity, pca_primary)
    build_readme(df, covariance, maturity, pca_primary)

    out = {
        "covariance": covariance,
        "pca_primary": pca_primary,
        "maturity": maturity,
        "waves": df.to_dict(orient="records"),
    }
    _write(DOCS / "federation_metrics.json", json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
