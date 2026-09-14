#!/usr/bin/env python3
"""Fail-closed static visual-control checks for QCELL MAIN v0.7.7.

This checks visual/semantic invariants only. It does not grant engineering authority.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "svg" / "qcell_main_v0_7_7.svg"
HTML = ROOT / "docs" / "index.html"
BOXES = ROOT / "src" / "qcell_collision_boxes_v0_7_7.json"

REQUIRED_GROUPS = {
    "thermal_body",
    "parasitic_loads",
    "compact_flow_legend",
    "endpoint_guides",
    "temperature_legend",
    "big_teaching_arrows",
}
REQUIRED_TEXT = {
    "4.5 K · 3 bar",
    "2–4 K · 26–31 mbar",
    "30–40 K · 12–13 bar",
    "50–60 K · ΔT≈20 K",
    "Temperature heat map",
    "300→50 K radiation",
    "300→50 K conduction",
    "50→2 K radiation",
    "50→2 K conduction",
}


def fail(msg: str) -> None:
    print(f"REJECT: {msg}")
    raise SystemExit(1)


def overlaps(a: dict, b: dict) -> bool:
    return not (
        a["x"] + a["w"] <= b["x"]
        or b["x"] + b["w"] <= a["x"]
        or a["y"] + a["h"] <= b["y"]
        or b["y"] + b["h"] <= a["y"]
    )


def main() -> int:
    for p in (SVG, HTML, BOXES):
        if not p.exists():
            fail(f"missing required artifact: {p.relative_to(ROOT)}")

    svg_text = SVG.read_text(encoding="utf-8")
    html_text = HTML.read_text(encoding="utf-8")
    root = ET.fromstring(svg_text)

    ids = {el.attrib.get("id") for el in root.iter() if el.attrib.get("id")}
    missing = REQUIRED_GROUPS - ids
    if missing:
        fail(f"missing SVG layer groups: {sorted(missing)}")

    if 'id="pressure_overlay"' in svg_text:
        fail("pressure overlay present in P1B MAIN despite deferred/OFF policy")

    big = next((el for el in root.iter() if el.attrib.get("id") == "big_teaching_arrows"), None)
    if big is None or "display:none" not in big.attrib.get("style", "").replace(" ", ""):
        fail("big teaching arrows are not fail-closed OFF by default")

    if 'class="guide"' not in svg_text or "stroke-dasharray:9 7" not in svg_text:
        fail("dotted endpoint-guide contract missing")

    for token in REQUIRED_TEXT:
        if token not in svg_text:
            fail(f"required semantic label missing: {token}")

    if "localStorage" not in html_text or "qcell-main-v0.7.7-layer-state" not in html_text:
        fail("persistent layer-state contract missing")
    if "Reset view" not in html_text:
        fail("governed reset-to-default control missing")

    payload = json.loads(BOXES.read_text(encoding="utf-8"))
    boxes = [b for b in payload["boxes"] if b.get("class") == "exclusive"]
    collisions = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            if overlaps(a, b):
                collisions.append([a["id"], b["id"]])
    if collisions:
        fail(f"forbidden exclusive-box overlaps: {collisions}")

    result = {
        "schema": "qsvg-visual-control-check/0.1.0",
        "status": "PASS",
        "authority": "VISUAL_SEMANTIC_ONLY",
        "required_groups": sorted(REQUIRED_GROUPS),
        "exclusive_boxes_checked": len(boxes),
        "forbidden_overlaps": 0,
        "pressure_overlay": "ABSENT_DEFERRED",
        "big_teaching_arrows": "OFF_DEFAULT",
        "endpoint_guides": "DOTTED_PRESENT",
        "persistent_layer_state": "PRESENT",
        "engineering_promotion_authority": False,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
