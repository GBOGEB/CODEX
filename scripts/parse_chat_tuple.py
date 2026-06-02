#!/usr/bin/env python3
"""Parse incubator tuple YAML files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
INCUBATOR_DIR = REPO_ROOT / "incubator"
TUPLE_FILE_PATTERN = re.compile(
    r"^[0-9]{2}_W[0-9]{2}_[0-9]{2}_[0-9]{2}__[A-Z0-9_]+__[A-Z0-9_]+__[A-Z0-9_]+__W[0-9]{3}\.yml$"
)
REQUIRED_KEYS = (
    "id",
    "date",
    "time_local",
    "iso_week",
    "category",
    "theme",
    "title",
    "wave",
    "status",
    "repo",
    "branch",
    "source_type",
)


def iter_tuple_files(incubator_dir: Path) -> list[Path]:
    return sorted(
        file_path
        for file_path in incubator_dir.glob("*.yml")
        if TUPLE_FILE_PATTERN.match(file_path.name)
    )


def load_yaml_file(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {path}")
    return payload


def load_tuple_documents(incubator_dir: Path | None = None) -> list[dict[str, Any]]:
    base_dir = incubator_dir or INCUBATOR_DIR
    docs: list[dict[str, Any]] = []
    for file_path in iter_tuple_files(base_dir):
        doc = load_yaml_file(file_path)
        missing = [key for key in REQUIRED_KEYS if key not in doc]
        if missing:
            raise ValueError(f"Missing required keys in {file_path.name}: {', '.join(missing)}")
        doc["_file"] = file_path.relative_to(REPO_ROOT).as_posix()
        docs.append(doc)
    return docs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=str(INCUBATOR_DIR))
    args = parser.parse_args()
    print(json.dumps(load_tuple_documents(Path(args.path)), indent=2))


if __name__ == "__main__":
    main()
