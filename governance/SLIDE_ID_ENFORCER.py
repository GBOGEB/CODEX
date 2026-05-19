from __future__ import annotations

import re
import sys
from pathlib import Path

ID_PATTERN = re.compile(r"^MSLIDE_[A-Z0-9_]+_\d{2}$")


def validate(path: str) -> int:
    lines = Path(path).read_text().splitlines()
    bad: list[str] = []
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("slide_id:"):
            value = line.split(":", 1)[1].strip()
            if not ID_PATTERN.match(value):
                bad.append(f"{path}:{i} invalid slide_id '{value}'")

    if bad:
        print("\n".join(bad))
        return 1

    print(f"PASS: slide_id format valid in {path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python governance/SLIDE_ID_ENFORCER.py <yaml-file>")
        raise SystemExit(2)
    raise SystemExit(validate(sys.argv[1]))
