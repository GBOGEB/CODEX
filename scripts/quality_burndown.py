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


def canonical_path(raw, root):
    """Normalize absolute checkout paths, preserving repo-relative paths."""
    path = Path(raw)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def fingerprints(records):
    # Keep multiplicity but do not treat shifted line positions as fixed defects.
    # Rule and message remain diagnostic-specific; no cross-tool coalescing.
    return collections.Counter(
        json.dumps({k: r.get(k) for k in ("tool", "path", "rule", "message")}, sort_keys=True)
        for r in records
    )


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
    ap.add_argument("--ruff-scanned-files", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-sha", default="unknown")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args()
    if not args.ruff and not args.pyright:
        ap.error("at least one diagnostics input required")
    records = []
    source_hashes = {}
    for tool, path in (("ruff", args.ruff), ("pyright", args.pyright)):
        if path is not None:
            data = path.read_bytes()
            source_hashes[tool] = hashlib.sha256(data).hexdigest()
            scanned = normalise(json.loads(data), tool)
            for diagnostic in scanned:
                diagnostic["path"] = canonical_path(diagnostic["path"], args.repo_root)
            records.extend(scanned)
    counter = fingerprints(records)
    receipt = {
        "schema": "codex-quality-burndown/v1",
        "source_sha": args.source_sha,
        "input_sha256": source_hashes,
        "current": summarise(records),
        "diagnostics": sorted(records, key=lambda r: (r["tool"], r["path"], r["line"], r["rule"])),
        "admission": "advisory",
    }
    if args.ruff_scanned_files is not None:
        if args.ruff is None:
            ap.error("--ruff-scanned-files requires --ruff")
        raw = args.ruff_scanned_files.read_bytes()
        paths = [
            canonical_path(line.strip(), args.repo_root)
            for line in raw.decode("utf-8").splitlines() if line.strip()
        ]
        if not paths:
            raise ValueError("Ruff scan scope is empty; refusing zero coverage")
        receipt["scan_scope"] = {
            "ruff": {
                "scanned_files": len(set(paths)),
                "scope_sha256": hashlib.sha256(raw).hexdigest(),
                "duplicate_entries": len(paths) - len(set(paths)),
            },
            "pyright": None,
            "note": "Ruff denominator only; Pyright file coverage remains UNKNOWN",
        }
    if args.baseline:
        base = json.loads(args.baseline.read_text(encoding="utf-8"))
        baseline_records = base["diagnostics"]
        for diagnostic in baseline_records:
            diagnostic["path"] = canonical_path(diagnostic["path"], args.repo_root)
        previous = fingerprints(baseline_records)
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
