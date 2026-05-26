"""Build runtime governance scaffold manifest."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "runtime_governance" / "manifest.json"
INPUTS = {
    "runtime_governance": ROOT / "governance" / "runtime_governance.yml",
    "agent_registry": ROOT / "governance" / "agent_registry.yml",
    "federation_registry": ROOT / "governance" / "federation_registry.yml",
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    payload = {
        "framework": "ABACUS-CODEX-FEDERATION",
        "version": 1,
        "inputs": {},
    }
    input_versions = set()

    for key, path in INPUTS.items():
        data = _load_yaml(path)
        version = data.get("version")
        if version is None:
            raise ValueError(f"{path} is missing required 'version'")
        input_versions.add(version)
        payload["inputs"][key] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "version": version,
        }

    if len(input_versions) != 1:
        raise ValueError(f"inconsistent input versions detected: {sorted(input_versions)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
