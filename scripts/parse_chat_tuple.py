#!/usr/bin/env python3
"""Parse incubator tuple YAML files using safe local parsing only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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
