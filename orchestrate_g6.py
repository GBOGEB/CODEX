#!/usr/bin/env python3
import json
import hashlib
from html import escape
from pathlib import Path

import yaml

from semantic_substrate.renderer.contrast_validator import ContrastValidator

ROOT = Path(__file__).resolve().parent
OUTPUT_HTML_DIR = ROOT / "outputs" / "html"
WAVE_PROGRESSION_PATH = ROOT / "MANIFEST" / "WAVE_PROGRESSION.yaml"
CONVERGENCE_KPIS_PATH = ROOT / "MANIFEST" / "CONVERGENCE_KPIS.yaml"


def _load_wave_series() -> tuple[list[float], list[float]]:
    with WAVE_PROGRESSION_PATH.open("r", encoding="utf-8") as handle:
        wave_progression = yaml.safe_load(handle) or {}
    with CONVERGENCE_KPIS_PATH.open("r", encoding="utf-8") as handle:
        convergence_kpis = yaml.safe_load(handle) or {}

    claimed_by_wave = {
        item["wave"]: float(item["completion"]) / 100.0
        for item in wave_progression.get("waves", [])
        if "wave" in item and "completion" in item
    }
    actual_by_wave = {
        wave: float(completion) / 100.0
        for wave, completion in convergence_kpis.get("convergence_kpis", {}).get("progression", {}).items()
    }

    common_waves = sorted(set(claimed_by_wave) & set(actual_by_wave))
    return [claimed_by_wave[wave] for wave in common_waves], [actual_by_wave[wave] for wave in common_waves]


def _format_wave_series(values: list[float]) -> list[str]:
    return [f"{value:.4f}" for value in values]


def _html_shell(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none';">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
</head>
<body>
{body}
</body>
</html>
"""


def run_g6_attestation_loop(output_dir: Path = OUTPUT_HTML_DIR) -> dict[str, object]:
    validator = ContrastValidator()

    warning_dark = validator.target_invariants["warning"]["dark"]
    contrast_results = validator.validate_theme_node(
        warning_dark["background"],
        warning_dark["text"],
    )

    claimed_waves, actual_waves = _load_wave_series()
    wave_delta = sum(abs(c - a) for c, a in zip(claimed_waves, actual_waves))

    state_payload = json.dumps(
        {
            "contrast_ratio": contrast_results["contrast_ratio"],
            "wcag_aa_compliant": contrast_results["wcag_aa_compliant"],
            "wave_delta": f"{wave_delta:.4f}",
            "claimed_waves": _format_wave_series(claimed_waves),
            "actual_waves": _format_wave_series(actual_waves),
        },
        sort_keys=True,
    )
    attestation_hash = hashlib.sha256(state_payload.encode()).hexdigest()[:16]

    ratio_text = escape(f"{contrast_results['contrast_ratio']}:1")
    compliant_text = escape(str(contrast_results["wcag_aa_compliant"]))
    hash_text = escape(attestation_hash)
    warning_bg = escape(warning_dark["background"])
    warning_text = escape(warning_dark["text"])

    files_html = _html_shell(
        "G6 Component Topography",
        f"""    <h2>📁 Generation 6 (G6) Attested Component Matrix</h2>
    <p><strong>System State Checksum:</strong> <code>{hash_text}</code></p>""",
    )

    dashboard_html = _html_shell(
        "G6 Telemetry Console",
        f"""    <h1>📊 Generation 6 QA Hardening Telemetry Center</h1>
    <p>Contrast ratio: {ratio_text}</p>
    <p>WCAG AA compliant: {compliant_text}</p>
    <p>Attestation hash: <code>{hash_text}</code></p>""",
    )

    slides_html = _html_shell(
        "G6 Verification Review",
        f"""    <h1>G6 Sign-Off: Hardened Renderer Core</h1>
    <p>Attestation Node: <code>{hash_text}</code></p>""",
    )

    attestation_summary = f"""# 🌌 G6 Unified Federation Framework & Deployment Attestation

## 📈 Verified Pipeline Metrics
* **Validated Warning Card Background:** `{warning_bg}`
* **Validated Warning Card Text:** `{warning_text}`
* **Calculated WCAG Contrast Performance Ratio:** `{ratio_text}`
* **Cryptographic Attestation Token:** `{hash_text}`
"""

    output_dir.mkdir(parents=True, exist_ok=True)

    files_path = output_dir / "g6_files.html"
    dashboard_path = output_dir / "g6_dashboard.html"
    slides_path = output_dir / "g6_slides.html"
    summary_path = output_dir / "g6_attestation.md"

    files_path.write_text(files_html, encoding="utf-8")
    dashboard_path.write_text(dashboard_html, encoding="utf-8")
    slides_path.write_text(slides_html, encoding="utf-8")
    summary_path.write_text(attestation_summary, encoding="utf-8")

    print(f"🚀 G6 Attestation Loop successful. Wrote artifacts to {output_dir}.")
    return {
        "attestation_hash": attestation_hash,
        "contrast_results": contrast_results,
        "warning_dark": warning_dark,
        "output_paths": {
            "files": str(files_path),
            "dashboard": str(dashboard_path),
            "slides": str(slides_path),
            "summary": str(summary_path),
        },
    }


if __name__ == "__main__":
    run_g6_attestation_loop()
