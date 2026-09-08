#!/usr/bin/env python3
"""Execute balanced CODEX ID-burndown packets as logical workers on one runner.

The pool consumes the immutable work_plan produced by the canonical census.
Workers emit append-only discovery receipts only; authority mutation is forbidden.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import statistics
import time
from pathlib import Path

ALLOWED = {1, 2, 4, 8, 16, 32, 64}


def spread(values: list[int | float]) -> float:
    if not values or max(values) == 0:
        return 0.0
    return round((max(values) - min(values)) / max(values), 4)


def consume(bucket: dict, workers: int, out_dir: Path) -> dict:
    shard = int(bucket["shard"])
    started = time.perf_counter_ns()
    # Discovery work is deliberately read-only. This loop is the extension point
    # for candidate-specific normalization/probes; registry writes stay serialized.
    candidates = list(bucket["items"])
    elapsed = time.perf_counter_ns() - started
    receipt = {
        "schema_version": "4.0",
        "purpose": "CODEX_ID_BURNDOWN_DISCOVERY_RECEIPT",
        "execution_transport": "LOCAL_LOGICAL_POOL",
        "workers": workers,
        "sue": workers * 3,
        "shard": shard,
        "queue": None,
        "assigned_count": len(candidates),
        "assigned_weight": bucket["weight"],
        "elapsed_ns": elapsed,
        "candidates": candidates,
        "authority_mutation": "FORBIDDEN",
    }
    path = out_dir / f"receipt-{shard:02d}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="reports/id_burndown/work_plan.json")
    ap.add_argument("--out-dir", default="reports/id_burndown/local-receipts")
    ap.add_argument("--physical-slots", type=int, default=0,
                    help="threads used on this runner; 0=auto bounded by logical workers")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    workers = int(plan["workers"])
    if workers not in ALLOWED:
        raise SystemExit(f"unsupported logical worker count: {workers}")
    bins = list(plan["bins"])
    if len(bins) != workers:
        raise SystemExit(f"plan bin count {len(bins)} != workers {workers}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slots = args.physical_slots or workers
    slots = max(1, min(slots, workers))
    wall_start = time.perf_counter_ns()
    with concurrent.futures.ThreadPoolExecutor(max_workers=slots) as pool:
        receipts = list(pool.map(lambda b: consume(b, workers, out_dir), bins))
    wall_ns = time.perf_counter_ns() - wall_start

    for r in receipts:
        r["queue"] = int(plan["queue"])
        p = out_dir / f"receipt-{int(r['shard']):02d}.json"
        p.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")

    counts = [r["assigned_count"] for r in receipts]
    weights = [r["assigned_weight"] for r in receipts]
    elapsed = [r["elapsed_ns"] for r in receipts]
    stats = {
        "schema_version": "1.0",
        "execution_transport": "LOCAL_LOGICAL_POOL",
        "logical_workers": workers,
        "physical_slots": slots,
        "sue": workers * 3,
        "queue": int(plan["queue"]),
        "queue_per_sue": round(int(plan["queue"]) / (workers * 3), 4),
        "completed_workers": len(receipts),
        "count_skew": spread(counts),
        "weight_skew": spread(weights),
        "processing_time_skew": spread(elapsed),
        "processing_ns_p50": int(statistics.median(elapsed)) if elapsed else 0,
        "processing_ns_max": max(elapsed) if elapsed else 0,
        "wall_ns": wall_ns,
        "authority_mutation": "FORBIDDEN",
    }
    (out_dir / "pool_stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print("ID_LOCAL_POOL_PASS " + json.dumps(stats, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
