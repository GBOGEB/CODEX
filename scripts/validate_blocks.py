#!/usr/bin/env python3
"""Validate CODEX reusable block YAML SSOT records.

This is intentionally small and dependency-light for the first runtime proof.
It validates required fields and basic heading/style consistency without needing
network access or generated Office artifacts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - user environment guard
    raise SystemExit("Missing dependency: pyyaml. Install with: pip install pyyaml") from exc

REQUIRED_BLOCK_FIELDS = {
    "block_id",
    "block_type",
    "title",
    "status",
    "version",
    "section",
    "lineage",
    "render",
    "content",
}

REQUIRED_SECTION_FIELDS = {"heading_id", "heading_level", "word_style"}
REQUIRED_RENDER_FIELDS = {"markdown", "word", "excel", "html"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the root")
    return data


def validate_block(block: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_BLOCK_FIELDS - set(block))
    if missing:
        errors.append(f"block[{index}] missing required fields: {', '.join(missing)}")

    block_id = block.get("block_id", f"block[{index}]")

    section = block.get("section")
    if not isinstance(section, dict):
        errors.append(f"{block_id}: section must be a mapping")
    else:
        missing_section = sorted(REQUIRED_SECTION_FIELDS - set(section))
        if missing_section:
            errors.append(f"{block_id}: section missing fields: {', '.join(missing_section)}")
        heading_level = section.get("heading_level")
        word_style = section.get("word_style")
        if isinstance(heading_level, int) and isinstance(word_style, str):
            expected = f"Heading {heading_level}"
            if word_style != expected:
                errors.append(f"{block_id}: word_style '{word_style}' should match heading_level as '{expected}'")

    render = block.get("render")
    if not isinstance(render, dict):
        errors.append(f"{block_id}: render must be a mapping")
    else:
        missing_render = sorted(REQUIRED_RENDER_FIELDS - set(render))
        if missing_render:
            errors.append(f"{block_id}: render missing fields: {', '.join(missing_render)}")

    lineage = block.get("lineage")
    if not isinstance(lineage, dict):
        errors.append(f"{block_id}: lineage must be a mapping")
    elif not lineage.get("created_from"):
        errors.append(f"{block_id}: lineage.created_from is required")

    content = block.get("content")
    if not isinstance(content, str) or not content.strip():
        errors.append(f"{block_id}: content must be a non-empty string")

    return errors


def validate_file(path: Path) -> tuple[int, list[str]]:
    data = load_yaml(path)
    blocks = data.get("blocks")
    if not isinstance(blocks, list):
        return 0, ["root key 'blocks' must be a list"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            errors.append(f"block[{index}] must be a mapping")
            continue
        block_id = block.get("block_id")
        if block_id in seen_ids:
            errors.append(f"duplicate block_id: {block_id}")
        if isinstance(block_id, str):
            seen_ids.add(block_id)
        errors.extend(validate_block(block, index))

    return len(blocks), errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CODEX reusable block YAML SSOT records")
    parser.add_argument("path", nargs="?", default="ssot/blocks/sample_blocks.yaml", help="Path to block YAML file")
    args = parser.parse_args()

    path = Path(args.path)
    count, errors = validate_file(path)
    if errors:
        print(f"FAIL: {path} contains {len(errors)} validation error(s) across {count} block(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS: {path} contains {count} valid reusable block(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
