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


def _normalize_repo_path(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    payload = {
        "framework": "ABACUS-CODEX-FEDERATION",
        "version": 1,
        "inputs": {},
    }
    input_versions = set()
    version_by_path = {}

    for key, path in INPUTS.items():
        data = _load_yaml(path)
        version = data.get("version")
        if version is None:
            raise ValueError(f"{path} is missing required 'version'")
        input_versions.add(version)
        normalized_path = _normalize_repo_path(path)
        version_by_path[normalized_path] = version
        payload["inputs"][key] = {
            "path": normalized_path,
            "version": version,
        }

    if len(input_versions) != 1:
        details = ", ".join(f"{path}={version}" for path, version in sorted(version_by_path.items()))
        raise ValueError(f"inconsistent input versions detected: {details}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
