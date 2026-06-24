#!/usr/bin/env python3
"""Validate CODEX reusable block heading registry records."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: pyyaml. Install with: pip install pyyaml") from exc

REQUIRED_HEADING_FIELDS = {
    "heading_id",
    "title",
    "level",
    "word_style",
    "numbering",
    "sort_order",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the root")
    return data


def validate_heading(heading: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    heading_id = heading.get("heading_id", f"heading[{index}]")
    missing = sorted(REQUIRED_HEADING_FIELDS - set(heading))
    if missing:
        errors.append(f"{heading_id}: missing required fields: {', '.join(missing)}")

    level = heading.get("level")
    word_style = heading.get("word_style")
    if isinstance(level, int) and isinstance(word_style, str):
        expected = f"Heading {level}"
        if word_style != expected:
            errors.append(f"{heading_id}: word_style '{word_style}' should be '{expected}'")
    elif level is not None:
        errors.append(f"{heading_id}: level must be an integer")

    numbering = heading.get("numbering")
    if not isinstance(numbering, dict):
        errors.append(f"{heading_id}: numbering must be a mapping")
    else:
        if numbering.get("mode") != "generated_by_word":
            errors.append(f"{heading_id}: numbering.mode must be generated_by_word")
        if not numbering.get("list_template"):
            errors.append(f"{heading_id}: numbering.list_template is required")

    children = heading.get("children", [])
    if children is not None and not isinstance(children, list):
        errors.append(f"{heading_id}: children must be a list")

    return errors


def validate_file(path: Path) -> tuple[int, list[str]]:
    data = load_yaml(path)
    headings = data.get("headings")
    if not isinstance(headings, list):
        return 0, ["root key 'headings' must be a list"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    heading_ids: set[str] = set()

    for heading in headings:
        if isinstance(heading, dict) and isinstance(heading.get("heading_id"), str):
            heading_ids.add(heading["heading_id"])

    for index, heading in enumerate(headings):
        if not isinstance(heading, dict):
            errors.append(f"heading[{index}] must be a mapping")
            continue
        heading_id = heading.get("heading_id")
        if heading_id in seen_ids:
            errors.append(f"duplicate heading_id: {heading_id}")
        if isinstance(heading_id, str):
            seen_ids.add(heading_id)
        parent_id = heading.get("parent_id")
        if parent_id is not None and parent_id not in heading_ids:
            errors.append(f"{heading_id}: parent_id '{parent_id}' does not exist")
        for child_id in heading.get("children", []) or []:
            if child_id not in heading_ids:
                errors.append(f"{heading_id}: child heading '{child_id}' does not exist")
        errors.extend(validate_heading(heading, index))

    return len(headings), errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CODEX heading registry YAML")
    parser.add_argument("path", nargs="?", default="ssot/blocks/sample_headings.yaml")
    args = parser.parse_args()

    path = Path(args.path)
    count, errors = validate_file(path)
    if errors:
        print(f"FAIL: {path} contains {len(errors)} validation error(s) across {count} heading(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS: {path} contains {count} valid heading record(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
