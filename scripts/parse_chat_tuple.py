#!/usr/bin/env python3
"""Parse incubator tuple YAML files using safe local parsing only."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml
    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _YAML_AVAILABLE = False

_REPO_ROOT = Path(__file__).resolve().parent.parent

# Required keys for every tuple document.
REQUIRED_KEYS: frozenset[str] = frozenset({
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
})

# Filename pattern: YY_Www_HH_MM__CATEGORY__THEME__TITLE__W###.yml
TUPLE_FILE_PATTERN: re.Pattern[str] = re.compile(
    r"^[0-9]{2}_W[0-9]{2}_[0-9]{2}_[0-9]{2}__[A-Z0-9_]+__[A-Z0-9_]+__[A-Z0-9_]+__W[0-9]{3}\.yml$"
)


def parse_simple_yaml(text: str) -> dict:
    """Parse a conservative YAML subset (key/value + one-level nested maps/lists)."""
    root: dict = {}
    stack = [(0, root)]

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        line = line.strip()

        while stack and indent < stack[-1][0]:
            stack.pop()

        container = stack[-1][1]

        if line.startswith("- "):
            value = line[2:].strip().strip('"')
            if isinstance(container, list):
                container.append(value)
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "":
            next_container = {}
            container[key] = next_container
            stack.append((indent + 2, next_container))
        elif value == "[]":
            container[key] = []
        else:
            cleaned = value.strip('"')
            container[key] = cleaned
            if cleaned == "-":
                container[key] = []

        if key in container and isinstance(container[key], list):
            stack.append((indent + 2, container[key]))

    return root


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load and return a YAML tuple document as a dict.

    Uses PyYAML when available, otherwise falls back to the built-in simple
    parser.

    Args:
        path: Path to the ``.yml`` tuple file.

    Returns:
        Parsed document as a plain ``dict``.
    """
    text = path.read_text(encoding="utf-8")
    if _YAML_AVAILABLE:
        doc = _yaml.safe_load(text)
    else:
        doc = parse_simple_yaml(text)
    if not isinstance(doc, dict):
        doc = {}
    return doc


def iter_tuple_files(incubator_dir: Path) -> list[Path]:
    """Return a sorted list of tuple files matching :data:`TUPLE_FILE_PATTERN`.

    Args:
        incubator_dir: Directory to scan for ``.yml`` tuple files.

    Returns:
        Sorted list of matching :class:`~pathlib.Path` objects.
    """
    return sorted(
        p for p in incubator_dir.glob("*.yml")
        if TUPLE_FILE_PATTERN.match(p.name)
    )


def load_tuple_documents(
    incubator_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Load all tuple documents from *incubator_dir*.

    Each returned document is the parsed YAML dict with an extra ``"_file"``
    key set to ``"<dir_name>/<filename>"``.

    Args:
        incubator_dir: Directory containing tuple ``.yml`` files.  Defaults
            to ``<repo_root>/incubator``.

    Returns:
        List of tuple document dicts, each with a ``"_file"`` key.
    """
    if incubator_dir is None:
        incubator_dir = _REPO_ROOT / "incubator"

    docs: list[dict[str, Any]] = []
    for path in iter_tuple_files(incubator_dir):
        doc = load_yaml_file(path)
        if doc.get("id"):
            doc["_file"] = f"{incubator_dir.name}/{path.name}"
            docs.append(doc)
    return docs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="incubator")
    args = parser.parse_args()

    base = Path(args.path)
    tuples = []

    for file in sorted(base.glob("*.yml")):
        data = parse_simple_yaml(file.read_text(encoding="utf-8"))
        if data.get("id"):
            tuples.append(data)

    print(json.dumps(tuples, indent=2))


if __name__ == "__main__":
    main()
