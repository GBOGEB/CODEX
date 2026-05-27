#!/usr/bin/env python3
"""PR-007 governance header parser and gate for federation_runtime."""

from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

HEADER_PATTERN = re.compile(r"## PR CLASSIFICATION\n(.*?)\n---", re.DOTALL)


def extract_governance_block(markdown_text: str) -> dict[str, str] | None:
    """Extract PR classification metadata from markdown."""
    match = HEADER_PATTERN.search(markdown_text)
    if not match:
        return None

    metadata: dict[str, str] = {}
    for raw_line in match.group(1).strip().splitlines():
        line = raw_line.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


def validate_metadata(metadata: dict[str, str], schema: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for key in schema.get("required", []):
        if key not in metadata:
            errors.append(f"Missing required key: {key}")

    properties = schema.get("properties", {})
    for key, prop in properties.items():
        if key not in metadata:
            continue
        value = metadata[key]
        pattern = prop.get("pattern")
        if pattern and not re.match(pattern, value):
            errors.append(f"Pattern mismatch for {key}: {value}")
        const = prop.get("const")
        if const and value != const:
            errors.append(f"Const mismatch for {key}: {value}")
        enum = prop.get("enum")
        if enum and value not in enum:
            errors.append(f"Enum mismatch for {key}: {value}")

    if metadata.get("TYPE") != "GOVERNANCE" and metadata.get("SCHEMA MUTATION") in {"YES", "CONTROLLED"}:
        errors.append("Unauthorized schema mutation outside GOVERNANCE type")

    return (len(errors) == 0, errors)


@lru_cache(maxsize=16)
def _yaml_key_pattern(key: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$")


def _extract_yaml_scalar(yaml_path: Path, key: str) -> str | None:
    key_pattern = _yaml_key_pattern(key)
    for raw_line in yaml_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = key_pattern.match(line)
        if not match:
            continue
        value = match.group(1).split("#", 1)[0].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value
    return None


def _validate_required_artifacts(manifest: dict, root: Path) -> list[str]:
    errors: list[str] = []
    required_artifacts = manifest.get("required_artifacts", {})
    for artifact_group in required_artifacts.values():
        if not isinstance(artifact_group, list):
            errors.append("Invalid required_artifacts shape in traceability manifest")
            continue
        for artifact in artifact_group:
            if not isinstance(artifact, str):
                errors.append("Invalid required artifact entry in traceability manifest")
                continue
            if Path(artifact).is_absolute():
                errors.append(f"Required artifact must be a relative path: {artifact}")
                continue
            artifact_path = root / artifact
            if not artifact_path.exists():
                errors.append(f"Required artifact missing on disk: {artifact}")
    return errors


def run_header_compliance_audit(
    target_file: Path,
    schema_path: Path,
    traceability_manifest_path: Path,
    pr_track_path: Path,
    wave_plan_path: Path,
    runtime_root: Path,
) -> int:
    print("[PR-007] Running federation governance parser...")
    print(
        f"[PR-007] INPUTS target={target_file} schema={schema_path} "
        f"traceability_manifest={traceability_manifest_path} pr_track={pr_track_path} "
        f"wave_plan={wave_plan_path}"
    )

    required_paths = {
        "target": target_file,
        "schema": schema_path,
        "traceability_manifest": traceability_manifest_path,
        "pr_track": pr_track_path,
        "wave_plan": wave_plan_path,
    }
    missing_inputs = [name for name, path in required_paths.items() if not path.exists()]
    if missing_inputs:
        print(f"[PR-007][ERROR] Missing required inputs: {', '.join(missing_inputs)}")
        return 1

    metadata = extract_governance_block(target_file.read_text(encoding="utf-8"))
    if not metadata:
        print("[PR-007][ERROR] Could not parse mandatory governance header block.")
        return 1

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    manifest = json.loads(traceability_manifest_path.read_text(encoding="utf-8"))

    process_steps = [
        "header-extraction",
        "schema-validation",
        "artifact-validation",
        "wave-drift-check",
        "pr-order-check",
    ]

    _, schema_errors = validate_metadata(metadata, schema)
    artifact_errors = _validate_required_artifacts(manifest, runtime_root)

    drift_errors: list[str] = []
    header_wave = metadata.get("WAVE")
    manifest_wave = manifest.get("active_wave")
    pr_track_wave = _extract_yaml_scalar(pr_track_path, "wave")
    wave_plan_active_wave = _extract_yaml_scalar(wave_plan_path, "active_wave")

    wave_sources = [
        ("manifest", manifest_wave),
        ("pr_track", pr_track_wave),
        ("wave_plan", wave_plan_active_wave),
    ]
    for source_name, source_wave in wave_sources:
        if header_wave and source_wave and header_wave != source_wave:
            drift_errors.append(f"Wave drift: header={header_wave} {source_name}={source_wave}")

    pr_order_errors: list[str] = []
    header_pr_id = metadata.get("PR-ID")
    pr_stream = manifest.get("pr_stream", [])
    valid_pr_stream: list[str] = []
    if isinstance(pr_stream, list):
        non_string_entries = [item for item in pr_stream if not isinstance(item, str)]
        if non_string_entries:
            invalid_types = sorted({type(item).__name__ for item in non_string_entries})
            pr_order_errors.append(
                f"Invalid pr_stream entries: {len(non_string_entries)} non-string item(s) "
                f"(types: {', '.join(invalid_types)})"
            )
        valid_pr_stream = [item for item in pr_stream if isinstance(item, str)]
    else:
        pr_order_errors.append("Invalid pr_stream shape in traceability manifest")

    if header_pr_id and header_pr_id not in valid_pr_stream:
        pr_order_errors.append(f"PR-ID not in traceability manifest stream: {header_pr_id}")

    pr_track_focus = _extract_yaml_scalar(pr_track_path, "current_focus")
    if header_pr_id and pr_track_focus and header_pr_id != pr_track_focus:
        pr_order_errors.append(f"PR track focus mismatch: header={header_pr_id} pr_track={pr_track_focus}")

    errors = schema_errors + artifact_errors + drift_errors + pr_order_errors
    if errors:
        for err in errors:
            print(f"[PR-007][ERROR] {err}")
        return 1

    audit_output = {
        "inputs": {k: str(v) for k, v in required_paths.items()},
        "process": process_steps,
        "output": {
            "metadata": metadata,
            "active_wave": header_wave,
            "pr_id": header_pr_id,
            "traceability_pr_stream_length": len(valid_pr_stream),
            "validation_status": "PASS",
        },
    }

    print(f"[PR-007] PR-ID={metadata.get('PR-ID')} WAVE={metadata.get('WAVE')} TYPE={metadata.get('TYPE')}")
    print(f"[PR-007] PROCESS={','.join(process_steps)}")
    print(f"[PR-007] OUTPUT={json.dumps(audit_output['output'], sort_keys=True)}")
    print("[PR-007] Governance header validated successfully.")
    return 0


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate federation governance PR header markdown")
    parser.add_argument(
        "--target",
        default=str(root / ".github" / "W003_PR_FOLLOW_UP.md"),
        help="Path to markdown file containing mandatory governance header",
    )
    parser.add_argument(
        "--schema",
        default=str(root / "schema" / "governance_header.schema.json"),
        help="Path to governance header schema",
    )
    parser.add_argument(
        "--traceability-manifest",
        default=str(root / "governance" / "traceability_manifest.json"),
        help="Path to governance traceability manifest",
    )
    parser.add_argument(
        "--pr-track",
        default=str(root / "governance" / "pr_track.yml"),
        help="Path to governance PR track file",
    )
    parser.add_argument(
        "--wave-plan",
        default=str(root / "governance" / "wave_recreation_plan.yml"),
        help="Path to wave recreation plan file",
    )
    args = parser.parse_args()
    sys.exit(
        run_header_compliance_audit(
            target_file=Path(args.target),
            schema_path=Path(args.schema),
            traceability_manifest_path=Path(args.traceability_manifest),
            pr_track_path=Path(args.pr_track),
            wave_plan_path=Path(args.wave_plan),
            runtime_root=root,
        )
    )
