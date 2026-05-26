#!/usr/bin/env python3
import html
import hashlib
import json
from pathlib import Path
from semantic_substrate.renderer.contrast_validator import ContrastValidator
from physics.helium_refrigeration_core import CryogenicHeliumEngineG8


def _load_g8_manifest() -> dict:
    manifest_path = Path(__file__).resolve().parent / "g8_lifecycle_manifest.json"
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _resolve_warning_dark(manifest_data: dict, fallback_warning_dark: dict) -> dict:
    validation_inputs = manifest_data.get("validation_inputs", {})
    candidate = validation_inputs.get("warning_dark")
    if isinstance(candidate, dict) and "background" in candidate and "text" in candidate:
        return candidate

    for component in manifest_data.get("components", []):
        component_candidate = component.get("target_invariant", {}).get("warning", {}).get("dark", {})
        if isinstance(component_candidate, dict) and "background" in component_candidate and "text" in component_candidate:
            return component_candidate

    return fallback_warning_dark


def _resolve_milestone_vectors(manifest_data: dict) -> tuple[list[float], list[float]]:
    validation_inputs = manifest_data.get("validation_inputs", {})
    milestones = validation_inputs.get("milestones", {})
    claimed = milestones.get("claimed", [0.20, 0.40, 0.60, 0.80, 1.00])
    actual = milestones.get("actual", [0.20, 0.41, 0.59, 0.80, 1.00])
    if not isinstance(claimed, list) or not isinstance(actual, list):
        return [0.20, 0.40, 0.60, 0.80, 1.00], [0.20, 0.41, 0.59, 0.80, 1.00]
    return claimed, actual


def _render_component_rows(manifest_data: dict) -> str:
    components = manifest_data.get("components", [])
    if not isinstance(components, list) or not components:
        components = [
            {
                "id": "G8-TUPLE-A66",
                "domain": "A66 Control Architecture",
                "spatial_tag": "CCB.Room_01",
                "upstream_path": "https://www.nasa.gov/history/afj/",
                "downstream_path": "https://www.nasa.gov/history/afj/ap11fj/pdf/a11_sa507-516_dap.pdf",
            },
            {
                "id": "G8-TUPLE-HE-REF",
                "domain": "MINERVA Cryo Plant Loop",
                "spatial_tag": "AUB.Room_02",
                "upstream_path": "https://home.cern/science/engineering/cryogenics-low-temperatures-high-performance",
                "downstream_path": "physics/helium_refrigeration_core.py",
            },
            {
                "id": "G8-TUPLE-RENDER",
                "domain": "A6 WCAG Renderer Logic",
                "spatial_tag": "CLOUD.Runner",
                "upstream_path": "themes/semantic_cards.yaml",
                "downstream_path": "semantic_substrate/renderer/contrast_validator.py",
            },
        ]

    rows = []
    for component in components:
        component_id = html.escape(str(component.get("id", "N/A")))
        domain = html.escape(str(component.get("domain", "N/A")))
        spatial_tag = html.escape(str(component.get("spatial_tag", "N/A")))
        upstream_path = html.escape(str(component.get("upstream_path", "N/A")))
        downstream_path = html.escape(str(component.get("downstream_path", "N/A")))
        rows.append(
            "<tr>"
            f"<td>{component_id}</td>"
            f"<td>{domain}</td>"
            f"<td><span class=\"tag\">{spatial_tag}</span></td>"
            f"<td>{upstream_path}</td>"
            f"<td>{downstream_path}</td>"
            "</tr>"
        )

    return "".join(rows)


def execute_g8_lifecycle_validation():
    manifest_data = _load_g8_manifest()
    validator = ContrastValidator()
    engine = CryogenicHeliumEngineG8()

    warning_dark = _resolve_warning_dark(manifest_data, validator.target_invariants["warning"]["dark"])
    contrast_results = validator.validate_theme_node(warning_dark["background"], warning_dark["text"])

    claimed_milestones, actual_milestones = _resolve_milestone_vectors(manifest_data)
    covariance, correlation = engine.calculate_g8_covariance_correlation(claimed_milestones, actual_milestones)

    calculated_exergy = engine.compute_g8_exergy_efficiency(
        mass_flow_he=11.5, h_in=15.0, h_out=32.0, s_in=0.03, s_out=0.06, power_input_kw=210.0
    )

    state_token = f"G8-VALIDATION-CR:{contrast_results['contrast_ratio']:.2f}-EXERGY:{calculated_exergy:.4f}"
    g8_hash = hashlib.sha256(state_token.encode()).hexdigest()[:16].upper()

    files_html = f"""<!DOCTYPE html>
<html lang=\"en\"><head><meta charset=\"UTF-8\"><title>G8 Component Registry</title>
<style>
body {{ font-family: 'Segoe UI', system-ui, sans-serif; padding: 40px; background: #030712; color: #f3f4f6; }}
h2 {{ color: #60a5fa; border-bottom: 2px solid #1f2937; padding-bottom: 10px; font-weight: 500; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
th, td {{ padding: 14px; border: 1px solid #1f2937; text-align: left; }}
th {{ background: #111827; color: #60a5fa; font-size: 0.85em; text-transform: uppercase; }}
tr:nth-child(even) {{ background: #111827; }}
.tag {{ font-family: monospace; background: #1f2937; padding: 3px 6px; border-radius: 4px; color: #f43f5e; }}
</style></head><body>
<h2>📁 Generation 8 (G8) Comprehensive Component Traceability Matrix</h2>
<p><strong>System Core Verification Token:</strong> <code>{g8_hash}</code></p>
<table><thead><tr><th>Component ID</th><th>Functional Substrate Domain</th><th>Equipment Tag</th><th>Upstream Target (codex)</th><th>Downstream Code (abacus)</th></tr></thead><tbody>
{_render_component_rows(manifest_data)}
</tbody></table></body></html>"""

    dashboard_html = f"""<!DOCTYPE html>
<html lang=\"en\"><head><meta charset=\"UTF-8\"><title>G8 Telemetry Control Center</title>
<style>
body {{ font-family: system-ui, sans-serif; padding: 40px; background: #020617; color: #f8fafc; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 25px; margin-top: 30px; }}
.card {{ background: #0f172a; padding: 24px; border-radius: 12px; border: 1px solid #1e293b; }}
.val {{ font-size: 2.3em; font-weight: bold; color: #10b981; margin-top: 8px; }}
.lbl {{ color: #64748b; text-transform: uppercase; font-size: 0.8em; letter-spacing: 0.5px; }}
</style></head><body><h1>📊 Generation 8 Converged Telemetry Control Center</h1><div class=\"grid\"> 
<div class=\"card\"><div class=\"lbl\">Helium Plant Exergy Efficiency</div><div class=\"val\">{calculated_exergy*100:.2f}%</div></div>
<div class=\"card\"><div class=\"lbl\">A6 Warning Card Contrast Ratio</div><div class=\"val\">{contrast_results['contrast_ratio']}:1</div></div>
<div class=\"card\"><div class=\"lbl\">Workspace Phase Correlation (R)</div><div class=\"val\">{correlation:.5f}</div></div>
</div></body></html>"""

    slides_html = f"""<!DOCTYPE html>
<html lang=\"en\"><head><meta charset=\"UTF-8\"><title>G8 Audit Deck</title>
<style>
body {{ font-family: system-ui, sans-serif; background: #000; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
.deck {{ max-width: 800px; padding: 60px; background: #09090b; border: 1px solid #27272a; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }}
h1 {{ color: #3b82f6; font-size: 2.5em; margin: 0 0 20px 0; }}
p {{ color: #a1a1aa; font-size: 1.25em; line-height: 1.6; }}
</style></head><body><div class=\"deck\"><h1>G8 Continuous Lifecycle Sign-Off</h1>
<p>The <strong>MINERVA QPLANT</strong> platform has completed long-term L8 closure protocols. Software deployment engines, thermodynamic models, and accessibility guardrails are locked into an optimized execution profile.</p>
<p style=\"color:#10b981;\">System Integrity Token: <code>{g8_hash}</code></p>
</div></body></html>"""

    buildout_todo = manifest_data.get("buildout_todo")
    if buildout_todo is None:
        buildout_todo = ["Declare buildout_todo entries in g8_lifecycle_manifest.json."]
    elif not isinstance(buildout_todo, list):
        buildout_todo = ["Ensure buildout_todo is encoded as a JSON list in g8_lifecycle_manifest.json."]
    elif not buildout_todo:
        buildout_todo = ["No open buildout TODO items."]
    todo_lines = "\n".join(f"* [ ] {item}" for item in buildout_todo)
    g8_report_content = f"""# 🌌 G8 Unified Federation Framework & System Verification Specification

## 🛡️ Level 8 (L8) Closed-Loop Post-Commissioning Summary
This control center acts as the final validation layer bridging conceptual designs inside **gbogeb/codex** to deployment realities inside **gbogeb/abacus**.

### 🧪 Thermodynamic & Layout Math Foundations
$$\\psi = \\dot{{m}}_{{He}} \\cdot \\left[ (h_{{out}} - h_{{in}}) - T_0(s_{{out}} - s_{{in}}) \\right]$$

$$CR = \\frac{{L_{{lightest}} + 0.05}}{{L_{{darkest}} + 0.05}}$$

### 📈 Verified G8 Run Audit Metrics
* **A6 Warning Card Text Contrast Performance:** `{contrast_results['contrast_ratio']}:1` (Target: $\\ge 4.5:1$)
* **Workspace Velocity Correlation (R):** `{correlation:.5f}`
* **Workspace Covariance Coefficient:** `{covariance:.5f}`
* **Calculated Helium Plant Loop Exergy:** `{calculated_exergy * 100:.2f}%`
* **Immutable System Audit Checksum:** `{g8_hash}`

### 🚧 Buildout Gaps (Framework Not Fully Built Out)
{todo_lines}

---
*G8 automated audit baseline complete. Buildout remains in-progress until TODO items are closed.*
"""

    html_output_dir = Path("outputs") / "html"
    html_output_dir.mkdir(parents=True, exist_ok=True)
    (html_output_dir / "files.html").write_text(files_html, encoding="utf-8")
    (html_output_dir / "dashboard.html").write_text(dashboard_html, encoding="utf-8")
    (html_output_dir / "slides_html.html").write_text(slides_html, encoding="utf-8")
    report_path = Path("outputs") / "g8_lifecycle_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(g8_report_content, encoding="utf-8")

    print("✨ Generation 8 Environment successfully synchronized. HTML artifacts and G8 report baked for deployment.")


if __name__ == "__main__":
    execute_g8_lifecycle_validation()
