#!/usr/bin/env python3
"""Deterministically render QCELL MAIN SVG/HTML from versioned SSOT + renderer templates.

The renderer is intentionally small and fail-closed. It proves reproducible visual
artifacts only and carries VISUAL_SEMANTIC_ONLY authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "src" / "qcell_main_v0_7_7.yaml"


def fail(message: str) -> None:
    print(f"REJECT: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render(template: str, mapping: dict[str, str]) -> str:
    output = template
    for key in sorted(mapping):
        output = output.replace(f"@@{key}@@", mapping[key])
    if "@@" in output:
        unresolved = sorted({chunk.split("@@", 1)[0] for chunk in output.split("@@")[1::2]})
        fail(f"unresolved template token(s): {unresolved}")
    return output


def build_mapping(model: dict) -> dict[str, str]:
    try:
        colours = model["colour_policy"]["temperature"]["value_colours"]
        streams = model["streams"]
        render_contract = model["render_contract"]
        mapping = {
            "VERSION": str(model["schema_version"]),
            "T2": str(colours[2]),
            "T4": str(colours[4]),
            "T30": str(colours[30]),
            "T50": str(colours[50]),
            "T60": str(colours[60]),
            "T77": str(colours[77]),
            "T300": str(colours[300]),
            "A_DISPLAY": str(streams["A"]["display"]),
            "B_DISPLAY": str(streams["B"]["display"]),
            "D_DISPLAY": str(streams["D"]["display"]),
            "E_DISPLAY": str(streams["E"]["display"]),
            "STORAGE_KEY": str(render_contract["storage_key"]),
            "PRESSURE_STATUS": str(render_contract["pressure_status_label"]),
        }
    except KeyError as exc:
        fail(f"missing required SSOT key: {exc}")

    if model.get("authority") != "VISUAL_SEMANTIC_ONLY":
        fail("renderer authority must remain VISUAL_SEMANTIC_ONLY")
    if model["main_policy"].get("pressure_overlay_deferred") is not True:
        fail("P1C renderer expects pressure overlay to remain deferred")
    if model["main_policy"].get("big_teaching_arrows_default_visible") is not False:
        fail("big teaching arrows must remain OFF by default")
    if model["main_policy"].get("dotted_endpoint_guides_default_visible") is not True:
        fail("dotted endpoint guides must remain ON by default")
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--verify-tracked", action="store_true")
    args = parser.parse_args()

    model = yaml.safe_load(read_text(SSOT))
    mapping = build_mapping(model)
    contract = model["render_contract"]

    svg_template = ROOT / contract["svg_template"]
    html_template = ROOT / contract["html_template"]
    if not svg_template.exists() or not html_template.exists():
        fail("renderer template missing")

    svg = render(read_text(svg_template), mapping)
    html = render(read_text(html_template), mapping)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    svg_out = args.out_dir / "qcell_main_v0_7_7.svg"
    html_out = args.out_dir / "index.html"
    svg_out.write_text(svg, encoding="utf-8", newline="\n")
    html_out.write_text(html, encoding="utf-8", newline="\n")

    result = {
        "schema": "qsvg-deterministic-render/0.1.0",
        "status": "PASS",
        "authority": "VISUAL_SEMANTIC_ONLY",
        "ssot": str(SSOT.relative_to(ROOT)),
        "svg_sha256": sha256_text(svg),
        "html_sha256": sha256_text(html),
        "promotion_authority": False,
    }

    if args.verify_tracked:
        tracked_svg = ROOT / contract["tracked_svg"]
        tracked_html = ROOT / contract["tracked_html"]
        if svg != read_text(tracked_svg):
            fail("generated SVG differs from tracked canonical SVG")
        if html != read_text(tracked_html):
            fail("generated HTML differs from tracked canonical HTML")
        result["tracked_equality"] = "PASS"

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
