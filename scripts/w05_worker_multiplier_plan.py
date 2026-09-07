#!/usr/bin/env python3
"""Build a deterministic bounded worker plan for CODEX W05 logical-ID burn-down.

The scaling policy is defined by release/W05_P4_POWER2_SCALE_EXPERIMENT.yaml.
This utility does not mutate the logical-ID registry. It only creates uniquely
named discovery/mutation lanes so parallel workers can be dispatched without
sharing mutation ownership.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PARTITIONS = (
    "authority",
    "runtime_engines",
    "contracts",
    "schemas",
    "workflows",
    "products_views",
    "compatibility",
    "orphan_duplicate_qa",
)
POWER2 = {1, 2, 4, 8, 16, 32, 64}


def _validate_multiple(name: str, value: int) -> None:
    if value not in POWER2:
        raise ValueError(f"{name} must be one of {sorted(POWER2)}")


def build_plan(discovery: int = 16, mutation: int = 8) -> dict:
    _validate_multiple("discovery", discovery)
    _validate_multiple("mutation", mutation)
    if mutation > discovery:
        raise ValueError("mutation multiple cannot exceed discovery multiple")

    discovery_workers = []
    for index in range(discovery):
        partition = PARTITIONS[index % len(PARTITIONS)]
        replica = index // len(PARTITIONS) + 1
        discovery_workers.append(
            {
                "worker_id": f"W05-D-{partition.upper()}-{replica:02d}",
                "mode": "discovery",
                "partition": partition,
                "registry_write": False,
                "three_pr_sue": 3,
            }
        )

    mutation_workers = []
    for index in range(mutation):
        partition = PARTITIONS[index % len(PARTITIONS)]
        replica = index // len(PARTITIONS) + 1
        mutation_workers.append(
            {
                "worker_id": f"W05-M-{partition.upper()}-{replica:02d}",
                "mode": "mutation_candidate",
                "partition": partition,
                "registry_write": False,
                "three_pr_sue": 3,
            }
        )

    return {
        "schema": "codex-w05-worker-multiplier-plan/v1",
        "source_policy": "release/W05_P4_POWER2_SCALE_EXPERIMENT.yaml",
        "job": "governed_logical_id_burndown",
        "discovery_multiple_3pr": discovery,
        "mutation_multiple_3pr": mutation,
        "discovery_sue_capacity": discovery * 3,
        "mutation_sue_capacity": mutation * 3,
        "single_writer_registry": True,
        "workers": discovery_workers + mutation_workers,
        "mutation_commit_rule": (
            "workers propose non-overlapping path-to-logical-ID bindings; only the "
            "single registry writer may commit accepted bindings after collision checks"
        ),
        "reverse_pressure": {
            "minimum_queue_per_sue": 1.5,
            "maximum_rework_fraction": 0.10,
            "maximum_collision_count": 0,
            "maximum_speed_per_sue_degradation_fraction": 0.20,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery", type=int, default=16)
    parser.add_argument("--mutation", type=int, default=8)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    try:
        plan = build_plan(args.discovery, args.mutation)
    except ValueError as exc:
        parser.error(str(exc))

    payload = json.dumps(plan, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
