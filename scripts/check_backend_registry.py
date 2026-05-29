"""Validate physics/backend_registry.yaml schema integrity.

Checks:
- All backends have the required fields.
- At least one backend is marked available=true.
- Available backends are importable (entrypoint class exists).

Usage:
    python scripts/check_backend_registry.py [--registry PATH]
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = REPO_ROOT / "physics" / "backend_registry.yaml"

REQUIRED_FIELDS = {"description", "available", "version", "entrypoint", "capabilities"}

# Ensure repo root is importable (covers physics.*, visuals.*, etc.)
_root_str = str(REPO_ROOT)
if _root_str not in sys.path:
    sys.path.insert(0, _root_str)


def validate_registry(path: Path) -> int:
    if not path.exists():
        print(f"FAIL: registry not found: {path}", file=sys.stderr)
        return 1

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    backends: dict = data.get("backends", {})

    if not backends:
        print("FAIL: registry has no backends defined", file=sys.stderr)
        return 1

    errors: list[str] = []

    # Check required fields
    for name, cfg in backends.items():
        missing = REQUIRED_FIELDS - set(cfg.keys())
        if missing:
            errors.append(f"{name}: missing required fields: {sorted(missing)}")

    # Check at_least_one_available
    available_names = [n for n, c in backends.items() if c.get("available", False)]
    if not available_names:
        errors.append("no backend has available=true")

    # Check available backends have importable entrypoints
    for name in available_names:
        entrypoint = backends[name].get("entrypoint", "")
        if not entrypoint:
            errors.append(f"{name}: available=true but entrypoint is empty")
            continue
        parts = entrypoint.rsplit(".", 1)
        if len(parts) != 2:
            errors.append(f"{name}: entrypoint '{entrypoint}' must be 'module.ClassName'")
            continue
        module_path, class_name = parts
        try:
            module = importlib.import_module(module_path)
            if not hasattr(module, class_name):
                errors.append(
                    f"{name}: class '{class_name}' not found in module '{module_path}'"
                )
        except ImportError as exc:
            errors.append(f"{name}: cannot import '{module_path}': {exc}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print(
        f"PASS: backend registry valid — {len(backends)} backends, "
        f"{len(available_names)} available: {available_names}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate physics/backend_registry.yaml.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help="Path to backend_registry.yaml",
    )
    args = parser.parse_args(argv)
    return validate_registry(args.registry)


if __name__ == "__main__":
    raise SystemExit(main())
