#!/usr/bin/env python3
"""Validate YAML files in governance and visualization manifests."""
from pathlib import Path
import yaml

TARGETS = [Path("governance"), Path("visualization")]


def main() -> int:
    errors = []
    for root in TARGETS:
        if not root.exists():
            continue
        for file in root.rglob("*.yml"):
            try:
                yaml.safe_load(file.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"{file}: {exc}")
    if errors:
        print("YAML validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("YAML validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
