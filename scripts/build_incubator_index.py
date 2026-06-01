#!/usr/bin/env python3
"""Build markdown index for incubator tuple files."""

from __future__ import annotations

import subprocess
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


def build_markdown() -> str:
    """Return a Markdown string indexing all incubator tuple documents.

    The output includes:
    - A top-level ``# Incubator Index`` heading with a brief description.
    - A Markdown table of all tuple files with columns
      ``ID | Date | Time | Category | Theme | Title | Wave | Status | Source``.
    - A ``## Notes`` section documenting the filename convention and CLI usage.

    Returns:
        Markdown-formatted index string.
    """
    import sys
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

    from scripts.parse_chat_tuple import load_tuple_documents

    docs = load_tuple_documents()

    lines: list[str] = [
        "# Incubator Index",
        "",
        "Machine-readable tuple ingress index for the CODEX INCUBATOR program wave.",
        "",
        "| ID | Date | Time | Category | Theme | Title | Wave | Status | Source |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for doc in docs:
        row = "| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            doc.get("id", ""),
            doc.get("date", ""),
            doc.get("time_local", ""),
            doc.get("category", ""),
            doc.get("theme", ""),
            doc.get("title", ""),
            doc.get("wave", ""),
            doc.get("status", ""),
            doc.get("source_type", ""),
        )
        lines.append(row)

    lines += [
        "",
        "## Notes",
        "",
        "Filename convention: `YY_Www_HH_MM__CATEGORY__THEME__TITLE__W###.yml`",
        "",
        "To regenerate this index:",
        "```",
        "python scripts/build_incubator_index.py",
        "```",
    ]

    return "\n".join(lines) + "\n"


def main() -> None:
    root = _REPO_ROOT
    output = root / "docs" / "incubator_index.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_markdown(), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

