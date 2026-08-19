#!/usr/bin/env python3
"""Render CODEX reusable block YAML records into a Markdown preview."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: pyyaml. Install with: pip install pyyaml") from exc


def load_blocks(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    blocks = data.get("blocks", [])
    if not isinstance(blocks, list):
        raise ValueError("root key 'blocks' must be a list")
    return blocks


def fence_language(block: dict[str, Any]) -> str:
    language = str(block.get("language") or "").strip().lower()
    if language in {"python", "bash", "json", "yaml", "markdown", "text"}:
        return language
    return "text"


def render_block(block: dict[str, Any]) -> list[str]:
    section = block.get("section") or {}
    lineage = block.get("lineage") or {}
    render = block.get("render") or {}
    title = block.get("title", "Untitled block")
    block_id = block.get("block_id", "UNKNOWN-BLOCK")
    level = section.get("heading_level", 2)
    heading_marks = "#" * max(2, min(int(level) if isinstance(level, int) else 2, 6))
    language = fence_language(block)
    content = str(block.get("content") or "").rstrip()

    lines = [
        f"{heading_marks} {title}",
        "",
        f"- Block ID: `{block_id}`",
        f"- Type: `{block.get('block_type', '')}`",
        f"- Status: `{block.get('status', '')}`",
        f"- Version: `{block.get('version', '')}`",
        f"- Heading ID: `{section.get('heading_id', '')}`",
        f"- Word style: `{section.get('word_style', '')}`",
        f"- Created from: `{lineage.get('created_from', '')}`",
        f"- Render targets: markdown={render.get('markdown', '')}, word={render.get('word', '')}, excel={render.get('excel', '')}, html={render.get('html', '')}",
        "",
        f"```{language}",
        content,
        "```",
        "",
    ]
    return lines


def render_preview(input_path: Path, output_path: Path) -> None:
    blocks = load_blocks(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CODEX Reusable Block Library Preview",
        "",
        "This file is generated from YAML SSOT block records.",
        "Do not treat this Markdown preview as the source of truth.",
        "",
        "Source of truth:",
        f"`{input_path}`",
        "",
        "---",
        "",
    ]
    for block in blocks:
        if isinstance(block, dict):
            lines.extend(render_block(block))
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render reusable block YAML to Markdown preview")
    parser.add_argument("input", nargs="?", default="ssot/blocks/sample_blocks.yaml")
    parser.add_argument("output", nargs="?", default="outputs/block_library_preview.md")
    args = parser.parse_args()
    render_preview(Path(args.input), Path(args.output))
    print(f"Wrote Markdown preview: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
