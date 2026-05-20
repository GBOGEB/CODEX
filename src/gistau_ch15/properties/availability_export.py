from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gistau_ch15.properties.backend_selector import availability_report_rows


DEFAULT_OUTPUT = Path("docs/gistau-ch15/data/backend_availability.json")


def write_backend_availability(path: str | Path = DEFAULT_OUTPUT) -> list[dict[str, Any]]:
    """Write backend availability rows for GitHub Pages review artifacts."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = availability_report_rows()
    output_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return rows


if __name__ == "__main__":
    write_backend_availability()
