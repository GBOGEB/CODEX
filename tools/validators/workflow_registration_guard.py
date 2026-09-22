#!/usr/bin/env python3
"""Fail closed on registration hazards in the controlled legacy workflow set."""

from pathlib import Path
import sys
import yaml

TARGETS = [
    Path(".github/workflows/validate.yml"),
    Path(".github/workflows/w70-qps-zero-delta-diagnostic.yml"),
    Path(".github/workflows/qps-roundtrip-zero-delta.yml"),
    Path(".github/workflows/w05-qps-roundtrip-regeneration-zero-delta.yml"),
]


def check(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if text.startswith("on:") or "\non:" in text:
        errors.append("top-level on key must be quoted as \"on\"")
    if path.name == "validate.yml" and ("&governance_paths" in text or "*governance_paths" in text):
        errors.append("governance trigger paths must be explicit; YAML anchors are not admitted")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        errors.append(f"YAML parse failed: {exc}")
        return errors
    if not isinstance(data, dict):
        errors.append("workflow root must be a mapping")
        return errors
    if "on" not in data:
        errors.append("parsed workflow has no string 'on' key")
    if not isinstance(data.get("jobs"), dict) or not data["jobs"]:
        errors.append("parsed workflow has no jobs mapping")
    return errors


def main() -> int:
    failed = False
    for path in TARGETS:
        errors = check(path)
        if errors:
            failed = True
            for error in errors:
                print(f"FAIL {path}: {error}")
        else:
            print(f"PASS {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
