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
    parser.add_argument("--coverage", type=Path)
    parser.add_argument("--queue", type=Path)
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
    coverage_input = read(args.coverage)
    if isinstance(coverage_input, dict):
        scanned = coverage_input.get("scanned_files")
        eligible = coverage_input.get("eligible_files")
        if (isinstance(scanned, int) and not isinstance(scanned, bool)
                and isinstance(eligible, int) and not isinstance(eligible, bool)
                and 0 <= scanned <= eligible and eligible > 0
                and coverage_input.get("source_sha") == args.source_sha):
            checks["quality"]["scanned_files"] = scanned
            checks["quality"]["eligible_files"] = eligible
            checks["quality"]["scan_coverage_pct"] = round(100 * scanned / eligible, 2)
    queue_input = read(args.queue)
    queue_metrics = {"observed_jobs": 0, "queue_depth": None,
                     "mean_queue_wait_seconds": None,
                     "mean_worker_handling_seconds": None}
    if isinstance(queue_input, dict) and queue_input.get("source_sha") == args.source_sha:
        rows = queue_input.get("jobs")
        if isinstance(rows, list):
            import datetime
            def seconds(start, end):
                if not isinstance(start, str) or not isinstance(end, str):
                    return None
                try:
                    x = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
                    y = datetime.datetime.fromisoformat(end.replace("Z", "+00:00"))
                    result = (y - x).total_seconds()
                    return result if result >= 0 else None
                except ValueError:
                    return None
            waits = [seconds(j.get("queued_at"), j.get("started_at"))
                     for j in rows if isinstance(j, dict)]
            durations = [seconds(j.get("started_at"), j.get("completed_at"))
                         for j in rows if isinstance(j, dict)]
            waits = [v for v in waits if v is not None]
            durations = [v for v in durations if v is not None]
            queue_metrics = {
                "observed_jobs": len(rows),
                "queue_depth": sum(j.get("status") == "queued" for j in rows
                                   if isinstance(j, dict)),
                "mean_queue_wait_seconds": round(sum(waits) / len(waits), 2) if waits else None,
                "mean_worker_handling_seconds": round(sum(durations) / len(durations), 2)
                                                if durations else None,
                "wait_samples": len(waits), "handling_samples": len(durations),
            }
    receipt = {
        "schema": "codex-diagnostic-coverage-rollup/v1",
        "source_sha": args.source_sha,
        "status": "ADVISORY",
        "coverage": checks,
        "metrics": {
            "verified_surfaces": sum(c["status"] == "MEASURED" for c in checks.values()),
            "eligible_surfaces": len(checks),
            **queue_metrics,
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
