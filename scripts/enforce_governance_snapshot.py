"""Enforce the exact-head governance snapshot after evidence-producing CI steps.

The emitter is intentionally non-failing so downstream artifacts can be collected.
This separate native verdict must fail closed on any missing, stale or failed check.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def validate(report: object, sha: str, required: list[str]) -> list[str]:
    problems = []
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        problems.append("invalid expected source SHA")
    if not isinstance(report, dict):
        return problems + ["missing or invalid governance snapshot object"]
    if report.get("sha") != sha:
        problems.append("snapshot SHA does not match exact CI head")
    if report.get("status") != "passed":
        problems.append("snapshot verdict is not passed")
    checks = report.get("checks")
    if not isinstance(checks, list):
        return problems + ["missing check population"]
    names = [x.get("name") if isinstance(x, dict) else None for x in checks]
    if len(names) != len(set(names)) or not all(isinstance(n, str) and n for n in names):
        problems.append("duplicate or malformed check identity")
    if len(required) != len(set(required)) or not required:
        problems.append("invalid expected check population")
    if set(names) != set(required):
        problems.append("snapshot check population differs from required checks")
    if any(not isinstance(x, dict) or x.get("status") != "passed" or x.get("passed") is not True for x in checks):
        problems.append("mandatory check is missing, skipped, failed or inconsistent")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--sha", required=True)
    ap.add_argument("--required", nargs="+", required=True)
    a = ap.parse_args(argv)
    try:
        report = json.loads(a.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"governance RED: missing or unreadable snapshot: {type(exc).__name__}")
        return 1
    problems = validate(report, a.sha, a.required)
    if problems:
        for problem in problems:
            print(f"governance RED: {problem}")
        return 1
    print("governance PASS: exact-head required-check population valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
