"""Emit the contracted typed QCELL visual receipt after fail-closed proof steps."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "src" / "qcell_main_v0_7_7.yaml"
BOXES = ROOT / "src" / "qcell_collision_boxes_v0_7_7.json"


def fail(message: str) -> None:
    print(f"REJECT: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def overlaps(a: dict, b: dict) -> bool:
    return not (
        a["x"] + a["w"] <= b["x"]
        or b["x"] + b["w"] <= a["x"]
        or a["y"] + a["h"] <= b["y"]
        or b["y"] + b["h"] <= a["y"]
    )


def collision_state() -> str:
    payload = json.loads(read_text(BOXES))
    boxes = [box for box in payload["boxes"] if box.get("class") == "exclusive"]
    for index, left in enumerate(boxes):
        for right in boxes[index + 1 :]:
            if overlaps(left, right):
                fail(f"forbidden exclusive-box overlap: {left['id']} / {right['id']}")
    return "PASS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer-sha", required=True)
    parser.add_argument("--render-a-dir", required=True, type=Path)
    parser.add_argument("--render-b-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-f]{40}", args.producer_sha):
        fail("producer SHA must be the exact 40-character lowercase Git SHA")

    model = yaml.safe_load(read_text(SSOT))
    if model.get("authority") != "VISUAL_SEMANTIC_ONLY":
        fail("authority must remain VISUAL_SEMANTIC_ONLY")
    policy = model["main_policy"]
    if policy.get("big_teaching_arrows_default_visible") is not False:
        fail("big teaching arrows must remain OFF by default")
    if policy.get("dotted_endpoint_guides_default_visible") is not True:
        fail("dotted endpoint guides must remain ON by default")
    if policy.get("pressure_overlay_deferred") is not True:
        fail("pressure overlay must remain deferred for P1C")

    svg_a = read_text(args.render_a_dir / "qcell_main_v0_7_7.svg")
    svg_b = read_text(args.render_b_dir / "qcell_main_v0_7_7.svg")
    html_a = read_text(args.render_a_dir / "index.html")
    html_b = read_text(args.render_b_dir / "index.html")
    if svg_a != svg_b or html_a != html_b:
        fail("A/B render outputs are not byte-identical after newline normalization")

    contract = model["render_contract"]
    if svg_a != read_text(ROOT / contract["tracked_svg"]):
        fail("generated SVG differs from tracked canonical SVG")
    if html_a != read_text(ROOT / contract["tracked_html"]):
        fail("generated HTML differs from tracked canonical HTML")

    receipt = {
        "schema": "qps-qcell-visual-receipt/1.0",
        "producer_repo": "GBOGEB/CODEX",
        "producer_sha": args.producer_sha,
        "ssot_schema": str(model["schema_version"]),
        "authority": "VISUAL_SEMANTIC_ONLY",
        "main_state": "ACCEPT",
        "collision_state": collision_state(),
        "render_determinism": "PASS",
        "svg_sha256": sha256_text(svg_a),
        "html_sha256": sha256_text(html_a),
        "pressure_overlay": "DEFERRED_OFF",
        "engineering_promotion_authority": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
