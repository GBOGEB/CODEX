#!/usr/bin/env python3
"""Work-conserving scheduler for CODEX ID/release microtasks.

Policy goals:
- reuse one coordinator for PRE + POST;
- keep execution workers in a shared pool across pulses;
- do not use FIFO/LIFO as the governing policy;
- maximize expected convergence gain per unit remaining time;
- prevent starvation with age/deadline escalation;
- only preempt work at declared resumable checkpoints.

The scheduler is advisory/execution-control only. It cannot mutate engineering or
SSOT authority by itself.
"""
from __future__ import annotations
import argparse, json, math, time
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Item:
    id: str
    state: str = "QUEUED"
    est_remaining_s: float = 1.0
    convergence_gain: float = 1.0
    stability_gain: float = 0.0
    unblock_gain: float = 0.0
    age_s: float = 0.0
    max_queue_s: float = 300.0
    resumable: bool = True
    setup_affinity: str = "default"
    checkpoint_cost_s: float = 0.0

    def urgency(self) -> float:
        if self.max_queue_s <= 0:
            return 1.0
        ratio = self.age_s / self.max_queue_s
        # Gentle aging early; hard escalation as the queue deadline is approached.
        return min(8.0, 1.0 + ratio * ratio * 4.0)

    def value_density(self, affinity_bonus: float = 0.0) -> float:
        useful = self.convergence_gain + 0.5 * self.stability_gain + 0.75 * self.unblock_gain
        cost = max(1e-6, self.est_remaining_s + self.checkpoint_cost_s)
        return (useful / cost) * self.urgency() * (1.0 + affinity_bonus)


def choose(items: list[Item], free_slots: int, active_affinities: set[str] | None = None) -> list[Item]:
    active_affinities = active_affinities or set()
    queued = [x for x in items if x.state == "QUEUED"]
    # Deadline breach always outranks efficiency score, then use value-density.
    def key(x: Item):
        overdue = x.age_s >= x.max_queue_s if x.max_queue_s > 0 else False
        affinity_bonus = 0.10 if x.setup_affinity in active_affinities else 0.0
        return (1 if overdue else 0, x.value_density(affinity_bonus), x.age_s)
    return sorted(queued, key=key, reverse=True)[:max(0, free_slots)]


def squeeze_candidate(items: list[Item], available_window_s: float, active_affinities: set[str] | None = None) -> Item | None:
    """Return useful queued work that can fit before a longer dependency/job completes."""
    fits = [x for x in items if x.state == "QUEUED" and x.est_remaining_s <= available_window_s]
    selected = choose(fits, 1, active_affinities)
    return selected[0] if selected else None


def preemption_candidate(running: list[Item], queued: list[Item]) -> tuple[Item, Item] | None:
    """Cooperative preemption only: replace low-value resumable work at checkpoints."""
    if not queued:
        return None
    incoming = choose(queued, 1)
    if not incoming:
        return None
    target = min((x for x in running if x.resumable), key=lambda x: x.value_density(), default=None)
    if target is None:
        return None
    # Require material gain to avoid thrash.
    if incoming[0].value_density() > target.value_density() * 1.5:
        return target, incoming[0]
    return None


def summarize(items: list[Item], pool_size: int, coordinator_slots: int = 1) -> dict:
    queued = [x for x in items if x.state == "QUEUED"]
    running = [x for x in items if x.state == "RUNNING"]
    ages = [x.age_s for x in queued]
    return {
        "schema_version": "1.0",
        "scheduler": "WORK_CONSERVING_NON_FIFO_WITH_AGING",
        "pool": {
            "total_slots": pool_size,
            "coordinator_slots": coordinator_slots,
            "execution_slots": max(0, pool_size - coordinator_slots),
            "pre_post_same_coordinator": True,
            "workers_reusable_across_pulses": True,
        },
        "queue_depth": len(queued),
        "running_depth": len(running),
        "max_queue_age_s": max(ages) if ages else 0.0,
        "p50_queue_age_s": sorted(ages)[len(ages)//2] if ages else 0.0,
        "overdue_count": sum(1 for x in queued if x.max_queue_s > 0 and x.age_s >= x.max_queue_s),
        "authority_mutation": "SERIALIZED_OUTSIDE_WORKER_POOL",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--queue-json", required=True)
    p.add_argument("--pool-size", type=int, default=5)
    p.add_argument("--free-slots", type=int, default=4)
    p.add_argument("--squeeze-window-s", type=float)
    args = p.parse_args()
    raw = json.loads(Path(args.queue_json).read_text(encoding="utf-8"))
    items = [Item(**row) for row in raw.get("items", [])]
    out = summarize(items, args.pool_size)
    out["dispatch"] = [asdict(x) for x in choose(items, args.free_slots)]
    if args.squeeze_window_s is not None:
        sq = squeeze_candidate(items, args.squeeze_window_s)
        out["squeeze"] = asdict(sq) if sq else None
    print(json.dumps(out, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
