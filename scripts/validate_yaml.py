#!/usr/bin/env python3
"""Validate governance YAML files for basic parse integrity."""

from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "governance/runtime_governance.yml",
    ROOT / "governance/agent_registry.yml",
    ROOT / "governance/federation_registry.yml",
]


def main() -> int:
    ok = True
    for target in TARGETS:
        try:
            with target.open("r", encoding="utf-8") as handle:
                yaml.safe_load(handle)
            print(f"OK: {target}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"FAIL: {target} -> {exc}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
