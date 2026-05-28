from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_MAP_PATH = ROOT / "federation" / "orchestration" / "codex_abacus_bridge_map.yaml"
ABACUS_MANIFEST_PATH = ROOT / "abacus_runtime" / "runtime_manifest.yaml"
FEDERATION_CONTRACT_PATH = ROOT / "governance" / "contracts" / "delta-1-runtime-federation-contract.yaml"
SYNC_PATH = ROOT / "governance" / "synchronization" / "abacus-codex-recursive-sync.yaml"
SEMANTIC_SCHEMA_PATH = ROOT / "federation" / "semantic_index" / "schema.yaml"


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def _is_dormant_directory(path: Path) -> bool:
    if not path.is_dir():
        return False
    entries = list(path.iterdir())
    if not entries:
        return True
    return all(entry.name == ".gitkeep" for entry in entries)


def _allowed_statuses(schema: dict) -> set[str]:
    return set(
        schema.get("properties", {})
        .get("human_render", {})
        .get("properties", {})
        .get("status", {})
        .get("enum", [])
    )


def validate(strict_dormant: bool, strict_coverage: bool = False) -> int:
    required_files = [
        BRIDGE_MAP_PATH,
        ABACUS_MANIFEST_PATH,
        FEDERATION_CONTRACT_PATH,
        SYNC_PATH,
        SEMANTIC_SCHEMA_PATH,
    ]
    missing_files = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing_files:
        print("bridge alignment check failed: required files missing")
        for file in missing_files:
            print(f"- {file}")
        return 1

    bridge_map = _load_yaml(BRIDGE_MAP_PATH).get("bridge", {})
    alignment = bridge_map.get("module_alignment", [])
    manifest_modules = set(_load_yaml(ABACUS_MANIFEST_PATH).get("modules", []))
    mapped_modules: set[str] = set()
    allowed_statuses: set[str] | None = None

    errors: list[str] = []
    dormant: list[str] = []
    unmapped: list[str] = []

    for item in alignment:
        module = item.get("abacus_module")
        codex_path = item.get("codex_path")
        workflow = item.get("workflow")
        status = item.get("status")

        if module not in manifest_modules:
            errors.append(f"module '{module}' is not defined in abacus_runtime/runtime_manifest.yaml")
        elif module in mapped_modules:
            errors.append(f"module '{module}' is mapped more than once in bridge alignment")
        else:
            mapped_modules.add(module)

        if not codex_path:
            errors.append("module_alignment entry has no codex_path")
            continue

        path = ROOT / codex_path
        if not path.exists():
            errors.append(f"codex_path '{codex_path}' does not exist")
            continue

        if _is_dormant_directory(path):
            dormant.append(codex_path)

        if workflow and not (ROOT / workflow).exists():
            errors.append(f"workflow '{workflow}' does not exist")

        if status:
            if allowed_statuses is None:
                allowed_statuses = _allowed_statuses(_load_yaml(SEMANTIC_SCHEMA_PATH))
            if allowed_statuses and status not in allowed_statuses:
                allowed = ", ".join(sorted(allowed_statuses))
                errors.append(f"status '{status}' is invalid (expected one of: {allowed})")

    if errors:
        print("bridge alignment check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    unmapped = sorted(manifest_modules - mapped_modules)

    print("bridge alignment check passed")
    print(f"- mapped modules: {len(alignment)}")
    print(f"- abacus module count: {len(manifest_modules)}")
    if manifest_modules:
        coverage = len(mapped_modules) / len(manifest_modules)
        print(f"- module coverage: {coverage:.2f}")
    else:
        print("- module coverage: N/A (no abacus modules declared)")

    if dormant:
        print("- dormant codex paths detected:")
        for path in dormant:
            print(f"  - {path}")
        if strict_dormant:
            print("strict dormant mode is enabled; failing due to dormant codex paths")
            return 1

    if unmapped:
        print("- unmapped abacus modules detected:")
        for module in unmapped:
            print(f"  - {module}")
        if strict_coverage:
            print("strict coverage mode is enabled; failing due to unmapped abacus modules")
            return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CODEX↔ABACUS bridge mapping and detect dormant bridge paths.")
    parser.add_argument(
        "--strict-dormant",
        action="store_true",
        help="Fail when mapped codex paths are empty or only contain .gitkeep.",
    )
    parser.add_argument(
        "--strict-coverage",
        action="store_true",
        help="Fail when ABACUS runtime modules are not mapped by the bridge file.",
    )
    args = parser.parse_args()
    return validate(strict_dormant=args.strict_dormant, strict_coverage=args.strict_coverage)


if __name__ == "__main__":
    raise SystemExit(main())
