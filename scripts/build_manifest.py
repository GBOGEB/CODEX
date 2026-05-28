#!/usr/bin/env python3
"""Build a minimal runtime manifest from governance registries."""

from __future__ import annotations

from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "governance/runtime_manifest.json"


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
    
    # Integrate ABACUS runtime if available
    abacus_runtime_path = ROOT / "abacus_runtime/runtime_manifest.yaml"
    if abacus_runtime_path.exists():
        manifest["abacus_runtime"] = load_yaml(abacus_runtime_path)
    
    # Integrate bridge manifest if available
    bridge_manifest_path = ROOT / "bridge_manifest.yaml"
    if bridge_manifest_path.exists():
        manifest["bridge_manifest"] = load_yaml(bridge_manifest_path)
    
    # Integrate agent implementation map if available
    agent_impl_path = ROOT / "governance/agent_implementation_map.yml"
    if agent_impl_path.exists():
        manifest["agent_implementation_map"] = load_yaml(agent_impl_path)
    
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
