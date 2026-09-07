#!/usr/bin/env python3
"""Validate the current CODEX release identity without promoting the next major."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"RELEASE_IDENTITY_FAIL: {message}")


def main() -> int:
    version_data = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
    canonical = str(version_data.get("version") or "").strip()
    if not canonical:
        fail("VERSION.json has no version")

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', pyproject, re.MULTILINE)
    if not match:
        fail("pyproject.toml project version not found")
    package = match.group(1)

    if package != canonical:
        fail(f"VERSION.json={canonical} pyproject.toml={package}")

    print(f"RELEASE_IDENTITY_PASS version={canonical} authority=VERSION.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
