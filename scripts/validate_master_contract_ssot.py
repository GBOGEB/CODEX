"""Validate the MASTER Contract Governance Workbench SSOT against its schema."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from codex.ssot_resolver import resolve_ssot


def _default_authority_paths() -> tuple[Path, Path]:
    """Resolve the canonical MASTER contract document and schema from authority."""
    node = resolve_ssot("CODEX_MASTER_CONTRACT", require_local=True)
    if "path" not in node or "schema" not in node:
        raise RuntimeError("CODEX_MASTER_CONTRACT must declare both path and schema")
    return Path(node["schema"]), Path(node["path"])


DEFAULT_SCHEMA, DEFAULT_SSOT = _default_authority_paths()


def load_yaml(path: Path) -> Any:
    """Load a YAML file from disk."""
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def validate(schema_path: Path, ssot_path: Path) -> None:
    """Validate the SSOT document against the supplied JSON Schema YAML file."""
    schema = load_yaml(schema_path)
    ssot = load_yaml(ssot_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(ssot), key=lambda error: list(error.path))
    if errors:
        details = "\n".join(
            f"- {'/'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise SystemExit(f"MASTER SSOT validation failed:\n{details}")
    print(f"Validated {ssot_path} against {schema_path}")


def main() -> None:
    """Command-line entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--ssot", type=Path, default=DEFAULT_SSOT)
    args = parser.parse_args()
    validate(args.schema, args.ssot)


if __name__ == "__main__":
    main()
