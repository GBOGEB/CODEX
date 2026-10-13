#!/usr/bin/env python3
"""Compare Ruff/Pyright diagnostics without silently transferring quality credit."""
import argparse
import collections
import hashlib
import json
from pathlib import Path


def normalise(report, engine):
    if engine == "ruff":
        entries = report if isinstance(report, list) else report.get("diagnostics", [])
        return [{"tool": engine, "path": str(x.get("filename", "")),
                 "rule": str(x.get("code", "unknown")),
                 "message": str(x.get("message", "")),
                 "line": (x.get("location") or {}).get("row", 0)}
                for x in entries]
    entries = report.get("generalDiagnostics", [])
    return [{"tool": engine, "path": str(x.get("file", "")),
             "rule": str(x.get("rule") or x.get("severity") or "unknown"),
             "message": str(x.get("message", "")),
             "line": ((x.get("range") or {}).get("start") or {}).get("line", -1) + 1}
            for x in entries]


def fingerprints(records):
    # A multiset preserves distinct occurrences without losing duplicate diagnostics.
    return collections.Counter(json.dumps(r, sort_keys=True) for r in records)


def summarise(records):
    return {
        "total": len(records),
        "by_rule": dict(sorted(collections.Counter(
            f'{x["tool"]}:{x["rule"]}' for x in records).items())),
        "by_file": dict(sorted(collections.Counter(x["path"] for x in records).items())),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruff", type=Path)
    ap.add_argument("--pyright", type=Path)
    ap.add_argument("--baseline", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-sha", default="unknown")
    args = ap.parse_args()
    if not args.ruff and not args.pyright:
        ap.error("at least one diagnostics input required")
    records = []
    source_hashes = {}
    for tool, path in (("ruff", args.ruff), ("pyright", args.pyright)):
        if path is not None:
            data = path.read_bytes()
            source_hashes[tool] = hashlib.sha256(data).hexdigest()
            records.extend(normalise(json.loads(data), tool))
    counter = fingerprints(records)
    receipt = {
        "schema": "codex-quality-burndown/v1",
        "source_sha": args.source_sha,
        "input_sha256": source_hashes,
        "current": summarise(records),
        "diagnostics": sorted(records, key=lambda r: (r["tool"], r["path"], r["line"], r["rule"])),
        "admission": "advisory",
    }
    if args.baseline:
        base = json.loads(args.baseline.read_text(encoding="utf-8"))
        previous = fingerprints(base["diagnostics"])
        receipt["comparison"] = {
            "baseline_source_sha": base.get("source_sha", "unknown"),
            "new": sum((counter - previous).values()),
            "resolved": sum((previous - counter).values()),
            "net_reduction": sum(previous.values()) - sum(counter.values()),
            "baseline_total": sum(previous.values()),
            "same_source": base.get("source_sha") == args.source_sha,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("source_sha", "current", "admission")},
                     sort_keys=True))


if __name__ == "__main__":
    main()
