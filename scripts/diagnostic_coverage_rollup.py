#!/usr/bin/env python3
"""Advisory exact-SHA diagnostic coverage collector; no network or authority writes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SHA = re.compile(r"^[a-f0-9]{40}$")
STATUSES = {"MEASURED", "FAILED", "UNKNOWN", "HISTORICAL", "SKIPPED"}


def read(path: Path | None):
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path | None):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path else None


def evidence(value, name: str, source: str, path: Path | None):
    if not isinstance(value, dict):
        return {"status": "UNKNOWN", "reason": "missing_receipt", "source": name}
    bound = value.get("source_sha")
    if not SHA.fullmatch(str(bound or "")):
        return {"status": "UNKNOWN", "reason": "invalid_source_sha", "source": name,
                "input_sha256": digest(path)}
    if bound != source:
        return {"status": "HISTORICAL", "reason": "different_source_sha",
                "source_sha": bound, "source": name, "input_sha256": digest(path)}
    return {"status": "MEASURED", "source_sha": bound, "source": name,
            "input_sha256": digest(path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--quality", type=Path)
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--ldab", type=Path)
    parser.add_argument("--crew", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not SHA.fullmatch(args.source_sha):
        parser.error("source-sha must be a full 40-digit lowercase hexadecimal commit")
    checks = {}
    for key in ("quality", "runtime", "ldab", "crew"):
        path = getattr(args, key)
        checks[key] = evidence(read(path), key, args.source_sha, path)
    quality = read(args.quality)
    if checks["quality"]["status"] == "MEASURED":
        current = quality.get("current", {})
        diagnostics = quality.get("diagnostics", [])
        checks["quality"]["ruff_findings"] = sum(d.get("tool") == "ruff" for d in diagnostics)
        checks["quality"]["pyright_findings"] = sum(d.get("tool") == "pyright" for d in diagnostics)
        checks["quality"]["total_findings"] = current.get("total")
        # No scan-file coverage denominator exists in v1; do not infer one from findings.
        checks["quality"]["scanned_files"] = None
        checks["quality"]["eligible_files"] = None
    runtime = read(args.runtime)
    if checks["runtime"]["status"] == "MEASURED":
        outcomes = runtime.get("outcomes", {})
        if outcomes and all(v == "PASS" for v in outcomes.values()) and runtime.get("image_digest"):
            checks["runtime"]["status"] = "MEASURED"
            checks["runtime"]["passed_entrypoints"] = len(outcomes)
        else:
            checks["runtime"]["status"] = "FAILED"
            checks["runtime"]["reason"] = "missing_or_failed_entrypoints"
    for key in ("ldab", "crew"):
        if checks[key]["status"] == "MEASURED":
            value = read(getattr(args, key))
            if value.get("status") not in STATUSES:
                checks[key]["status"] = "UNKNOWN"
                checks[key]["reason"] = "missing_valid_status"
            else:
                checks[key]["status"] = value["status"]
    receipt = {
        "schema": "codex-diagnostic-coverage-rollup/v1",
        "source_sha": args.source_sha,
        "status": "ADVISORY",
        "coverage": checks,
        "metrics": {
            "verified_surfaces": sum(c["status"] == "MEASURED" for c in checks.values()),
            "eligible_surfaces": len(checks),
            "mean_queue_wait_seconds": None,
            "mean_worker_handling_seconds": None,
            "gm_authenticated_workers": None,
        },
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"source_sha": args.source_sha, "states": {
        k: v["status"] for k, v in checks.items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
