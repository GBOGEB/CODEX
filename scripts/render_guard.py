#!/usr/bin/env python3
"""Render guard: verify required governance manifests and docs are present and loadable."""
from pathlib import Path
import yaml

REQUIRED_GOVERNANCE = [
    Path("governance/runtime_governance.yml"),
    Path("governance/agent_registry.yml"),
    Path("governance/federation_registry.yml"),
    Path("governance/traceability_policy.yml"),
]

REQUIRED_DOCS = [
    Path("docs/index.md"),
    Path("docs/runtime_map.md"),
    Path("docs/federation_map.md"),
    Path("docs/governance_states.md"),
]


def main() -> int:
    errors = []
    for path in REQUIRED_GOVERNANCE:
        if not path.exists():
            errors.append(f"missing governance manifest: {path}")
        else:
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"invalid YAML in {path}: {exc}")
    for path in REQUIRED_DOCS:
        if not path.exists():
            errors.append(f"missing docs file: {path}")
    if errors:
        print("render guard: FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("render guard: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
