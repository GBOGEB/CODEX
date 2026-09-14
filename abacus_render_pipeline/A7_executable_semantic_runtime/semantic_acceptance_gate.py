from __future__ import annotations

import json
from typing import Any, Dict

from closed_loop import run as run_closed_loop
from semantic_delta_replay import run as run_replay


def evaluate(render_validation_passed: bool = True) -> Dict[str, Any]:
    closed_loop = run_closed_loop()
    replay = run_replay()

    checks = {
        "render_validation_passed": bool(render_validation_passed),
        "schema_parentage_reconstruction_dag_completeness_passed": closed_loop["status"] == "PASS",
        "semantic_delta_replay_passed": replay["status"] == "PASS",
        "replay_ready": bool(closed_loop["runtime"]["state"]["replay_ready"]),
        "traceable_tuple_count": closed_loop["completeness"]["tuple_count"] >= 8,
    }

    promotions_allowed = all(checks.values())
    return {
        "status": "PASS" if promotions_allowed else "FAIL",
        "semantic_promotions_allowed": promotions_allowed,
        "checks": checks,
        "closed_loop_summary": {
            "tuple_count": closed_loop["completeness"]["tuple_count"],
            "invariant_count": closed_loop["completeness"]["invariant_count"],
            "debt_count": closed_loop["completeness"]["debt_count"],
            "completeness_score": closed_loop["completeness"]["score"],
        },
        "replay_summary": replay.get("final_state", {}),
    }


if __name__ == "__main__":
    result = evaluate(render_validation_passed=True)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
