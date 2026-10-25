"""Compute exact-base changed executable-line coverage from coverage.py XML.

A measured zero denominator is reported as N/A, never as 100% coverage.

When the base resolves to HEAD itself (for example a push to main, where
``merge-base HEAD origin/main`` is HEAD) there is no changed-line diff to
measure, so the result is ``NOT_MEASURED`` rather than a false failure.

The admission target is owner policy and is REPORT-ONLY: ``--target`` (or the
``CHANGED_LINE_COVERAGE_TARGET`` environment variable, default 80 from the
source branch) is recorded and compared, but this script never exits non-zero
because a percentage is below it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_TARGET = 80.0  # owner policy; value taken from repair/20261013-postmerge-ruff-i001


def _not_measured(commit: str, base: str, reason: str) -> dict:
    return {
        "schema": "changed-line-coverage/1",
        "exact_sha": commit,
        "base_sha": base,
        "eligible_lines": 0,
        "covered_lines": 0,
        "percent": None,
        "status": "NOT_MEASURED",
        "reason": reason,
        "missing_source_files": [],
        "uncovered": [],
    }


def measure(xml: Path, base: str, root: Path) -> dict:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if not base or base == commit:
        return _not_measured(commit, base, "EMPTY_BASE_DIFF: base is HEAD (e.g. push to main)")
    diff = subprocess.check_output(
        ["git", "diff", "--unified=0", f"{base}...HEAD", "--", "*.py"],
        cwd=root, text=True,
    )
    changes: dict[str, set[int]] = {}
    path = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("@@ ") and path:
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start = int(match.group(1))
                count = int(match.group(2) or "1")
                changes.setdefault(path, set()).update(range(start, start + count))
    tree = ET.parse(xml)
    eligible, covered = set(), set()
    observed_paths: set[str] = set()
    for cls in tree.findall(".//class"):
        filename = cls.get("filename", "")
        candidates = [filename, f"src/{filename}", f"scripts/{filename}", f"tests/{filename}"]
        matches = sorted({x for x in candidates if x in changes})
        if len(matches) > 1:
            raise ValueError(f"Ambiguous coverage source path: {filename}: {matches}")
        matched = matches[0] if matches else None
        if matched is None:
            continue
        observed_paths.add(matched)
        for element in cls.findall("./lines/line"):
            number = int(element.get("number", "0"))
            if number in changes[matched]:
                eligible.add((matched, number))
                if int(element.get("hits", "0")) > 0:
                    covered.add((matched, number))
    missing_source_files = sorted(set(changes) - observed_paths)
    total = len(eligible)
    return {
        "schema": "changed-line-coverage/1",
        "exact_sha": commit,
        "base_sha": base,
        "eligible_lines": total,
        "covered_lines": len(covered),
        "percent": round(100 * len(covered) / total, 2) if total and not missing_source_files else None,
        "status": "INCOMPLETE_INSTRUMENTATION" if missing_source_files else ("MEASURED" if total else "NO_ELIGIBLE_CHANGED_LINES"),
        "missing_source_files": missing_source_files,
        "uncovered": [f"{p}:{n}" for p, n in eligible if (p, n) not in set(covered)],
    }


def evaluate(result: dict, target: float) -> dict:
    """Report-only comparison against the owner-policy target. Never raises."""
    percent = result.get("percent")
    if result.get("status") != "MEASURED" or percent is None:
        verdict = "SKIPPED"
    elif percent >= target:
        verdict = "AT_OR_ABOVE_TARGET"
    else:
        verdict = "BELOW_TARGET"
    return {"target_percent": target, "verdict": verdict, "enforcement": "REPORT_ONLY"}


def _target_from_env() -> float:
    raw = os.environ.get("CHANGED_LINE_COVERAGE_TARGET", "").strip()
    try:
        return float(raw) if raw else DEFAULT_TARGET
    except ValueError:
        return DEFAULT_TARGET


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("coverage_xml", type=Path)
    parser.add_argument("base_sha")
    parser.add_argument("out_json", type=Path)
    parser.add_argument("--target", type=float, default=None,
                        help="owner-policy target percent (report-only)")
    args = parser.parse_args(argv)
    result = measure(args.coverage_xml, args.base_sha, Path.cwd())
    target = args.target if args.target is not None else _target_from_env()
    result["admission"] = evaluate(result, target)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
