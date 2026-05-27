#!/usr/bin/env python3
"""Build markdown index for incubator tuple files."""

from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = root / "scripts" / "parse_chat_tuple.py"
    result = subprocess.check_output(["python3", str(parser), str(root / "incubator")], text=True)

    import json

    items = json.loads(result)
    out = ["# Incubator Index", "", "| id | date | category | theme | status |", "|---|---|---|---|---|"]
    for item in items:
        out.append(
            f"| {item.get('id','')} | {item.get('date','')} | {item.get('category','')} | {item.get('theme','')} | {item.get('status','')} |"
        )

    output = root / "docs" / "incubator_index.md"
    output.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
