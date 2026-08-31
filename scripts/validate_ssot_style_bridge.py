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
REQUIRED_BLOCKING_CONCLUSIONS = {"failure", "timed_out", "action_required", "startup_failure", "stale"}
REQUIRED_MANUAL_REVIEW_CONCLUSIONS = {"cancelled"}
REQUIRED_PENDING_STATUSES = {"queued", "in_progress", "requested", "waiting", "pending"}
REQUIRED_REPAIR_PRS = {"GBOGEB/ABACUS": {754, 756}, "GBOGEB/CODEX": {298, 300}}
REQUIRED_ALL_CLEAR_REQUIREMENTS = {"no_blocking_conclusions", "no_unwaived_cancelled_checks", "no_pending_required_checks", "no_unresolved_material_reviews", "repaired_sha_retested", "downstream_return_receipt_accepted"}
REQUIRED_FEDERATION_REPOS = {"GBOGEB/ABACUS", "GBOGEB/CODEX", "GBOGEB/cryoplant-project"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def format_missing(values: set[Any]) -> str:
    return ", ".join(str(value) for value in sorted(values))


def require_mapping(value: Any, field_name: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field_name} must be an object")
        return {}
    return value


def require_pr_set(value: Any, field_name: str, errors: list[str]) -> set[int]:
    if isinstance(value, int):
        return {value}
    if not isinstance(value, list) or not all(isinstance(item, int) for item in value):
        errors.append(f"{field_name} must be an integer or list of integers")
        return set()
    return set(value)


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
    consumers = require_mapping(manifest.get("federation_consumers", {}), "federation_consumers", errors)
    require(consumers.get("wave_id") == "SSOT-STYLE-W04", "federation consumer wave_id must be SSOT-STYLE-W04", errors)
    require(consumers.get("public_consumer") == "GBOGEB/ABACUS", "public consumer must be GBOGEB/ABACUS", errors)
    require(consumers.get("controlled_adapter") == "GBOGEB/cryoplant-project", "controlled adapter must be GBOGEB/cryoplant-project", errors)
    shared_lanes = require_string_list(consumers.get("shared_lanes", []), "federation_consumers.shared_lanes", errors)
    missing_lanes = REQUIRED_FEDERATION_LANES - set(shared_lanes)
    require(not missing_lanes, f"missing federation shared lane(s): {format_missing(missing_lanes)}", errors)
    method_order = require_string_list(consumers.get("method_order", []), "federation_consumers.method_order", errors)
    require(method_order == REQUIRED_METHOD_ORDER, "method_order must be DMAIC, PCA_REVERSED_P5_TO_P1, BT_PRIORITY", errors)
    validate_handoff_check_policy(manifest, errors)
    validate_lineage_binding(manifest, errors)
    validate_palette_bridge(manifest, errors)
    return errors


def validate_handoff_check_policy(manifest: dict[str, Any], errors: list[str]) -> None:
    policy = require_mapping(manifest.get("handoff_check_policy", {}), "handoff_check_policy", errors)
    require(policy.get("wave_id") == "SSOT-STYLE-W04", "handoff check policy wave_id must be SSOT-STYLE-W04", errors)
    repair_links = require_mapping(policy.get("linked_repair_prs", {}), "handoff_check_policy.linked_repair_prs", errors)
    for repo, required in REQUIRED_REPAIR_PRS.items():
        observed = require_pr_set(repair_links.get(repo, []), f"handoff_check_policy.linked_repair_prs.{repo}", errors)
        missing = required - observed
        require(not missing, f"linked repair PR(s) missing for {repo}: {format_missing(missing)}", errors)

    blocking = set(require_string_list(policy.get("blocking_conclusions", []), "handoff_check_policy.blocking_conclusions", errors))
    manual = set(require_string_list(policy.get("manual_review_conclusions", []), "handoff_check_policy.manual_review_conclusions", errors))
    pending = set(require_string_list(policy.get("pending_statuses", []), "handoff_check_policy.pending_statuses", errors))
    require(REQUIRED_BLOCKING_CONCLUSIONS <= blocking, f"missing blocking conclusion(s): {format_missing(REQUIRED_BLOCKING_CONCLUSIONS - blocking)}", errors)
    require(REQUIRED_MANUAL_REVIEW_CONCLUSIONS <= manual, f"missing manual-review conclusion(s): {format_missing(REQUIRED_MANUAL_REVIEW_CONCLUSIONS - manual)}", errors)
    require(REQUIRED_PENDING_STATUSES <= pending, f"missing pending status(es): {format_missing(REQUIRED_PENDING_STATUSES - pending)}", errors)

    requirements = set(require_string_list(policy.get("all_clear_requirements", []), "handoff_check_policy.all_clear_requirements", errors))
    require(REQUIRED_ALL_CLEAR_REQUIREMENTS <= requirements, f"missing all-clear requirement(s): {format_missing(REQUIRED_ALL_CLEAR_REQUIREMENTS - requirements)}", errors)
    feedback = require_mapping(policy.get("repository_feedback", {}), "handoff_check_policy.repository_feedback", errors)
    for field in ("from_abacus", "to_abacus"):
        require(isinstance(feedback.get(field), str) and bool(feedback[field].strip()), f"repository_feedback.{field} must be a non-empty string", errors)


def validate_lineage_binding(manifest: dict[str, Any], errors: list[str]) -> None:
    lineage = require_mapping(manifest.get("lineage_binding", {}), "lineage_binding", errors)
    require(lineage.get("contract_version") == "0.2.0", "lineage contract_version must be 0.2.0", errors)
    require(lineage.get("status") == "pending_retest", "lineage status must be pending_retest", errors)
    inputs = require_mapping(lineage.get("baseline_inputs", {}), "lineage_binding.baseline_inputs", errors)
    for repo in REQUIRED_FEDERATION_REPOS:
        binding = require_mapping(inputs.get(repo, {}), f"lineage_binding.baseline_inputs.{repo}", errors)
        require(bool(SHA_RE.fullmatch(str(binding.get("commit_sha", "")))), f"invalid commit SHA for {repo}", errors)
        require(bool(SHA256_RE.fullmatch(str(binding.get("manifest_sha256", "")))), f"invalid manifest SHA256 for {repo}", errors)
        require(bool(binding.get("manifest_path")), f"manifest path missing for {repo}", errors)


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
        "handoff_check_policy": manifest.get("handoff_check_policy", {}),
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
