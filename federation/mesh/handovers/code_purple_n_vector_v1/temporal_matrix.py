"""Read-only origin-independent telemetry reference; no GitHub operations or admission authority."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import isfinite

_HEX = frozenset("0123456789abcdef")
_REQUIRED = (
    "exact_head", "native_tests", "security", "independent_review",
    "effective_protection", "required_ci",
)


def _utc(value: str) -> datetime:
    """Require source UTC observations, not local or naive timestamps."""
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC timestamp ending Z required")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("invalid UTC timestamp") from exc
    if parsed.tzinfo != UTC:
        raise ValueError("UTC timestamp required")
    return parsed


@dataclass(frozen=True)
class Metric:
    value: float | None
    unit: str
    repository: str
    source_sha: str
    producer: str
    config_digest: str
    scope_digest: str
    observed_at_utc: str
    denominator: float | None = None

    def __post_init__(self) -> None:
        if self.value is not None and (
            type(self.value) not in (int, float) or not isfinite(self.value)
        ):
            raise ValueError("finite numeric value or None required")
        if self.denominator is not None and (
            type(self.denominator) not in (int, float)
            or not isfinite(self.denominator)
            or self.denominator <= 0
        ):
            raise ValueError("positive finite denominator required")
        if not isinstance(self.source_sha, str) or (
            len(self.source_sha) != 40 or any(x not in _HEX for x in self.source_sha)
        ):
            raise ValueError("full lowercase SHA-1 object ID required")
        for field in ("unit", "repository", "producer", "config_digest", "scope_digest"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"missing metric identity: {field}")
        _utc(self.observed_at_utc)


def rebase_index(index: int, origin: int) -> int:
    """Origin shift does not modify SHA, clock, or causal identity."""
    if type(index) is not int or type(origin) is not int:
        raise ValueError("integer ordinals required")
    return index - origin


def comparable_delta(before: Metric, after: Metric) -> float | None:
    """Only same-scope, chronologically ordered exact-source observations compare."""
    identity = (
        "repository", "unit", "producer", "config_digest",
        "scope_digest", "denominator",
    )
    if any(getattr(before, k) != getattr(after, k) for k in identity):
        return None
    if before.value is None or after.value is None:
        return None
    if before.source_sha == after.source_sha:
        return None
    if _utc(before.observed_at_utc) >= _utc(after.observed_at_utc):
        return None
    return float(after.value - before.value)


def masked_first_difference(
    rows: list[list[float | None]], comparable: list[list[bool]]
) -> list[list[float | None]]:
    """Adjacent first differences D X, masked; nulls remain null."""
    if len(rows) < 2 or len(comparable) != len(rows) - 1:
        raise ValueError("invalid revision dimension")
    width = len(rows[0])
    if width == 0 or any(len(x) != width for x in rows + comparable):
        raise ValueError("invalid metric dimension")
    output: list[list[float | None]] = []
    for i, flags in enumerate(comparable):
        values: list[float | None] = []
        for j, flag in enumerate(flags):
            if type(flag) is not bool:
                raise ValueError("mask must contain booleans")
            old, new = rows[i][j], rows[i + 1][j]
            if not flag or old is None or new is None:
                values.append(None)
                continue
            if type(old) not in (int, float) or type(new) not in (int, float):
                raise ValueError("invalid measurement type")
            if not isfinite(old) or not isfinite(new):
                values.append(None)
                continue
            values.append(float(new - old))
        output.append(values)
    return output


def admission_gate(states: dict[str, Optional[bool]]) -> str:
    """No inference or automatic merging from a complete gate set."""
    if any(states.get(k) is not True for k in _REQUIRED):
        return "HOLD"
    return "ELIGIBLE_FOR_SEPARATE_OWNER_DECISION"
