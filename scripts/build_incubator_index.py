#!/usr/bin/env python3
"""Build markdown index for incubator tuple files."""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.parse_chat_tuple import load_tuple_documents


def build_markdown() -> str:
    rows = [
        "# Incubator Index",
        "",
        "Machine-readable tuple ingress index for governed incubator records.",
        "",
        "| ID | Date | Time | Category | Theme | Title | Wave | Status | Source |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for item in load_tuple_documents():
        rows.append(
            "| {id} | {date} | {time_local} | {category} | {theme} | {title} | {wave} | {status} | {source_type} |".format(
                **item
            )
        )
    rows.extend(
        [
            "",
            "## Notes",
            "- Filename and tuple ID convention: `YY_Www_HH_MM__CATEGORY__THEME__TITLE__W###`",
            "- Regenerate with `python scripts/build_incubator_index.py`",
        ]
    )
    return "\n".join(rows) + "\n"


def main() -> None:
    output = REPO_ROOT / "docs" / "incubator_index.md"
    output.write_text(build_markdown(), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
