#!/usr/bin/env python3
"""
MESSAGE 3: Static Offline Reconciler.

Loads the Google Drive exchange manifest locally without calling external APIs or
altering production tracks. The reconciler inspects the configured
``lineage_mapping`` entries, detects missing inbound files, and prints strategy
telemetry for review.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ALLOWED_STRATEGIES = {"PRUNE", "BRIDGE", "CHERRY-PICK", "PARALLEL", "DISCARD"}


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load the YAML manifest, preferring PyYAML with a small fallback parser."""
    content = manifest_path.read_text(encoding="utf-8")
    if importlib.util.find_spec("yaml") is not None:
        import yaml

        loaded = yaml.safe_load(content)
        return loaded if isinstance(loaded, dict) else {}
    return parse_minimal_manifest(content)


def parse_minimal_manifest(content: str) -> dict[str, Any]:
    """Parse the simple manifest structures used by this provisional exchange."""
    manifest: dict[str, Any] = {}
    current_key: str | None = None
    current_dict: dict[str, str] | None = None

    for raw_line in content.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            current_key = line[:-1]
            manifest[current_key] = [] if current_key == "lineage_mapping" else {}
            current_dict = None
            continue
        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            manifest[key] = clean_scalar(value)
            current_key = key
            current_dict = None
            continue
        if current_key == "lineage_mapping" and line.startswith("- "):
            current_dict = {}
            manifest.setdefault("lineage_mapping", []).append(current_dict)
            remainder = line[2:]
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current_dict[key.strip()] = clean_scalar(value)
            continue
        if current_key == "lineage_mapping" and current_dict is not None and ":" in line:
            key, value = line.split(":", 1)
            current_dict[key.strip()] = clean_scalar(value)

    return manifest


def clean_scalar(value: str) -> Any:
    stripped = value.strip()
    if stripped == "[]":
        return []
    if stripped == "":
        return ""
    if (stripped.startswith('"') and stripped.endswith('"')) or (
        stripped.startswith("'") and stripped.endswith("'")
    ):
        return stripped[1:-1]
    return stripped


def normalize_lineage_mapping(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = manifest.get("lineage_mapping", [])
    if mapping is None or mapping == "":
        return []
    if not isinstance(mapping, list):
        raise ValueError("lineage_mapping must be a list")
    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(mapping, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"lineage_mapping entry {index} must be a mapping")
        normalized.append(entry)
    return normalized


def entry_source_path(entry: dict[str, Any]) -> str:
    for key in ("source_path", "inbound", "inbound_file", "source", "file"):
        value = entry.get(key)
        if value:
            return str(value)
    raise ValueError(f"lineage_mapping entry is missing source_path: {entry}")


def entry_strategy(entry: dict[str, Any], source_path: str) -> str:
    strategy = str(entry.get("action_strategy", entry.get("strategy", "PARALLEL"))).upper()
    if strategy not in ALLOWED_STRATEGIES:
        raise ValueError(f"Invalid strategy for {source_path}: {strategy}")
    return strategy


def entry_destination(entry: dict[str, Any]) -> str:
    return str(entry.get("target_destination", entry.get("target_path", "")))


class StaticReconciler:
    """Offline manifest reconciler for review-first Drive telemetry."""

    def __init__(self, root: Path):
        self.root = root
        self.exchange_dir = root / "googledrive"
        self.manifest_path = self.exchange_dir / ".codex-exchange.yaml"

    def build_report(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest absent at {self.manifest_path}")

        manifest = load_manifest(self.manifest_path)
        mappings = normalize_lineage_mapping(manifest)
        telemetry: Counter[str] = Counter()
        missing: list[str] = []
        entries: list[dict[str, Any]] = []

        for item in mappings:
            source_path = entry_source_path(item)
            strategy = entry_strategy(item, source_path)
            destination = entry_destination(item)
            source_rel = Path(source_path)
            if source_rel.is_absolute() or ".." in source_rel.parts:
                raise ValueError(f"Unsafe source_path in manifest: {source_path}")
            source = self.exchange_dir / source_rel
            exists = source.exists()
            telemetry[strategy] += 1
            if not exists:
                missing.append(source_path)
            entries.append(
                {
                    "source_path": source_path,
                    "exists": exists,
                    "action_strategy": strategy,
                    "target_destination": destination,
                    "rationale": str(item.get("rationale", "")),
                }
            )

        return {
            "manifest": str(self.manifest_path),
            "mapping_count": len(mappings),
            "entries": entries,
            "missing_inbound_files": missing,
            "strategy_telemetry": {
                strategy: telemetry.get(strategy, 0) for strategy in sorted(ALLOWED_STRATEGIES)
            },
        }

    def execute_static_check(self, emit_json: bool = False) -> dict[str, Any]:
        report = self.build_report()
        if emit_json:
            print(json.dumps(report, indent=2, sort_keys=True))
            return report

        print("[*] Initiating Offline Manifest Verification...")
        print(f"[+] Loaded {report['mapping_count']} mappings from SSoT manifest.")
        print("-" * 70)
        for item in report["entries"]:
            exists = "FOUND" if item["exists"] else "MISSING"
            print(f"File: {item['source_path']} [{exists}]")
            print(f" ├── Strategy Target: {item['action_strategy']}")
            print(f" └── Destination:     {item['target_destination']}")
        print("-" * 70)
        print("Strategy telemetry:")
        for strategy, count in report["strategy_telemetry"].items():
            print(f"- {strategy}: {count}")
        if report["missing_inbound_files"]:
            print("Missing inbound files:")
            for source_path in report["missing_inbound_files"]:
                print(f"- {source_path}")
        print("No production files were mutated.")
        return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print telemetry as JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    workspace_root = Path(__file__).resolve().parents[2]
    StaticReconciler(workspace_root).execute_static_check(emit_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
