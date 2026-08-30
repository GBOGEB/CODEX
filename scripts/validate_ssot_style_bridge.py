#!/usr/bin/env python3
"""Validate CODEX SSOT-style bridge controls and score awake/penetration depth."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "ssot" / "ssot_style_bridge.json"
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
REQUIRED_FEDERATION_LANES = {"html", "pdf", "pptx", "excel", "graphs", "ci", "dow", "keb"}
REQUIRED_METHOD_ORDER = ["DMAIC", "PCA_REVERSED_P5_TO_P1", "BT_PRIORITY"]


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def require_string_list(value: Any, field_name: str, errors: list[str]) -> list[str]:
    """Validate JSON/YAML list-of-string fields before set/order checks."""
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field_name} must be a list of strings")
        return []
    return value


def format_missing(values: set[str]) -> str:
    return ", ".join(sorted(values))


def validate_palette_bridge(manifest: dict[str, Any], errors: list[str]) -> None:
    bridge = manifest.get("palette_bridge", {})
    palette_path = ROOT / bridge.get("source", "")
    require(palette_path.exists(), f"palette source missing: {palette_path}", errors)
    text = read_text(palette_path)

    for card in bridge.get("required_cards", []):
        require(re.search(rf"^\s{{2}}{re.escape(card)}:\s*$", text, re.MULTILINE) is not None, f"palette card missing: {card}", errors)
    for mode in bridge.get("required_modes", []):
        require(re.search(rf"^\s{{4}}{re.escape(mode)}:\s*$", text, re.MULTILINE) is not None, f"palette mode missing: {mode}", errors)
    for token in bridge.get("required_tokens", []):
        require(re.search(rf"^\s{{6}}{re.escape(token)}:\s*['\"]#[0-9A-Fa-f]{{6}}['\"]", text, re.MULTILINE) is not None, f"palette token missing or invalid: {token}", errors)

    hex_values = re.findall(r"['\"](#[0-9A-Fa-f]{6})['\"]", text)
    require(bool(hex_values), "palette has no hex color values", errors)
    for value in hex_values:
        require(HEX_RE.match(value) is not None, f"invalid hex color: {value}", errors)


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(manifest.get("version") == "0.1.0", "version must be 0.1.0", errors)
    require(manifest.get("status") in {"draft_control", "controlled"}, "status must be draft_control or controlled", errors)
    require(manifest.get("authority", {}).get("source_repo") == "GBOGEB/CODEX", "source_repo must be GBOGEB/CODEX", errors)
    require(manifest.get("authority", {}).get("mode") == "bridge_contract", "authority mode must be bridge_contract", errors)

    lanes = manifest.get("artifact_lanes", {})
    for lane in ("html", "pdf", "pptx", "excel", "graphs"):
        require(lane in lanes, f"artifact lane missing: {lane}", errors)
        require(bool(lanes.get(lane, {}).get("controls")), f"artifact lane has no controls: {lane}", errors)

    probes = manifest.get("awake_probes", [])
    require(len(probes) >= 8, "at least eight awake probes are required", errors)
    for probe in probes:
        require(bool(probe.get("id")), "awake probe missing id", errors)
        require(bool(probe.get("kind")), f"awake probe missing kind: {probe}", errors)
        require(bool(probe.get("path")), f"awake probe missing path: {probe}", errors)
        require(isinstance(probe.get("weight"), int) and probe["weight"] > 0, f"awake probe must have positive integer weight: {probe}", errors)

    pca_axes = manifest.get("pca_axes", [])
    require([axis.get("id") for axis in pca_axes] == ["P5", "P4", "P3", "P2", "P1"], "pca_axes must be ordered P5 to P1", errors)
    require(bool(manifest.get("bt_priority", {}).get("current_top_focus")), "bt priority current_top_focus missing", errors)
    consumers = manifest.get("federation_consumers", {})
    require(consumers.get("wave_id") == "SSOT-STYLE-W04", "federation consumer wave_id must be SSOT-STYLE-W04", errors)
    require(consumers.get("public_consumer") == "GBOGEB/ABACUS", "public consumer must be GBOGEB/ABACUS", errors)
    require(consumers.get("controlled_adapter") == "GBOGEB/cryoplant-project", "controlled adapter must be GBOGEB/cryoplant-project", errors)
    shared_lanes = require_string_list(consumers.get("shared_lanes", []), "federation_consumers.shared_lanes", errors)
    missing_lanes = REQUIRED_FEDERATION_LANES - set(shared_lanes)
    require(not missing_lanes, f"missing federation shared lane(s): {format_missing(missing_lanes)}", errors)
    method_order = require_string_list(consumers.get("method_order", []), "federation_consumers.method_order", errors)
    require(method_order == REQUIRED_METHOD_ORDER, "method_order must be DMAIC, PCA_REVERSED_P5_TO_P1, BT_PRIORITY", errors)
    validate_palette_bridge(manifest, errors)
    return errors


def score_awake_probes(manifest: dict[str, Any]) -> dict[str, Any]:
    probes = manifest.get("awake_probes", [])
    total = sum(probe["weight"] for probe in probes)
    awake = 0
    by_kind: dict[str, dict[str, int]] = {}
    details = []
    for probe in probes:
        exists = (ROOT / probe["path"]).exists()
        weight = probe["weight"]
        kind = probe["kind"]
        if exists:
            awake += weight
        bucket = by_kind.setdefault(kind, {"awake": 0, "total": 0})
        bucket["total"] += weight
        bucket["awake"] += weight if exists else 0
        details.append({**probe, "exists": exists})
    return {
        "score": round((awake / total) * 100, 1) if total else 0.0,
        "awake_weight": awake,
        "total_weight": total,
        "by_kind": by_kind,
        "details": details,
    }


def probe_depth(path: Path, kind: str) -> tuple[int, int, list[str]]:
    text = read_text(path)
    if not path.exists():
        return 0, 4, ["missing"]

    signals: list[tuple[str, bool]]
    if kind == "style":
        signals = [
            ("exists", True),
            ("semantic_cards", "semantic_cards" in text),
            ("dark_mode", "dark:" in text),
            ("hex_palette", bool(re.search(r"#[0-9A-Fa-f]{6}", text))),
        ]
    elif kind == "ci":
        signals = [
            ("exists", True),
            ("pull_request", "pull_request" in text),
            ("python_setup", "setup-python" in text),
            ("validator_or_test", "pytest" in text or "python " in text or "test -f" in text),
        ]
    elif kind == "render":
        signals = [
            ("exists", True),
            ("render_language", "render" in text.lower()),
            ("guardrail", "guard" in text.lower() or "stale" in text.lower()),
            ("checksum_or_manifest", "checksum" in text.lower() or "manifest" in text.lower()),
        ]
    elif kind == "html":
        signals = [
            ("exists", True),
            ("dashboard", "dashboard" in text.lower()),
            ("health", "health" in text.lower()),
            ("pull_request", "pull_request" in text),
        ]
    elif kind == "federation":
        signals = [
            ("exists", True),
            ("runtime", "runtime" in text.lower()),
            ("federation", "federation" in text.lower()),
            ("artifact_upload", "upload-artifact" in text),
        ]
    elif kind == "keb":
        signals = [
            ("exists", True),
            ("test", "test" in text.lower()),
            ("client", "client" in text.lower()),
            ("feedback_or_queue", "feedback" in text.lower() or "queue" in text.lower()),
        ]
    elif kind == "pca":
        signals = [
            ("exists", True),
            ("test", "test" in text.lower()),
            ("federation", "federation" in text.lower()),
            ("scree_or_pca", "scree" in text.lower() or "pca" in text.lower()),
        ]
    else:
        signals = [
            ("exists", True),
            ("non_empty", bool(text.strip())),
            ("structured", ":" in text or "def " in text),
            ("governance_signal", "governance" in text.lower() or "validation" in text.lower()),
        ]

    labels = [label for label, ok in signals if ok]
    return len(labels), len(signals), labels


def score_penetration(manifest: dict[str, Any]) -> dict[str, Any]:
    depth = 0
    total = 0
    details = []
    by_kind: dict[str, dict[str, int]] = {}
    for probe in manifest.get("awake_probes", []):
        got, possible, signals = probe_depth(ROOT / probe["path"], probe["kind"])
        depth += got
        total += possible
        bucket = by_kind.setdefault(probe["kind"], {"depth": 0, "total": 0})
        bucket["depth"] += got
        bucket["total"] += possible
        details.append({"id": probe["id"], "kind": probe["kind"], "path": probe["path"], "depth": got, "total": possible, "signals": signals})
    return {
        "score": round((depth / total) * 100, 1) if total else 0.0,
        "depth": depth,
        "total": total,
        "by_kind": by_kind,
        "details": details,
    }


def artifact_lane_score(manifest: dict[str, Any]) -> dict[str, Any]:
    lanes = manifest.get("artifact_lanes", {})
    total = sum(len(lane.get("controls", [])) for lane in lanes.values())
    covered = sum(1 for lane in lanes.values() for control in lane.get("controls", []) if control)
    return {
        "families": len(lanes),
        "controls": total,
        "score": round((covered / total) * 100, 1) if total else 0.0,
    }


def build_report(manifest: dict[str, Any]) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    return {
        "valid": not errors,
        "errors": errors,
        "version": manifest.get("version"),
        "artifact_lanes": artifact_lane_score(manifest),
        "awake": score_awake_probes(manifest),
        "penetration": score_penetration(manifest),
        "pca_axes": manifest.get("pca_axes", []),
        "bt_priority": manifest.get("bt_priority", {}),
        "dmaic": manifest.get("dmaic", {}),
        "federation_consumers": manifest.get("federation_consumers", {}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    report = build_report(manifest)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
