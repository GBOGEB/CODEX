#!/usr/bin/env python3
"""Read-only exact-head coverage census validator; no network or repository mutations."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
ALLOWED = {"MEASURED", "DERIVED_FROM_MEASURED", "WITHHELD"}
POPULATIONS = ("statement", "branch", "diff", "ruff_files", "pyright_files", "pipeline_outputs", "ldab_live_sessions", "dod", "dov")


def verify(data: dict) -> dict:
    errors: list[str] = []
    repo = data.get("repository")
    head = data.get("head_sha")
    if not isinstance(repo, str) or "/" not in repo:
        errors.append("repository is required as owner/name")
    if not isinstance(head, str) or not SHA.fullmatch(head):
        errors.append("head_sha must be a 40-hex commit SHA")
    rows = data.get("populations", {})
    if not isinstance(rows, dict):
        rows = {}
        errors.append("populations must be an object")
    result = {}
    for name in POPULATIONS:
        row = rows.get(name)
        if row is None:
            result[name] = {"status": "WITHHELD", "percent": None, "reason": "no census evidence"}
            continue
        if not isinstance(row, dict):
            errors.append(f"{name}: expected object")
            continue
        status = row.get("status", "WITHHELD")
        num, den = row.get("numerator"), row.get("denominator")
        run, source_sha = row.get("run_id"), row.get("source_sha")
        if status not in ALLOWED:
            errors.append(f"{name}: invalid status")
            continue
        if status == "WITHHELD":
            if num is not None or den is not None:
                errors.append(f"{name}: withheld cannot supply numerical claims")
            result[name] = {"status": "WITHHELD", "percent": None, "reason": row.get("reason", "evidence withheld")}
            continue
        if any(type(x) is not int for x in (num, den)) or not (0 <= num <= den and den > 0):
            errors.append(f"{name}: invalid numerator/denominator")
            continue
        if not isinstance(source_sha, str) or source_sha != head:
            errors.append(f"{name}: stale/mismatched exact-head source")
            continue
        if type(run) is not int or run <= 0:
            errors.append(f"{name}: observed run_id required")
            continue
        if name in ("pipeline_outputs", "ldab_live_sessions", "dov") and not DIGEST.fullmatch(str(row.get("receipt_sha256") or "")):
            errors.append(f"{name}: valid 64-digit receipt SHA-256 required")
            continue
        result[name] = {"status": status, "numerator": num, "denominator": den, "percent": round(num / den * 100, 2), "run_id": run, "source_sha": source_sha}
    return {"schema": "code-purple.disjoint-census-validation.v1", "repository": repo, "head_sha": head, "valid": not errors, "errors": errors, "populations": result}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = verify(json.loads(args.input.read_text(encoding="utf-8")))
    body = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
