#!/usr/bin/env python3
"""Ruff ratchet: the lint count on the checked tree may never rise above the committed baseline.

Usage::

    python scripts/ruff_ratchet.py [--baseline ci/ruff_baseline.json] [--ruff ruff]

ruff was report-only (``continue-on-error``) while the governance snapshot listed it as mandatory, so every
run of ``CI`` was red on the 1,400-odd violations that predate the pin. The ratchet keeps ruff mandatory for
new violations without demanding the whole backlog first:

* exit 0  the count is at or below ``max_violations``; a lower count prints the new value to commit.
* exit 1  the count rose: the new violations are listed.
* exit 3  UNKNOWN: ruff is not the pinned version, or its output cannot be read. Never a pass.

Paths resolve from the repository root, so the working directory does not matter. ASCII output only.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "ci" / "ruff_baseline.json"
EXIT_ROSE = 1
EXIT_UNKNOWN = 3


def run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--ruff", default="ruff", help="ruff executable")
    args = parser.parse_args(argv)
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    pinned, ceiling, scope = baseline["ruff_version"], int(baseline["max_violations"]), baseline["args"]

    code, out, err = run([args.ruff, "--version"])
    version = out.strip().split()[-1] if code == 0 and out.strip() else None
    if version != pinned:
        print(f"RUFF_RATCHET UNKNOWN: ruff {version} is not the pinned {pinned}", file=sys.stderr)
        return EXIT_UNKNOWN
    code, out, err = run([args.ruff, "check", *scope, "--output-format", "json", "--exit-zero"])
    try:
        findings = json.loads(out)
        assert code == 0 and isinstance(findings, list)
    except (ValueError, AssertionError):
        print(f"RUFF_RATCHET UNKNOWN: ruff exited {code}; output unreadable. {err.strip()[:300]}", file=sys.stderr)
        return EXIT_UNKNOWN

    count = len(findings)
    print("RUFF_RATCHET " + json.dumps({"count": count, "max_violations": ceiling, "ruff": version,
                                         "args": scope}, sort_keys=True))
    if count > ceiling:
        for item in findings[:200]:
            where = Path(item.get("filename", "?"))
            where = where.relative_to(ROOT) if where.is_absolute() and ROOT in where.parents else where
            row = (item.get("location") or {}).get("row", "?")
            print(f"  {where}:{row} {item.get('code')} {item.get('message', '')}"[:200])
        print(f"FAIL: ruff found {count} violations, above the baseline {ceiling}. Fix the new ones; "
              "the ratchet never rises.", file=sys.stderr)
        return EXIT_ROSE
    if count < ceiling:
        print(f"OK: {count} <= {ceiling}. Lower max_violations in {args.baseline.name} to {count} "
              "to lock in the improvement.")
    else:
        print(f"OK: {count} == {ceiling}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
