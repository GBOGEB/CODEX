from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gistau_ch15.properties.coolprop_state_grid import build_coolprop_state_grid_report


DEFAULT_OUTPUT = Path("docs/gistau-ch15/data/coolprop_state_grid_report.json")


def write_coolprop_state_grid_report(output_path: str | Path = DEFAULT_OUTPUT) -> list[dict[str, Any]]:
    """Build and write the CoolProp state-grid report.

    The helper is CI-safe because build_coolprop_state_grid_report returns
    explicit unavailable rows when CoolProp is not installed.
    """

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = build_coolprop_state_grid_report()
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return rows


def main() -> None:
    rows = write_coolprop_state_grid_report()
    available_flagged = sum(1 for row in rows if row.get("available"))
    print(
        f"wrote {len(rows)} CoolProp state-grid rows "
        f"({available_flagged} flagged available by CoolProp support)"
    )


if __name__ == "__main__":
    main()
