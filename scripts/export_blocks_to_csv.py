#!/usr/bin/env python3
"""Export CODEX reusable block YAML records to a sortable CSV register."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: pyyaml. Install with: pip install pyyaml") from exc

COLUMNS = [
    "block_id",
    "block_type",
    "title",
    "status",
    "version",
    "source_repo",
    "heading_id",
    "heading_level",
    "word_style",
    "target_runtime",
    "tags",
    "dependencies",
    "created_from",
    "source_prompt_id",
    "renders_markdown",
    "renders_word",
    "renders_excel",
    "renders_html",
    "content_preview",
]


def load_blocks(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    blocks = data.get("blocks", [])
    if not isinstance(blocks, list):
        raise ValueError("root key 'blocks' must be a list")
    return blocks


def as_list_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def flatten_block(block: dict[str, Any]) -> dict[str, Any]:
    section = block.get("section") or {}
    lineage = block.get("lineage") or {}
    render = block.get("render") or {}
    dependencies = block.get("dependencies") or {}
    content = str(block.get("content") or "").strip().replace("\n", " ")
    return {
        "block_id": block.get("block_id", ""),
        "block_type": block.get("block_type", ""),
        "title": block.get("title", ""),
        "status": block.get("status", ""),
        "version": block.get("version", ""),
        "source_repo": block.get("source_repo", ""),
        "heading_id": section.get("heading_id", ""),
        "heading_level": section.get("heading_level", ""),
        "word_style": section.get("word_style", ""),
        "target_runtime": as_list_text(block.get("target_runtime")),
        "tags": as_list_text(block.get("tags")),
        "dependencies": as_list_text(dependencies.get("requires")),
        "created_from": lineage.get("created_from", ""),
        "source_prompt_id": lineage.get("source_prompt_id", ""),
        "renders_markdown": render.get("markdown", ""),
        "renders_word": render.get("word", ""),
        "renders_excel": render.get("excel", ""),
        "renders_html": render.get("html", ""),
        "content_preview": content[:240],
    }


def export_csv(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    blocks = load_blocks(input_path)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for block in blocks:
            writer.writerow(flatten_block(block))


def main() -> int:
    parser = argparse.ArgumentParser(description="Export reusable blocks to CSV")
    parser.add_argument("input", nargs="?", default="ssot/blocks/sample_blocks.yaml")
    parser.add_argument("output", nargs="?", default="outputs/block_register.csv")
    args = parser.parse_args()
    export_csv(Path(args.input), Path(args.output))
    print(f"Wrote block register: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
