from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class RuntimeState:
    latest_tuple: Optional[str]
    active_branches: tuple[str, ...]
    invariant_count: int
    open_debt_count: int
    tuple_count: int
    replay_ready: bool


def _open_debt(items: Iterable[Dict[str, Any]]) -> int:
    return sum(1 for item in items if str(item.get("status", "open")).lower() not in {"closed", "resolved", "done"})


def reconstruct(
    tuples: List[Dict[str, Any]],
    invariants: List[Dict[str, Any]],
    semantic_debt: List[Dict[str, Any]],
) -> RuntimeState:
    """Pure/idempotent state reconstruction from semantic ledgers."""
    tuple_ids = [str(t["id"]) for t in tuples if t.get("id")]
    branches = sorted({str(t.get("branch")) for t in tuples if t.get("branch")})
    latest = tuple_ids[-1] if tuple_ids else None

    replay_ready = bool(tuple_ids) and bool(invariants)

    return RuntimeState(
        latest_tuple=latest,
        active_branches=tuple(branches),
        invariant_count=len(invariants),
        open_debt_count=_open_debt(semantic_debt),
        tuple_count=len(tuple_ids),
        replay_ready=replay_ready,
    )


def validate(state: RuntimeState) -> Dict[str, Any]:
    errors: List[str] = []
    if state.tuple_count == 0:
        errors.append("no semantic tuples loaded")
    if state.invariant_count == 0:
        errors.append("no active invariants loaded")
    if not state.replay_ready:
        errors.append("state is not replay-ready")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "state": {
            "latest_tuple": state.latest_tuple,
            "active_branches": list(state.active_branches),
            "tuple_count": state.tuple_count,
            "invariant_count": state.invariant_count,
            "open_debt_count": state.open_debt_count,
            "replay_ready": state.replay_ready,
        },
    }
