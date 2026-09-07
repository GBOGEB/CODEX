#!/usr/bin/env python3
"""Fail-closed power-of-two controller for CODEX ID discovery pulses."""
from __future__ import annotations
import argparse, json

LEVELS = (1, 2, 4, 8, 16, 32, 64)

def decide(current: int, queue: int, active_workers: int, rework_rate: float,
           collisions: int, speed_per_sue: float | None,
           baseline_speed_per_sue: float | None) -> dict:
    if current not in LEVELS:
        raise ValueError("current workers must be a power of two from 1..64")
    effective_sue = max(active_workers * 3, 1)
    q_per_sue = queue / effective_sue
    utilization = active_workers / current if current else 0.0
    degradation = None
    if speed_per_sue is not None and baseline_speed_per_sue not in (None, 0):
        degradation = 1.0 - (speed_per_sue / baseline_speed_per_sue)

    idx = LEVELS.index(current)
    next_workers = current
    action = "HOLD"
    reasons = []

    # Immediate reverse pressure on correctness or material efficiency failure.
    if collisions > 0 or rework_rate >= 0.10 or (degradation is not None and degradation > 0.20):
        next_workers = LEVELS[max(0, idx - 1)]
        action = "RAMP_DOWN"
        reasons.append("correctness_or_efficiency_guard")
    # Runner starvation: adding requested workers cannot create effective capacity.
    elif utilization < 0.50:
        next_workers = LEVELS[max(0, idx - 1)] if current > 1 else 1
        action = "RAMP_DOWN" if next_workers < current else "HOLD"
        reasons.append("runner_capacity_starved")
    # Queue too shallow for current effective SUE.
    elif q_per_sue < 1.0:
        next_workers = LEVELS[max(0, idx - 1)]
        action = "RAMP_DOWN"
        reasons.append("queue_shallow")
    # Promotion requires queue headroom and clean execution.
    elif q_per_sue >= 1.5 and utilization >= 0.80 and collisions == 0 and rework_rate < 0.10 and (degradation is None or degradation <= 0.20):
        next_workers = LEVELS[min(len(LEVELS) - 1, idx + 1)]
        action = "RAMP_UP" if next_workers > current else "HOLD"
        reasons.append("promotion_gate_pass")
    else:
        reasons.append("hold_band")

    return {
        "schema_version": "1.0",
        "current_workers": current,
        "current_sue": current * 3,
        "active_workers": active_workers,
        "effective_sue": active_workers * 3,
        "queue": queue,
        "queue_per_effective_sue": round(q_per_sue, 4),
        "runner_utilization": round(utilization, 4),
        "rework_rate": rework_rate,
        "collisions": collisions,
        "speed_per_sue": speed_per_sue,
        "baseline_speed_per_sue": baseline_speed_per_sue,
        "speed_degradation": None if degradation is None else round(degradation, 4),
        "action": action,
        "next_workers": next_workers,
        "next_sue": next_workers * 3,
        "reasons": reasons,
        "authority_mutation": "SERIALIZED_OUTSIDE_DISCOVERY_WORKERS",
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--current", type=int, required=True)
    p.add_argument("--queue", type=int, required=True)
    p.add_argument("--active-workers", type=int, required=True)
    p.add_argument("--rework-rate", type=float, default=0.0)
    p.add_argument("--collisions", type=int, default=0)
    p.add_argument("--speed-per-sue", type=float)
    p.add_argument("--baseline-speed-per-sue", type=float)
    args = p.parse_args()
    print(json.dumps(decide(args.current, args.queue, args.active_workers,
                            args.rework_rate, args.collisions,
                            args.speed_per_sue, args.baseline_speed_per_sue), indent=2))

if __name__ == "__main__":
    main()
