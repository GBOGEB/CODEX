#!/usr/bin/env python3
"""Build a minimal runtime manifest from governance registries."""

from __future__ import annotations

from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "MANIFEST.json"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    manifest = {
        "wave": "W000",
        "runtime_governance": load_yaml(ROOT / "governance/runtime_governance.yml"),
        "agent_registry": load_yaml(ROOT / "governance/agent_registry.yml"),
        "federation_registry": load_yaml(ROOT / "governance/federation_registry.yml"),
    }
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
