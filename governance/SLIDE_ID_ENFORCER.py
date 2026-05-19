from __future__ import annotations

import re
import sys
from pathlib import Path

ID_PATTERN = re.compile(r"^MSLIDE_[A-Z0-9_]+_\d{2}$")


def _normalize_value(raw: str) -> str:
    value = raw.split("#", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def validate(path: str) -> int:
    lines = Path(path).read_text().splitlines()
    bad: list[str] = []
    found = 0
    for i, line in enumerate(lines, start=1):
        if re.match(r"^\s*slide_id\s*:", line):
            found += 1
            value = _normalize_value(line.split(":", 1)[1])
            if not ID_PATTERN.match(value):
                bad.append(f"{path}:{i} invalid slide_id '{value}'")
    if found == 0:
        print(f"{path}: no slide_id entries found")
        return 1

    if bad:
        print("\n".join(bad))
        return 1

    print(f"PASS: slide_id format valid in {path} ({found} entries)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python governance/SLIDE_ID_ENFORCER.py <yaml-file>")
        raise SystemExit(2)
    raise SystemExit(validate(sys.argv[1]))
