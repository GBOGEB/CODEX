from __future__ import annotations

import hashlib
import html
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"))

from renderers.layout_intelligence import AdaptiveLayoutEngine, CardLayoutInput
from renderers.lint.thresholds import MAX_CARD_BODY_LINES
from renderers.theme_runtime import SemanticThemeRuntime
from semantic_delta_replay import run as run_semantic_replay

RENDERER_VERSION = "abacus-reference-html/1.0.0"
HERE = Path(__file__).resolve().parent
DEFAULT_SSOT = HERE / "ssot" / "reference_publication.yaml"
TUPLE_LEDGER = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime" / "data" / "semantic_tuple_ledger.json"
OUTPUT_DIR = HERE / "outputs"
RECEIPT_DIR = HERE / "receipts"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def linearize(channel: float) -> float:
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def luminance(value: str) -> float:
    r, g, b = (linearize(c) for c in hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: str, background: str) -> float:
    a, b = luminance(foreground), luminance(background)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def render_html(ssot: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    publication = ssot["publication"]
    card = publication["semantic_card"]
    mode = publication["theme"]

    theme = SemanticThemeRuntime().resolve(card["type"], mode)
    body_lines = [str(line) for line in card.get("body", [])]

    layout_engine = AdaptiveLayoutEngine()
    layout_decisions = layout_engine.decide_card_layout(
        CardLayoutInput(
            title=str(card["title"]),
            body_line_count=len(body_lines),
            semantic_weight=str(card.get("semantic_weight", "normal")),
        )
    )

    ratio = contrast_ratio(theme.text, theme.background)
    contrast_pass = ratio >= 4.5
    overflow_pass = len(body_lines) <= MAX_CARD_BODY_LINES
    layout_pass = not any(d.decision == "split_card_or_reduce_density" for d in layout_decisions)

    body_html = "\n".join(f"<li>{html.escape(line)}</li>" for line in body_lines)
    artifact = f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>{html.escape(publication['title'])}</title></head>
<body style=\"background:#181421;color:#F5F2FF;font-family:Aptos,Arial,sans-serif\">
<main data-publication-id=\"{html.escape(publication['id'])}\" data-render-mode=\"{html.escape(publication['render_mode'])}\">
<section style=\"background:{theme.background};color:{theme.text};border:1px solid {theme.border};padding:24px;border-radius:12px\">
<h1>{html.escape(card['title'])}</h1>
<ul>
{body_html}
</ul>
</section>
</main>
</body>
</html>
""".encode("utf-8")

    checks = {
        "contrast": {
            "pass": contrast_pass,
            "ratio": round(ratio, 3),
            "threshold": 4.5,
            "foreground": theme.text,
            "background": theme.background,
        },
        "layout": {
            "pass": layout_pass,
            "decisions": [
                {"component": d.component, "decision": d.decision, "reason": d.reason}
                for d in layout_decisions
            ],
        },
        "overflow": {
            "pass": overflow_pass,
            "body_line_count": len(body_lines),
            "max_body_lines": MAX_CARD_BODY_LINES,
        },
    }
    return artifact, checks


def execute(ssot_path: Path = DEFAULT_SSOT) -> dict[str, Any]:
    ssot_bytes = ssot_path.read_bytes()
    ssot = yaml.safe_load(ssot_bytes)
    if not isinstance(ssot, dict) or "publication" not in ssot:
        raise ValueError("SSOT must contain a publication mapping")

    artifact_bytes, renderer_checks = render_html(ssot)
    replay = run_semantic_replay()
    replay_pass = replay.get("status") == "PASS"

    checks = dict(renderer_checks)
    checks["semantic_replay"] = {
        "pass": replay_pass,
        "status": replay.get("status", "UNKNOWN"),
        "tuple_count": replay.get("final_state", {}).get("tuple_count"),
    }

    decision = "accept" if all(check["pass"] for check in checks.values()) else "reject"
    publication = ssot["publication"]

    receipt = {
        "receipt_version": "A8.0",
        "artifact_sha256": sha256_bytes(artifact_bytes),
        "ssot_sha256": sha256_bytes(ssot_bytes),
        "renderer_version": RENDERER_VERSION,
        "theme": publication["theme"],
        "render_mode": publication["render_mode"],
        "checks": checks,
        "tuple_ledger_sha256": sha256_bytes(TUPLE_LEDGER.read_bytes()),
        "decision": decision,
        "source_commit": os.environ.get("GITHUB_SHA", "local"),
        "publication_id": publication["id"],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "reference_render.html").write_bytes(artifact_bytes)
    (RECEIPT_DIR / "renderer_execution_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt


if __name__ == "__main__":
    result = execute()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "accept" else 1)
