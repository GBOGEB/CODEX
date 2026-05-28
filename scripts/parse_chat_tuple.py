"""Parse INCUBATOR chat/session tuple YAML files from local repository paths."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
INCUBATOR_DIR = ROOT / "incubator"
TUPLE_FILE_PATTERN = re.compile(
    r"^\d{2}_W\d{2}_\d{2}_\d{2}__[A-Z0-9_]+__[A-Z0-9_]+__[A-Z0-9_]+__W\d{3}\.yml$"
)
REQUIRED_KEYS = {
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
}


def iter_tuple_files(incubator_dir: Path = INCUBATOR_DIR) -> list[Path]:
    """Return sorted tuple files matching the naming convention."""
    return sorted(
        path
        for path in incubator_dir.glob("*.yml")
        if path.name != "session_tuple_schema.yml" and TUPLE_FILE_PATTERN.match(path.name)
    )


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Safely load a YAML document from disk."""
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping at top level.")
    missing = sorted(REQUIRED_KEYS - set(payload.keys()))
    if missing:
        raise ValueError(f"{path} is missing required keys: {', '.join(missing)}")
    return payload


def load_tuple_documents(incubator_dir: Path = INCUBATOR_DIR) -> list[dict[str, Any]]:
    """Load all tuple documents from incubator/*.yml."""
    documents: list[dict[str, Any]] = []
    for path in iter_tuple_files(incubator_dir):
        doc = load_yaml_file(path)
        # Try to compute relative path, fall back to absolute if outside repo
        try:
            doc["_file"] = str(path.relative_to(ROOT))
        except ValueError:
            doc["_file"] = str(path)
        documents.append(doc)
    return documents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--incubator-dir",
        type=Path,
        default=INCUBATOR_DIR,
        help="Directory containing tuple YAML files.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional path to write parsed tuples as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    docs = load_tuple_documents(args.incubator_dir)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(docs, indent=2), encoding="utf-8")
    else:
        print(json.dumps(docs, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
